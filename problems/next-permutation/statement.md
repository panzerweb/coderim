# Next Permutation

Adapted from [LeetCode 31: Next Permutation](https://leetcode.com/problems/next-permutation/) for Code Relay.

Rearrange the array into the next lexicographically greater permutation. If it is already maximal, rearrange it into ascending order. Equal values are allowed. Modify the supplied array in place and use only constant auxiliary memory.

## Write the function

Implement `nextPermutation(nums)` in the starter. Modify nums and return no value. The driver ignores your return value and prints the original caller-held array after invocation. Keep the provided input/output section intact; the whole program remains editable.

Python and JavaScript use the supplied function. C++ uses vectors by reference for array inputs. Java supplies static methods inside Main with int[] array inputs/results, integer counts, or void mutation methods.

## Input specification

Read N followed by N integers. Bounds: 1 <= N <= 100; 0 <= nums[i] <= 100. There is one test case per input.

## Output specification

Return no value. The driver ignores return values and prints the caller-held array as an ordered JSON integer array. Returning a different array without mutating the supplied one does not solve this task. JSON formatting outside strings and object field order do not matter. Do not print debug text or prompts.

## Practice information

Medium (LeetCode classification). Suggested duration: 40 minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Constant-space claims are assessed from source under Technical Quality; output tests are evidence of behavior, not proof of allocations. Correct alternative algorithms are allowed.
