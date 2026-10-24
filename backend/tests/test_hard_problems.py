import io
import random
import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'backend'))
from hard_problem_content import generate_streak, generate_tree, module, streak_input, streak_oracle, tree_input, tree_oracle
from app.problems import load_problem, MAX_PACKAGE_BYTES, MAX_CASES


class HardProblemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.streak_root = ROOT / 'problems/longest-rising-streak-updates'
        cls.tree_root = ROOT / 'problems/g-tree-changing-root'
        cls.streak = module(cls.streak_root)
        cls.tree = module(cls.tree_root)

    def test_streak_randomized_updates_and_all_ranges(self):
        rng = random.Random(2481)
        for _ in range(200):
            n = rng.randrange(1, 35)
            values = [rng.randrange(-5, 6) for _ in range(n)]
            tree = self.streak.SegmentTree(values)
            for _ in range(30):
                if rng.randrange(3) == 0:
                    p, x = rng.randrange(n), rng.randrange(-5, 6)
                    values[p] = x; tree.update(p, x)
                l, r = sorted((rng.randrange(n), rng.randrange(n)))
                expected = int(streak_oracle([(values, [('QUERY', l + 1, r + 1)])]))
                self.assertEqual(tree.query(l, r), expected)

    def test_streak_merge_identity_and_order(self):
        rng = random.Random(2482)
        for _ in range(1000):
            values = [rng.randrange(-5, 6) for _ in range(rng.randrange(1, 30))]
            split = rng.randrange(len(values) + 1)
            def fold(part):
                answer = None
                for x in part:
                    answer = self.streak.merge(answer, (1, x, x, 1, 1, 1))
                return answer
            self.assertEqual(self.streak.merge(fold(values[:split]), fold(values[split:])), fold(values))
        self.assertNotEqual(self.streak.merge((1, 1, 1, 1, 1, 1), (1, 2, 2, 1, 1, 1)),
            self.streak.merge((1, 2, 2, 1, 1, 1), (1, 1, 1, 1, 1, 1)))

    def test_changing_roots_against_brute_force(self):
        rng = random.Random(2483)
        for _ in range(100):
            n = rng.randrange(1, 22)
            edges = [(rng.randrange(1, v), v) for v in range(2, n + 1)]
            rng.shuffle(edges)
            tree = self.tree.AncestorTree(n, [(p - 1, c - 1) for p, c in edges])
            operations = []
            actual = []
            for root in range(1, n + 1):
                operations.append(('ROOT', root))
                for u in range(1, n + 1):
                    for v in range(1, n + 1):
                        operations.append(('QUERY', u, v))
                        actual.append('YES\n' if tree.ancestor(root - 1, u - 1, v - 1) else 'NO\n')
            self.assertEqual(''.join(actual), tree_oracle(n, edges, operations))

    def test_saved_packages_limits_scale_and_sample_outputs(self):
        for root in (self.streak_root, self.tree_root):
            p = load_problem(root)
            self.assertLessEqual(len(p.cases), MAX_CASES)
            self.assertLessEqual(sum(len(c.stdin.encode()) + len(c.expected.encode()) for c in p.cases), MAX_PACKAGE_BYTES)
            self.assertTrue(any(len(c.stdin.encode()) > 1048576 for c in p.cases))
            self.assertEqual(len(p.meta.requirements), 4)
            self.assertEqual(p.meta.version, 1)
            self.assertEqual(p.meta.rubric.weights, {'correctness': 50, 'requirements': 20, 'readability': 15, 'technical': 15})
            self.assertTrue(all('TODO' in value for value in p.starters.values()))
        p = load_problem(self.streak_root)
        self.assertEqual([s.expected_output for s in p.samples], ['4\n3\n', '4\n4\n7\n1\n', '2\n2\n1\n'])
        outputs = next(c for c in p.cases if c.id == 'scale-many-outputs')
        self.assertGreater(len(outputs.expected.encode()), 1048576)
        self.assertEqual(outputs.expected, '10000\n' * 180000)
        chain = next(c for c in load_problem(self.tree_root).cases if c.id == 'scale-chain')
        self.assertEqual(chain.expected, 'YES\nNO\n' * 25000)
        maximum = next(c for c in p.cases if c.id == 'scale-max')
        self.assertEqual(maximum.expected, '100000\n' + '100000\n50001\n' * 24999 + '100000\n')
        star = next(c for c in load_problem(self.tree_root).cases if c.id == 'scale-star')
        self.assertEqual(star.expected, 'YES\n' * 49999 + 'NO\n')

    def test_all_saved_inputs_obey_the_published_contracts(self):
        for c in load_problem(self.streak_root).cases:
            data = iter(c.stdin.split()); count = int(next(data)); size = 0
            self.assertTrue(1 <= count <= 10)
            for _ in range(count):
                n, q = int(next(data)), int(next(data)); size += n + q
                self.assertTrue(1 <= n <= 100000 and 1 <= q <= 100000)
                self.assertTrue(all(-1000000 <= int(next(data)) <= 1000000 for _ in range(n)))
                for _ in range(q):
                    command, a, b = next(data), int(next(data)), int(next(data))
                    if command == 'UPDATE':
                        self.assertTrue(1 <= a <= n and -1000000 <= b <= 1000000)
                    else:
                        self.assertEqual(command, 'QUERY'); self.assertTrue(1 <= a <= b <= n)
            self.assertLessEqual(size, 200000)
            self.assertIsNone(next(data, None))
        for c in load_problem(self.tree_root).cases:
            data = iter(c.stdin.split()); n = int(next(data))
            parents = [0] * (n + 1); adjacent = [[] for _ in range(n + 1)]
            for _ in range(n - 1):
                parent, child = int(next(data)), int(next(data))
                self.assertTrue(1 <= parent <= n and 2 <= child <= n)
                self.assertEqual(parents[child], 0); parents[child] = parent
                adjacent[parent].append(child)
            visited = set(); stack = [1]
            while stack:
                node = stack.pop(); self.assertNotIn(node, visited); visited.add(node); stack.extend(adjacent[node])
            self.assertEqual(len(visited), n)
            q = int(next(data)); self.assertTrue(1 <= q <= 100000)
            for _ in range(q):
                command, node = next(data), int(next(data)); self.assertTrue(1 <= node <= n)
                if command != 'ROOT':
                    self.assertEqual(command, 'QUERY'); self.assertTrue(1 <= int(next(data)) <= n)
            self.assertIsNone(next(data, None))

    def test_generators_reproduce_packages_without_changing_sources(self):
        import contextlib
        for original, generate in ((self.streak_root, generate_streak), (self.tree_root, generate_tree)):
            with tempfile.TemporaryDirectory() as temp:
                copied = Path(temp) / original.name
                (copied / 'author').mkdir(parents=True)
                (copied / 'author/reference.py').write_bytes((original / 'author/reference.py').read_bytes())
                with contextlib.redirect_stdout(io.StringIO()):
                    generate(copied)
                for relative in [Path('problem.json'), Path('samples.json'), *[p.relative_to(copied) for p in (copied / 'tests').iterdir()], *[p.relative_to(copied) for p in (copied / 'starters').iterdir()]]:
                    self.assertEqual((copied / relative).read_bytes(), (original / relative).read_bytes(), str(relative))


if __name__ == '__main__':
    unittest.main()
