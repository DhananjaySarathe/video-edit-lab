"""Portrait compositions for reusable technique demonstrations."""
from bisect import bisect_right
from functools import partial
from math import sin

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from preview_common import font
from preview_live_action import GOLD, MINT, PAPER, tag, tween, type_at
from preview_plates import shot

SIZE = (360, 640)
W, H = SIZE
PANEL = '#18322a'
LIGHT = '#f4f2e5'

CAPTION_BEATS = {
    'stacked-hook-text': ('ONE STEP', 'THAT SAVES TIME', 'stack'),
    'staggered-kinetic-title': ('CUT', 'ON THE ANSWER', 'kinetic'),
    'rolling-letter-reveal': ('TRY', 'THE QUICK TEST', 'roll'),
    'animated-caption-layers': ('EDIT THE TAKE', 'KEEP THE PAUSE', 'layers'),
    'blur-slide-caption': ('HERE IS', 'THE BETTER CUT', 'slide'),
    'focus-pull-text': ('WATCH', 'THE SMALL CHANGE', 'focus'),
    'caption-hierarchy': ('I NEEDED', 'ONE GOOD TAKE', 'emphasis'),
    'gradient-caption': ('A NEW LOOK', 'IN ONE TAKE', 'gradient'),
    'bounce-settle-caption': ('THE TEST', 'WORKED', 'bounce'),
    'highlight-sweep-caption': ('CUT ON', 'THE ACTION', 'highlight'),
    'sheen-caption': ('THE LAST', 'FRAME MATTERS', 'sheen'),
    'brief-text-flicker': ('WAIT', 'WATCH THE CUT', 'flicker'),
    'rim-lit-caption': ('KEEP', 'THE OUTLINE', 'rim'),
}

SPLIT_IDS = {'side-by-side-callout', 'side-by-side-reference', 'comparative-chart',
             'vertical-safe-zone', 'long-payoff-back'}
WIDE_GRAPHICS = {'Charts and infographics', 'Maps and documentary graphics',
                 'Explanations and screen recordings', 'AI editing workflows'}
FLOATING_PLATES = {'world-anchored-graphic', 'world-anchored-type', 'floating-interface-layers',
                   'floating-screen', 'floating-notification', 'floating-card-carousel',
                   'projected-hud', 'picture-in-picture-demo', 'screen-replacement',
                   'tracked-chat-bubbles', 'curved-tracked-text', 'grounded-particle-overlay'}
FOCAL_X = {'tracked-callout': .51, 'ar-wayfinding': .57, 'glowing-orb': .57,
           'gesture-triggered-vfx': .58, 'product-orbit': .55, 'explanatory-b-roll': .52,
           'stylized-silhouette': .46}


def plate(name, t, zoom=1, x=0, y=0):
    return shot(name, t, zoom, x, y, SIZE)


def fit_title(draw, text, width, start):
    size = start
    while size > 14 and draw.textlength(text, font=font(size)) > width:
        size -= 1
    return size


def caption_demo(identifier, t):
    lead, phrase, style = CAPTION_BEATS[identifier]
    frame = plate('portrait-live', t, 1.03, 0, -4)
    shade = Image.new('RGBA', SIZE)
    draw = ImageDraw.Draw(shade)
    for y in range(248, 589):
        alpha = round(163 * max(0, 1 - abs(y - 442) / 187))
        draw.line((0, y, W, y), fill=(12, 22, 20, alpha))
    frame.paste(shade, (0, 0), shade)

    motion = tween(t, .26, .72)
    lead_y = 356 if style != 'stack' else 317
    if style == 'layers' and t >= 1.68:
        lead, phrase, motion = 'KEEP THE BREATH', 'CUT THE REPEAT', tween(t, 1.68, 1.99)
    type_at(frame, (30, lead_y), lead, 23, PAPER, 'lm', 2)
    draw = ImageDraw.Draw(frame)
    size = fit_title(draw, phrase, 280, 52 if style in ('emphasis', 'stack', 'bounce') else 42)
    width = draw.textlength(phrase, font=font(size))
    y, x = lead_y + 44, 30
    if style == 'slide':
        y += round(62 * (1 - motion))
    elif style == 'bounce':
        y += round(-44 * (1 - motion) + 11 * sin(t * 24) * max(0, 1 - t / 1.0))
    if style == 'highlight' and motion > 0:
        draw.rounded_rectangle((x - 4, y - 18, x + width * motion + 4, y + 18), 6, fill='#ad7337')
    if style == 'kinetic' and t < .74:
        phrase = ' '.join(phrase.split()[:1 + int(t * 4.1)])
    if style == 'roll':
        count = max(1, round(len(phrase) * motion))
        phrase = phrase[:count] + ('·' if count < len(phrase) else '')
    glyphs = Image.new('RGBA', SIZE)
    tone = GOLD if style in ('stack', 'emphasis', 'highlight', 'rim') else MINT
    if style == 'flicker' and .2 <= t < .52 and int(t * 29) % 3 == 0:
        tone = '#7e9b90'
    type_at(glyphs, (x, y), phrase, size, tone, 'lm', 2)
    if style in ('gradient', 'sheen'):
        mask = glyphs.getchannel('A')
        colors = Image.new('RGB', SIZE, '#a9e5c3')
        brush = ImageDraw.Draw(colors)
        for cx in range(W):
            peak = max(0, 1 - abs(cx - (110 if style == 'gradient' else 415 * motion - 32)) / 124)
            brush.line((cx, y - 46, cx, y + 46), fill=(round(151 + 102 * peak), round(207 + 41 * peak), round(170 + 46 * peak)))
        frame.paste(colors, (0, 0), mask)
    else:
        if style in ('focus', 'slide') and motion < 1:
            glyphs = glyphs.filter(ImageFilter.GaussianBlur((1 - motion) * (11 if style == 'focus' else 5)))
        if style == 'rim':
            glow = glyphs.filter(ImageFilter.GaussianBlur(5))
            frame.paste(glow, (0, 0), glow)
        frame.paste(glyphs, (0, 0), glyphs)
    return frame


def caption_behind(t):
    # The true moving matte shares the exact portrait crop and time.
    actor = plate('host-live', t, 1.03, -34, -9)
    matte = plate('host-live-matte', t, 1.03, -34, -9)
    stage = ImageEnhance.Brightness(actor).enhance(.69)
    stage.paste(actor, (0, 0), matte)
    title = Image.new('RGBA', SIZE)
    type_at(title, (180, 159 - 26 * tween(t, .1, .62)), 'ONE CUT', 64, GOLD, 'mm', 1)
    ImageDraw.Draw(title).line((21, 180, 328, 180), fill=GOLD, width=4)
    stage.paste(title, (0, 0), title)
    stage.paste(actor, (0, 0), matte)
    type_at(stage, (31, 496), 'Text behind the speaker', 21, PAPER, 'lm', 2)
    return stage


def emphasis_cut(t, slow=False):
    zoom = 1 + .25 * (tween(t, .15, 2.5) if slow else (t >= .72))
    frame = plate('portrait-live', t, zoom, -8, -22)
    type_at(frame, (30, 472), 'Here is the detail.' if t >= .72 else 'Watch this closer.', 29, PAPER, 'lm', 2)
    return frame


def proof_burst(t, montage=False):
    cuts = (.54, .91, 1.21, 1.52) if montage else (.44, .78, 1.06, 1.41)
    i = bisect_right(cuts, t)
    offsets = (2.6, .03, .39, .87, 2.76)
    zoom = (1.17, 1.02, 1.49, 1.3, 1.05)[i]
    phase = t - ((0,) + cuts)[i]
    frame = plate('coffee-live', offsets[i] + phase * .61, zoom, -32, 16)
    phrases = ('THE RESULT', 'THE FIRST POUR', 'WATCH THE EDGE', 'ONE CLEAN MOVE', 'HERE IS THE PROOF')
    tag(frame, phrases[i], 13, 73, i in (0, 4))
    return frame


def layout_split(identifier, frame):
    # Put the two simultaneous states above and below each other at phone size.
    size = (W, H // 2)
    if identifier == 'vertical-safe-zone':
        left = frame.crop((125, 18, 311, 347))
        right = frame.crop((335, 18, 521, 347))
    else:
        left = frame.crop((6, 18, 316, 345))
        right = frame.crop((324, 18, 634, 345))
    canvas = Image.new('RGB', SIZE, PANEL)
    canvas.paste(ImageOps.fit(left, size, Image.Resampling.LANCZOS), (0, 0))
    canvas.paste(ImageOps.fit(right, size, Image.Resampling.LANCZOS), (0, H // 2))
    ImageDraw.Draw(canvas).line((0, H // 2, W, H // 2), fill=LIGHT, width=2)
    return canvas


def place_graphic(frame, t, title, section, identifier):
    if section == 'Maps and documentary graphics':
        canvas = plate('walk-live', t, 1.1, -7)
    elif section == 'Explanations and screen recordings' or identifier in FLOATING_PLATES:
        canvas = plate('host-live', t, 1.05, -34, -17)
    else:
        canvas = Image.new('RGB', SIZE, PANEL)
    canvas = ImageEnhance.Brightness(canvas).enhance(.61)
    measure = ImageDraw.Draw(canvas)
    words = title.split()
    lines = ['']
    for word in words:
        combined = (lines[-1] + ' ' + word).strip()
        if lines[-1] and measure.textlength(combined, font=font(31)) > 294:
            lines.append(word)
        else:
            lines[-1] = combined
    loaded = frame.resize((360, 203), Image.Resampling.LANCZOS)
    if section == 'Sound and music':
        ribbon = frame.crop((5, 236, 635, 352)).resize((W, 101), Image.Resampling.LANCZOS)
        picture = ImageOps.fit(frame.crop((0, 0, 640, 235)), (W, 381), Image.Resampling.LANCZOS)
        canvas.paste(picture, (0, 0))
        canvas.paste(ribbon, (0, 498))
        start_y = 419
    else:
        canvas.paste(loaded, (0, 264 if identifier in FLOATING_PLATES else 212))
        start_y = 156 - 20 * (len(lines) - 1)
    for i, line in enumerate(lines):
        type_at(canvas, (26, start_y + i * 35), line, 31, PAPER, 'lm', 2)
    return canvas


def reframe(identifier, section, title, source, t):
    frame = source(t)
    if identifier in SPLIT_IDS:
        return layout_split(identifier, frame)
    if section in WIDE_GRAPHICS or section == 'Sound and music' or identifier in FLOATING_PLATES:
        return place_graphic(frame, t, title, section, identifier)
    return ImageOps.fit(frame, SIZE, Image.Resampling.LANCZOS, centering=(FOCAL_X.get(identifier, .5), .5))


SCENES = {key: partial(caption_demo, key) for key in CAPTION_BEATS}
SCENES.update({
    'text-behind-subject': caption_behind,
    'punch-in': emphasis_cut,
    'slow-push-in': partial(emphasis_cut, slow=True),
    'short-proof-burst': proof_burst,
    'payoff-montage': partial(proof_burst, montage=True),
})
