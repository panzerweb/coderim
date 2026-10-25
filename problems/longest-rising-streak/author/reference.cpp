#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int t; cin >> t;
while(t--) { int n,previous; cin >> n >> previous; int best=1,current=1;
  for(int i=1;i<n;i++) { int value; cin >> value; current=value>previous?current+1:1; best=max(best,current); previous=value; }
  cout << best << '\n';
}
}
