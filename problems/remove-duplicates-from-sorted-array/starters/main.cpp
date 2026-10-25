#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
int removeDuplicates(vector<int>& nums) {
  // TODO: implement the function.
  return 0;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
string jsonInts(const vector<int>& values,int count=-1){if(count<0)count=values.size();string out="[";for(int i=0;i<count;i++){if(i)out+=',';out+=to_string(values[i]);}return out+']';}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int n;cin>>n;vector<int> nums(n);for(int& value:nums)cin>>value;
int k=removeDuplicates(nums);if(k<0||k>n||k>(int)nums.size())cout<<"null\n";else cout<<"{\"k\":"<<k<<",\"nums\":"<<jsonInts(nums,k)<<"}\n";
}
