"""Worked widescreen hooks with reproducible evidence and local footage."""

from functools import lru_cache

from PIL import Image, ImageDraw, ImageEnhance

from preview_common import H, W, ease, font, progress
from preview_phone import device
from preview_plates import shot


INK = '#14261f'
MUTED = '#506557'
PAPER = '#f8f4e8'
FAINT = '#d8e3d5'
GREEN = '#a9e1be'
GOLD = '#ffce72'
SIZE = W, H


def write(draw, at, value, size, color=PAPER, anchor='lm', weight='bold'):
    draw.text(at, value, font=font(size, weight), fill=color, anchor=anchor)


def badge(draw, at, value, fill=INK, color=PAPER):
    x, y = at
    width = round(font(15).getlength(value)) + 22
    draw.rounded_rectangle((x, y, x + width, y + 29), 5, fill=fill)
    write(draw, (x + 11, y + 15), value, 15, color)


CAPTION = 'WALK THIS WAY'
CAPTION_X, CAPTION_Y, CAPTION_SIZE = 158, 269, 35
PHONE_LEFT, PHONE_RIGHT = 220, 423
CHOSEN_FRAME = 2.21


def caption_master(stamp):
    frame = shot('walk-live', stamp, 1.05, 11, 2)
    draw = ImageDraw.Draw(frame)
    draw.text((CAPTION_X, CAPTION_Y), CAPTION, font=font(CAPTION_SIZE), fill='white',
              anchor='lm', stroke_width=3, stroke_fill='#101817')
    return frame


def crop_edges(draw, left, right, color):
    for x in (left, right):
        for y in range(12, H - 4, 18):
            draw.line((x, y, x, min(y + 10, H)), fill=color, width=2)


def word_crop(t):
    if t < 15.5:
        stamp = min(CHOSEN_FRAME, .30 + t * .25)
        frame = caption_master(stamp)
        draw = ImageDraw.Draw(frame, 'RGBA')
        draw.rectangle((0, 0, PHONE_LEFT - 1, H), fill=(20, 38, 31, 45))
        draw.rectangle((PHONE_RIGHT, 0, W, H), fill=(20, 38, 31, 45))
        crop_edges(draw, PHONE_LEFT, PHONE_RIGHT, '#f9e2a6')
        badge(draw, (17, 16), 'Original 16:9 edit')
        draw.rounded_rectangle((15, 307, 625, 345), 5, fill=INK)
        caption = 'Which word will the phone crop lose?' if t < 6.5 else 'Pick the first word that gets clipped.'
        write(draw, (320, 326), caption, 24, anchor='mm')
        return frame

    master = caption_master(CHOSEN_FRAME)
    if t < 17.0:
        amount = ease(progress(t, 15.5, 17.0))
        left = round(PHONE_LEFT * amount)
        right = round(W - (W - PHONE_RIGHT) * amount)
        master.paste(INK, (0, 0, left, H))
        master.paste(INK, (right, 0, W, H))
        crop_edges(ImageDraw.Draw(master), left, right, GOLD)
        return master

    # Reuse the exact same rendered master and convert only the viewport.
    phone_export = master.crop((PHONE_LEFT, 0, PHONE_RIGHT, H)).resize((360, 640), Image.Resampling.LANCZOS)
    frame = Image.new('RGB', SIZE, INK)
    frame.paste(phone_export.resize((180, 320), Image.Resampling.LANCZOS), (30, 20))
    draw = ImageDraw.Draw(frame)
    badge(draw, (237, 37), '9:16 export · 360 × 640', GREEN, INK)
    write(draw, (237, 111), 'WALK clips first.', 40)
    write(draw, (237, 157), 'The caption stayed put.', 26, GREEN)
    draw.line((237, 185, 604, 185), fill='#547163')
    write(draw, (237, 222), 'Crop starts at x = 220.', 23)
    write(draw, (237, 253), 'WALK starts at x = 158.', 23)
    write(draw, (237, 309), 'Next, check each word at delivery size.', 16, GREEN, weight='regular')
    return frame


VALUES = ('2', '10', '1', '12')
TEXT_ORDER = tuple(sorted(VALUES))
NUMBER_ORDER = tuple(str(value) for value in sorted(int(value) for value in VALUES))


def list_view(frame, at, size, values, label, *, typed=False, limit=4):
    x, y = at
    width, height = size
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((x, y, x + width, y + height), 8, fill='#fffdf7', outline='#b2c3b4')
    write(draw, (x + 17, y + 22), label, 19, INK)
    write(draw, (x + width - 15, y + 22), 'Ascending ↑', 14, MUTED, 'rm')
    draw.line((x + 15, y + 40, x + width - 15, y + 40), fill=FAINT)
    for index, value in enumerate(values[:limit]):
        row = y + 64 + 37 * index
        if typed and value in ('10', '2'):
            draw.rounded_rectangle((x + 12, row - 16, x + width - 12, row + 16), 3, fill='#ffe8b6')
        write(draw, (x + 18, row), str(index + 1), 14, MUTED, weight='regular')
        write(draw, (x + 48, row), f'“{value}”' if typed else value, 26, INK)
    if limit < len(values):
        write(draw, (x + 49, y + height - 34), 'More rows below', 15, MUTED)


def sorted_as_text(t):
    frame = Image.new('RGB', SIZE, PAPER)
    draw = ImageDraw.Draw(frame)
    if t < 13.5:
        write(draw, (22, 27), 'I assumed the list was sorted numerically.' if t < 5.8 else 'Look at the stored type.',
              26, INK)
        revealed = t >= 5.8
        left_label = 'Stored as text' if revealed else 'Sample list'
        list_view(frame, (20, 57), (342, 218), TEXT_ORDER, left_label,
                  typed=revealed, limit=4 if revealed else 2)
        if revealed:
            draw.rounded_rectangle((378, 57, 620, 274), 8, fill=INK)
            write(draw, (397, 97), 'TEXT', 32, GREEN)
            write(draw, (397, 147), '“10”', 54)
            write(draw, (397, 207), 'before “2”', 29, GOLD)
            write(draw, (398, 247), 'The first character decides.', 15, GREEN)
        else:
            plate = shot('editing-live', min(2.90, .14 + t * .53), 1.02, 0, 5, (241, 216))
            frame.paste(plate, (380, 58))
        draw.rectangle((0, 292, W, H), fill=INK)
        write(draw, (22, 325), 'Same direction. Different data type.' if revealed else 'The control says Ascending.',
              26)
        return frame

    write(draw, (21, 27), 'Run both sorts on the same source values.', 27, INK)
    list_view(frame, (20, 57), (294, 210), TEXT_ORDER, 'Text', typed=True)
    list_view(frame, (326, 57), (294, 210), NUMBER_ORDER, 'Number')
    draw.rectangle((0, 287, W, H), fill=INK)
    if t < 20.0:
        write(draw, (22, 320), 'Type decides what Ascending means.', 27)
    else:
        write(draw, (22, 312), 'Should this field be a quantity or a code?', 25)
        write(draw, (22, 339), 'Keep identifiers as text when their original digits matter.', 17, GREEN, weight='regular')
    return frame


TRAILER_ROLES = ('Street wide', 'Footfall detail', 'Phone map')
TRAILER_PROMISE = 'Follow the walk past the brick steps.'


@lru_cache(maxsize=1)
def route_map():
    panel = Image.new('RGBA', (170, 314), '#163226')
    draw = ImageDraw.Draw(panel)
    for offset in range(-72, 202, 30):
        draw.line((offset, 30, offset + 92, 282), fill='#3b5748', width=2)
    for offset in range(68, 296, 30):
        draw.line((6, offset, 166, offset - 22), fill='#3b5748', width=2)
    path = ((39, 246), (52, 196), (109, 169), (104, 126), (131, 99))
    draw.line(path, fill=GOLD, width=7, joint='curve')
    for x, y in (path[0], path[-1]):
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=PAPER)
    write(draw, (15, 35), 'Walk route', 23)
    write(draw, (106, 76), 'STEPS', 15, GOLD)
    write(draw, (45, 271), 'START', 14, GREEN)
    return panel


@lru_cache(maxsize=144)
def trailer_plate(index, frame_number, size):
    stamp = frame_number / 20
    if index == 2:
        phone, _ = device(stamp, route_map())
        return phone.resize(size, Image.Resampling.LANCZOS)
    name = ('walk-live', 'steps-live')[index]
    return shot(name, stamp, 1.02, 0, 0, size)


def trailer_slot(draw, x, index, used, selected):
    color = GREEN if selected else '#547566' if index < used else '#283c33'
    draw.rounded_rectangle((x, 298, x + 193, 341), 5, fill=color,
                           outline='#5c7b6b' if index >= used else None)
    foreground = INK if selected else PAPER
    label = TRAILER_ROLES[index] if index < used else 'Empty slot'
    write(draw, (x + 13, 320), f'{index + 1}  {label}', 17, foreground)


def three_clips(t):
    if t < 5.8:
        used, selected, local_time = 0, 0, .18
        instruction = 'The timeline starts with three empty slots.'
    elif t < 14.1:
        used, selected, local_time = 1, 0, min(3.18, t - 5.8)
        instruction = 'First source: let the walk establish the setting.'
    elif t < 18.8:
        used, selected, local_time = 2, 1, min(3.16, t - 14.1)
        instruction = 'Second source: carry the movement into the detail.'
    else:
        used = 3
        if t < 20.0:
            selected, local_time = 2, .35 + t - 18.8
            instruction = 'Third source: connect the movement to the map.'
        else:
            selected = min(2, int(t - 20.0))
            local_time = .95 + (t - 20.0) % 1
            instruction = 'First assembly · 3 sources'

    frame = Image.new('RGB', SIZE, INK)
    draw = ImageDraw.Draw(frame)
    write(draw, (17, 27), 'Three clips have to carry this trailer.', 28)
    write(draw, (624, 27), f'{used} / 3', 23, GOLD, 'rm')
    draw.line((15, 47, 625, 47), fill='#507061')
    write(draw, (19, 69), 'Source bin', 17, GREEN)
    for index, title in enumerate(TRAILER_ROLES):
        y = 88 + 57 * index
        fill = '#2e4e3e' if index == selected and used else '#22392f'
        draw.rounded_rectangle((13, y - 3, 218, y + 47), 5, fill=fill)
        frame.paste(trailer_plate(index, 17, (66, 39)), (18, y + 2))
        write(draw, (92, y + 21), title, 16)

    frame.paste(trailer_plate(selected, round(20 * local_time), (393, 216)), (229, 54))
    if not used:
        plate = frame.crop((229, 54, 622, 270))
        frame.paste(ImageEnhance.Brightness(plate).enhance(.64), (229, 54))
        badge(draw, (244, 66), 'Source preview')
    draw.rounded_rectangle((237, 239, 614, 262), 4, fill=INK)
    write(draw, (250, 250), instruction, 15, PAPER, weight='regular')
    write(draw, (18, 277), TRAILER_PROMISE, 18, GREEN)
    for index in range(3):
        trailer_slot(draw, 17 + 205 * index, index, used, used > 0 and selected == index)
    return frame


SCENES = {
    'hook-long-evidence-led-reversal-021': sorted_as_text,
    'hook-long-constraint-challenge-005': three_clips,
    'hook-long-prediction-014': word_crop,
}

POSTERS = {
    'hook-long-evidence-led-reversal-021': 8.4,
    'hook-long-constraint-challenge-005': 15.6,
    'hook-long-prediction-014': 3.3,
}
