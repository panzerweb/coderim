import json
import sys

# YOUR SOLUTION: edit this function body.
def isNumber(s):
    i, n = 0, len(s)
    if i < n and s[i] in '+-':
        i += 1
    digits = 0
    while i < n and '0' <= s[i] <= '9':
        digits += 1
        i += 1
    if i < n and s[i] == '.':
        i += 1
        while i < n and '0' <= s[i] <= '9':
            digits += 1
            i += 1
    if not digits:
        return False
    if i < n and s[i] in 'eE':
        i += 1
        if i < n and s[i] in '+-':
            i += 1
        exponent_start = i
        while i < n and '0' <= s[i] <= '9':
            i += 1
        if i == exponent_start:
            return False
    return i == n

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    s=stream.readline().rstrip('\r\n')
    result=isNumber(s)
    output.write(json.dumps(result) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
