"""Worked hook examples built from actual stock frames and original editing timelines."""
from functools import lru_cache
from math import hypot

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from preview_common import ease, font, progress
from preview_plates import shot


PORTRAIT = (360, 640)
WIDE = (640, 360)
INK = '#192821'
PAPER = '#f6f2e8'
MINT = '#b8ebbc'
GOLD = '#ffd477'
CORAL = '#f29b82'
SOFT = '#697b70'


def words(draw, at, text, size, color=PAPER, anchor='lm', weight='bold'):
    draw.text(at, text, font=font(size, weight), fill=color, anchor=anchor)


def chip(draw, at, label, fill=INK, color=PAPER, size=15):
    x, y = at
    face = font(size)
    width = round(face.getlength(label)) + 18
    draw.rounded_rectangle((x, y, x + width, y + size + 13), 5, fill=fill)
    words(draw, (x + 9, y + (size + 13) / 2), label, size, color)


def timed_caption(t):
    # Each pass lasts 2.4 s. The caption lasts 0.6 s in the first and 2.4 s in the second.
    replay = t >= 2.4
    elapsed = min(2.4, t - 2.4 if replay else t)
    source_time = min(3.1, .2 + elapsed)
    graphic = shot('coffee-live', source_time, 1.06, -56, 16, PORTRAIT)
    draw = ImageDraw.Draw(graphic)
    chip(draw, (20, 57), 'Earlier caption' if replay else 'First cut', MINT if replay else INK, INK if replay else PAPER)
    # Start with words visible on the actual first frame. Then expose the early cut.
    visible = replay or t < .6
    if visible:
        draw.rounded_rectangle((18, 391, 323, 473), 7, fill=INK)
        words(draw, (31, 415), 'Pour slowly along', 29)
        words(draw, (31, 448), 'the inside edge.', 29, GOLD)
    else:
        graphic = shot('coffee-live', .75 + elapsed * .7, 1.48, -74, 39, PORTRAIT)
        draw = ImageDraw.Draw(graphic)
        chip(draw, (20, 57), 'Cut already landed')
    draw.rounded_rectangle((22, 497, 327, 544), 6, fill=INK)
    words(draw, (33, 511), '6 words', 13)
    words(draw, (314, 511), '2.4 s to read' if replay else '0.6 s to read', 13, MINT if replay else GOLD, 'rm')
    draw.rounded_rectangle((34, 528, 315, 533), 2, fill=SOFT)
    span = 2.4 if replay else .6
    fill = round(281 * min(span, elapsed) / 2.4)
    if fill:
        draw.rectangle((34, 528, 34 + fill, 533), fill=MINT if replay else GOLD)
    return graphic


def behind_type(t):
    stamp = .57 + min(t, .85) * .83 if t < 2.15 else .48 + min(2.65, t - 2.15)
    raw = shot('host-live', stamp, 1.0, -7, -3, PORTRAIT)
    matte = shot('host-live-matte', stamp, 1.0, -7, -3, PORTRAIT)
    if .85 <= t < 2.15:
        frame = ImageOps.colorize(matte, '#13211f', '#d1f2cf').convert('RGB')
        label = '2 / Foreground matte'
    else:
        frame = ImageEnhance.Brightness(raw).enhance(.73)
        layer = ImageDraw.Draw(frame)
        if t < .85 or t >= 2.88:
            words(layer, (339, 218), 'ONE', 77, GOLD, 'rm')
            words(layer, (343, 343), 'CUT', 103, GOLD, 'rm')
            layer.line((124, 397, 342, 397), fill=GOLD, width=3)
        if t < .85 or t >= 3.56:
            frame.paste(raw, (0, 0), matte)
        label = '1 / Finished cut' if t < .85 else ('3 / Source take' if t < 2.88 else '4 / Title layer' if t < 3.56 else '5 / Foreground on top')
    chip(ImageDraw.Draw(frame), (19, 511), label)
    return frame


def identical_grays(t):
    frame = Image.new('RGB', PORTRAIT, PAPER)
    draw = ImageDraw.Draw(frame)
    words(draw, (23, 77), 'Which square', 35, INK)
    words(draw, (23, 116), 'looks darker?', 35, INK)
    draw.rectangle((17, 185, 178, 382), fill='#292929')
    draw.rectangle((182, 185, 343, 382), fill='#fdfdfd', outline='#ddd9d1')
    draw.rectangle((17, 383, 343, 470), fill='#a2a2a2')
    slide = ease(progress(t, 1.2, 2.8))
    y = round(279 + 142 * slide)
    gap = round(83 - 48 * slide)
    for x in (180 - gap, 180 + gap):
        draw.rectangle((x - 35, y - 35, x + 35, y + 35), fill='#808080')
    if t >= 2.8:
        chip(draw, (79, 493), '#808080 on both sides', INK, MINT, 17)
    else:
        words(draw, (180, 506), 'Watch both squares move.', 17, INK, 'mm', 'regular')
    return frame


@lru_cache(maxsize=2)
def setting_panel(enabled):
    page = Image.new('RGB', (760, 520), '#f7f7f2')
    draw = ImageDraw.Draw(page)
    draw.rectangle((0, 0, 760, 51), fill=INK)
    words(draw, (24, 25), 'Caption editor', 24)
    draw.rounded_rectangle((24, 75, 480, 474), 7, fill='#d5ddd1')
    page.paste(shot('host-live', 1.05, size=(428, 292)), (38, 87))
    if enabled:
        draw.rounded_rectangle((85, 297, 420, 347), 7, fill=INK)
        words(draw, (252, 322), 'Keep the gesture visible.', 24, PAPER, 'mm')
    else:
        words(draw, (251, 322), 'Keep the gesture visible.', 23, PAPER, 'mm')
    words(draw, (517, 106), 'Text settings', 22, INK)
    for i, name in enumerate(('Typeface', 'Size', 'Alignment', 'Background')):
        y = 158 + 48 * i
        words(draw, (517, y), name, 18, INK, weight='regular')
        draw.line((512, y + 24, 735, y + 24), fill='#d2d9ce')
    draw.rounded_rectangle((669, 287, 723, 315), 15, fill='#457650' if enabled else '#899489')
    x = 708 if enabled else 685
    draw.ellipse((x - 10, 291, x + 10, 311), fill=PAPER)
    return page


def zoom_to_control(t):
    frame = Image.new('RGB', PORTRAIT, '#16271f')
    draw = ImageDraw.Draw(frame)
    chip(draw, (19, 64), 'One setting', MINT, INK)
    words(draw, (20, 135), 'Find the', 40)
    words(draw, (20, 181), 'background switch.', 34, GOLD)
    on = t >= 2.12
    page = setting_panel(on)
    zoom = ease(progress(t, .95, 1.25)) * (1 - ease(progress(t, 2.7, 3.05)))
    bounds = tuple(a + (b - a) * zoom for a, b in zip((0, 0, 760, 520), (490, 205, 750, 383)))
    frame.paste(page.transform((336, 230), Image.Transform.EXTENT, bounds, Image.Resampling.BICUBIC), (12, 240))
    if 1.3 < t < 2.65:
        px = round(224 + 59 * ease(progress(t, 1.3, 2.05)))
        py = round(428 - 59 * ease(progress(t, 1.3, 2.05)))
        draw.polygon(((px, py), (px + 4, py + 22), (px + 9, py + 15), (px + 17, py + 14)), fill=INK, outline=PAPER)
    words(draw, (20, 516), 'Back to the full frame' if t >= 2.7 else 'Follow the pointer' if t >= .95 else 'Full editing canvas', 20)
    return frame


def line_breaks(t):
    frame = Image.new('RGB', PORTRAIT, '#15231e')
    draw = ImageDraw.Draw(frame)
    words(draw, (19, 72), 'Keep the number', 31)
    words(draw, (19, 108), 'with its unit.', 31, GOLD)
    for i, (label, y, lines) in enumerate((
        ('A', 167, ('The walk takes 15', 'minutes each way.')),
        ('B', 332, ('The walk takes', '15 minutes each way.')),
    )):
        active = (i == 0 and t < 1) or (i == 1 and t >= 1)
        draw.rounded_rectangle((16, y, 333, y + 134), 8, fill='#294237' if active else '#203229')
        chip(draw, (27, y + 9), label, MINT if active else INK, INK if active else PAPER, 12)
        for j, line in enumerate(lines):
            words(draw, (34, y + 65 + j * 32), line, 25)
        if t >= 2.55 and i == 1:
            draw.line((34, y + 116, 170, y + 116), fill=GOLD, width=3)
    words(draw, (20, 512), 'Same words. Same type size.', 19, MINT)
    words(draw, (20, 544), 'Compare the break.', 19)
    return frame


def caption_export(t):
    frame = Image.new('RGB', WIDE, '#192824')
    draw = ImageDraw.Draw(frame)
    phase = 0 if t < 6 else 1 if t < 14.5 else 2
    chip(draw, (18, 13), ('Export / 640 × 360', 'Source / same frame', 'Fix the bottom margin')[phase])
    stamp = min(2.2, .31 + t * .60) if phase == 0 else 2.2
    panel = shot('host-live', stamp, 1.04, -8, 0, (504, 284))
    p = ImageDraw.Draw(panel)
    baseline = 281 if phase < 2 else round(281 - 51 * ease(progress(t, 14.5, 16.6)))
    p.rounded_rectangle((48, baseline - 18, 451, baseline + 20), 7, fill=INK)
    words(p, (250, baseline + 2), 'Keep the gesture in the frame.', 23, PAPER, 'mm')
    if phase:
        p.rectangle((27, 17, 477, 260), outline=GOLD, width=2)
        p.line((28, 260, 478, 260), fill=CORAL, width=2)
    frame.paste(panel, (68, 51))
    return frame


def project_restore(t):
    frame = Image.new('RGB', WIDE, '#17231f')
    draw = ImageDraw.Draw(frame)
    restored = t < 13.8
    chip(draw, (13, 13), 'Restored project' if restored else 'Earlier / backup manifest',
         MINT if restored else GOLD, INK)
    if restored:
        detail = t >= 5.6
        stamp = (t - 5.6 if detail else t) % 3.0
        footage = 'steps-live' if detail or t > 2.9 else 'walk-live'
        frame.paste(shot(footage, stamp, size=(403, 210)), (12, 49))
        words(draw, (32, 218), 'ON FOOT', 29, GOLD)
        words(draw, (437, 80), 'Media', 21)
        for i, name in enumerate(('Street wide', 'Steps insert', 'End title')):
            words(draw, (437, 121 + 40 * i), name, 16, GOLD if detail and i == 1 else PAPER)
            words(draw, (437, 139 + 40 * i), 'Connected', 12, MINT)
    else:
        words(draw, (25, 86), 'Restore this clip from the delivery copy', 23)
        for i, (name, state) in enumerate((('01_street.mp4', 'Present'), ('02_steps.mp4', 'Media offline'), ('03_title', 'Present'))):
            y = 128 + i * 35
            draw.line((24, y + 17, 593, y + 17), fill=SOFT)
            words(draw, (29, y), name, 16, PAPER, weight='mono')
            words(draw, (550, y), state, 16, CORAL if i == 1 else MINT, 'rm')
    blocks = ((18, 197, 'Street'), (200, 351, 'Steps insert'), (354, 617, 'Street'))
    for i, (left, right, text) in enumerate(blocks):
        fill = '#41675a' if i != 1 else '#956458' if not restored else '#76956d'
        draw.rounded_rectangle((left, 277, right, 316), 4, fill=fill)
        words(draw, (left + 7, 296), text, 14)
    marker = 201 + round(143 * min(1, (t - 5.6) / 8.2)) if 5.6 <= t < 13.8 else 18 + round(178 * min(1, t / 5.6)) if t < 5.6 else 211
    draw.line((marker, 269, marker, 327), fill=GOLD, width=2)
    return frame


ROUTES = (((51, 173), (105, 173), (137, 116), (203, 116), (245, 65)),
          ((67, 70), (116, 70), (154, 116), (203, 116), (244, 171)))


def path_line(draw, points, color, dashed=False):
    for a, b in zip(points, points[1:]):
        if not dashed:
            draw.line((a, b), fill=color, width=5)
            continue
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = hypot(dx, dy)
        for begin in range(0, round(length), 12):
            stop = min(length, begin + 7)
            draw.line((a[0] + dx * begin / length, a[1] + dy * begin / length,
                       a[0] + dx * stop / length, a[1] + dy * stop / length), fill=color, width=5)


def route_print(t):
    frame = Image.new('RGB', WIDE, '#e4e6dc')
    draw = ImageDraw.Draw(frame)
    words(draw, (19, 30), 'Will both routes survive a monochrome print?', 23, INK)
    different = t >= 5.2
    for i, title in enumerate(('Drawing', 'Print preview')):
        panel = Image.new('RGB', (292, 211), '#fbfaf1')
        p = ImageDraw.Draw(panel)
        for x in range(15, 292, 29):
            p.line((x, 43, x, 204), fill='#dde0d6')
        for y in range(48, 210, 24):
            p.line((9, y, 281, y), fill='#dde0d6')
        words(p, (15, 24), title, 17, INK)
        path_line(p, ROUTES[0], '#27634c' if i == 0 else '#49514c')
        path_line(p, ROUTES[1], '#b05b37' if i == 0 else '#49514c', different)
        for pts, name in zip(ROUTES, ('Pier', 'Market')):
            x, y = pts[-1]
            p.ellipse((x - 4, y - 4, x + 4, y + 4), fill=INK)
            words(p, (x - 4, y - 12), name, 13, INK, 'rm')
        frame.paste(panel, (18 + 312 * i, 57))
    if t < 5.2:
        words(draw, (21, 305), 'Two colors become the same gray at the junction.', 19, INK)
    elif t < 12.2:
        words(draw, (21, 305), 'A broken stroke survives the change to gray.', 19, INK)
    else:
        path_line(draw, ((25, 306), (96, 306)), '#49514c')
        words(draw, (108, 307), 'Pier route', 19, INK)
        path_line(draw, ((311, 306), (383, 306)), '#49514c', True)
        words(draw, (396, 307), 'Market route', 19, INK)
    return frame


def framing_compare(t):
    frame = Image.new('RGB', WIDE, INK)
    draw = ImageDraw.Draw(frame)
    words(draw, (18, 29), 'Which crop shows the whole gesture?', 24)
    stamp = (.25 + t % 2.6) if t < 6.1 or t > 14.8 else 1.5
    for i, (label, scale, bias) in enumerate((('Wide', 1, -40), ('Tight', 1.63, -30))):
        tile = shot('host-live', stamp, scale, bias, -13 if i else 0, (296, 212))
        frame.paste(tile, (18 + 308 * i, 60))
        chip(draw, (24 + 308 * i, 68), label)
    if t < 6.1:
        line = 'Both panels use the same take and source time.'
    elif t < 14.8:
        line = 'Pause on contact. Check the fingers and elbows.'
    else:
        line = 'Replay both at speed. Which action could you describe?'
    words(draw, (20, 308), line, 18, MINT)
    return frame


SCENES = {
    'hook-short-test-in-motion-021': timed_caption,
    'hook-short-proof-first-001': behind_type,
    'hook-short-live-contradiction-001': identical_grays,
    'hook-short-specific-fix-032': zoom_to_control,
    'hook-short-choice-live-034': line_breaks,
    'hook-long-result-first-018': project_restore,
    'hook-long-visible-problem-015': caption_export,
    'hook-long-learning-promise-021': route_print,
    'hook-long-head-to-head-032': framing_compare,
}

POSTERS = {'hook-short-proof-first-001': .32, 'hook-short-test-in-motion-021': .25,
           'hook-long-result-first-018': .65}
