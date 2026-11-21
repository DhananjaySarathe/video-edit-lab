"""Picture-first Shorts openings composed directly on a 9:16 canvas."""
from functools import lru_cache

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from preview_common import ease, font, progress
from preview_live_action import GOLD, INK, PAPER, type_at
from preview_plates import shot

SIZE = (360, 640)
MINT = '#c1f2d0'


def caption(frame, words, x, y, size=26, *, accent=None):
    draw = ImageDraw.Draw(frame, 'RGBA')
    width = draw.textlength(words, font=font(size))
    draw.rounded_rectangle((x, y, x+width+26, y+size+17), 8,
                           fill=accent or (14, 25, 23, 235))
    type_at(frame, (x+13, y+(size+17)/2), words, size, INK if accent else PAPER, 'lm')


def test_start(t):
    # Resume on the same pour frame at the punch-in. Only the crop changes.
    stamp = .65 + t*.94
    if t < .47:
        frame = shot('coffee-live', stamp, 1.03, -63, 0, SIZE)
    else:
        follow = ease(progress(t, 1.40, 2.68))
        frame = shot('coffee-live', stamp, 1.28-.11*follow, -66-66*follow, 26, SIZE)
    if .08 <= t < 1.30:
        caption(frame, 'To the rim?', 21, 495, 30)
    elif t >= 1.30:
        caption(frame, 'No spill.', 21, 495, 30, accent=GOLD)
    return frame


def layered_words(frame, matte, t):
    width, height = frame.size
    shift = 13*(1-ease(progress(t, 0, .40)))
    y = round(min(172, height*.34)+shift)
    image = ImageEnhance.Brightness(frame).enhance(.76)
    words = Image.new('RGBA', frame.size)
    type_at(words, (84, y), 'ONE', 61, GOLD)
    type_at(words, (278, y), 'CUT', 61, GOLD)
    ImageDraw.Draw(words).line((26, y+40, width-26, y+40), fill=GOLD, width=2)
    image.paste(words, (0, 0), words)
    image.paste(frame, (0, 0), matte)
    return image


def matched_proof(t):
    # The same frame and transform drive both panes, including the foreground matte.
    stamp = .46 + t*.95
    if t >= 1.67:
        raw = shot('host-live', stamp, 1.02, -85, 0, SIZE)
        matte = shot('host-live-matte', stamp, 1.02, -85, 0, SIZE)
        result = layered_words(raw, matte, t)
        caption(result, 'Edited', 19, 68, 21, accent=GOLD)
        return result

    panel = (360, 320)
    raw = shot('host-live', stamp, 1.16, -46, 10, panel)
    matte = shot('host-live-matte', stamp, 1.16, -46, 10, panel)
    result = Image.new('RGB', SIZE)
    result.paste(raw, (0, 0))
    result.paste(layered_words(raw, matte, t), (0, 320))
    ImageDraw.Draw(result).line((0, 319, 360, 319), fill='#d5e6d3', width=2)
    caption(result, 'Raw', 19, 65, 21)
    caption(result, 'Edited', 19, 347, 21, accent=GOLD)
    return result


@lru_cache(maxsize=1)
def bench():
    plate = shot('room', size=SIZE).filter(ImageFilter.GaussianBlur(17))
    plate = ImageEnhance.Brightness(plate).enhance(.44)
    frame = Image.blend(plate, Image.new('RGB', SIZE, '#182820'), .56)
    shadow = Image.new('L', SIZE)
    ImageDraw.Draw(shadow).ellipse((22, 298, 339, 593), fill=134)
    frame.paste('#101611', (0, 0, *SIZE), shadow.filter(ImageFilter.GaussianBlur(18)))
    draw = ImageDraw.Draw(frame, 'RGBA')
    draw.polygon(((38, 525), (322, 525), (311, 553), (49, 553)), fill='#233e37')
    draw.polygon(((94, 144), (266, 144), (322, 525), (38, 525)),
                 fill='#516a60', outline='#879c8d', width=2)
    draw.polygon(((125, 156), (235, 156), (276, 506), (84, 506)), fill='#2c5046')
    draw.line((125, 157, 84, 507), fill='#9aac99', width=3)
    draw.line((235, 157, 276, 507), fill='#9aac99', width=3)
    for y in range(221, 512, 34):
        draw.line((180, y, 180, y+12), fill=(179, 211, 190, 100), width=2)
    draw.ellipse((148, 162, 212, 194), fill='#446559', outline='#a7bdae', width=3)
    return frame


def draw_puck(frame, y):
    shadow = Image.new('L', SIZE)
    ImageDraw.Draw(shadow).ellipse((148, y-4, 216, y+28), fill=139)
    frame.paste('#142c26', (0, 0, *SIZE), shadow.filter(ImageFilter.GaussianBlur(6)))
    draw = ImageDraw.Draw(frame)
    draw.ellipse((148, y-13, 212, y+21), fill='#8b5e2b')
    draw.ellipse((148, y-19, 212, y+13), fill='#d89d37', outline='#f8d487', width=2)
    draw.ellipse((154, y-17, 206, y+9), fill='#ecb653')
    draw.arc((154, y-17, 206, y+9), 202, 320, fill='#ffe6a6', width=2)
    draw.ellipse((166, y-12, 194, y+4), outline='#986d34', width=2)


def draw_gate(frame, opening):
    draw = ImageDraw.Draw(frame)
    for x in (98, 262):
        draw.rounded_rectangle((x-8, 223, x+11, 337), 4, fill='#263d37')
        draw.line((x-4, 228, x-4, 332), fill='#90a89a', width=3)
        draw.ellipse((x-13, 329, x+16, 341), fill='#22392f')
        draw.ellipse((x+1, 233, x+7, 239), fill=MINT if opening > .95 else '#eeaa72')
    tip = round(253-131*opening)
    depth = round(69*opening)
    draw.polygon(((108, 254), (tip, 254-depth), (tip, 325-depth), (108, 325)),
                 fill='#447568', outline='#a6c2ae', width=2)
    draw.line((110, 313, tip, 313-depth), fill='#c5dbc6', width=5)
    draw.line((110, 261, tip, 261-depth), fill='#628e78', width=2)


def rule_retest(t):
    run = min(2, int(t/.61))
    phase = t - run*.61
    opening = ease(progress(phase, .09, .34)) if run == 2 else 0
    if run == 2:
        puck = 457 - 279*ease(progress(phase, 0, .88))
    else:
        puck = 443 - 100*progress(phase, -.03, .25) + 28*ease(progress(phase, .25, .48))

    frame = bench().copy()
    if puck < 325:
        draw_puck(frame, puck)
    draw_gate(frame, opening)
    if puck >= 325:
        draw_puck(frame, puck)
    if t < 2.02:
        caption(frame, 'Can it pass?', 20, 63, 29)
    else:
        caption(frame, 'The gate opens.', 20, 63, 29, accent=GOLD)
    if run < 2:
        type_at(frame, (20, 128), f'Try {run+1}', 21, PAPER, 'lm')
        if phase >= .25:
            caption(frame, 'Stopped', 21, 476, 25)
    elif phase < .80:
        type_at(frame, (20, 128), 'Same test', 21, PAPER, 'lm')
    else:
        caption(frame, 'Through', 21, 476, 25, accent=MINT)
    return frame


SCENES = {
    'advanced-test-start': test_start,
    'advanced-matched-proof': matched_proof,
    'advanced-rule-retest': rule_retest,
}
