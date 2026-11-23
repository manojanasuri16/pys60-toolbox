#!/bin/sh
# Builds rscfix/group/myapp_rscfix.exe with the GnuPoc toolchain. Rename the target
# (see the mmp) for a real app. SYMBIAN_SDK: dir with s60_32/, gnupoc-bin/, csl-gcc/.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
S=${SYMBIAN_SDK:-$HERE/../symbian-sdk}
export EPOCROOT="$S/s60_32/"
export PATH="$S/gnupoc-bin:$S/csl-gcc/bin:$PATH"
mkdir -p "$HERE/out"
cd "$HERE/rscfix/group"
bldmake bldfiles >/dev/null 2>&1
abld build gcce urel > "$HERE/out/build.log" 2>&1 || true
[ -f "$EPOCROOT/epoc32/release/gcce/urel/myapp_rscfix.exe" ] || { echo "build failed, see out/build.log"; exit 1; }
cp "$EPOCROOT/epoc32/release/gcce/urel/myapp_rscfix.exe" "$HERE/out/"
ls -la "$HERE/out/myapp_rscfix.exe"
