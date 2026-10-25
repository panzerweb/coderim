import sys
d=iter(map(int,sys.stdin.read().split()))
for _ in range(next(d)):
 n=next(d);a=[next(d) for _ in range(n)];best=cur=1
 for i in range(1,n):
  cur=cur+1 if a[i]>=a[i-1] else 1;best=max(best,cur)
 print(best)
