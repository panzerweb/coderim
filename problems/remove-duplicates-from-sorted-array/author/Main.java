import java.io.*;
import java.util.*;
public class Main{
// YOUR SOLUTION: edit this function body.
static int removeDuplicates(int[] nums) {
  int k=0;for(int i=0;i<nums.length;i++)if(k==0||nums[i]!=nums[k-1])nums[k++]=nums[i];return k;
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
int n=in.number();int[] nums=new int[n];for(int i=0;i<n;i++)nums[i]=in.number();
int k=removeDuplicates(nums);if(k<0||k>n||k>nums.length)System.out.println("null");else System.out.println("{\"k\":"+k+",\"nums\":"+jsonInts(nums,k)+"}");
}
}
