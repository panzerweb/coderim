import json
import sys

# YOUR SOLUTION: edit this function body.
def findSubstring(s, words):
    from collections import Counter
    k=len(words[0]);total=k*len(words);required=Counter(words);i=0;result=[]
    while i+total<=len(s):
        if Counter(s[j:j+k] for j in range(i,i+total,k))==required:
            result.append(i);i+=total
        else:
            i+=1
    return result

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    data=iter(stream.read().split())
    s=next(data)
    words=[next(data) for _ in range(int(next(data)))]
    result=findSubstring(s,words)
    output.write(json.dumps(result) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
