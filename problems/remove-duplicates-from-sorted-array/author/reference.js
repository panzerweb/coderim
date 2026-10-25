// YOUR SOLUTION: edit this function body.
function removeDuplicates(nums) {
  let k=0;
  for (let i=0;i<nums.length;i++) {
    if (k===0 || nums[i]!==nums[k-1]) nums[k++]=nums[i];
  }
  return k;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const tokens=raw.trim().split(/\s+/);let position=0;const next=()=>Number(tokens[position++]);
const n=next(),nums=Array.from({length:n},next);
const k=removeDuplicates(nums);
const result=Number.isInteger(k)&&k>=0&&k<=n&&k<=nums.length?{k,nums:nums.slice(0,k)}:null;
process.stdout.write(JSON.stringify(result)+'\n');
