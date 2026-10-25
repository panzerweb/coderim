"""Trusted private references and editable function starters for three challenges."""
from practice_references import JAVA_SCANNER

PYTHON = {
    'text-justification': '''def fullJustify(words, maxWidth):
    result = []
    start = 0
    while start < len(words):
        end = start + 1
        letters = len(words[start])
        while end < len(words) and letters + len(words[end]) + end - start <= maxWidth:
            letters += len(words[end])
            end += 1
        gaps = end - start - 1
        if end == len(words) or gaps == 0:
            line = ' '.join(words[start:end])
            line += ' ' * (maxWidth - len(line))
        else:
            each, extra = divmod(maxWidth - letters, gaps)
            parts = []
            for i in range(start, end - 1):
                parts.append(words[i])
                parts.append(' ' * (each + (i - start < extra)))
            parts.append(words[end - 1])
            line = ''.join(parts)
        result.append(line)
        start = end
    return result
''',
    'valid-number': '''def isNumber(s):
    i, n = 0, len(s)
    if i < n and s[i] in '+-':
        i += 1
    digits = 0
    while i < n and '0' <= s[i] <= '9':
        digits += 1
        i += 1
    if i < n and s[i] == '.':
        i += 1
        while i < n and '0' <= s[i] <= '9':
            digits += 1
            i += 1
    if not digits:
        return False
    if i < n and s[i] in 'eE':
        i += 1
        if i < n and s[i] in '+-':
            i += 1
        exponent_start = i
        while i < n and '0' <= s[i] <= '9':
            i += 1
        if i == exponent_start:
            return False
    return i == n
''',
    'substring-concatenation-all-words': '''def findSubstring(s, words):
    from collections import Counter
    size, count = len(words[0]), len(words)
    if size * count > len(s):
        return []
    required = Counter(words)
    result = []
    for offset in range(size):
        left = offset
        seen = {}
        used = 0
        for right in range(offset, len(s) - size + 1, size):
            word = s[right:right + size]
            if word not in required:
                seen.clear()
                used = 0
                left = right + size
                continue
            seen[word] = seen.get(word, 0) + 1
            used += 1
            while seen[word] > required[word]:
                removed = s[left:left + size]
                seen[removed] -= 1
                used -= 1
                left += size
            if used == count:
                result.append(left)
                removed = s[left:left + size]
                seen[removed] -= 1
                used -= 1
                left += size
    return result
''',
}

JS = {
    'text-justification': '''function fullJustify(words, maxWidth) {
  const result = [];
  for (let start = 0; start < words.length;) {
    let end = start + 1, letters = words[start].length;
    while (end < words.length && letters + words[end].length + end - start <= maxWidth) letters += words[end++].length;
    const gaps = end - start - 1;
    let line;
    if (end === words.length || gaps === 0) line = words.slice(start, end).join(' ').padEnd(maxWidth, ' ');
    else {
      const each = Math.floor((maxWidth - letters) / gaps), extra = (maxWidth - letters) % gaps;
      line = '';
      for (let i = start; i < end; i++) {
        line += words[i];
        if (i < end - 1) line += ' '.repeat(each + (i - start < extra ? 1 : 0));
      }
    }
    result.push(line); start = end;
  }
  return result;
}''',
    'valid-number': '''function isNumber(s) {
  let i = 0, digits = 0;
  const digit = c => c !== undefined && c >= '0' && c <= '9';
  if (s[i] === '+' || s[i] === '-') i++;
  while (digit(s[i])) { digits++; i++; }
  if (s[i] === '.') { i++; while (digit(s[i])) { digits++; i++; } }
  if (!digits) return false;
  if (s[i] === 'e' || s[i] === 'E') {
    i++; if (s[i] === '+' || s[i] === '-') i++;
    const start = i; while (digit(s[i])) i++;
    if (i === start) return false;
  }
  return i === s.length;
}''',
    'substring-concatenation-all-words': '''function findSubstring(s, words) {
  const size = words[0].length, count = words.length, result = [];
  if (size * count > s.length) return result;
  const required = new Map(); for (const w of words) required.set(w, (required.get(w) || 0) + 1);
  for (let offset = 0; offset < size; offset++) {
    let left = offset, used = 0; const seen = new Map();
    for (let right = offset; right + size <= s.length; right += size) {
      const word = s.slice(right, right + size);
      if (!required.has(word)) { seen.clear(); used = 0; left = right + size; continue; }
      seen.set(word, (seen.get(word) || 0) + 1); used++;
      while (seen.get(word) > required.get(word)) {
        const removed = s.slice(left, left + size); seen.set(removed, seen.get(removed) - 1); used--; left += size;
      }
      if (used === count) {
        result.push(left); const removed = s.slice(left, left + size);
        seen.set(removed, seen.get(removed) - 1); used--; left += size;
      }
    }
  }
  return result;
}''',
}

CPP = {
    'text-justification': '''vector<string> fullJustify(const vector<string>& words, int maxWidth) {
  vector<string> result;
  for (int start=0; start<(int)words.size();) {
    int end=start+1, letters=words[start].size();
    while(end<(int)words.size() && letters+(int)words[end].size()+end-start<=maxWidth) letters+=words[end++].size();
    int gaps=end-start-1; string line;
    if(end==(int)words.size() || gaps==0) {
      for(int i=start;i<end;i++){if(i>start)line+=' ';line+=words[i];}
      line+=string(maxWidth-line.size(),' ');
    } else {
      int each=(maxWidth-letters)/gaps, extra=(maxWidth-letters)%gaps;
      for(int i=start;i<end;i++){line+=words[i];if(i<end-1)line+=string(each+(i-start<extra),' ');}
    }
    result.push_back(line);start=end;
  }
  return result;
}''',
    'valid-number': '''bool isNumber(const string& s) {
  int i=0,n=s.size(),digits=0;auto digit=[](char c){return c>='0'&&c<='9';};
  if(i<n&&(s[i]=='+'||s[i]=='-'))i++;
  while(i<n&&digit(s[i])){digits++;i++;}
  if(i<n&&s[i]=='.'){i++;while(i<n&&digit(s[i])){digits++;i++;}}
  if(!digits)return false;
  if(i<n&&(s[i]=='e'||s[i]=='E')){i++;if(i<n&&(s[i]=='+'||s[i]=='-'))i++;int start=i;while(i<n&&digit(s[i]))i++;if(i==start)return false;}
  return i==n;
}''',
    'substring-concatenation-all-words': '''vector<int> findSubstring(const string& s, const vector<string>& words) {
  int size=words[0].size(),count=words.size();vector<int> result;
  if(size*count>(int)s.size())return result;
  unordered_map<string,int> required;for(const auto& w:words)required[w]++;
  for(int offset=0;offset<size;offset++){
    int left=offset,used=0;unordered_map<string,int> seen;
    for(int right=offset;right+size<=(int)s.size();right+=size){
      string word=s.substr(right,size);
      if(!required.count(word)){seen.clear();used=0;left=right+size;continue;}
      seen[word]++;used++;
      while(seen[word]>required[word]){seen[s.substr(left,size)]--;used--;left+=size;}
      if(used==count){result.push_back(left);seen[s.substr(left,size)]--;used--;left+=size;}
    }
  }
  return result;
}''',
}

JAVA = {
    'text-justification': '''static List<String> fullJustify(String[] words, int maxWidth) {
  List<String> result=new ArrayList<>();
  for(int start=0;start<words.length;){
    int end=start+1,letters=words[start].length();
    while(end<words.length&&letters+words[end].length()+end-start<=maxWidth)letters+=words[end++].length();
    int gaps=end-start-1;StringBuilder line=new StringBuilder();
    if(end==words.length||gaps==0){
      for(int i=start;i<end;i++){if(i>start)line.append(' ');line.append(words[i]);}
      while(line.length()<maxWidth)line.append(' ');
    }else{
      int each=(maxWidth-letters)/gaps,extra=(maxWidth-letters)%gaps;
      for(int i=start;i<end;i++){line.append(words[i]);if(i<end-1)line.append(" ".repeat(each+(i-start<extra?1:0)));}
    }
    result.add(line.toString());start=end;
  }
  return result;
}''',
    'valid-number': '''static boolean isNumber(String s) {
  int i=0,n=s.length(),digits=0;
  if(i<n&&(s.charAt(i)=='+'||s.charAt(i)=='-'))i++;
  while(i<n&&s.charAt(i)>='0'&&s.charAt(i)<='9'){digits++;i++;}
  if(i<n&&s.charAt(i)=='.'){i++;while(i<n&&s.charAt(i)>='0'&&s.charAt(i)<='9'){digits++;i++;}}
  if(digits==0)return false;
  if(i<n&&(s.charAt(i)=='e'||s.charAt(i)=='E')){
    i++;if(i<n&&(s.charAt(i)=='+'||s.charAt(i)=='-'))i++;int start=i;
    while(i<n&&s.charAt(i)>='0'&&s.charAt(i)<='9')i++;
    if(i==start)return false;
  }
  return i==n;
}''',
    'substring-concatenation-all-words': '''static List<Integer> findSubstring(String s, String[] words) {
  int size=words[0].length(),count=words.length;List<Integer> result=new ArrayList<>();
  if(size*count>s.length())return result;
  Map<String,Integer> required=new HashMap<>();for(String w:words)required.put(w,required.getOrDefault(w,0)+1);
  for(int offset=0;offset<size;offset++){
    int left=offset,used=0;Map<String,Integer> seen=new HashMap<>();
    for(int right=offset;right+size<=s.length();right+=size){
      String word=s.substring(right,right+size);
      if(!required.containsKey(word)){seen.clear();used=0;left=right+size;continue;}
      seen.put(word,seen.getOrDefault(word,0)+1);used++;
      while(seen.get(word)>required.get(word)){String removed=s.substring(left,left+size);seen.put(removed,seen.get(removed)-1);used--;left+=size;}
      if(used==count){result.add(left);String removed=s.substring(left,left+size);seen.put(removed,seen.get(removed)-1);used--;left+=size;}
    }
  }
  return result;
}''',
}

CPP_JSON = r'''// Provided JSON string escaping; spaces inside strings are preserved.
string quoteJSON(const string& value) {
  string out="\"";const char* hex="0123456789abcdef";
  for(unsigned char c:value){
    if(c=='"'||c=='\\'){out+='\\';out+=(char)c;}
    else if(c<32){out+="\\u00";out+=hex[c>>4];out+=hex[c&15];}
    else out+=(char)c;
  }
  return out+'"';
}
'''

JAVA_JSON = r'''// Provided JSON string escaping; spaces inside strings are preserved.
static String quoteJSON(String value){
  StringBuilder out=new StringBuilder("\"");String hex="0123456789abcdef";
  for(int i=0;i<value.length();i++){char c=value.charAt(i);
    if(c=='"'||c=='\\'){out.append('\\').append(c);}
    else if(c<32){out.append("\\u00").append(hex.charAt(c>>4)).append(hex.charAt(c&15));}
    else out.append(c);
  }
  return out.append('"').toString();
}
'''


from array_function_references import PYTHON as ARRAY_PYTHON, JS as ARRAY_JS, CPP as ARRAY_CPP, JAVA as ARRAY_JAVA
PYTHON.update(ARRAY_PYTHON)
JS.update(ARRAY_JS)
CPP.update(ARRAY_CPP)
JAVA.update(ARRAY_JAVA)


def python_source(slug, function):
    if slug in ARRAY_PYTHON:
        from array_function_references import python_source as array_source
        return array_source(slug, function)
    if slug == 'text-justification':
        parse = "data=iter(stream.read().split())\n    n,maxWidth=int(next(data)),int(next(data))\n    words=[next(data) for _ in range(n)]\n    result=fullJustify(words,maxWidth)"
    elif slug == 'valid-number':
        parse = "s=stream.readline().rstrip('\\r\\n')\n    result=isNumber(s)"
    else:
        parse = "data=iter(stream.read().split())\n    s=next(data)\n    words=[next(data) for _ in range(int(next(data)))]\n    result=findSubstring(s,words)"
    return ('import json\nimport sys\n\n# YOUR SOLUTION: edit this function body.\n'+function+
        '\n# PROVIDED INPUT/OUTPUT: leave this section intact.\ndef solve(stream, output):\n    '+parse+
        "\n    output.write(json.dumps(result) + '\\n')\n\nif __name__ == '__main__':\n    solve(sys.stdin, sys.stdout)\n")


def sources(slug, stub=False):
    if slug in ARRAY_PYTHON:
        from array_function_references import sources as array_sources
        return array_sources(slug, stub)
    py,js,cpp,java=PYTHON[slug],JS[slug],CPP[slug],JAVA[slug]
    if stub:
        boolean=slug=='valid-number'
        py=py.split('\n',1)[0]+('\n    # TODO: return whether s is a valid number.\n    return False\n' if boolean else '\n    # TODO: return the result array.\n    return []\n')
        js=js.split('\n',1)[0]+'\n  // TODO: implement the function.\n  return '+('false' if boolean else '[]')+';\n}'
        cpp=cpp.split('\n',1)[0]+'\n  // TODO: implement the function.\n  return '+('false' if boolean else '{}')+';\n}'
        java=java.split('\n',1)[0]+'\n  // TODO: implement the function.\n  return '+('false' if boolean else 'new ArrayList<>()')+';\n}'
    js_io="const raw=require('fs').readFileSync(0,'utf8');\n"
    if slug=='valid-number':
        js_io+="const s=raw.replace(/\\r?\\n$/, '');\nconst result=isNumber(s);\n"
        cpp_io="string s;getline(cin,s);if(!s.empty()&&s.back()=='\\r')s.pop_back();cout<<(isNumber(s)?\"true\":\"false\")<<'\\n';"
        java_io="String s=new BufferedReader(new InputStreamReader(System.in)).readLine();System.out.println(isNumber(s)?\"true\":\"false\");"
    else:
        js_io+="const tokens=raw.trim().split(/\\s+/);let position=0;const next=()=>tokens[position++];\n"
        if slug=='text-justification':
            js_io+="const n=Number(next()),maxWidth=Number(next()),words=Array.from({length:n},next);\nconst result=fullJustify(words,maxWidth);\n"
            cpp_io="int n,maxWidth;cin>>n>>maxWidth;vector<string> words(n);for(auto& w:words)cin>>w;auto result=fullJustify(words,maxWidth);\ncout<<'[';for(int i=0;i<(int)result.size();i++){if(i)cout<<',';cout<<quoteJSON(result[i]);}cout<<\"]\\n\";"
            java_io="int n=in.number(),maxWidth=in.number();String[] words=new String[n];for(int i=0;i<n;i++)words[i]=in.token();List<String> result=fullJustify(words,maxWidth);\nStringJoiner out=new StringJoiner(\",\",\"[\",\"]\");for(String line:result)out.add(quoteJSON(line));System.out.println(out);"
        else:
            js_io+="const s=next(),n=Number(next()),words=Array.from({length:n},next);\nconst result=findSubstring(s,words);\n"
            cpp_io="string s;int n;cin>>s>>n;vector<string> words(n);for(auto& w:words)cin>>w;auto result=findSubstring(s,words);\ncout<<'[';for(int i=0;i<(int)result.size();i++){if(i)cout<<',';cout<<result[i];}cout<<\"]\\n\";"
            java_io="String s=in.token();int n=in.number();String[] words=new String[n];for(int i=0;i<n;i++)words[i]=in.token();List<Integer> result=findSubstring(s,words);\nStringJoiner out=new StringJoiner(\",\",\"[\",\"]\");for(int index:result)out.add(Integer.toString(index));System.out.println(out);"
    js_io+="process.stdout.write(JSON.stringify(result)+'\\n');\n"
    return {
        'reference.py':python_source(slug,py),
        'reference.js':'// YOUR SOLUTION: edit this function body.\n'+js+'\n\n// PROVIDED INPUT/OUTPUT: leave this section intact.\n'+js_io,
        'reference.cpp':'#include <bits/stdc++.h>\nusing namespace std;\n\n// YOUR SOLUTION: edit this function body.\n'+cpp+'\n\n// PROVIDED INPUT/OUTPUT: leave this section intact.\n'+CPP_JSON+'int main(){ios::sync_with_stdio(false);cin.tie(nullptr);\n'+cpp_io+'\n}\n',
        'Main.java':'import java.io.*;\nimport java.util.*;\npublic class Main{\n// YOUR SOLUTION: edit this function body.\n'+java+'\n\n// PROVIDED INPUT/OUTPUT: leave this section intact.\n'+JAVA_SCANNER+JAVA_JSON+'public static void main(String[] args)throws Exception{FastScanner in=new FastScanner();\n'+java_io+'\n}\n}\n',
    }
