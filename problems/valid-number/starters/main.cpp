#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
bool isNumber(const string& s) {
  // TODO: implement the function.
  return false;
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
string s;getline(cin,s);if(!s.empty()&&s.back()=='\r')s.pop_back();cout<<(isNumber(s)?"true":"false")<<'\n';
}
