"""Original widescreen demonstrations with a source note and a paper-dial prototype."""

from functools import lru_cache

from PIL import Image, ImageDraw

from preview_common import H, W, font


INK = '#172e29'
PAPER = '#f7f0dc'
SURFACE = '#e3e9df'
TEAL = '#276654'
LIGHT_TEAL = '#cce5cc'
ORANGE = '#ef9062'
MUTED = '#4a6259'
BLUE = '#245179'
REGISTRATION = '#52705d'
SIZE = (W, H)
CLAUSE = 'only while a guide is present'


def text(draw, at, words, size, fill=INK, anchor='lm', weight='bold'):
    draw.text(at, words, font=font(size, weight), fill=fill, anchor=anchor)


def source_crop(draw, x, style):
    draw.rounded_rectangle((x + 2, 94, x + 295, 267), 7, fill='#c1cdc2')
    draw.rounded_rectangle((x, 90, x + 293, 263), 7, fill=PAPER, outline='#cfcbba')
    text(draw, (x + 15, 108), 'PRACTICE NOTE · ROOM ACCESS', 13, MUTED)
    draw.line((x + 15, 123, x + 278, 123), fill='#d8d1bd')
    left = x + 15
    right = left + round(font(19).getlength(CLAUSE)) - 1
    if style == 'block':
        draw.rectangle((left, 176, right, 200), fill='#baddae')
    text(draw, (left, 152), 'The studio door stays open', 19)
    text(draw, (left, 188), CLAUSE + '.', 19)
    if style == 'underline':
        draw.line((left, 201, right, 201), fill=TEAL, width=2)
    text(draw, (left, 225), 'Visitors sign in at reception.', 19, MUTED, weight='regular')


def clause_emphasis(t):
    frame = Image.new('RGB', SIZE, SURFACE)
    draw = ImageDraw.Draw(frame)
    if t < 14.8:
        title = 'Which mark points to the exact source phrase?'
        if t >= 6.1:
            title = 'Which words support the narration?'
        text(draw, (24, 33), title, 25)
        text(draw, (21, 72), 'A   Thin underline', 18, TEAL)
        text(draw, (326, 72), 'B   One block', 18, TEAL)
        source_crop(draw, 21, 'underline')
        source_crop(draw, 326, 'block')
        draw.rectangle((0, 286, W, H), fill=INK)
        if t < 6.1:
            text(draw, (25, 323), 'Same source excerpt and display size.', 23, PAPER)
        else:
            text(draw, (25, 309), 'Narration to check', 15, LIGHT_TEAL)
            text(draw, (25, 336), '“The door can stay open only with a guide there.”', 21, PAPER)
        return frame

    text(draw, (24, 34), 'Check where each mark starts and ends.', 27)
    draw.rounded_rectangle((23, 65, 617, 278), 7, fill=PAPER)
    left = 89
    right = left + round(font(29).getlength(CLAUSE)) - 1
    text(draw, (left, 103), 'The studio door stays open', 25, MUTED, weight='regular')
    text(draw, (left, 154), CLAUSE + '.', 29)
    draw.line((left, 198, right, 198), fill=TEAL, width=2)
    draw.rectangle((left, 228, right, 241), fill='#baddae')
    for x in (left, right):
        draw.line((x, 177, x, 256), fill='#6b8476', width=1)
    text(draw, (right + 20, 198), 'Underline', 18, TEAL)
    text(draw, (right + 20, 235), 'Block', 18, TEAL)
    draw.rectangle((0, 298, W, H), fill=INK)
    text(draw, (24, 326), 'Listen for “only while” in each viewer’s answer.', 24, PAPER)
    return frame


@lru_cache(maxsize=1)
def wheel():
    image = Image.new('RGBA', (222, 222))
    draw = ImageDraw.Draw(image)
    circle = (5, 5, 216, 216)
    for i, color in enumerate(('#c6ddf0', '#e8f0f0', '#87b3d9', '#dae8ef')):
        draw.pieslice(circle, start=i * 90, end=(i + 1) * 90, fill=color, outline=BLUE, width=2)
    draw.ellipse(circle, outline=BLUE, width=3)
    for at, letter in zip(((169, 168), (51, 168), (51, 52), (169, 52)), 'ABCD'):
        text(draw, at, letter, 35, BLUE, 'mm')
    draw.ellipse((105, 105, 116, 116), fill=BLUE)
    return image


def strip(draw, x, y):
    draw.rounded_rectangle((x - 7, y - 9, x + 127, y + 9), 6, fill='#8e453a')
    draw.rounded_rectangle((x - 6, y - 8, x + 126, y + 7), 5, fill=ORANGE)
    draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=INK)
    draw.ellipse((x + 113, y - 3, x + 119, y + 3), fill=INK)


def paper_pointer(t):
    frame = Image.new('RGB', SIZE, SURFACE)
    draw = ImageDraw.Draw(frame)
    if t < 13.8:
        text(draw, (23, 29), 'The pointer stays still as the card spins.', 26)
        draw.rounded_rectangle((20, 58, 381, 337), 11, fill='#a6b8af')
        draw.rounded_rectangle((20, 56, 379, 333), 10, fill='#c5cfc2', outline='#879b8e')
        cx, cy = 180, 194
        draw.ellipse((cx - 105, cy - 101, cx + 105, cy + 111), fill='#a9bcaf')
        moving = wheel().rotate(-t * 360 / 5.6, Image.Resampling.BICUBIC)
        frame.paste(moving, (cx - 111, cy - 111), moving)
        if t >= 5.6:
            draw.line((cx + 136, cy, 366, cy), width=4, fill='#8e453a')
            draw.line((356, cy - 10, 356, cy + 10), width=2, fill='#8e453a')
        strip(draw, cx, cy)
        text(draw, (405, 91), 'Animated paper model', 18, MUTED)
        draw.rounded_rectangle((405, 137, 423, 155), 3, fill=ORANGE)
        text(draw, (433, 146), 'Fixed pointer', 21)
        draw.rounded_rectangle((405, 178, 423, 196), 3, fill=BLUE)
        text(draw, (433, 187), 'Rotating wheel', 21)
        if t >= 5.6:
            text(draw, (405, 254), 'Board mark and pointer', 17, MUTED)
            text(draw, (405, 280), 'stay aligned.', 21, '#8e453a')
        return frame

    text(draw, (23, 28), 'Before assembly', 30)
    text(draw, (28, 68), 'Paper layer 1 · Wheel', 20, BLUE)
    text(draw, (358, 68), 'Paper layer 2 · Pointer', 20, '#8e453a')
    moving = wheel().rotate(-13.8 * 360 / 5.6, Image.Resampling.BICUBIC)
    frame.paste(moving, (68, 87), moving)
    draw.rounded_rectangle((350, 109, 601, 269), 6, fill=PAPER, outline='#c5bda9')
    strip(draw, 393, 182)
    draw.line((179, 198, 393, 182), fill='#587a6a', width=2)
    for x, y in ((179, 198), (393, 182)):
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=REGISTRATION)
    text(draw, (415, 221), 'Fix this end to the board.', 15, MUTED)
    draw.line((510, 194, 510, 209), fill='#8e453a', width=2)
    draw.rectangle((0, 314, W, H), fill=INK)
    text(draw, (24, 336), 'First, register both layers on the center hole.', 24, PAPER)
    return frame


SCENES = {
    'hook-long-head-to-head-030': clause_emphasis,
    'hook-long-result-first-024': paper_pointer,
}
POSTERS = {
    'hook-long-head-to-head-030': 0,
    'hook-long-result-first-024': 7.2,
}
