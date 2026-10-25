import sys
d=iter(sys.stdin.read().split());r,c=int(next(d)),int(next(d));g=[next(d) for _ in range(r)];s=next((i,j) for i in range(r) for j in range(c) if g[i][j]=='S');seen={s};st=[(*s,0)];ans=-1
while st:
 i,j,k=st.pop()
 if g[i][j]=='E':ans=k;break
 for x,y in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
  if 0<=x<r and 0<=y<c and g[x][y]!='#' and (x,y) not in seen:seen.add((x,y));st.append((x,y,k+1))
print(ans)
