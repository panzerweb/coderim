"""Private references and complete editable drivers for four array/string tasks."""
from practice_references import JAVA_SCANNER

PYTHON={
 'plus-one':'''def plusOne(digits):
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    return [1] + digits
''',
 'remove-duplicates-from-sorted-array':'''def removeDuplicates(nums):
    k = 0
    for i in range(len(nums)):
        if k == 0 or nums[i] != nums[k - 1]:
            nums[k] = nums[i]
            k += 1
    return k
''',
 'next-permutation':'''def nextPermutation(nums):
    pivot = len(nums) - 2
    while pivot >= 0 and nums[pivot] >= nums[pivot + 1]:
        pivot -= 1
    if pivot >= 0:
        successor = len(nums) - 1
        while nums[successor] <= nums[pivot]:
            successor -= 1
        nums[pivot], nums[successor] = nums[successor], nums[pivot]
    left, right = pivot + 1, len(nums) - 1
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left += 1
        right -= 1
''',
 'longest-substring-without-repeating-characters':'''def lengthOfLongestSubstring(s):
    last = [-1] * 128
    left = best = 0
    for right, character in enumerate(s):
        code = ord(character)
        left = max(left, last[code] + 1)
        last[code] = right
        best = max(best, right - left + 1)
    return best
''',
}

JS={
 'plus-one':'''function plusOne(digits) {
  for (let i=digits.length-1;i>=0;i--) {
    if (digits[i]<9) { digits[i]++; return digits; }
    digits[i]=0;
  }
  return [1,...digits];
}''',
 'remove-duplicates-from-sorted-array':'''function removeDuplicates(nums) {
  let k=0;
  for (let i=0;i<nums.length;i++) {
    if (k===0 || nums[i]!==nums[k-1]) nums[k++]=nums[i];
  }
  return k;
}''',
 'next-permutation':'''function nextPermutation(nums) {
  let pivot=nums.length-2;
  while (pivot>=0 && nums[pivot]>=nums[pivot+1]) pivot--;
  if (pivot>=0) {
    let successor=nums.length-1;
    while (nums[successor]<=nums[pivot]) successor--;
    [nums[pivot],nums[successor]]=[nums[successor],nums[pivot]];
  }
  let left=pivot+1,right=nums.length-1;
  while (left<right) { [nums[left],nums[right]]=[nums[right],nums[left]]; left++; right--; }
}''',
 'longest-substring-without-repeating-characters':'''function lengthOfLongestSubstring(s) {
  const last=new Int32Array(128).fill(-1); let left=0,best=0;
  for (let right=0;right<s.length;right++) {
    const code=s.charCodeAt(right); left=Math.max(left,last[code]+1);
    last[code]=right; best=Math.max(best,right-left+1);
  }
  return best;
}''',
}

CPP={
 'plus-one':'''vector<int> plusOne(vector<int>& digits) {
  for (int i=(int)digits.size()-1;i>=0;i--) {
    if (digits[i]<9) { digits[i]++; return digits; }
    digits[i]=0;
  }
  vector<int> result(digits.size()+1,0); result[0]=1; return result;
}''',
 'remove-duplicates-from-sorted-array':'''int removeDuplicates(vector<int>& nums) {
  int k=0;
  for (int i=0;i<(int)nums.size();i++) if(k==0 || nums[i]!=nums[k-1]) nums[k++]=nums[i];
  return k;
}''',
 'next-permutation':'''void nextPermutation(vector<int>& nums) {
  int pivot=(int)nums.size()-2;
  while(pivot>=0 && nums[pivot]>=nums[pivot+1])pivot--;
  if(pivot>=0){int successor=nums.size()-1;while(nums[successor]<=nums[pivot])successor--;swap(nums[pivot],nums[successor]);}
  reverse(nums.begin()+pivot+1,nums.end());
}''',
 'longest-substring-without-repeating-characters':'''int lengthOfLongestSubstring(const string& s) {
  int last[128];fill(begin(last),end(last),-1);int left=0,best=0;
  for(int right=0;right<(int)s.size();right++){unsigned char c=s[right];left=max(left,last[c]+1);last[c]=right;best=max(best,right-left+1);}
  return best;
}''',
}

JAVA={
 'plus-one':'''static int[] plusOne(int[] digits) {
  for(int i=digits.length-1;i>=0;i--){if(digits[i]<9){digits[i]++;return digits;}digits[i]=0;}
  int[] result=new int[digits.length+1];result[0]=1;return result;
}''',
 'remove-duplicates-from-sorted-array':'''static int removeDuplicates(int[] nums) {
  int k=0;for(int i=0;i<nums.length;i++)if(k==0||nums[i]!=nums[k-1])nums[k++]=nums[i];return k;
}''',
 'next-permutation':'''static void nextPermutation(int[] nums) {
  int pivot=nums.length-2;while(pivot>=0&&nums[pivot]>=nums[pivot+1])pivot--;
  if(pivot>=0){int successor=nums.length-1;while(nums[successor]<=nums[pivot])successor--;
    int t=nums[pivot];nums[pivot]=nums[successor];nums[successor]=t;}
  int left=pivot+1,right=nums.length-1;while(left<right){int t=nums[left];nums[left]=nums[right];nums[right]=t;left++;right--;}
}''',
 'longest-substring-without-repeating-characters':'''static int lengthOfLongestSubstring(String s) {
  int[] last=new int[128];Arrays.fill(last,-1);int left=0,best=0;
  for(int right=0;right<s.length();right++){int c=s.charAt(right);left=Math.max(left,last[c]+1);last[c]=right;best=Math.max(best,right-left+1);}return best;
}''',
}


def python_source(slug,function):
    if slug=='longest-substring-without-repeating-characters':
        body="s=stream.readline()\n    if s.endswith('\\n'):\n        s=s[:-1]\n        if s.endswith('\\r'): s=s[:-1]\n    result=lengthOfLongestSubstring(s)"
    else:
        body="data=iter(stream.read().split())\n    n=int(next(data))\n    nums=[int(next(data)) for _ in range(n)]\n    "
        if slug=='plus-one':body+='result=plusOne(nums)'
        elif slug=='next-permutation':body+='nextPermutation(nums)\n    result=nums'
        else:body+="k=removeDuplicates(nums)\n    result={'k':k,'nums':nums[:k]} if type(k) is int and 0<=k<=n and k<=len(nums) else None"
    return ('import json\nimport sys\n\n# YOUR SOLUTION: edit this function body.\n'+function+
        '\n# PROVIDED INPUT/OUTPUT: leave this section intact.\ndef solve(stream, output):\n    '+body+
        "\n    output.write(json.dumps(result)+'\\n')\n\nif __name__ == '__main__':\n    solve(sys.stdin, sys.stdout)\n")


def sources(slug,stub=False):
    py,js,cpp,java=PYTHON[slug],JS[slug],CPP[slug],JAVA[slug]
    if stub:
        void=slug=='next-permutation';array=slug=='plus-one'
        py=py.split('\n',1)[0]+'\n    # TODO: implement the function.\n    return'+('' if void else ' []' if array else ' 0')+'\n'
        js=js.split('\n',1)[0]+'\n  // TODO: implement the function.\n  return'+('' if void else ' []' if array else ' 0')+';\n}'
        cpp=cpp.split('\n',1)[0]+'\n  // TODO: implement the function.\n  return'+('' if void else ' {}' if array else ' 0')+';\n}'
        java=java.split('\n',1)[0]+'\n  // TODO: implement the function.\n  return'+('' if void else ' new int[0]' if array else ' 0')+';\n}'
    js_io="const raw=require('fs').readFileSync(0,'utf8');\n"
    if slug=='longest-substring-without-repeating-characters':
        js_io+="const s=raw.replace(/\\r?\\n$/, '');\nconst result=lengthOfLongestSubstring(s);\n"
        cpp_io="string s;getline(cin,s);if(!s.empty()&&s.back()=='\\r')s.pop_back();cout<<lengthOfLongestSubstring(s)<<'\\n';"
        java_io="String s=new BufferedReader(new InputStreamReader(System.in)).readLine();if(s==null)s=\"\";System.out.println(lengthOfLongestSubstring(s));"
    else:
        js_io+="const tokens=raw.trim().split(/\\s+/);let position=0;const next=()=>Number(tokens[position++]);\nconst n=next(),nums=Array.from({length:n},next);\n"
        cpp_io="int n;cin>>n;vector<int> nums(n);for(int& value:nums)cin>>value;\n"
        java_io="int n=in.number();int[] nums=new int[n];for(int i=0;i<n;i++)nums[i]=in.number();\n"
        if slug=='plus-one':
            js_io+='const result=plusOne(nums);\n';cpp_io+='auto result=plusOne(nums);cout<<jsonInts(result)<<\'\\n\';';java_io+='System.out.println(jsonInts(plusOne(nums),-1));'
        elif slug=='next-permutation':
            js_io+='nextPermutation(nums);\nconst result=nums;\n';cpp_io+='nextPermutation(nums);cout<<jsonInts(nums)<<\'\\n\';';java_io+='nextPermutation(nums);System.out.println(jsonInts(nums,-1));'
        else:
            js_io+="const k=removeDuplicates(nums);\nconst result=Number.isInteger(k)&&k>=0&&k<=n&&k<=nums.length?{k,nums:nums.slice(0,k)}:null;\n"
            cpp_io+='int k=removeDuplicates(nums);if(k<0||k>n||k>(int)nums.size())cout<<"null\\n";else cout<<"{\\\"k\\\":"<<k<<",\\\"nums\\\":"<<jsonInts(nums,k)<<"}\\n";'
            java_io+='int k=removeDuplicates(nums);if(k<0||k>n||k>nums.length)System.out.println("null");else System.out.println("{\\\"k\\\":"+k+",\\\"nums\\\":"+jsonInts(nums,k)+"}");'
    js_io+="process.stdout.write(JSON.stringify(result)+'\\n');\n"
    cpp_json='string jsonInts(const vector<int>& values,int count=-1){if(count<0)count=values.size();string out="[";for(int i=0;i<count;i++){if(i)out+=\',\';out+=to_string(values[i]);}return out+\']\';}\n'
    java_json='static String jsonInts(int[] values,int count){if(count<0)count=values.length;StringJoiner out=new StringJoiner(",","[","]");for(int i=0;i<count;i++)out.add(Integer.toString(values[i]));return out.toString();}\n'
    return {
        'reference.py':python_source(slug,py),
        'reference.js':'// YOUR SOLUTION: edit this function body.\n'+js+'\n\n// PROVIDED INPUT/OUTPUT: leave this section intact.\n'+js_io,
        'reference.cpp':'#include <bits/stdc++.h>\nusing namespace std;\n\n// YOUR SOLUTION: edit this function body.\n'+cpp+'\n\n// PROVIDED INPUT/OUTPUT: leave this section intact.\n'+cpp_json+'int main(){ios::sync_with_stdio(false);cin.tie(nullptr);\n'+cpp_io+'\n}\n',
        'Main.java':'import java.io.*;\nimport java.util.*;\npublic class Main{\n// YOUR SOLUTION: edit this function body.\n'+java+'\n\n// PROVIDED INPUT/OUTPUT: leave this section intact.\n'+JAVA_SCANNER+java_json+'public static void main(String[] args)throws Exception{FastScanner in=new FastScanner();\n'+java_io+'\n}\n}\n',
    }
