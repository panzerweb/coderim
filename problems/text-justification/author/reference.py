import json
import sys

# YOUR SOLUTION: edit this function body.
def fullJustify(words, maxWidth):
    result = []
    start = 0
    while start < len(words):
        end = start + 1
        letters = len(words[start])
        while end < len(words) and letters + len(words[end]) + end - start <= maxWidth:
            letters += len(words[end])
            end += 1
        gaps = end - start - 1
        if end == len(words) or gaps == 0:
            line = ' '.join(words[start:end])
            line += ' ' * (maxWidth - len(line))
        else:
            each, extra = divmod(maxWidth - letters, gaps)
            parts = []
            for i in range(start, end - 1):
                parts.append(words[i])
                parts.append(' ' * (each + (i - start < extra)))
            parts.append(words[end - 1])
            line = ''.join(parts)
        result.append(line)
        start = end
    return result

# PROVIDED INPUT/OUTPUT: leave this section intact.
def solve(stream, output):
    data=iter(stream.read().split())
    n,maxWidth=int(next(data)),int(next(data))
    words=[next(data) for _ in range(n)]
    result=fullJustify(words,maxWidth)
    output.write(json.dumps(result) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
