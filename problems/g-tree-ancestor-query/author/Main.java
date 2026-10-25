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
int n=in.number();int[] head=new int[n+1],to=new int[n-1],next=new int[n-1];Arrays.fill(head,-1);
for(int i=0;i<n-1;i++){int p=in.number(),c=in.number();to[i]=c;next[i]=head[p];head[p]=i;}
int[] tin=new int[n+1],tout=new int[n+1],stack=new int[2*n+1];int size=0,clock=0;stack[size++]=1;
while(size>0){int v=stack[--size];if(v<0)tout[-v]=clock;else{tin[v]=clock++;stack[size++]=-v;
  for(int e=head[v];e>=0;e=next[e])stack[size++]=to[e];}}
int q=in.number();StringBuilder out=new StringBuilder();while(q-->0){int u=in.number(),v=in.number();
out.append(tin[u]<=tin[v]&&tin[v]<tout[u]?"YES\n":"NO\n");}System.out.print(out);
}
}
