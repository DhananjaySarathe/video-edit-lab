"""Original full-frame 9:16 previews composed from licensed footage and graphics."""

from array import array
from bisect import bisect_right
from functools import lru_cache
from math import sin
from random import Random
import sys
import wave

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from preview_common import ease, font, progress
from preview_live_action import type_at
from preview_phone import device
from preview_plates import shot, source
from preview_sound import LENGTH, RATE, bed, impact, window
from preview_spatial import solve, warp


SIZE = 360, 640
W, H = SIZE
INK = '#171b20'
PAPER = '#fff8ec'
GOLD = '#ffda69'
PINK = '#ffb7c5'
MINT = '#aef0cf'
HYPER_CUTS = (.40, .72, .97, 1.23, 1.46, 1.76, 2.04)
HYPER_SHOTS = (
    (2.88, .25, 1.10, -61, 12),
    (.16, .92, 1.48, -101, -96),
    (.44, 1.06, 1.71, -76, -23),
    (.71, 1.12, 1.53, -65, 49),
    (1.05, 1.17, 1.88, -66, 73),
    (1.44, 1.12, 1.16, -69, 42),
    (1.94, 1.35, 1.75, -75, 65),
    (2.52, .63, 1.20, -71, 40),
)


def portrait(name, stamp=0, zoom=1, x=0, y=0):
    return shot(name, stamp, zoom, x, y, SIZE)


def sub(frame, text, center=180, y=526, size=34, fill=PAPER):
    type_at(frame, (center, y), text, size, fill, stroke=3)


def role_name(frame, text, x, y, fill):
    draw = ImageDraw.Draw(frame)
    width = draw.textlength(text, font=font(15)) + 20
    draw.rounded_rectangle((x - width / 2, y - 14, x + width / 2, y + 14), 4, fill=INK)
    type_at(frame, (x, y), text, 15, fill)


@lru_cache(maxsize=1)
def studio():
    frame = portrait('room', zoom=1.09, x=17)
    frame = ImageEnhance.Brightness(frame).enhance(.72)
    return frame.filter(ImageFilter.GaussianBlur(1.6))


def actor(frame, stamp, at, height, mirrored=False):
    extent = (133, 0, 421, 360)
    dimensions = round(height * (extent[2] - extent[0]) / extent[3]), height
    picture = source('host-live', stamp).crop(extent)
    matte = source('host-live-matte', stamp).crop(extent)
    if mirrored:
        picture, matte = ImageOps.mirror(picture), ImageOps.mirror(matte)
        red, green, _ = picture.split()
        jacket = ImageChops.subtract(green, red).point(lambda value: min(255, 3 * value))
        magenta = ImageOps.colorize(picture.convert('L'), '#322038', '#ffb6ca')
        picture.paste(magenta, (0, 0), jacket)
    picture = picture.resize(dimensions, Image.Resampling.LANCZOS)
    matte = matte.resize(dimensions, Image.Resampling.LANCZOS)
    frame.paste(picture, at, matte)


def clone_split(t):
    frame = studio().copy()
    actor(frame, 2.1 + .30 * t, (92, 216), 450, mirrored=True)
    actor(frame, .26 + .62 * t, (-79, 219), 450)

    type_at(frame, (180, 101), 'ME vs. ME', 53, PAPER, stroke=2)
    role_name(frame, 'CREATOR', 89, 203, MINT)
    role_name(frame, 'EDITOR', 270, 203, PINK)
    if t < 1.04:
        sub(frame, 'MORE CUTS?', 94, 536, 22, MINT)
    elif t < 2.29:
        sub(frame, 'LET IT LAND.', 260, 536, 22, PINK)
    else:
        sub(frame, '…FAIR.', 92, 536, 24, MINT)
    return frame


def role_reverse(t):
    reverse = .79 <= t < 2.57
    if reverse:
        left = portrait('host-live', .66 + (t - .79) * .76, 1.18, -60, -37)
        frame = ImageOps.mirror(left)
        warm = ImageOps.colorize(frame.convert('L'), '#38243c', '#ffdbc8')
        frame = Image.blend(frame, warm, .34)
    else:
        frame = portrait('host-live', t + .13, 1.09, -59, -27)
    role_name(frame, 'EDITOR' if reverse else 'CREATOR', 279 if reverse else 74, 48,
              PINK if reverse else MINT)

    if t < .94:
        sub(frame, 'Can you cut faster?', y=527, size=29)
    elif 1.34 <= t < 2.57:
        sub(frame, 'Show me the result.', y=527, size=29, fill=PINK)
    elif t >= 2.57:
        sub(frame, 'Oh.', y=527, size=35, fill=MINT)
    return frame


def hyperedit(t):
    index = bisect_right(HYPER_CUTS, t)
    phase = t - (0, *HYPER_CUTS)[index]
    stamp, speed, scale, x, y = HYPER_SHOTS[index]
    frame = portrait('coffee-live', stamp + phase * speed, scale, x, y)
    if index == 0:
        sub(frame, 'THE SWIRL', y=518, size=42, fill=GOLD)
    elif index == len(HYPER_CUTS):
        sub(frame, 'ONE CLEAN POUR', y=526, size=31, fill=GOLD)
    return frame


def hyper_audio(path):
    rng = Random(57)
    slow_noise = 0.0
    samples = array('h')
    for index in range(round(RATE * LENGTH)):
        t = index / RATE
        noise = rng.uniform(-1, 1)
        slow_noise = .76 * slow_noise + .24 * noise
        stream = window(t, .55, 1.82, .20) * (.12 * abs(sin(t * 28)) + .05)
        liquid = stream * (slow_noise + .28 * noise)
        tap = .18 * impact(t, .97, 19, 242) + .21 * impact(t, 2.04, 13, 109)
        texture = .058 * impact(t, .40, 27, 348) + .069 * impact(t, 1.46, 24, 396)
        score = .12 * bed(t, shift=2, pace=.245)
        gain = 1 - ease(progress(t, LENGTH - .29, LENGTH))
        samples.append(round(32767 * (score + liquid + tap + texture) * gain))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as output:
        output.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(samples.tobytes())


def match_loop(t):
    if t < .65 or t >= 2.40:
        stamp = .8 + t if t < .65 else t - 2.40
        frame = portrait('coffee-live', stamp, 1.08, -79, 20)
        if .16 <= t < .65:
            sub(frame, 'Will it hold?', y=525, size=37)
        return frame

    if t < 1.25:
        return portrait('coffee-live', 1.68 + (t - .65) * .83, 1.39, -65, 47)

    frame = portrait('coffee-live', 2.59 + (t - 1.25) * .52, 1.12, -79, 26)
    sub(frame, 'It held.', y=525, size=38, fill=GOLD)
    return frame


def extent_at(cx, top, height, ratio):
    width = height * ratio
    return cx - width / 2, top, cx + width / 2, top + height


def blend_pane(raw, outer, inner, blend):
    coordinates = tuple(a + (b - a) * blend for a, b in zip(outer, inner))
    return raw.transform((W, H // 2), Image.Transform.EXTENT, coordinates, Image.Resampling.BICUBIC)


def hidden_seam(t):
    raw = source('walk-live', .31 + t * .88)
    amount = ease(progress(t, .30, 1.44))
    cx = 309 + 13 * sin(t * .82)
    final = extent_at(cx, 21, 332, W / H)
    if amount == 1:
        return raw.transform(SIZE, Image.Transform.EXTENT, final, Image.Resampling.BICUBIC)

    ratio = W / (H // 2)
    top = blend_pane(raw, extent_at(cx, 23, 247, ratio), extent_at(cx, 21, 166, ratio), amount)
    bottom = blend_pane(raw, extent_at(cx + 28, 228, 129, ratio), extent_at(cx, 187, 166, ratio), amount)
    frame = Image.new('RGB', SIZE)
    frame.paste(top, (0, 0))
    frame.paste(bottom, (0, H // 2))
    opacity = round(220 * (1 - progress(t, 1.22, 1.44)))
    ImageDraw.Draw(frame, 'RGBA').line((0, H // 2, W, H // 2), fill=(255, 238, 200, opacity), width=3)
    return frame


def cut_from_quad(image, quad):
    equations, target = [], []
    for (x, y), (u, v) in zip(((0, 0), (W, 0), (W, H), (0, H)), quad):
        equations += [[x, y, 1, 0, 0, 0, -x * u, -y * u], [0, 0, 0, x, y, 1, -x * v, -y * v]]
        target += [u, v]
    return image.transform(SIZE, Image.Transform.PERSPECTIVE, solve(equations, target), Image.Resampling.BICUBIC)


def screen_world(t):
    arrival = 1.45
    destination = portrait('walk-live', .19 + .84 * t, 1.04, 19, 23)
    if t >= arrival:
        return destination

    phone, tracked = device(.22 + t * .61, destination.convert('RGBA'))
    cx = sum(x for x, _ in tracked) / len(tracked)
    half = 360 * W / H / 2
    outside = ((cx - half, 0), (cx + half, 0), (cx + half, 360), (cx - half, 360))
    push = ease(progress(t, .32, arrival))
    # Clear the bezel by the final sampled transition frame.
    if t >= 1.4:
        push = 1
    quad = [tuple(a + (b - a) * push for a, b in zip(start, end))
            for start, end in zip(outside, tracked)]
    return cut_from_quad(phone, quad)


def render_chart(t):
    panel = Image.new('RGBA', (274, 198))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((1, 1, 272, 196), 8, fill=(19, 36, 37, 241),
                           outline='#9cd3b3', width=2)
    type_at(panel, (14, 24), 'Render time', 24, PAPER, 'lm')
    type_at(panel, (14, 51), 'Example · seconds', 15, MINT, 'lm')
    for y, value in ((72, '8'), (102, '6'), (132, '4')):
        type_at(panel, (23, y), value, 13, '#d8e9e0')
        draw.line((36, y, 251, y), fill='#5f8176', width=1)

    points = ((46, 72), (97, 94), (145, 106), (207, 129))
    amount = ease(progress(t, .87, 1.55))
    if amount:
        segment = min(amount * (len(points) - 1), len(points) - 1.001)
        index = int(segment)
        mix = segment - index
        point = tuple(a + (b - a) * mix for a, b in zip(points[index], points[index + 1]))
        draw.line([*points[:index + 1], point], fill=MINT, width=4, joint='curve')

    if t >= 1.55:
        x, y = points[-1]
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=GOLD)
        type_at(panel, (x + 13, y - 16), '4.2 s', 23, GOLD, 'rm')
    type_at(panel, (46, 148), 'Run 1', 13, MINT)
    type_at(panel, (207, 148), 'Run 4', 13, MINT)
    draw.line((14, 161, 260, 161), fill='#5f8176', width=1)
    if t >= 2.39:
        type_at(panel, (14, 174), 'Cause unverified', 18, GOLD, 'lm')
    return panel


def anchored_answer(t):
    frame = studio().copy()
    appear = ease(progress(t, .35, .85))
    if appear:
        span = 266 * appear
        quad = ((65, 78), (65 + span, 78 - 17 * appear),
                (69 + span, 282 - 19 * appear), (69, 282))
        warp(frame, render_chart(t), quad)
    actor(frame, .65 + t * .8, (-31, 273), 377)
    zoom = 1 + .048 * ease(progress(t, 0, LENGTH))
    frame = frame.transform(SIZE, Image.Transform.EXTENT, extent_at(181, 5 * (zoom - 1), H / zoom, W / H),
                            Image.Resampling.BICUBIC)
    if t < .35:
        sub(frame, 'How much faster?', y=533, size=31)
    elif t < 1.55:
        sub(frame, 'Render time', y=533, size=35, fill=MINT)
    elif t < 2.39:
        sub(frame, '4.2 seconds', y=533, size=38, fill=GOLD)
    else:
        sub(frame, 'What changed?', y=533, size=33)
    return frame


SCENES = {
    'short-clone-split': clone_split,
    'short-role-reverse': role_reverse,
    'short-hyperedit': hyperedit,
    'short-match-loop': match_loop,
    'advanced-hidden-seam': hidden_seam,
    'short-screen-world': screen_world,
    'advanced-anchored-answer': anchored_answer,
}
AUDIO = {'short-hyperedit': hyper_audio}
