"""Create an unpublished echo example demonstrating the generic package contract."""
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def scaffold(slug, problem_root=None):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Use a lowercase hyphenated slug')
    root = Path(problem_root or ROOT / 'problems') / slug
    root.mkdir(parents=True, exist_ok=False)
    (root / 'tests').mkdir()
    (root / 'author' / 'incorrect_solutions').mkdir(parents=True)
    metadata = {'schema_version': 1, 'id': slug, 'version': 1, 'title': slug.replace('-', ' ').title(),
        'difficulty': 'Easy', 'tags': ['example'], 'status': 'draft', 'category_weights': {'behavior': 100},
        'requirements': [{'id': 'echo', 'text': 'Print the input line unchanged.'}]}
    samples = [{'id': 'sample-01', 'input': 'hello\n', 'expected_output': 'hello\n',
        'explanation': 'Preserve the input.', 'category': 'behavior', 'requirements': ['echo']}]
    manifest = {'cases': [{'id': 'hidden-01', 'input_file': 'tests/spaces.in', 'output_file': 'tests/spaces.out',
        'category': 'behavior', 'requirements': ['echo']}]}
    for name, data in [('problem.json', metadata), ('samples.json', samples), ('tests/manifest.json', manifest)]:
        (root / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    for name in ('spaces.in', 'spaces.out'):
        (root / 'tests' / name).write_text('  preserved spaces  \n', encoding='utf-8')
    (root / 'statement.md').write_text('# Echo example\n\nRead one line and print it unchanged. Replace this example with your challenge.\n', encoding='utf-8')
    (root / 'author' / 'reference.py').write_text('import sys\nsys.stdout.write(sys.stdin.readline())\n', encoding='utf-8')
    (root / 'author' / 'editorial.md').write_text('Replace the echo example and verify all outputs before publishing.\n', encoding='utf-8')
    return root


if __name__ == '__main__':
    try:
        print(scaffold(sys.argv[1]))
    except (IndexError, ValueError, FileExistsError) as error:
        print(f'Scaffold failed: {error}')
        sys.exit(1)
