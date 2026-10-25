import base64
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import ExitStack

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'backend'),str(ROOT/'tools')]
from app.checkers import outputs_match,validate_expected_output
from app.models import Checker,JsonChecker,ProblemMetadata
from app.problems import Case,Problem,load_problem
from app.judge import Judge,normalize
from app.languages import Registry
from app.storage import Storage
from app.remote_judge import Judge0Client,RemoteJudge
from hosted_support import FakeProvider
from scaffold_problem import scaffold


def fixture(checker,expected):
    meta=ProblemMetadata(id='json-fixture',version=1,title='JSON fixture',difficulty='Hard',tags=[],status='published',
        checker=checker,category_weights={'behavior':100},requirements=[{'id':'r','text':'Correct output'}])
    return Problem(meta,'Fixture',(),(Case('sample','sample\n',expected,'behavior',('r',),True),
        Case('hidden','private-hidden-input\n',expected,'behavior',('r',))),{})


class JsonCheckerTests(unittest.TestCase):
    def test_types_whitespace_order_multiplicity_and_escaping(self):
        boolean=JsonChecker(value_type='boolean')
        self.assertTrue(outputs_match(' \r\ntrue\t','true',boolean))
        for actual in ('1','0','"true"','True','null','[]','{}','NaN','Infinity','true false','true\nlog',''):
            self.assertFalse(outputs_match(actual,'true',boolean),actual)
        strings=JsonChecker(value_type='string_array')
        self.assertTrue(outputs_match('["a  ","b"]','[\n "a  ",\n"b"\n]',strings))
        self.assertTrue(outputs_match('["\\u0061\\\\\\\""]',json.dumps(['a\\"']),strings))
        for actual in ('["a","b"]','["b","a  "]','["a\\t ","b"]','[true]','[1]','[["a  "]]','null'):
            self.assertFalse(outputs_match(actual,'["a  ","b"]',strings),actual)
        integers=JsonChecker(value_type='integer_array',unordered=True)
        self.assertTrue(outputs_match('[9,0,6]','[0,6,9]',integers))
        self.assertTrue(outputs_match('[2,1,1]','[1,2,1]',integers))
        for actual in ('[0,6,9,9]','[0,6]','[0,6,9.0]','[false,6,9]','["0",6,9]','[0,6,9] []','[0,6,NaN]'):
            self.assertFalse(outputs_match(actual,'[0,6,9]',integers),actual)
        self.assertFalse(outputs_match('[2,1]','[1,2]',JsonChecker(value_type='integer_array')))
        self.assertTrue(outputs_match('[]','[]',integers))
        self.assertFalse(outputs_match('['*2000+']'*2000,'[]',integers))

    def test_expected_outputs_and_invalid_configuration(self):
        for shape,expected in (('boolean','1'),('boolean','NaN'),('string_array','[1]'),('integer_array','[true]'),('integer_array','[1.0]')):
            with self.assertRaises(ValueError):validate_expected_output(expected,JsonChecker(value_type=shape))
        self.assertRaises(ValueError,JsonChecker,value_type='string_array',unordered=True)
        self.assertRaises(ValueError,JsonChecker,value_type='object')
        self.assertRaises(ValueError,JsonChecker,value_type='boolean',trim_trailing_whitespace_per_line=True)
        with tempfile.TemporaryDirectory() as temp:
            root=scaffold('json-fixture',Path(temp))
            metadata=json.loads((root/'problem.json').read_text());metadata['checker']={'type':'json','value_type':'boolean'}
            (root/'problem.json').write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,'Invalid expected JSON'):load_problem(root)
            samples=json.loads((root/'samples.json').read_text());samples[0]['expected_output']='true\n'
            (root/'samples.json').write_text(json.dumps(samples));(root/'tests/spaces.out').write_text('false\n')
            self.assertIsInstance(load_problem(root).meta.checker,JsonChecker)

    def test_integer_and_deduplicated_array_shapes(self):
        integer=JsonChecker(value_type='integer')
        for value in ('0','17','-1'):
            self.assertTrue(outputs_match(value,value,integer))
        for value in ('false','true','0.0','"0"','null','[]','0 1','NaN'):
            self.assertFalse(outputs_match(value,'0',integer),value)
            self.assertRaises(ValueError,validate_expected_output,value,integer)
        checker=JsonChecker(value_type='deduplicated_array')
        expected='{"k":2,"nums":[1,2]}'
        self.assertTrue(outputs_match('{"nums":[1,2], "k":2}',expected,checker))
        self.assertTrue(outputs_match('{"k":0,"nums":[]}','{"nums":[],"k":0}',checker))
        bad=['{"k":true,"nums":[1]}','{"k":2.0,"nums":[1,2]}','{"k":-1,"nums":[]}',
             '{"k":2,"nums":[1]}','{"k":2,"nums":[1,2,999]}','{"k":2,"nums":[1,2.0]}',
             '{"k":2,"nums":[true,2]}','{"k":2,"nums":[1,2],"extra":0}',
             '{"k":1,"k":2,"nums":[1,2]}','{"k":2}','null','[2,1,2]']
        for value in bad:
            self.assertFalse(outputs_match(value,expected,checker),value)
            self.assertRaises(ValueError,validate_expected_output,value,checker)
        self.assertFalse(outputs_match('{"k":2,"nums":[2,1]}',expected,checker))
        for shape in ('integer','deduplicated_array'):
            self.assertRaises(ValueError,JsonChecker,value_type=shape,unordered=True)

    def test_existing_json_checker_serialization_is_unchanged(self):
        for kind in ('boolean','string_array','integer_array'):
            checker=JsonChecker(value_type=kind)
            self.assertEqual(checker.model_dump(),{'type':'json','value_type':kind,'unordered':False})

    def test_legacy_text_normalization_serialization_and_fingerprint(self):
        checker=Checker()
        legacy={'type':'text','normalize_line_endings':True,'trim_trailing_whitespace_per_line':True,'ignore_final_newline':True}
        self.assertEqual(checker.model_dump(),legacy)
        self.assertEqual(normalize('value \t\r\n',checker),'value')
        self.assertTrue(outputs_match('value \t\r\n','value\n',checker))
        self.assertFalse(outputs_match(' value\n','value\n',checker))
        p=load_problem(ROOT/'problems/broken-code-formatter')
        metadata=p.meta.model_dump(exclude={'statement_file','samples_file','tests_manifest','starters'})
        metadata['checker']=legacy
        digest=hashlib.sha256(json.dumps(metadata,sort_keys=True).encode())
        for c in p.cases:
            digest.update(json.dumps({'id':c.id,'category':c.category,'requirements':c.requirements,'visible':c.visible},sort_keys=True).encode())
            digest.update(c.stdin.encode());digest.update(b'\0');digest.update(c.expected.encode());digest.update(b'\0')
        self.assertEqual(Judge0Client.problem_fingerprint(p),digest.hexdigest())


class JsonExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.registry=Registry()

    def test_local_and_managed_use_the_same_typed_comparator(self):
        matrix=[('boolean','true','true',True),('boolean','true','1',False),('boolean','true','broken',False),
            ('string_array','["x "]','["x"]',False),('string_array','["x "]',' [ "x " ] ',True),
            ('integer_array','[0,2]','[2,0]',True),('integer_array','[0,2]','[0,2,2]',False),
            ('integer_array','[0,2]','[0.0,2]',False),('integer','0','0',True),('integer','0','false',False),
            ('deduplicated_array','{"k":2,"nums":[1,2]}','{"nums":[1,2],"k":2}',True),
            ('deduplicated_array','{"k":2,"nums":[1,2]}','{"k":2,"nums":[1,2,2]}',False),
            ('deduplicated_array','{"k":2,"nums":[1,2]}','{"k":1,"k":2,"nums":[1,2]}',False)]
        with tempfile.TemporaryDirectory() as temp, ExitStack() as cleanup:
            store=Storage(Path(temp)/'db');cleanup.callback(store.close)
            judge=Judge(self.registry,Path(temp)/'runs')
            for shape,expected,actual,accepted in matrix:
                with self.subTest(shape=shape,actual=actual):
                    p=fixture(JsonChecker(value_type=shape,unordered=shape=='integer_array'),expected)
                    local=judge.run(p,'python',f'import sys\nsys.stdout.write({actual!r})\n')
                    provider=FakeProvider(SimpleNamespace(published=lambda:[p]))
                    response={'status':{'id':3},'stdout':base64.b64encode(actual.encode()).decode(),'time':'0.001','exit_code':0}
                    with patch.object(provider,'result',return_value=response),patch('app.judge.execute',side_effect=AssertionError('Managed execution must stay remote')):
                        remote=RemoteJudge(provider,store).run(p,'python','RESPONSE')
                    for result in (local,remote):
                        self.assertEqual(result['verdict'],'Accepted' if accepted else 'Wrong Answer',result)
                        self.assertTrue(result['assessment']['complete'])
                        self.assertEqual(result['assessment']['correctness'],100 if accepted else 0)
                        self.assertEqual(len(result['cases']),1)
                        self.assertNotIn('private-hidden-input',json.dumps(result))
            custom=judge.run(p,'python',"print('not JSON')",mode='custom',stdin='custom')
            self.assertEqual(custom['verdict'],'Completed');self.assertIsNone(custom['assessment'])

    def test_mutation_driver_guards_with_installed_languages(self):
        from array_function_references import sources,PYTHON,JS,CPP,JAVA
        slug='remove-duplicates-from-sorted-array';p=load_problem(ROOT/'problems'/slug)
        templates={'python':(PYTHON,'reference.py'),'javascript':(JS,'reference.js'),'cpp':(CPP,'reference.cpp'),'java':(JAVA,'Main.java')}
        with tempfile.TemporaryDirectory() as temp:
            judge=Judge(self.registry,Path(temp)/'runs')
            for language,(templates_for_language,filename) in templates.items():
                if not self.registry.status[language]['available']:continue
                original=templates_for_language[slug]
                for body,expected in [('return -1',None),('return 4',None),('nums[0]=1; nums[1]=2; nums[2]=999; return 2',{'k':2,'nums':[1,2]})]:
                    function=original.splitlines()[0]+'\n    '+body+('' if language=='python' else ';\n}')+'\n'
                    code=sources(slug)[filename].replace(original,function,1)
                    with self.subTest(language=language,body=body):
                        result=judge.run(p,language,code,mode='custom',stdin='3\n1 1 2\n')
                        self.assertEqual(result['verdict'],'Completed',result)
                        self.assertEqual(json.loads(result['cases'][0]['stdout']),expected)


if __name__=='__main__':unittest.main()
