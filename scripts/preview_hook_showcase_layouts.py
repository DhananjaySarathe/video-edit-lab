"""Original portrait edits showing the actual occlusion, crop, or layout change."""
from functools import lru_cache

from PIL import Image, ImageDraw

from preview_common import ease, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, PORTRAIT, chip, words
from preview_plates import shot, source


@lru_cache(maxsize=1)
def ruled_sheet():
    sheet = Image.new('RGB', (486, 702), '#f0ebd9')
    d = ImageDraw.Draw(sheet)
    for y in range(29, 702, 35):
        d.line((0, y, 486, y + 7), fill='#b9c3bc', width=2)
    d.line((46, 0, 38, 702), fill='#c48d83', width=2)
    for x in range(14):
        shade = 192 + 3 * x
        d.line((x, 0, x, 701), fill=(shade, shade - 5, shade - 13))
    page = sheet.rotate(-4, resample=Image.Resampling.BICUBIC, expand=True)
    mask = Image.new('L', sheet.size, 255).rotate(-4, resample=Image.Resampling.BICUBIC, expand=True)
    return page, mask


def page_pass(p):
    # At the join both source takes sit completely behind the same moving sheet.
    p = min(1., max(0., p))
    base = shot('notebook-live' if p < .5 else 'editing-live', .45 + p * 1.9, size=PORTRAIT)
    page, mask = ruled_sheet()
    x = round(-page.width + (360 + page.width) * p)
    base.paste(page, (x, -40), mask)
    return base


def hidden_page_cut(t):
    if t < .85:
        # Start mid-flip so the new workspace is already emerging.
        return page_pass(.65 + .35 * t / .85)
    if t < 1.14:
        frame = page_pass(.5)
        chip(ImageDraw.Draw(frame), (17, 478), 'Cut here / full cover')
        return frame
    if t < 2.15:
        frame = Image.new('RGB', PORTRAIT, INK)
        d = ImageDraw.Draw(frame)
        for i, (key, label) in enumerate((('notebook-live', 'A / notebook desk'), ('editing-live', 'B / editing desk'))):
            y = 59 + i * 247
            frame.paste(shot(key, .8, size=(326, 213)), (17, y))
            chip(d, (23, y + 8), label)
        return frame
    p = progress(t, 2.15, 4.49)
    frame = page_pass(p)
    label = 'A / approach' if p < .46 else 'Cut under the sheet' if p < .55 else 'B / same direction'
    chip(ImageDraw.Draw(frame), (17, 502), label)
    return frame


def social_rail(draw):
    # Deliberately uses sample player controls so the actual words can be obscured.
    for i, symbol in enumerate(('+', '♥', '•••')):
        y = 309 + i * 64
        draw.ellipse((302, y, 349, y + 47), fill='#30453e', outline=PAPER, width=2)
        words(draw, (326, y + 22), symbol, 21, PAPER, 'mm')


def rail_safe_caption(t):
    stamp = .35 + (max(0., t - 2.7) if t >= 2.7 else min(t, 1.88))
    frame = shot('portrait-live', min(3.05, stamp), size=PORTRAIT)
    d = ImageDraw.Draw(frame)
    safe = t >= .95
    if safe:
        d.rounded_rectangle((19, 371, 263, 454), 6, fill=INK)
        words(d, (31, 393), 'Read the very', 27)
        words(d, (31, 427), 'last word.', 27, GOLD)
    else:
        d.rounded_rectangle((12, 374, 355, 418), 6, fill=INK)
        words(d, (21, 396), 'Read the very last word.', 29)
    social_rail(d)
    if .95 <= t < 2.7:
        d.line((277, 310, 277, 482), fill=GOLD, width=2)
        chip(d, (187, 459), 'Text edge', INK, GOLD, 12)
    chip(d, (18, 64), 'Sample player / check the last word' if t < .95 else
         'Move the words left' if t < 2.7 else 'Replay with controls visible')
    return frame


@lru_cache(maxsize=1)
def counter_document():
    page = Image.new('RGB', (606, 390), '#f9f6e9')
    d = ImageDraw.Draw(page)
    words(d, (24, 32), 'Studio requests', 25, INK)
    words(d, (24, 64), 'Example log through Friday', 15, '#496459', weight='regular')
    xs = (25, 212, 396)
    for x, name in zip(xs, ('Day', 'New today', 'Total to date')):
        words(d, (x, 114), name, 19, INK)
    d.line((22, 136, 583, 136), fill='#63806f', width=2)
    for i, row in enumerate((('Wednesday', '14', '82'), ('Thursday', '23', '105'), ('Friday', '17', '122'))):
        y = 170 + i * 65
        if i == 2:
            d.rounded_rectangle((16, y - 26, 580, y + 27), 5, fill='#dce9d4')
        for x, val in zip(xs, row):
            words(d, (x, y), val, 22, INK)
    return page


def restore_column_title(t):
    frame = Image.new('RGB', PORTRAIT, INK)
    d = ImageDraw.Draw(frame)
    words(d, (22, 86), 'What does 122', 32)
    words(d, (22, 123), 'actually count?', 32, GOLD)
    page = counter_document()
    if t < 2.7:
        f = ease(progress(t, .95, 1.70))
        a, b = (371, 257, 563, 349), (365, 77, 580, 344)
        rect = tuple(a0 + (b0 - a0) * f for a0, b0 in zip(a, b))
        # Uniform scaling keeps the original typeface and number proportions intact.
        crop = page.crop(tuple(round(v) for v in rect))
        scale = min(306 / crop.width, 254 / crop.height)
        crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.Resampling.LANCZOS)
        frame.paste(crop, ((360 - crop.width) // 2, 330 - crop.height // 2))
    else:
        for i, (left, right, label) in enumerate(((192, 352, 'New today'), (375, 574, 'Total to date'))):
            x = 16 + 170 * i
            d.rounded_rectangle((x, 246, x + 155, 394), 6, fill=PAPER)
            words(d, (x + 9, 274), label, 17, INK)
            crop = page.crop((left, 274, right, 328))
            crop.thumbnail((144, 56), Image.Resampling.LANCZOS)
            frame.paste(crop, (x + 5, 308))
        words(d, (21, 430), 'Friday alone contributed 17.', 20, MINT)
    chip(d, (18, 505), 'Example log / cropped' if t < .95 else 'Restore the field title' if t < 2.7 else 'Compare the same day', PAPER, INK)
    return frame


def source_bounds(width, height, scale):
    # Photo height can change while the eye stays 36 output pixels from the top.
    left, top = 259 - width * .47 * scale, 69 - 36 * scale
    return (left, top, left + width * scale, top + height * scale)


def two_print_layouts(t):
    frame = Image.new('RGB', PORTRAIT, '#e9e8da')
    d = ImageDraw.Draw(frame)
    picture = source('host-live', .92)
    if .85 <= t < 2.15:
        words(d, (19, 93), 'One source portrait', 29, INK)
        scale = 324 / picture.width
        frame.paste(picture.resize((324, round(picture.height * scale))), (18, 222))
        for h, factor, col in ((166, 1.05, GOLD), (92, 1.48, MINT)):
            rect = source_bounds(144, h, factor)
            d.rectangle(tuple((18 if i % 2 == 0 else 222) + value * scale for i, value in enumerate(rect)), outline=col, width=2)
        x, y = 18 + 259 * scale, 222 + 69 * scale
        d.line((x - 9, y, x + 9, y), fill=PAPER, width=2)
        d.line((x, y - 9, x, y + 9), fill=PAPER, width=2)
        words(d, (20, 469), 'The eye anchors both crops.', 21, INK)
    else:
        words(d, (19, 81), 'One photo,', 34, INK)
        words(d, (19, 121), 'two layouts.', 34, INK)
        morph = ease(progress(t, 2.25, 4.1)) if t >= 2.15 else 1
        other_height = round(166 - morph * 74)
        other_scale = 1.05 + morph * .43
        for i, (h, factor) in enumerate(((166, 1.05), (other_height, other_scale))):
            x, y = 16 + 170 * i, 205
            d.rectangle((x, y, x + 156, y + 238), fill=PAPER, outline='#abbaa9')
            crop = picture.transform((144, h), Image.Transform.EXTENT, source_bounds(144, h, factor), Image.Resampling.BICUBIC)
            frame.paste(crop, (x + 6, y + 6))
            lines = ('Meet the', 'maker.') if i == 0 or morph < .54 else ('Meet the maker.',)
            for ln, txt in enumerate(lines):
                words(d, (x + 8, y + h + 27 + 22 * ln), txt, 15, INK)
            if t >= 2.15:
                px, py = x + 6 + .47 * 144, y + 6 + 36
                d.line((px - 8, py, px + 8, py), fill=GOLD, width=2)
                d.line((px, py - 8, px, py + 8), fill=GOLD, width=2)
        words(d, (18, 487), 'Finished layout pair' if t < .85 else 'Text reflows below the same face.', 18, INK)
    return frame


SCENES = {
    'hook-short-proof-first-003': hidden_page_cut,
    'hook-short-proof-first-093': two_print_layouts,
    'hook-short-specific-fix-020': rail_safe_caption,
    'hook-short-specific-fix-078': restore_column_title,
}

POSTERS = {'hook-short-proof-first-003': .36, 'hook-short-specific-fix-020': .37}
