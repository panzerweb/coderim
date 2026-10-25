#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
vector<int> findSubstring(const string& s, const vector<string>& words) {
  // TODO: implement the function.
  return {};
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
// Provided JSON string escaping; spaces inside strings are preserved.
string quoteJSON(const string& value) {
  string out="\"";const char* hex="0123456789abcdef";
  for(unsigned char c:value){
    if(c=='"'||c=='\\'){out+='\\';out+=(char)c;}
    else if(c<32){out+="\\u00";out+=hex[c>>4];out+=hex[c&15];}
    else out+=(char)c;
  }
  return out+'"';
}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
string s;int n;cin>>s>>n;vector<string> words(n);for(auto& w:words)cin>>w;auto result=findSubstring(s,words);
cout<<'[';for(int i=0;i<(int)result.size();i++){if(i)cout<<',';cout<<result[i];}cout<<"]\n";
}
