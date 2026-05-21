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


def analogous(val, d=100):
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


def create_range(clr, margin=10):
    r, g, b = int(clr[0]), int(clr[1]), int(clr[2])
    return (
        set(range(r - margin, r + margin)),
        set(range(g - margin, g + margin)),
        set(range(b - margin, b + margin)),
    )


def check_color_range(clr, r_range, g_range, b_range):
    """Returns True if clr falls within any of the given RGB ranges."""
    return (
        int(clr[0]) in r_range or
        int(clr[1]) in g_range or
        int(clr[2]) in b_range
    )
