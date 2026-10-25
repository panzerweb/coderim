import sys,collections
a=list(map(int,sys.stdin.read().split()))[1:];c=collections.Counter(a);v=max(c,key=lambda x:(c[x],x));print(v,c[v])
