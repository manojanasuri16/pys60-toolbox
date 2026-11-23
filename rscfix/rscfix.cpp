// <app>_rscfix.exe: run once by the installer, after the app's files are in
// place (SIS "run on install"). The same source serves every app: the app name
// comes from the exe's own name (retrosend_rscfix.exe -> "retrosend"), giving
// the log <app>_log.txt and the shipped copy \resource\<app>\appuifwmodule.rsc.
// From RetroTorch (github.com/manojanasuri16/RetroTorch).
//
// A Python for S60 1.4.5 app closes at once, before any of its Python code
// runs, unless \resource\apps\appuifwmodule.rsc is on the app's own drive:
// PyS60's app framework loads it from the drive of the app (appuifwmodule.cpp:
// TParse::Set(KAppuiFwRscFile, &AppFullName(), NULL)), but Python for S60 puts
// it only on its own drive. A .sis can't install it there (the installer
// refuses to "eclipse" Python's copy on the other drive), so this program
// copies the copy the app ships in \resource\<app>\ into place.
//
// It runs from \sys\bin on the drive the app was installed to. Writing into
// \resource needs an unlocked phone (e.g. the Open4All patch); otherwise the
// copy fails and the log says so.

#include <e32base.h>
#include <f32file.h>

_LIT(KRsc, "\\resource\\apps\\appuifwmodule.rsc");
_LIT(KRscDir, "\\resource\\apps\\");
_LIT(KSuffix, "_rscfix");

static TBuf<32> gApp;       // "retrosend" for retrosend_rscfix.exe

static void Log(RFs& aFs, const TDesC8& aMsg, TInt aNum)
{
    TFileName log1(_L("E:\\"));
    log1.Append(gApp);
    log1.Append(_L("_log.txt"));
    TFileName log2(_L("C:\\Data\\"));
    log2.Append(gApp);
    log2.Append(_L("_log.txt"));
    TBuf8<200> line;
    line.Copy(_L8("rscfix: "));
    line.Append(aMsg);
    line.Append(' ');
    line.AppendNum(aNum);
    line.Append('\n');
    const TDesC* names[2] = {&log1, &log2};
    for (TInt i = 0; i < 2; i++) {
        RFile f;
        TInt err = f.Open(aFs, *names[i], EFileWrite | EFileShareAny);
        if (err == KErrNotFound)
            err = f.Create(aFs, *names[i], EFileWrite | EFileShareAny);
        if (err == KErrNone) {
            TInt pos = 0;
            f.Seek(ESeekEnd, pos);
            f.Write(line);
            f.Close();
            return;
        }
    }
}

static TBool Exists(RFs& aFs, const TDesC& aPath)
{
    TEntry e;
    return aFs.Entry(aPath, e) == KErrNone;
}

static TInt CopyFile(RFs& aFs, const TDesC& aFrom, const TDesC& aTo)
{
    RFile in;
    TInt err = in.Open(aFs, aFrom, EFileRead | EFileShareReadersOnly);
    if (err != KErrNone)
        return err;
    TInt size = 0;
    in.Size(size);
    HBufC8* buf = HBufC8::New(size);
    if (!buf) {
        in.Close();
        return KErrNoMemory;
    }
    TPtr8 p = buf->Des();
    err = in.Read(p);
    in.Close();
    if (err == KErrNone) {
        RFile out;
        err = out.Replace(aFs, aTo, EFileWrite);
        if (err == KErrNone) {
            err = out.Write(p);
            out.Close();
        }
    }
    delete buf;
    return err;
}

static void Fix()
{
    RFs fs;
    if (fs.Connect() != KErrNone)
        return;
    TFileName me = RProcess().FileName();     // X:\sys\bin\<app>_rscfix.exe
    TBuf<2> drive = me.Left(2);
    TParsePtrC parse(me);
    TPtrC name = parse.Name();
    TInt cut = name.FindF(KSuffix);
    if (cut > 0)
        name.Set(name.Left(cut));
    gApp.Copy(name.Left(32));
    TFileName target(drive);
    target.Append(KRsc);
    Log(fs, _L8("start, app drive"), drive[0]);
    if (Exists(fs, target)) {
        Log(fs, _L8("appuifwmodule.rsc already on the app drive"), 0);
        fs.Close();
        return;
    }
    // the copy shipped with RetroTorch, else Python's own on another drive
    TFileName src(drive);
    src.Append(_L("\\resource\\"));
    src.Append(gApp);
    src.Append(_L("\\appuifwmodule.rsc"));
    if (!Exists(fs, src)) {
        src.Zero();
        for (TInt d = 'C'; d <= 'Z' && src.Length() == 0; d++) {
            TFileName p;
            p.Append(TChar(d));
            p.Append(':');
            p.Append(KRsc);
            if (d != drive[0] && Exists(fs, p))
                src = p;
        }
    }
    if (src.Length() == 0) {
        Log(fs, _L8("no copy of appuifwmodule.rsc found"), 0);
        fs.Close();
        return;
    }
    TFileName dir(drive);
    dir.Append(KRscDir);
    TInt err = fs.MkDirAll(dir);
    if (err != KErrAlreadyExists && err != KErrNone)
        Log(fs, _L8("mkdir error"), err);
    err = CopyFile(fs, src, target);
    if (err == KErrNone)
        Log(fs, _L8("copied appuifwmodule.rsc to the app drive, ok"), 0);
    else
        Log(fs, _L8("COPY FAILED (phone not unlocked?), error"), err);
    fs.Close();
}

GLDEF_C TInt E32Main()
{
    CTrapCleanup* cleanup = CTrapCleanup::New();
    Fix();
    delete cleanup;
    return 0;
}
