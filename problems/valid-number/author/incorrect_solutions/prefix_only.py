import json
import sys

# YOUR SOLUTION: edit this function body.
def isNumber(s):
    import re
    return re.match(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?',s) is not None

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    s=stream.readline().rstrip('\r\n')
    result=isNumber(s)
    output.write(json.dumps(result) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
