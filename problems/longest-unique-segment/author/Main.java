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
int n=in.number(),left=0,best=0;Map<Integer,Integer> last=new HashMap<>();
for(int r=0;r<n;r++){int v=in.number();left=Math.max(left,last.getOrDefault(v,-1)+1);last.put(v,r);best=Math.max(best,r-left+1);}
System.out.println(best);
}
}
