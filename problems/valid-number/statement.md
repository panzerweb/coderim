# Valid Number

Adapted from [LeetCode 65: Valid Number](https://leetcode.com/problems/valid-number/) for Code Relay.

Decide whether the entire string follows the number grammar. An integer has an optional + or - followed by one or more ASCII digits. A decimal has an optional sign followed by digits and a dot, digits-dot-digits, or a dot and digits. An integer or decimal may be followed by one exponent: e or E, then an optionally signed integer. Syntax determines validity, independently of the numeric magnitude.

## Write the function

Implement `isNumber(s)` in the starter. Return the result; the provided code reads input, calls your function, and prints JSON. Keep the provided input/output section intact. The entire program remains editable.

Python and JavaScript use the function name above; C++ uses `vector<string>` / `vector<int>` for array results, and Java supplies static methods inside `Main` with `List<String>` / `List<Integer>` results. Boolean results use the language's boolean type.

## Input specification

Read one line s without surrounding quotes. There is one test case per input. Bounds: 1 <= s.length <= 20. Characters are English letters, ASCII digits 0-9, +, -, or a dot. Remove the line ending only; do not trim or accept extra whitespace.

## Output specification

Return a boolean. The supplied driver prints JSON true or false (lowercase). Numeric values, strings, and extra output are not accepted as booleans.

## Practice information

Hard (LeetCode classification). Suggested duration: 60 minutes, informational and provisional. Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor. Alternative correct algorithms are allowed.
