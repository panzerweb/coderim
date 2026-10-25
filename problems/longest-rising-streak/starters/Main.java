import java.io.*;
import java.util.*;
public class Main{
static class FastScanner {
  private final InputStream stream=System.in;
  private final byte[] buffer=new byte[65536]; private int position=0,length=0;
  int read() throws IOException {if(position>=length){length=stream.read(buffer);position=0;if(length<0)return -1;}return buffer[position++];}
  String token() throws IOException {StringBuilder s=new StringBuilder();int c;do{c=read();}while(c>=0&&c<=32);
    while(c>32){s.append((char)c);c=read();}return s.toString();}
  int number() throws IOException {return Integer.parseInt(token());}
}
public static void main(String[] args)throws Exception{FastScanner in=new FastScanner();
int t=in.number();while(t-->0){int n=in.number();int[] temperatures=new int[n];for(int i=0;i<n;i++)temperatures[i]=in.number();
// TODO: print one answer.
}
// TODO: solve and print the required answer(s).
}
}
