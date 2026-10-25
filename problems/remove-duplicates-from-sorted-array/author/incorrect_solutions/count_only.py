import json
import sys

# YOUR SOLUTION: edit this function body.
def removeDuplicates(nums):
    return len(set(nums))

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    data=iter(stream.read().split())
    n=int(next(data))
    nums=[int(next(data)) for _ in range(n)]
    k=removeDuplicates(nums)
    result={'k':k,'nums':nums[:k]} if type(k) is int and 0<=k<=n and k<=len(nums) else None
    output.write(json.dumps(result)+'\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
