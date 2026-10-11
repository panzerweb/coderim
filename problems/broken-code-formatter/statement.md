# The Broken Code Formatter

A team is building a lightweight formatter that checks whether brackets are properly balanced. Given one line of source code, validate brackets while ignoring those inside quoted strings.

## Your task

Print `VALID` exactly when all four conditions hold:

1. Every opening bracket outside a string has a matching closing bracket of the correct type: `()`, `[]`, or `{}`.
2. Brackets outside strings are properly nested.
3. All single-quoted (`'`) and double-quoted (`"`) strings are closed.
4. No backslash escape is left dangling at the end of a quoted string.

Otherwise print `INVALID`.

Only the same type of quote closes an active string. Within a string, a backslash (`\`) escapes **exactly the following character**, including another backslash or a quote. Brackets and the opposite quote type inside a string are ordinary characters.

Outside strings, a backslash has no escaping effect. Comments and backticks have no special syntax: their brackets and quotes are processed by these same rules.

## Input format

Exactly one line of 1–100,000 ASCII characters, excluding its optional transport line ending. Input is case-sensitive. Preserve spaces. No multiline strings or comment syntax are supported.

## Output format

Print one line containing `VALID` or `INVALID`. Do not print prompts or debug messages.

## Constraints

| Parameter | Constraint |
| --- | --- |
| Source-code length | 1–100,000 characters |
| Input lines | Exactly one |
| Execution time | 2 seconds per case |
| Memory target | 256 MB; unenforced by the local runner |
| Suggested practice duration | 60 minutes; informational |

## Samples

The six executable samples and their explanations are displayed below from the authoritative sample file.
