import io
import itertools
import json
import random
import string
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'backend'),str(ROOT/'tools')]
from app.checkers import outputs_match
from app.problems import Repository,load_problem,MAX_CASES,MAX_PACKAGE_BYTES
from array_function_content import SPECS,oracle,permutation_oracle
from array_function_references import sources,python_source,PYTHON


class ArrayFunctionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules={}
        for slug in SPECS:
            namespace={'__name__':'private_reference'}
            exec(compile(sources(slug)['reference.py'],slug,'exec'),namespace)
            cls.modules[slug]=namespace

    def test_catalog_contracts_bounds_and_saved_outputs(self):
        repo=Repository(ROOT/'problems');self.assertEqual(repo.errors,{})
        self.assertEqual(len(repo.published()),17)
        self.assertEqual([p.meta.id for p in repo.published()][13:],list(SPECS))
        for slug,spec in SPECS.items():
            p=repo.get(slug)
            self.assertEqual(p.meta.version,1);self.assertEqual(p.meta.difficulty,spec['difficulty'])
            self.assertEqual(p.meta.suggested_duration_minutes,spec['minutes'])
            self.assertEqual(p.meta.checker.value_type,spec['shape']);self.assertFalse(p.meta.checker.unordered)
            self.assertEqual(p.meta.limits.time_ms,2000);self.assertEqual(p.meta.limits.stdin_bytes,1048576)
            self.assertEqual(len(p.cases),35);self.assertEqual(len(p.samples),3);self.assertEqual(len(p.meta.requirements),4)
            self.assertLessEqual(len(p.cases),MAX_CASES)
            self.assertLessEqual(sum(len(c.stdin.encode())+len(c.expected.encode()) for c in p.cases),MAX_PACKAGE_BYTES)
            self.assertEqual(p.meta.category_weights,{'basic':20,'boundaries':20,'behavior':40,'scale':20})
            self.assertEqual(p.meta.rubric.weights,{'correctness':50,'requirements':20,'readability':15,'technical':15})
            for starter in p.starters.values():self.assertIn('TODO',starter);self.assertIn('PROVIDED INPUT/OUTPUT',starter)
            for secret in ('author/','reference.py','tests/','scale-01'):self.assertNotIn(secret,json.dumps(p.public()))
            for c in p.cases:
                out=io.StringIO();self.modules[slug]['solve'](io.StringIO(c.stdin),out)
                self.assertTrue(outputs_match(out.getvalue(),c.expected,p.meta.checker),f'{slug}/{c.id}')
                if isinstance(c.stdin,str) and slug=='longest-substring-without-repeating-characters':
                    s=c.stdin.removesuffix('\n')
                    self.assertTrue(len(s)<=100000 and all(32<=ord(ch)<=126 for ch in s))
                else:
                    data=list(map(int,c.stdin.split()));n=data[0];values=data[1:]
                    self.assertEqual(n,len(values))
                    if slug=='plus-one':
                        self.assertTrue(1<=n<=100 and all(0<=v<=9 for v in values))
                        self.assertTrue(n==1 or values[0]!=0)
                    elif slug=='next-permutation':self.assertTrue(1<=n<=100 and all(0<=v<=100 for v in values))
                    else:self.assertTrue(1<=n<=30000 and all(-100<=v<=100 for v in values));self.assertEqual(values,sorted(values))
                    self.assertEqual(json.loads(c.expected),oracle(slug,values))

    def test_independent_randomized_oracles_and_mutation(self):
        rng=random.Random(6626313)
        plus=self.modules['plus-one']['plusOne'];dedup=self.modules['remove-duplicates-from-sorted-array']['removeDuplicates']
        permute=self.modules['next-permutation']['nextPermutation'];longest=self.modules['longest-substring-without-repeating-characters']['lengthOfLongestSubstring']
        for _ in range(250):
            n=rng.randrange(1,101);digits=[rng.randrange(1,10)]+[rng.randrange(10) for _ in range(n-1)]
            self.assertEqual(plus(digits.copy()),oracle('plus-one',digits))
            values=sorted(rng.randrange(-100,101) for _ in range(rng.randrange(1,100)))
            caller=values.copy();k=dedup(caller);self.assertEqual({'k':k,'nums':caller[:k]},oracle('remove-duplicates-from-sorted-array',values))
            values=[rng.randrange(4) for _ in range(rng.randrange(1,8))]
            arrangements=sorted(set(itertools.permutations(values)));index=arrangements.index(tuple(values))
            expected=list(arrangements[(index+1)%len(arrangements)])
            self.assertEqual(permutation_oracle(values),expected)
            caller=values.copy();self.assertIsNone(permute(caller));self.assertEqual(caller,expected)
            s=''.join(rng.choice('aA09 !?\\"') for _ in range(rng.randrange(50)))
            self.assertEqual(longest(s),oracle('longest-substring-without-repeating-characters',s))
        for s,expected in [('',0),(' ',1),('a ',2),(' a',2),('aA',2),('abba',2),('pwwkew',3)]:self.assertEqual(longest(s),expected)

    def test_mutation_drivers_guard_k_and_ignore_unused_tail_and_return_values(self):
        slug='remove-duplicates-from-sorted-array'
        bodies=['return -1','return 4','return True','return 2.0','return None','nums.clear(); return 1']
        for body in bodies:
            ns={'__name__':'test_driver'};exec(python_source(slug,'def removeDuplicates(nums):\n    '+body+'\n'),ns)
            out=io.StringIO();ns['solve'](io.StringIO('3\n1 1 2\n'),out);self.assertIsNone(json.loads(out.getvalue()),body)
        ns={'__name__':'test_driver'}
        exec(python_source(slug,'def removeDuplicates(nums):\n    nums[0]=1; nums[1]=2; nums[2]=999\n    return 2\n'),ns)
        out=io.StringIO();ns['solve'](io.StringIO('3\n1 1 2\n'),out)
        self.assertEqual(json.loads(out.getvalue()),{'k':2,'nums':[1,2]})
        ns={'__name__':'test_driver'}
        exec(python_source('next-permutation','def nextPermutation(nums):\n    return [1,3,2]\n'),ns)
        out=io.StringIO();ns['solve'](io.StringIO('3\n1 2 3\n'),out);self.assertEqual(json.loads(out.getvalue()),[1,2,3])
        for stdin in ('','\n',' \n',' a \r\n'):
            out=io.StringIO();self.modules['longest-substring-without-repeating-characters']['solve'](io.StringIO(stdin),out)
            s=stdin.removesuffix('\n').removesuffix('\r');self.assertEqual(json.loads(out.getvalue()),oracle('longest-substring-without-repeating-characters',s))


if __name__=='__main__':unittest.main()
