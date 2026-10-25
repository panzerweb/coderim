import java.io.*;
import java.util.*;
public class Main{
// YOUR SOLUTION: edit this function body.
static List<Integer> findSubstring(String s, String[] words) {
  int size=words[0].length(),count=words.length;List<Integer> result=new ArrayList<>();
  if(size*count>s.length())return result;
  Map<String,Integer> required=new HashMap<>();for(String w:words)required.put(w,required.getOrDefault(w,0)+1);
  for(int offset=0;offset<size;offset++){
    int left=offset,used=0;Map<String,Integer> seen=new HashMap<>();
    for(int right=offset;right+size<=s.length();right+=size){
      String word=s.substring(right,right+size);
      if(!required.containsKey(word)){seen.clear();used=0;left=right+size;continue;}
      seen.put(word,seen.getOrDefault(word,0)+1);used++;
      while(seen.get(word)>required.get(word)){String removed=s.substring(left,left+size);seen.put(removed,seen.get(removed)-1);used--;left+=size;}
      if(used==count){result.add(left);String removed=s.substring(left,left+size);seen.put(removed,seen.get(removed)-1);used--;left+=size;}
    }
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
String s=in.token();int n=in.number();String[] words=new String[n];for(int i=0;i<n;i++)words[i]=in.token();List<Integer> result=findSubstring(s,words);
StringJoiner out=new StringJoiner(",","[","]");for(int index:result)out.add(Integer.toString(index));System.out.println(out);
}
}
