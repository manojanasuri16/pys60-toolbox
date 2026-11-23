# ensymble py2sis, with <app>_rscfix.exe run once by the installer.
#
# The exe (native/rscfix/rscfix.cpp, from RetroTorch) puts appuifw's resource file on the app's
# drive, so the app starts from phone memory or the memory card wherever Python
# for S60 is installed. It must run after the files are installed, so it is
# held back and added last, marked "run on install" (SIS FILERUN, RI).
#
# Usage: python2 py2sis_rscfix.py ENSYMBLE_SRC_DIR <py2sis options...>
import sys

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[1] + "/ensymble")   # its modules import "utils"
from ensymble.actions import py2sis

writer = py2sis.sisfile.SimpleSISWriter
field = py2sis.sisfield
orig_addfile = writer.addfile
orig_tostring = writer.tostring
held = []


def addfile(self, contents, target=None, *args, **kw):
    if target and target.lower().endswith(u"_rscfix.exe"):
        held.append((contents, target, args, kw))
        return
    orig_addfile(self, contents, target, *args, **kw)


def tostring(self):
    while held:
        contents, target, args, kw = held.pop(0)
        kw["operation"] = field.EOpRun
        kw["options"] = field.EInstFileRunOptionInstall | field.EInstFileRunOptionWaitEnd
        orig_addfile(self, contents, target, *args, **kw)
        print "rscfix: %s runs on install" % target
    return orig_tostring(self)

writer.addfile = addfile
writer.tostring = tostring
py2sis.run("ensymble.py", sys.argv[2:])
