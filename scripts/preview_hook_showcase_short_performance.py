"""Original portrait openings that show the editor's choice in the footage."""

from PIL import Image, ImageDraw

from preview_common import ease, font, progress
from preview_phone import device
from preview_plates import shot


SIZE = (360, 640)
INK, PAPER, MINT, GOLD, CORAL = '#142720', '#fff6e7', '#bde9c8', '#ffdb88', '#ffb4a0'
FREEZE_EARLY, FREEZE_RESULT = 1.05, 1.85  # The visible stream clears at the second mark.
SWITCH, REPLAY = 1.05, 2.55


def text(draw, at, words, size, color=PAPER, anchor='lm'):
    draw.text(at, words, fill=color, font=font(size), anchor=anchor)


def chip(draw, x, y, words, color=PAPER):
    width = round(draw.textlength(words, font=font(17)))
    draw.rounded_rectangle((x, y, x + width + 20, y + 31), 6, fill=INK)
    text(draw, (x + 10, y + 16), words, 17, color)


def timeline(draw, at, fixed, moved=False):
    x0, width, y = 25, 309, 570
    draw.rounded_rectangle((x0, y, x0 + width, y + 6), 3, fill='#496759')
    draw.line((x0, y + 3, x0 + width * at / 3.15, y + 3), fill='#89a68f', width=3)
    freeze_x = x0 + width * fixed / 3.15
    head = x0 + width * at / 3.15
    draw.line((freeze_x, y - 12, freeze_x, y + 20), fill=MINT if moved else CORAL, width=4)
    draw.ellipse((head - 5, y - 2, head + 5, y + 9), fill=PAPER)
    text(draw, (x0, 608), 'SOURCE', 15, PAPER)
    text(draw, (x0 + width, 608), f'{at:.2f} s', 17, PAPER, 'rm')


def moved_freeze(t):
    if t < SWITCH:
        source_time = min(FREEZE_EARLY, .76 + t)
        target = FREEZE_EARLY
        stage = 'PLAYBACK' if source_time < FREEZE_EARLY else 'HELD TOO EARLY'
        line = 'The pour is still going.'
        held = source_time == FREEZE_EARLY
    elif t < REPLAY:
        amount = ease(progress(t, SWITCH + .12, REPLAY - .35))
        source_time = FREEZE_EARLY + (FREEZE_RESULT - FREEZE_EARLY) * amount
        target = source_time
        stage = 'SCRUB THE SOURCE'
        line = 'Put the hold after the pour.'
        held = False
    else:
        source_time = min(FREEZE_RESULT, .76 + t - REPLAY)
        target = FREEZE_RESULT
        held = source_time == FREEZE_RESULT
        stage = 'HOLD ON THE RESULT' if held else 'REPLAY AT NORMAL SPEED'
        line = 'The cup is ready.' if held else 'Let the whole action play.'

    frame = shot('coffee-live', source_time, 1.0, -40, 0, SIZE)
    draw = ImageDraw.Draw(frame)
    chip(draw, 20, 46, stage, MINT if t >= REPLAY else PAPER)
    if held:
        x, y = 42, 440
        draw.rounded_rectangle((x - 20, y - 19, x + 21, y + 21), 7, fill=INK)
        for dx in (-6, 5):
            draw.rectangle((x + dx - 2, y - 7, x + dx + 3, y + 9), fill=PAPER)
    draw.rectangle((0, 490, 360, 640), fill=INK)
    if t < SWITCH:
        text(draw, (22, 513), 'That freeze is holding', 26)
        text(draw, (22, 540), 'the wrong frame.', 26)
    else:
        text(draw, (22, 529), line, 24, PAPER)
    timeline(draw, source_time, target, t >= SWITCH)
    return frame


def sign_panel(width, height, zoom):
    panel = Image.new('RGB', (width, height), '#264735')
    draw = ImageDraw.Draw(panel)
    cx, cy = width // 2, height // 2
    w, h = round(width * .63 * zoom), round(height * .51 * zoom)
    draw.rounded_rectangle((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2), 5, fill='#e1ead2')
    text(draw, (cx, cy), 'GATE 24', max(9, round(width * .13 * zoom)), INK, 'mm')
    return panel


def phone_ui(zoom, index):
    screen = Image.new('RGBA', (170, 314), INK)
    draw = ImageDraw.Draw(screen)
    text(draw, (85, 41), 'VIEW TEST', 19, MINT, 'mm')
    sign = sign_panel(144, 146, zoom)
    screen.paste(sign, (13, 67))
    for i, label in enumerate(('1×', '1.6×')):
        x = 16 + i * 75
        draw.rounded_rectangle((x, 218, x + 64, 250), 7, fill=MINT if i == index else '#385544')
        text(draw, (x + 32, 234), label, 20, INK if i == index else PAPER, 'mm')
    return screen


def contact_preview(frame, x, y, zoom, active):
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((x, y, x + 149, y + 87), 6, fill=INK,
                           outline=MINT if active else '#628071', width=2)
    preview = sign_panel(137, 44, zoom)
    frame.paste(preview, (x + 6, y + 6))
    text(draw, (x + 75, y + 66), 'Default 1×' if zoom == 1 else 'Zoomed 1.6×', 18,
         MINT if active else PAPER, 'mm')


def choose_phone_crop(t):
    compare = t >= 2.55
    index = int(t >= 1.68)
    zoom = 1.0 + .6 * ease(progress(t, 1.68, 1.85))
    raw, _ = device(min(3.15, .18 + t * .77), phone_ui(zoom, index))
    frame = raw.transform(SIZE, Image.Transform.EXTENT, (140, 0, 342.5, 360), Image.Resampling.BICUBIC)
    draw = ImageDraw.Draw(frame)
    chip(draw, 19, 39, 'Practice display')
    draw.rectangle((0, 478, 360, 640), fill=INK)
    if t < 1.0:
        text(draw, (20, 508), 'Default view or zoomed view?', 22)
    elif compare:
        text(draw, (20, 508), 'Which reads at a glance?', 24)
    else:
        text(draw, (20, 508), 'Try each view on the same sign', 21)
    contact_preview(frame, 22, 533, 1, not index and not compare)
    contact_preview(frame, 190, 533, 1.6, index == 1 and not compare)
    if 1.04 <= t < 1.30 or 1.68 <= t < 1.94:
        tap_time, x = (1.04, 96) if t < 1.3 else (1.68, 263)
        p = progress(t, tap_time, tap_time + .26)
        r = round(8 + 15 * p)
        draw.ellipse((x - r, 596 - r, x + r, 596 + r), outline=GOLD, width=2)
    return frame


SCENES = {
    'hook-short-choice-live-021': choose_phone_crop,
    'hook-short-turning-point-086': moved_freeze,
}

POSTERS = {'hook-short-choice-live-021': .28, 'hook-short-turning-point-086': .56}
