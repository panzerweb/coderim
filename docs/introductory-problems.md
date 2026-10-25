# Easy and Medium practice problems

The seven introductory version-1 packages provide four Easy and three Medium challenges. The current seventeen-problem catalog also includes six Hard challenges and four more Easy/Medium LeetCode function tasks. Add Two Numbers is a five-minute application test; the other Easy tasks suggest 20 minutes and Medium tasks suggest 40. These estimates are informational and provisional for university DSA students.

| Package | Key behavior | Reference target |
| --- | --- | --- |
| `add-two-numbers` | Two signed integers, one sum; no prompts | O(1) time/auxiliary space |
| `longest-rising-streak` | T independent cases; strict consecutive increases, equality breaks a streak | O(sum N) time; O(1) auxiliary space when streaming |
| `most-frequent-reading` | Print value and count; smallest numeric value wins ties | Expected O(N) time; O(D) auxiliary space |
| `palindrome-check` | ASCII letters/digits only, ignore case; empty normalized text is YES | O(L) time; O(1) extra space beyond stored line |
| `g-tree-ancestor-query` | Fixed root 1, arbitrary edge order, self-ancestry | O(N) preprocessing, O(1) per query; O(N) auxiliary space |
| `shortest-grid-route` | Four directions, walls, unit-cost moves; unreachable is -1 | O(RC) time/auxiliary space |
| `longest-unique-segment` | Longest contiguous segment with no repeated values | Expected O(N) time; O(D) auxiliary space |

N is the number of values or tree nodes; D is distinct values; L is text length; R/C are grid dimensions. Expected map bounds assume hash-table operations with expected constant cost. They are not worst-case guarantees. Stored input, output collections, and stacks count toward total program space. Reference targets never replace the organizer's assessment of a submission.

Each package has three samples, twenty hidden cases, four behavioral requirements, and categories weighted 20% basic, 20% boundaries, 40% specific behavior, and 20% scale/numeric limits. Assessment remains 50/20/15/15; every official case must pass for acceptance. Maximum case execution time is 2 seconds and the 256 MB local memory target remains unenforced. The fixed-root tree allows 4 MiB stdin; other new packages use the default 1 MiB stdin/stdout limits.

## Using the testing problem

1. Create a contest and select **Add Two Numbers** before publishing.
2. Register a team, start the contest, and join using a separate browser profile.
3. Select Python and enter the solution below.
4. Click **Run Code** with Custom input unchecked to run the samples, then confirm **Record Submission**. Expect all 23 official cases to pass.
5. Open the organizer console and inspect the team's saved source and results. Save code-quality and complexity feedback; the team can read it in History.

This solution accepts operands separated by any whitespace:

```python
import sys
a, b = map(int, sys.stdin.read().split())
print(a + b)
```

Practice runs remain outside official history. Published contests retain their original pinned selections even after more packages are added or repository content changes. Restart the backend after a repository update, then publish a new contest to use the new problems.

## Author verification

From the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe tools/validate_problems.py
.\.venv\Scripts\python.exe tools/verify_practice_problems.py
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_practice_problems.py -v
```

The verification tool checks Python outputs, detects deliberately faulty solutions, and runs references plus input starters through the actual judge in every available language. Missing toolchains are reported as skips. Timing records are saved privately in `.runtime/content-verification/practice-results.json`; these author checks do not add benchmark scores to submissions.

Reproduce all seven packages with `python tools/practice_problem_content.py`, or run a package's `author/generate_tests.py`. Small cases use independent oracles and fixed seeds; maximum-size cases use independently checkable patterns. Reference programs, faulty solutions, editorials, and generation scripts remain private under `author/`. Correct alternative algorithms are allowed.
