import importlib.util
import itertools
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
sys.path.insert(0, str(ROOT / 'tools'))
from app.execution import execute
from app.judge import Judge, assessment, normalize
from app.jobs import Jobs
from app.languages import LANGUAGES, Registry
from app.models import Checker, Limits, ProblemMetadata, ReviewRequest, SubmissionRequest
from app.problems import Case, Problem, Repository, load_problem, safe_path
from app.storage import Storage
from scaffold_problem import scaffold


def small_problem(time_ms=1000):
    meta = ProblemMetadata(id='test-problem', version=1, title='Test', difficulty='Easy', tags=[],
        status='published', category_weights={'behavior': 100}, requirements=[{'id': 'r', 'text': 'Behavior'}],
        limits=Limits(time_ms=time_ms, stdout_bytes=4096, stderr_bytes=1024))
    return Problem(meta, 'Test', (), (Case('sample', 'x\n', 'VALID\n', 'behavior', ('r',), True),
        Case('private', 'secret-test-data\n', 'VALID\n', 'behavior', ('r',))), {})


class ContentTests(unittest.TestCase):
    def test_package_and_reference_independent_oracle(self):
        p = load_problem(ROOT / 'problems/broken-code-formatter')
        self.assertEqual(len(p.samples), 6)
        spec = importlib.util.spec_from_file_location('reference', ROOT / 'problems/broken-code-formatter/author/reference.py')
        reference = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reference)
        quoted = re.compile(r'''"(?:\\[\s\S]|[^"\\])*"|'(?:\\[\s\S]|[^'\\])*' ''', re.VERBOSE)
        def oracle(source):
            without_strings = quoted.sub('', source)
            if '"' in without_strings or "'" in without_strings:
                return False
            brackets = ''.join(c for c in without_strings if c in '()[]{}')
            while True:
                reduced = brackets.replace('()', '').replace('[]', '').replace('{}', '')
                if reduced == brackets:
                    return not reduced
                brackets = reduced
        for length in range(6):
            for chars in itertools.product('()[]\'"\\a', repeat=length):
                source = ''.join(chars)
                self.assertEqual(reference.validate(source), oracle(source), repr(source))
        for c in p.cases:
            source = c.stdin.removesuffix('\n').removesuffix('\r')
            self.assertGreaterEqual(len(source), 1)
            self.assertLessEqual(len(source), 100000)
            self.assertTrue(source.isascii())
            self.assertEqual(('VALID' if reference.validate(source) else 'INVALID') + '\n', c.expected)

    def test_safe_paths_and_invalid_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            p = scaffold('echo', root)
            self.assertRaises(ValueError, safe_path, p, '../escape')
            self.assertRaises(ValueError, safe_path, p, str(ROOT / 'code_relay_judge_implementation_plan.md'))
            self.assertRaises(ValueError, safe_path, p, 'missing')
            for mutate in [
                lambda m: m.update(schema_version=2),
                lambda m: m.update(id='wrong-folder'),
                lambda m: m.update(category_weights={'missing': 100}),
                lambda m: m.update(category_weights={'behavior': 90}),
                lambda m: m.update(checker={'type': 'arbitrary-code'}),
                lambda m: m.update(requirements=[{'id': 'uncovered', 'text': 'Missing'}]),
            ]:
                path = p / 'problem.json'
                original = path.read_text()
                metadata = json.loads(original); mutate(metadata)
                path.write_text(json.dumps(metadata))
                self.assertRaises(ValueError, load_problem, p)
                path.write_text(original)
            samples = json.loads((p / 'samples.json').read_text())
            samples[0]['id'] = 'hidden-01'
            (p / 'samples.json').write_text(json.dumps(samples))
            self.assertRaises(ValueError, load_problem, p)
            self.assertIn('echo', Repository(root).errors)

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); package = scaffold('echo', root)
            try:
                (package / 'link').symlink_to(ROOT / 'code_relay_judge_implementation_plan.md')
            except OSError:
                self.skipTest('Creating symlinks requires an OS privilege on this machine')
            self.assertRaises(ValueError, safe_path, package, 'link')

    def test_raw_transport_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            p = scaffold('echo', Path(temp))
            (p / 'tests/spaces.in').write_bytes(b'  preserved spaces  \r\n')
            self.assertTrue(load_problem(p).cases[-1].stdin.endswith('\r\n'))


class ComparatorTests(unittest.TestCase):
    def test_normalization_preserves_meaning(self):
        checker = Checker()
        self.assertEqual(normalize('VALID \t\r\n', checker), 'VALID')
        self.assertEqual(normalize('a\rb', checker), 'a\nb')
        for actual in (' VALID', 'valid', 'VALID\n\n', 'VAL ID', 'debug\nVALID'):
            self.assertNotEqual(normalize(actual, checker), 'VALID')
        self.assertEqual(normalize(' a b \n', checker), ' a b')
        self.assertEqual(normalize('x \r\n', Checker(normalize_line_endings=False, trim_trailing_whitespace_per_line=False, ignore_final_newline=False)), 'x \r\n')


class JudgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.judge = Judge(self.registry, self.directory)

    def tearDown(self):
        self.temp.cleanup()

    def test_full_suite_first_failure_and_privacy(self):
        p = small_problem()
        result = self.judge.run(p, 'python', "import sys\nprint('INVALID' if sys.stdin.readline().strip() == 'x' else 'VALID')")
        self.assertEqual(result['verdict'], 'Wrong Answer')
        self.assertEqual((result['attempted'], result['passed']), (2, 1))
        self.assertEqual(result['assessment']['correctness'], 50)
        self.assertEqual(result['assessment']['requirements'], 0)
        self.assertEqual(len(result['cases']), 1)
        self.assertNotIn('secret-test-data', json.dumps(result))
        self.assertIsNone(result['assessment']['final'])
        self.assertFalse(list(self.directory.iterdir()))

    def test_faulty_programs_and_cleanup(self):
        cases = [("print('VALID')", 'Accepted'), ("print('INVALID')", 'Wrong Answer'),
            ('this is invalid syntax!', 'Compile Error'), ('raise RuntimeError("oops")', 'Runtime Error'),
            ('while True: pass', 'Time Limit Exceeded'), ("print('x' * 100000)", 'Output Limit Exceeded'),
            ("import sys\nsys.stderr.write('x' * 100000)", 'Output Limit Exceeded')]
        for code, verdict in cases:
            with self.subTest(verdict=verdict, code=code):
                result = self.judge.run(small_problem(100 if verdict == 'Time Limit Exceeded' else 1000), 'python', code)
                self.assertEqual(result['verdict'], verdict)
                self.assertEqual(result['assessment']['correctness'], 100 if verdict == 'Accepted' else 0)
                self.assertFalse(list(self.directory.iterdir()))

    def test_custom_has_no_assessment(self):
        result = self.judge.run(small_problem(), 'python', 'import sys\nprint(sys.stdin.read(), end="")', 'custom', 'abc\n')
        self.assertEqual(result['verdict'], 'Completed')
        self.assertEqual(result['cases'][0]['stdout'].replace('\r\n', '\n'), 'abc\n')
        self.assertIsNone(result['assessment'])

    def test_budget_is_incomplete(self):
        judge = Judge(self.registry, self.directory, job_budget=.25)
        result = judge.run(small_problem(1000), 'python', 'import time\ntime.sleep(.4)\nprint("VALID")')
        self.assertEqual(result['verdict'], 'Judge Error')
        self.assertFalse(result['assessment']['complete'])
        self.assertIsNone(result['assessment']['correctness'])

    def test_cancel_and_infrastructure_failure(self):
        cancel = threading.Event(); cancel.set()
        with self.assertLogs(level='ERROR'):
            result = self.judge.run(small_problem(), 'python', 'print("VALID")', cancel=cancel)
        self.assertFalse(result['assessment']['complete'])
        from unittest.mock import patch
        with patch('app.judge.execute', side_effect=OSError('secret-test-data')), self.assertLogs(level='ERROR'):
            result = self.judge.run(small_problem(), 'python', 'print("VALID")')
        self.assertEqual(result['verdict'], 'Judge Error')
        self.assertNotIn('secret-test-data', json.dumps(result))

    def test_tree_termination_even_when_parent_exits(self):
        marker = self.directory / 'child-survived'
        child = f'import time; time.sleep(1); open({str(marker)!r}, "w").write("bad")'
        parent = 'import subprocess,sys,time\nsubprocess.Popen([sys.executable,"-c",' + repr(child) + '])\n'
        cwd = self.directory / 'case'; cwd.mkdir()
        result = execute([sys.executable, '-c', parent], cwd, '', 2, 4096, 4096)
        self.assertEqual(result.verdict, 'OK')
        time.sleep(1.2)
        self.assertFalse(marker.exists())
        loop = parent + 'while True: time.sleep(.1)\n'
        result = execute([sys.executable, '-c', loop], cwd, '', .15, 4096, 4096)
        self.assertEqual(result.verdict, 'Time Limit Exceeded')
        time.sleep(1.2)
        self.assertFalse(marker.exists())

    def test_output_limit_detected_without_waiting_for_full_buffer(self):
        cwd = self.directory / 'bounded'; cwd.mkdir()
        code = 'import sys,time\nsys.stdout.write("xx");sys.stdout.flush();time.sleep(2)'
        result = execute([sys.executable, '-c', code], cwd, '', 1, 1, 4096)
        self.assertEqual(result.verdict, 'Output Limit Exceeded')
        self.assertEqual(result.stdout, 'x')

    def test_reference_and_installed_languages(self):
        p = load_problem(ROOT / 'problems/broken-code-formatter')
        reference = (ROOT / 'problems/broken-code-formatter/author/reference.py').read_text()
        result = self.judge.run(p, 'python', reference)
        self.assertEqual(result['verdict'], 'Accepted')
        self.assertEqual(result['attempted'], len(p.cases))
        self.assertEqual(result['assessment']['requirements'], 100)
        programs = {'javascript': "console.log('VALID')", 'cpp': '#include <iostream>\nint main(){std::cout << "VALID\\n";}',
            'java': 'public class Main { public static void main(String[] a){System.out.println("VALID");} }'}
        for language, code in programs.items():
            if self.registry.status[language]['available']:
                result = self.judge.run(small_problem(2000), language, code)
                self.assertEqual(result['verdict'], 'Accepted', language)

    def test_extension_without_core_changes(self):
        root = self.directory / 'problems'
        package = scaffold('second-problem', root)
        metadata = json.loads((package / 'problem.json').read_text()); metadata['status'] = 'published'
        (package / 'problem.json').write_text(json.dumps(metadata))
        repo = Repository(root)
        self.assertEqual(repo.published()[0].meta.id, 'second-problem')
        result = self.judge.run(repo.get('second-problem'), 'python', (package / 'author/reference.py').read_text())
        self.assertEqual(result['verdict'], 'Accepted')


class ScoringStorageTests(unittest.TestCase):
    def test_exact_weighted_scoring(self):
        p = load_problem(ROOT / 'problems/broken-code-formatter')
        outcomes = [{'id': c.id, 'verdict': 'Accepted' if c.category != 'escapes' else 'Wrong Answer'} for c in p.cases]
        score = assessment(p, outcomes, True)
        self.assertEqual(score['correctness'], 80)
        self.assertEqual(score['requirements'], 50)
        incomplete = assessment(p, outcomes[:1], False)
        self.assertIsNone(incomplete['correctness'])

    def test_reviews_snapshots_restart_and_filters(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'history.sqlite3'
            storage = Storage(path)
            p = small_problem()
            request = SubmissionRequest(problem_id=p.meta.id, problem_version=1, language='python', code='print("VALID")')
            storage.create('a', request, p.meta.rubric.model_dump())
            storage.complete('a', {'verdict': 'Accepted', 'assessment': assessment(p, [{'id': c.id, 'verdict': 'Accepted'} for c in p.cases], True), 'cases': []})
            saved = storage.review('a', ReviewRequest(readability=[4, 3, 2, 1], technical=[4, 4, 4, 4], rationale='Clear source with some naming gaps.'))
            self.assertEqual(saved['result']['assessment']['readability'], 62.5)
            self.assertEqual(saved['result']['assessment']['technical'], 100)
            self.assertEqual(saved['result']['assessment']['final'], 94.38)
            # Completed judge results are immutable; only review changes are accepted.
            storage.complete('a', {'verdict': 'Wrong Answer'})
            storage.create('pending', request, p.meta.rubric.model_dump())
            storage.close()
            storage = Storage(path)
            self.assertEqual(storage.get('a')['code'], request.code)
            self.assertEqual(storage.get('a')['result']['assessment']['final'], 94.38)
            self.assertEqual(storage.get('pending')['status'], 'interrupted')
            self.assertEqual(storage.list(p.meta.id, 2, 'python'), [])
            self.assertEqual(storage.list(p.meta.id, 1, 'javascript'), [])
            self.assertNotIn('code', storage.list(p.meta.id, 1, 'python')[0])
            storage.close()

    def test_review_validation(self):
        for rating in (-1, 5, 1.5, True, '4'):
            self.assertRaises(ValueError, ReviewRequest, readability=[rating, 4, 4, 4], technical=[4] * 4, rationale='Review')
        self.assertRaises(ValueError, ReviewRequest, readability=[4] * 4, technical=[4] * 4, rationale=' ')

    def test_bounded_queue_and_expiry(self):
        class FakeJudge:
            def run(self, *args):
                entered.set(); release.wait(2)
                return {'verdict': 'Completed'}
        with tempfile.TemporaryDirectory() as temp:
            entered, release = threading.Event(), threading.Event()
            storage = Storage(Path(temp) / 'db')
            jobs = Jobs(FakeJudge(), storage, capacity=1, retention=.03)
            req = SubmissionRequest(problem_id='test-problem', problem_version=1, language='python', code='x')
            a = jobs.enqueue(req, small_problem(), 'samples')['job_id']
            self.assertTrue(entered.wait(1))
            jobs.enqueue(req, small_problem(), 'samples')
            import queue
            self.assertRaises(queue.Full, jobs.enqueue, req, small_problem(), 'samples')
            release.set(); jobs.queue.join(); time.sleep(.05)
            self.assertIsNone(jobs.get(a))
            jobs.close(); storage.close()


if __name__ == '__main__':
    unittest.main()
