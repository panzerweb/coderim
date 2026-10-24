import base64
import hashlib
import hmac
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import httpx
from starlette.responses import Response

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'))
from app.auth import Auth
from app.remote_judge import Judge0Client,ProviderError,RemoteJudge
from app.models import Limits
from app.problems import Repository
from app.storage import Storage
from hosted_support import FakeProvider


class ManagedProviderTests(unittest.TestCase):
    def test_transport_keeps_expected_outputs_private_and_uses_execution_limits(self):
        requests=[]
        def handle(request):
            requests.append(request)
            if request.method=='POST':return httpx.Response(201,json={'token':'private-token'})
            return httpx.Response(200,json={'status':{'id':3},'stdout':base64.b64encode(b'wrong').decode()})
        with tempfile.TemporaryDirectory() as temp:
            client=Judge0Client(temp,'x'*32,client=httpx.Client(transport=httpx.MockTransport(handle)),
                url='https://judge.example',headers={'X-Auth-Token':'private-key'},language_ids={'python':71})
            token=client.create('python','print(1)','private input',Limits())
            payload=json.loads(requests[0].content)
            self.assertNotIn('expected_output',payload)
            self.assertEqual(base64.b64decode(payload['stdin']),b'private input')
            self.assertFalse(payload['enable_network']);self.assertEqual(payload['memory_limit'],262144)
            self.assertEqual(payload['cpu_time_limit'],2)
            self.assertEqual(client.result(token)['status']['id'],3)
            self.assertNotIn('private-key',json.dumps(client.public()))
            client.close()

    def test_http_errors_malformed_response_and_bound(self):
        for response in [httpx.Response(429,json={}),httpx.Response(503,text='private-key'),httpx.Response(200,text='bad json'),httpx.Response(200,content=b'x'*(8*1024*1024+1))]:
            with tempfile.TemporaryDirectory() as temp:
                client=Judge0Client(temp,'x'*32,client=httpx.Client(transport=httpx.MockTransport(lambda request:response)),url='https://judge.example',headers={'key':'private-key'},language_ids={'python':71})
                with self.assertRaises(ProviderError) as failure:client.request('GET','/languages')
                self.assertNotIn('private-key',str(failure.exception));client.close()

    def test_signed_verification_accepts_pinned_subset_and_rejects_content_or_configuration_changes(self):
        repo=Repository(ROOT/'problems')
        with tempfile.TemporaryDirectory() as temp:
            client=Judge0Client(temp,'x'*32,url='https://judge.example',headers={'key':'secret'},language_ids={'python':71})
            data={'fingerprint':client.fingerprint(repo),'verified_at':'test'}
            data['signature']=hmac.new(b'x'*32,json.dumps(data,sort_keys=True).encode(),hashlib.sha256).hexdigest()
            client.receipt.write_text(json.dumps(data))
            self.assertTrue(client.refresh(repo))
            problem=next(iter(repo.published()))
            subset=SimpleNamespace(published=lambda:[problem])
            self.assertTrue(client.refresh(subset))
            before=problem.meta.title;problem.meta.title='Changed'
            self.assertFalse(client.refresh(subset));problem.meta.title=before
            client.language_ids['python']=999
            self.assertFalse(client.refresh(subset));client.close()

    def test_budget_partial_progress_and_malformed_timing_are_incomplete(self):
        repo=Repository(ROOT/'problems');p=repo.get('broken-code-formatter')
        with tempfile.TemporaryDirectory() as temp:
            store=Storage(Path(temp)/'db');provider=FakeProvider(repo)
            with patch('app.remote_judge.time.monotonic',side_effect=[0,1,1]):
                result=RemoteJudge(provider,store,budget=.000001).run(p,'python','ACCEPT')
            self.assertFalse(result['assessment']['complete']);self.assertIsNone(result['assessment']['correctness'])
            self.assertEqual(provider.calls,[])
            with patch.object(provider,'result',return_value={'status':{'id':3},'stdout':'','time':'NaN'}):
                result=RemoteJudge(provider,store).run(p,'python','ACCEPT')
            self.assertFalse(result['assessment']['complete']);store.close()

    def test_v2_migration_preserves_source_results_review_and_context(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'db';db=sqlite3.connect(path)
            db.executescript('CREATE TABLE attempts(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,problem_id TEXT NOT NULL,problem_version INTEGER NOT NULL,language TEXT NOT NULL,code TEXT NOT NULL,rubric_json TEXT NOT NULL,status TEXT NOT NULL,result_json TEXT,review_json TEXT,complexity_context_json TEXT); PRAGMA user_version=2;')
            rubric=Repository(ROOT/'problems').get('broken-code-formatter').meta.rubric.model_dump()
            original=('old','2026-01-01T00:00:00+00:00','broken-code-formatter',1,'python','original',json.dumps(rubric),'completed',json.dumps({'verdict':'Accepted','assessment':{'complete':True,'correctness':100,'requirements':100}}),json.dumps({'readability':[4]*4,'technical':[4]*4,'rationale':'old review'}),json.dumps({'auxiliary_space':'O(L)'}))
            db.execute('INSERT INTO attempts VALUES(?,?,?,?,?,?,?,?,?,?,?)',original);db.commit();db.close()
            store=Storage(path,resume_owned=True)
            self.assertEqual(tuple(store.db.execute('SELECT id,created_at,problem_id,problem_version,language,code,rubric_json,status,result_json,review_json,complexity_context_json FROM attempts').fetchone()),original)
            self.assertEqual(store.get('old')['result']['assessment']['final'],100)
            auth=Auth(store,'x'*32,{'https://app.example.com'})
            organizer=auth.create_organizer('test','a-long-password')
            response=Response();auth.issue('organizer',organizer,response)
            cookie=response.headers['set-cookie']
            for value in ('__Host-relay_organizer=','Secure','HttpOnly','SameSite=strict','Path=/'):self.assertIn(value,cookie)
            self.assertNotIn('Domain=',cookie)
            self.assertEqual(store.db.execute('PRAGMA foreign_keys').fetchone()[0],1)
            self.assertEqual(store.db.execute('PRAGMA busy_timeout').fetchone()[0],5000)
            self.assertEqual(store.db.execute('PRAGMA journal_mode').fetchone()[0],'wal');store.close()

    def test_ambiguous_delivery_holds_provider_across_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            def lost(request):raise httpx.ReadTimeout('response lost')
            client=Judge0Client(temp,'x'*32,client=httpx.Client(transport=httpx.MockTransport(lost)),url='https://judge.example',headers={'key':'secret'},language_ids={'python':71})
            self.assertRaises(ProviderError,client.create,'python','print(1)','',Limits())
            self.assertTrue(client.hold_file.exists());client.close()
            client=Judge0Client(temp,'x'*32,url='https://judge.example',headers={'key':'secret'},language_ids={'python':71})
            self.assertRaises(ProviderError,client.create,'python','print(1)','',Limits());client.close()

    def test_restart_preserves_job_budget(self):
        repo=Repository(ROOT/'problems');p=repo.get('broken-code-formatter')
        from app.models import SubmissionRequest
        with tempfile.TemporaryDirectory() as temp:
            store=Storage(Path(temp)/'db')
            store.create('budget',SubmissionRequest(problem_id=p.meta.id,problem_version=1,language='python',code='ACCEPT'),p.meta.rubric.model_dump())
            store.remote_job('budget',600)
            with store.db:store.db.execute("UPDATE provider_jobs SET started_at='2020-01-01T00:00:00+00:00'")
            provider=FakeProvider(repo)
            result=RemoteJudge(provider,store,budget=999999).run(p,'python','ACCEPT',attempt_id='budget')
            self.assertFalse(result['assessment']['complete']);self.assertEqual(provider.calls,[]);store.close()
