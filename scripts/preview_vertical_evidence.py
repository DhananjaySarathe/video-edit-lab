"""Portrait demonstrations composed around footage, timing and visible evidence."""
from array import array
import sys
import wave

from PIL import Image, ImageDraw

from preview_common import blend, ease, font, progress
from preview_phone import device
from preview_plates import source
from preview_sound import LENGTH, RATE, impact

SIZE = (360, 640)
PAPER = '#fbf4e5'
GOLD = '#ffdb78'
MINT = '#c4f2cf'
INK = '#142921'
DARK = (16, 29, 25, 237)

GESTURE_START = .65
GESTURE_INSERT = .55
SCORE_UPDATE = .80
GESTURE_HOLD = 1.65
POUR_START = .40
POUR_INSERT = .30
GAP_FRAME = 1.75
GAP_CUE = GAP_FRAME - POUR_START
PHONE_CUE = .75

GESTURE_WIDE = (173, 0, 375.5, 360)
GESTURE_CLOSE = (169, 60, 337.75, 360)
POUR_WIDE = (143, 0, 345.5, 360)
POUR_CLOSE = (169, 31, 331, 319)
PHONE_FRAME = (143, 0, 345.5, 360)


def portrait(frame, area):
    return frame.transform(SIZE, Image.Transform.EXTENT, area, Image.Resampling.BICUBIC)


def caption(draw, xy, text, size=27):
    x, y = xy
    width = round(draw.textlength(text, font=font(size)))
    draw.rounded_rectangle((x, y, x + width + 24, y + size + 16), 8, fill=DARK)
    draw.text((x + 12, y + (size + 16) / 2), text, font=font(size), fill=PAPER, anchor='lm')


def live_score(t):
    source_time = min(GESTURE_HOLD, GESTURE_START + t)
    area = GESTURE_CLOSE if GESTURE_INSERT <= t < 1.4 else GESTURE_WIDE
    frame = portrait(source('host-live', source_time), area)
    draw = ImageDraw.Draw(frame, 'RGBA')
    caption(draw, (22, 412), 'Do the hands touch?')

    scored = t >= SCORE_UPDATE
    settle = ease(progress(t, SCORE_UPDATE, SCORE_UPDATE + .24))
    active_color = blend((255, 219, 120), (196, 242, 207), settle)
    for index, (choice, x) in enumerate((('Touch', 22), ('Stay apart', 156))):
        selected = index == 0 and scored
        draw.rounded_rectangle((x, 463, x + 128, 519), 8,
                               fill=active_color if selected else DARK)
        color = INK if selected else PAPER
        draw.text((x + 10, 491), choice, font=font(17), fill=color, anchor='lm')
        draw.text((x + 117, 489), '1' if selected else '0', font=font(31), fill=color, anchor='rm')
    return frame


def score_audio(path):
    samples = array('h', (round(32767 * .22 * impact(i / RATE, SCORE_UPDATE, 36, 485))
                          for i in range(round(RATE * LENGTH))))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as recording:
        recording.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        recording.writeframes(samples.tobytes())


def spout_pin(t):
    # Source-pixel positions of the lip. The crop is fixed while the pitcher tilts.
    keys = ((.85, 267, 95), (1.20, 269, 95), (1.45, 278, 94),
            (1.60, 291, 88), (1.70, 298, 75), (GAP_FRAME, 306, 70))
    for (start, x, y), (end, next_x, next_y) in zip(keys, keys[1:]):
        if t <= end:
            fraction = progress(t, start, end)
            x += (next_x - x) * fraction
            y += (next_y - y) * fraction
            break
    left, top, right, bottom = POUR_CLOSE
    return (round((x - left) * SIZE[0] / (right - left)),
            round((y - top) * SIZE[1] / (bottom - top)))


def artifact_evidence(t):
    source_time = min(GAP_FRAME, POUR_START + t)
    frame = portrait(source('coffee-live', source_time), POUR_WIDE if t < POUR_INSERT else POUR_CLOSE)
    draw = ImageDraw.Draw(frame, 'RGBA')
    if t < .50:
        caption(draw, (22, 71), 'Watch the stream')
        return frame

    x, y = spout_pin(source_time)
    fade = ease(progress(t, .50, .65))
    alpha = round(255 * fade)
    draw.line(((103, 96), (151, 96), (x, y)), fill=(255, 219, 120, alpha), width=3)
    draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 219, 120, alpha))
    caption(draw, (22, 74), 'Spout', 25)

    if t >= GAP_CUE:
        draw.rounded_rectangle((22, 434, 253, 532), 8, fill=DARK)
        draw.text((37, 459), 'Visible gap', font=font(22), fill=PAPER, anchor='lm')
        draw.text((36, 499), f'{GAP_FRAME:.2f} s', font=font(39), fill=MINT, anchor='lm')
        draw.text((150, 502), 'in source clip', font=font(16), fill=PAPER, anchor='lm')
    return frame


def offline_display(t):
    panel = Image.new('RGBA', (170, 314), '#142d28')
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((24, 43, 146, 74), 7, fill=PAPER)
    draw.text((85, 59), 'OFFLINE', font=font(21), fill=INK, anchor='mm')
    if t < PHONE_CUE:
        draw.text((85, 125), 'Saved trail', font=font(25), fill=PAPER, anchor='mm')
        draw.rounded_rectangle((25, 158, 145, 201), 8, fill=MINT)
        draw.text((85, 179), 'Open map', font=font(22), fill=INK, anchor='mm')
        tap = ease(progress(t, .43, PHONE_CUE))
        if tap > 0:
            radius = round(5 + 18 * tap)
            draw.ellipse((85 - radius, 180 - radius, 85 + radius, 180 + radius), outline=INK, width=3)
        return panel

    draw.rounded_rectangle((12, 92, 158, 264), 8, fill='#406855')
    draw.polygon(((13, 194), (59, 159), (94, 184), (157, 127), (157, 263), (13, 263)), fill='#2d5145')
    draw.line(((13, 163), (65, 141), (103, 155), (157, 107)), fill='#9bd3d7', width=6)
    route = ((33, 234), (60, 191), (91, 208), (119, 169), (142, 134))
    draw.line(route, fill=GOLD, width=6, joint='curve')
    for x, y in (route[0], route[-1]):
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=PAPER)
    draw.text((85, 286), 'Stored locally', font=font(20), fill=PAPER, anchor='mm')
    return panel


def contradiction(t):
    # The same held phone and signal status remain visible through the response.
    filmed, _ = device(.32 + t * .75, offline_display(t))
    frame = portrait(filmed, PHONE_FRAME)
    draw = ImageDraw.Draw(frame, 'RGBA')
    caption(draw, (22, 72), 'No signal. No map?' if t < PHONE_CUE else 'The map still opens')
    caption(draw, (22, 525), 'Illustrated screen', 19)
    return frame


SCENES = {
    'advanced-live-score': live_score,
    'advanced-artifact-evidence': artifact_evidence,
    'advanced-contradiction': contradiction,
}
AUDIO = {'advanced-live-score': score_audio}
