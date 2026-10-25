import java.io.*;
import java.util.*;
public class Main{
// YOUR SOLUTION: edit this function body.
static int lengthOfLongestSubstring(String s) {
  int[] last=new int[128];Arrays.fill(last,-1);int left=0,best=0;
  for(int right=0;right<s.length();right++){int c=s.charAt(right);left=Math.max(left,last[c]+1);last[c]=right;best=Math.max(best,right-left+1);}return best;
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
static String jsonInts(int[] values,int count){if(count<0)count=values.length;StringJoiner out=new StringJoiner(",","[","]");for(int i=0;i<count;i++)out.add(Integer.toString(values[i]));return out.toString();}
public static void main(String[] args)throws Exception{FastScanner in=new FastScanner();
String s=new BufferedReader(new InputStreamReader(System.in)).readLine();if(s==null)s="";System.out.println(lengthOfLongestSubstring(s));
}
}
