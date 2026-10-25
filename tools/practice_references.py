"""Private source templates for the introductory stdin/stdout packages."""

PYTHON = {
    'add-two-numbers': '''a, b = int(next(data)), int(next(data))
output.write(str(a + b) + '\\n')''',
    'longest-rising-streak': '''for _ in range(int(next(data))):
    n = int(next(data))
    previous = int(next(data))
    best = current = 1
    for _ in range(n - 1):
        value = int(next(data))
        current = current + 1 if value > previous else 1
        best = max(best, current)
        previous = value
    output.write(str(best) + '\\n')''',
    'most-frequent-reading': '''counts = {}
for _ in range(int(next(data))):
    value = int(next(data))
    counts[value] = counts.get(value, 0) + 1
value = min(counts, key=lambda x: (-counts[x], x))
output.write(f'{value} {counts[value]}\\n')''',
    'palindrome-check': '''text = stream.readline().rstrip('\\r\\n')
left, right = 0, len(text) - 1
def alnum(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9'
while left < right:
    if not alnum(text[left]):
        left += 1
    elif not alnum(text[right]):
        right -= 1
    elif text[left].lower() != text[right].lower():
        output.write('NO\\n')
        return
    else:
        left += 1
        right -= 1
output.write('YES\\n')''',
    'g-tree-ancestor-query': '''n = int(next(data))
children = [[] for _ in range(n + 1)]
for _ in range(n - 1):
    p, c = int(next(data)), int(next(data))
    children[p].append(c)
tin, tout = [0] * (n + 1), [0] * (n + 1)
stack, clock = [1], 0
while stack:
    node = stack.pop()
    if node < 0:
        tout[-node] = clock
    else:
        tin[node] = clock
        clock += 1
        stack.append(-node)
        stack.extend(children[node])
for _ in range(int(next(data))):
    u, v = int(next(data)), int(next(data))
    output.write('YES\\n' if tin[u] <= tin[v] < tout[u] else 'NO\\n')''',
    'shortest-grid-route': '''from collections import deque
rows, cols = int(next(data)), int(next(data))
grid = [next(data) for _ in range(rows)]
start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 'S')
distance = [[-1] * cols for _ in range(rows)]
distance[start[0]][start[1]] = 0
queue = deque([start])
while queue:
    r, c = queue.popleft()
    if grid[r][c] == 'E':
        output.write(str(distance[r][c]) + '\\n')
        return
    for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#' and distance[nr][nc] < 0:
            distance[nr][nc] = distance[r][c] + 1
            queue.append((nr, nc))
output.write('-1\\n')''',
    'longest-unique-segment': '''last = {}
left = best = 0
for right in range(int(next(data))):
    value = int(next(data))
    left = max(left, last.get(value, -1) + 1)
    last[value] = right
    best = max(best, right - left + 1)
output.write(str(best) + '\\n')''',
}

JAVASCRIPT = {
    'add-two-numbers': "console.log(number() + number());",
    'longest-rising-streak': '''const t = number();
for (let test = 0; test < t; test++) {
  const n = number(); let previous = number(), best = 1, current = 1;
  for (let i = 1; i < n; i++) {
    const value = number(); current = value > previous ? current + 1 : 1;
    best = Math.max(best, current); previous = value;
  }
  answers.push(String(best));
}
console.log(answers.join('\\n'));''',
    'most-frequent-reading': '''const n = number(), counts = new Map();
let bestValue = Infinity, bestCount = 0;
for (let i = 0; i < n; i++) {
  const value = number(), count = (counts.get(value) || 0) + 1;
  counts.set(value, count);
  if (count > bestCount || (count === bestCount && value < bestValue)) {
    bestValue = value; bestCount = count;
  }
}
console.log(bestValue + ' ' + bestCount);''',
    'palindrome-check': '''const text = raw.replace(/[\\r\\n]+$/, '');
const alnum = c => /[a-zA-Z0-9]/.test(c);
let left = 0, right = text.length - 1, valid = true;
while (left < right) {
  if (!alnum(text[left])) left++;
  else if (!alnum(text[right])) right--;
  else if (text[left].toLowerCase() !== text[right].toLowerCase()) { valid = false; break; }
  else { left++; right--; }
}
console.log(valid ? 'YES' : 'NO');''',
    'g-tree-ancestor-query': '''const n = number(), children = Array.from({length:n + 1}, () => []);
for (let i = 1; i < n; i++) { const p = number(), c = number(); children[p].push(c); }
const tin = new Int32Array(n + 1), tout = new Int32Array(n + 1), stack = [1];
let clock = 0;
while (stack.length) {
  const node = stack.pop();
  if (node < 0) tout[-node] = clock;
  else { tin[node] = clock++; stack.push(-node); for (const c of children[node]) stack.push(c); }
}
const q = number();
for (let i = 0; i < q; i++) {
  const u = number(), v = number(); answers.push(tin[u] <= tin[v] && tin[v] < tout[u] ? 'YES' : 'NO');
}
console.log(answers.join('\\n'));''',
    'shortest-grid-route': '''const rows = number(), cols = number(), grid = [];
let start = -1;
for (let r = 0; r < rows; r++) {
  grid.push(token()); const c = grid[r].indexOf('S'); if (c >= 0) start = r * cols + c;
}
const dist = new Int32Array(rows * cols).fill(-1), queue = [start];
dist[start] = 0; let result = -1;
for (let head = 0; head < queue.length; head++) {
  const cell = queue[head], r = Math.floor(cell / cols), c = cell % cols;
  if (grid[r][c] === 'E') { result = dist[cell]; break; }
  for (const [nr,nc] of [[r-1,c],[r+1,c],[r,c-1],[r,c+1]]) {
    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
      const next = nr * cols + nc;
      if (grid[nr][nc] !== '#' && dist[next] < 0) { dist[next] = dist[cell] + 1; queue.push(next); }
    }
  }
}
console.log(result);''',
    'longest-unique-segment': '''const n = number(), last = new Map(); let left = 0, best = 0;
for (let right = 0; right < n; right++) {
  const value = number(); left = Math.max(left, (last.get(value) ?? -1) + 1);
  last.set(value, right); best = Math.max(best, right - left + 1);
}
console.log(best);''',
}

CPP = {
    'add-two-numbers': "long long a,b; cin >> a >> b; cout << a+b << '\\n';",
    'longest-rising-streak': '''int t; cin >> t;
while(t--) { int n,previous; cin >> n >> previous; int best=1,current=1;
  for(int i=1;i<n;i++) { int value; cin >> value; current=value>previous?current+1:1; best=max(best,current); previous=value; }
  cout << best << '\\n';
}''',
    'most-frequent-reading': '''int n; cin >> n; unordered_map<int,int> counts;
int bestValue=INT_MAX,bestCount=0;
for(int i=0;i<n;i++) { int v; cin >> v; int count=++counts[v];
  if(count>bestCount || (count==bestCount && v<bestValue)) { bestCount=count; bestValue=v; }
}
cout << bestValue << ' ' << bestCount << '\\n';''',
    'palindrome-check': '''string text; getline(cin,text);
auto alnum=[](char c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9');};
int l=0,r=(int)text.size()-1; bool valid=true;
while(l<r) { if(!alnum(text[l])) ++l; else if(!alnum(text[r])) --r;
  else if(tolower((unsigned char)text[l])!=tolower((unsigned char)text[r])) {valid=false;break;}
  else {++l;--r;}
}
cout << (valid?"YES":"NO") << '\\n';''',
    'g-tree-ancestor-query': '''int n; cin >> n; vector<vector<int>> children(n+1);
for(int i=1;i<n;i++) {int p,c;cin>>p>>c;children[p].push_back(c);}
vector<int> tin(n+1),tout(n+1),st{1}; int clock=0;
while(!st.empty()) {int v=st.back();st.pop_back();if(v<0)tout[-v]=clock;
  else {tin[v]=clock++;st.push_back(-v);for(int c:children[v])st.push_back(c);}}
int q;cin>>q;while(q--){int u,v;cin>>u>>v;cout<<(tin[u]<=tin[v]&&tin[v]<tout[u]?"YES":"NO")<<'\\n';}''',
    'shortest-grid-route': '''int rows,cols;cin>>rows>>cols;vector<string> grid(rows);int start=0;
for(int r=0;r<rows;r++){cin>>grid[r];for(int c=0;c<cols;c++)if(grid[r][c]=='S')start=r*cols+c;}
vector<int> dist(rows*cols,-1);queue<int> q;q.push(start);dist[start]=0;
int answer=-1,dr[]={-1,1,0,0},dc[]={0,0,-1,1};
while(!q.empty()){int x=q.front();q.pop();int r=x/cols,c=x%cols;
  if(grid[r][c]=='E'){answer=dist[x];break;}
  for(int d=0;d<4;d++){int nr=r+dr[d],nc=c+dc[d];
    if(nr>=0&&nr<rows&&nc>=0&&nc<cols&&grid[nr][nc]!='#'&&dist[nr*cols+nc]<0){
      dist[nr*cols+nc]=dist[x]+1;q.push(nr*cols+nc);}}}
cout<<answer<<'\\n';''',
    'longest-unique-segment': '''int n;cin>>n;unordered_map<int,int> last;int left=0,best=0;
for(int r=0;r<n;r++){int v;cin>>v;auto it=last.find(v);if(it!=last.end())left=max(left,it->second+1);
last[v]=r;best=max(best,r-left+1);}cout<<best<<'\\n';''',
}

JAVA = {
    'add-two-numbers': 'long a=in.number(),b=in.number(); System.out.println(a+b);',
    'longest-rising-streak': '''int t=in.number(); StringBuilder out=new StringBuilder();
while(t-->0){int n=in.number(),previous=in.number(),best=1,current=1;
  for(int i=1;i<n;i++){int value=in.number();current=value>previous?current+1:1;best=Math.max(best,current);previous=value;}
  out.append(best).append('\\n');}System.out.print(out);''',
    'most-frequent-reading': '''int n=in.number(),bestValue=Integer.MAX_VALUE,bestCount=0; Map<Integer,Integer> counts=new HashMap<>();
for(int i=0;i<n;i++){int v=in.number(),count=counts.getOrDefault(v,0)+1;counts.put(v,count);
  if(count>bestCount||(count==bestCount&&v<bestValue)){bestCount=count;bestValue=v;}}
System.out.println(bestValue+" "+bestCount);''',
    'palindrome-check': '''String text=new BufferedReader(new InputStreamReader(System.in)).readLine();
int l=0,r=text.length()-1;boolean valid=true;
while(l<r){char a=text.charAt(l),b=text.charAt(r);
  if(!asciiAlnum(a))l++;else if(!asciiAlnum(b))r--;
  else if(Character.toLowerCase(a)!=Character.toLowerCase(b)){valid=false;break;}else{l++;r--;}}
System.out.println(valid?"YES":"NO");''',
    'g-tree-ancestor-query': '''int n=in.number();int[] head=new int[n+1],to=new int[n-1],next=new int[n-1];Arrays.fill(head,-1);
for(int i=0;i<n-1;i++){int p=in.number(),c=in.number();to[i]=c;next[i]=head[p];head[p]=i;}
int[] tin=new int[n+1],tout=new int[n+1],stack=new int[2*n+1];int size=0,clock=0;stack[size++]=1;
while(size>0){int v=stack[--size];if(v<0)tout[-v]=clock;else{tin[v]=clock++;stack[size++]=-v;
  for(int e=head[v];e>=0;e=next[e])stack[size++]=to[e];}}
int q=in.number();StringBuilder out=new StringBuilder();while(q-->0){int u=in.number(),v=in.number();
out.append(tin[u]<=tin[v]&&tin[v]<tout[u]?"YES\\n":"NO\\n");}System.out.print(out);''',
    'shortest-grid-route': '''int rows=in.number(),cols=in.number(),start=0;String[] grid=new String[rows];
for(int r=0;r<rows;r++){grid[r]=in.token();int c=grid[r].indexOf('S');if(c>=0)start=r*cols+c;}
int[] dist=new int[rows*cols],queue=new int[rows*cols],dr={-1,1,0,0},dc={0,0,-1,1};Arrays.fill(dist,-1);
int tail=0,answer=-1;queue[tail++]=start;dist[start]=0;
for(int h=0;h<tail;h++){int x=queue[h],r=x/cols,c=x%cols;if(grid[r].charAt(c)=='E'){answer=dist[x];break;}
  for(int d=0;d<4;d++){int nr=r+dr[d],nc=c+dc[d];if(nr>=0&&nr<rows&&nc>=0&&nc<cols){int y=nr*cols+nc;
    if(grid[nr].charAt(nc)!='#'&&dist[y]<0){dist[y]=dist[x]+1;queue[tail++]=y;}}}}
System.out.println(answer);''',
    'longest-unique-segment': '''int n=in.number(),left=0,best=0;Map<Integer,Integer> last=new HashMap<>();
for(int r=0;r<n;r++){int v=in.number();left=Math.max(left,last.getOrDefault(v,-1)+1);last.put(v,r);best=Math.max(best,r-left+1);}
System.out.println(best);''',
}

JAVA_SCANNER = '''static class FastScanner {
  private final InputStream stream=System.in;
  private final byte[] buffer=new byte[65536]; private int position=0,length=0;
  int read() throws IOException {if(position>=length){length=stream.read(buffer);position=0;if(length<0)return -1;}return buffer[position++];}
  String token() throws IOException {StringBuilder s=new StringBuilder();int c;do{c=read();}while(c>=0&&c<=32);
    while(c>32){s.append((char)c);c=read();}return s.toString();}
  int number() throws IOException {return Integer.parseInt(token());}
}
'''


def sources(slug):
    """Python solve() supports in-process differential tests without subprocesses."""
    import textwrap
    python = '"""Private organizer reference; auxiliary bounds exclude stored I/O."""\nimport sys\n\n'
    python += 'def tokens(stream):\n    for line in stream:\n        yield from line.split()\n\n'
    python += 'def solve(stream, output):\n'
    if slug != 'palindrome-check':
        python += '    data = iter(tokens(stream))\n'
    python += textwrap.indent(PYTHON[slug], '    ') + '\n\n'
    python += "if __name__ == '__main__':\n    solve(sys.stdin, sys.stdout)\n"
    js = "// Private organizer reference. Tokenized input and buffered output count toward total space.\nconst raw = require('fs').readFileSync(0, 'utf8');\n"
    if slug != 'palindrome-check':
        js += "let position = 0; const words = raw.trim().split(/\\s+/);\nconst token = () => words[position++], number = () => Number(token());\nconst answers = [];\n"
    js += JAVASCRIPT[slug] + '\n'
    cpp = '#include <bits/stdc++.h>\nusing namespace std;\nint main(){ios::sync_with_stdio(false);cin.tie(nullptr);\n' + CPP[slug] + '\n}\n'
    java = 'import java.io.*;\nimport java.util.*;\npublic class Main {\n' + JAVA_SCANNER
    java += "static boolean asciiAlnum(char c){return c>='a'&&c<='z'||c>='A'&&c<='Z'||c>='0'&&c<='9';}\n"
    java += 'public static void main(String[] args) throws Exception {\nFastScanner in=new FastScanner();\n' + JAVA[slug] + '\n}\n}\n'
    return {'reference.py': python, 'reference.js': js, 'reference.cpp': cpp, 'Main.java': java}


def starters(slug):
    """Parse the actual input contract without providing the reference algorithm."""
    py = {
        'add-two-numbers': 'a, b = int(next(data)), int(next(data))\n# TODO: print the sum.',
        'longest-rising-streak': 'for _ in range(int(next(data))):\n    n = int(next(data))\n    temperatures = [int(next(data)) for _ in range(n)]\n    # TODO: print the longest strictly increasing consecutive streak.',
        'most-frequent-reading': 'n = int(next(data))\nvalues = [int(next(data)) for _ in range(n)]\n# TODO: print the most frequent value and its frequency; smallest value wins ties.',
        'palindrome-check': "text = sys.stdin.readline().rstrip('\\r\\n')\n# TODO: compare ASCII letters/digits ignoring case; print YES or NO.",
        'g-tree-ancestor-query': 'n = int(next(data))\nedges = [(int(next(data)), int(next(data))) for _ in range(n - 1)]\n# TODO: prepare the fixed-root tree.\nfor _ in range(int(next(data))):\n    u, v = int(next(data)), int(next(data))\n    # TODO: print YES or NO for this query.',
        'shortest-grid-route': 'rows, cols = int(next(data)), int(next(data))\ngrid = [next(data) for _ in range(rows)]\n# TODO: print the shortest four-direction route length, or -1.',
        'longest-unique-segment': 'n = int(next(data))\nvalues = [int(next(data)) for _ in range(n)]\n# TODO: print the longest consecutive segment with distinct values.',
    }
    js = {
        'add-two-numbers': 'const a=number(), b=number();',
        'longest-rising-streak': 'const t=number();\nfor(let test=0;test<t;test++){const n=number(), temperatures=Array.from({length:n},number);\n  // TODO: print one answer for this test case.\n}',
        'most-frequent-reading': 'const n=number(), values=Array.from({length:n},number);',
        'palindrome-check': "const text=raw.replace(/[\\r\\n]+$/, '');",
        'g-tree-ancestor-query': 'const n=number(), edges=[];\nfor(let i=1;i<n;i++)edges.push([number(),number()]);\nconst q=number();\nfor(let i=0;i<q;i++){const u=number(),v=number();\n  // TODO: print YES or NO.\n}',
        'shortest-grid-route': 'const rows=number(), cols=number(), grid=Array.from({length:rows},token);',
        'longest-unique-segment': 'const n=number(), values=Array.from({length:n},number);',
    }
    cpp = {
        'add-two-numbers': 'long long a,b; cin>>a>>b;',
        'longest-rising-streak': 'int t;cin>>t;while(t--){int n;cin>>n;vector<int> temperatures(n);for(int &v:temperatures)cin>>v;\n// TODO: print one answer.\n}',
        'most-frequent-reading': 'int n;cin>>n;vector<int> values(n);for(int &v:values)cin>>v;',
        'palindrome-check': 'string text;getline(cin,text);',
        'g-tree-ancestor-query': 'int n;cin>>n;vector<pair<int,int>> edges(n-1);for(auto &e:edges)cin>>e.first>>e.second;\nint q;cin>>q;while(q--){int u,v;cin>>u>>v;\n// TODO: print YES or NO.\n}',
        'shortest-grid-route': 'int rows,cols;cin>>rows>>cols;vector<string> grid(rows);for(string &row:grid)cin>>row;',
        'longest-unique-segment': 'int n;cin>>n;vector<int> values(n);for(int &v:values)cin>>v;',
    }
    java = {
        'add-two-numbers': 'long a=in.number(),b=in.number();',
        'longest-rising-streak': 'int t=in.number();while(t-->0){int n=in.number();int[] temperatures=new int[n];for(int i=0;i<n;i++)temperatures[i]=in.number();\n// TODO: print one answer.\n}',
        'most-frequent-reading': 'int n=in.number();int[] values=new int[n];for(int i=0;i<n;i++)values[i]=in.number();',
        'palindrome-check': 'String text=new BufferedReader(new InputStreamReader(System.in)).readLine();',
        'g-tree-ancestor-query': 'int n=in.number();int[][] edges=new int[n-1][2];for(int i=0;i<n-1;i++){edges[i][0]=in.number();edges[i][1]=in.number();}\nint q=in.number();while(q-->0){int u=in.number(),v=in.number();\n// TODO: print YES or NO.\n}',
        'shortest-grid-route': 'int rows=in.number(),cols=in.number();String[] grid=new String[rows];for(int i=0;i<rows;i++)grid[i]=in.token();',
        'longest-unique-segment': 'int n=in.number();int[] values=new int[n];for(int i=0;i<n;i++)values[i]=in.number();',
    }
    py_prefix = 'import sys\n\n'
    if slug != 'palindrome-check':
        py_prefix += 'data = (word for line in sys.stdin for word in line.split())\n'
    js_prefix = "const raw=require('fs').readFileSync(0,'utf8');\n"
    if slug != 'palindrome-check':
        js_prefix += "const words=raw.trim().split(/\\s+/);let position=0;\nconst token=()=>words[position++],number=()=>Number(token());\n"
    return {
        'main.py': py_prefix + py[slug] + '\n',
        'main.js': js_prefix + js[slug] + '\n// TODO: solve the problem and print only the required answer(s).\n',
        'main.cpp': '#include <bits/stdc++.h>\nusing namespace std;\nint main(){ios::sync_with_stdio(false);cin.tie(nullptr);\n' + cpp[slug] + '\n// TODO: solve and print the required answer(s).\n}\n',
        'Main.java': 'import java.io.*;\nimport java.util.*;\npublic class Main{\n' + JAVA_SCANNER + 'public static void main(String[] args)throws Exception{FastScanner in=new FastScanner();\n' + java[slug] + '\n// TODO: solve and print the required answer(s).\n}\n}\n',
    }
