#include <iostream>
#include <string>
#include <vector>
#include <tuple>
int main() {
    std::ios::sync_with_stdio(false);std::cin.tie(nullptr);
    int n;std::cin>>n;std::vector<std::vector<int>> adj(n);
    for(int i=1,p,c;i<n;i++){std::cin>>p>>c;--p;--c;adj[p].push_back(c);adj[c].push_back(p);}
    int levels=1;while((1<<levels)<=n)levels++;
    std::vector<std::vector<int>> up(levels,std::vector<int>(n));
    std::vector<int> depth(n),tin(n),tout(n);
    std::vector<std::tuple<int,int,bool>> stack{{0,-1,false}};int clock=0;
    while(!stack.empty()) {
        auto [v,p,exit]=stack.back();stack.pop_back();
        if(exit){tout[v]=clock;continue;}
        up[0][v]=p<0?v:p;tin[v]=clock++;stack.push_back({v,p,true});
        for(int c:adj[v])if(c!=p){depth[c]=depth[v]+1;stack.push_back({c,v,false});}
    }
    for(int k=1;k<levels;k++)for(int v=0;v<n;v++)up[k][v]=up[k-1][up[k-1][v]];
    auto fixed=[&](int u,int v){return tin[u]<=tin[v]&&tin[v]<tout[u];};
    auto ancestor=[&](int root,int u,int v){
        if(u==v||u==root)return true;
        if(!fixed(u,root))return fixed(u,v);
        int child=root,distance=depth[root]-depth[u]-1,bit=0;
        while(distance){if(distance&1)child=up[bit][child];distance>>=1;bit++;}
        return !fixed(child,v);
    };
    int q,root=0;std::cin>>q;
    while(q--){std::string op;std::cin>>op;if(op=="ROOT"){std::cin>>root;--root;}
        else{int u,v;std::cin>>u>>v;std::cout<<(ancestor(root,u-1,v-1)?"YES":"NO")<<'\n';}}
}
