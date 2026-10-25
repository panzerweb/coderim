import java.io.*;
import java.util.*;
public class Main{
// YOUR SOLUTION: edit this function body.
static List<String> fullJustify(String[] words, int maxWidth) {
  List<String> result=new ArrayList<>();
  for(int start=0;start<words.length;){
    int end=start+1,letters=words[start].length();
    while(end<words.length&&letters+words[end].length()+end-start<=maxWidth)letters+=words[end++].length();
    int gaps=end-start-1;StringBuilder line=new StringBuilder();
    if(end==words.length||gaps==0){
      for(int i=start;i<end;i++){if(i>start)line.append(' ');line.append(words[i]);}
      while(line.length()<maxWidth)line.append(' ');
    }else{
      int each=(maxWidth-letters)/gaps,extra=(maxWidth-letters)%gaps;
      for(int i=start;i<end;i++){line.append(words[i]);if(i<end-1)line.append(" ".repeat(each+(i-start<extra?1:0)));}
    }
    result.add(line.toString());start=end;
  }
  return result;
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
int n=in.number(),maxWidth=in.number();String[] words=new String[n];for(int i=0;i<n;i++)words[i]=in.token();List<String> result=fullJustify(words,maxWidth);
StringJoiner out=new StringJoiner(",","[","]");for(String line:result)out.add(quoteJSON(line));System.out.println(out);
}
}
