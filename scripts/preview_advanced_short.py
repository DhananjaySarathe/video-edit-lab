"""Original picture-first examples of four short-form editing decisions."""
from functools import lru_cache

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from preview_common import H, W, ease, font, progress
from preview_live_action import GOLD, INK, PAPER, type_at
from preview_phone import device
from preview_plates import shot, source

MINT = '#b3ebbc'


def label(frame, text, x, y, *, highlight=False, size=23):
    draw = ImageDraw.Draw(frame, 'RGBA')
    width = round(draw.textlength(text, font=font(size))) + 29
    fill = GOLD if highlight else (17, 25, 24, 232)
    draw.rounded_rectangle((x, y, x+width, y+size+19), 8, fill=fill)
    type_at(frame, (x+14, y+(size+19)/2), text, size, INK if highlight else PAPER, 'lm')


def test_start(t):
    if t < .70:
        frame = shot('coffee-live', .67+t*.82, 1.15, -31, 0)
    else:
        frame = shot('coffee-live', 1.27+(t-.70)*.84, 1.53, -30, 25)
    if t < 1.45:
        label(frame, 'Pour to the rim', 411, 244)
    elif t >= 1.78:
        label(frame, 'No spill', 411, 244, highlight=True)
    return frame


@lru_cache(maxsize=1)
def testing_bench():
    room = shot('room', zoom=1.08).filter(ImageFilter.GaussianBlur(12))
    room = ImageEnhance.Brightness(room).enhance(.47)
    frame = Image.blend(room, Image.new('RGB', (W, H), '#1d2b2c'), .36)
    shadow = Image.new('L', (W, H))
    ImageDraw.Draw(shadow).ellipse((24, 194, 626, 313), fill=143)
    frame.paste('#101817', (0, 0, W, H), shadow.filter(ImageFilter.GaussianBlur(20)))

    draw = ImageDraw.Draw(frame, 'RGBA')
    draw.polygon(((42, 264), (603, 264), (598, 284), (50, 284)), fill='#263634')
    draw.polygon(((90, 169), (550, 169), (603, 264), (42, 264)), fill='#536560')
    draw.line(((90, 169), (550, 169), (603, 264), (42, 264), (90, 169)),
              fill='#7d8f81', width=2)
    draw.polygon(((89, 203), (574, 203), (586, 246), (66, 246)), fill='#435a54')
    draw.line((89, 203, 574, 203), fill='#354b46', width=2)
    draw.line((66, 246, 586, 246), fill='#6b8072', width=2)
    draw.line((111, 225, 530, 225), fill=(174, 199, 173, 103), width=2)
    for x in (503, 518, 533, 548):
        draw.line((x, 203, x+9, 246), fill=(221, 233, 210, 114), width=3)
    type_at(frame, (533, 186), 'FINISH', 15, PAPER)
    return frame


def puck(frame, x):
    shadow = Image.new('L', (W, H))
    ImageDraw.Draw(shadow).ellipse((x-24, 219, x+27, 243), fill=150)
    frame.paste('#0e1b17', (0, 0, W, H), shadow.filter(ImageFilter.GaussianBlur(5)))

    draw = ImageDraw.Draw(frame)
    draw.ellipse((x-23, 214, x+23, 240), fill='#795229')
    draw.ellipse((x-23, 208, x+23, 235), fill='#cd9a40', outline='#f5c975', width=1)
    draw.ellipse((x-19, 210, x+19, 231), fill='#eeb856')
    draw.arc((x-19, 210, x+19, 231), 203, 325, fill='#ffe6a2', width=2)
    draw.ellipse((x-8, 214, x+8, 225), outline='#9d702b', width=2)


def gate(frame, raised, front=False):
    draw = ImageDraw.Draw(frame, 'RGBA')
    if front:
        draw.line((351, 135, 351, 248), fill='#162e2c', width=10)
        draw.line((348, 136, 348, 247), fill='#b3c8b4', width=2)
        draw.line((343, 249, 361, 249), fill='#263c37', width=4)
        return

    draw.line((314, 120, 314, 203), fill='#263e3b', width=8)
    draw.line((312, 121, 312, 202), fill='#a5bca7', width=2)
    lift = round(57*raised)
    draw.polygon(((315, 151-lift), (350, 168-lift), (350, 244-lift), (315, 223-lift)),
                 fill=(44, 83, 77, 219), outline='#9bb6a8', width=2)
    draw.line((319, 219-lift, 347, 236-lift), fill='#c1d9c4', width=3)
    draw.line((313, 121, 352, 137), fill='#bfd1bc', width=8)
    draw.line((313, 119, 352, 135), fill='#dfe4c8', width=2)


def rule_retest(t):
    attempt = min(2, int(t/.98))
    phase = t-.98*attempt
    raised = ease(progress(phase, .13, .42)) if attempt == 2 else 0
    if attempt < 2:
        x = 128 + 179*progress(phase, 0, .54) - 21*ease(progress(phase, .54, .73))
    else:
        x = 128 + 421*ease(progress(phase, 0, .89))

    frame = testing_bench().copy()
    gate(frame, raised)
    puck(frame, x)
    gate(frame, raised, front=True)
    label(frame, ('First pass', 'Second pass', 'Same test')[attempt], 58, 52)
    if attempt < 2 and phase >= .55:
        type_at(frame, (82, 308), 'Stops at the gate', 21, PAPER, 'lm')
    if attempt == 2 and phase >= .79:
        label(frame, 'Gets through', 419, 289, highlight=True, size=21)
    return frame


def view_panel(raw, opening, joined, matched):
    extent = tuple(a+(b-a)*matched for a,b in zip(opening, joined))
    return raw.transform((W, H//2), Image.Transform.EXTENT, extent, Image.Resampling.BICUBIC)


def hidden_seam(t):
    # Both perspectives share the same moving footfall and fixed masonry landmarks.
    raw = source('walk-live', .37+t*.93)
    match = ease(progress(t, .44, 1.51))
    joined = (100, 78, 540, 325.5)
    upper_join = (100, 78, 540, 201.75)
    lower_join = (100, 201.75, 540, 325.5)
    if match >= 1:
        return raw.transform((W, H), Image.Transform.EXTENT, joined, Image.Resampling.BICUBIC)

    frame = Image.new('RGB', (W, H))
    frame.paste(view_panel(raw, (48, 137, 596, 291.125), upper_join, match), (0, 0))
    frame.paste(view_panel(raw, (230, 225, 430, 281.25), lower_join, match), (0, H//2))
    seam = ImageDraw.Draw(frame, 'RGBA')
    opacity = round(255*(1-progress(t, 1.28, 1.51)))
    seam.line((0, H//2, W, H//2), fill=(216, 238, 214, opacity), width=3)
    if t < .55:
        label(frame, 'Wide', 19, 15, size=19)
        label(frame, 'Footfall', 19, 198, size=19)
    return frame


def map_screen(t):
    panel = Image.new('RGBA', (170, 314), '#172b29')
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((16, 30, 153, 61), 6, fill='#b9cbb6')
    type_at(panel, (84, 46), 'AIRPLANE MODE', 12, INK)
    if t < 1.04:
        type_at(panel, (85, 125), 'Saved trail', 23)
        draw.rounded_rectangle((23, 165, 147, 206), 7, fill=MINT)
        type_at(panel, (85, 186), 'Open map', 19, INK)
        if t >= .78:
            draw.ellipse((70, 170, 101, 201), outline='#1a5845', width=3)
        return panel

    draw.rounded_rectangle((12, 79, 158, 264), 10, fill='#344f41')
    draw.polygon(((13, 212), (53, 164), (93, 180), (157, 119), (157, 263), (13, 263)),
                 fill='#497154')
    draw.line(((12, 157), (54, 145), (93, 152), (158, 99)), fill='#8ac4c6', width=6)
    route = ((32, 238), (56, 200), (83, 211), (115, 177), (137, 135))
    draw.line(route, fill=GOLD, width=6, joint='curve')
    for x,y in (route[0], route[-1]):
        draw.ellipse((x-6, y-6, x+6, y+6), fill=PAPER)
    type_at(panel, (85, 287), 'North trail', 19)
    return panel


def contradiction(t):
    frame, _ = device(t*.7, map_screen(t))
    if t < 1.04:
        label(frame, 'No signal?', 359, 121, size=27)
    else:
        label(frame, 'The map still opens', 350, 121, highlight=True, size=24)
        label(frame, 'Saved on the device', 350, 175, size=19)
    return frame


SCENES = {
    'advanced-test-start': test_start,
    'advanced-rule-retest': rule_retest,
    'advanced-hidden-seam': hidden_seam,
    'advanced-contradiction': contradiction,
}
