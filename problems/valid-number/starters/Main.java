import java.io.*;
import java.util.*;
public class Main{
// YOUR SOLUTION: edit this function body.
static boolean isNumber(String s) {
  // TODO: implement the function.
  return false;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
static class FastScanner {
  private final InputStream stream=System.in;
  private final byte[] buffer=new byte[65536]; private int position=0,length=0;
  int read() throws IOException {if(position>=length){length=stream.read(buffer);position=0;if(length<0)return -1;}return buffer[position++];}
  String token() throws IOException {StringBuilder s=new StringBuilder();int c;do{c=read();}while(c>=0&&c<=32);
    while(c>32){s.append((char)c);c=read();}return s.toString();}
  int number() throws IOException {return Integer.parseInt(token());}
}
// Provided JSON string escaping; spaces inside strings are preserved.
static String quoteJSON(String value){
  StringBuilder out=new StringBuilder("\"");String hex="0123456789abcdef";
  for(int i=0;i<value.length();i++){char c=value.charAt(i);
    if(c=='"'||c=='\\'){out.append('\\').append(c);}
    else if(c<32){out.append("\\u00").append(hex.charAt(c>>4)).append(hex.charAt(c&15));}
    else out.append(c);
  }
  return out.append('"').toString();
}
public static void main(String[] args)throws Exception{FastScanner in=new FastScanner();
String s=new BufferedReader(new InputStreamReader(System.in)).readLine();System.out.println(isNumber(s)?"true":"false");
}
}
