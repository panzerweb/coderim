# Longest Rising Streak with Updates

A weather station records one temperature for each day. Readings may be corrected later. Process corrections and answer questions about rising streaks in selected date ranges.

A **rising streak** contains consecutive days whose temperatures are strictly increasing. Equal temperatures break a streak. Days cannot be skipped, reordered, or deleted.

## Operations

- `UPDATE I X`: replace the temperature on day `I` with `X`. The correction affects all subsequent queries in this test case.
- `QUERY L R`: print the length of the longest rising streak entirely inside the inclusive range from day `L` to day `R`.

All indices are **one-based**. A single day forms a streak of length 1. Test cases are independent.

## Input format

The first line contains `T`, the number of test cases. For each test case:

1. Read `N Q`, the number of days and operations.
2. Read `N` integer temperatures, separated by whitespace.
3. Read exactly `Q` operations, one per line, in either format above.

## Output format

For each `QUERY`, print one integer on its own line. Print nothing for `UPDATE` and do not add case headings or blank separators. A test case containing only updates produces no output.

## Constraints

| Parameter | Constraint |
| --- | --- |
| Test cases | `1 ≤ T ≤ 10` |
| Days / operations per test case | `1 ≤ N,Q ≤ 100,000` |
| Total size in one input | Sum of `N + Q` across test cases ≤ `200,000` |
| Initial or updated temperature | `−1,000,000 ≤ X ≤ 1,000,000` |
| Update position | `1 ≤ I ≤ N` |
| Query range | `1 ≤ L ≤ R ≤ N` |
| Execution time | 5 seconds per official input, provisional |
| Memory target | 256 MB; unenforced by the local runner |
| Suggested practice duration | 60 minutes, provisional Hard level for DSA students |

Each official input may contain multiple test cases; the app counts that entire input as one judged case. Executable samples and explanations follow below.
