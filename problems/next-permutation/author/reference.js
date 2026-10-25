// YOUR SOLUTION: edit this function body.
function nextPermutation(nums) {
  let pivot=nums.length-2;
  while (pivot>=0 && nums[pivot]>=nums[pivot+1]) pivot--;
  if (pivot>=0) {
    let successor=nums.length-1;
    while (nums[successor]<=nums[pivot]) successor--;
    [nums[pivot],nums[successor]]=[nums[successor],nums[pivot]];
  }
  let left=pivot+1,right=nums.length-1;
  while (left<right) { [nums[left],nums[right]]=[nums[right],nums[left]]; left++; right--; }
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const tokens=raw.trim().split(/\s+/);let position=0;const next=()=>Number(tokens[position++]);
const n=next(),nums=Array.from({length:n},next);
nextPermutation(nums);
const result=nums;
process.stdout.write(JSON.stringify(result)+'\n');
