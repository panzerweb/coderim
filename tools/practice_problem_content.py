"""Deterministic, independently checked Easy/Medium content authoring.

Run this trusted tool to reproduce only the seven introductory packages.
No application modules depend on authoring tools.
"""
import io
import json
import random
from collections import Counter
from pathlib import Path
from practice_references import sources, starters

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    'add-two-numbers': {
        'title': 'Add Two Numbers', 'difficulty': 'Easy', 'minutes': 5, 'tags': ['Arithmetic', 'Input and Output'],
        'description': 'A tiny problem for testing the submission flow. Read two integers and print their sum.',
        'input': 'Two whitespace-separated integers A and B, each from -1,000,000,000 to 1,000,000,000.',
        'output': 'Print A + B as one integer. Do not print prompts or labels.',
        'requirements': [('operands', 'Read both integer operands.'), ('addition', 'Compute their arithmetic sum.'),
            ('signed-values', 'Handle negative operands and zero.'), ('answer-only', 'Print only the required integer answer.')],
        'variables': {'A, B': 'The two bounded integer operands'}, 'time': {'Compute': 'O(1)'}, 'space': 'O(1)',
        'editorial': 'Parse both signed integers and add them. All answers fit a signed 32-bit integer; using a wider integer is also valid.',
    },
    'longest-rising-streak': {
        'title': 'Longest Rising Streak', 'difficulty': 'Easy', 'minutes': 20, 'tags': ['Arrays', 'Linear Scan'],
        'description': "A weather station records daily temperatures. Find the longest consecutive streak where every day's temperature is strictly higher than the previous day's. Days must be adjacent in the original list; equal temperatures break a streak.",
        'input': 'The first integer is T (1 <= T <= 10). For each test case, read N (1 <= N <= 100,000), then N temperatures from -1,000,000 to 1,000,000. The sum of N across test cases is at most 100,000. Whitespace may separate the integers across lines.',
        'output': 'Print one streak length per test case, in input order. A singleton streak has length 1.',
        'requirements': [('strict-rise', 'Only strictly higher adjacent temperatures extend a streak.'), ('consecutive', 'Find the longest consecutive streak rather than a subsequence.'),
            ('boundaries', 'Handle singleton, equal, and signed temperatures.'), ('independent-cases', 'Reset state and print one answer for each test case.')],
        'variables': {'N': 'Temperatures in a test case', 'T': 'Test cases'}, 'time': {'All cases': 'O(sum N)'},
        'space': 'O(1) when processing temperatures sequentially',
        'editorial': 'Keep the previous temperature, the current rising run length, and the best length. Reset the current length to 1 at every non-increase. Reset all state between cases.',
    },
    'most-frequent-reading': {
        'title': 'Most Frequent Reading', 'difficulty': 'Easy', 'minutes': 20, 'tags': ['Frequency Counting', 'Maps'],
        'description': 'Find the most frequent reading. If several values have the same highest frequency, choose the smallest numeric value.',
        'input': 'Read N (1 <= N <= 100,000), then N integers from -1,000,000 to 1,000,000. Integers may be separated by any whitespace.',
        'output': 'Print the selected value and its frequency, separated by a space.',
        'requirements': [('count', 'Count occurrences across the entire input.'), ('maximum', 'Choose a value with the highest frequency.'),
            ('tie', 'Choose the smallest numeric value when frequencies tie.'), ('signed-output', 'Support signed readings and print value followed by frequency.')],
        'variables': {'N': 'Readings', 'D': 'Distinct readings'}, 'time': {'Frequency counting': 'Expected O(N) with a hash table'}, 'space': 'O(D)',
        'editorial': 'Count all readings in a map, then choose by descending count and ascending numeric value. Online updates of the best pair are also valid. Sorting is an alternative correct approach.',
    },
    'palindrome-check': {
        'title': 'Palindrome Check', 'difficulty': 'Easy', 'minutes': 20, 'tags': ['Strings', 'Two Pointers'],
        'description': 'Determine whether a line reads the same forward and backward when comparing only ASCII letters and digits. Ignore letter case, punctuation, and spaces. A line containing no letters or digits is a palindrome.',
        'input': 'Read one line containing 1 to 100,000 printable ASCII characters (codes 32 through 126). The line ending is not part of the text. Leading and trailing spaces may occur.',
        'output': 'Print YES if the normalized text is a palindrome; otherwise print NO.',
        'requirements': [('filter', 'Compare only ASCII letters and digits.'), ('case', 'Ignore differences in letter case.'),
            ('mirror', 'Compare the complete normalized text in reverse order.'), ('empty-singleton', 'Accept empty normalized text and a single normalized character.')],
        'variables': {'L': 'Characters in the input line'}, 'time': {'Two-pointer comparison': 'O(L)'},
        'space': 'O(1) beyond the stored input line',
        'editorial': 'Use pointers from both ends. Skip non-alphanumeric characters and compare remaining characters after case folding. The pointers use constant extra space; storing or normalizing the whole line consumes O(L) total space.',
    },
    'g-tree-ancestor-query': {
        'title': 'G-Tree Node Ancestor Query', 'difficulty': 'Medium', 'minutes': 40, 'tags': ['Trees', 'DFS', 'Ancestor Queries'],
        'description': 'A tree has nodes numbered 1 through N and is rooted at node 1. For each pair U V, determine whether U is an ancestor of V. Every node is an ancestor of itself. The root never changes.',
        'input': 'Read N (1 <= N <= 100,000), followed by exactly N-1 parent-child pairs P C describing a valid connected tree rooted at 1. Edges may appear in any order. Read Q (1 <= Q <= 100,000), followed by Q pairs U V. All labels are between 1 and N.',
        'output': 'Print YES or NO for every query, in input order.',
        'requirements': [('ancestor', 'Determine ancestor direction under the fixed root 1.'), ('self-root', 'Handle self-ancestry and root relationships.'),
            ('edge-order', 'Build the tree regardless of edge ordering.'), ('queries', 'Return one correct answer per query across branches and depths.')],
        'variables': {'N': 'Tree nodes', 'Q': 'Queries'}, 'time': {'Preprocessing': 'O(N)', 'Each query': 'O(1)', 'Total': 'O(N + Q)'}, 'space': 'O(N)',
        'editorial': 'An iterative DFS assigns entry times and exclusive exit times. U is an ancestor of V exactly when tin[U] <= tin[V] < tout[U]. Use an explicit stack so a chain of 100,000 nodes does not overflow the call stack.',
    },
    'shortest-grid-route': {
        'title': 'Shortest Grid Route', 'difficulty': 'Medium', 'minutes': 40, 'tags': ['Graphs', 'BFS', 'Grids'],
        'description': 'Find the fewest moves from S to E in a grid. Each move goes one cell up, down, left, or right. You cannot leave the grid or enter a wall (#). Every move costs one.',
        'input': 'Read R C (1 <= R,C <= 500; R*C >= 2), followed by R rows of exactly C symbols. A dot (.) is open, # is a wall, S is the unique start, and E is the unique exit. Start and exit occupy distinct cells.',
        'output': 'Print the minimum number of moves from S to E, or -1 if no route exists. Count moves, not visited cells.',
        'requirements': [('movement', 'Use only in-bounds horizontal or vertical moves.'), ('walls', 'Avoid walls and detect an unreachable exit.'),
            ('shortest', 'Return the shortest available route rather than any route.'), ('distance', 'Count moves correctly for narrow, adjacent, and large grids.')],
        'variables': {'R': 'Grid rows', 'C': 'Grid columns'}, 'time': {'Breadth-first search': 'O(RC)'}, 'space': 'O(RC)',
        'editorial': 'Breadth-first search processes cells in increasing distance. Mark a cell when enqueuing it and store its distance, starting at 0 for S. DFS finding an arbitrary path does not guarantee the shortest route.',
    },
    'longest-unique-segment': {
        'title': 'Longest Unique Segment', 'difficulty': 'Medium', 'minutes': 40, 'tags': ['Arrays', 'Sliding Window', 'Maps'],
        'description': 'Find the length of the longest consecutive segment containing no repeated values. The segment must be contiguous in the original list.',
        'input': 'Read N (1 <= N <= 100,000), followed by N integers from -1,000,000 to 1,000,000. Integers may be separated by any whitespace.',
        'output': 'Print the maximum segment length as one integer.',
        'requirements': [('contiguous', 'Measure consecutive segments rather than distinct values globally.'), ('unique', 'Exclude every repeated value from the current segment.'),
            ('window', 'Move the left boundary forward without losing valid overlapping segments.'), ('bounds', 'Handle singleton, signed, all-equal, and all-distinct inputs.')],
        'variables': {'N': 'Input values', 'D': 'Distinct input values'}, 'time': {'Sliding window': 'Expected O(N) with a hash table'}, 'space': 'O(D)',
        'editorial': 'Track the last position of each value. On a repetition, set left = max(left, last[value] + 1), then update the best window length. Never move left backward because of an occurrence outside the current window.',
    },
}


def array_input(values):
    return str(len(values)) + '\n' + ' '.join(map(str, values)) + '\n'


def streak_input(cases):
    return str(len(cases)) + '\n' + ''.join(array_input(values) for values in cases)


def tree_input(n, edges, queries):
    return str(n) + '\n' + ''.join(f'{p} {c}\n' for p, c in edges) + str(len(queries)) + '\n' + ''.join(f'{u} {v}\n' for u, v in queries)


def grid_input(rows):
    return f'{len(rows)} {len(rows[0])}\n' + '\n'.join(rows) + '\n'


def oracle(slug, stdin):
    """Independent small-case oracles; scale outputs use explicit known patterns."""
    if slug == 'palindrome-check':
        cleaned = ''.join(c.lower() for c in stdin.rstrip('\r\n') if c.isascii() and c.isalnum())
        return ('YES' if cleaned == cleaned[::-1] else 'NO') + '\n'
    words = iter(stdin.split())
    if slug == 'add-two-numbers':
        return str(sum(map(int, words))) + '\n'
    if slug == 'longest-rising-streak':
        result = []
        for _ in range(int(next(words))):
            values = [int(next(words)) for _ in range(int(next(words)))]
            # Break into maximal runs using their start/end boundaries.
            starts = [0] + [i for i in range(1, len(values)) if values[i] <= values[i - 1]] + [len(values)]
            result.append(str(max(b - a for a, b in zip(starts, starts[1:]))))
        return '\n'.join(result) + '\n'
    if slug in ('most-frequent-reading', 'longest-unique-segment'):
        values = [int(next(words)) for _ in range(int(next(words)))]
        if slug == 'most-frequent-reading':
            counts = Counter(values)
            value = sorted(counts, key=lambda v: (-counts[v], v))[0]
            return f'{value} {counts[value]}\n'
        best = 0
        for left in range(len(values)):
            for right in range(left + best + 1, len(values) + 1):
                part = values[left:right]
                if len(set(part)) != len(part):
                    break
                best = len(part)
        return str(best) + '\n'
    if slug == 'g-tree-ancestor-query':
        n = int(next(words)); parent = [0] * (n + 1)
        for _ in range(n - 1):
            p, c = int(next(words)), int(next(words)); parent[c] = p
        answers = []
        for _ in range(int(next(words))):
            u, v = int(next(words)), int(next(words))
            while v and v != u:
                v = parent[v]
            answers.append('YES' if v == u else 'NO')
        return '\n'.join(answers) + '\n'
    rows, cols = int(next(words)), int(next(words)); grid = [next(words) for _ in range(rows)]
    start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 'S')
    end = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 'E')
    # Repeated relaxation, deliberately different from the queue-based reference.
    distance = {start: 0}
    for _ in range(rows * cols):
        previous = dict(distance)
        for (r, c), d in previous.items():
            for nr, nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#':
                    distance[nr, nc] = min(distance.get((nr, nc), rows * cols + 1), d + 1)
        if distance == previous:
            break
    return str(distance.get(end, -1)) + '\n'


def cases(slug):
    """Return samples and hidden cases; expected samples are fixed by hand."""
    rng = random.Random(7081 + list(SPECS).index(slug))
    samples, hidden = [], []
    reqs = [r[0] for r in SPECS[slug]['requirements']]
    def add(category, stdin, expected=None, sample=False, explanation='', requirements=None):
        target = samples if sample else hidden
        key = f'sample-{len(samples)+1:02}' if sample else f'{category}-{sum(c[1] == category for c in hidden)+1:02}'
        actual = oracle(slug, stdin) if expected is None else expected
        mapped = list(requirements or reqs)
        if slug == 'palindrome-check':
            text=stdin.rstrip('\r\n');clean=''.join(c for c in text if c.isalnum())
            mapped=['mirror'] if len(clean)>1 else ['empty-singleton']
            if any(not c.isalnum() for c in text):mapped.append('filter')
            if any(c.isupper() for c in clean):mapped.append('case')
        elif slug == 'most-frequent-reading':
            counts=Counter(map(int,stdin.split()[1:]));mapped=[r for r in reqs if r!='tie']
            if list(counts.values()).count(max(counts.values()))>1:mapped.append('tie')
        elif slug == 'longest-rising-streak' and int(stdin.split()[0])==1:
            mapped=[r for r in mapped if r!='independent-cases']
        elif slug == 'shortest-grid-route':
            mapped=['movement','distance']
            if '#' in stdin:mapped.append('walls')
            if int(stdin.split()[0])*int(stdin.split()[1])>=4:mapped.append('shortest')
        elif slug == 'add-two-numbers' and all(int(v)>0 for v in stdin.split()):
            mapped=[r for r in mapped if r!='signed-values']
        target.append((key, category, stdin, actual, explanation, mapped))
    if slug == 'add-two-numbers':
        for a,b in ((2,3),(-7,10),(0,0)):
            add('basic', f'{a} {b}\n', f'{a+b}\n', True, f'The sum of {a} and {b} is {a+b}.')
        groups = {'basic': [(1,1),(5,8),(20,30),(123,456)], 'boundaries': [(0,9),(9,0),(0,0),(1,-1)],
            'behavior': [(-5,-8),(-20,3),(3,-20),(-40,40)],
            'scale': [(10**9,10**9),(-10**9,-10**9),(10**9,-10**9),(-10**9,999999999)]}
        for category,pairs in groups.items():
            for a,b in pairs:
                mapped = reqs if a <= 0 or b <= 0 else [reqs[i] for i in (0,1,3)]
                add(category, f'  {a}\n{b}  \n', requirements=mapped)
    elif slug == 'longest-rising-streak':
        add('basic', streak_input([[1,2,4,3,5,6,7],[1,2,2,3,4,1]]), '4\n3\n', True, 'The longest consecutive rising streaks have lengths 4 and 3.')
        add('boundaries', streak_input([[8],[-3,-2,-1],[2,2,2]]), '1\n3\n1\n', True, 'Singletons and equal readings have length 1; negative temperatures can rise.')
        add('behavior', streak_input([[1,5,2,3,4],[9,7,5]]), '3\n1\n', True, 'A subsequence does not count; each test case starts fresh.')
        groups = {'basic': [[[1,2,3]],[[3,2,1]],[[-3,-1,0]],[[1,2,0,1]]],
            'boundaries': [[[1]],[[2,2,2]],[[-1000000,1000000]],[[0,-1,0,0,1]]],
            'behavior': [[[1,10,2,3,4]],[[1,2,3],[1]],[[4,4],[3,2],[1,2]],[[1,2,3,0,1,2,3,4]]],
            'scale': [[list(range(100000))],[list(range(100000,0,-1))],[[0]*100000], [list(range(10000)) for _ in range(10)]]}
        for category,inputs in groups.items():
            for values in inputs:
                add(category, streak_input(values), requirements=reqs if len(values)>1 else reqs[:3])
    elif slug in ('most-frequent-reading', 'longest-unique-segment'):
        frequency = slug == 'most-frequent-reading'
        sample_values = [[4,2,4,2,4],[-1,2,-1,2],[7]] if frequency else [[1,2,1,3,4],[-2,-2,-1,0],[9]]
        sample_outputs = ['4 3\n','-1 2\n','7 1\n'] if frequency else ['4\n','3\n','1\n']
        explanations = ['Count all readings and choose the highest frequency.', 'Signed values follow the same rules.', 'A single reading is valid.'] if frequency else ['The final four values form a unique consecutive segment.', 'The repeated initial value is excluded.', 'A singleton has length 1.']
        for values,expected,explanation in zip(sample_values,sample_outputs,explanations):
            add('basic', array_input(values), expected, True, explanation)
        groups = {'basic': [[1,2,3],[1,1,1],[3,2,3,1],[8,9,8,9,8]],
            'boundaries': [[-1000000],[0,0],[1000000,-1000000,0],[-2,-1,-2,-1]],
            'behavior': [[2,1,2,1],[1,2,2,1,3],[1,2,3,2,4,1,5],[4,3,2,1,4,5,3]]}
        for category,inputs in groups.items():
            for values in inputs:
                add(category, array_input(values))
        scales = [([0]*100000,'0 100000\n' if frequency else '1\n'),
            (list(range(100000)), '0 1\n' if frequency else '100000\n'),
            ([i%1000 for i in range(100000)], '0 100\n' if frequency else '1000\n'),
            ([-1000000,1000000]*50000, '-1000000 50000\n' if frequency else '2\n')]
        for values,expected in scales:
            add('scale', array_input(values), expected)
    elif slug == 'palindrome-check':
        for text,expected,explanation in [('A man, a plan, a canal: Panama!','YES\n','Ignore spaces, punctuation, and letter case.'),
                ('race a car','NO\n','The remaining letters differ when reversed.'),(' !? ','YES\n','Empty normalized text is a palindrome.')]:
            add('basic', text+'\n', expected, True, explanation)
        groups = {'basic':['abba','abc','level','12321'], 'boundaries':['x','  ','!!!',' a '],
            'behavior':['Aa','0P','No lemon, no melon.','1a2A1'],
            'scale':['A'*100000,'a'*99999+'b', ' '*100000, 'a1'*25000+'1A'*25000]}
        for category,texts in groups.items():
            for text in texts:
                mapped = [reqs[i] for i in (0,1,3)] if len(''.join(c for c in text if c.isalnum()))<=1 else reqs[:3]
                add(category, text+'\n', requirements=mapped)
    elif slug == 'g-tree-ancestor-query':
        add('basic', tree_input(6,[(1,2),(1,3),(2,4),(3,6),(2,5)],[(1,5),(3,4),(2,2)]), 'YES\nNO\nYES\n', True, 'The fifth edge is 2 5. The root is an ancestor of node 5; self-ancestry is allowed.')
        add('boundaries', tree_input(1,[],[(1,1)]), 'YES\n', True, 'A one-node tree is valid.')
        add('behavior', tree_input(4,[(3,4),(1,2),(2,3)],[(2,4),(4,2),(3,3)]), 'YES\nNO\nYES\n', True, 'Edges need not arrive in traversal order; ancestor direction matters.')
        for category in ('basic','boundaries','behavior'):
            for index in range(4):
                n=1 if category=='boundaries' and index==0 else 8+index
                edges=[(v-1 if index%2 else 1,v) for v in range(2,n+1)]
                if category=='behavior':
                    labels=list(range(2,n+1));rng.shuffle(labels);labels=[0,1]+labels
                    edges=[(labels[rng.randrange(1,v)],labels[v]) for v in range(2,n+1)];rng.shuffle(edges)
                queries=[(u,v) for u in range(1,n+1) for v in range(1,n+1)]
                mapped=reqs if category=='behavior' else [r for r in reqs if r!='edge-order']
                add(category,tree_input(n,edges,queries),requirements=mapped)
        n=100000
        chain=[(v-1,v) for v in range(2,n+1)]
        star=[(1,v) for v in range(2,n+1)]
        for edges,queries,expected in [
            (chain,[(1,n),(n,1)]*50000,'YES\nNO\n'*50000),
            (list(reversed(chain)),[(n,n),(1,1)]*50000,'YES\n'*100000),
            (star,[(2,3),(1,n)]*50000,'NO\nYES\n'*50000),
            (list(reversed([(1,n)]+[(v,v-1) for v in range(n,2,-1)])),[(n,2),(2,n)]*50000,'YES\nNO\n'*50000)]:
            add('scale',tree_input(n,edges,queries),expected)
    elif slug == 'shortest-grid-route':
        for rows,expected,explanation in [(['S..','.#.','..E'],'4\n','Go around the wall in four moves.'),
                (['S#E'],'-1\n','The wall blocks the only row.'),(['SE'],'1\n','Adjacent start and exit require one move.')]:
            add('basic',grid_input(rows),expected,True,explanation)
        groups={'basic':[['S.E'],['S..','...','..E'],['S#','..','.E'],['E..','.#.','..S']],
            'boundaries':[['SE'],['S','E'],['S#E'],['S','#','E']],
            'behavior':[['S....','.###.','...#E'],['S#E','...'],['S...E','.....','.....'],['S#..','.#E.','....']]}
        for category,grids in groups.items():
            for rows in grids:
                add(category,grid_input(rows))
        open_grid=['.'*500 for _ in range(500)];open_grid[0]='S'+'.'*499;open_grid[-1]='.'*499+'E'
        blocked=open_grid.copy();blocked[250]='#'*500
        # Alternating open rows joined at opposite ends create a single long corridor.
        snake=[]
        for r in range(499):
            snake.append('.'*500 if r%2==0 else ('#'*499+'.' if (r//2)%2==0 else '.'+'#'*499))
        snake[0]='S'+snake[0][1:];snake[-1]='E'+snake[-1][1:] if (498//2)%2 else snake[-1][:-1]+'E'
        # Row 498 ends on the left: 250 horizontal traversals and 498 vertical moves.
        for rows,expected in [(open_grid,'998\n'),(blocked,'-1\n'),(snake,str(250*499+498)+'\n'),(['S'+'.'*498+'E'],'499\n')]:
            add('scale',grid_input(rows),expected)
    # Seeded small cases supplement the structured/scale cases.
    for _ in range(4):
        if slug=='add-two-numbers': stdin=f'{rng.randrange(-10**9,10**9+1)} {rng.randrange(-10**9,10**9+1)}\n'
        elif slug=='longest-rising-streak': stdin=streak_input([[rng.randrange(-9,10) for _ in range(rng.randrange(1,40))] for _ in range(3)])
        elif slug in ('most-frequent-reading','longest-unique-segment'): stdin=array_input([rng.randrange(-9,10) for _ in range(40)])
        elif slug=='palindrome-check': stdin=''.join(rng.choice('aAbB09 !?') for _ in range(40))+'\n'
        elif slug=='g-tree-ancestor-query':
            labels=list(range(2,21));rng.shuffle(labels);labels=[0,1]+labels
            edges=[(labels[rng.randrange(1,v)],labels[v]) for v in range(2,21)];rng.shuffle(edges)
            stdin=tree_input(20,edges,[(rng.randrange(1,21),rng.randrange(1,21)) for _ in range(40)])
        else:
            rows=[''.join(rng.choice('...#') for _ in range(7)) for _ in range(6)];rows[0]='S'+rows[0][1:];rows[-1]=rows[-1][:-1]+'E';stdin=grid_input(rows)
        add('behavior',stdin)
    return samples,hidden


FAULTS = {
    'add-two-numbers': [('subtract', "import sys\na,b=map(int,sys.stdin.read().split());print(a-b)\n"), ('absolute', "import sys\na,b=map(int,sys.stdin.read().split());print(abs(a)+abs(b))\n")],
    'longest-rising-streak': [('non_strict', "import sys\nd=iter(map(int,sys.stdin.read().split()))\nfor _ in range(next(d)):\n n=next(d);a=[next(d) for _ in range(n)];best=cur=1\n for i in range(1,n):\n  cur=cur+1 if a[i]>=a[i-1] else 1;best=max(best,cur)\n print(best)\n"),
        ('subsequence', "import sys,bisect\nd=iter(map(int,sys.stdin.read().split()))\nfor _ in range(next(d)):\n n=next(d);tails=[]\n for _ in range(n):\n  v=next(d);i=bisect.bisect_left(tails,v)\n  if i==len(tails):tails.append(v)\n  else:tails[i]=v\n print(len(tails))\n")],
    'most-frequent-reading': [('largest_tie', "import sys,collections\na=list(map(int,sys.stdin.read().split()))[1:];c=collections.Counter(a);v=max(c,key=lambda x:(c[x],x));print(v,c[v])\n"), ('first', "import sys\na=list(map(int,sys.stdin.read().split()))[1:];print(a[0],a.count(a[0]))\n")],
    'palindrome-check': [('literal', "s=input();print('YES' if s==s[::-1] else 'NO')\n"), ('drops_digits', "s=''.join(c.lower() for c in input() if c.isalpha());print('YES' if s==s[::-1] else 'NO')\n")],
    'g-tree-ancestor-query': [('no_self', sources('g-tree-ancestor-query')['reference.py'].replace('tin[u] <= tin[v]', 'tin[u] < tin[v]')),
        ('reverse', sources('g-tree-ancestor-query')['reference.py'].replace('tin[u] <= tin[v] < tout[u]', 'tin[v] <= tin[u] < tout[v]'))],
    'shortest-grid-route': [('dfs_path', "import sys\nd=iter(sys.stdin.read().split());r,c=int(next(d)),int(next(d));g=[next(d) for _ in range(r)];s=next((i,j) for i in range(r) for j in range(c) if g[i][j]=='S');seen={s};st=[(*s,0)];ans=-1\nwhile st:\n i,j,k=st.pop()\n if g[i][j]=='E':ans=k;break\n for x,y in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):\n  if 0<=x<r and 0<=y<c and g[x][y]!='#' and (x,y) not in seen:seen.add((x,y));st.append((x,y,k+1))\nprint(ans)\n"),
        ('counts_cells', sources('shortest-grid-route')['reference.py'].replace('str(distance[r][c])', 'str(distance[r][c] + 1)'))],
    'longest-unique-segment': [('global_distinct', "import sys\nprint(len(set(sys.stdin.read().split()[1:])))\n"),
        ('backward_window', sources('longest-unique-segment')['reference.py'].replace('max(left, last.get(value, -1) + 1)', 'last.get(value, -1) + 1'))],
}


def generate(slug, root=None):
    spec=SPECS[slug];root=Path(root or ROOT/'problems'/slug)
    def write(name,text):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8',newline='\n')
    def json_file(name,value):write(name,json.dumps(value,indent=2)+'\n')
    metadata={'schema_version':1,'id':slug,'version':1,'title':spec['title'],'difficulty':spec['difficulty'],
        'order':4+list(SPECS).index(slug),'tags':spec['tags'],'status':'published',
        'suggested_duration_minutes':spec['minutes'],'category_weights':{'basic':20,'boundaries':20,'behavior':40,'scale':20},
        'requirements':[{'id':key,'text':text} for key,text in spec['requirements']],
        'limits':{'time_ms':2000,'memory_mb':256,'stdin_bytes':4194304 if slug=='g-tree-ancestor-query' else 1048576,'stdout_bytes':1048576},
        'starters':{'python':'starters/main.py','javascript':'starters/main.js','cpp':'starters/main.cpp','java':'starters/Main.java'},
        'reference_complexity':{'variables':spec['variables'],'time_by_phase':spec['time'],'auxiliary_space':spec['space'],
            'notes':'Reference targets describe an algorithm, not the submitted program. Include stored input/output and recursion stacks when reviewing total space. Tokenized input and buffered output in some language references consume additional space. Hash-table bounds, where stated, are expected rather than worst-case guarantees. Difficulty and duration are provisional estimates for university DSA students.'}}
    json_file('problem.json',metadata)
    write('statement.md',f"# {spec['title']}\n\n{spec['description']}\n\n## Input specification\n\n{spec['input']}\n\n## Output specification\n\n{spec['output']}\n\n## Practice information\n\nSuggested duration: {spec['minutes']} minutes (informational). Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor.\n")
    for name,source in sources(slug).items():write('author/'+name,source)
    for name,source in starters(slug).items():write('starters/'+name,source)
    write('author/editorial.md',f"# Private organizer notes: {spec['title']}\n\n{spec['editorial']}\n\nTime: {spec['time']}. Auxiliary space: {spec['space']}.\n\nAlternative correct algorithms are allowed. Expected hash-map time is not a worst-case guarantee. Account for materialized input, output, and stacks separately. Tests assess observable behavior.\n\nRegenerate with `python author/generate_tests.py`; use the repository verification tool before publishing. Sample outputs are fixed explicitly; small hidden outputs use an independent oracle. Scale outputs use known patterns or a separate linear oracle.\n")
    write('author/generate_tests.py',"from pathlib import Path\nimport sys\nROOT=Path(__file__).resolve().parents[3]\nsys.path.insert(0,str(ROOT/'tools'))\nfrom practice_problem_content import generate\nif __name__=='__main__':\n    generate(Path(__file__).resolve().parents[1].name)\n")
    for name,source in FAULTS[slug]:write('author/incorrect_solutions/'+name+'.py',source)
    samples,hidden=cases(slug)
    json_file('samples.json',[{'id':key,'category':category,'input':stdin,'expected_output':expected,'explanation':explanation,'requirements':reqs} for key,category,stdin,expected,explanation,reqs in samples])
    manifest=[]
    for key,category,stdin,expected,_,reqs in hidden:
        write(f'tests/{key}.in',stdin);write(f'tests/{key}.out',expected)
        manifest.append({'id':key,'category':category,'requirements':reqs,'input_file':f'tests/{key}.in','output_file':f'tests/{key}.out'})
    json_file('tests/manifest.json',{'cases':manifest})
    print(f'{slug}: {len(samples)} samples + {len(hidden)} hidden')
    return root


if __name__=='__main__':
    for slug in SPECS:generate(slug)
