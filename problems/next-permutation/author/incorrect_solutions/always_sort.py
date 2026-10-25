import json
import sys

# YOUR SOLUTION: edit this function body.
def nextPermutation(nums):
    nums.sort()

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    data=iter(stream.read().split())
    n=int(next(data))
    nums=[int(next(data)) for _ in range(n)]
    nextPermutation(nums)
    result=nums
    output.write(json.dumps(result)+'\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
