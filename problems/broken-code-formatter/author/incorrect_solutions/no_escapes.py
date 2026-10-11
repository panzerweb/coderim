import sys
stack = []
quote = None
valid = True
for c in sys.stdin.readline():
    if quote:
        if c == quote:
            quote = None
    elif c in "\"'":
        quote = c
    elif c in '([{':
        stack.append(c)
    elif c in ')]}':
        if not stack or stack.pop() != {')': '(', ']': '[', '}': '{'}[c]:
            valid = False
            break
print('VALID' if valid and not stack and not quote else 'INVALID')
