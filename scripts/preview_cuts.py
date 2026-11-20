"""Original illustrated demonstrations of cutting and pacing techniques."""

from functools import lru_cache
from math import cos, pi, sin

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from preview_common import H, W, backdrop, blend, ease, font, progress
from preview_typography import AMBER, LEAF, PAPER, TEAL, coffee, footage, person, set_plate


SKY = (236, 171, 126)
HILL = (47, 87, 79)
INK = (29, 47, 46)
MUTED = (110, 143, 125)
CLAY = (183, 105, 70)


def stage(t, start, end):
    return ease(progress(t, start, end))


def crop(im, scale, x=320, y=180):
    """Scale a picture while holding the point (x, y) at the same screen position."""
    return im.transform(
        (W, H), Image.Transform.AFFINE,
        (1 / scale, 0, x * (1 - 1 / scale), 0, 1 / scale, y * (1 - 1 / scale)),
        resample=Image.Resampling.BICUBIC,
    )


def text(d, x, y, value, size=13, color=PAPER, weight='bold', anchor='mm'):
    d.text((x, y), value, fill=color, font=font(size, weight), anchor=anchor)


def clip_track(im, t, cuts, *, pulses=False):
    """A narrow cue strip under the action marks the cut boundaries."""
    d = ImageDraw.Draw(im)
    y = 325
    d.rounded_rectangle((56, 310, 584, 341), radius=13, fill=(21, 38, 39))
    d.line((74, y, 566, y), fill=(92, 122, 109), width=1)
    for bound in cuts:
        x = round(74 + 492 * bound / 3.2)
        active = abs(t - bound) < .085 and pulses
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=AMBER if active else PAPER)
        if active:
            d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=AMBER)
    x = round(74 + 492 * min(t / 3.2, 1))
    d.line((x, y - 8, x, y + 8), fill=LEAF, width=2)


def room_with_mic(t):
    im = footage(t, x=345, theme='blue', eyes=137)
    d = ImageDraw.Draw(im)
    d.line((468, H, 432, 256, 414, 252), fill=(32, 36, 34), width=7, joint='curve')
    d.rounded_rectangle((395, 221, 432, 267), radius=15, fill=(31, 42, 45),
                        outline=(94, 118, 113), width=2)
    for yy in range(230, 246, 5):
        d.line((403, yy, 423, yy), fill=(113, 127, 112), width=1)
    return im


def slow_push(t):
    im = room_with_mic(t)
    amount = stage(t, .25, 2.37)
    if t >= 2.8:
        amount = 0
    return crop(im, 1 + .26 * amount, 345, 137)


def punch(t):
    im = room_with_mic(t)
    tight = .86 <= t < 2.07
    if tight:
        d = ImageDraw.Draw(im)
        d.arc((307, 129, 376, 183), 11, 52, fill=(115, 76, 65), width=2)
        return crop(im, 1.42, 345, 138)
    return im


@lru_cache(maxsize=8)
def hill_plate(theme):
    if theme == 'day':
        sky, distant, near = (226, 171, 131), (102, 134, 116), (53, 91, 78)
    elif theme == 'dusk':
        sky, distant, near = (166, 158, 151), (71, 99, 107), (33, 65, 70)
    else:
        sky, distant, near = (88, 109, 133), (48, 74, 96), (32, 51, 64)
    im = backdrop(sky, blend(sky, PAPER, .54))
    d = ImageDraw.Draw(im)
    d.ellipse((410, 53, 496, 139), fill=(245, 209, 159) if theme == 'day' else (216, 222, 205))
    d.polygon(((0, 202), (96, 158), (176, 164), (252, 134), (318, 159),
               (375, 140), (462, 185), (523, 156), (640, 194), (640, 360), (0, 360)),
              fill=distant)
    d.polygon(((0, 241), (88, 191), (158, 193), (234, 204), (323, 181),
               (401, 218), (501, 174), (640, 232), (640, 360), (0, 360)),
              fill=near)
    d.polygon(((0, 289), (178, 275), (367, 255), (640, 249), (640, 360), (0, 360)),
              fill=blend(near, INK, .82))
    d.line((0, 283, 178, 269, 367, 249, 640, 243), fill=blend(distant, PAPER, .2), width=2)
    grasses = (21, 46, 49) if theme != 'day' else (37, 67, 59)
    for x in range(0, 650, 21):
        y = 300 - x // 19 + (x % 39) // 3
        d.line((x, y, x - 7, y - 9, x - 11, y - 12), fill=grasses, width=2)
        d.line((x, y, x + 4, y - 14, x + 9, y - 17), fill=grasses, width=2)
    return im


def bicycle(d, x, y, s=1, angle=0, jacket=AMBER):
    def pt(a, b):
        return (x + a * s, y + b * s)

    def line(points, color, size=3):
        d.line([pt(a, b) for a, b in points], fill=color, width=max(1, round(size * s)),
               joint='curve')

    def circle(a, b, r, color=None, outline=None, width=2):
        d.ellipse((*pt(a - r, b - r), *pt(a + r, b + r)), fill=color, outline=outline,
                  width=max(1, int(width * s)))

    for center in (-34, 32):
        circle(center, 0, 24, outline=INK, width=4)
        circle(center, 0, 21, outline=(208, 213, 187), width=1)
        for i in range(8):
            a = angle + i * pi / 4
            line(((center, 0), (center + 20 * cos(a), 20 * sin(a))), (135, 166, 148), 1)
        circle(center, 0, 3, AMBER)
    line(((-34, 0), (-17, -34), (4, -5), (19, -36), (-17, -34), (4, -5), (-34, 0)),
         (220, 218, 179), 3)
    line(((32, 0), (19, -36), (15, -46), (26, -49)), PAPER, 3)
    line(((-24, -39), (-10, -39)), INK, 4)
    line(((-15, -44), (1, -21), (-3 + 10 * cos(angle), -7 + 10 * sin(angle))), BLUE_SHADOW, 7)
    line(((-15, -44), (-7, -21), (10 - 10 * cos(angle), -7 - 10 * sin(angle))), (65, 103, 101), 6)
    line(((-15, -44), (-8, -68), (5, -73)), jacket, 12)
    line(((1, -67), (11, -55), (24, -48)), jacket, 6)
    circle(9, -76, 8, (176, 123, 91))
    d.pieslice((*pt(.3, -89), *pt(18, -71)), 175, 356, fill=INK)
    line(((15, -76), (20, -76)), (182, 210, 158), 2)


BLUE_SHADOW = (45, 75, 87)


def direction_flow(t):
    first = t < 1.5
    im = hill_plate('day' if first else 'dusk').copy()
    d = ImageDraw.Draw(im)
    if first:
        for x in (20, 120, 530):
            d.rectangle((x, 142, x + 3, 279 - x // 22), fill=(89, 104, 80))
        d.line((0, 155, 165, 166, 365, 167, 640, 157), fill=(110, 120, 92))
    else:
        for x, h in ((85, 39), (142, 50), (189, 42), (240, 33)):
            y = 174 - h
            d.rectangle((x, y, x + 27, 191), fill=(59, 87, 92))
            d.rectangle((x + 9, y + 11, x + 15, y + 16), fill=(224, 188, 123))
    x = 30 + 190 * t
    bicycle(d, x, 260 - x * .052, 1.23 if first else 1.18, t * 9, AMBER)
    return im


@lru_cache(maxsize=2)
def countertop(theme='studio'):
    top, low = ((137, 112, 85), (80, 65, 52)) if theme == 'studio' else ((59, 92, 87), (27, 55, 56))
    im = backdrop(top, low)
    d = ImageDraw.Draw(im)
    d.polygon(((0, 196), (640, 172), (640, 360), (0, 360)), fill=blend(low, (109, 76, 55), .68))
    d.line((0, 196, 640, 172), fill=blend(top, PAPER, .22), width=3)
    for rough in range(5):
        y = 237 + rough * 28
        d.line((0, y, 640, y - 24), fill=blend(low, PAPER, .13), width=1)
    d.rounded_rectangle((470, 57, 574, 172), radius=24, fill=blend(top, low, .31))
    d.line((521, 59, 521, 171), fill=blend(top, PAPER, .28), width=2)
    return im


def mug(d, x, y, size=1, body=(192, 197, 159)):
    def frame(a, b, c, e):
        return (x + a * size, y + b * size, x + c * size, y + e * size)
    d.ellipse(frame(-44, 32, 57, 48), fill=(64, 54, 41))
    d.ellipse(frame(24, -26, 60, 12), fill=body)
    d.ellipse(frame(30, -20, 52, 7), fill=(69, 61, 44))
    d.rounded_rectangle(frame(-35, -41, 35, 37), radius=max(2, round(14 * size)), fill=body)
    d.ellipse(frame(-35, -48, 35, -25), fill=PAPER, outline=body, width=2)
    d.ellipse(frame(-28, -45, 28, -28), fill=(125, 82, 53))
    d.arc(frame(-30, -18, 21, 34), 87, 214, fill=blend(body, PAPER, .5),
          width=max(1, round(3 * size)))


def action_cut(t):
    im = countertop().copy()
    d = ImageDraw.Draw(im)
    fraction = stage(t, .33, 2.1)
    y = 79 + 163 * fraction
    if fraction < .997:
        d.polygon(((0, y - 20), (240, y - 45), (316, y - 36), (337, y - 23),
                   (321, y - 5), (293, y + 1), (0, y + 15)), fill=(191, 136, 101))
        d.polygon(((0, y - 16), (215, y - 30), (224, y + 11), (0, y + 19)), fill=(101, 139, 116))
    else:
        retreat = stage(t, 2.09, 2.74)
        e = 220 * retreat
        d.polygon(((0, y - 20 - e * .17), (240 - e, y - 45 - e * .35),
                   (316 - e, y - 36 - e * .6), (337 - e, y - 23 - e * .54),
                   (298 - e, y - 10 - e * .54), (0, y + 15 - e * .35)), fill=(191, 136, 101))
    mug(d, 353, y, 1.06)
    return crop(im, 1.54, 352, 187) if t >= 1.19 else im


@lru_cache(maxsize=2)
def ocean_sun():
    im = backdrop((163, 125, 119), (231, 174, 110))
    d = ImageDraw.Draw(im)
    d.ellipse((258, 114, 382, 238), fill=(252, 207, 135))
    d.rectangle((0, 244, 640, 360), fill=(55, 79, 78))
    for i in range(10):
        x = 14 + 24 * i
        d.line((x, 258 + 9 * i, x + 176 + i * 14, 258 + 9 * i),
               fill=blend((55, 79, 78), (162, 154, 115), 1 - .064 * i), width=2)
    return im


def cup_overhead(t):
    im = backdrop((135, 106, 79), (69, 62, 58))
    d = ImageDraw.Draw(im)
    for i in range(8):
        d.line((0, i * 53 + 15, 640, i * 53 - 60), fill=(112, 89, 68), width=2)
    d.ellipse((251, 114, 396, 255), fill=(61, 47, 40))
    d.ellipse((256, 111, 382, 241), fill=(228, 186, 121), outline=PAPER, width=4)
    d.ellipse((268, 125, 371, 228), fill=(154, 101, 59))
    d.ellipse((375, 153, 414, 192), fill=(228, 186, 121))
    d.ellipse((381, 160, 407, 185), fill=(108, 87, 66))
    reveal = stage(t, 1.34, 2.03)
    for i in range(6):
        y = 151 + i * 9
        w = max(1, (32 - 3 * i) * reveal)
        d.ellipse((320 - w, y, 320 + w, y + 13), fill=(231, 194, 124))
    if reveal > .08:
        d.line((320, 148, 319, 211), fill=(240, 215, 155), width=2)
    return im


def visual_match(t):
    if t < 1.36:
        return ocean_sun().copy()
    return cup_overhead(t)


def smash(t):
    if t < .37:
        return crop(coffee(t), 1.28, 300, 172)
    if t < .74:
        return crop(coffee(t - .37, detail=True), 1.3, 388, 192)
    if t < 1.07:
        im = hill_plate('day').copy()
        bicycle(ImageDraw.Draw(im), 350 + 262 * (t - .74), 257, 2.15, t * 18, AMBER)
        return im
    im = hill_plate('night').copy()
    d = ImageDraw.Draw(im)
    d.line((0, 264, 640, 251), fill=(35, 58, 71), width=5)
    d.ellipse((224, 264, 389, 276), fill=(24, 42, 48))
    d.polygon(((291, 269), (295, 201), (303, 185), (328, 186), (339, 219), (341, 268)),
              fill=(37, 58, 67))
    d.ellipse((301, 163, 328, 196), fill=(68, 91, 92))
    return im


def plant_state(t, count):
    im = countertop('green').copy()
    d = ImageDraw.Draw(im)
    d.ellipse((240, 298, 400, 315), fill=(57, 50, 43))
    d.polygon(((278, 242), (365, 242), (355, 299), (291, 299)), fill=CLAY)
    d.ellipse((274, 224, 370, 256), fill=(104, 84, 66), outline=(216, 149, 108), width=5)
    if count:
        d.line((324, 236, 319, 139, 323, 80 if count > 2 else 138),
               fill=(128, 159, 98), width=5)
        leaves = [
            (283, 170, 320, 194, (166, 184, 113)),
            (320, 154, 364, 181, (107, 151, 98)),
            (292, 120, 323, 138, (196, 207, 132)),
            (320, 90, 366, 120, (137, 163, 100)),
            (295, 71, 326, 99, (204, 212, 129)),
        ]
        for x0, y0, x1, y1, tone in leaves[:count]:
            d.ellipse((x0, y0 + 2 * sin(t * 4), x1, y1), fill=tone)
            d.line((x0 + 4, y1 - 5, x1 - 6, y0 + 8), fill=blend(tone, INK, .34))
    else:
        d.ellipse((317, 231, 330, 240), fill=(215, 188, 133))
    return im


def jump(t):
    cuts = (.72, 1.46, 2.05)
    state = sum(t >= cut for cut in cuts)
    im = plant_state(t, (0, 1, 3, 5)[state])
    clip_track(im, t, cuts)
    return im


def variable(t):
    cuts = (.28, .54, .86, 1.12)
    shot = sum(t >= cut for cut in cuts)
    if shot == 0:
        im = countertop().copy()
        mug(ImageDraw.Draw(im), 320, 232, 1.35, (216, 182, 143))
    elif shot == 1:
        im = crop(coffee(t * 2, detail=True), 1.15, 382, 183)
    elif shot == 2:
        im = crop(plant_state(t, 5), 1.44, 310, 154)
    elif shot == 3:
        im = crop(coffee(t), 1.23, 320, 174)
    else:
        im = footage(t, x=335, theme='amber')
    clip_track(im, t, cuts)
    return im


def beat(t):
    beats = (.42, .96, 1.5, 2.04, 2.58)
    shot = sum(t >= cut for cut in beats)
    im = room_with_mic(t)
    im = crop(im, (1, 1.21, 1.04, 1.36, 1.13, 1.22)[shot], 345, 137)
    clip_track(im, t, beats, pulses=True)
    return im


def monochrome(t):
    if .74 <= t < 2.03:
        im = ImageOps.colorize(ImageOps.grayscale(coffee(t, detail=True)), (29, 38, 40), (239, 237, 222))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((36, 30, 117, 59), radius=12, fill=(35, 45, 45))
        text(d, 76, 45, 'Earlier', size=15)
        return im
    return footage(t, x=330, theme='amber')


def diagonal(t):
    im = hill_plate('day').copy()
    night = hill_plate('night').copy()
    origin = -290 + stage(t, .54, 2.34) * 1080
    mask = Image.new('L', (W, H))
    md = ImageDraw.Draw(mask)
    md.polygon(((-300, -30), (round(origin + 162), -30),
                (round(origin - 171), 390), (-300, 390)), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3.2))
    im.paste(night, (0, 0), mask)
    return im


def cutout_zoom(t):
    old = set_plate('amber').copy()
    new = hill_plate('dusk').copy()
    switch = stage(t, 1.08, 1.57)
    expand = stage(t, .8, 1.37) - .73 * stage(t, 1.49, 2.19)
    retreat = stage(t, 2.08, 2.78)
    base_y = 142 - 27 * expand
    x = 321 + 9 * sin(t * 2.3)
    im = Image.blend(old, new, switch)
    if .77 < t < 1.95:
        person(im, x, base_y, 1.07 + 2.26 * expand, outline=True)
    else:
        person(im, x, base_y + 8 * retreat, 1.07 + 2.26 * expand)
    return im


@lru_cache(maxsize=2)
def doorway(inside):
    if inside:
        im = backdrop((69, 107, 103), (32, 57, 59))
        d = ImageDraw.Draw(im)
        d.polygon(((0, 360), (640, 360), (486, 261), (165, 261)), fill=(92, 97, 77))
        d.polygon(((0, 25), (0, 360), (165, 261), (165, 55)), fill=(64, 91, 77))
        d.polygon(((640, 25), (640, 360), (486, 261), (486, 55)), fill=(49, 82, 77))
        d.rounded_rectangle((219, 71, 424, 248), radius=61, fill=(91, 134, 123),
                            outline=(141, 165, 139), width=3)
        d.rounded_rectangle((230, 82, 413, 239), radius=49, fill=(141, 173, 151))
        d.line((321, 82, 321, 238), fill=(86, 123, 110), width=3)
        d.line((232, 158, 412, 158), fill=(86, 123, 110), width=3)
        d.polygon(((230, 212), (271, 169), (308, 210), (346, 164), (410, 210), (410, 228), (230, 221)),
                  fill=(96, 143, 126))
        return im
    im = hill_plate('day').copy()
    d = ImageDraw.Draw(im)
    d.polygon(((140, 288), (140, 124), (322, 46), (509, 124), (509, 282)), fill=(167, 137, 96))
    d.polygon(((115, 137), (322, 32), (532, 136), (505, 155), (322, 62), (140, 153)),
              fill=(84, 77, 60))
    for x, y in ((177, 165), (438, 160)):
        d.rounded_rectangle((x, y, x + 38, y + 53), 4, fill=(62, 79, 66),
                            outline=(206, 177, 123), width=3)
        d.line((x + 19, y + 2, x + 19, y + 52), fill=(178, 161, 116), width=2)
    d.rounded_rectangle((269, 131, 371, 284), radius=38, fill=(43, 68, 61))
    d.polygon(((274, 282), (367, 281), (425, 360), (231, 360)), fill=(174, 144, 106))
    return im


def inward(t):
    if t < 1.58:
        zoom = 1 + .98 * stage(t, 1.08, 1.58)
        return crop(doorway(False), zoom, 320, 218)
    zoom = 1 + .5 * (1 - stage(t, 1.58, 2.11))
    return crop(doorway(True), zoom, 320, 161)


def speed_ramp(t):
    im = hill_plate('dusk').copy()
    d = ImageDraw.Draw(im)
    first = stage(t, .02, 1.22)
    center = progress(t, .80, 2.24)
    exit_amount = stage(t, 1.98, 3.08)
    x = -62 + 305 * first + 109 * center + 350 * exit_amount
    bicycle(d, x, 266 - x * .043, 1.72, x * .072, AMBER)
    if 1.23 < t < 2.0:
        activity = stage(t, 1.23, 1.43) * (1 - stage(t, 1.86, 2.0))
        for sy in (127, 156):
            length = max(1, 28 * activity)
            d.line((x - 95 - length, sy, x - 95, sy),
                   fill=blend((64, 98, 99), LEAF, activity * .65), width=2)
    return im


SCENES = {
    'slow-push-in': slow_push,
    'punch-in': punch,
    'motion-flow-cut': direction_flow,
    'cut-on-action': action_cut,
    'visual-match-cut': visual_match,
    'smash-cut': smash,
    'intentional-jump-cut': jump,
    'variable-pacing': variable,
    'beat-synced-cuts': beat,
    'monochrome-flashback': monochrome,
    'diagonal-mask-wipe': diagonal,
    'cutout-match-zoom': cutout_zoom,
    'pull-in-transition': inward,
    'speed-ramp': speed_ramp,
}
