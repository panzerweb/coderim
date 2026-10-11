import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
from app.main import create_app
from app.languages import Registry


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = Path(self.temp.name)
        self.app = create_app(runtime=self.runtime, registry=self.registry)
        self.client = TestClient(self.app, base_url='http://127.0.0.1:8000')
        self.client.__enter__()
        self.payload = {'problem_id': 'broken-code-formatter', 'problem_version': 1, 'language': 'python',
            'code': "import sys\nprint('VALID')"}

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def finished(self, key, limit=15):
        start = time.monotonic()
        while time.monotonic() - start < limit:
            response = self.client.get('/api/jobs/' + key)
            self.assertEqual(response.status_code, 200)
            job = response.json()
            if job['state'] in ('completed', 'failed'):
                return job
            time.sleep(.03)
        self.fail('Job did not finish')

    def test_catalog_safe_detail_and_validation(self):
        catalog = self.client.get('/api/problems').json()
        self.assertEqual(catalog[0]['difficulty'], 'Hard')
        problem = self.client.get('/api/problems/broken-code-formatter').json()
        public = json.dumps(problem)
        self.assertNotIn('reference.py', public)
        self.assertNotIn('tests/', public)
        self.assertNotIn('author/', public)
        self.assertFalse(problem['limits']['memory_enforced'])
        self.assertEqual(len(problem['samples']), 6)
        self.assertEqual(self.client.get('/api/problems/unknown').status_code, 404)
        self.assertEqual(self.client.get('/api/unknown').status_code, 404)
        for values, status in [({'problem_version': 2}, 409), ({'language': 'hacked-command'}, 422),
                ({'code': 'é' * 40000}, 413), ({'problem_id': 'missing'}, 404)]:
            self.assertEqual(self.client.post('/api/submissions', json={**self.payload, **values}).status_code, status)
        unavailable = next((key for key, value in self.registry.status.items() if not value['available']), None)
        if unavailable:
            self.assertEqual(self.client.post('/api/submissions', json={**self.payload, 'language': unavailable}).status_code, 422)
        self.assertEqual(self.client.post('/api/runs', json={**self.payload, 'mode': 'custom', 'stdin': 'é' * 600000}).status_code, 413)
        self.assertEqual(self.client.get('/api/jobs/unknown').status_code, 404)

    def test_origin_and_body_protection(self):
        for origin in ('https://evil.example', 'null'):
            self.assertEqual(self.client.post('/api/submissions', json=self.payload, headers={'Origin': origin}).status_code, 403)
        self.assertEqual(self.client.post('/api/submissions', content='code=bad', headers={'Content-Type': 'application/x-www-form-urlencoded'}).status_code, 403)
        self.assertEqual(self.client.post('/api/submissions', content=b'x' * 1200001, headers={'Content-Type': 'application/json'}).status_code, 413)
        self.assertEqual(self.client.get('/api/health', headers={'Host': 'evil.example'}).status_code, 400)

    def test_queue_overload_response(self):
        import queue
        from unittest.mock import patch
        with patch.object(self.app.state.jobs, 'enqueue', side_effect=queue.Full):
            response = self.client.post('/api/submissions', json=self.payload)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers['Retry-After'], '2')

    def test_submit_review_restart_privacy_and_history(self):
        reference = (ROOT / 'problems/broken-code-formatter/author/reference.py').read_text()
        response = self.client.post('/api/submissions', json={**self.payload, 'code': reference}, headers={'Origin': 'http://127.0.0.1:8000'})
        self.assertEqual(response.status_code, 202)
        key = response.json()['attempt_id']
        job = self.finished(key)
        result = job['result']
        self.assertEqual(result['verdict'], 'Accepted')
        self.assertEqual(result['attempted'], 65)
        self.assertEqual(len(result['cases']), 6)
        self.assertIsNone(result['assessment']['final'])
        self.assertNotIn('large-01', json.dumps(result))
        invalid = self.client.put(f'/api/attempts/{key}/review', json={'readability': [5] * 4, 'technical': [4] * 4, 'rationale': 'Bad'})
        self.assertEqual(invalid.status_code, 422)
        reviewed = self.client.put(f'/api/attempts/{key}/review', json={'readability': [3] * 4, 'technical': [4] * 4, 'rationale': 'Readable state transitions and linear algorithm.'}).json()
        self.assertEqual(reviewed['result']['assessment']['final'], 96.25)
        self.client.__exit__(None, None, None)
        self.app = create_app(runtime=self.runtime, registry=self.registry)
        self.client = TestClient(self.app, base_url='http://127.0.0.1:8000'); self.client.__enter__()
        saved = self.client.get(f'/api/attempts/{key}').json()
        self.assertEqual(saved['code'], reference)
        self.assertEqual(saved['result']['assessment']['final'], 96.25)
        self.assertEqual(self.client.get('/api/jobs/' + key).status_code, 404)
        listed = self.client.get('/api/attempts', params={'problem_id': 'broken-code-formatter', 'problem_version': 1, 'language': 'python'}).json()
        self.assertEqual(listed[0]['id'], key)
        self.assertNotIn('code', listed[0])
        self.assertNotIn('cases', listed[0]['result'])

    def test_custom_sample_modes_and_responsiveness(self):
        response = self.client.post('/api/runs', json={**self.payload, 'mode': 'custom', 'stdin': 'user input\n', 'code': 'import sys\nsys.stdout.write(sys.stdin.read())'})
        job = self.finished(response.json()['job_id'])
        self.assertEqual(job['result']['verdict'], 'Completed')
        self.assertIsNone(job['result']['assessment'])
        sample = self.client.post('/api/runs', json={**self.payload, 'mode': 'samples'})
        self.assertEqual(self.finished(sample.json()['job_id'])['result']['total'], 6)
        response = self.client.post('/api/runs', json={**self.payload, 'mode': 'custom', 'code': 'import time\ntime.sleep(.5)'})
        started = time.monotonic()
        self.assertEqual(self.client.get('/api/health').status_code, 200)
        self.assertLess(time.monotonic() - started, .4)
        self.finished(response.json()['job_id'])
        self.assertEqual(self.client.get('/api/attempts', params={'problem_id': 'broken-code-formatter', 'problem_version': 1, 'language': 'python'}).json(), [])


if __name__ == '__main__':
    unittest.main()
