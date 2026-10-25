import json
import sys

# YOUR SOLUTION: edit this function body.
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    s=stream.readline().rstrip('\r\n')
    result=isNumber(s)
    output.write(json.dumps(result) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
