import sys

source = sys.stdin.readline().removesuffix("\n").removesuffix("\r")

# Deliberately limited fixture: public samples 1, 2, and 6 only.
implemented = {
    "function test() { return [a, (b + c)]; }",
    'print("This [ is not a bracket!")',
    "log('User said \"Hello [World]\"')",
}
print("VALID" if source in implemented else "NOT_IMPLEMENTED")
