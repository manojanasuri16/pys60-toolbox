#!/usr/bin/env python3
"""Reports constructs in a Python file that Python 2.2 (PyS60 1.4.5) cannot run."""
import ast
import sys

BAD_BUILTINS = {"enumerate", "sorted", "reversed", "sum", "set", "frozenset",
                "any", "all", "basestring", "next"}


def check(path):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src, path)
    issues = []

    def bad(node, msg):
        issues.append("%s:%d: %s" % (path, getattr(node, "lineno", 0), msg))

    def visit(node, in_try_finally=False):
        if isinstance(node, ast.IfExp):
            bad(node, "conditional expression (a if c else b)")
        elif isinstance(node, ast.GeneratorExp):
            bad(node, "generator expression")
        elif isinstance(node, (ast.SetComp, ast.DictComp, ast.Set)):
            bad(node, "set/dict comprehension or set literal")
        elif isinstance(node, (ast.With, getattr(ast, "AsyncWith", ast.With))):
            bad(node, "with statement")
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.decorator_list:
            bad(node, "decorator")
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bad(node, "'except X as e' (use sys.exc_info())")
        elif isinstance(node, (ast.Yield, ast.YieldFrom)) and in_try_finally:
            bad(node, "yield inside try/finally")
        elif isinstance(node, ast.Slice) and node.step is not None:
            bad(node, "slice with a step (a[::2]) needs Python 2.3")
        elif isinstance(node, ast.MatMult if hasattr(ast, "MatMult") else ()):
            bad(node, "@ operator")
        elif isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id in BAD_BUILTINS:
                bad(node, "builtin %s() not in Python 2.2" % f.id)
            if isinstance(f, ast.Name) and f.id == "print" and node.keywords:
                bad(node, "print() with keyword arguments")
            if isinstance(f, ast.Attribute):
                if f.attr == "sort" and any(k.arg in ("key", "reverse") for k in node.keywords):
                    bad(node, ".sort(key=/reverse=) not in Python 2.2")
                if f.attr == "rsplit":
                    bad(node, "str.rsplit not in Python 2.2")
        tf = in_try_finally
        if isinstance(node, ast.Try):
            if node.handlers and node.finalbody:
                bad(node, "try with both except and finally (nest them)")
            if node.finalbody:
                tf = True
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            tf = False
        for child in ast.iter_child_nodes(node):
            visit(child, tf)

    visit(tree)
    return issues


def main():
    issues = []
    for p in sys.argv[1:]:
        issues.extend(check(p))
    for i in issues:
        print(i)
    if issues:
        print("%d Python 2.2 issue(s)" % len(issues))
        sys.exit(1)
    print("Python 2.2 check: OK")


if __name__ == "__main__":
    main()
