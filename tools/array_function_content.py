"""Reproducible Easy/Medium packages with mutation-aware function drivers."""
import itertools
import json
import math
import random
import string
from collections import Counter
from pathlib import Path
from array_function_references import sources,python_source,PYTHON

ROOT=Path(__file__).resolve().parents[1]
SPECS={
 'plus-one':{
  'title':'Plus One','number':66,'difficulty':'Easy','minutes':20,'function':'plusOne(digits)','shape':'integer_array','tags':['Arrays','Arithmetic','Carry Propagation'],
  'requirements':[('increment','Increment the represented integer by exactly one.'),('digits','Return ordered base-ten digits without precision loss or leading zeros.'),('carry','Propagate carries through consecutive trailing nines.'),('growth','Grow the result when every input digit is nine.')],
  'description':'An integer is represented by its decimal digits, most significant first. Increment it by one and return the resulting digit array. You may update the supplied digits or return a new array. The number may be too large for a fixed-width numeric type.',
  'input':'Read N followed by N digits. Bounds: 1 <= N <= 100; digits are 0-9. There are no leading zeros, except that [0] is a valid representation of zero. There is one test case per input.',
  'output':'Return an ordered digit array. The provided driver prints a JSON integer array. For example, [9] becomes [1,0].',
  'variables':{'N':'Number of input digits'},'time':{'Worst-case carry propagation':'O(N)'},'space':'O(1) working space, excluding returned output of up to N+1 digits',
  'editorial':'Visit digits from right to left. Increment the first digit below nine and stop; replace each carried-through nine by zero. If all digits were nine, return a leading one followed by the zeros. Input mutation is allowed, not required. Never rely on fixed-width or floating-point numeric conversion.',
 },
 'remove-duplicates-from-sorted-array':{
  'title':'Remove Duplicates from Sorted Array','number':26,'difficulty':'Easy','minutes':20,'function':'removeDuplicates(nums)','shape':'deduplicated_array','tags':['Arrays','Two Pointers','In-place'],
  'requirements':[('count','Return the number k of distinct values.'),('prefix','Modify the caller-visible array so its first k entries contain the unique values.'),('order','Preserve sorted order and include each distinct value exactly once.'),('bounds','Handle signed, singleton, all-equal, and maximum-size sorted arrays.')],
  'description':'Compact the unique values of a non-decreasing array into its beginning and return their count k. The first k entries must contain those values in order; everything after them is ignored. Modify the supplied array rather than merely returning or locally rebinding a different array. Use constant auxiliary space.',
  'input':'Read N followed by N non-decreasing integers. Bounds: 1 <= N <= 30,000; -100 <= nums[i] <= 100. There is one test case per input.',
  'output':'Return only integer k. After calling your function, the driver prints {"k":k,"nums":prefix}, where prefix contains the first k entries of the caller-held array. Tail contents are ignored. Invalid k values produce null and are judged Wrong Answer. Example: [1,1,2] produces {"k":2,"nums":[1,2]}.',
  'variables':{'N':'Input array length','K':'Unique values (at most 201)'},'time':{'Compaction':'O(N)'},'space':'O(1) auxiliary space; the provided driver stores/serializes O(K) result data',
  'editorial':'Keep a write index k. Scan left to right and write a value only when it differs from the last written value, then increment k. The driver checks k and the mutated prefix, not the tail. A new local binding does not update the caller. Constant-space compliance is reviewed from source under Technical Quality; output tests do not prove allocation behavior.',
 },
 'next-permutation':{
  'title':'Next Permutation','number':31,'difficulty':'Medium','minutes':40,'function':'nextPermutation(nums)','shape':'integer_array','tags':['Arrays','Lexicographic Order','In-place'],
  'requirements':[('next','Produce the nearest lexicographically greater arrangement when it exists.'),('multiplicity','Preserve the complete multiset of values and array length.'),('wrap','Wrap a maximal arrangement to the smallest ascending arrangement.'),('mutation','Modify the caller-held array, including duplicate and singleton cases.')],
  'description':'Rearrange the array into the next lexicographically greater permutation. If it is already maximal, rearrange it into ascending order. Equal values are allowed. Modify the supplied array in place and use only constant auxiliary memory.',
  'input':'Read N followed by N integers. Bounds: 1 <= N <= 100; 0 <= nums[i] <= 100. There is one test case per input.',
  'output':'Return no value. The driver ignores return values and prints the caller-held array as an ordered JSON integer array. Returning a different array without mutating the supplied one does not solve this task.',
  'variables':{'N':'Array length'},'time':{'Find pivot, swap, and reverse':'O(N)'},'space':'O(1) auxiliary space, excluding stored input and serialized output',
  'editorial':'Find the rightmost position whose value is smaller than its successor. Swap it with the rightmost larger value, then reverse the suffix. If no pivot exists, reverse the whole array. Use explicit swaps/two pointers rather than allocating a suffix copy in references. Tests observe mutation through the supplied driver; space compliance remains a manual review dimension.',
 },
 'longest-substring-without-repeating-characters':{
  'title':'Longest Substring Without Repeating Characters','number':3,'difficulty':'Medium','minutes':40,'function':'lengthOfLongestSubstring(s)','shape':'integer','tags':['Strings','Sliding Window','ASCII'],
  'requirements':[('contiguous','Measure consecutive substrings rather than subsequences or global distinct counts.'),('unique','Exclude repeated characters while preserving case and spaces.'),('window','Move the left boundary forward and retain valid overlapping windows.'),('bounds','Handle empty strings, significant edge spaces, and maximum-length input.')],
  'description':'Find the length of the longest contiguous substring containing no repeated characters. Uppercase and lowercase letters are distinct; spaces and punctuation are ordinary characters. Do not strip spaces from the input. An empty string has answer zero.',
  'input':'Read one raw line without surrounding quotes. Bounds: 0 <= length <= 100,000. Characters are printable ASCII codes 32-126, including spaces. Remove only the physical LF/CRLF line ending; preserve leading and trailing spaces. An empty line or EOF with no characters represents the empty string. There is one test case per input.',
  'output':'Return an integer length. The provided driver prints one JSON integer. For empty input the result is 0; booleans, strings, and floating-point JSON values are not integer results.',
  'variables':{'L':'Characters in the input string'},'time':{'Sliding window':'O(L)'},'space':'O(1) auxiliary space with a fixed ASCII table; stored input takes O(L)',
  'editorial':'Keep the last position of each ASCII character. Update left=max(left,last[c]+1), record the new position, and update the best window length. Never move left backward when the previous occurrence is outside the window. A fixed 128-entry array uses constant auxiliary space; parsing and retained input still contribute to total program space.',
 },
}


def plus_oracle(values):return [int(c) for c in str(int(''.join(map(str,values)))+1)]
def dedup_oracle(values):
    unique=sorted(set(values));return {'k':len(unique),'nums':unique}


def permutation_oracle(values):
    """Independent multiset lexicographic ranking/unranking, no pivot algorithm."""
    counts=Counter(values);alphabet=sorted(counts);n=len(values)
    total=math.factorial(n)
    for count in counts.values():total//=math.factorial(count)
    full=total;rank=0
    for remaining,current in zip(range(n,0,-1),values):
        for value in alphabet:
            if value>=current:break
            rank+=total*counts[value]//remaining
        total=total*counts[current]//remaining;counts[current]-=1
    target=(rank+1)%full;counts=Counter(values);total=full;result=[]
    for remaining in range(n,0,-1):
        for value in alphabet:
            if not counts[value]:continue
            block=total*counts[value]//remaining
            if target>=block:target-=block
            else:
                result.append(value);counts[value]-=1;total=block;break
    return result


def substring_oracle(s):
    best=0
    for left in range(len(s)):
        seen=set()
        for c in s[left:]:
            if c in seen:break
            seen.add(c);best=max(best,len(seen))
    return best


def oracle(slug,value):
    return {'plus-one':plus_oracle,'remove-duplicates-from-sorted-array':dedup_oracle,
        'next-permutation':permutation_oracle,'longest-substring-without-repeating-characters':substring_oracle}[slug](value)


def cases(slug):
    samples=[];hidden=[];spec=SPECS[slug];rng=random.Random(6626313)
    def add(category,value,expected=None,sample=False,explanation='',eof=False):
        actual=oracle(slug,value) if expected is None else expected
        stdin=('' if eof else value+'\n') if isinstance(value,str) else str(len(value))+'\n'+' '.join(map(str,value))+'\n'
        ids=[r[0] for r in spec['requirements']]
        if slug=='plus-one':
            ids=ids[:2]+(['carry'] if value[-1]==9 else [])+(['growth'] if all(v==9 for v in value) else [])
        elif slug=='next-permutation' and value!=sorted(value,reverse=True):ids.remove('wrap')
        elif slug=='longest-substring-without-repeating-characters' and value and ' ' not in value and len(value)<100000:ids.remove('bounds')
        target=samples if sample else hidden
        key=f'sample-{len(samples)+1:02}' if sample else f'{category}-{sum(c[1]==category for c in hidden)+1:02}'
        target.append((key,category,stdin,json.dumps(actual,indent=2)+'\n',explanation,ids))
    if slug=='plus-one':
        for values,expected in [([1,2,3],[1,2,4]),([4,3,2,1],[4,3,2,2]),([9],[1,0])]:
            assert plus_oracle(values)==expected;add('basic',values,expected,True,'Increment the represented integer by exactly one; propagate any carry.')
        groups={'basic':[[1,2,3],[4,3,2,1],[8],[1,0],[2,4,6],[5,0,5],[7,8,1],[1,2,4]],
          'boundaries':[[0],[9],[1],[9,9],[1,0,0],[8,9],[9,0],[1,0,9]],
          'behavior':[[1,2,9],[1,9,9],[9,9,8],[5,9,9,9],[2,0,9,9],[9,9,9,9],[9,1,9,9],[9,0,0,9]],
          'scale':[[1]+[0]*99,[9]*100,[8]+[9]*99,[1,9]*50,[9]*99+[8],[1]+[9]*98+[8],list(map(int,str(2**53+11))),list(map(int,str(2**63+11)))]}
    elif slug=='remove-duplicates-from-sorted-array':
        for values in ([1,1,2],[0,0,1,1,1,2,2,3,3,4],[-1,-1,0,0,1]):
            add('basic',values,sample=True,explanation='Return k and update the first k entries. The driver shows only that prefix; the remaining entries do not matter.')
        groups={'basic':[[1,2,3],[1,1,2],[0,1,1,2],[-3,-2,-1],[0,0,1,2],[-1,0,1],[2,2,3,3],[1,2,2,3,4]],
          'boundaries':[[-100],[100],[0],[-100,-100],[100,100],[-100,100],[-100,0,0,100],[-1,-1,0,0,1]],
          'behavior':[[-100]*3+[-1]*2+[0]*4+[100]*2,[7]*17,[v for v in range(-8,9) for _ in range(3)],
            [0]*10+[1],[0]+[1]*10,[-3]*5+[-2]*5+[-1]*5,list(range(-100,101)),[-1,-1,1,1,2,2,3]],
          'scale':[[-100]*30000,[100]*30000,sorted(i%201-100 for i in range(30000)),[-1]*15000+[0]*15000,
            [0]*29999+[1],[-100]+[100]*29999,sorted(i%3-1 for i in range(30000)),[0]*30000]}
    elif slug=='next-permutation':
        for values,expected in [([1,2,3],[1,3,2]),([3,2,1],[1,2,3]),([1,1,5],[1,5,1])]:
            assert permutation_oracle(values)==expected;add('basic',values,expected,True,'Modify the supplied array to its next lexicographic arrangement, wrapping to ascending order if needed.')
        shuffled=list(range(100));rng.shuffle(shuffled)
        groups={'basic':[[1,2,3],[2,3,1],[1,3,2],[2,1,3],[3,1,2],[3,2,1],[0,1,2,3],[0,2,1,3]],
          'boundaries':[[0],[100],[1,1],[0,0,0],[1,1,5],[5,1,1],[0,100],[100,0]],
          'behavior':[[1,3,2,2],[2,2,3,1],[1,5,1],[1,2,3,6,5,4],[2,3,3,2,1],[0,1,0,0],[1,3,5,4,2],[2,4,3,3,1]],
          'scale':[list(range(100)),list(range(99,-1,-1)),[1]*100,[0]+[100]*99,[0,1]*50,
            [50]*49+[49]+[50]*50,[i for i in range(50) for _ in range(2)],shuffled]}
    else:
        for s,expected in [('abcabcbb',3),('bbbbb',1),('pwwkew',3)]:
            assert substring_oracle(s)==expected;add('basic',s,expected,True,'Count a contiguous substring with no repeated characters; a subsequence does not count.')
        groups={'basic':['abcabcbb','bbbbb','pwwkew','abc','abcdabc','abca','abac','aabbcc'],
          'boundaries':['','', ' ','a','a ',' a','  ','aA'],
          'behavior':['abba','dvdf','tmmzuxt','pwwkew','a a','aA a','"\\!?"','abcbadeaf']}
        for category,values in groups.items():
            for index,value in enumerate(values):add(category,value,eof=category=='boundaries' and index==1)
        alphabets=[''.join(map(chr,range(32,127))),'a','ab',string.ascii_lowercase,string.ascii_letters,
            ''.join(map(chr,range(33,127))),' ',''.join(map(chr,range(126,31,-1)))]
        for alphabet in alphabets:
            value=(alphabet*((100000+len(alphabet)-1)//len(alphabet)))[:100000]
            add('scale',value,len(alphabet))
        assert len(hidden)==32
        return samples,hidden
    for category,values in groups.items():
        for value in values:add(category,value)
    assert len(samples)==3 and len(hidden)==32
    return samples,hidden


FAULTS={
 'plus-one':{
  'no_carry':"def plusOne(digits):\n    digits[-1]+=1\n    return digits\n",
  'bounded_conversion':"def plusOne(digits):\n    return [int(c) for c in str(int(float(''.join(map(str,digits))))+1)]\n",
  'missing_growth':PYTHON['plus-one'].replace('return [1] + digits','return digits'),
 },
 'remove-duplicates-from-sorted-array':{
  'count_only':"def removeDuplicates(nums):\n    return len(set(nums))\n",
  'rebind_only':"def removeDuplicates(nums):\n    nums=sorted(set(nums))\n    return len(nums)\n",
  'off_by_one':PYTHON['remove-duplicates-from-sorted-array'].replace('return k','return k-1'),
 },
 'next-permutation':{
  'returns_new_array':"def nextPermutation(nums):\n    return list(reversed(nums))\n",
  'always_sort':"def nextPermutation(nums):\n    nums.sort()\n",
  'wrong_successor':PYTHON['next-permutation'].replace('successor = len(nums) - 1','successor = pivot + 1').replace('successor -= 1','successor += 1'),
 },
 'longest-substring-without-repeating-characters':{
  'global_distinct':"def lengthOfLongestSubstring(s):\n    return len(set(s))\n",
  'backward_window':PYTHON['longest-substring-without-repeating-characters'].replace('max(left, last[code] + 1)','last[code] + 1'),
  'strip_spaces':PYTHON['longest-substring-without-repeating-characters'].replace('last = [-1] * 128','s=s.strip()\n    last = [-1] * 128'),
 },
}


def generate(slug,root=None):
    root=Path(root or ROOT/'problems'/slug);spec=SPECS[slug]
    def write(name,text):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8',newline='\n')
    def write_json(name,value):write(name,json.dumps(value,indent=2)+'\n')
    metadata={'schema_version':1,'id':slug,'version':1,'title':spec['title'],'difficulty':spec['difficulty'],'order':14+list(SPECS).index(slug),
      'tags':spec['tags'],'status':'published','suggested_duration_minutes':spec['minutes'],
      'limits':{'time_ms':2000,'memory_mb':256,'stdin_bytes':1048576,'stdout_bytes':1048576},
      'checker':{'type':'json','value_type':spec['shape'],'unordered':False},
      'requirements':[{'id':key,'text':value} for key,value in spec['requirements']],
      'category_weights':{'basic':20,'boundaries':20,'behavior':40,'scale':20},
      'starters':{'python':'starters/main.py','javascript':'starters/main.js','cpp':'starters/main.cpp','java':'starters/Main.java'},
      'reference_complexity':{'variables':spec['variables'],'time_by_phase':spec['time'],'auxiliary_space':spec['space'],
        'notes':'Reference guidance, not an assessment of submitted source. Include stored input, serialized output, returned arrays, and stacks in total space. In-place/constant-space compliance is reviewed manually under Technical Quality; no automatic memory or complexity score is added. Difficulty follows LeetCode and the suggested practice duration is provisional.'}}
    write_json('problem.json',metadata)
    instruction='Return the result; the driver reads input, calls your function, and prints JSON.'
    if slug=='remove-duplicates-from-sorted-array':instruction='Return k and modify nums. The driver reads input, calls your function, and prints k with the modified prefix.'
    elif slug=='next-permutation':instruction='Modify nums and return no value. The driver ignores your return value and prints the original caller-held array after invocation.'
    statement=f"# {spec['title']}\n\nAdapted from [LeetCode {spec['number']}: {spec['title']}](https://leetcode.com/problems/{slug}/) for Code Relay.\n\n{spec['description']}\n\n## Write the function\n\nImplement `{spec['function']}` in the starter. {instruction} Keep the provided input/output section intact; the whole program remains editable.\n\nPython and JavaScript use the supplied function. C++ uses vectors by reference for array inputs. Java supplies static methods inside Main with int[] array inputs/results, integer counts, or void mutation methods.\n\n## Input specification\n\n{spec['input']}\n\n## Output specification\n\n{spec['output']} JSON formatting outside strings and object field order do not matter. Do not print debug text or prompts.\n\n## Practice information\n\n{spec['difficulty']} (LeetCode classification). Suggested duration: {spec['minutes']} minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Constant-space claims are assessed from source under Technical Quality; output tests are evidence of behavior, not proof of allocations. Correct alternative algorithms are allowed.\n"
    write('statement.md',statement)
    names={'reference.py':'main.py','reference.js':'main.js','reference.cpp':'main.cpp','Main.java':'Main.java'}
    for name,text in sources(slug).items():write('author/'+name,text)
    for name,text in sources(slug,stub=True).items():write('starters/'+names[name],text)
    for name,function in FAULTS[slug].items():write('author/incorrect_solutions/'+name+'.py',python_source(slug,function))
    write('author/editorial.md',f"# Private organizer reference: {spec['title']}\n\n{spec['editorial']}\n\nTime: {spec['time']}. Auxiliary space: {spec['space']}. Account separately for retained input and serialized results.\n\nRegenerate using author/generate_tests.py. Outputs use independent arbitrary-precision, sorted-set, multiset-ranking, or small-substring oracles. Large string patterns have independently known answers. Tests observe outputs; they do not enforce internal allocation behavior.\n")
    write('author/generate_tests.py',"from pathlib import Path\nimport sys\nROOT=Path(__file__).resolve().parents[3]\nsys.path.insert(0,str(ROOT/'tools'))\nfrom array_function_content import generate\nif __name__=='__main__':\n    generate(Path(__file__).resolve().parents[1].name)\n")
    samples,hidden=cases(slug)
    write_json('samples.json',[{'id':key,'category':category,'input':stdin,'expected_output':expected,'explanation':explanation,'requirements':ids} for key,category,stdin,expected,explanation,ids in samples])
    manifest=[]
    for key,category,stdin,expected,_,ids in hidden:
        write(f'tests/{key}.in',stdin);write(f'tests/{key}.out',expected)
        manifest.append({'id':key,'category':category,'requirements':ids,'input_file':f'tests/{key}.in','output_file':f'tests/{key}.out'})
    write_json('tests/manifest.json',{'cases':manifest})
    print(f'{slug}: {len(samples)} samples + {len(hidden)} hidden',flush=True)
    return root


if __name__=='__main__':
    for slug in SPECS:generate(slug)
