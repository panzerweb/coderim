#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
string text; getline(cin,text);
auto alnum=[](char c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9');};
int l=0,r=(int)text.size()-1; bool valid=true;
while(l<r) { if(!alnum(text[l])) ++l; else if(!alnum(text[r])) --r;
  else if(tolower((unsigned char)text[l])!=tolower((unsigned char)text[r])) {valid=false;break;}
  else {++l;--r;}
}
cout << (valid?"YES":"NO") << '\n';
}
