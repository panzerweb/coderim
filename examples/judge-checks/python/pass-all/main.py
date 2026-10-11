import sys


def is_valid(source):
    stack = []
    quote = None
    escaped = False
    matching = {')': '(', ']': '[', '}': '{'}

    for char in source:
        if quote is not None:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
        elif char in '([{':
            stack.append(char)
        elif char in matching:
            if not stack or stack.pop() != matching[char]:
                return False

    return not stack and quote is None and not escaped


source = sys.stdin.readline().removesuffix("\n").removesuffix("\r")
print("VALID" if is_valid(source) else "INVALID")
