#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
struct Node {
    int length=0, first=0, last=0, prefix=0, suffix=0, best=0;
};
Node leaf(int x) { return {1,x,x,1,1,1}; }
Node merge(Node a, Node b) {
    if (!a.length) return b;
    if (!b.length) return a;
    bool joins=a.last<b.first;
    return {a.length+b.length,a.first,b.last,
        joins && a.prefix==a.length ? a.length+b.prefix:a.prefix,
        joins && b.suffix==b.length ? b.length+a.suffix:b.suffix,
        std::max({a.best,b.best,joins ? a.suffix+b.prefix:0})};
}
int main() {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    int t; std::cin>>t;
    while(t--) {
        int n,q,size=1; std::cin>>n>>q; while(size<n)size*=2;
        std::vector<Node> tree(2*size);
        for(int i=0,x;i<n;i++){std::cin>>x;tree[size+i]=leaf(x);}
        for(int i=size-1;i>0;i--)tree[i]=merge(tree[i*2],tree[i*2+1]);
        while(q--) {
            std::string op;int a,b;std::cin>>op>>a>>b;
            if(op=="UPDATE") {
                int p=size+a-1;tree[p]=leaf(b);
                for(p/=2;p>0;p/=2)tree[p]=merge(tree[p*2],tree[p*2+1]);
            } else {
                int l=size+a-1,r=size+b;Node before,after;
                while(l<r) {
                    if(l&1)before=merge(before,tree[l++]);
                    if(r&1)after=merge(tree[--r],after);
                    l/=2;r/=2;
                }
                std::cout<<merge(before,after).best<<'\n';
            }
        }
    }
}
