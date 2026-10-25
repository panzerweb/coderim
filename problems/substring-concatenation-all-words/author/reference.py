import json
import sys

# YOUR SOLUTION: edit this function body.
def findSubstring(s, words):
    from collections import Counter
    size, count = len(words[0]), len(words)
    if size * count > len(s):
        return []
    required = Counter(words)
    result = []
    for offset in range(size):
        left = offset
        seen = {}
        used = 0
        for right in range(offset, len(s) - size + 1, size):
            word = s[right:right + size]
            if word not in required:
                seen.clear()
                used = 0
                left = right + size
                continue
            seen[word] = seen.get(word, 0) + 1
            used += 1
            while seen[word] > required[word]:
                removed = s[left:left + size]
                seen[removed] -= 1
                used -= 1
                left += size
            if used == count:
                result.append(left)
                removed = s[left:left + size]
                seen[removed] -= 1
                used -= 1
                left += size
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
