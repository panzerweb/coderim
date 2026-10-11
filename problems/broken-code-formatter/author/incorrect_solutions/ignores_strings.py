import sys
s = sys.stdin.readline()
stack = []
valid = True
for c in s:
    if c in '([{':
        stack.append(c)
    elif c in ')]}':
        if not stack or stack.pop() != {')': '(', ']': '[', '}': '{'}[c]:
            valid = False
            break
print('VALID' if valid and not stack else 'INVALID')
