#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
int lengthOfLongestSubstring(const string& s) {
  // TODO: implement the function.
  return 0;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
string jsonInts(const vector<int>& values,int count=-1){if(count<0)count=values.size();string out="[";for(int i=0;i<count;i++){if(i)out+=',';out+=to_string(values[i]);}return out+']';}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
string s;getline(cin,s);if(!s.empty()&&s.back()=='\r')s.pop_back();cout<<lengthOfLongestSubstring(s)<<'\n';
}
