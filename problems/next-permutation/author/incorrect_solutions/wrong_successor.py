import json
import sys

# YOUR SOLUTION: edit this function body.
def nextPermutation(nums):
    pivot = len(nums) - 2
    while pivot >= 0 and nums[pivot] >= nums[pivot + 1]:
        pivot -= 1
    if pivot >= 0:
        successor = pivot + 1
        while nums[successor] <= nums[pivot]:
            successor += 1
        nums[pivot], nums[successor] = nums[successor], nums[pivot]
    left, right = pivot + 1, len(nums) - 1
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left += 1
        right -= 1

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
