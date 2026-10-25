#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
void nextPermutation(vector<int>& nums) {
  int pivot=(int)nums.size()-2;
  while(pivot>=0 && nums[pivot]>=nums[pivot+1])pivot--;
  if(pivot>=0){int successor=nums.size()-1;while(nums[successor]<=nums[pivot])successor--;swap(nums[pivot],nums[successor]);}
  reverse(nums.begin()+pivot+1,nums.end());
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
string jsonInts(const vector<int>& values,int count=-1){if(count<0)count=values.size();string out="[";for(int i=0;i<count;i++){if(i)out+=',';out+=to_string(values[i]);}return out+']';}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int n;cin>>n;vector<int> nums(n);for(int& value:nums)cin>>value;
nextPermutation(nums);cout<<jsonInts(nums)<<'\n';
}
