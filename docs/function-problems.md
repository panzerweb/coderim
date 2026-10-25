# Function-based problems

Seven LeetCode-derived packages are available in the seventeen-problem catalog (six Easy, five Medium, six Hard). LeetCode difficulty labels are retained; suggested durations are provisional: 20 minutes for the two Easy additions, 40 for the two Medium additions, and 60 for the three Hard additions. Each uses a 2-second case limit and a 256 MB memory target that remains unenforced by the local executor.

## Editing a solution

Select a language, then implement the function in the **YOUR SOLUTION** section. Return the result, or mutate the array as the task specifies. Keep the **PROVIDED INPUT/OUTPUT** section intact: it parses stdin, calls your function, captures any array changes, and prints valid JSON. You do not need to add a call to your function or write the output yourself. Both sections remain editable; resetting a starter still requires confirmation before replacing a draft.

| Problem | Function | Result | Cases |
| --- | --- | --- | ---: |
| [Text Justification (68)](https://leetcode.com/problems/text-justification/) | `fullJustify(words, maxWidth)` | Ordered string array | 3 samples + 40 hidden |
| [Valid Number (65)](https://leetcode.com/problems/valid-number/) | `isNumber(s)` | Boolean | 3 samples + 64 hidden |
| [Substring Concatenation (30)](https://leetcode.com/problems/substring-with-concatenation-of-all-words/) | `findSubstring(s, words)` | Integer array, any order | 3 samples + 40 hidden |
| [Plus One (66)](https://leetcode.com/problems/plus-one/) | `plusOne(digits)` | Ordered digit array | 3 samples + 32 hidden |
| [Remove Duplicates (26)](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | `removeDuplicates(nums)` | k plus mutated prefix | 3 samples + 32 hidden |
| [Next Permutation (31)](https://leetcode.com/problems/next-permutation/) | `nextPermutation(nums)` | Mutated array; no return value | 3 samples + 32 hidden |
| [Longest Substring (3)](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | `lengthOfLongestSubstring(s)` | Integer length | 3 samples + 32 hidden |

Python and JavaScript use these function names directly. C++ uses vectors by reference for mutable arrays and returns vectors, bool, int, or void as specified. Java uses static methods inside Main: the older Hard array results use Lists, Plus One uses int[], count/length functions return int, and Next Permutation is void. Correct alternatives to the private reference algorithms are allowed.

The default false, zero, empty-array, or no-op bodies are placeholders, not completed solutions. Run Code in a team workspace (Run samples in practice mode) checks samples. Custom input shows output without a correctness score. Record Submission confirms and saves the entire program, including the provided driver, then checks the full official suite.

## Input and output

Every input is one test case. Inputs use these stdin contracts rather than LeetCode's `words = [...]` notation:

- **Text:** read `N maxWidth`, then N whitespace-separated words. Words contain printable non-whitespace ASCII and have length 1-20; N is 1-300, width is 1-100, and every word fits.
- **Number:** read one line s, without quotes, with length 1-20. Its alphabet is English letters, digits, `+`, `-`, and `.`. Remove only the line ending. Syntax, rather than floating-point magnitude, determines validity.
- **Substring:** read s, M, then M whitespace-separated words. The string length is 1-10,000; M is 1-5,000; all words have the same length, 1-30. Strings contain lowercase English letters. Word lists whose concatenation is longer than s are valid inputs with no matches.
- **Plus One:** read N and N digits, with length 1-100. Leading zeros are excluded except [0]. Return the incremented digit array; do not rely on fixed-width numeric conversion for 100-digit inputs.
- **Remove Duplicates:** read N and N sorted integers. N is 1-30,000, values are -100 through 100. Return k and mutate the caller's first k entries. The driver prints `{"k":2,"nums":[1,2]}` for input `[1,1,2]`; it ignores all tail values. A new local binding does not update the caller. Invalid k values (including negative, noninteger, or unavailable prefixes) produce null and are Wrong Answer.
- **Next Permutation:** read N and N integers, with N 1-100 and values 0-100. Mutate the caller's array; returning a different array alone is insufficient. Its final order is significant, and a maximal permutation wraps to ascending order.
- **Longest Substring:** read one raw ASCII line, including all spaces, with length 0-100,000. Preserve case and punctuation; strip only the LF/CRLF terminator. Empty line/empty EOF returns 0. For example, ` a ` has result 2. This task is separate from the numeric-array Longest Unique Segment problem.

The in-place tasks' drivers inspect the original caller-held array. Constant auxiliary space is assessed manually under Technical Quality. Tests observe results rather than proving allocation behavior, and no new automatic complexity or acceptance rule is introduced. Reference targets exclude stored input and serialized output; include them when reviewing total space.

For example, substring sample 1 is entered as:

```text
barfoothefoobarman
2
foo
bar
```

The returned indices `[0, 9]` and `[9, 0]` are equally valid. Every matching index must appear exactly once. No matches means `[]`, not missing output. Duplicate words in the input retain their required counts, and matching substrings can overlap.

The driver prints exactly one JSON result. Indentation and whitespace outside JSON strings do not matter. For Text Justification, every decoded character inside a string matters, including right padding: `"shall be        "` has width 16, with eight trailing spaces. Line order must be preserved. The supplied serializers also escape quotes and backslashes in words correctly.

Valid Number returns JSON true or false; Longest Substring returns a strict JSON integer. Booleans do not count as integer zero/one, and floating-point JSON counts or indices are rejected. Remove Duplicates requires exactly k and nums, with an integer k equal to the prefix length and integer array entries; object field order is ignored, but duplicate or extra fields are rejected. Debug text, malformed JSON, and incorrect shapes are Wrong Answer. The original ten problems retain their text-output checking rules and starters.

## Author verification and rollout

```powershell
.\.venv\Scripts\python.exe tools/validate_problems.py
.\.venv\Scripts\python.exe tools/verify_function_problems.py
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
```

The verification tool checks saved outputs, detects deliberately faulty programs, and compiles/runs private references and untouched starters through every available language runner. Missing toolchains are reported as skips. Private authoring timing records are written to `.runtime/content-verification/function-results.json`; they are not participant efficiency scores.

Regenerate all seven function packages with `python tools/leetcode_problem_content.py`, only the four array/string additions with `python tools/array_function_content.py`, or run a package's author/generate_tests.py. Existing package generation remains byte-for-byte reproducible. Fixed seeds and independent oracles reproduce saved cases, including exact-integer addition, sorted unique values, permutation enumeration/ranking, and brute-force small substrings. Keep all author files private. Tests remain within the existing 100-case/20 MiB package bounds and default 1 MiB input/output limits.

Restart the backend to discover the packages, then create and publish a new contest to select them. Existing contests keep their pinned statements, starters, tests, and checker configuration. Completed history and reviews retain their original scores; no database migration is required. Quality assessment weights remain 50/20/15/15, and acceptance still requires every official test to pass.
