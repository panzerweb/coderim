import json
import sys

# YOUR SOLUTION: edit this function body.
def plusOne(digits):
    digits[-1]+=1
    return digits

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    data=iter(stream.read().split())
    n=int(next(data))
    nums=[int(next(data)) for _ in range(n)]
    result=plusOne(nums)
    output.write(json.dumps(result)+'\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
