import sys
s = sys.stdin.readline()
print('VALID' if all(s.count(a) == s.count(b) for a, b in [('(', ')'), ('[', ']'), ('{', '}')]) else 'INVALID')
