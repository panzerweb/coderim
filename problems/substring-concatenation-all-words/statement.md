# Substring with Concatenation of All Words

Adapted from [LeetCode 30: Substring with Concatenation of All Words](https://leetcode.com/problems/substring-with-concatenation-of-all-words/) for Code Relay.

Find all positions where a consecutive substring consists of exactly the supplied words concatenated in some order. All words have the same length. Repeated words must occur with their supplied multiplicity. Matches may overlap, and positions need not align to the beginning of s.

## Write the function

Implement `findSubstring(s, words)` in the starter. Return the result; the provided code reads input, calls your function, and prints JSON. Keep the provided input/output section intact. The entire program remains editable.

Python and JavaScript use the function name above; C++ uses `vector<string>` / `vector<int>` for array results, and Java supplies static methods inside `Main` with `List<String>` / `List<Integer>` results. Boolean results use the language's boolean type.

## Input specification

Read s, then M, then M whitespace-separated words. There is one test case per input. Bounds: 1 <= s.length <= 10,000; 1 <= M <= 5,000; 1 <= word length <= 30. All words have the same length and all characters are lowercase English letters. A total word length greater than s.length is valid input and has no matches.

## Output specification

Return an array of zero-based starting indices, in any order. The supplied driver prints a JSON integer array. Return [] when there are no matches. Include every matching position exactly once; duplicate indices are incorrect.

## Practice information

Hard (LeetCode classification). Suggested duration: 60 minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Alternative correct algorithms are allowed.
