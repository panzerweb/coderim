#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
int lengthOfLongestSubstring(const string& s) {
  int last[128];fill(begin(last),end(last),-1);int left=0,best=0;
  for(int right=0;right<(int)s.size();right++){unsigned char c=s[right];left=max(left,last[c]+1);last[c]=right;best=max(best,right-left+1);}
  return best;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
string jsonInts(const vector<int>& values,int count=-1){if(count<0)count=values.size();string out="[";for(int i=0;i<count;i++){if(i)out+=',';out+=to_string(values[i]);}return out+']';}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
string s;getline(cin,s);if(!s.empty()&&s.back()=='\r')s.pop_back();cout<<lengthOfLongestSubstring(s)<<'\n';
}
