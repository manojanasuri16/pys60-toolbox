# pys60-toolbox

Small, tested helpers for writing and shipping **Python for S60 1.4.5** (Python 2.2) apps on
Nokia S60 3rd Edition phones (developed on the Nokia N79):

1. **`rscfix`: the memory-card install fix.** A PyS60 1.4.5 app on a drive other than Python's
   closes at once, silently. A tiny native program run by the installer fixes that, so one `.sis`
   works from phone memory or the card.
2. **Python 2.2 checkers** (`check_py22.py`, `check_ints.py`): catch the syntax, builtins and integer
   traps that a modern Python 3 / 2.7 lets through but Python 2.2 on the phone does not.
3. **Notes** on Python 2.2 and PyS60 UI/sockets, and a few drop-in snippets.

All of it comes out of [RetroTele](https://github.com/manojanasuri16/RetroTele),
[RetroSend](https://github.com/manojanasuri16/RetroSend) and
[RetroTorch](https://github.com/manojanasuri16/RetroTorch) (the memory-card fix was found in RetroTorch).

## Status

| Part | Verified |
|---|---|
| rscfix on the phone | yes: Nokia N79, app on the memory card, Python for S60 in phone memory, **unlocked phone (Open4All)**; shipped in RetroSend, RetroTorch and RetroTele |
| rscfix rebuilt from this repo layout | yes, 2026-11-23, compiles and links (`myapp_rscfix.exe`, 2,433 bytes); not re-installed on a phone from this layout |
| rscfix on a **stock (not unlocked) phone** | does **not** work: writing into `\resource` needs the unlock; use the manual fix below |
| `check_py22.py`, `check_ints.py` | used in the three apps' test runs; run here on the example files (OK) |
| Other S60 3rd Edition devices | untested (the mechanism is not N79 specific: it is how PyS60 1.4.5 loads `appuifw`) |

## 1. rscfix: PyS60 apps from the memory card

**Symptom:** the app is installed on `E:` (card) and closes immediately, before any Python runs, with no
message and no log.

**Cause:** when PyS60 1.4.5's app framework starts a script it loads
`\resource\apps\appuifwmodule.rsc` from the **drive of the app** (`appuifwmodule.cpp` calls
`TParse::Set(KAppuiFwRscFile, &AppFullName(), NULL)`), but the Python for S60 installer puts that file only on its
own drive (normally `C:`). A fix in the app's Python code cannot work: `appuifw` is loaded before the app's first line.

**Why a plain `.sis` cannot fix it:** installing `E:\resource\apps\appuifwmodule.rsc` makes the installer refuse
with "Update error", because a file with the same name on another drive would "eclipse" Python's file.

**Fix:** ship a copy of the rsc in your package (`\resource\<app>\appuifwmodule.rsc`) and a native EXE
named `<app>_rscfix.exe` in `\sys\bin`, marked "run on install" (SIS `FILERUN`, option RI + wait for end). After the files
are in place it copies the rsc to `<drive>:\resource\apps\` if it is not there already (if the copy is missing it searches the other drives for
Python's own). It logs to `E:\<app>_log.txt` or `C:\Data\<app>_log.txt` (`rscfix: ...` lines). The program takes
the app name from its own file name, so one source serves every app.

Writing into `\resource` is reserved on a stock phone, so this works only on an **unlocked phone (RomPatcher+ Open4All)**:
see the [unlock guide](https://github.com/manojanasuri16/symbian-unlock-guide). The EXE itself is built with
`CAPABILITY NONE` and relies on that patch.

### Use it in your app

1. Copy `rscfix/` and `build_rscfix.sh`. In `rscfix/group/myapp_rscfix.mmp` rename `TARGET` to `<yourapp>_rscfix.exe` and set a
   **unique UID** (the template uses `0xE0000001`; a duplicate UID/SID anywhere on the phone makes the install fail with just "Unable to install").
2. Build with the toolchain from [symbian-s60v3-toolchain](https://github.com/manojanasuri16/symbian-s60v3-toolchain):
   `SYMBIAN_SDK=/path/to/sdk sh build_rscfix.sh` -> `out/myapp_rscfix.exe`.
3. Lay out your package's extras: `extras/sys/bin/<yourapp>_rscfix.exe` and
   `extras/resource/<yourapp>/appuifwmodule.rsc` (the file from `rscfix/`).
4. Package with Ensymble, but through `tools/py2sis_rscfix.py`, which wraps `py2sis` so the `_rscfix.exe` is added last and
   marked run-on-install:

```sh
python2 tools/py2sis_rscfix.py /path/to/ensymble/src --uid=0xE0000002 --appname=MyApp --version=1.0.0 \
        --caps=NetworkServices+LocalServices+ReadUserData+WriteUserData+UserEnvironment \
        --extrasdir=extras --drive=any --cert=my.cer --privkey=my.key  myapp_dir  MyApp.sis </dev/null
# prints: rscfix: ...rscfix.exe runs on install
```

(`--drive=any` lets the installer ask phone memory or card. Never commit your certificate and key. Ensymble needs the patch in
`tools/ensymble-openssl.patch` to run with current OpenSSL on Linux, and `</dev/null` so it does not wait for a passphrase.
The py2sis_rscfix.py wrapper and this exact flow are what RetroTele's `build_sis.sh` uses; the command above was not run from this repo.)

### Phone not unlocked? By hand

Copy `appuifwmodule.rsc` to `resource\apps\` **on the app's drive**: USB "Mass storage" mode and copy it into the card's `resource/apps/`
folder, or use a file manager that can write to `E:\resource\`. Or install the app on the same drive as Python. Installing Python
itself on the card works for card apps but then Python apps in phone memory stop starting (same reason, reversed).

## 2. Python 2.2 checkers

```sh
python3 tools/check_py22.py myapp.py other.py     # syntax/builtins Python 2.2 lacks
python3 tools/check_ints.py *.py                  # non-ASCII source, '<<', hex literals >= 0x80000000
```

They parse your files with Python 3's `ast`, so the files must also be valid Python 3 syntax (print as a function, etc.) for them to be
checked, which RetroTele's sources are written to be. They report: conditional expressions, generator expressions, set/dict comprehensions, `with`, decorators, `except X as e`, step slices, `enumerate`, `sorted`, `reversed`, `sum`, `set`, `frozenset`, `any`,
`all`, `basestring`, `next`, `.sort(key=/reverse=)`, `str.rsplit`, `try/except/finally` in one statement, `print` with keywords, `<<`,
big hex literals, non-ASCII characters. They are static heuristics, not a Python 2.2 interpreter (building one on the PC was not possible
in this setup): a pass is not proof, a failure is a real problem. See [docs/PYTHON-2.2-NOTES.md](docs/PYTHON-2.2-NOTES.md).

## 3. Notes and snippets

- [docs/PYTHON-2.2-NOTES.md](docs/PYTHON-2.2-NOTES.md): integer rules, library gaps.
- [docs/PYS60-NOTES.md](docs/PYS60-NOTES.md): UI and socket patterns that worked on the N79 (avoiding blank screens, never
  closing sockets, int coordinates, logging, exit handling). RetroSend's longer
  [PYS60-NOTES.md](https://github.com/manojanasuri16/RetroSend/blob/main/docs/PYS60-NOTES.md) has the socket internals.
- `examples/safedraw.py`: the `SafeDraw` wrapper that makes every `graphics.Image` coordinate a plain int.

## Layout

```
rscfix/rscfix.cpp, appuifwmodule.rsc, group/   the on-install copier and its Symbian build files
build_rscfix.sh                                 builds it with GnuPoc
tools/                                          check_py22.py, check_ints.py, py2sis_rscfix.py, ensymble-openssl.patch
examples/safedraw.py
docs/
```

## Licence

MIT, see [LICENSE](LICENSE). `appuifwmodule.rsc` is Python for S60's, Apache 2.0: see [THIRD-PARTY.md](THIRD-PARTY.md).

## Part of the RetroArchive ecosystem

Extracted from [RetroTele](https://github.com/manojanasuri16/RetroTele), [RetroTorch](https://github.com/manojanasuri16/RetroTorch), [RetroSend](https://github.com/manojanasuri16/RetroSend). All apps, guides and open-source repos are listed on [RetroArchive](https://manojanasuri16.github.io/RetroArchive/) (see the [Open source page](https://manojanasuri16.github.io/RetroArchive/opensource/)); the build toolchain is [symbian-s60v3-toolchain](https://github.com/manojanasuri16/symbian-s60v3-toolchain).
