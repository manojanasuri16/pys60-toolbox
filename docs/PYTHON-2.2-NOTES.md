# Writing for Python 2.2 (Python for S60 1.4.5)

The interpreter on S60 3rd Edition is Python 2.2.2 on a 32-bit ARM. Rules learned writing a
whole MTProto/crypto stack and three apps for it (see also `tools/check_py22.py`, `tools/check_ints.py`).

## Integers (the nasty ones)

- **`<<` drops bits** on an `int` instead of growing into a `long`. Multiply by a power of two instead (multiplication promotes).
- **Hex literals >= `0x80000000` are negative `int`s.** Write big masks in decimal (`4294967295`).
- Keep 32-bit values in `0 .. 2**32-1` and mask with `M32` after `+` and `*`.
- For speed in hot loops, keep 32-bit words as two 16-bit halves: long arithmetic on the phone is slow.
- `random.randint(0, 0x7fffffff)` raises `OverflowError` (it adds 1 to the bound); keep ranges small.
- PyS60 drawing calls want plain `int` coordinates, not longs (see `examples/safedraw.py`).

## Language gaps

No `bool` (`True` is `1`, so a JSON encoder cannot tell them apart), `enumerate`, `sorted`, `reversed`, `sum`, `set`, `any`/`all`,
generator expressions, conditional expressions (`x if c else y`), `with`, decorators, `except X as e` (use `sys.exc_info()`),
`try/except/finally` in one statement (nest them), step slices (`a[::2]`, Python 2.3), `str.rsplit`, `list.sort(key=...)`,
`"ab" in s` for substrings (use `s.find("ab") >= 0`), `b""` literals.

## Source files

- **ASCII only** (`check_ints.py` enforces it): write non-ASCII text as `\u` escapes in `u"..."` strings. Beware that some editors and tools turn `\\u` into the literal character, which then breaks the file.
- `.py` files run from the app directory; a script crash during start-up just closes the app silently. Log to a file from line 1 (see the PyS60 notes).

## Tooling

- Static checks: `check_py22.py` (syntax/builtins), `check_ints.py` (integer rules + ASCII). Keep your files valid Python 3 *syntax* so the
  checkers can parse them, and run the real tests with a Python 2.7 (it is much more permissive than 2.2: a pass proves less than you think).
- Building Python 2.2 itself on a modern 64-bit PC was not possible in the author's setup, so real 2.2 behaviour was only ever tested on the phone.
