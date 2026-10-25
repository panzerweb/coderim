"""Private organizer reference; auxiliary bounds exclude stored I/O."""
import sys

def tokens(stream):
    for line in stream:
        yield from line.split()

def solve(stream, output):
    text = stream.readline().rstrip('\r\n')
    left, right = 0, len(text) - 1
    def alnum(c):
        return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9'
    while left < right:
        if not alnum(text[left]):
            left += 1
        elif not alnum(text[right]):
            right -= 1
        elif text[left].lower() != text[right].lower():
            output.write('NO\n')
            return
        else:
            left += 1
            right -= 1
    output.write('YES\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
