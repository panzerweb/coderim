import concurrent.futures
import json
import shutil
import sqlite3
import sys
import tempfile
import time
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'));sys.path.insert(0,str(ROOT/'tools'))
from app.main import create_app
from app.problems import Repository
from app.storage import Storage
from app.models import ReviewRequest
from app.remote_judge import RemoteJudge
from app.hosted_jobs import HostedJobs
from scaffold_problem import scaffold
from contest_backup import backup, restore
from hosted_support import FakeProvider

ORIGIN='http://127.0.0.1:5173'
SECRET='test-session-secret-for-hosted-contests-only'


class HostedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content=tempfile.TemporaryDirectory();cls.problem_root=Path(cls.content.name)
        for i in range(5):
            folder=scaffold(f'fixture-{i}',cls.problem_root)
            metadata=json.loads((folder/'problem.json').read_text());metadata['status']='published'
            (folder/'problem.json').write_text(json.dumps(metadata))
        cls.repository=Repository(cls.problem_root)

    @classmethod
    def tearDownClass(cls):cls.content.cleanup()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.runtime=Path(self.temp.name)/'runtime'
        self.provider=FakeProvider(self.repository)
        self.app=create_app(problem_root=self.problem_root,runtime=self.runtime,mode='contest',
            provider=self.provider,session_secret=SECRET,secure_cookies=False)
        self.admin=TestClient(self.app,base_url='http://127.0.0.1:8000',headers={'Origin':ORIGIN})
        self.admin.__enter__();self.clients=[]
        self.app.state.auth.create_organizer('organizer','test-organizer-password')
        response=self.admin.post('/api/organizer/login',json={'username':'organizer','password':'test-organizer-password'})
        self.assertEqual(response.status_code,200,response.text)
        self.admin.headers['X-CSRF-Token']=response.json()['csrf_token']
        response=self.admin.post('/api/organizer/contests',json={'name':'Test Relay',
            'starts_at':(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat(),'duration_minutes':210})
        self.assertEqual(response.status_code,201,response.text);self.contest=response.json()['id']
        response=self.admin.post(f'/api/organizer/contests/{self.contest}/publish',json={'problem_ids':list(self.repository.problems)})
        self.assertEqual(response.status_code,200,response.text)

    def tearDown(self):
        self.provider.gate.set()
        for client in self.clients:client.close()
        self.admin.__exit__(None,None,None);self.temp.cleanup()

    def client(self):
        client=TestClient(self.app,base_url='http://127.0.0.1:8000',headers={'Origin':ORIGIN,'X-Relay-Role':'team'})
        self.clients.append(client);return client

    def team(self,name):
        response=self.admin.post(f'/api/organizer/contests/{self.contest}/teams',json={'name':name})
        self.assertEqual(response.status_code,201,response.text)
        data=response.json();client=self.client()
        response=client.post('/api/teams/join',json={'contest_id':self.contest,'team_name':name,'join_code':data['join_code']})
        self.assertEqual(response.status_code,200,response.text)
        client.headers['X-CSRF-Token']=response.json()['csrf_token']
        return client,data

    def submit(self,client,problem='fixture-0',code='ACCEPT',key=None,language='python'):
        key=key or str(uuid.uuid4())
        response=client.post('/api/submissions',json={'problem_id':problem,'problem_version':1,'language':language,'code':code},headers={'Idempotency-Key':key})
        self.assertEqual(response.status_code,202,response.text)
        return response.json()['job_id'],key

    def finished(self,client,key):
        until=time.monotonic()+8
        while time.monotonic()<until:
            response=client.get('/api/jobs/'+key);self.assertEqual(response.status_code,200,response.text)
            if response.json()['state'] in ('completed','failed'):return response.json()
            time.sleep(.01)
        self.fail('Hosted job did not finish')

    def phase(self,start,end):
        with self.app.state.storage.lock,self.app.state.storage.db:
            self.app.state.storage.db.execute('UPDATE contests SET starts_at=?,ends_at=? WHERE id=?',(start.isoformat(),end.isoformat(),self.contest))

    def test_cookie_csrf_ownership_all_paths_and_organizer_only_reviews(self):
        a,ta=self.team('Alpha');b,tb=self.team('Beta');anonymous=self.client()
        for path in ['/api/problems','/api/problems/fixture-0','/api/languages','/api/attempts?problem_id=fixture-0&problem_version=1&language=python','/api/submissions/me','/api/organizer/teams?contest_id='+self.contest]:
            self.assertEqual(anonymous.get(path).status_code,401,path)
        a.headers.pop('X-CSRF-Token');self.assertEqual(a.post('/api/runs',json={'problem_id':'fixture-0','problem_version':1,'language':'python','code':'ACCEPT'}).status_code,403)
        a.headers['X-CSRF-Token']=a.get('/api/teams/me').json()['csrf_token']
        key,_=self.submit(a);self.finished(a,key)
        for path in [f'/api/jobs/{key}',f'/api/attempts/{key}',f'/api/submissions/{key}']:
            self.assertEqual(b.get(path).status_code,404,path);self.assertEqual(anonymous.get(path).status_code,401,path)
        self.assertEqual(b.get('/api/submissions/me').json(),[])
        self.assertEqual(b.get('/api/attempts?problem_id=fixture-0&problem_version=1&language=python').json(),[])
        review={'readability':[4]*4,'technical':[4]*4,'rationale':'Reviewed source'}
        self.assertEqual(a.put(f'/api/attempts/{key}/review',json=review).status_code,401)
        self.assertEqual(self.admin.put(f'/api/attempts/{key}/review',json=review).status_code,200)
        self.assertEqual(a.get('/api/submissions/'+key).json()['result']['assessment']['final'],100)
        payload={'problem_id':'fixture-0','problem_version':1,'language':'python','code':'ACCEPT','team_id':tb['id']}
        self.assertEqual(a.post('/api/submissions',json=payload,headers={'Idempotency-Key':str(uuid.uuid4())}).status_code,422)
        self.assertEqual(a.post('/api/teams/logout',json={},headers={'Origin':'https://evil.test'}).status_code,403)
        self.assertEqual(a.post('/api/teams/logout',json={}).status_code,200)
        self.assertEqual(a.get('/api/teams/me').status_code,401)

    def test_single_session_normalization_rotation_activity_and_expiry(self):
        a,data=self.team('Alpha')
        duplicate=self.client();payload={'contest_id':self.contest,'team_name':' ALPHA ','join_code':data['join_code']}
        self.assertEqual(duplicate.post('/api/teams/join',json=payload).status_code,409)
        self.assertEqual(self.admin.post(f'/api/organizer/contests/{self.contest}/teams',json={'name':' alpha '}).status_code,409)
        self.admin.post(f'/api/organizer/teams/{data["id"]}/reset-session',json={})
        self.assertEqual(a.get('/api/teams/me').status_code,401)
        response=duplicate.post('/api/teams/join',json=payload);self.assertEqual(response.status_code,200)
        duplicate.headers['X-CSRF-Token']=response.json()['csrf_token']
        rotated=self.admin.post(f'/api/organizer/teams/{data["id"]}/rotate-code',json={}).json()['join_code']
        self.assertEqual(duplicate.get('/api/teams/me').status_code,401)
        another=self.client();self.assertEqual(another.post('/api/teams/join',json=payload).status_code,401)
        payload['join_code']=rotated
        response=another.post('/api/teams/join',json=payload);self.assertEqual(response.status_code,200)
        self.admin.put(f'/api/organizer/teams/{data["id"]}',json={'is_active':False})
        self.assertEqual(another.get('/api/teams/me').status_code,401)
        self.assertEqual(self.client().post('/api/teams/join',json=payload).status_code,401)
        self.admin.put(f'/api/organizer/teams/{data["id"]}',json={'is_active':True})
        # This scenario exercises more than the default five logins per 15 minutes.
        with self.app.state.storage.lock,self.app.state.storage.db:
            self.app.state.storage.db.execute('DELETE FROM auth_limits')
        revived=self.client();self.assertEqual(revived.post('/api/teams/join',json=payload).status_code,200)
        with self.app.state.storage.lock,self.app.state.storage.db:
            self.app.state.storage.db.execute("UPDATE sessions SET expires_at='2000-01-01T00:00:00+00:00' WHERE team_id=?",(data['id'],))
        self.assertEqual(revived.get('/api/teams/me').status_code,401)
        self.assertEqual(self.client().post('/api/teams/join',json=payload).status_code,200)

    def test_rate_limits_generic_errors_and_hashed_storage(self):
        client=self.client()
        errors=[]
        for i in range(5):
            response=client.post('/api/teams/join',json={'contest_id':self.contest,'team_name':'Missing','join_code':'wrong'})
            self.assertEqual(response.status_code,401);errors.append(response.json())
        self.assertEqual(len({json.dumps(e) for e in errors}),1)
        self.assertEqual(client.post('/api/teams/join',json={'contest_id':self.contest,'team_name':'Missing','join_code':'wrong'}).status_code,429)
        team,data=self.team('Secrets')
        with self.app.state.storage.lock:
            row=self.app.state.storage.db.execute('SELECT * FROM teams WHERE id=?',(data['id'],)).fetchone()
            self.assertTrue(row['join_code_hash'].startswith('$argon2id$'))
            self.assertNotIn(data['join_code'],str(tuple(row)))
            sessions=self.app.state.storage.db.execute('SELECT token_hash FROM sessions WHERE team_id=?',(data['id'],)).fetchall()
        self.assertTrue(all(len(s['token_hash'])==64 for s in sessions))
        self.assertNotIn('join_code_hash',self.admin.get('/api/organizer/teams?contest_id='+self.contest).text)

    def test_waiting_deadline_queued_result_and_idempotency(self):
        a,_=self.team('Alpha');clock=datetime.now(timezone.utc)
        self.phase(clock+timedelta(hours=1),clock+timedelta(hours=4))
        self.assertEqual(a.get('/api/teams/me').json()['contest']['phase'],'waiting')
        self.assertEqual(a.get('/api/problems').status_code,403)
        payload={'problem_id':'fixture-0','problem_version':1,'language':'python','code':'ACCEPT'}
        self.assertEqual(a.post('/api/submissions',json=payload,headers={'Idempotency-Key':'early'}).status_code,409)
        self.phase(clock-timedelta(minutes=1),clock+timedelta(hours=2))
        self.provider.gate.clear();key,retry=self.submit(a)
        self.assertTrue(self.provider.started.wait(2))
        self.assertEqual(a.post('/api/submissions',json=payload,headers={'Idempotency-Key':retry}).json()['job_id'],key)
        self.assertEqual(a.post('/api/submissions',json={**payload,'code':'changed'},headers={'Idempotency-Key':retry}).status_code,409)
        self.admin.post(f'/api/organizer/contests/{self.contest}/end',json={'confirm':True})
        self.assertEqual(a.post('/api/runs',json=payload).status_code,409)
        self.assertEqual(a.post('/api/submissions',json=payload,headers={'Idempotency-Key':retry}).json()['job_id'],key)
        self.provider.gate.set();self.assertEqual(self.finished(a,key)['result']['verdict'],'Accepted')
        me=a.get('/api/teams/me').json();self.assertEqual(me['metrics'],{'solved_problems':1,'official_attempts':1})
        self.assertEqual(a.get('/api/submissions/'+key).status_code,200)

    def test_distinct_solved_five_versus_four_and_failed_attempts(self):
        a,_=self.team('Alpha');b,_=self.team('Beta')
        for i in range(5):
            key,_=self.submit(a,f'fixture-{i}');self.finished(a,key)
        for i in range(4):
            key,_=self.submit(b,f'fixture-{i}');self.finished(b,key)
        key,_=self.submit(a,'fixture-0',language='java');self.finished(a,key)
        key,_=self.submit(b,'fixture-4','WRONG');self.finished(b,key)
        self.assertEqual(a.get('/api/teams/me').json()['metrics'],{'solved_problems':5,'official_attempts':6})
        self.assertEqual(b.get('/api/teams/me').json()['metrics'],{'solved_problems':4,'official_attempts':5})
        self.assertEqual(b.get('/api/submissions/me').json()[0]['result']['verdict'],'Wrong Answer')

    def test_snapshot_integrity_publication_and_schedule_extensions(self):
        a,_=self.team('Alpha')
        from app.remote_judge import Judge0Client
        from types import SimpleNamespace
        verifier=Judge0Client(self.runtime,SECRET,url='https://judge.example',headers={'key':'test'},language_ids={'python':71})
        self.assertEqual(verifier.fingerprint(self.repository),verifier.fingerprint(SimpleNamespace(published=lambda:self.app.state.contests.problems(self.contest))))
        verifier.close()
        p=self.app.state.repository.problems['fixture-0']
        original=p.meta.title;p.meta.title='Repository changed after publication'
        try:self.assertNotEqual(a.get('/api/problems/fixture-0').json()['title'],p.meta.title)
        finally:p.meta.title=original
        self.assertEqual(self.admin.post(f'/api/organizer/contests/{self.contest}/publish',json={'problem_ids':['fixture-0']}).status_code,409)
        c=self.admin.get('/api/organizer/contests').json()[0]
        values={'name':c['name'],'starts_at':c['starts_at'],'duration_minutes':300}
        self.assertEqual(self.admin.put('/api/organizer/contests/'+self.contest,json=values).status_code,200)
        self.assertEqual(self.admin.put('/api/organizer/contests/'+self.contest,json={**values,'duration_minutes':100}).status_code,409)
        self.assertEqual(self.admin.post('/api/organizer/contests',json={**values,'duration_minutes':0}).status_code,422)

    def test_five_simultaneous_teams_queue_and_api_responsiveness(self):
        teams=[self.team(f'Team {i}')[0] for i in range(5)]
        self.provider.gate.clear()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            jobs=list(pool.map(lambda c:self.submit(c)[0],teams))
        self.assertEqual(len(set(jobs)),5)
        started=time.monotonic();self.assertEqual(self.admin.get('/api/health').status_code,200);self.assertLess(time.monotonic()-started,.5)
        payload={'problem_id':'fixture-0','problem_version':1,'language':'python','code':'ACCEPT'}
        self.assertEqual(teams[0].post('/api/runs',json=payload).status_code,409)
        self.provider.gate.set()
        for client,key in zip(teams,jobs):self.assertEqual(self.finished(client,key)['result']['verdict'],'Accepted')
        self.assertLessEqual(self.provider.maximum,2)
        self.assertEqual(self.app.state.storage.db.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_provider_failure_unknown_delivery_and_no_local_processes(self):
        a,_=self.team('Alpha')
        with patch('subprocess.Popen',side_effect=AssertionError('Hosted requests must never execute locally')):
            for code,verdict in [('ACCEPT','Accepted'),('COMPILE','Compile Error'),('CRASH','Runtime Error'),('TIMEOUT','Time Limit Exceeded'),('OUTPUT','Output Limit Exceeded'),('INFRA','Judge Error'),('DELIVERY_UNKNOWN','Judge Error')]:
                key,retry=self.submit(a,code=code);result=self.finished(a,key)['result']
                self.assertEqual(result['verdict'],verdict,code)
                self.assertNotIn('token',json.dumps(result));self.assertNotIn('secret-test-data',json.dumps(result))
                if code in ('INFRA','DELIVERY_UNKNOWN'):self.assertIsNone(result['assessment']['correctness'])
        calls=len(self.provider.calls)
        payload={'problem_id':'fixture-0','problem_version':1,'language':'python','code':'DELIVERY_UNKNOWN'}
        self.assertEqual(a.post('/api/submissions',json=payload,headers={'Idempotency-Key':retry}).json()['job_id'],key)
        self.assertEqual(len(self.provider.calls),calls)

    def test_backup_restore_contains_pinned_content_and_never_overwrites(self):
        a,_=self.team('Alpha');key,_=self.submit(a);self.finished(a,key)
        archive=Path(self.temp.name)/'backup.zip';restored=Path(self.temp.name)/'restored'
        backup(self.runtime,archive);restore(archive,restored)
        storage=Storage(restored/'history.sqlite3',resume_owned=True)
        try:
            self.assertEqual(storage.get(key)['result']['verdict'],'Accepted')
            self.assertEqual(storage.db.execute('PRAGMA user_version').fetchone()[0],3)
            self.assertTrue((restored/'contests'/self.contest/'problems'/'fixture-0'/'problem.json').exists())
        finally:storage.close()
        self.assertRaises(ValueError,restore,archive,restored)

    def test_concurrent_join_and_queue_overload(self):
        registration=self.admin.post(f'/api/organizer/contests/{self.contest}/teams',json={'name':'Concurrent'}).json()
        payload={'contest_id':self.contest,'team_name':'Concurrent','join_code':registration['join_code']}
        clients=[self.client(),self.client()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            responses=list(pool.map(lambda c:c.post('/api/teams/join',json=payload),clients))
        self.assertEqual(sorted(r.status_code for r in responses),[200,409])
        a,_=self.team('Queued A');b,_=self.team('Queued B');c,_=self.team('Queued C')
        self.app.state.jobs.queue.maxsize=1;self.provider.gate.clear()
        first,_=self.submit(a);self.assertTrue(self.provider.started.wait(2))
        second,_=self.submit(b)
        request={'problem_id':'fixture-0','problem_version':1,'language':'python','code':'ACCEPT'}
        rejected=c.post('/api/submissions',json=request,headers={'Idempotency-Key':'not-admitted'})
        self.assertEqual(rejected.status_code,429)
        self.assertEqual(c.get('/api/submissions/me').json(),[])
        self.provider.gate.set();self.finished(a,first);self.finished(b,second)

    def test_restart_resumes_known_tokens_and_refuses_uncertain_creation(self):
        a,data=self.team('Restart')
        self.app.state.jobs.close()
        from app.models import SubmissionRequest
        p=self.app.state.contests.problem(self.contest,'fixture-0')
        request=SubmissionRequest(problem_id='fixture-0',problem_version=1,language='python',code='ACCEPT')
        store=self.app.state.storage
        store.create('resume',request,p.meta.rubric.model_dump(),team_id=data['id'],contest_id=self.contest,idempotency_key='resume')
        for case in p.cases:
            token=self.provider.create('python','ACCEPT',case.stdin,p.meta.limits)
            store.save_provider_case('resume',case.id,'running',token=token)
        count=len(self.provider.calls)
        self.app.state.jobs=HostedJobs(RemoteJudge(self.provider,store),store,self.app.state.contests)
        self.assertEqual(self.finished(a,'resume')['result']['verdict'],'Accepted')
        self.assertEqual(len(self.provider.calls),count)
        self.app.state.jobs.close()
        store.create('uncertain',request,p.meta.rubric.model_dump(),team_id=data['id'],contest_id=self.contest,idempotency_key='uncertain')
        store.save_provider_case('uncertain',p.cases[0].id,'creating')
        self.app.state.jobs=HostedJobs(RemoteJudge(self.provider,store),store,self.app.state.contests)
        result=self.finished(a,'uncertain')['result']
        self.assertEqual(result['verdict'],'Judge Error');self.assertFalse(result['assessment']['complete'])
        self.assertEqual(len(self.provider.calls),count)
        self.assertEqual(a.get('/api/teams/me').json()['metrics']['official_attempts'],2)

    def test_unowned_legacy_history_is_organizer_only(self):
        a,_=self.team('Owner')
        from app.models import SubmissionRequest
        p=self.repository.get('fixture-0')
        self.app.state.storage.create('legacy',SubmissionRequest(problem_id='fixture-0',problem_version=1,language='python',code='old code'),p.meta.rubric.model_dump())
        self.app.state.storage.complete('legacy',{'verdict':'Wrong Answer','assessment':None})
        self.assertEqual(a.get('/api/attempts/legacy').status_code,404)
        self.assertEqual(a.get('/api/jobs/legacy').status_code,404)
        self.assertEqual(a.get('/api/submissions/me').json(),[])
        self.assertEqual(self.admin.get('/api/attempts/legacy').json()['code'],'old code')
        self.assertEqual(self.admin.get('/api/organizer/submissions').json()[0]['id'],'legacy')

    def test_unavailable_provider_languages_byte_limits_and_exact_cors(self):
        a,_=self.team('Limits')
        payload={'problem_id':'fixture-0','problem_version':1,'language':'cpp','code':'ACCEPT'}
        self.provider.ready=False
        self.assertEqual(a.post('/api/runs',json=payload).status_code,503)
        self.provider.ready=True;self.provider.status['cpp']['available']=False
        self.assertEqual(a.post('/api/runs',json=payload).status_code,422)
        self.assertEqual(a.post('/api/runs',json={**payload,'language':'python','code':'\u20ac'*30000}).status_code,413)
        self.assertEqual(a.post('/api/runs',json={**payload,'language':'python','stdin':'x'*1048577}).status_code,413)
        preflight=a.options('/api/submissions',headers={'Origin':ORIGIN,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'X-CSRF-Token,Idempotency-Key'})
        self.assertEqual(preflight.headers['access-control-allow-origin'],ORIGIN)
        self.assertEqual(preflight.headers['access-control-allow-credentials'],'true')
        self.assertNotIn('access-control-allow-origin',a.get('/api/health',headers={'Origin':'https://evil.test'}).headers)
        self.assertEqual(a.get('/api/submissions/me').headers['cache-control'],'no-store')
        self.assertEqual(a.get('/api/submissions/me').json(),[])


if __name__=='__main__':unittest.main()
