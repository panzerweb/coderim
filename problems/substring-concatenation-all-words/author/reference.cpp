#include <bits/stdc++.h>
using namespace std;

// YOUR SOLUTION: edit this function body.
vector<int> findSubstring(const string& s, const vector<string>& words) {
  int size=words[0].size(),count=words.size();vector<int> result;
  if(size*count>(int)s.size())return result;
  unordered_map<string,int> required;for(const auto& w:words)required[w]++;
  for(int offset=0;offset<size;offset++){
    int left=offset,used=0;unordered_map<string,int> seen;
    for(int right=offset;right+size<=(int)s.size();right+=size){
      string word=s.substr(right,size);
      if(!required.count(word)){seen.clear();used=0;left=right+size;continue;}
      seen[word]++;used++;
      while(seen[word]>required[word]){seen[s.substr(left,size)]--;used--;left+=size;}
      if(used==count){result.push_back(left);seen[s.substr(left,size)]--;used--;left+=size;}
    }
  }
  return result;
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
