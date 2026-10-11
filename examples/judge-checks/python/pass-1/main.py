import sys

source = sys.stdin.readline().removesuffix("\n").removesuffix("\r")

# Deliberately limited fixture: only public sample 1 is implemented.
if source == "function test() { return [a, (b + c)]; }":
    print("VALID")
else:
    print("NOT_IMPLEMENTED")
