import json
import sys

# YOUR SOLUTION: edit this function body.
def fullJustify(words, maxWidth):
    # TODO: return the result array.
    return []

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    data=iter(stream.read().split())
    n,maxWidth=int(next(data)),int(next(data))
    words=[next(data) for _ in range(n)]
    result=fullJustify(words,maxWidth)
    output.write(json.dumps(result) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
