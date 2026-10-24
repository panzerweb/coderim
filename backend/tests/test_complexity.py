import copy
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
from app.models import MAX_REQUEST_BYTES, MAX_STDIN_BYTES, MAX_SOURCE_BYTES, ReferenceComplexity, ReviewedComplexity, ReviewRequest, SubmissionRequest
from app.storage import Storage
from app.main import create_app
from app.languages import Registry
from app.problems import load_problem
from fastapi.testclient import TestClient


def analysis(**updates):
    return {'status': 'assessed', 'worst_case_time': 'O(N + Q log N)', 'auxiliary_space': 'O(N)',
        'total_space': 'O(N + Q)', 'reasoning': 'A segment tree serves queries; this implementation retains answers.', **updates}


class ComplexityTests(unittest.TestCase):
    def test_bounds_are_annotations_with_explicit_unknown(self):
        self.assertEqual(ReviewedComplexity(**analysis()).status, 'assessed')
        for changes in ({'worst_case_time': None}, {'auxiliary_space': ' '}, {'total_space': None}, {'reasoning': ' '}):
            self.assertRaises(ValueError, ReviewedComplexity, **analysis(**changes))
        unknown = ReviewedComplexity(status='unable_to_assess', reasoning='Insufficient code to establish a bound.')
        self.assertIsNone(unknown.worst_case_time)
        self.assertRaises(ValueError, ReviewedComplexity, status='unable_to_assess', reasoning=' ', worst_case_time=None)
        self.assertRaises(ValueError, ReviewedComplexity, **analysis(status='unable_to_assess'))
        self.assertGreaterEqual(MAX_REQUEST_BYTES, 6 * (MAX_SOURCE_BYTES + MAX_STDIN_BYTES))

    def test_migrate_v1_and_preserve_completed_history_and_scores(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'db.sqlite3'
            database = sqlite3.connect(path)
            database.executescript('''CREATE TABLE attempts (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, problem_id TEXT NOT NULL,
                problem_version INTEGER NOT NULL, language TEXT NOT NULL, code TEXT NOT NULL,
                rubric_json TEXT NOT NULL, status TEXT NOT NULL, result_json TEXT, review_json TEXT);
                PRAGMA user_version=1;''')
            rubric = {'version': 1, 'weights': {'correctness': 50, 'requirements': 20, 'readability': 15, 'technical': 15},
                'readability': ['a'] * 4, 'technical': ['a'] * 4}
            result = {'verdict': 'Accepted', 'assessment': {'complete': True, 'correctness': 100, 'requirements': 100}}
            review = {'readability': [4] * 4, 'technical': [4] * 4, 'rationale': 'Original review.'}
            originals = ('old', '2026-10-01T00:00:00+00:00', 'p', 1, 'python', 'print("original")',
                json.dumps(rubric), 'completed', json.dumps(result), json.dumps(review))
            database.execute('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?,?,?)', originals)
            database.commit(); database.close()
            storage = Storage(path)
            self.assertEqual(storage.db.execute('PRAGMA user_version').fetchone()[0], 2)
            self.assertEqual(tuple(storage.db.execute('SELECT id, created_at, problem_id, problem_version, language, code, rubric_json, status, result_json, review_json FROM attempts').fetchone()), originals)
            old = storage.get('old')
            self.assertIsNone(old['reference_complexity'])
            self.assertIsNone(old['review'].get('complexity'))
            self.assertEqual(old['result']['assessment']['final'], 100)
            storage.close()
            storage = Storage(path)  # Migration is idempotent.
            self.assertEqual(storage.get('old')['result']['assessment']['final'], 100)
            storage.close()

    def test_context_is_frozen_legacy_reviews_preserve_analysis(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'db'
            store = Storage(path)
            problem = load_problem(ROOT / 'problems/longest-rising-streak-updates')
            context = problem.meta.reference_complexity.model_dump()
            request = SubmissionRequest(problem_id=problem.meta.id, problem_version=1, language='python', code='print(1)')
            store.create('new', request, problem.meta.rubric.model_dump(), context)
            context['auxiliary_space'] = 'O(N squared)'
            store.complete('new', {'verdict': 'Wrong Answer', 'assessment': {'complete': True, 'correctness': 50, 'requirements': 25}})
            reviewed = store.review('new', ReviewRequest(readability=[3] * 4, technical=[2] * 4,
                rationale='Original rationale', complexity=analysis()))
            score = reviewed['result']['assessment']['final']
            reviewed = store.review('new', ReviewRequest(readability=[3] * 4, technical=[2] * 4, rationale='Legacy edit'))
            self.assertEqual(reviewed['review']['complexity']['worst_case_time'], 'O(N + Q log N)')
            self.assertEqual(reviewed['reference_complexity']['auxiliary_space'], 'O(N) per test case')
            reviewed = store.review('new', ReviewRequest(readability=[3] * 4, technical=[2] * 4,
                rationale='Cannot establish the bound', complexity={'status': 'unable_to_assess', 'reasoning': 'External library contract is unspecified.'}))
            self.assertEqual(reviewed['result']['assessment']['final'], score)
            self.assertEqual(reviewed['result']['verdict'], 'Wrong Answer')
            self.assertIsNone(reviewed['review']['complexity']['worst_case_time'])
            store.close(); store = Storage(path)
            self.assertEqual(store.get('new')['review']['complexity']['status'], 'unable_to_assess')
            self.assertEqual(store.get('new')['reference_complexity']['auxiliary_space'], 'O(N) per test case')
            store.close()

    def test_migration_rolls_back_on_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'invalid.db'
            # Version 1 with an unexpected table shape: the migration must not
            # partially add its new column or advance the schema version.
            connection = sqlite3.connect(path)
            connection.executescript('CREATE TABLE attempts (id TEXT); PRAGMA user_version=1;')
            connection.close()
            self.assertRaises(sqlite3.OperationalError, Storage, path)
            connection = sqlite3.connect(path)
            self.assertEqual(connection.execute('PRAGMA user_version').fetchone()[0], 1)
            self.assertEqual([r[1] for r in connection.execute('PRAGMA table_info(attempts)')], ['id'])
            connection.close()


class LargeInputApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry()

    def test_new_limits_safe_dtos_and_json_expansion(self):
        with tempfile.TemporaryDirectory() as temp:
            app = create_app(runtime=Path(temp), registry=self.registry)
            with TestClient(app, base_url='http://127.0.0.1:8000') as client:
                self.assertEqual(len(client.get('/api/problems').json()), 3)
                for slug in ('longest-rising-streak-updates', 'g-tree-changing-root'):
                    detail = client.get('/api/problems/' + slug).json()
                    self.assertEqual(detail['limits']['stdin_bytes'], MAX_STDIN_BYTES)
                    self.assertEqual(detail['limits']['time_ms'], 5000)
                    self.assertIsNotNone(detail['reference_complexity'])
                    self.assertNotIn('reference.py', json.dumps(detail))
                    self.assertNotIn('scale-chain', json.dumps(detail))
                payload = {'problem_id': 'longest-rising-streak-updates', 'problem_version': 1,
                    'language': 'python', 'code': 'print(1)', 'mode': 'custom'}
                accepted = {'job_id': 'test', 'attempt_id': None}
                with patch.object(app.state.jobs, 'enqueue', return_value=accepted) as enqueue:
                    # Payload grows to >6 MiB in JSON but decodes to just >1 MiB.
                    response = client.post('/api/runs', json={**payload, 'stdin': '\x00' * (1024 * 1024 + 1)})
                    self.assertEqual(response.status_code, 202)
                    self.assertGreater(len(enqueue.call_args.args[0].stdin), 1024 * 1024)
                response = client.post('/api/runs', json={**payload, 'stdin': 'é' * (MAX_STDIN_BYTES // 2 + 1)})
                self.assertEqual(response.status_code, 413)
                # Existing formatter keeps its original lower limit.
                self.assertEqual(client.post('/api/runs', json={**payload, 'problem_id': 'broken-code-formatter', 'stdin': 'x' * (1024 * 1024 + 1)}).status_code, 413)
                self.assertEqual(client.post('/api/runs', json={**payload, 'stdin': 'x' * (MAX_STDIN_BYTES + 1)}).status_code, 422)
                with patch('app.main.MAX_REQUEST_BYTES', 2048):
                    self.assertEqual(client.post('/api/runs', content=b'x' * 2049, headers={'Content-Type': 'application/json'}).status_code, 413)


if __name__ == '__main__':
    unittest.main()
