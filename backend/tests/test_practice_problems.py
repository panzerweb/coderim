"""Content regressions for the seven Easy/Medium packages."""
import contextlib
import importlib.util
import io
import json
import random
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'backend'), str(ROOT/'tools')]
from app.problems import Repository, load_problem, MAX_CASES, MAX_PACKAGE_BYTES
from practice_problem_content import SPECS, generate, oracle, array_input, streak_input, tree_input, grid_input


def reference(slug):
    spec=importlib.util.spec_from_file_location(slug.replace('-','_'),ROOT/'problems'/slug/'author/reference.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class PracticeProblemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.references={slug:reference(slug) for slug in SPECS}

    def result(self,slug,stdin):
        out=io.StringIO();self.references[slug].solve(io.StringIO(stdin),out);return out.getvalue()

    def test_discovery_metadata_and_private_content(self):
        repository=Repository(ROOT/'problems')
        self.assertEqual(repository.errors,{})
        published=repository.published()
        self.assertEqual(len(published),17)
        self.assertEqual(Counter(p.meta.difficulty for p in published),{'Easy':6,'Medium':5,'Hard':6})
        self.assertEqual([p.meta.id for p in published][:3],['broken-code-formatter','longest-rising-streak-updates','g-tree-changing-root'])
        self.assertEqual([p.meta.id for p in published][3:10],list(SPECS))
        for slug,spec in SPECS.items():
            p=repository.get(slug)
            self.assertEqual(p.meta.version,1)
            self.assertEqual(p.meta.suggested_duration_minutes,spec['minutes'])
            self.assertEqual(p.meta.limits.time_ms,2000)
            self.assertEqual(len(p.samples),3)
            self.assertGreaterEqual(len(p.cases)-len(p.samples),16)
            self.assertLessEqual(len(p.cases),MAX_CASES)
            self.assertLessEqual(sum(len(c.stdin.encode())+len(c.expected.encode()) for c in p.cases),MAX_PACKAGE_BYTES)
            self.assertEqual(p.meta.category_weights,{'basic':20,'boundaries':20,'behavior':40,'scale':20})
            self.assertEqual(len(p.meta.requirements),4)
            self.assertEqual(p.meta.rubric.weights,{'correctness':50,'requirements':20,'readability':15,'technical':15})
            public=json.dumps(p.public())
            for secret in ('author/','reference.py','incorrect_solutions','scale-01','tests/'):
                self.assertNotIn(secret,public)
            self.assertFalse(p.public()['limits']['memory_enforced'])
            for starter in p.starters.values():self.assertIn('TODO',starter)

    def test_every_saved_output_matches_reference_and_all_inputs_obey_contract(self):
        for slug in SPECS:
            p=load_problem(ROOT/'problems'/slug)
            for case in p.cases:
                with self.subTest(problem=slug,case=case.id):
                    self.assertEqual(self.result(slug,case.stdin),case.expected)
                    self.validate_input(slug,case.stdin)
        tree=load_problem(ROOT/'problems/g-tree-ancestor-query')
        self.assertIn('2 5\n',tree.samples[0].input)
        self.assertEqual(tree.meta.limits.stdin_bytes,4*1024*1024)
        labels=iter(map(int,next(c.stdin for c in tree.cases if c.id=='scale-04').split()))
        n=next(labels)
        self.assertTrue(any(next(labels)>next(labels) for _ in range(n-1)))

    def validate_input(self,slug,stdin):
        if slug=='palindrome-check':
            text=stdin.removesuffix('\n')
            self.assertTrue(1<=len(text)<=100000)
            self.assertTrue(all(32<=ord(c)<=126 for c in text));return
        data=iter(map(int,stdin.split())) if slug!='shortest-grid-route' else iter(stdin.split())
        if slug=='add-two-numbers':
            self.assertTrue(all(-10**9<=next(data)<=10**9 for _ in range(2)))
        elif slug=='longest-rising-streak':
            t=next(data);self.assertTrue(1<=t<=10);total=0
            for _ in range(t):
                n=next(data);total+=n;self.assertTrue(1<=n<=100000)
                self.assertTrue(all(-1000000<=next(data)<=1000000 for _ in range(n)))
            self.assertLessEqual(total,100000)
        elif slug in ('most-frequent-reading','longest-unique-segment'):
            n=next(data);self.assertTrue(1<=n<=100000)
            self.assertTrue(all(-1000000<=next(data)<=1000000 for _ in range(n)))
        elif slug=='g-tree-ancestor-query':
            n=next(data);self.assertTrue(1<=n<=100000);children=[[] for _ in range(n+1)];parents=set()
            for _ in range(n-1):
                parent,child=next(data),next(data)
                self.assertTrue(1<=parent<=n and 2<=child<=n)
                self.assertNotIn(child,parents);parents.add(child);children[parent].append(child)
            visited=set();stack=[1]
            while stack:
                node=stack.pop();self.assertNotIn(node,visited);visited.add(node);stack.extend(children[node])
            self.assertEqual(len(visited),n)
            q=next(data);self.assertTrue(1<=q<=100000)
            self.assertTrue(all(1<=next(data)<=n for _ in range(q*2)))
        else:
            rows,cols=int(next(data)),int(next(data));self.assertTrue(1<=rows<=500 and 1<=cols<=500 and rows*cols>=2)
            grid=[next(data) for _ in range(rows)];self.assertTrue(all(len(row)==cols and set(row)<=set('.#SE') for row in grid))
            self.assertEqual(''.join(grid).count('S'),1);self.assertEqual(''.join(grid).count('E'),1)
        self.assertIsNone(next(data,None))

    def test_randomized_references_against_independent_oracles(self):
        rng=random.Random(7098)
        for _ in range(120):
            values=[rng.randrange(-6,7) for _ in range(rng.randrange(1,30))]
            inputs={
                'add-two-numbers':f'{rng.randrange(-10**9,10**9+1)} {rng.randrange(-10**9,10**9+1)}\n',
                'longest-rising-streak':streak_input([values,[0],list(reversed(values))]),
                'most-frequent-reading':array_input(values),
                'longest-unique-segment':array_input(values),
                'palindrome-check':''.join(rng.choice('aAzZ09 !?') for _ in range(50))+'\n',
            }
            n=rng.randrange(1,25);labels=list(range(2,n+1));rng.shuffle(labels);labels=[0,1]+labels
            edges=[(labels[rng.randrange(1,v)],labels[v]) for v in range(2,n+1)];rng.shuffle(edges)
            inputs['g-tree-ancestor-query']=tree_input(n,edges,[(u,v) for u in range(1,n+1) for v in range(1,n+1)])
            rows=[''.join(rng.choice('...#') for _ in range(6)) for _ in range(5)]
            rows[0]='S'+rows[0][1:];rows[-1]=rows[-1][:-1]+'E'
            inputs['shortest-grid-route']=grid_input(rows)
            for slug,stdin in inputs.items():
                with self.subTest(problem=slug):self.assertEqual(self.result(slug,stdin),oracle(slug,stdin))

    def test_generators_reproduce_all_package_files(self):
        with tempfile.TemporaryDirectory() as temp:
            for slug in SPECS:
                with contextlib.redirect_stdout(io.StringIO()):generated=generate(slug,Path(temp)/slug)
                original=ROOT/'problems'/slug
                paths={p.relative_to(generated) for p in generated.rglob('*') if p.is_file()}
                originals={p.relative_to(original) for p in original.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
                self.assertEqual(paths,originals)
                for relative in paths:self.assertEqual((generated/relative).read_bytes(),(original/relative).read_bytes(),f'{slug}/{relative}')


if __name__=='__main__':unittest.main()
