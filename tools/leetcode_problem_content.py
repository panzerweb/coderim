"""Reproducible authoring for three function-based, JSON-result challenges."""
import json
import random
import re
from collections import Counter
from pathlib import Path
from leetcode_references import sources, python_source, PYTHON

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    'text-justification': {
        'title':'Text Justification','number':68,'function':'fullJustify(words, maxWidth)',
        'tags':['Strings','Greedy','Formatting'],'shape':'string_array',
        'categories':{'packing-order':25,'space-distribution':30,'special-lines':25,'boundaries':20},
        'requirements':[('packing','Keep every word in order and greedily fit as many words as possible on each line.'),
            ('width','Make every output line exactly maxWidth characters long.'),
            ('spaces','Distribute spaces evenly on ordinary lines, assigning the remainder to leftmost gaps.'),
            ('special','Left-align the last line and any single-word line, preserving right padding.')],
        'description':'Arrange the words into fixed-width lines. Fill each line greedily without changing word order. On ordinary lines distribute all available spaces as evenly as possible between words; leftmost gaps receive any remainder. Use single spaces between words on the final line, then pad its right edge. A line with one word is also padded on the right.',
        'input':'Read N maxWidth, then N whitespace-separated words. There is one test case per input. Bounds: 1 <= N <= 300; 1 <= maxWidth <= 100; 1 <= word length <= 20; each word fits maxWidth. Words contain printable ASCII characters (codes 33-126), excluding whitespace.',
        'output':'Return an ordered array of strings. The supplied driver prints it as a JSON array. Every decoded string must contain exactly maxWidth characters, including trailing spaces. JSON formatting outside strings is ignored; characters inside strings, including spaces, must match exactly.',
        'variables':{'C':'Total characters in input words','S':'Total characters in rendered output lines','W':'maxWidth'},
        'time':{'Formatting':'O(C + S)'},'space':'O(W) working space, excluding input and returned output',
        'editorial':'Greedily choose the next line using word lengths plus mandatory gaps. For a non-final line with multiple words, divide spare width by the number of gaps and assign the remainder from left to right. Handle final and singleton lines separately. Returned strings occupy O(S) space.',
    },
    'valid-number': {
        'title':'Valid Number','number':65,'function':'isNumber(s)',
        'tags':['Strings','Parsing','State Machines'],'shape':'boolean',
        'categories':{'integers-signs':20,'decimals':25,'exponents':30,'invalid-syntax':25},
        'requirements':[('mantissa','Require at least one mantissa digit and permit an optional leading sign.'),
            ('decimal','Accept exactly the permitted decimal forms, with at most one decimal point.'),
            ('exponent','Allow one optional e/E exponent containing a signed or unsigned integer.'),
            ('reject','Reject all other characters, missing components, and misplaced signs or separators.')],
        'description':'Decide whether the entire string follows the number grammar. An integer has an optional + or - followed by one or more ASCII digits. A decimal has an optional sign followed by digits and a dot, digits-dot-digits, or a dot and digits. An integer or decimal may be followed by one exponent: e or E, then an optionally signed integer. Syntax determines validity, independently of the numeric magnitude.',
        'input':'Read one line s without surrounding quotes. There is one test case per input. Bounds: 1 <= s.length <= 20. Characters are English letters, ASCII digits 0-9, +, -, or a dot. Remove the line ending only; do not trim or accept extra whitespace.',
        'output':'Return a boolean. The supplied driver prints JSON true or false (lowercase). Numeric values, strings, and extra output are not accepted as booleans.',
        'variables':{'L':'Characters in s'},'time':{'Syntax scan':'O(L)'},'space':'O(1) auxiliary space',
        'editorial':'Scan an optional sign, mantissa digits, an optional decimal point and more mantissa digits. Require at least one mantissa digit. If an exponent appears, consume an optional sign and require exponent digits. Accept only if the entire string is consumed. Do not convert to a floating-point value: NaN/Infinity are invalid spellings, while a syntactically valid enormous exponent is allowed.',
    },
    'substring-concatenation-all-words': {
        'title':'Substring with Concatenation of All Words','number':30,'function':'findSubstring(s, words)',
        'url':'substring-with-concatenation-of-all-words',
        'tags':['Strings','Sliding Window','Frequency Counting'],'shape':'integer_array',
        'categories':{'basic':15,'multiplicities':25,'overlaps-offsets':25,'boundaries':15,'scale':20},
        'requirements':[('permutation','Match a concatenation of exactly all supplied words, in any permutation.'),
            ('multiplicity','Respect the required occurrence count of every word, including duplicates.'),
            ('overlaps','Find overlapping matches and starts at every word-length offset.'),
            ('complete','Return every valid zero-based index once, including exact-end matches, or an empty array.')],
        'description':'Find all positions where a consecutive substring consists of exactly the supplied words concatenated in some order. All words have the same length. Repeated words must occur with their supplied multiplicity. Matches may overlap, and positions need not align to the beginning of s.',
        'input':'Read s, then M, then M whitespace-separated words. There is one test case per input. Bounds: 1 <= s.length <= 10,000; 1 <= M <= 5,000; 1 <= word length <= 30. All words have the same length and all characters are lowercase English letters. A total word length greater than s.length is valid input and has no matches.',
        'output':'Return an array of zero-based starting indices, in any order. The supplied driver prints a JSON integer array. Return [] when there are no matches. Include every matching position exactly once; duplicate indices are incorrect.',
        'variables':{'N':'Characters in s','M':'Number of supplied words','K':'Common word length','D':'Distinct supplied words','A':'Returned indices'},
        'time':{'Build word counts':'Expected O(MK)','Scan all offsets':'Expected O(NK)','Return indices':'O(A)'},
        'space':'O(DK) working space, excluding input and O(A) returned output',
        'editorial':'Count required words, then scan K aligned windows. Reset when an unknown word occurs; shrink from the left when the new word is overrepresented. Record a start when the window contains M words, then advance one word so overlaps remain possible. Do not sort the result: output order is unrestricted. Hashing and substring creation contribute a K factor. Hash-table operation bounds are expected, not worst-case guarantees.',
    },
}


from array_function_content import SPECS as ARRAY_SPECS
SPECS.update(ARRAY_SPECS)


def text_input(words,width):return f'{len(words)} {width}\n'+' '.join(words)+'\n'
def substring_input(s,words):return s+'\n'+str(len(words))+'\n'+'\n'.join(words)+'\n'


def text_oracle(words,width):
    """Independent formatter distributing individual spaces round-robin."""
    groups=[];group=[]
    for word in words:
        if group and sum(map(len,group))+len(group)+len(word)>width:
            groups.append(group);group=[]
        group.append(word)
    groups.append(group);result=[]
    for row,group in enumerate(groups):
        if row==len(groups)-1 or len(group)==1:
            result.append(' '.join(group).ljust(width));continue
        gaps=[' ']*(len(group)-1)
        spare=width-sum(map(len,group))-len(gaps)
        i=0
        while spare:
            gaps[i%len(gaps)]+=' ';i+=1;spare-=1
        result.append(''.join(word+gap for word,gap in zip(group,gaps))+group[-1])
    return result


NUMBER_PATTERN=re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?',re.ASCII)
def number_oracle(s):return NUMBER_PATTERN.fullmatch(s) is not None


def substring_oracle(s,words):
    size=len(words[0]);total=len(words)*size;required=Counter(words)
    return [i for i in range(len(s)-total+1)
        if Counter(s[j:j+size] for j in range(i,i+total,size))==required]


def cases(slug):
    if slug in ARRAY_SPECS:
        from array_function_content import cases as array_cases
        return array_cases(slug)
    rng=random.Random(680065+list(SPECS).index(slug))
    samples=[];hidden=[];spec=SPECS[slug]
    def add(category,args,expected=None,sample=False,explanation=''):
        if slug=='text-justification':
            words,width=args;stdin=text_input(words,width)
            actual=text_oracle(words,width)
            reqs=['packing','width','special']
            if any(len(line.split())>1 for line in actual[:-1]):reqs.append('spaces')
        elif slug=='valid-number':
            stdin=args+'\n';actual=number_oracle(args);reqs=['mantissa']
            if '.' in args:reqs.append('decimal')
            if 'e' in args or 'E' in args:reqs.append('exponent')
            if not actual:reqs.append('reject')
        else:
            s,words=args;stdin=substring_input(s,words)
            actual=substring_oracle(s,words) if expected is None else expected
            reqs=['permutation','complete']
            if len(set(words))<len(words):reqs.append('multiplicity')
            ordered=sorted(actual);total=len(words)*len(words[0])
            if any(i%len(words[0]) for i in actual) or any(b-a<total for a,b in zip(ordered,ordered[1:])):reqs.append('overlaps')
        if expected is not None and actual!=expected:raise AssertionError(f'Incorrect fixed sample: {slug}/{args}')
        target=samples if sample else hidden
        key=f'sample-{len(samples)+1:02}' if sample else f'{category}-{sum(c[1]==category for c in hidden)+1:02}'
        target.append((key,category,stdin,json.dumps(actual,indent=2)+'\n',explanation,reqs))
    if slug=='text-justification':
        add('packing-order',(['This','is','an','example','of','text','justification.'],16),
            ['This    is    an','example  of text','justification.  '],True,'Greedy packing creates three lines of exactly 16 characters. The final line has two trailing spaces.')
        add('special-lines',(['What','must','be','acknowledgment','shall','be'],16),
            ['What   must   be','acknowledgment  ','shall be        '],True,'The single-word line has two trailing spaces. The final line, "shall be", has eight trailing spaces, making its width 16.')
        add('space-distribution',(['Science','is','what','we','understand','well','enough','to','explain','to','a','computer.','Art','is','everything','else','we','do'],20),
            ['Science  is  what we','understand      well','enough to explain to','a  computer.  Art is','everything  else  we','do                  '],True,'Extra spaces go to leftmost gaps. The last line has eighteen trailing spaces.')
        packing=[(['one','two','three','four'],9),(['a','b','c','d'],3),(['abc','d','ef','g'],6),(['a','bc','def','g'],6),
            (['a','b','c','d','e','f','g'],5),(['word']*11,14),(['ab','cd','ef','gh','ij'],8),(['a','longer','b','end'],8)]
        packing += [([''.join(rng.choice('abcd') for _ in range(rng.randrange(1,6))) for _ in range(25)],15) for _ in range(2)]
        for args in packing:add('packing-order',args)
        for count in range(2,6):
            for spare in range(1,4):
                words=[chr(97+i)*(1+i%3) for i in range(count)]
                width=sum(map(len,words))+count-1+spare
                add('space-distribution',(words+['Z'*min(20,width),'x'],width))
        special=[(['a'],1),(['hello'],12),(['a','b'],10),(['one','two'],7),(['abc','def','g'],5),
            (['longword','a','b'],8),(['a','b','c','last'],5),(['xx','yy','z'],5),(['x']*5,2),(['last'],100)]
        for args in special:add('special-lines',args)
        boundary=[(['a']*300,1),(['x'*20]*300,20),(['x'*20]*300,100),(['a']*300,100),
            (['say','"hello"','a\\b','[]{}','!@#$%^&*()'],20),
            ([(''.join(chr(c) for c in range(33,127)))[i:i+20] for i in range(0,94,20)],40),
            (['!','?','@','#'],2),(['a'*20],20)]
        for args in boundary:add('boundaries',args)
    elif slug=='valid-number':
        for s,expected,explanation in [('0',True,'An integer with one digit.'),('e',False,'An exponent marker alone is not a number.'),('.',False,'A decimal point needs at least one mantissa digit.')]:
            add('integers-signs' if expected else 'invalid-syntax',s,expected,True,explanation)
        groups={
            'integers-signs':['2','0089','+0','-0','000','+0089','99999999999999999999','-9999999999999999999','7','+42','-42','00000000000000000000','12345678901234567890','01','-00001','+1234567890123456789'],
            'decimals':['-0.1','+3.14','4.','-.9','.0','0.','+.8','-4.','00.00','+.000','1.2','.1234567890123456789','1234567890123456789.','-0.00000000000000001','1..0','.e1'],
            'exponents':['2e10','-90E3','3e+7','+6e-1','53.5e93','-123.456e789','0e0','1E-0','1.e2','.1E+2','1e999999999999999999','1e-99999999999999999','1e','e3','99e2.5','1e+','1ee2','1E--2','1e2e3','1e.5'],
            'invalid-syntax':['abc','1a','--6','-+3','95a54e53','+','-','NaN','Infinity','0x10','-.','++1'],
        }
        for category,strings in groups.items():
            for s in strings:add(category,s)
    else:
        add('basic',('barfoothefoobarman',['foo','bar']),[0,9],True,'The matches are barfoo at 0 and foobar at 9.')
        add('multiplicities',('wordgoodgoodgoodbestword',['word','good','best','word']),[],True,'Two occurrences of word are required within the same concatenation.')
        add('basic',('barfoofoobarthefoobarman',['bar','foo','the']),[6,9,12],True,'Three overlapping concatenations contain all three words. Their indices may be returned in any order.')
        basic=[('foobar',['foo','bar']),('barfoo',['foo','bar']),('abc',['a','b','c']),('xyzabc',['abc']),
            ('dogcatdog',['cat','dog']),('abefcd',['ab','cd','ef']),('abcdef',['ab','cd','ef']),('hello',['he','ll'])]
        for args in basic:add('basic',args)
        duplicates=[('wordgoodgoodgoodbestword',['word','good','best','good']),('aaaaaa',['aa','aa']),('abababab',['ab','ab']),
            ('catcatdogcat',['cat','cat','dog']),('foofoofoo',['foo','foo']),('goodwordgood',['good','good']),
            ('aaaaab',['a','a','b']),('abbabb',['ab','ab','bb'])]
        for args in duplicates:add('multiplicities',args)
        overlaps=[('aaaaa',['a','a']),('aaaaaa',['aa','aa']),('xfoobarfoo',['foo','bar']),('xxfoobar',['foo','bar']),
            ('abababab',['ab','ba']),('bbbbbbb',['bb','bb']),('barfoobarfoo',['bar','foo']),('aaaaaaaaa',['aaa','aaa']),
            ('cabababc',['ab','ab']),('ababa',['a','b','a'])]
        for args in overlaps:add('overlaps-offsets',args)
        boundary=[('a',['a']),('a',['b']),('a',['aa']),('abc',['abc','abc']),('xfoobar',['foo','bar']),('a'*30,['a'*30]),
            ('zzabc',['abc']),('abc',['abc'])]
        for args in boundary:add('boundaries',args)
        scales=[(('a'*10000,['a']*5000),list(range(5001))),
            (('a'*10000,['aa']*2500),list(range(5001))),
            (('abc'*3330,['abc']*1000),list(range(0,6991,3))),
            (('a'*10000,['b']*5000),[]),
            (('a'*10000,['a'*30]*5000),[]),
            ((('a'*30+'b'*30)*166,['a'*30,'b'*30]),list(range(0,9901,30)))]
        for args,expected in scales:add('scale',args,expected)
    assert len(samples)==3
    assert len(hidden)==(64 if slug=='valid-number' else 40),(slug,len(hidden))
    return samples,hidden


FAULTS={
    'text-justification':{
        'missing_padding':PYTHON['text-justification'].replace('return result','return [line.rstrip() for line in result]'),
        'right_biased':PYTHON['text-justification'].replace('(i - start < extra)','(i - start >= gaps - extra)'),
        'left_only':PYTHON['text-justification'].replace('if end == len(words) or gaps == 0:', 'if True:'),
        'one_word_per_line':"def fullJustify(words, maxWidth):\n    return [w.ljust(maxWidth) for w in words]\n",
    },
    'valid-number':{
        'float_conversion':"def isNumber(s):\n    try:\n        float(s)\n        return True\n    except ValueError:\n        return False\n",
        'prefix_only':"def isNumber(s):\n    import re\n    return re.match(r'[+-]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?',s) is not None\n",
        'finite_conversion':"def isNumber(s):\n    import math\n    try:\n        return math.isfinite(float(s))\n    except ValueError:\n        return False\n",
    },
    'substring-concatenation-all-words':{
        'offset_zero':PYTHON['substring-concatenation-all-words'].replace('for offset in range(size):','for offset in range(1):'),
        'word_set':"def findSubstring(s, words):\n    k=len(words[0]);total=k*len(words)\n    return [i for i in range(len(s)-total+1) if set(s[j:j+k] for j in range(i,i+total,k))==set(words)]\n",
        'no_overlaps':"def findSubstring(s, words):\n    from collections import Counter\n    k=len(words[0]);total=k*len(words);required=Counter(words);i=0;result=[]\n    while i+total<=len(s):\n        if Counter(s[j:j+k] for j in range(i,i+total,k))==required:\n            result.append(i);i+=total\n        else:\n            i+=1\n    return result\n",
    },
}


def generate(slug,root=None):
    if slug in ARRAY_SPECS:
        from array_function_content import generate as array_generate
        return array_generate(slug,root)
    root=Path(root or ROOT/'problems'/slug);spec=SPECS[slug]
    def write(name,text):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8',newline='\n')
    def write_json(name,value):write(name,json.dumps(value,indent=2)+'\n')
    metadata={'schema_version':1,'id':slug,'version':1,'title':spec['title'],'difficulty':'Hard','order':11+list(SPECS).index(slug),
        'tags':spec['tags'],'status':'published','suggested_duration_minutes':60,
        'limits':{'time_ms':2000,'memory_mb':256,'stdin_bytes':1048576,'stdout_bytes':1048576},
        'checker':{'type':'json','value_type':spec['shape'],'unordered':spec['shape']=='integer_array'},
        'requirements':[{'id':key,'text':text} for key,text in spec['requirements']],
        'category_weights':spec['categories'],
        'starters':{'python':'starters/main.py','javascript':'starters/main.js','cpp':'starters/main.cpp','java':'starters/Main.java'},
        'reference_complexity':{'variables':spec['variables'],'time_by_phase':spec['time'],'auxiliary_space':spec['space'],
            'notes':'Reference guidance, not an analysis of the submitted program. Include stored input, returned values, JSON serialization buffers, and recursion stacks in total space. Hash-table bounds, where stated, are expected rather than worst-case guarantees. Hard follows LeetCode; the 60-minute practice estimate is provisional.'}}
    write_json('problem.json',metadata)
    url='https://leetcode.com/problems/'+spec.get('url',slug)+'/'
    statement=f"# {spec['title']}\n\nAdapted from [LeetCode {spec['number']}: {spec['title']}]({url}) for Code Relay.\n\n{spec['description']}\n\n## Write the function\n\nImplement `{spec['function']}` in the starter. Return the result; the provided code reads input, calls your function, and prints JSON. Keep the provided input/output section intact. The entire program remains editable.\n\nPython and JavaScript use the function name above; C++ uses `vector<string>` / `vector<int>` for array results, and Java supplies static methods inside `Main` with `List<String>` / `List<Integer>` results. Boolean results use the language's boolean type.\n\n## Input specification\n\n{spec['input']}\n\n## Output specification\n\n{spec['output']}\n\n## Practice information\n\nHard (LeetCode classification). Suggested duration: 60 minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Alternative correct algorithms are allowed.\n"
    write('statement.md',statement)
    names={'reference.py':'main.py','reference.js':'main.js','reference.cpp':'main.cpp','Main.java':'Main.java'}
    for name,text in sources(slug).items():write('author/'+name,text)
    for name,text in sources(slug,stub=True).items():write('starters/'+names[name],text)
    for name,function in FAULTS[slug].items():write('author/incorrect_solutions/'+name+'.py',python_source(slug,function))
    write('author/editorial.md',f"# Private organizer reference: {spec['title']}\n\n{spec['editorial']}\n\nTime: {spec['time']}. Auxiliary space: {spec['space']}. Include input/output storage and serialization when reviewing total space. The reference is not a required implementation.\n\nGenerate with `python author/generate_tests.py`; verify with the repository's function-problem verification tool. Saved samples have explicitly checked expected results. Random small cases use independent oracles; substring scale cases use known patterns.\n")
    write('author/generate_tests.py',"from pathlib import Path\nimport sys\nROOT=Path(__file__).resolve().parents[3]\nsys.path.insert(0,str(ROOT/'tools'))\nfrom leetcode_problem_content import generate\nif __name__=='__main__':\n    generate(Path(__file__).resolve().parents[1].name)\n")
    samples,hidden=cases(slug)
    write_json('samples.json',[{'id':key,'category':category,'input':stdin,'expected_output':expected,'explanation':explanation,'requirements':reqs} for key,category,stdin,expected,explanation,reqs in samples])
    manifest=[]
    for key,category,stdin,expected,_,reqs in hidden:
        write(f'tests/{key}.in',stdin);write(f'tests/{key}.out',expected)
        manifest.append({'id':key,'category':category,'requirements':reqs,'input_file':f'tests/{key}.in','output_file':f'tests/{key}.out'})
    write_json('tests/manifest.json',{'cases':manifest})
    print(f'{slug}: {len(samples)} samples + {len(hidden)} hidden',flush=True)
    return root


if __name__=='__main__':
    for slug in SPECS:generate(slug)
