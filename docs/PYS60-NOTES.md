# PyS60 1.4.5 UI and runtime patterns that worked (Nokia N79)

Found while writing RetroTele (a large Canvas-drawn UI), RetroSend and RetroTorch. For sockets in depth
see [RetroSend's PYS60-NOTES.md](https://github.com/manojanasuri16/RetroSend/blob/main/docs/PYS60-NOTES.md).

## Sockets and the main loop

- Use sockets **only on the main thread** with the callback forms (`connect/recv/send(..., cb)` on the raw `e32socket` object,
  `e32.Ao_timer` for timers, `e32.Ao_lock().wait()` as the loop). A socket call in a background thread freezes the app.
- **Never `close()` a socket while the app runs**: `close()` also stops the network connection for every socket. Use `shutdown(2)` and
  drop the reference; `close()` only on exit (RetroTele's `PhoneConn.close` vs `hard_close`).
- **Exit cleanly:** cancel all `Ao_timer`s and close the sockets with pending reads when the app exits; a socket with a pending read
  kept RetroTele on a **white screen** instead of closing.
- Ask for the access point once and reuse it (`socket.select_access_point()` once, `set_default_access_point`).

## Drawing

- Draw into an off-screen `graphics.Image` and `canvas.blit` it in the redraw callback; do the drawing inside `try/except` and
  paint an error banner plus log the traceback instead of letting an exception leave a blank/white canvas.
- PyS60 drawing functions accept **only plain ints** as coordinates: wrap the image (`examples/safedraw.py`).
- Cache fonts and measure text with `measure_text`; log paints slower than ~0.4 s.
- A canvas-drawn UI lets you build your own list views and look; PC previews of the screens (a fake `appuifw`/`graphics`) catch most
  mistakes before you build a `.sis`.

## Diagnostics

- A start-up crash closes the app silently. Wrap the entry point, write a timestamped log (`E:\<app>_log.txt`, fall back to
  `C:\Data\`) from the first line, show Python tracebacks on screen, and log a heartbeat to tell a freeze from a crash.
- Keep an on-phone log of every risky native call *before* it runs (the last line identifies the hang).

## Packaging and installs

- Memory card installs need `rscfix` (see the README) and an unlocked phone.
- A binary's UID/SID must be unique across everything on the phone; otherwise the installer says only "Unable to install".
- Capabilities beyond the user-grantable set (MultimediaDD, ReadDeviceData, WriteDeviceData, AllFiles, ...) require an unlocked phone;
  a `.pyd` loaded by the Python process must not require more capabilities than the process has.
- Version every release and keep old installers and logs off the card's root (the author's layout: `E:\Install\`, `E:\Others\old-logs\`).
