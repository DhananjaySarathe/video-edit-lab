"""Specific cutting, typography, color and framing exercises on original local footage."""
from functools import lru_cache

from PIL import Image, ImageDraw, ImageOps

from preview_common import ease, font, progress
from preview_hook_showcase_editing import CORAL, GOLD, INK, MINT, PAPER, PORTRAIT, WIDE, chip, words
from preview_plates import shot, source


def eye_crop(stamp, scale, lock=True, angle=0):
    # Native presenter source eye position in this short take, checked on the first and final frames.
    image = source('host-live', stamp)
    eye = 259, 69
    target = (144, 162) if lock else ((117, 118), (206, 198), (142, 151))[angle]
    ratio = .55 / scale
    l, top = eye[0] - target[0] * ratio, eye[1] - target[1] * ratio
    return image.transform(PORTRAIT, Image.Transform.EXTENT,
                           (l, top, l + 360 * ratio, top + 640 * ratio), Image.Resampling.BICUBIC)


def three_crops(t):
    index = min(2, int((t % .85) / .284))
    if t < .85:
        frame = eye_crop(.60 + t, (1, 1.21, 1.47)[index])
        line = 'Finished sequence'
    elif t < 2.15:
        index = min(2, int((t - .85) / .433))
        frame = eye_crop(.80, (1, 1.21, 1.47)[index], False, index)
        line = 'Unaligned crops'
    else:
        index = min(2, int((t - 2.15) / .86))
        frame = eye_crop(min(2.9, .59 + t - 2.15), (1, 1.21, 1.47)[index])
        line = 'Lock the eye position'
    draw = ImageDraw.Draw(frame)
    if t >= .85:
        draw.line((113, 162, 175, 162), fill=GOLD, width=2)
        draw.line((144, 131, 144, 193), fill=GOLD, width=2)
    chip(draw, (21, 503), line)
    return frame


def blocked_hand(t):
    # Keep one source interval on both passes; only the caption placement changes.
    replay = t >= 2.7
    at = min(2.6, .3 + (t - 2.7 if replay else t))
    frame = shot('camera-live', at, 1, 0, 0, PORTRAIT)
    draw = ImageDraw.Draw(frame)
    y = round(359 - 197 * ease(progress(t, .95, 1.4)))
    draw.rounded_rectangle((49, y - 22, 302, y + 23), 6, fill=INK)
    words(draw, (175, y), 'Turn this dial.', 31, PAPER, 'mm')
    chip(draw, (21, 504), 'Replay / same gesture' if replay else 'Move only the caption' if t >= .95 else 'The caption covers the hand')
    return frame


def caption_baseline(t):
    frame = shot('portrait-live', min(t % 2.7, 2.5), size=PORTRAIT)
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((13, 344, 337, 474), 8, fill=INK)
    fixed = t >= .95
    emphasis = ease(progress(t % 1.52, .06, .48)) * (1 - ease(progress(t % 1.52, .90, 1.35)))
    baseline = 430 if fixed else round(430 - 27 * emphasis)
    if fixed:
        draw.line((26, 431, 324, 431), fill=GOLD, width=1)
    token = 'word' if t < 4.2 else 'phrase'
    pieces = ((28, 'Keep', 26), (101, 'this', 26), (162, token, round(28 + 14 * emphasis)))
    for x, piece, size in pieces:
        draw.text((x, baseline), piece, font=font(size), anchor='ls', fill=GOLD if piece == token else PAPER)
    chip(draw, (21, 59), 'Fixed baseline' if fixed else 'Whole line shifts')
    return frame


def pointer_cue(t):
    frame = Image.new('RGB', PORTRAIT, '#e6eadf')
    draw = ImageDraw.Draw(frame)
    words(draw, (21, 80), 'Land the pointer', 33, INK)
    words(draw, (21, 118), 'on the control.', 33, INK)
    draw.rounded_rectangle((19, 174, 332, 441), 11, fill='#fdfcf5', outline='#bac8bb')
    words(draw, (36, 213), 'Export settings', 24, INK)
    draw.line((35, 240, 307, 240), fill='#c1cbbd')
    words(draw, (36, 281), 'Show captions', 21, INK, weight='regular')
    replay = t >= 2.7
    local = (t - 2.7) % 2.4 if replay else abs(t - .95) if t >= .95 else t
    timely = t >= .95
    hit = .64
    fraction = ease(progress(local, 0, hit))
    px = round(69 + 180 * fraction)
    py = round(390 - 109 * fraction)
    draw.rounded_rectangle((229, 265, 292, 297), 16, fill='#558e6a' if timely and local >= hit else '#9aa89b')
    cx = 274 if timely and local >= hit else 246
    draw.ellipse((cx - 11, 270, cx + 11, 292), fill=PAPER)
    onset = hit if timely else .02
    if onset <= local < onset + .42:
        radius = round(13 + 23 * progress(local, onset, onset + .42))
        draw.ellipse((249 - radius, 281 - radius, 249 + radius, 281 + radius), outline='#ac581b', width=3)
    draw.polygon(((px, py), (px + 3, py + 21), (px + 9, py + 14), (px + 18, py + 14)), fill=INK, outline=PAPER)
    chip(draw, (23, 490), 'Ring follows arrival' if timely else 'Ring fires too early')
    return frame


def units(t):
    frame = Image.new('RGB', PORTRAIT, '#f5f3e9')
    draw = ImageDraw.Draw(frame)
    fixed = t >= .95
    words(draw, (20, 80), 'Compare time', 36, INK)
    words(draw, (20, 123), 'in the same unit.', 30, INK)
    chip(draw, (19, 175), 'Illustrative timing data')
    for i, (name, val, amount) in enumerate((('Trial A', '30 s', 30), ('Trial B', '45 s' if fixed else '45,000 ms', 45))):
        y = 253 + 99 * i
        words(draw, (23, y), name, 20, INK)
        words(draw, (320, y), val, 21, INK, 'rm')
        width = round(amount / 60 * 287) if fixed or i == 0 else 287
        draw.rounded_rectangle((23, y + 19, 23 + width, y + 44), 5,
                               fill=('#55795c' if fixed or i == 0 else '#be7955'))
    words(draw, (23, 450), 'Shared scale: 0–60 seconds' if fixed else 'Separate units and scales', 17, INK)
    if t >= 2.7:
        chip(draw, (20, 505), '45,000 ms ÷ 1,000 = 45 s', INK, MINT, 18)
    return frame


@lru_cache(maxsize=1)
def map_source():
    m = Image.new('RGB', (400, 235), '#e7e9da')
    d = ImageDraw.Draw(m)
    for x in range(12, 398, 30):
        d.line((x, 0, x - 23, 234), fill='#fcfbf2', width=7)
    for y in range(9, 234, 25):
        d.line((0, y + 8, 399, y), fill='#fcfbf2', width=6)
    route = ((45, 173), (135, 173), (135, 79), (332, 79))
    d.line(route, fill='#2d674e', width=7, joint='curve')
    for i, (x, y) in enumerate(route[1:3], 1):
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=INK)
        words(d, (x, y), str(i), 14, PAPER, 'mm')
    for (x, y), label in ((route[0], 'FROM'), (route[-1], 'TO')):
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill='#a05136')
        words(d, (x, y + 19), label, 12, INK, 'mm')
    return m


def map_crop(t):
    frame = Image.new('RGB', PORTRAIT, INK)
    draw = ImageDraw.Draw(frame)
    words(draw, (19, 78), 'Can you spot', 31)
    words(draw, (19, 113), 'both turns?', 35, GOLD)
    for i, (bounds, name) in enumerate((((0, 108, 263, 224), 'A / close'), ((0, 22, 399, 218), 'B / whole route'))):
        top = 163 + 169 * i
        tile = map_source().transform((321, 141), Image.Transform.EXTENT, bounds, Image.Resampling.BICUBIC)
        frame.paste(tile, (19, top))
        chip(draw, (24, top + 7), name, INK, PAPER, 12)
    if t >= 2.55:
        chip(draw, (20, 509), 'Both turns fit in B', MINT, INK, 18)
    return frame


def neutral_balance(t):
    frame = Image.new('RGB', WIDE, INK)
    draw = ImageDraw.Draw(frame)
    tested = t >= 12.2
    words(draw, (20, 26), 'Measure the neutral before the grade', 24)
    for i, (cast, name) in enumerate(((False, 'Reference'), (True, 'Warmer angle'))):
        picture = shot('camera-live', min(2.5, t * .4), 1.0 + i * .14, 0, 0, (292, 205))
        pd = ImageDraw.Draw(picture)
        pd.rectangle((18, 150, 72, 189), fill=(128, 128, 128))
        if cast:
            red, green, blue = picture.split()
            picture = Image.merge('RGB', (red.point(lambda x: min(255, x + 16)), green, blue.point(lambda x: max(0, x - 18))))
        frame.paste(picture, (18 + 312 * i, 60))
        chip(draw, (23 + 312 * i, 66), name)
        if tested:
            rgb = picture.getpixel((43, 173))
            words(draw, (24 + 312 * i, 288), 'RGB ' + ' / '.join(map(str, rgb)), 18, MINT)
    words(draw, (19, 327), 'Simulated reference card in both angles. The lighting cast is applied to the pixels.', 14, PAPER, weight='regular')
    return frame


def locked_exposure(t):
    frame = Image.new('RGB', PORTRAIT, PAPER)
    draw = ImageDraw.Draw(frame)
    # Both copies decode the same source frame with identical transforms.
    base = shot('portrait-live', 1.05, size=(117, 190))
    neutral = ease(progress(t, 1.2, 2.8))
    shade = round(38 + 99 * neutral)
    for i, c in enumerate((shade, round(237 - 100 * neutral))):
        left = 15 + 168 * i
        draw.rectangle((left, 169, left + 160, 414), fill=(c, c, c))
        frame.paste(base, (left + 21, 192))
        if t >= 1.2:
            x, y = left + 21 + 62, 192 + 77
            draw.rectangle((x - 5, y - 5, x + 5, y + 5), outline=GOLD, width=2)
    words(draw, (20, 73), 'Did the face', 32, INK)
    words(draw, (20, 112), 'change exposure?', 31, INK)
    if t >= 2.8:
        rgb = base.getpixel((62, 77))
        chip(draw, (20, 466), 'Same RGB on both sides', INK, MINT, 17)
        words(draw, (20, 524), ' / '.join(str(x) for x in rgb), 24, INK)
    else:
        words(draw, (20, 493), 'Only the surround changes.', 21, INK)
    return frame


def thumb_comparison(t):
    frame = Image.new('RGB', WIDE, '#1a2a22')
    draw = ImageDraw.Draw(frame)
    words(draw, (18, 26), 'Find the clip with the dial at its edge.', 24)
    sources = ('cooking-live', 'camera-live', 'coffee-live')
    for row, label in enumerate(('Center crops', 'Full frame')):
        y = 52 + row * 128
        chip(draw, (17, y), label)
        for index, name in enumerate(sources):
            x = 162 + index * 151
            full = shot(name, 1.7, size=(138, 94))
            # An actual edge identifier lets viewers check the difference on both strips.
            if index == 1:
                ImageDraw.Draw(full).rectangle((118, 15, 135, 31), fill=GOLD)
                words(ImageDraw.Draw(full), (127, 23), 'D', 11, INK, 'mm')
            tile = ImageOps.fit(full.crop((24, 2, 114, 91)), (138, 94)) if row == 0 else full
            frame.paste(tile, (x, y))
            if t >= 6.1 and row == 1 and index == 1:
                draw.rectangle((x + 116, y + 13, x + 137, y + 34), outline=CORAL, width=2)
    words(draw, (18, 326), 'Same files and order.' if t < 14.8 else 'Test lookup time and correct selections under each view.', 19, MINT)
    return frame


SCENES = {
    'hook-short-proof-first-009': three_crops,
    'hook-short-specific-fix-011': blocked_hand,
    'hook-short-specific-fix-019': caption_baseline,
    'hook-short-specific-fix-033': pointer_cue,
    'hook-short-specific-fix-072': units,
    'hook-short-choice-live-085': map_crop,
    'hook-short-live-contradiction-018': locked_exposure,
    'hook-long-learning-promise-032': neutral_balance,
    'hook-long-head-to-head-026': thumb_comparison,
}

POSTERS = {'hook-short-proof-first-009': .44, 'hook-short-specific-fix-011': .44,
           'hook-short-specific-fix-019': .35, 'hook-short-specific-fix-033': .21}
