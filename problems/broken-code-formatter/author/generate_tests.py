"""Reproducibly rebuild official content. Run from any working directory."""
import json
import random
from pathlib import Path
from reference import validate

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = [
    {'id': 'matching', 'text': 'Opening brackets have matching closing brackets of the correct type outside strings.'},
    {'id': 'nesting', 'text': 'Brackets outside strings are properly nested.'},
    {'id': 'closed-quotes', 'text': 'All quoted strings are properly closed; brackets inside strings are ignored.'},
    {'id': 'complete-escapes', 'text': 'Within strings a backslash escapes exactly the next character; no escape is dangling.'},
]
MAP = {
    'basic': ['matching', 'nesting'], 'nesting': ['matching', 'nesting'],
    'quotes': ['matching', 'closed-quotes'], 'escapes': ['closed-quotes', 'complete-escapes'],
    'unclosed': [r['id'] for r in REQUIREMENTS], 'large': [r['id'] for r in REQUIREMENTS],
}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def main():
    save(ROOT / 'problem.json', {
        'schema_version': 1, 'id': ROOT.name, 'version': 1, 'title': 'The Broken Code Formatter',
        'difficulty': 'Hard', 'tags': ['Strings', 'Stacks', 'Parsing'], 'status': 'published',
        'order': 1, 'suggested_duration_minutes': 60, 'submission_mode': 'stdin_stdout',
        'statement_file': 'statement.md', 'samples_file': 'samples.json', 'tests_manifest': 'tests/manifest.json',
        'limits': {'time_ms': 2000, 'memory_mb': 256, 'source_bytes': 65536, 'stdin_bytes': 1048576,
            'stdout_bytes': 1048576, 'stderr_bytes': 65536},
        'checker': {'type': 'text', 'normalize_line_endings': True, 'trim_trailing_whitespace_per_line': True,
            'ignore_final_newline': True},
        'starters': {'python': 'starters/main.py', 'javascript': 'starters/main.js', 'cpp': 'starters/main.cpp', 'java': 'starters/Main.java'},
        'category_weights': {'basic': 15, 'nesting': 20, 'quotes': 20, 'escapes': 20, 'unclosed': 15, 'large': 10},
        'requirements': REQUIREMENTS,
        'reference_complexity': {'variables': {'L': 'Characters in the source-code line'},
            'time_by_phase': {'Validation': 'O(L)'}, 'auxiliary_space': 'O(L)',
            'notes': 'The reference visits each character once and stores unmatched opening brackets. Include the stored source line, recursion, and input/output buffers when reviewing total program space. This is a reference target, not an inferred property of submitted code.'},
        'rubric': {'version': 1, 'weights': {'correctness': 50, 'requirements': 20, 'readability': 15, 'technical': 15},
            'readability': ['Naming', 'Clarity', 'Useful explanations and comments', 'Ease of handoff'],
            'technical': ['Structure', 'State management', 'Algorithm and data structures', 'Avoiding unnecessary complexity']},
    })
    raw_samples = [
        ('function test() { return [a, (b + c)]; }', True, 'nesting', 'All brackets are properly matched and nested.'),
        ('print("This [ is not a bracket!")', True, 'quotes', 'The unmatched square bracket is inside a double-quoted string.'),
        ('function test() { return [(a + b]); }', False, 'nesting', 'The closing square bracket does not match the innermost opening parenthesis.'),
        (r'print("She said \"Hello!\"")', True, 'escapes', 'Escaped quotation marks do not close the string.'),
        ('message = "Hello World', False, 'unclosed', 'The double-quoted string is not closed.'),
        ('''log('User said "Hello [World]"')''', True, 'quotes', 'Opposite quotes and brackets are ordinary characters inside this single-quoted string.'),
    ]
    samples = []
    for index, (source, expected, category, explanation) in enumerate(raw_samples, 1):
        assert validate(source) == expected, f'Sample {index} is inconsistent'
        samples.append({'id': f'sample-{index:02}', 'input': source + '\n',
            'expected_output': ('VALID' if expected else 'INVALID') + '\n',
            'category': category, 'requirements': MAP[category], 'explanation': explanation})
    save(ROOT / 'samples.json', samples)
    groups = {
        'basic': ['a', ' ', '()', '[]', '{}', ')', '[', '(]', '()[]{}', '\\', 'a [ b ]'],
        'nesting': ['([{}])', '([{)]}', '{[()]()}[{}]', '(((())))', '([)]', '}}', '(a[b{c}])'],
        'quotes': ['"[({"', "']})'", '""', "''", '''"a'b"''', ''''a"b' ''', '"["()', r'\"closed"', '`[ ]`', '//(', "' ] "] ,
        'escapes': [r'"\""', r'"\\"', r'"\\\""', r'"\\\\"', r"'\''", '"a\\', r'"a\"', r"'\]'"] ,
        'unclosed': ['(', '[(', '"', "'", '("x")]', '"x\\', "'x\\", '(["abc"]', '"abc\\\\'],
        'large': ['(' * 50000 + ')' * 50000, '[' * 50000 + ']' * 49999 + ')',
            '"' + '[' * 99998 + '"', 'a' * 100000, '"' + '\\' * 99999],
    }
    rng = random.Random(3003)
    groups['nesting'] += [''.join(rng.choice('()[]{}abc') for _ in range(40)) for _ in range(4)]
    groups['escapes'] += [''.join(rng.choice('()[]{}\'"\\abc ') for _ in range(60)) for _ in range(4)]
    manifest = []
    for category, sources in groups.items():
        for index, source in enumerate(sources, 1):
            assert 1 <= len(source) <= 100000 and source.isascii() and '\n' not in source
            key = f'{category}-{index:02}'
            (ROOT / 'tests').mkdir(exist_ok=True)
            (ROOT / 'tests' / (key + '.in')).write_text(source + '\n', encoding='utf-8', newline='\n')
            (ROOT / 'tests' / (key + '.out')).write_text(('VALID' if validate(source) else 'INVALID') + '\n', encoding='utf-8', newline='\n')
            manifest.append({'id': key, 'category': category, 'requirements': MAP[category],
                'input_file': f'tests/{key}.in', 'output_file': f'tests/{key}.out'})
    save(ROOT / 'tests/manifest.json', {'cases': manifest})
    print(f'Generated {len(samples)} samples and {len(manifest)} hidden cases (seed 3003).')


if __name__ == '__main__':
    main()
