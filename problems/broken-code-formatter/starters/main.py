import sys

source = sys.stdin.readline()
if source.endswith('\n'):
    source = source[:-1]
    if source.endswith('\r'):
        source = source[:-1]

# Read one source-code line, preserving spaces. Print VALID or INVALID.
