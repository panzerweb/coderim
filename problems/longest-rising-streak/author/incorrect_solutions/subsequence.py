import sys,bisect
d=iter(map(int,sys.stdin.read().split()))
for _ in range(next(d)):
 n=next(d);tails=[]
 for _ in range(n):
  v=next(d);i=bisect.bisect_left(tails,v)
  if i==len(tails):tails.append(v)
  else:tails[i]=v
 print(len(tails))
