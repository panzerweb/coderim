import json
import sys

# YOUR SOLUTION: edit this function body.
def findSubstring(s, words):
    # TODO: return the result array.
    return []

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    data=iter(stream.read().split())
    s=next(data)
    words=[next(data) for _ in range(int(next(data)))]
    result=findSubstring(s,words)
    output.write(json.dumps(result) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
