#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int n;cin>>n;unordered_map<int,int> last;int left=0,best=0;
for(int r=0;r<n;r++){int v;cin>>v;auto it=last.find(v);if(it!=last.end())left=max(left,it->second+1);
last[v]=r;best=max(best,r-left+1);}cout<<best<<'\n';
}
