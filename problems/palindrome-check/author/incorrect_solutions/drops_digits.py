s=''.join(c.lower() for c in input() if c.isalpha());print('YES' if s==s[::-1] else 'NO')
