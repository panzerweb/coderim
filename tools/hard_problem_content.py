"""Trusted authoring helpers. Generate fixed, bounded packages with saved outputs."""
import importlib.util
import io
import json
import random
from pathlib import Path
from input_starters import write_starters


def module(root):
    spec = importlib.util.spec_from_file_location(root.name.replace('-', '_') + '_reference', root / 'author/reference.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def save_package(root, metadata, samples, hidden):
    write_starters(root, root.name == 'longest-rising-streak-updates')
    reference = module(root)
    prepared_samples, manifest = [], []
    for visible, cases in ((True, samples), (False, hidden)):
        for case in cases:
            key, category, stdin, expected, explanation = case
            output = io.StringIO()
            reference.solve(io.StringIO(stdin), output)
            actual = output.getvalue()
            if expected is not None and expected != actual:
                raise AssertionError(f'Independent expected output disagrees: {key}')
            if root.name == 'longest-rising-streak-updates':
                reqs = ['independent-cases']
                if 'QUERY' in stdin:
                    reqs += ['strict-streak', 'query-boundaries']
                if 'UPDATE' in stdin:
                    reqs.append('persistent-updates')
            else:
                reqs = ['query-output']
                if 'QUERY' in stdin:
                    reqs.append('ancestor-path')
                if 'ROOT' in stdin:
                    reqs.append('logical-root')
                if any(line.startswith('QUERY ') and line.split()[1] == line.split()[2] for line in stdin.splitlines()):
                    reqs.append('self-ancestry')
            if visible:
                prepared_samples.append({'id': key, 'category': category, 'input': stdin,
                    'expected_output': actual, 'explanation': explanation, 'requirements': reqs})
            else:
                (root / 'tests').mkdir(exist_ok=True)
                (root / 'tests' / f'{key}.in').write_text(stdin, encoding='utf-8', newline='\n')
                (root / 'tests' / f'{key}.out').write_text(actual, encoding='utf-8', newline='\n')
                manifest.append({'id': key, 'category': category, 'requirements': reqs,
                    'input_file': f'tests/{key}.in', 'output_file': f'tests/{key}.out'})
    metadata.update(schema_version=1, id=root.name, version=1, difficulty='Hard', status='published',
        suggested_duration_minutes=60,
        starters={'python': 'starters/main.py', 'javascript': 'starters/main.js',
            'cpp': 'starters/main.cpp', 'java': 'starters/Main.java'})
    write_json(root / 'problem.json', metadata)
    write_json(root / 'samples.json', prepared_samples)
    write_json(root / 'tests/manifest.json', {'cases': manifest})
    total = sum(len(c[2].encode()) for c in samples + hidden)
    print(f'{root.name}: {len(samples)} samples + {len(hidden)} hidden; input bytes {total:,}')


def streak_input(cases):
    lines = [str(len(cases))]
    for values, operations in cases:
        lines.extend((f'{len(values)} {len(operations)}', ' '.join(map(str, values))))
        lines.extend(' '.join(map(str, op)) for op in operations)
    return '\n'.join(lines) + '\n'


def streak_oracle(cases, non_strict=False, ignore_updates=False):
    answers = []
    for values, operations in cases:
        values = list(values)
        for command, a, b in operations:
            if command == 'UPDATE':
                if not ignore_updates:
                    values[a - 1] = b
            else:
                best = current = 1
                for i in range(a, b):
                    increasing = values[i] >= values[i - 1] if non_strict else values[i] > values[i - 1]
                    current = current + 1 if increasing else 1
                    best = max(best, current)
                answers.append(str(best))
    return ''.join(answer + '\n' for answer in answers)


def generate_streak(root):
    rng = random.Random(2401)
    samples, hidden = [], []
    def add(key, category, cases, visible=False, explanation='', oracle=True):
        (samples if visible else hidden).append((key, category, streak_input(cases),
            streak_oracle(cases) if oracle else None, explanation))
    query = lambda l, r: ('QUERY', l, r)
    update = lambda i, x: ('UPDATE', i, x)
    add('sample-01', 'basic', [([1, 2, 4, 3, 5, 6, 7], [query(1, 7)]),
        ([1, 2, 2, 3, 4, 1], [query(1, 6)])], True,
        'The original streaks have lengths 4 and 3. Equality breaks a rising streak.')
    add('sample-02', 'updates', [([1, 2, 4, 3, 5, 6, 7], [query(1, 7), update(3, 3), query(1, 7),
        update(4, 4), query(1, 7), query(3, 3)])], True,
        'The first correction leaves an equality boundary. The next joins all seven days; a singleton query returns 1.')
    add('sample-03', 'range-merging', [([-3, -1, 0, -2, 2], [query(2, 5), query(4, 5), query(3, 3)])], True,
        'Only days inside the query interval count. Negative readings and singleton ranges are valid.')
    for index, values in enumerate(([7], [5, 4, 3, 2, 1], [-5, -4, -3, -2], [1, 2, 1, 2, 3, 0, 1]), 1):
        add(f'basic-{index:02}', 'basic', [(values, [query(1, len(values)), query(1, 1), query(len(values), len(values))])])
    add('equality-01', 'equality-boundaries', [([2] * 9, [query(1, 9), update(1, -1000000), query(1, 9), update(9, 1000000), query(8, 9)])])
    add('equality-02', 'equality-boundaries', [([-1000000, 0, 1000000, 1000000, -1000000], [query(1, 5), query(3, 4), query(5, 5)])])
    add('updates-01', 'updates', [([1, 2, 3, 4, 5], [update(3, -5), query(1, 5), update(3, 3), query(1, 5), update(3, 3), query(2, 4)])])
    add('updates-only', 'updates', [([1], [update(1, 2), update(1, -1)])])
    for n in (3, 5, 7, 11, 17):
        values = [rng.randrange(-5, 6) for _ in range(n)]
        operations = [query(l, r) for l in range(1, n + 1) for r in range(l, n + 1)]
        add(f'ranges-{n}', 'range-merging', [(values, operations)])
    add('multiple-01', 'multiple-testcases', [([i, i + 1, i + 2], [query(1, 3), update(2, -99), query(1, 3)]) for i in range(10)])
    add('multiple-reset', 'multiple-testcases', [([1, 2, 3], [update(2, 99), query(1, 3)]), ([1, 2, 3], [query(1, 3)])])
    for index in range(8):
        cases = []
        for _ in range(rng.randrange(1, 5)):
            n = rng.randrange(1, 40)
            values = [rng.randrange(-10, 11) for _ in range(n)]
            operations = []
            for _ in range(100):
                if rng.randrange(3) == 0:
                    operations.append(update(rng.randrange(1, n + 1), rng.randrange(-10, 11)))
                else:
                    left = rng.randrange(1, n + 1)
                    operations.append(query(left, rng.randrange(left, n + 1)))
            cases.append((values, operations))
        add(f'random-{index:02}', 'range-merging' if index % 2 else 'updates', cases)
    # Long full-range queries force a scan-based solution to visit billions of cells.
    n = 100000
    operations = [query(1, n) if i % 2 == 0 else update(50000, 50000 if i % 4 == 1 else -1000000)
        for i in range(100000)]
    add('scale-max', 'scale', [(list(range(1, n + 1)), operations)], oracle=False)
    # More than the old 1 MiB stdout ceiling, within the approved aggregate bound.
    add('scale-many-outputs', 'scale', [(list(range(10000)), [query(1, 10000)] * 90000) for _ in range(2)], oracle=False)
    save_package(root, {
        'title': 'Longest Rising Streak with Updates', 'order': 2, 'tags': ['Segment Trees', 'Arrays', 'Range Queries'],
        'limits': {'time_ms': 5000, 'stdin_bytes': 8388608, 'stdout_bytes': 2097152, 'memory_mb': 256},
        'category_weights': {'basic': 15, 'equality-boundaries': 15, 'updates': 20, 'range-merging': 25,
            'multiple-testcases': 10, 'scale': 15},
        'requirements': [{'id': 'strict-streak', 'text': 'Count only strictly increasing consecutive days.'},
            {'id': 'persistent-updates', 'text': 'Apply corrections to subsequent queries within the same test case.'},
            {'id': 'query-boundaries', 'text': 'Restrict streaks to inclusive one-based query boundaries.'},
            {'id': 'independent-cases', 'text': 'Keep test cases independent and print only query answers in order.'}],
        'reference_complexity': {'variables': {'N': 'Days in one test case', 'Q': 'Operations in that test case'},
            'time_by_phase': {'Build': 'O(N)', 'UPDATE': 'O(log N)', 'QUERY': 'O(log N)',
                'All test cases': 'O(sum(N + Q log N))'}, 'auxiliary_space': 'O(N) per test case',
            'notes': 'Reference target, not an analysis of the submitted program. Python streams operation lines/output; retained input, output buffers, and recursion count toward total program space. Hard/60 minutes and limits are provisional.'},
    }, samples, hidden)


def tree_input(n, edges, operations):
    return '\n'.join([str(n), *(f'{p} {c}' for p, c in edges), str(len(operations)),
        *(' '.join(map(str, op)) for op in operations)]) + '\n'


def tree_oracle(n, edges, operations, ignore_root=False, strict=False):
    adjacent = [[] for _ in range(n + 1)]
    for p, c in edges:
        adjacent[p].append(c); adjacent[c].append(p)
    root = 1
    answers = []
    for op in operations:
        if op[0] == 'ROOT':
            if not ignore_root:
                root = op[1]
            continue
        parent = [0] * (n + 1); parent[root] = root
        todo = [root]
        for node in todo:
            for child in adjacent[node]:
                if not parent[child]:
                    parent[child] = node; todo.append(child)
        _, u, v = op
        current = v
        while current != u and current != root:
            current = parent[current]
        answers.append('YES' if current == u and not (strict and u == v) else 'NO')
    return ''.join(answer + '\n' for answer in answers)


def generate_tree(root):
    rng = random.Random(2402)
    samples, hidden = [], []
    def add(key, category, n, edges, operations, visible=False, explanation='', oracle=True):
        (samples if visible else hidden).append((key, category, tree_input(n, edges, operations),
            tree_oracle(n, edges, operations) if oracle else None, explanation))
    query = lambda u, v: ('QUERY', u, v)
    change = lambda r: ('ROOT', r)
    edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
    add('sample-01', 'basic', 6, edges, [query(1, 5), query(3, 4), query(2, 2)], True,
        'The repaired original sample includes edge 2–5. The initial root is 1; a node is its own ancestor.')
    add('sample-02', 'root-changes', 6, edges, [change(5), query(2, 1), query(1, 5), query(3, 6), query(5, 4),
        change(6), query(3, 5), query(2, 6), query(6, 6)], True,
        'Changing the root changes ancestry directions but preserves every edge. The current root is an ancestor of every node.')
    add('sample-03', 'self-root', 1, [], [query(1, 1), change(1), query(1, 1)], True,
        'A one-node tree has no edge lines. Its only node remains its own ancestor.')
    add('basic-chain', 'basic', 8, [(i, i + 1) for i in range(1, 8)], [query(1, 8), query(4, 8), query(8, 1), query(5, 3)])
    add('self-all-roots', 'self-root', 6, edges, [op for r in range(1, 7) for op in (change(r), query(r, r), query(r, 1), query(4, 4))])
    add('root-only', 'root-changes', 6, edges, [change(6), change(1), change(5)])
    add('root-chain', 'root-changes', 12, [(i, i + 1) for i in range(1, 12)],
        [op for r in (12, 1, 6, 6, 2, 11) for op in (change(r), query(4, 9), query(9, 4), query(1, 12))])
    star = [(1, i) for i in range(2, 21)]
    add('branches-star', 'branches', 20, star, [op for r in (1, 2, 17) for op in (change(r), query(1, 3), query(2, 3), query(3, 2), query(1, r))])
    add('branches-balanced', 'branches', 31, [(i // 2, i) for i in range(2, 32)],
        [op for r in (1, 16, 31, 7) for op in (change(r), query(2, 31), query(3, 16), query(1, 7), query(7, 1))])
    shuffled = edges[:]; rng.shuffle(shuffled)
    add('shuffled-edges', 'edge-order', 6, shuffled, [change(4), query(2, 6), query(3, 5), change(1), query(1, 5)])
    # Permute labels while preserving original root 1, preventing label-order assumptions.
    labels = [1, 6, 3, 5, 2, 4]
    relabeled = [(labels[p - 1], labels[c - 1]) for p, c in edges]; rng.shuffle(relabeled)
    add('permuted-labels', 'edge-order', 6, relabeled, [query(u, v) for u in range(1, 7) for v in range(1, 7)])
    for index in range(10):
        n = rng.randrange(2, 40)
        edges = [(rng.randrange(1, v), v) for v in range(2, n + 1)]; rng.shuffle(edges)
        operations = [change(rng.randrange(1, n + 1)) if rng.randrange(4) == 0 else query(rng.randrange(1, n + 1), rng.randrange(1, n + 1)) for _ in range(150)]
        add(f'random-{index:02}', 'root-changes' if index % 2 else 'branches', n, edges, operations)
    n = 100000
    add('scale-chain', 'scale', n, [(i, i + 1) for i in range(1, n)],
        [change(1 if i % 4 == 0 else n) if i % 2 == 0 else query(25000, 75000) for i in range(100000)], oracle=False)
    add('scale-star', 'scale', n, [(1, i) for i in range(2, n + 1)],
        [change(2 + i % (n - 1)) if i % 2 == 0 else query(1, n) for i in range(100000)], oracle=False)
    save_package(root, {
        'title': 'G-Tree: Ancestors with a Changing Root', 'order': 3, 'tags': ['Trees', 'Binary Lifting', 'Queries'],
        'limits': {'time_ms': 5000, 'stdin_bytes': 8388608, 'stdout_bytes': 1048576, 'memory_mb': 256},
        'category_weights': {'basic': 15, 'self-root': 15, 'root-changes': 25, 'branches': 20, 'edge-order': 10, 'scale': 15},
        'requirements': [{'id': 'ancestor-path', 'text': 'Determine ancestry using the path from the current root.'},
            {'id': 'self-ancestry', 'text': 'Treat each node as its own ancestor, including singleton trees.'},
            {'id': 'logical-root', 'text': 'Persist logical root changes without changing the given edges.'},
            {'id': 'query-output', 'text': 'Accept arbitrary initial edge order and print only ordered query answers.'}],
        'reference_complexity': {'variables': {'N': 'Tree nodes', 'Q': 'Operations'},
            'time_by_phase': {'Preprocessing': 'O(N log N)', 'ROOT': 'O(1)', 'QUERY': 'O(log N)',
                'Whole input': 'O(N log N + Q log N)'}, 'auxiliary_space': 'O(N log N)',
            'notes': 'Reference uses iterative traversal, one original-root index, and binary lifting. Retained input/output and recursion count toward total program space. These are reference targets, not inferred bounds for submitted code. Hard/60 minutes and limits are provisional.'},
    }, samples, hidden)
