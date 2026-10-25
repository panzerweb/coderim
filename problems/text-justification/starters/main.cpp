#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
vector<string> fullJustify(const vector<string>& words, int maxWidth) {
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
int n,maxWidth;cin>>n>>maxWidth;vector<string> words(n);for(auto& w:words)cin>>w;auto result=fullJustify(words,maxWidth);
cout<<'[';for(int i=0;i<(int)result.size();i++){if(i)cout<<',';cout<<quoteJSON(result[i]);}cout<<"]\n";
}
