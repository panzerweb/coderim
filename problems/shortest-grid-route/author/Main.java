import java.io.*;
import java.util.*;
public class Main {
static class FastScanner {
  private final InputStream stream=System.in;
  private final byte[] buffer=new byte[65536]; private int position=0,length=0;
  int read() throws IOException {if(position>=length){length=stream.read(buffer);position=0;if(length<0)return -1;}return buffer[position++];}
  String token() throws IOException {StringBuilder s=new StringBuilder();int c;do{c=read();}while(c>=0&&c<=32);
    while(c>32){s.append((char)c);c=read();}return s.toString();}
  int number() throws IOException {return Integer.parseInt(token());}
}
static boolean asciiAlnum(char c){return c>='a'&&c<='z'||c>='A'&&c<='Z'||c>='0'&&c<='9';}
public static void main(String[] args) throws Exception {
FastScanner in=new FastScanner();
int rows=in.number(),cols=in.number(),start=0;String[] grid=new String[rows];
for(int r=0;r<rows;r++){grid[r]=in.token();int c=grid[r].indexOf('S');if(c>=0)start=r*cols+c;}
int[] dist=new int[rows*cols],queue=new int[rows*cols],dr={-1,1,0,0},dc={0,0,-1,1};Arrays.fill(dist,-1);
int tail=0,answer=-1;queue[tail++]=start;dist[start]=0;
for(int h=0;h<tail;h++){int x=queue[h],r=x/cols,c=x%cols;if(grid[r].charAt(c)=='E'){answer=dist[x];break;}
  for(int d=0;d<4;d++){int nr=r+dr[d],nc=c+dc[d];if(nr>=0&&nr<rows&&nc>=0&&nc<cols){int y=nr*cols+nc;
    if(grid[nr].charAt(nc)!='#'&&dist[y]<0){dist[y]=dist[x]+1;queue[tail++]=y;}}}}
System.out.println(answer);
}
}
