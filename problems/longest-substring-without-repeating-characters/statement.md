# Longest Substring Without Repeating Characters

Adapted from [LeetCode 3: Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) for Code Relay.

Find the length of the longest contiguous substring containing no repeated characters. Uppercase and lowercase letters are distinct; spaces and punctuation are ordinary characters. Do not strip spaces from the input. An empty string has answer zero.

## Write the function

Implement `lengthOfLongestSubstring(s)` in the starter. Return the result; the driver reads input, calls your function, and prints JSON. Keep the provided input/output section intact; the whole program remains editable.

Python and JavaScript use the supplied function. C++ uses vectors by reference for array inputs. Java supplies static methods inside Main with int[] array inputs/results, integer counts, or void mutation methods.

## Input specification

Read one raw line without surrounding quotes. Bounds: 0 <= length <= 100,000. Characters are printable ASCII codes 32-126, including spaces. Remove only the physical LF/CRLF line ending; preserve leading and trailing spaces. An empty line or EOF with no characters represents the empty string. There is one test case per input.

## Output specification

Return an integer length. The provided driver prints one JSON integer. For empty input the result is 0; booleans, strings, and floating-point JSON values are not integer results. JSON formatting outside strings and object field order do not matter. Do not print debug text or prompts.

## Practice information

Medium (LeetCode classification). Suggested duration: 40 minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Constant-space claims are assessed from source under Technical Quality; output tests are evidence of behavior, not proof of allocations. Correct alternative algorithms are allowed.
