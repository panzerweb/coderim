#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int n; cin >> n; vector<vector<int>> children(n+1);
for(int i=1;i<n;i++) {int p,c;cin>>p>>c;children[p].push_back(c);}
vector<int> tin(n+1),tout(n+1),st{1}; int clock=0;
while(!st.empty()) {int v=st.back();st.pop_back();if(v<0)tout[-v]=clock;
  else {tin[v]=clock++;st.push_back(-v);for(int c:children[v])st.push_back(c);}}
int q;cin>>q;while(q--){int u,v;cin>>u>>v;cout<<(tin[u]<=tin[v]&&tin[v]<tout[u]?"YES":"NO")<<'\n';}
}
