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
int n=in.number(),bestValue=Integer.MAX_VALUE,bestCount=0; Map<Integer,Integer> counts=new HashMap<>();
for(int i=0;i<n;i++){int v=in.number(),count=counts.getOrDefault(v,0)+1;counts.put(v,count);
  if(count>bestCount||(count==bestCount&&v<bestValue)){bestCount=count;bestValue=v;}}
System.out.println(bestValue+" "+bestCount);
}
}
