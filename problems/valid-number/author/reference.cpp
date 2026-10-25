#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
bool isNumber(const string& s) {
  int i=0,n=s.size(),digits=0;auto digit=[](char c){return c>='0'&&c<='9';};
  if(i<n&&(s[i]=='+'||s[i]=='-'))i++;
  while(i<n&&digit(s[i])){digits++;i++;}
  if(i<n&&s[i]=='.'){i++;while(i<n&&digit(s[i])){digits++;i++;}}
  if(!digits)return false;
  if(i<n&&(s[i]=='e'||s[i]=='E')){i++;if(i<n&&(s[i]=='+'||s[i]=='-'))i++;int start=i;while(i<n&&digit(s[i]))i++;if(i==start)return false;}
  return i==n;
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
