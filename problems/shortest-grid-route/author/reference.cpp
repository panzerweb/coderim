#include <bits/stdc++.h>
using namespace std;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int rows,cols;cin>>rows>>cols;vector<string> grid(rows);int start=0;
for(int r=0;r<rows;r++){cin>>grid[r];for(int c=0;c<cols;c++)if(grid[r][c]=='S')start=r*cols+c;}
vector<int> dist(rows*cols,-1);queue<int> q;q.push(start);dist[start]=0;
int answer=-1,dr[]={-1,1,0,0},dc[]={0,0,-1,1};
while(!q.empty()){int x=q.front();q.pop();int r=x/cols,c=x%cols;
  if(grid[r][c]=='E'){answer=dist[x];break;}
  for(int d=0;d<4;d++){int nr=r+dr[d],nc=c+dc[d];
    if(nr>=0&&nr<rows&&nc>=0&&nc<cols&&grid[nr][nc]!='#'&&dist[nr*cols+nc]<0){
      dist[nr*cols+nc]=dist[x]+1;q.push(nr*cols+nc);}}}
cout<<answer<<'\n';
}
