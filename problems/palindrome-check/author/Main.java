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
String text=new BufferedReader(new InputStreamReader(System.in)).readLine();
int l=0,r=text.length()-1;boolean valid=true;
while(l<r){char a=text.charAt(l),b=text.charAt(r);
  if(!asciiAlnum(a))l++;else if(!asciiAlnum(b))r--;
  else if(Character.toLowerCase(a)!=Character.toLowerCase(b)){valid=false;break;}else{l++;r--;}}
System.out.println(valid?"YES":"NO");
}
}
