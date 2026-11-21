"""Directed widescreen hook examples using original graphics and local footage."""
from array import array
from math import exp, sin, tau
import sys
import wave

from PIL import Image, ImageDraw, ImageEnhance

from preview_common import H, W, ease, font, progress
from preview_plates import shot
from preview_sound import RATE


INK = '#112520'
PANEL = '#19372f'
MUTED = '#a6c6bc'
PAPER = '#fff5dd'
GOLD = '#ffcd70'
MINT = '#bcf3ce'
RULE = '#4d6a5e'
RARE_CUE = 6.4
RARE_CAPTION = 7.8


def text(draw, value, x, y, size, fill=PAPER, *, anchor='lm', weight='bold'):
    draw.text((x, y), value, font=font(size, weight), fill=fill, anchor=anchor)


def badge(frame, label, x=20, y=17):
    draw = ImageDraw.Draw(frame)
    width = round(font(16).getlength(label)) + 22
    draw.rounded_rectangle((x, y, x + width, y + 30), 6, fill=INK, outline=RULE, width=1)
    text(draw, label, x + 11, y + 15, 16, MINT)


def caption(frame, words, detail=None, size=29):
    draw = ImageDraw.Draw(frame, 'RGBA')
    draw.rectangle((0, 278, W, H), fill=(14, 29, 25, 247))
    text(draw, words, 23, 306 if detail else 321, size)
    if detail:
        text(draw, detail, 24, 338, 17, MUTED, weight='regular')


def feed_frame(draw, label, x, y, width, height):
    draw.rounded_rectangle((x, y, x + width, y + height), 8, fill=PANEL, outline=RULE, width=1)
    text(draw, label, x + 13, y + 17, 17, MINT)
    draw.line((x + 12, y + 32, x + width - 12, y + 32), fill=RULE)


def feed_delay(t):
    frame = Image.new('RGB', (W, H), INK)
    draw = ImageDraw.Draw(frame)
    x0, x1 = 161, 595
    def place(time):
        return round(x0 + (x1 - x0) * progress(time, 5.9, 8.35))

    badge(frame, 'Caption desk rehearsal')
    text(draw, 'Two feeds, one clock', 23, 75, 33)
    for label, y in (('Audio feed', 143), ('Caption feed', 211)):
        text(draw, label, 23, y, 18, MUTED)
        draw.line((x0, y, x1, y), fill=RULE, width=2)
    if t >= RARE_CUE:
        cx = place(RARE_CUE)
        draw.line((cx, 112, cx, 225), fill=GOLD, width=2)
        text(draw, '06.40', cx, 102, 18, GOLD, anchor='mm', weight='mono')
        for index in range(12):
            x = cx + index * 4
            amplitude = (12, 21, 33, 25, 19, 27, 21, 43, 24, 17, 21, 10)[index]
            draw.line((x, 143 - amplitude / 2, x, 143 + amplitude / 2), fill=GOLD, width=2)
        text(draw, 'Test tone', cx + 55, 143, 16, PAPER, weight='regular')
    if t >= RARE_CAPTION:
        out = place(RARE_CAPTION)
        draw.line((out, 111, out, 225), fill=MINT, width=2)
        text(draw, '07.80', out, 102, 18, MINT, anchor='mm', weight='mono')
        draw.rounded_rectangle((out + 3, 195, 602, 225), 4, fill=MINT)
        text(draw, 'Mina Rao', out + 12, 211, 16, INK)
        start = place(RARE_CUE)
        draw.line((start, 247, out, 247), fill=PAPER, width=2)
        for x in (start, out):
            draw.line((x, 240, x, 253), fill=PAPER, width=2)
        text(draw, '1.40 s', (start + out) / 2, 265, 24, PAPER, anchor='mm')
    else:
        head = place(t)
        draw.line((head, 221, head, 239), fill=PAPER, width=2)
    caption(frame, 'Wait for the caption to appear' if t < RARE_CAPTION else 'The caption follows the signal',
            'Controlled timing demonstration')
    return frame


def rare_access(t):
    if 5.9 <= t < 14.9:
        return feed_delay(t)
    if t >= 14.9:
        frame = ImageEnhance.Brightness(shot('notebook-live', min(2.9, (t - 14.9) * .38),
                                                1.1, -21, 4)).enhance(.53)
        draw = ImageDraw.Draw(frame)
        badge(frame, 'Caption desk rehearsal')
        draw.rounded_rectangle((267, 57, 616, 254), 9, fill='#f5ead0', outline=RULE, width=2)
        text(draw, 'Caption rundown', 287, 86, 24, INK)
        text(draw, '03  Guest welcome', 287, 119, 18, '#365449', weight='regular')
        draw.line((286, 140, 597, 140), fill='#b6b497', width=1)
        if t >= 17.0:
            length = round(289 * ease(progress(t, 17.0, 17.6)))
            draw.rectangle((286, 157, 286 + length, 208), fill=GOLD)
        text(draw, 'Mina Rao', 297, 182, 30, INK)
        text(draw, 'Sample name checked before going live', 287, 229, 17, '#365449', weight='regular')
        caption(frame, 'The first check happens before the cue', 'A known name is ready when it is needed.')
        return frame

    frame = ImageEnhance.Brightness(shot('editing-live', min(2.9, .25 + t * .54), 1.02, -21, 10)).enhance(.76)
    draw = ImageDraw.Draw(frame)
    feed_frame(draw, 'Rehearsal preview', 280, 56, 333, 191)
    frame.paste(shot('host-live', .17 + t * .42, 1.08, -24, 3, (307, 131)), (293, 94))
    draw.rectangle((297, 228, 591, 239), fill=INK)
    draw.line((300, 233, 326 + round(81 * progress(t, 0, 5.9)), 233), fill=MINT, width=3)
    badge(frame, 'Caption desk rehearsal')
    caption(frame, 'The words arrive on a separate clock', 'Illustrated desk and local stock footage')
    return frame


def caption_cue_tone(path):
    samples = array('h')
    for index in range(round(24 * RATE)):
        t = index / RATE - RARE_CUE
        level = .44 * sin(tau * 960 * t) * min(1, t * 550) * exp(-21 * t) if 0 <= t < .32 else 0
        samples.append(round(32767 * level))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as recording:
        recording.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        recording.writeframes(samples.tobytes())


def mystery(t):
    if t < 6.8:
        frame = shot('room', zoom=1.04 + t * .007, x=16, y=-9)
        draw = ImageDraw.Draw(frame, 'RGBA')
        badge(frame, 'Reconstructed edit')
        draw.rounded_rectangle((113, 211, 527, 254), 6, fill=(0, 0, 0, 229))
        text(draw, 'Guide: Doors open at nine.', 320, 233, 25, anchor='mm')
        caption(frame, 'That caption belongs to a voice we can’t hear', 'The program audio is silent at this cue.', size=26)
        return frame

    if t < 16.0:
        frame = Image.new('RGB', (W, H), INK)
        draw = ImageDraw.Draw(frame)
        badge(frame, 'Reconstructed edit')
        text(draw, 'Check the original cue', 25, 76, 32)
        text(draw, '00:04.20', 611, 76, 22, MINT, anchor='rm', weight='mono')
        for title, y in (('EN subtitles', 110), ('Program audio', 181)):
            draw.rounded_rectangle((24, y, 616, y + 61), 6, fill=PANEL, outline=RULE)
            text(draw, title, 38, y + 32, 16)
        draw.rounded_rectangle((199, 122, 449, 158), 4, fill='#cae8cc')
        text(draw, 'Guide: Doors open at nine.', 212, 141, 17, INK)
        draw.line((186, 212, 600, 212), fill=MUTED, width=2)
        x = round(189 + 17 * ease(progress(t, 6.8, 7.6)))
        draw.line((x, 108, x, 249), fill=GOLD, width=2)
        text(draw, 'No speech signal', 603, 250, 17, MINT, anchor='rm')
        caption(frame, 'The cue exists. The program track is flat.', 'The two lanes refer to the same moment.')
        return frame

    frame = ImageEnhance.Brightness(shot('editing-live', min(2.8, .4 + (t - 16.0) * .31), 1.03)).enhance(.45)
    draw = ImageDraw.Draw(frame)
    badge(frame, 'Reconstructed edit')
    feed_frame(draw, 'Source check', 67, 62, 506, 191)
    text(draw, 'Program mix', 87, 122, 21)
    text(draw, 'Silent here', 552, 122, 19, MUTED, anchor='rm')
    draw.line((88, 151, 551, 151), fill=RULE, width=1)
    if t >= 17.1:
        draw.rounded_rectangle((87, 165, 554, 226), 5, fill=MINT)
        text(draw, 'Guide’s separate recording', 101, 196, 21, INK)
        text(draw, 'Check next', 538, 196, 17, INK, anchor='rm')
    caption(frame, 'Find the speaker’s original recording', 'The opening leaves the cause open.')
    return frame


def personal_stakes(t):
    if t < 7.3:
        frame = ImageEnhance.Brightness(shot('editing-live', min(2.98, .11 + t * .44), 1.04, -12, 9)).enhance(.76)
        draw = ImageDraw.Draw(frame)
        badge(frame, 'Staged schedule')
        if t >= 3.2:
            feed_frame(draw, 'Thursday', 377, 83, 231, 107)
            text(draw, '19:00', 394, 147, 28, GOLD, weight='mono')
            text(draw, 'Film', 590, 147, 23, PAPER, anchor='rm')
        caption(frame, 'I want evenings with my family again', 'A creator looks at the time their filming takes.')
        return frame

    if t < 16.4:
        frame = Image.new('RGB', (W, H), '#ece6d1')
        draw = ImageDraw.Draw(frame)
        badge(frame, 'Staged schedule')
        text(draw, 'Protect the evening', 25, 80, 35, INK)
        for x, day, time in ((22, 'Thursday', '19:00'), (326, 'Saturday', '09:00')):
            draw.rounded_rectangle((x, 110, x + 290, 249), 7, fill='#f9f1d9', outline='#809688', width=1)
            text(draw, day, x + 14, 135, 22, INK)
            text(draw, time, x + 15, 173, 31, INK, weight='mono')
        draw.rounded_rectangle((36, 197, 298, 235), 6, fill='#d8e8d7')
        text(draw, 'Family time', 49, 216, 21, INK)
        if t >= 9.1:
            amount = ease(progress(t, 9.1, 9.55))
            x = round(341 + 42 * (1 - amount))
            draw.rounded_rectangle((x, 197, x + 257, 235), 6, fill=GOLD)
            text(draw, 'Film', x + 13, 216, 21, INK)
        caption(frame, 'Move the shoot to Saturday morning', 'The schedule protects a specific block of time.')
        return frame

    frame = (shot('room', zoom=1.05 + .04 * progress(t, 16.4, 18.9), x=-38, y=3)
             if t < 18.9 else shot('host-live', min(3.1, .28 + (t - 18.9) * .43), 1.14, 44, -8))
    badge(frame, 'Staged schedule')
    draw = ImageDraw.Draw(frame, 'RGBA')
    draw.rounded_rectangle((343, 67, 609, 200), 8, fill=(14, 37, 30, 241), outline=RULE, width=2)
    text(draw, 'Next shoot', 362, 94, 20, MINT)
    text(draw, 'Saturday, 09:00', 362, 129, 27)
    if t >= 18.9:
        draw.ellipse((364, 161, 377, 174), fill=GOLD)
        text(draw, 'Take 01', 385, 168, 20, PAPER, weight='mono')
    caption(frame, 'Start the next shoot inside the new rule', 'The rest of the episode shows what the change costs.')
    return frame


def decisive_moment(t):
    if t < 17.5:
        # Keep the actual stream far enough from its finish to leave the outcome open.
        if t < 7.0:
            frame = shot('coffee-live', .24 + min(t, 6.9) * .095)
            marker = (282, 149)
        else:
            area = (100, 26, 460, 228.5)
            sample_time = .90 + .032 * (min(t, 17.0) - 7.0) + max(0.0, t - 17.0)
            frame = shot('coffee-live', sample_time).transform((W, H), Image.Transform.EXTENT,
                                                               area, Image.Resampling.BICUBIC)
            marker = (324, 218)
        badge(frame, 'Staged fill test')
        draw = ImageDraw.Draw(frame)
        x, y = marker
        for start in range(x, x + 78, 12):
            draw.line((start, y, start + 6, y), fill=GOLD, width=3)
        draw.line(((x + 78, y), (x + 98, y - 22), (x + 115, y - 22)), fill=GOLD, width=2)
        draw.rounded_rectangle((x + 114, y - 36, x + 270, y - 7), 5, fill=INK)
        text(draw, 'Illustrated target', x + 125, y - 21, 17, GOLD)
        if t < 7.0:
            caption(frame, 'Our test ends when this reaches the mark', 'Slow check at the target level')
        else:
            caption(frame, 'Stay with the approach to the line', 'Cut before seeing how the attempt ends.')
        return frame

    if t < 17.86:
        return Image.new('RGB', (W, H), '#141c18')

    frame = Image.new('RGB', (W, H), '#ede7d0')
    draw = ImageDraw.Draw(frame)
    badge(frame, 'Earlier · setup drawing')
    glass = ((134, 96), (159, 240), (265, 240), (294, 96))
    draw.polygon(glass, fill='#d9efe4', outline='#2f6758', width=3)
    draw.ellipse((134, 77, 295, 108), fill='#e8f2e9', outline='#2f6758', width=3)
    draw.arc((159, 226, 265, 252), 0, 180, fill='#2f6758', width=3)
    stage = ease(progress(t, 18.0, 20.0))
    draws_to = round(147 + stage * 133)
    if draws_to > 151:
        draw.line((147, 132, draws_to, 132), fill='#ad562d', width=4)
    if t >= 19.5:
        draw.line((279, 132, 317, 115, 350, 115), fill='#ad562d', width=2)
    text(draw, 'Mark the empty glass', 345, 96, 24, INK)
    text(draw, 'Keep the camera', 345, 161, 20, '#365449', weight='regular')
    text(draw, 'at the same height.', 345, 190, 20, '#365449', weight='regular')
    caption(frame, 'Earlier, when the mark was set', 'The body returns to the same pour for the result.')
    return frame


SCENES = {
    'hook-long-rare-access-032': rare_access,
    'hook-long-mystery-038': mystery,
    'hook-long-personal-stakes-021': personal_stakes,
    'hook-long-decisive-moment-064': decisive_moment,
}

POSTERS = {
    'hook-long-rare-access-032': 1.0,
    'hook-long-mystery-038': 0.5,
    'hook-long-personal-stakes-021': 4.0,
    'hook-long-decisive-moment-064': .5,
}

AUDIO = {'hook-long-rare-access-032': caption_cue_tone}
