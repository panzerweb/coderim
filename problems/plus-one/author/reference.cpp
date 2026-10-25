#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
vector<int> plusOne(vector<int>& digits) {
  for (int i=(int)digits.size()-1;i>=0;i--) {
    if (digits[i]<9) { digits[i]++; return digits; }
    digits[i]=0;
  }
  vector<int> result(digits.size()+1,0); result[0]=1; return result;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
string jsonInts(const vector<int>& values,int count=-1){if(count<0)count=values.size();string out="[";for(int i=0;i<count;i++){if(i)out+=',';out+=to_string(values[i]);}return out+']';}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int n;cin>>n;vector<int> nums(n);for(int& value:nums)cin>>value;
auto result=plusOne(nums);cout<<jsonInts(result)<<'\n';
}
