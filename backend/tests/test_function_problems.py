import contextlib
import importlib.util
import io
import itertools
import json
import random
import string
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'backend'),str(ROOT/'tools')]
from app.problems import Repository,load_problem,MAX_CASES,MAX_PACKAGE_BYTES
from app.checkers import outputs_match
from app.models import JsonChecker
from leetcode_problem_content import SPECS,generate,text_oracle,number_oracle,substring_oracle
from leetcode_references import sources,PYTHON,JS,CPP,JAVA


class FunctionProblemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules={}
        for slug in SPECS:
            spec=importlib.util.spec_from_file_location(slug.replace('-','_'),ROOT/'problems'/slug/'author/reference.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);cls.modules[slug]=module

    def test_contracts_saved_results_privacy_and_input_bounds(self):
        repo=Repository(ROOT/'problems');self.assertEqual(repo.errors,{})
        self.assertEqual([p.meta.id for p in repo.published()][10:],list(SPECS))
        for slug in list(SPECS)[:3]:
            spec=SPECS[slug]
            p=repo.get(slug)
            self.assertIsInstance(p.meta.checker,JsonChecker)
            self.assertEqual(p.meta.checker.value_type,spec['shape'])
            self.assertEqual(p.meta.version,1);self.assertEqual(p.meta.difficulty,'Hard')
            self.assertEqual(p.meta.suggested_duration_minutes,60)
            self.assertEqual(p.meta.limits.time_ms,2000)
            self.assertEqual(len(p.samples),3)
            self.assertEqual(len(p.cases),67 if slug=='valid-number' else 43)
            self.assertLessEqual(len(p.cases),MAX_CASES)
            self.assertLessEqual(sum(len(c.stdin.encode())+len(c.expected.encode()) for c in p.cases),MAX_PACKAGE_BYTES)
            self.assertEqual(len(p.meta.requirements),4)
            self.assertEqual(p.meta.rubric.weights,{'correctness':50,'requirements':20,'readability':15,'technical':15})
            for starter in p.starters.values():
                self.assertIn('TODO',starter);self.assertIn('PROVIDED INPUT/OUTPUT',starter)
            for secret in ('author/','reference.py','tests/','incorrect_solutions'):
                self.assertNotIn(secret,json.dumps(p.public()))
            for case in p.cases:
                out=io.StringIO();self.modules[slug].solve(io.StringIO(case.stdin),out)
                self.assertTrue(outputs_match(out.getvalue(),case.expected,p.meta.checker),f'{slug}/{case.id}')
                words=iter(case.stdin.split())
                if slug=='valid-number':
                    s=case.stdin.removesuffix('\n')
                    self.assertTrue(1<=len(s)<=20)
                    self.assertTrue(set(s)<=set(string.ascii_letters+string.digits+'+-.'))
                    self.assertEqual(json.loads(case.expected),number_oracle(s))
                elif slug=='text-justification':
                    n,width=int(next(words)),int(next(words));values=list(words)
                    self.assertTrue(1<=n<=300 and 1<=width<=100);self.assertEqual(len(values),n)
                    self.assertTrue(all(1<=len(w)<=min(width,20) and all(33<=ord(c)<=126 for c in w) for w in values))
                    lines=json.loads(case.expected);self.assertTrue(all(len(line)==width for line in lines))
                    self.assertEqual(' '.join(lines).split(),values)
                else:
                    s=next(words);n=int(next(words));values=list(words)
                    self.assertTrue(1<=len(s)<=10000 and 1<=n<=5000);self.assertEqual(n,len(values))
                    k=len(values[0]);self.assertTrue(1<=k<=30)
                    self.assertTrue(set(s)<=set(string.ascii_lowercase))
                    self.assertTrue(all(len(w)==k and set(w)<=set(string.ascii_lowercase) for w in values))
                    indices=json.loads(case.expected);self.assertEqual(len(set(indices)),len(indices))
                    self.assertTrue(all(0<=i<=len(s)-n*k for i in indices))
        text=repo.get('text-justification')
        self.assertEqual(json.loads(text.samples[1].expected_output)[-1],'shall be'+' '*8)

    def test_independent_randomized_and_exhaustive_oracles(self):
        rng=random.Random(686530)
        text=self.modules['text-justification'].fullJustify
        number=self.modules['valid-number'].isNumber
        substring=self.modules['substring-concatenation-all-words'].findSubstring
        for length in range(1,6):
            for chars in itertools.product('01+-.eEa',repeat=length):
                s=''.join(chars);self.assertEqual(number(s),number_oracle(s),s)
        for _ in range(500):
            width=rng.randrange(1,31)
            words=[''.join(rng.choice('ab\\"!?') for _ in range(rng.randrange(1,min(width,20)+1))) for _ in range(rng.randrange(1,35))]
            self.assertEqual(text(words,width),text_oracle(words,width))
            k=rng.randrange(1,4)
            words=[''.join(rng.choice('ab') for _ in range(k)) for _ in range(rng.randrange(1,5))]
            s=''.join(rng.choice('ab') for _ in range(rng.randrange(1,22)))
            result=substring(s,words)
            self.assertEqual(sorted(result),substring_oracle(s,words));self.assertEqual(len(result),len(set(result)))
        self.assertEqual(substring('aaaaaa',['aa','aa']),[0,2,1])

    def test_starters_only_need_function_replacement(self):
        # This is also checked by compiling/running real drivers in the author tool.
        for slug in SPECS:
            for template,filename in ((PYTHON,'reference.py'),(JS,'reference.js'),(CPP,'reference.cpp'),(JAVA,'Main.java')):
                starter=sources(slug,stub=True)[filename];reference=sources(slug)[filename]
                marker='# PROVIDED INPUT/OUTPUT' if filename.endswith('.py') else '// PROVIDED INPUT/OUTPUT'
                self.assertEqual(starter.split(marker,1)[1],reference.split(marker,1)[1])
                self.assertIn(template[slug].splitlines()[0],starter)

    def test_generators_reproduce_all_files(self):
        with tempfile.TemporaryDirectory() as temp:
            for slug in SPECS:
                with contextlib.redirect_stdout(io.StringIO()):root=generate(slug,Path(temp)/slug)
                original=ROOT/'problems'/slug
                paths={p.relative_to(root) for p in root.rglob('*') if p.is_file()}
                self.assertEqual(paths,{p.relative_to(original) for p in original.rglob('*') if p.is_file() and '__pycache__' not in p.parts})
                for path in paths:self.assertEqual((root/path).read_bytes(),(original/path).read_bytes(),f'{slug}/{path}')


if __name__=='__main__':unittest.main()
