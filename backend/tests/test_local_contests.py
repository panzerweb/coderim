"""Team ownership and organizer workflows using real existing local execution."""
import concurrent.futures
import json
import os
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'backend'), str(ROOT/'tools')]
from app.main import create_app
from app.languages import Registry
from app.models import SubmissionRequest
from app.storage import Storage
from local_contest import prepare, main as start_local
from contest_backup import backup, restore

ORIGIN = 'http://127.0.0.1:8000'
SECRET = 'local-contest-integration-test-secret'


class LocalContestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = Path(self.temp.name)/'runtime'
        self.clients = []
        self.app = self.application()
        self.admin = self.enter(self.app)
        self.app.state.auth.create_organizer('organizer', 'local-organizer-password')
        login = self.admin.post('/api/organizer/login', json={'username':'organizer','password':'local-organizer-password'})
        self.assertEqual(login.status_code, 200, login.text)
        self.admin.headers['X-CSRF-Token'] = login.json()['csrf_token']
        event = self.admin.post('/api/organizer/contests', json={'name':'Local contest',
            'starts_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(), 'duration_minutes':210})
        self.assertEqual(event.status_code, 201, event.text)
        self.contest = event.json()['id']
        published = self.admin.post(f'/api/organizer/contests/{self.contest}/publish', json={
            'problem_ids':['broken-code-formatter','longest-rising-streak-updates','g-tree-changing-root']})
        self.assertEqual(published.status_code, 200, published.text)

    def application(self):
        return create_app(runtime=self.runtime, mode='contest', executor='local', registry=self.registry,
            session_secret=SECRET, secure_cookies=False, frontend_origin=ORIGIN)

    def enter(self, app):
        client = TestClient(app, base_url=ORIGIN, headers={'Origin':ORIGIN})
        with patch('app.remote_judge.Judge0Client', side_effect=AssertionError('No provider in local contests')):
            client.__enter__()
        self.clients.append(client)
        return client

    def tearDown(self):
        for client in reversed(self.clients):
            client.__exit__(None,None,None)
        self.temp.cleanup()

    def team(self, name):
        data = self.admin.post(f'/api/organizer/contests/{self.contest}/teams', json={'name':name}).json()
        client = TestClient(self.app, base_url=ORIGIN, headers={'Origin':ORIGIN,'X-Relay-Role':'team'})
        self.addCleanup(client.close)
        response = client.post('/api/teams/join',json={'contest_id':self.contest,'team_name':name,'join_code':data['join_code']})
        self.assertEqual(response.status_code,200,response.text)
        client.headers['X-CSRF-Token'] = response.json()['csrf_token']
        return client, data

    def start(self):
        response = self.admin.post(f'/api/organizer/contests/{self.contest}/start', json={'confirm':True})
        self.assertEqual(response.status_code,200,response.text)
        return response.json()

    def job(self, client, slug, source, *, mode=None, stdin='', key=None):
        payload = {'problem_id':slug,'problem_version':1,'language':'python','code':source}
        if mode: payload.update(mode=mode,stdin=stdin)
        response = client.post('/api/runs' if mode else '/api/submissions',json=payload,
            headers={} if mode else {'Idempotency-Key':key or str(time.time_ns())})
        self.assertEqual(response.status_code,202,response.text)
        identifier = response.json()['job_id']
        deadline = time.monotonic()+60
        while time.monotonic()<deadline:
            current = client.get('/api/jobs/'+identifier).json()
            if current['state'] in ('completed','failed'): return identifier,current['result']
            time.sleep(.02)
        self.fail('Local contest job did not finish')

    def test_provider_free_publication_join_manual_timer_and_privacy(self):
        a,_ = self.team('Alpha'); b,_ = self.team('Beta')
        self.assertIsNone(self.app.state.provider)
        self.assertEqual(self.admin.get('/api/config').json()['executor'],'local')
        self.assertFalse(self.admin.get('/api/health').json()['memory_enforced'])
        self.assertEqual(self.admin.get('/api/organizer/provider').json()['executor'],'local')
        self.assertEqual(a.get('/api/problems').status_code,403)
        self.assertEqual(a.post(f'/api/organizer/contests/{self.contest}/start',json={'confirm':True}).status_code,401)
        self.assertEqual(self.admin.post(f'/api/organizer/contests/{self.contest}/start',json={'confirm':False}).status_code,422)
        started = self.start()
        self.assertEqual(started['duration_minutes'],210)
        self.assertEqual(started['phase'],'active')
        self.assertEqual(len(a.get('/api/problems').json()),3)
        self.assertEqual(self.admin.post(f'/api/organizer/contests/{self.contest}/start',json={'confirm':True}).status_code,409)
        self.assertEqual(a.get('/api/submissions/me').json(),[])
        self.assertEqual(b.get('/api/submissions/me').json(),[])
        events=self.admin.get('/api/organizer/audit').json()
        self.assertEqual(sum(e['action']=='contest_started_manually' for e in events),1)

    def test_new_problem_selection_pinning_submission_review_and_private_history(self):
        from practice_problem_content import SPECS
        old,_=self.team('Original selection');self.start()
        self.assertEqual(len(old.get('/api/problems').json()),3)
        self.assertEqual(len(self.admin.get('/api/problems').json()),17)
        event=self.admin.post('/api/organizer/contests',json={'name':'Introductory problems',
            'starts_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'duration_minutes':60})
        self.assertEqual(event.status_code,201,event.text);self.contest=event.json()['id']
        published=self.admin.post(f'/api/organizer/contests/{self.contest}/publish',json={'problem_ids':list(SPECS)})
        self.assertEqual(published.status_code,200,published.text)
        a,owner=self.team('New Alpha');b,_=self.team('New Beta');self.start()
        self.assertEqual({p['id'] for p in a.get('/api/problems').json()},set(SPECS))
        self.assertEqual(len(old.get('/api/problems').json()),3)
        self.assertEqual(a.get('/api/problems/broken-code-formatter').status_code,404)
        # Repository changes after publication cannot reinterpret this selection.
        original=self.app.state.repository.get('add-two-numbers')
        self.app.state.repository.problems['add-two-numbers']=replace(original,
            meta=original.meta.model_copy(update={'version':2,'title':'Changed repository title'}))
        detail=a.get('/api/problems/add-two-numbers').json()
        self.assertEqual(detail['version'],1);self.assertEqual(detail['title'],'Add Two Numbers')
        for slug in SPECS:
            detail=a.get('/api/problems/'+slug).json()
            self.assertEqual(detail['difficulty'],SPECS[slug]['difficulty'])
            self.assertNotIn('author/',json.dumps(detail));self.assertNotIn('tests/',json.dumps(detail))
        source=(ROOT/'problems/add-two-numbers/author/reference.py').read_text(encoding='utf-8')
        identifier,result=self.job(a,'add-two-numbers',source)
        self.assertEqual(result['verdict'],'Accepted',result)
        saved=a.get('/api/submissions/'+identifier).json()
        self.assertEqual(saved['code'],source);self.assertEqual(saved['team_id'],owner['id'])
        self.assertEqual(saved['problem_version'],1)
        self.assertEqual(saved['reference_complexity'],original.public()['reference_complexity'])
        self.assertEqual(b.get('/api/submissions/'+identifier).status_code,404)
        self.assertEqual(b.get('/api/jobs/'+identifier).status_code,404)
        self.assertEqual(b.get('/api/submissions/me').json(),[])
        review={'readability':[4]*4,'technical':[4]*4,'rationale':'Simple and correct sum of both signed operands.',
            'complexity':{'status':'assessed','worst_case_time':'O(1)','auxiliary_space':'O(1)','total_space':'O(1)',
                'reasoning':'Two bounded integers and one bounded result require constant space and time.'}}
        self.assertEqual(a.put('/api/attempts/'+identifier+'/review',json=review).status_code,401)
        response=self.admin.put('/api/attempts/'+identifier+'/review',json=review)
        self.assertEqual(response.status_code,200,response.text)
        saved=a.get('/api/submissions/'+identifier).json()
        self.assertEqual(saved['result']['assessment']['final'],100)
        self.assertEqual(saved['review']['complexity']['worst_case_time'],'O(1)')
        self.assertEqual(len(saved['result']['cases']),3)
        serialized=json.dumps(saved)
        for secret in ('scale-01','input_file','output_file','author/','provider_token'):self.assertNotIn(secret,serialized)
        self.assertEqual(len(a.get('/api/submissions/me').json()),1)

    def test_real_tests_scoring_all_problem_sources_reviews_and_owned_history(self):
        a,owner = self.team('Alpha'); b,other = self.team('Beta'); self.start()
        for slug,total in [('broken-code-formatter',65),('longest-rising-streak-updates',28),('g-tree-changing-root',23)]:
            source = (ROOT/'problems'/slug/'author/reference.py').read_text(encoding='utf-8')
            identifier,result = self.job(a,slug,source)
            self.assertEqual(result['verdict'],'Accepted',result)
            self.assertEqual(result['passed'],total)
            self.assertEqual(result['assessment']['correctness'],100)
            self.assertEqual(result['assessment']['requirements'],100)
            self.assertIsNone(result['assessment']['final'])
            saved = a.get('/api/submissions/'+identifier).json()
            self.assertEqual(saved['code'],source)
            self.assertEqual(saved['team_id'],owner['id'])
            for path in ('/api/submissions/','/api/attempts/','/api/jobs/'):
                self.assertEqual(b.get(path+identifier).status_code,404)
            self.assertEqual(len(saved['result']['cases']),len(self.app.state.repository.get(slug).samples))
        identifier,wrong = self.job(a,'broken-code-formatter',"print('INVALID')\n",key='wrong')
        self.assertEqual(wrong['verdict'],'Wrong Answer')
        self.assertTrue(wrong['assessment']['complete'])
        self.assertEqual(a.get('/api/teams/me').json()['metrics'],{'solved_problems':3,'official_attempts':4})
        review={'readability':[4]*4,'technical':[3]*4,'rationale':'Reviewed the saved code.',
            'complexity':{'status':'assessed','worst_case_time':'O(1)','auxiliary_space':'O(1)','total_space':'O(1)','reasoning':'This program only prints a constant and does not parse the input.'}}
        self.assertEqual(a.put('/api/attempts/'+identifier+'/review',json=review).status_code,401)
        reviewed=self.admin.put('/api/attempts/'+identifier+'/review',json=review)
        self.assertEqual(reviewed.status_code,200,reviewed.text)
        self.assertIsNotNone(a.get('/api/attempts/'+identifier).json()['result']['assessment']['final'])
        self.assertEqual(len(self.admin.get('/api/organizer/submissions?contest_id='+self.contest).json()),4)
        self.assertEqual(self.admin.get('/api/organizer/submissions?team_id='+other['id']).json(),[])
        self.assertEqual(len(self.admin.get('/api/organizer/submissions?team_id='+owner['id']).json()),4)
        self.assertEqual(b.get('/api/submissions/me').json(),[])
        self.assertEqual(self.app.state.storage.db.execute('SELECT COUNT(*) FROM provider_cases').fetchone()[0],0)
        self.assertFalse((self.runtime/'provider-verification.json').exists())

    def test_runs_are_transient_and_recording_is_idempotent_after_deadline(self):
        a,_=self.team('Runs');self.start()
        source=(ROOT/'problems/broken-code-formatter/author/reference.py').read_text(encoding='utf-8')
        _,sample=self.job(a,'broken-code-formatter',source,mode='samples')
        self.assertEqual(sample['passed'],6)
        _,custom=self.job(a,'broken-code-formatter','import sys\nprint(sys.stdin.read().upper(),end="")',mode='custom',stdin='hello\n')
        self.assertEqual(custom['verdict'],'Completed');self.assertIsNone(custom['assessment'])
        self.assertEqual(custom['cases'][0]['stdout'].replace('\r\n','\n'),'HELLO\n')
        self.assertEqual(a.get('/api/submissions/me').json(),[])
        identifier,_=self.job(a,'broken-code-formatter',source,key='original')
        self.admin.post(f'/api/organizer/contests/{self.contest}/end',json={'confirm':True})
        payload={'problem_id':'broken-code-formatter','problem_version':1,'language':'python','code':source}
        replay=a.post('/api/submissions',json=payload,headers={'Idempotency-Key':'original'})
        self.assertEqual(replay.json()['job_id'],identifier)
        self.assertEqual(a.post('/api/submissions',json=payload,headers={'Idempotency-Key':'new'}).status_code,409)
        self.assertEqual(a.post('/api/runs',json=payload).status_code,409)
        self.assertEqual(a.get('/api/teams/me').json()['metrics']['official_attempts'],1)

    def test_completed_history_survives_restart_and_pending_local_work_is_interrupted(self):
        a,data=self.team('Restart');self.start()
        source=(ROOT/'problems/broken-code-formatter/author/reference.py').read_text(encoding='utf-8')
        identifier,_=self.job(a,'broken-code-formatter',source)
        p=self.app.state.repository.get('broken-code-formatter')
        self.app.state.storage.create('unfinished',SubmissionRequest(problem_id=p.meta.id,problem_version=1,language='python',code='while True: pass'),p.meta.rubric.model_dump(),team_id=data['id'],contest_id=self.contest)
        cookies=dict(a.cookies)
        self.clients.pop().__exit__(None,None,None)
        self.app=self.application();self.admin=self.enter(self.app)
        self.admin.cookies.update(cookies);self.admin.headers['X-Relay-Role']='team'
        saved=self.admin.get('/api/submissions/'+identifier)
        self.assertEqual(saved.status_code,200);self.assertEqual(saved.json()['code'],source)
        self.assertEqual(saved.json()['result']['verdict'],'Accepted')
        interrupted=self.admin.get('/api/submissions/unfinished').json()
        self.assertEqual(interrupted['status'],'interrupted')
        self.assertEqual(interrupted['result']['verdict'],'Judge Error')
        self.assertEqual(self.admin.get('/api/jobs/unfinished').json()['state'],'interrupted')

    def test_json_problem_checkers_are_pinned_and_results_reviews_survive_restart(self):
        from leetcode_problem_content import SPECS
        original_client,_=self.team('Original catalog');self.start()
        event=self.admin.post('/api/organizer/contests',json={'name':'Function problems',
            'starts_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'duration_minutes':210})
        self.assertEqual(event.status_code,201,event.text);self.contest=event.json()['id']
        response=self.admin.post(f'/api/organizer/contests/{self.contest}/publish',json={'problem_ids':list(SPECS)})
        self.assertEqual(response.status_code,200,response.text)
        a,_=self.team('Functions');b,_=self.team('Other functions');self.start()
        self.assertEqual({p['id'] for p in a.get('/api/problems').json()},set(SPECS))
        self.assertEqual(len(original_client.get('/api/problems').json()),3)
        expected_checkers={slug:self.app.state.repository.get(slug).meta.checker.model_dump() for slug in SPECS}
        # Replacing repository comparison rules cannot alter already pinned rules.
        original=self.app.state.repository.get('substring-concatenation-all-words')
        from app.models import Checker
        self.app.state.repository.problems[original.meta.id]=replace(original,meta=original.meta.model_copy(update={'checker':Checker()}))
        identifiers={}
        for slug in SPECS:
            source=(ROOT/'problems'/slug/'author/reference.py').read_text(encoding='utf-8')
            identifier,result=self.job(a,slug,source)
            self.assertEqual(result['verdict'],'Accepted',result)
            self.assertEqual(result['assessment']['correctness'],100)
            self.assertEqual(result['assessment']['requirements'],100)
            self.assertIsNone(result['assessment']['final'])
            identifiers[slug]=identifier
            for path in ('/api/submissions/','/api/jobs/','/api/attempts/'):
                self.assertEqual(b.get(path+identifier).status_code,404)
            detail=a.get('/api/submissions/'+identifier).json()
            self.assertEqual(detail['code'],source);self.assertEqual(len(detail['result']['cases']),3)
            self.assertNotIn('scale-01',json.dumps(detail));self.assertNotIn('provider_token',json.dumps(detail))
            pinned=self.app.state.contests.problem(self.contest,slug)
            self.assertEqual(pinned.meta.checker.model_dump(),expected_checkers[slug])
        review={'readability':[4]*4,'technical':[4]*4,'rationale':'Checked syntax scanning and provided I/O.',
            'complexity':{'status':'assessed','worst_case_time':'O(L)','auxiliary_space':'O(1)','total_space':'O(L)',
                'reasoning':'The function scans once with constant state; its input string is retained.'}}
        identifier=identifiers['valid-number']
        self.assertEqual(a.put('/api/attempts/'+identifier+'/review',json=review).status_code,401)
        self.assertEqual(self.admin.put('/api/attempts/'+identifier+'/review',json=review).status_code,200)
        cookies=dict(a.cookies)
        # Close the shared app's lifespan before opening the same database again.
        self.clients.pop().__exit__(None,None,None)
        self.app=self.application();restarted=self.enter(self.app)
        restarted.cookies.update(cookies);restarted.headers['X-Relay-Role']='team'
        history=restarted.get('/api/submissions/me').json();self.assertEqual(len(history),len(SPECS))
        saved=restarted.get('/api/submissions/'+identifier).json()
        self.assertEqual(saved['result']['assessment']['final'],100)
        self.assertEqual(saved['review']['complexity']['worst_case_time'],'O(L)')
        for slug in SPECS:
            self.assertEqual(self.app.state.contests.problem(self.contest,slug).meta.checker.model_dump(),expected_checkers[slug])

    def test_manual_start_is_atomic(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            statuses=list(pool.map(lambda _:self.admin.post(f'/api/organizer/contests/{self.contest}/start',json={'confirm':True}).status_code,range(2)))
        self.assertEqual(sorted(statuses),[200,409])


class LocalStartupTests(unittest.TestCase):
    def test_launcher_selects_local_executor_and_loopback_without_manual_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.dict(os.environ,{'RENDER':'','RELAY_RUNTIME':temporary,'RELAY_EXECUTOR':'managed'}):
                with patch('local_contest.prepare',return_value=SECRET),patch('uvicorn.run') as run:
                    start_local()
                    self.assertEqual(os.environ['RELAY_MODE'],'contest')
                    self.assertEqual(os.environ['RELAY_EXECUTOR'],'local')
                    self.assertEqual(os.environ['RELAY_SESSION_SECRET'],SECRET)
                    self.assertEqual(os.environ['RELAY_DEV_COOKIES'],'true')
                    run.assert_called_once_with('app.main:app',host='127.0.0.1',port=8000,workers=1)
        with patch.dict(os.environ,{'RENDER':'true'}):
            self.assertRaises(SystemExit,start_local)

    def test_first_run_bootstrap_secret_reuse_and_backup(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime=Path(temporary)/'runtime'
            with patch.dict(os.environ,{'RELAY_SESSION_SECRET':SECRET}):
                secret=prepare(runtime,input_name=lambda _: 'organizer',password=lambda _: 'local-launch-password')
            self.assertEqual(secret,SECRET)
            with patch.dict(os.environ,{'RELAY_SESSION_SECRET':'a-different-secret-that-must-not-rotate-sessions'}):
                self.assertEqual(prepare(runtime,input_name=lambda _:self.fail('Must reuse existing organizer')),secret)
            archive=Path(temporary)/'backup.zip';target=Path(temporary)/'restore'
            backup(runtime,archive);restore(archive,target)
            self.assertEqual((target/'session-secret.txt').read_text(),secret)

    def test_public_local_execution_is_explicit(self):
        with patch.dict(os.environ,{'RENDER':'true','RELAY_TRUSTED_LOCAL_EXECUTION':''}):
            self.assertRaises(ValueError,create_app,mode='contest',executor='local',secure_cookies=True,frontend_origin='https://app.example.com')
        with patch.dict(os.environ,{'RENDER':'true','RELAY_TRUSTED_LOCAL_EXECUTION':'true'}):
            create_app(mode='contest',executor='local',secure_cookies=True,frontend_origin='https://app.example.com')
