# SafeDraw: wrap a PyS60 graphics.Image so every coordinate is converted to a plain int.
# PyS60 1.4.5 drawing functions only accept plain ints as coordinates, while the phone hands out
# longs (durations, file sizes, big ids). Extracted unchanged from RetroTele's tgui.py; runs on
# the phone (wrap the Image you draw into: g = SafeDraw(graphics.Image.new((w, h)))).

def _ints(c):
    out = []
    for v in c:
        if type(v) is type(()) or type(v) is type([]):
            out.append(tuple(_ints(v)))
        else:
            out.append(int(v))
    return out


class SafeDraw:
    """Wraps an Image: PyS60 only accepts plain ints as coordinates, while
    the phone hands out longs (durations, file sizes, big ids)."""
    def __init__(self, img):
        self.img = img
        self.size = img.size

    def clear(self, *a, **k):
        return self.img.clear(*a, **k)

    def text(self, xy, t, **k):
        return self.img.text(tuple(_ints(xy)), t, **k)

    def measure_text(self, *a, **k):
        return self.img.measure_text(*a, **k)

    def rectangle(self, c, **k):
        return self.img.rectangle(tuple(_ints(c)), **k)

    def ellipse(self, c, **k):
        return self.img.ellipse(tuple(_ints(c)), **k)

    def line(self, c, **k):
        return self.img.line(tuple(_ints(c)), **k)

    def polygon(self, c, **k):
        return self.img.polygon(_ints(c), **k)

    def blit(self, img, **k):
        if k.has_key("target"):
            k["target"] = tuple(_ints(k["target"]))
        if k.has_key("source"):
            k["source"] = tuple(_ints(k["source"]))
        return self.img.blit(img, **k)
