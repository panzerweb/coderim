import json
import sys

# YOUR SOLUTION: edit this function body.
def lengthOfLongestSubstring(s):
    return len(set(s))

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
