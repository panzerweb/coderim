"""Organizer reference; never served to the participant interface."""
import sys


def validate(source: str) -> bool:
    stack = []
    quote = None
    escaped = False
    matching = {')': '(', ']': '[', '}': '{'}
    for char in source:
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char in '([{':
            stack.append(char)
        elif char in matching:
            if not stack or stack.pop() != matching[char]:
                return False
    return not stack and quote is None and not escaped


if __name__ == '__main__':
    line = sys.stdin.readline()
    if line.endswith('\n'):
        line = line[:-1]
        if line.endswith('\r'):
            line = line[:-1]
    print('VALID' if validate(line) else 'INVALID')
