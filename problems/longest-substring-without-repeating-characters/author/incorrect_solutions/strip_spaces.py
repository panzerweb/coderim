import json
import sys

# YOUR SOLUTION: edit this function body.
def lengthOfLongestSubstring(s):
    s=s.strip()
    last = [-1] * 128
    left = best = 0
    for right, character in enumerate(s):
        code = ord(character)
        left = max(left, last[code] + 1)
        last[code] = right
        best = max(best, right - left + 1)
    return best

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    s=stream.readline()
    if s.endswith('\n'):
        s=s[:-1]
        if s.endswith('\r'): s=s[:-1]
    result=lengthOfLongestSubstring(s)
    output.write(json.dumps(result)+'\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
