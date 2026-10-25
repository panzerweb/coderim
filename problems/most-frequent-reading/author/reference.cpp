#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int n; cin >> n; unordered_map<int,int> counts;
int bestValue=INT_MAX,bestCount=0;
for(int i=0;i<n;i++) { int v; cin >> v; int count=++counts[v];
  if(count>bestCount || (count==bestCount && v<bestValue)) { bestCount=count; bestValue=v; }
}
cout << bestValue << ' ' << bestCount << '\n';
}
