import colorsys


def complementary(val):
    r, g, b = map(lambda x: x / 255.0, val)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    color_180 = list(map(lambda x: round(x * 255), colorsys.hls_to_rgb(h + 180.0 / 360.0, l, s)))
    return [color_180]


def split_complementary(val):
    r, g, b = map(lambda x: x / 255.0, val)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    c150 = list(map(lambda x: round(x * 255), colorsys.hls_to_rgb(h + 150.0 / 360.0, l, s)))
    c210 = list(map(lambda x: round(x * 255), colorsys.hls_to_rgb(h + 210.0 / 360.0, l, s)))
    return [c150, c210]


def analogous(val, d=30):
    step = d / 360.0
    r, g, b = map(lambda x: x / 255.0, val)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return [
        list(map(lambda x: round(x * 255), colorsys.hls_to_rgb((h - step) % 1, l, s))),
        list(map(lambda x: round(x * 255), colorsys.hls_to_rgb((h + step) % 1, l, s))),
    ]


def triadic(val):
    r, g, b = map(lambda x: x / 255.0, val)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    c120 = list(map(lambda x: round(x * 255), colorsys.hls_to_rgb(h + 120.0 / 360.0, l, s)))
    c240 = list(map(lambda x: round(x * 255), colorsys.hls_to_rgb(h + 240.0 / 360.0, l, s)))
    return [c120, c240]


def tetradic(val):
    r, g, b = map(lambda x: x / 255.0, val)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    c60  = list(map(lambda x: round(x * 255), colorsys.hls_to_rgb(h + 60.0  / 360.0, l, s)))
    c180 = list(map(lambda x: round(x * 255), colorsys.hls_to_rgb(h + 180.0 / 360.0, l, s)))
    c240 = list(map(lambda x: round(x * 255), colorsys.hls_to_rgb(h + 240.0 / 360.0, l, s)))
    return [c60, c180, c240]


HARMONY_FUNCTIONS = [complementary, split_complementary, analogous, triadic, tetradic]


def _hue_deg(rgb):
    h, _, _ = colorsys.rgb_to_hls(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    return h * 360


def _hue_dist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def is_hue_match(clr, candidate, tol=20):
    """Returns True if clr's hue is within tol degrees of candidate's hue."""
    return _hue_dist(_hue_deg(clr), _hue_deg(candidate)) <= tol
