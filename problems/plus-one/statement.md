# Plus One

Adapted from [LeetCode 66: Plus One](https://leetcode.com/problems/plus-one/) for Code Relay.

An integer is represented by its decimal digits, most significant first. Increment it by one and return the resulting digit array. You may update the supplied digits or return a new array. The number may be too large for a fixed-width numeric type.

## Write the function

Implement `plusOne(digits)` in the starter. Return the result; the driver reads input, calls your function, and prints JSON. Keep the provided input/output section intact; the whole program remains editable.

Python and JavaScript use the supplied function. C++ uses vectors by reference for array inputs. Java supplies static methods inside Main with int[] array inputs/results, integer counts, or void mutation methods.

## Input specification

Read N followed by N digits. Bounds: 1 <= N <= 100; digits are 0-9. There are no leading zeros, except that [0] is a valid representation of zero. There is one test case per input.

## Output specification

Return an ordered digit array. The provided driver prints a JSON integer array. For example, [9] becomes [1,0]. JSON formatting outside strings and object field order do not matter. Do not print debug text or prompts.

## Practice information

Easy (LeetCode classification). Suggested duration: 20 minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Constant-space claims are assessed from source under Technical Quality; output tests are evidence of behavior, not proof of allocations. Correct alternative algorithms are allowed.
