# Remove Duplicates from Sorted Array

Adapted from [LeetCode 26: Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) for Code Relay.

Compact the unique values of a non-decreasing array into its beginning and return their count k. The first k entries must contain those values in order; everything after them is ignored. Modify the supplied array rather than merely returning or locally rebinding a different array. Use constant auxiliary space.

## Write the function

Implement `removeDuplicates(nums)` in the starter. Return k and modify nums. The driver reads input, calls your function, and prints k with the modified prefix. Keep the provided input/output section intact; the whole program remains editable.

Python and JavaScript use the supplied function. C++ uses vectors by reference for array inputs. Java supplies static methods inside Main with int[] array inputs/results, integer counts, or void mutation methods.

## Input specification

Read N followed by N non-decreasing integers. Bounds: 1 <= N <= 30,000; -100 <= nums[i] <= 100. There is one test case per input.

## Output specification

Return only integer k. After calling your function, the driver prints {"k":k,"nums":prefix}, where prefix contains the first k entries of the caller-held array. Tail contents are ignored. Invalid k values produce null and are judged Wrong Answer. Example: [1,1,2] produces {"k":2,"nums":[1,2]}. JSON formatting outside strings and object field order do not matter. Do not print debug text or prompts.

## Practice information

Easy (LeetCode classification). Suggested duration: 20 minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Constant-space claims are assessed from source under Technical Quality; output tests are evidence of behavior, not proof of allocations. Correct alternative algorithms are allowed.
