# Text Justification

Adapted from [LeetCode 68: Text Justification](https://leetcode.com/problems/text-justification/) for Code Relay.

Arrange the words into fixed-width lines. Fill each line greedily without changing word order. On ordinary lines distribute all available spaces as evenly as possible between words; leftmost gaps receive any remainder. Use single spaces between words on the final line, then pad its right edge. A line with one word is also padded on the right.

## Write the function

Implement `fullJustify(words, maxWidth)` in the starter. Return the result; the provided code reads input, calls your function, and prints JSON. Keep the provided input/output section intact. The entire program remains editable.

Python and JavaScript use the function name above; C++ uses `vector<string>` / `vector<int>` for array results, and Java supplies static methods inside `Main` with `List<String>` / `List<Integer>` results. Boolean results use the language's boolean type.

## Input specification

Read N maxWidth, then N whitespace-separated words. There is one test case per input. Bounds: 1 <= N <= 300; 1 <= maxWidth <= 100; 1 <= word length <= 20; each word fits maxWidth. Words contain printable ASCII characters (codes 33-126), excluding whitespace.

## Output specification

Return an ordered array of strings. The supplied driver prints it as a JSON array. Every decoded string must contain exactly maxWidth characters, including trailing spaces. JSON formatting outside strings is ignored; characters inside strings, including spaces, must match exactly.

## Practice information

Hard (LeetCode classification). Suggested duration: 60 minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Alternative correct algorithms are allowed.
