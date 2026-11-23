#!/usr/bin/env python3
"""Non-ASCII source and integer traps of Python 2.2 on a 32-bit phone (see tgcrypto.py):
  * `<<` drops high bits instead of growing into a long -> multiply instead
  * hex literals >= 0x80000000 are negative ints -> write them in decimal
"""
import ast
import io
import sys
import tokenize


def check(path):
    src = open(path, encoding="utf-8").read()
    issues = []
    for n, line in enumerate(src.split("\n")):
        if any(ord(c) > 127 for c in line):
            issues.append("%s:%d: non-ASCII character (Python 2.2 needs \\u escapes)"
                          % (path, n + 1))
    for node in ast.walk(ast.parse(src, path)):
        if isinstance(node, (ast.BinOp, ast.AugAssign)) and isinstance(node.op, ast.LShift):
            issues.append("%s:%d: '<<' (use multiplication)" % (path, node.lineno))
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.NUMBER and tok.string.lower().startswith("0x"):
            if int(tok.string, 16) >= 0x80000000:
                issues.append("%s:%d: hex literal %s is negative on Python 2.2"
                              % (path, tok.start[0], tok.string))
    return issues


issues = []
for p in sys.argv[1:]:
    issues.extend(check(p))
for i in issues:
    print(i)
if issues:
    sys.exit(1)
print("integer check: OK")
