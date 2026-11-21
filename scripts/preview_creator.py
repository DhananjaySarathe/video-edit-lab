"""Previews for the talking-head hooks and the edit moves.

Every preview is built from the licensed stock plates. A stand-in presenter plays the creator, the on-screen text and
captions come from the hook itself, and the edit move is applied on top: punch-ins, jump cuts, cutaways, receipts,
phone inserts, split screens, slams, freezes, counters and sound.
"""
from array import array
from functools import lru_cache
import json
import math
from pathlib import Path
import random
import sys
import wave

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from preview_common import ease, font, progress
from preview_plates import FRAME_RATE, movie

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / 'src' / 'creator-hooks'
FPS = FRAME_RATE
VERTICAL, WIDE = (360, 640), (640, 360)
RATE = 24000

ACCENT = (255, 212, 0)
WHITE = (255, 255, 255)
INK = (16, 16, 16)
SOFT = (238, 240, 243)

# Face position (fraction of the source frame) for each presenter plate.
FACE = {'host-live': (0.435, 0.2), 'portrait-live': (0.47, 0.24)}
# Where the interesting part of each plate sits.
PLATE_FOCUS = {
    'phone-live': (0.39, 0.5), 'editing-live': (0.5, 0.36), 'coffee-live': (0.38, 0.55),
    'cooking-live': (0.5, 0.45), 'workshop-live': (0.5, 0.48), 'camera-live': (0.5, 0.5),
    'notebook-live': (0.62, 0.55), 'sewing-live': (0.6, 0.55), 'walk-live': (0.62, 0.62),
    'steps-live': (0.55, 0.6),
}
# Where a zoom-to-detail lands in each plate.
ZOOM_TARGET = {
    'editing-live': (0.42, 0.22), 'phone-live': (0.39, 0.45), 'camera-live': (0.48, 0.42),
    'sewing-live': (0.66, 0.62), 'notebook-live': (0.7, 0.62), 'workshop-live': (0.48, 0.5),
    'coffee-live': (0.33, 0.62), 'cooking-live': (0.48, 0.5),
}
NUMBER_WORDS = {
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'fifteen',
    'twenty', 'thirty', 'forty', 'fifty', 'hundred', 'thousand', 'million', 'zero', 'half', 'nineteen', 'eighty',
}
STOP_WORDS = {'the', 'a', 'an', 'and', 'to', 'of', 'in', 'is', 'it', 'you', 'your', 'my', 'i', 'on', 'for', 'this',
              'that', 'at', 'with', 'not', 'one', 'no'}


def clean(word):
    return ''.join(ch for ch in word.lower() if ch.isalnum())


def frame(name, t):
    frames = movie(name)
    return frames[int(round(t * FPS)) % len(frames)]


def fill(image, size, zoom=1.0, focus=(0.5, 0.5)):
    """Crop an image to fill size, zoomed around a focus point and clamped to the frame."""
    w, h = size
    iw, ih = image.size
    scale = max(w / iw, h / ih) * zoom
    cw, ch = w / scale, h / scale
    x0 = min(max(focus[0] * iw - cw / 2, 0), iw - cw)
    y0 = min(max(focus[1] * ih - ch / 2, 0), ih - ch)
    return image.transform(size, Image.Transform.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.Resampling.BICUBIC)


def wrap(draw, text, face, width):
    """Greedy wrap, then rebalance two-line results so one word never sits alone."""
    lines = _greedy(draw, text, face, width)
    if len(lines) == 2:
        words = text.split()
        best = None
        for cut in range(1, len(words)):
            a, b = ' '.join(words[:cut]), ' '.join(words[cut:])
            widest = max(draw.textlength(a, font=face), draw.textlength(b, font=face))
            if widest <= width and (best is None or widest < best[0]):
                best = (widest, [a, b])
        if best:
            lines = best[1]
    return lines


def _greedy(draw, text, face, width):
    lines, line = [], ''
    for word in text.split():
        trial = f'{line} {word}'.strip()
        if line and draw.textlength(trial, font=face) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def chip(img, text, xy, *, fill_color=WHITE, color=INK, size=13, anchor='la', weight='black', pad=(8, 5)):
    draw = ImageDraw.Draw(img)
    face = font(size, weight)
    tw = draw.textlength(text, font=face)
    th = size
    x, y = xy
    if anchor[0] == 'r':
        x -= tw + pad[0] * 2
    elif anchor[0] == 'm':
        x -= (tw + pad[0] * 2) / 2
    draw.rounded_rectangle((x, y, x + tw + pad[0] * 2, y + th + pad[1] * 2), radius=5, fill=fill_color)
    draw.text((x + pad[0], y + pad[1] + th / 2 + 1), text, font=face, fill=color, anchor='lm')
    return (x, y, x + tw + pad[0] * 2, y + th + pad[1] * 2)


# ---------------------------------------------------------------- generic receipts (no real brands)

def avatar(draw, box, color):
    draw.ellipse(box, fill=color)


def gray_lines(draw, x, y, width, rows, gap=13, color=(214, 218, 224)):
    for i in range(rows):
        draw.rounded_rectangle((x, y + i * gap, x + width * (0.94 if i % 3 else 0.72), y + i * gap + 6), 3, fill=color)


@lru_cache(maxsize=64)
def receipt(kind, note, w, h, dark=False):
    """Draw a generic interface card. Returns the card and the box to highlight."""
    bg = (24, 26, 30) if dark else WHITE
    fg = (240, 240, 240) if dark else INK
    sub = (150, 156, 166) if dark else (110, 116, 126)
    card = Image.new('RGB', (w, h), bg)
    draw = ImageDraw.Draw(card)
    s = w / 300
    pad = round(16 * s)
    big, mid, small = font(19 * s, 'bold'), font(14 * s, 'bold'), font(12 * s, 'regular')
    mark = (pad, pad, pad, pad)
    if kind == 'comment':
        avatar(draw, (pad, pad, pad + 30 * s, pad + 30 * s), (120, 160, 230))
        draw.text((pad + 40 * s, pad + 2 * s), 'viewer_204', font=mid, fill=fg)
        draw.text((pad + 40 * s, pad + 20 * s), '2 days ago', font=small, fill=sub)
        lines = wrap(draw, note, big, w - pad * 2)
        y = pad + 46 * s
        for line in lines:
            draw.text((pad, y), line, font=big, fill=fg)
            y += 25 * s
        mark = (pad - 4, pad + 42 * s, pad + max(draw.textlength(l, font=big) for l in lines) + 4, y + 2)
        draw.text((pad, y + 10 * s), '♥ 1,284    Reply', font=mid, fill=sub)
    elif kind == 'post':
        avatar(draw, (pad, pad, pad + 26 * s, pad + 26 * s), (230, 140, 120))
        draw.text((pad + 34 * s, pad + 13 * s), 'yourhandle', font=mid, fill=fg, anchor='lm')
        top, bottom = pad + 38 * s, h - 66 * s
        grad = Image.linear_gradient('L').resize((w - pad * 2, max(4, round(bottom - top))))
        tile = ImageOps.colorize(grad, (255, 196, 120), (214, 92, 120))
        card.paste(tile, (pad, round(top)))
        draw.text((w / 2, (top + bottom) / 2), '▶', font=font(40 * s, 'bold'), fill=(255, 255, 255), anchor='mm')
        draw.text((pad, bottom + 12 * s), '♥ 2.1k   ✉ 316', font=mid, fill=fg)
        draw.text((pad, bottom + 34 * s), note, font=mid, fill=fg)
        mark = (pad - 4, bottom + 30 * s, pad + draw.textlength(note, font=mid) + 4, bottom + 52 * s)
    elif kind == 'article':
        draw.rectangle((0, 0, w, 30 * s), fill=(30, 30, 30) if not dark else (60, 60, 60))
        draw.text((pad, 15 * s), 'THE DAILY', font=font(13 * s, 'serif'), fill=(255, 255, 255), anchor='lm')
        lines = wrap(draw, note, font(22 * s, 'serif'), w - pad * 2)
        y = 46 * s
        for line in lines:
            draw.text((pad, y), line, font=font(22 * s, 'serif'), fill=fg)
            y += 28 * s
        mark = (pad - 4, 44 * s, w - pad, y + 2)
        gray_lines(draw, pad, y + 14 * s, w - pad * 2, 6, gap=13 * s)
    elif kind == 'dm':
        draw.text((w / 2, pad + 6 * s), 'Messages', font=mid, fill=fg, anchor='mm')
        draw.line((0, pad + 22 * s, w, pad + 22 * s), fill=(200, 204, 210) if not dark else (60, 62, 66))
        y = pad + 36 * s
        bubble = (236, 238, 241) if not dark else (52, 54, 60)
        lines = wrap(draw, note, mid, w * 0.62)
        bh = len(lines) * 19 * s + 16 * s
        bw = max(draw.textlength(l, font=mid) for l in lines) + 22 * s
        draw.rounded_rectangle((pad, y, pad + bw, y + bh), radius=14 * s, fill=bubble)
        for i, line in enumerate(lines):
            draw.text((pad + 11 * s, y + 8 * s + i * 19 * s), line, font=mid, fill=fg)
        mark = (pad - 3, y - 3, pad + bw + 3, y + bh + 3)
        y += bh + 12 * s
        draw.rounded_rectangle((w - pad - 120 * s, y, w - pad, y + 30 * s), radius=14 * s, fill=(52, 120, 246))
        draw.text((w - pad - 60 * s, y + 15 * s), 'one sec', font=mid, fill=WHITE, anchor='mm')
        y += 42 * s
        for i in range(3):
            draw.ellipse((pad + 12 * s + i * 12 * s, y, pad + 19 * s + i * 12 * s, y + 7 * s), fill=sub)
    elif kind == 'chart':
        draw.text((pad, pad), note, font=big, fill=fg)
        x0, y0, x1, y1 = pad, pad + 40 * s, w - pad, h - pad - 10 * s
        for i in range(4):
            yy = y0 + (y1 - y0) * i / 3
            draw.line((x0, yy, x1, yy), fill=(225, 228, 232) if not dark else (55, 58, 64))
        falling = any(word in note.lower() for word in ('watching', 'balance', 'screen'))
        pts = []
        for i in range(9):
            x = x0 + (x1 - x0) * i / 8
            v = (1 - i / 8) ** 1.6 if falling else (i / 8) ** 1.7
            wobble = 0.05 * math.sin(i * 1.9)
            pts.append((x, y1 - (y1 - y0) * (0.08 + 0.84 * max(0, min(1, v + wobble)))))
        draw.line(pts, fill=(229, 72, 77) if falling else (36, 168, 98), width=max(2, round(4 * s)), joint='curve')
        draw.ellipse((pts[-1][0] - 5 * s, pts[-1][1] - 5 * s, pts[-1][0] + 5 * s, pts[-1][1] + 5 * s),
                     fill=(229, 72, 77) if falling else (36, 168, 98))
        mark = (pts[-3][0] - 10, min(p[1] for p in pts[-3:]) - 12, x1 + 4, max(p[1] for p in pts[-3:]) + 12)
    elif kind == 'receipt':
        draw.text((pad, pad), 'INVOICE', font=big, fill=fg)
        draw.text((w - pad, pad + 4 * s), '#014', font=mid, fill=sub, anchor='ra')
        y = pad + 40 * s
        for label in ('Design work', 'Revisions', note, 'Tax'):
            highlight = label == note
            draw.text((pad, y), label, font=mid if highlight else small, fill=fg if highlight else sub)
            draw.text((w - pad, y), '—' if highlight else '···', font=mid, fill=fg, anchor='ra')
            if highlight:
                mark = (pad - 4, y - 4, w - pad + 4, y + 20 * s)
            y += 28 * s
        draw.line((pad, y, w - pad, y), fill=(200, 204, 210))
        draw.text((pad, y + 10 * s), 'Total due', font=mid, fill=fg)
    elif kind == 'calendar':
        draw.text((pad, pad), 'Today', font=big, fill=fg)
        y0 = pad + 36 * s
        for i, hour in enumerate(('9 AM', '11 AM', '1 PM', '3 PM', '5 PM', '7 PM')):
            yy = y0 + i * 30 * s
            draw.text((pad, yy), hour, font=small, fill=sub)
            draw.line((pad + 46 * s, yy + 6 * s, w - pad, yy + 6 * s), fill=(225, 228, 232) if not dark else (55, 58, 64))
        for i, (row, span) in enumerate(((0, 1), (1.4, .8), (2.6, .6), (3.4, 1.1))):
            top = y0 + row * 30 * s + 8 * s
            draw.rounded_rectangle((pad + 52 * s, top, w - pad, top + span * 30 * s - 3), radius=5,
                                   fill=(186, 214, 255) if not dark else (60, 90, 140))
            draw.text((pad + 60 * s, top + 6 * s), note, font=small, fill=fg)
        mark = (pad + 48 * s, y0 + 8 * s - 3, w - pad + 3, y0 + 38 * s)
    elif kind == 'files':
        draw.text((pad, pad), 'Projects', font=big, fill=fg)
        y = pad + 38 * s
        for name in ('final.mp4', 'final_v2.mp4', note + '.mp4', 'final_REAL.mp4', 'use_this_one.mp4'):
            highlight = name.startswith(note)
            draw.rounded_rectangle((pad, y + 2 * s, pad + 16 * s, y + 16 * s), 3, fill=(120, 150, 210))
            draw.text((pad + 26 * s, y), name, font=mid if highlight else small, fill=fg if highlight else sub)
            if highlight:
                mark = (pad - 4, y - 4, w - pad, y + 22 * s)
            y += 28 * s
    elif kind == 'checklist':
        draw.text((pad, pad), note, font=big, fill=fg)
        y = pad + 40 * s
        for i in range(6):
            draw.rounded_rectangle((pad, y, pad + 16 * s, y + 16 * s), 3, outline=sub, width=2)
            if i < 4:
                draw.line((pad + 3 * s, y + 8 * s, pad + 7 * s, y + 13 * s, pad + 14 * s, y + 3 * s), fill=(36, 168, 98), width=3)
            draw.rounded_rectangle((pad + 26 * s, y + 5 * s, pad + 26 * s + (w - pad * 3) * (0.5 + 0.08 * (i % 3)),
                                    y + 11 * s), 3, fill=(214, 218, 224) if not dark else (70, 74, 80))
            y += 27 * s
        mark = (pad - 4, pad - 4, w - pad, pad + 28 * s)
    return card, tuple(round(v) for v in mark)


# ---------------------------------------------------------------- plan

class Plan:
    """Everything one preview needs: timing, layout and which shots to use."""

    def __init__(self, hook, mode, index, demo=False):
        self.hook = hook
        self.demo = demo
        self.wide = mode == 'long'
        self.size = WIDE if self.wide else VERTICAL
        self.W, self.H = self.size
        self.move = hook['move']
        self.preset = hook['for'][0]
        self.cut = hook.get('cut')
        self.prop = hook.get('prop')
        self.note = hook.get('note', '')
        self.text = hook.get('text')
        if self.preset == 'podcast':
            self.presenter, self.other = 'portrait-live', 'host-live'
        else:
            self.presenter = 'host-live' if (self.wide or index % 2 == 0) else 'portrait-live'
            self.other = 'portrait-live' if self.presenter == 'host-live' else 'host-live'
        if self.preset in ('faceless', 'product', 'vlog'):
            self.main = 'plate'
        elif self.preset == 'podcast' and self.wide:
            self.main = 'podcast'
        else:
            self.main = 'presenter'
        self.words = hook['say'].split()
        count = len(self.words)
        self.speech = min(5.4, max(2.6, count / 3.0))
        self.dur = round((self.speech + 0.75) * FPS) / FPS
        start, end = 0.12, 0.12 + self.speech
        weights = [len(clean(word)) + 2 for word in self.words]
        total, acc, self.times = sum(weights), 0, []
        for weight in weights:
            self.times.append(start + (end - start) * acc / total)
            acc += weight
        self.speech_end = end
        self.ts = self.stress_time()
        # The lead is the face shot before the layout changes.
        lead_moves = {'green-screen', 'inside-device', 'split-screen', 'zoom-to-detail', 'freeze-frame'}
        self.lead = 0.0
        if self.main != 'plate' and self.move in lead_moves and (self.cut or self.prop or self.move == 'inside-device'):
            self.lead = 0.75
        if self.move == 'split-screen' and not self.cut:
            self.lead = 0.0
        if self.move == 'zoom-to-detail' or self.move == 'freeze-frame':
            self.ts = max(self.ts, self.lead + 0.6)
        self.ts = min(self.ts, self.dur - 1.0)
        self.text_end = min(self.dur - 0.2, 2.9)
        self.tail = 1.6 if demo else 0.0
        self.total = round((self.dur + self.tail) * FPS) / FPS
        self.sound = self.move in ({'sfx-layer'} if not demo else
                                   {'sfx-layer', 'kinetic-slam', 'freeze-frame', 'rehook', 'reaction-insert'})

    def stress_time(self):
        text_words = {clean(word) for word in (self.text or self.note or '').split()} - STOP_WORDS
        for word, at in zip(self.words, self.times):
            key = clean(word)
            if at < 0.7 or not key:
                continue
            if any(ch.isdigit() for ch in key) or key in NUMBER_WORDS or key in text_words:
                return at
        return self.times[min(len(self.times) - 1, int(len(self.times) * 0.45))]

    @property
    def poster(self):
        if self.move in ('green-screen', 'inside-device', 'split-screen'):
            return max(self.lead + 0.5, min(self.ts + 0.4, self.dur - 0.3))
        if self.move == 'kinetic-slam':
            return self.ts + 0.3
        if self.move in ('zoom-to-detail',):
            return self.ts + 0.7
        return max(0.9, min(self.ts + 0.35, self.dur - 0.3))


# ---------------------------------------------------------------- shots

def presenter_focus(plan, name, zoom):
    fx, fy = FACE[name]
    lift = 0.2 if not plan.wide else 0.16
    return fx, fy + lift / zoom


def presenter_shot(plan, t, zoom=1.0, name=None, size=None, rhythm=True):
    name = name or plan.presenter
    size = size or plan.size
    jump = plan.move == 'jump-cut'
    seg = 0.85 if jump else 1.5
    k = int(t // seg) if rhythm else 0
    local = t - k * seg
    src = (k * 0.55) % max(0.1, 3.1 - seg) + local
    if rhythm:
        zoom *= (1.0, 1.14 if jump else 1.07)[k % 2]
    fx, fy = presenter_focus(plan, name, zoom)
    if jump and k % 2:
        fx += 0.035 if k % 4 == 1 else -0.035
    return fill(frame(name, src), size, zoom, (fx, fy))


def plate_shot(plan, name, t, zoom=1.0, size=None, focus=None, offset=0.0):
    size = size or plan.size
    if name == 'phone-live':
        return fill(phone_frame(plan, t + offset), size, zoom, focus or PLATE_FOCUS['phone-live'])
    seg = 1.6
    k = int(t // seg)
    src = (k * 0.6) % 1.4 + (t - k * seg) + offset
    return fill(frame(name, src), size, zoom, focus or PLATE_FOCUS.get(name, (0.5, 0.5)))


def podcast_two_up(plan, t, zoom=1.0):
    canvas = Image.new('RGB', plan.size, (14, 14, 16))
    w = (plan.W - 6) // 2
    left = fill(frame('host-live', t), (w, plan.H), 1.0 * zoom, (0.435, 0.42))
    right = fill(frame('portrait-live', t + 0.4), (w, plan.H), 1.05 * zoom, (0.47, 0.45))
    canvas.paste(left, (0, 0))
    canvas.paste(right, (w + 6, 0))
    return canvas


def punch(plan, t):
    if plan.move in ('punch-in', 'sfx-layer'):
        strength = 0.22 if plan.move == 'punch-in' else 0.14
        return 1 + strength * ease(progress(t, plan.ts - 0.03, plan.ts + 0.07))
    return 1.0


def main_shot(plan, t, zoom=1.0):
    zoom *= punch(plan, t)
    if plan.main == 'plate':
        return plate_shot(plan, plan.cut, t, zoom)
    if plan.main == 'podcast':
        return podcast_two_up(plan, t, zoom)
    if plan.lead and t >= plan.lead and plan.cut and plan.move in ('zoom-to-detail', 'freeze-frame'):
        return plate_shot(plan, plan.cut, t, zoom)
    return presenter_shot(plan, t, zoom, rhythm=plan.move not in ('punch-in',) or t < plan.ts)


def treat(image, before):
    if before:
        image = ImageEnhance.Color(image).enhance(0.35)
        image = ImageEnhance.Contrast(image).enhance(0.8)
        return ImageEnhance.Brightness(image).enhance(0.9).filter(ImageFilter.GaussianBlur(0.7))
    image = ImageEnhance.Color(image).enhance(1.18)
    return ImageEnhance.Contrast(image).enhance(1.06)


def split_shot(plan, t):
    canvas = Image.new('RGB', plan.size, WHITE)
    labels = (plan.note or 'BEFORE|AFTER').split('|')
    if plan.wide:
        half = ((plan.W - 4) // 2, plan.H)
        spots = ((0, 0), (half[0] + 4, 0))
    else:
        half = (plan.W, (plan.H - 4) // 2)
        spots = ((0, 0), (0, half[1] + 4))
    for i, spot in enumerate(spots):
        if plan.cut:
            picture = treat(plate_shot(plan, plan.cut, t, 1.0, size=half, offset=0.5 * i), before=i == 0)
        else:
            name = ('portrait-live', 'host-live')[i]
            picture = fill(frame(name, t + 0.3 * i), half, 1.05, presenter_focus(plan, name, 1.05))
        canvas.paste(picture, spot)
        label_in = progress(t, plan.lead + 0.1 + 0.15 * i, plan.lead + 0.25 + 0.15 * i)
        if label_in > 0:
            chip(canvas, labels[min(i, len(labels) - 1)], (spot[0] + 12, spot[1] + 12 + round(6 * (1 - ease(label_in)))),
                 fill_color=ACCENT if i else WHITE, size=18)
    return canvas


def blurred_backdrop(plan, t):
    base = main_shot(plan, min(t, plan.lead)) if plan.main != 'plate' else plate_shot(plan, plan.cut, t)
    base = base.resize((plan.W // 6, plan.H // 6)).filter(ImageFilter.GaussianBlur(2)).resize(plan.size)
    return ImageEnhance.Brightness(base).enhance(0.45)


def face_circle(plan, t, radius):
    if plan.main == 'plate':
        picture = fill(frame(plan.cut, t), (radius * 2, radius * 2), 1.2, PLATE_FOCUS.get(plan.cut, (0.5, 0.5)))
    else:
        name = plan.presenter
        fx, fy = FACE[name]
        picture = fill(frame(name, t), (radius * 2, radius * 2), 2.2 if name == 'host-live' else 1.6, (fx, fy + 0.08))
    mask = Image.new('L', (radius * 8, radius * 8), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, radius * 8 - 1, radius * 8 - 1), fill=255)
    return picture, mask.resize((radius * 2, radius * 2), Image.Resampling.LANCZOS)


def receipt_layout(plan, t):
    canvas = blurred_backdrop(plan, t)
    if plan.wide:
        box = (round(plan.W * 0.05), round(plan.H * 0.27), round(plan.W * 0.58), round(plan.H * 0.84))
        center, radius = (round(plan.W * 0.8), round(plan.H * 0.6)), round(plan.H * 0.2)
    else:
        box = (round(plan.W * 0.06), round(plan.H * 0.24), round(plan.W * 0.94), round(plan.H * 0.62))
        center, radius = (round(plan.W * 0.25), round(plan.H * 0.85)), round(plan.W * 0.19)
    width, height = box[2] - box[0], box[3] - box[1]
    shrink = {'comment': 0.5, 'dm': 0.72}.get(plan.prop, 1.0)
    if shrink < 1:
        trim = round(height * (1 - shrink))
        box = (box[0], box[1] + trim // 2, box[2], box[3] - trim // 2)
        height = box[3] - box[1]
    card, mark = receipt(plan.prop, plan.note, width, height)
    enter = ease(progress(t, plan.lead, plan.lead + 0.16))
    scale = 0.92 + 0.08 * enter
    shown = card.resize((round(width * scale), round(height * scale)))
    mask = Image.new('L', card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=14, fill=255)
    mask = mask.resize(shown.size)
    ox = box[0] + (width - shown.width) // 2
    oy = box[1] + (height - shown.height) // 2 + round(16 * (1 - enter))
    canvas.paste(shown, (ox, oy), mask)
    reveal = ease(progress(t, plan.ts, plan.ts + 0.45))
    if reveal > 0 and enter >= 1:
        overlay = Image.new('RGBA', plan.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        x0, y0, x1, y1 = mark
        draw.rounded_rectangle((ox + x0, oy + y0, ox + x0 + (x1 - x0) * reveal, oy + y1), radius=4,
                               fill=ACCENT + (95,), outline=ACCENT + (255,), width=2)
        canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay).convert('RGB')
    face, face_mask = face_circle(plan, t, radius)
    ring = ImageDraw.Draw(canvas)
    ring.ellipse((center[0] - radius - 3, center[1] - radius - 3, center[0] + radius + 3, center[1] + radius + 3), fill=WHITE)
    canvas.paste(face, (center[0] - radius, center[1] - radius), face_mask)
    return canvas


@lru_cache(maxsize=128)
def phone_key(index):
    picture = movie('phone-live')[index]
    px = picture.load()
    mask = Image.new('L', picture.size, 0)
    mp = mask.load()
    xs, ys = [], []
    for y in range(20, picture.height - 10):
        for x in range(150, 360):
            r, g, b = px[x, y]
            if g > 150 and g - r > 50 and g - b > 80:
                mp[x, y] = 255
                xs.append(x)
                ys.append(y)
    mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    return mask, (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def phone_frame(plan, t, prop=None):
    """The handheld phone plate with something real on its screen instead of the green key."""
    frames = movie('phone-live')
    index = int(round(t * FPS)) % len(frames)
    source = frames[index].copy()
    mask, box = phone_key(index)
    bw, bh = box[2] - box[0], box[3] - box[1]
    if prop:
        content, _ = receipt(prop, plan.note, bw * 2, bh * 2, dark=True)
        content = content.resize((bw, bh), Image.Resampling.LANCZOS)
    else:
        content = presenter_shot(plan, t, 1.0, size=(bw, bh), rhythm=False)
    layer = Image.new('RGB', source.size)
    layer.paste(content, box[:2])
    source.paste(layer, (0, 0), mask)
    return source


def device_shot(plan, t):
    push = 1.0 + 0.1 * ease(progress(t, plan.lead, plan.dur))
    return fill(phone_frame(plan, t, plan.prop), plan.size, push, (0.39, 0.48))


def slam_frame(plan, local):
    words = (plan.note or plan.text or '').upper()
    canvas = Image.new('RGB', plan.size, ACCENT if not plan.wide else INK)
    draw = ImageDraw.Draw(canvas)
    size = 120 if not plan.wide else 110
    while size > 20:
        face = font(size, 'black')
        lines = wrap(draw, words, face, plan.W * 0.86)
        if len(lines) <= 2 and all(draw.textlength(line, font=face) <= plan.W * 0.86 for line in lines):
            break
        size -= 4
    scale = 1.3 - 0.3 * ease(progress(local, 0, 0.1))
    shake = 4 * (1 - progress(local, 0, 0.25))
    dx = round(shake * math.sin(local * 90))
    face = font(size * scale, 'black')
    total = len(lines) * size * scale * 1.05
    y = plan.H / 2 - total / 2 + size * scale * 0.52
    for line in lines:
        draw.text((plan.W / 2 + dx, y), line, font=face, fill=INK if not plan.wide else ACCENT, anchor='mm')
        y += size * scale * 1.05
    return canvas


def reaction_frame(plan, local):
    if plan.preset == 'podcast':
        name = plan.other
        picture = fill(frame(name, plan.ts + local), plan.size, 1.7 + 0.15 * local, presenter_focus(plan, name, 1.8))
        return picture
    name = plan.presenter
    fx, fy = FACE[name]
    zoom = (2.1 if name == 'host-live' else 1.8) + 0.25 * ease(progress(local, 0, 0.5))
    picture = fill(frame(name, plan.ts + local), plan.size, zoom, (fx + 0.01 * math.sin(local * 60), fy + 0.05))
    return ImageOps.grayscale(picture).convert('RGB')


# ---------------------------------------------------------------- overlays

@lru_cache(maxsize=256)
def text_card(text, width, wide, big=False):
    """The on-screen hook line: dark text on a white plate (Reels) or a bold title plate (long form)."""
    probe = ImageDraw.Draw(Image.new('L', (1, 1)))
    size = (27 if not wide else 24) * (1.2 if big else 1)
    face = font(size, 'black' if wide else 'bold')
    lines = wrap(probe, text, face, width - 28)
    line_h = round(size * 1.22)
    tw = max(probe.textlength(line, font=face) for line in lines)
    card = Image.new('RGBA', (round(tw + 28), line_h * len(lines) + 18), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    fill_color = (255, 255, 255, 255) if not wide else (14, 14, 14, 228)
    draw.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=9, fill=fill_color)
    for i, line in enumerate(lines):
        draw.text((card.width / 2, 9 + line_h * i + line_h / 2), line, font=face,
                  fill=INK if not wide else (255, 255, 255), anchor='mm')
    return card


def place_text(img, plan, t):
    if not plan.text or t > plan.text_end:
        return img
    big = plan.move == 'stakes-text'
    width = round(plan.W * (0.86 if not plan.wide else 0.36))
    card = text_card(plan.text, width, plan.wide, big)
    pop = ease(progress(t, 0, 0.14))
    scale = 1.18 - 0.18 * pop if t < 0.14 else 1.0
    fade = 1 - progress(t, plan.text_end - 0.12, plan.text_end)
    shown = card.resize((max(1, round(card.width * scale)), max(1, round(card.height * scale))))
    if fade < 1:
        alpha = shown.getchannel('A').point(lambda a: round(a * fade))
        shown.putalpha(alpha)
    if plan.wide:
        right = plan.main != 'plate'
        x = round(plan.W * 0.95 - shown.width) if right else round(plan.W * 0.05)
        y = round(plan.H * 0.1)
    else:
        x = round(plan.W / 2 - shown.width / 2)
        y = round(plan.H * 0.13 - shown.height / 2 + 20)
    base = img.convert('RGBA')
    base.alpha_composite(shown, (max(0, x), max(0, y)))
    return base.convert('RGB')


def caption_chunks(words):
    chunks, current = [], []
    for i, word in enumerate(words):
        current.append(i)
        letters = sum(len(words[j]) for j in current)
        if len(current) == 3 or letters > 13 or word[-1] in '.,?!:':
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def draw_captions(img, plan, t, size=27):
    if t < plan.times[0] or t > plan.speech_end + 0.35:
        return img
    active = max(i for i, at in enumerate(plan.times) if at <= t)
    chunks = caption_chunks(plan.words)
    chunk = next(c for c in chunks if active in c)
    draw = ImageDraw.Draw(img)
    face = font(size, 'black')
    labels = [plan.words[i].upper().strip('"\'') for i in chunk]
    space = draw.textlength(' ', font=face)
    widths = [draw.textlength(label, font=face) for label in labels]
    total = sum(widths) + space * (len(labels) - 1)
    while total > plan.W * 0.9 and size > 16:
        size -= 2
        face = font(size, 'black')
        space = draw.textlength(' ', font=face)
        widths = [draw.textlength(label, font=face) for label in labels]
        total = sum(widths) + space * (len(labels) - 1)
    x = plan.W / 2 - total / 2
    y = plan.H * 0.7
    for i, label, width in zip(chunk, labels, widths):
        now = i == active
        draw.text((x, y), label, font=face, fill=ACCENT if now else WHITE, anchor='lm',
                  stroke_width=max(2, size // 9), stroke_fill=INK)
        x += width + space
    return img


def draw_subtitles(img, plan, t):
    if t < plan.times[0] or t > plan.speech_end + 0.35:
        return img
    active = max(i for i, at in enumerate(plan.times) if at <= t)
    start = (active // 7) * 7
    line = ' '.join(plan.words[start:start + 7])
    overlay = Image.new('RGBA', plan.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    face = font(16, 'bold')
    width = draw.textlength(line, font=face)
    y = plan.H * 0.885
    draw.rounded_rectangle((plan.W / 2 - width / 2 - 9, y - 13, plan.W / 2 + width / 2 + 9, y + 13), radius=5,
                           fill=(0, 0, 0, 165))
    draw.text((plan.W / 2, y), line, font=face, fill=WHITE, anchor='mm')
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')


def draw_counter(img, plan, t):
    note = plan.note or '1/3'
    if ':' in note:
        minutes, seconds = note.split(':')
        left = max(0, int(minutes) * 60 + int(seconds) - int(t))
        note = f'{left // 60:02d}:{left % 60:02d}'
    pop = ease(progress(t, 0.25, 0.38))
    if pop <= 0:
        return img
    draw = ImageDraw.Draw(img)
    bar_h = 5 if not plan.wide else 4
    draw.rectangle((0, 0, plan.W * min(1, t / plan.dur), bar_h), fill=ACCENT)
    x = plan.W - 14 if not (plan.wide and plan.main != 'plate') else 14
    anchor = 'ra' if x > plan.W / 2 else 'la'
    y = 14 if plan.wide else 16
    chip(img, note, (x, y + round(6 * (1 - pop))), fill_color=INK, color=ACCENT, size=21, anchor=anchor, pad=(11, 7))
    return img


def flash(img, amount):
    if amount <= 0:
        return img
    return Image.blend(img, Image.new('RGB', img.size, WHITE), min(1, amount))


# ---------------------------------------------------------------- scene

def picture(plan, t):
    m = plan.move
    if m == 'green-screen' and t >= plan.lead:
        return receipt_layout(plan, t)
    if m == 'inside-device' and t >= plan.lead:
        return device_shot(plan, t)
    if m == 'split-screen' and t >= plan.lead:
        return split_shot(plan, t)
    if m == 'broll-cutaway' and plan.ts - 0.15 <= t < plan.ts + 1.45:
        return plate_shot(plan, plan.cut, t)
    if m == 'kinetic-slam' and plan.ts <= t < plan.ts + 0.85:
        return slam_frame(plan, t - plan.ts)
    if m == 'reaction-insert' and plan.ts <= t < plan.ts + 0.7:
        return reaction_frame(plan, t - plan.ts)
    if m == 'freeze-frame':
        if plan.ts <= t < plan.ts + 0.8:
            return main_shot(plan, plan.ts)
        if t >= plan.ts + 0.8:
            return main_shot(plan, t - 0.8)
    if m == 'zoom-to-detail' and t >= plan.lead:
        name = plan.cut or plan.presenter
        k = ease(progress(t, plan.ts, plan.ts + 0.45)) * (1 - ease(progress(t, plan.dur - 0.6, plan.dur - 0.2)))
        start = PLATE_FOCUS.get(name, (0.5, 0.5))
        target = ZOOM_TARGET.get(name, start)
        focus = (start[0] + (target[0] - start[0]) * k, start[1] + (target[1] - start[1]) * k)
        return plate_shot(plan, name, t, 1 + 1.15 * k, focus=focus)
    if m == 'rehook':
        crash = 1 + 0.3 * ease(progress(t, plan.ts, plan.ts + 0.12))
        return main_shot(plan, t, crash)
    return main_shot(plan, t)


def decorate(img, plan, t):
    m = plan.move
    hidden = (m == 'kinetic-slam' and plan.ts <= t < plan.ts + 0.85) or (m == 'reaction-insert' and plan.ts <= t < plan.ts + 0.7)
    if m == 'zoom-to-detail' and plan.ts + 0.45 <= t < plan.dur - 0.6:
        draw = ImageDraw.Draw(img)
        pulse = 2 * math.sin((t - plan.ts) * 9)
        w, h = plan.W * (0.46 if not plan.wide else 0.3), plan.H * (0.12 if not plan.wide else 0.2)
        draw.rounded_rectangle((plan.W / 2 - w / 2 - pulse, plan.H / 2 - h / 2 - pulse,
                                plan.W / 2 + w / 2 + pulse, plan.H / 2 + h / 2 + pulse), radius=10, outline=ACCENT, width=4)
    if m == 'freeze-frame' and plan.ts <= t < plan.ts + 0.8:
        img = flash(img, 1 - progress(t, plan.ts, plan.ts + 0.14))
        draw = ImageDraw.Draw(img)
        r = plan.W * (0.17 if not plan.wide else 0.1)
        cx, cy = plan.W / 2, plan.H * (0.48 if not plan.wide else 0.5)
        grow = ease(progress(t, plan.ts + 0.05, plan.ts + 0.2))
        draw.ellipse((cx - r * grow, cy - r * grow, cx + r * grow, cy + r * grow), outline=ACCENT, width=4)
        if grow >= 1:
            chip(img, (plan.note or 'this moment').upper(), (cx, cy + r + 10), fill_color=ACCENT, size=14, anchor='ma')
    if m == 'rehook' and t >= plan.ts:
        img = flash(img, 0.85 * (1 - progress(t, plan.ts, plan.ts + 0.12)))
    if not hidden:
        if m == 'rehook' and t >= plan.ts:
            card = text_card(plan.note, round(plan.W * 0.84), plan.wide)
            base = img.convert('RGBA')
            base.alpha_composite(card, (round(plan.W / 2 - card.width / 2), round(plan.H * 0.13)))
            img = base.convert('RGB')
        else:
            img = place_text(img, plan, t)
        if plan.wide:
            img = draw_subtitles(img, plan, t)
        else:
            img = draw_captions(img, plan, t, 31 if m == 'word-captions' else 27)
    if m == 'progress-counter':
        img = draw_counter(img, plan, t)
    return img


def raw_tail(plan, local):
    if plan.main == 'plate':
        img = plate_shot(plan, plan.cut, local)
    elif plan.main == 'podcast':
        img = podcast_two_up(plan, local)
    else:
        img = fill(frame(plan.presenter, local + 0.2), plan.size, 1.0, presenter_focus(plan, plan.presenter, 1.0))
    img = ImageEnhance.Color(img).enhance(0.85)
    chip(img, 'BEFORE · RAW TAKE', (14, 14), fill_color=(0, 0, 0), color=WHITE, size=12)
    return img


def scene(plan, t):
    if t >= plan.dur:
        return raw_tail(plan, t - plan.dur)
    return decorate(picture(plan, t), plan, t)


# ---------------------------------------------------------------- sound

def sound_events(plan):
    events = [(0.0, 'pop')]
    if plan.move in ('sfx-layer',):
        events += [(plan.ts - 0.6, 'whoosh'), (plan.ts, 'hit')]
        if 'music' not in plan.hook['say'].lower():
            events.append((plan.ts + 0.9, 'pop'))
    if plan.move == 'kinetic-slam':
        events.append((plan.ts, 'hit'))
    if plan.move == 'freeze-frame':
        events.append((plan.ts, 'shutter'))
    if plan.move == 'rehook':
        events += [(plan.ts - 0.25, 'whoosh'), (plan.ts, 'hit')]
    if plan.move == 'reaction-insert':
        events.append((plan.ts, 'pop'))
    return events


def sound_for(plan):
    events = sound_events(plan)
    stop_at = plan.ts if 'music' in plan.hook['say'].lower() else None

    def write(path):
        rng = random.Random(11)
        n = round(RATE * plan.total)
        out = [0.0] * n
        # Soft chord bed under everything, like a quiet music track.
        notes = (196.0, 246.9, 293.7, 392.0)
        for i in range(round(RATE * plan.dur)):
            t = i / RATE
            if stop_at is not None and t > stop_at:
                break
            env = min(1, t / 0.3) * (1 - progress(t, plan.dur - 0.25, plan.dur))
            out[i] += 0.045 * env * sum(math.sin(math.tau * f * t + k) for k, f in enumerate(notes)) * (0.8 + 0.2 * math.sin(t * 3))
        if stop_at is not None:
            start = round(stop_at * RATE)
            phase = 0.0
            for i in range(round(0.35 * RATE)):
                t = i / RATE
                freq = 300 * (1 - t / 0.35) + 30
                phase += math.tau * freq / RATE
                if start + i < n:
                    out[start + i] += 0.25 * (1 - t / 0.35) * math.sin(phase)
        for at, kind in events:
            start = max(0, round(at * RATE))
            if kind == 'pop':
                length, phase = round(0.08 * RATE), 0.0
                for i in range(length):
                    t = i / RATE
                    phase += math.tau * (1150 - 6500 * t) / RATE
                    if start + i < n:
                        out[start + i] += 0.32 * math.exp(-t * 45) * math.sin(phase)
            elif kind == 'whoosh':
                length, low = round(0.42 * RATE), 0.0
                for i in range(length):
                    t = i / RATE
                    x = t / 0.42
                    alpha = 0.04 + 0.4 * math.sin(math.pi * x)
                    low += alpha * (rng.uniform(-1, 1) - low)
                    if start + i < n:
                        out[start + i] += 0.55 * math.sin(math.pi * x) ** 2 * low
            elif kind == 'hit':
                length, phase = round(0.5 * RATE), 0.0
                for i in range(length):
                    t = i / RATE
                    phase += math.tau * (95 - 70 * min(1, t / 0.25)) / RATE
                    tone = math.exp(-t * 7) * math.sin(phase)
                    noise = math.exp(-t * 40) * rng.uniform(-1, 1)
                    if start + i < n:
                        out[start + i] += 0.62 * tone + 0.18 * noise
            elif kind == 'shutter':
                for offset in (0, round(0.06 * RATE)):
                    for i in range(round(0.012 * RATE)):
                        if start + offset + i < n:
                            out[start + offset + i] += 0.45 * rng.uniform(-1, 1) * (1 - i / (0.012 * RATE))
        samples = array('h', (round(32767 * max(-0.95, min(0.95, value))) for value in out))
        if sys.byteorder == 'big':
            samples.byteswap()
        with wave.open(str(path), 'wb') as recording:
            recording.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            recording.writeframes(samples.tobytes())

    return write


# ---------------------------------------------------------------- catalog

MOVE_DEMOS = {
    'jump-cut': {'say': "So I tried it, and honestly, it worked way better than I expected it to.", 'for': ['talking-head']},
    'punch-in': {'say': "Most edits feel flat because nothing changes. Punch in on the word that matters.", 'text': 'Punch in on the stress', 'for': ['talking-head']},
    'word-captions': {'say': "Most people scroll with the sound off, so your words need to be on screen.", 'for': ['talking-head']},
    'stakes-text': {'say': "I nearly lost the whole project because of one export setting.", 'text': '1 setting. Whole project.', 'for': ['talking-head']},
    'kinetic-slam': {'say': "After all that testing, the answer was really simple. Cut less.", 'for': ['talking-head'], 'note': 'CUT LESS'},
    'broll-cutaway': {'say': "Every morning starts the same way, with a flat white from the café downstairs.", 'for': ['talking-head'], 'cut': 'coffee-live'},
    'green-screen': {'say': "Someone commented that my edits are way too fast. Let's check that.", 'for': ['talking-head'], 'prop': 'comment', 'note': 'way too fast to follow tbh'},
    'zoom-to-detail': {'say': "Open the export window and change this one setting before you render.", 'for': ['screen'], 'cut': 'editing-live'},
    'inside-device': {'say': "This is the post that brought in our first hundred customers.", 'for': ['talking-head'], 'prop': 'post', 'note': 'Our launch post'},
    'split-screen': {'say': "Same cup, same milk. The only change is how I hold the jug.", 'for': ['product'], 'cut': 'coffee-live', 'note': 'BEFORE|AFTER'},
    'sfx-layer': {'say': "Every cut, every word on screen and every reveal gets its own sound.", 'text': 'Hear the edit', 'for': ['talking-head']},
    'reaction-insert': {'say': "That one video got two million views, and I didn't even recognise it.", 'for': ['podcast']},
    'freeze-frame': {'say': "Watch the milk fold over right here. That's when you start the pattern.", 'for': ['product'], 'cut': 'coffee-live', 'note': 'this fold'},
    'progress-counter': {'say': "Three cuts that save a boring take. Number one: delete your first sentence.", 'for': ['talking-head'], 'note': '1/3'},
    'rehook': {'say': "That fixed the start. But the part that surprised me came much later.", 'for': ['talking-head'], 'note': "But here's the catch"},
}


def load(mode):
    return json.loads((DATA / f'{mode}.json').read_text())


def hook_jobs():
    jobs = {}
    for mode in ('short', 'long'):
        for group in load(mode):
            for n, hook in enumerate(group['hooks'], 1):
                key = f'th-{mode}-{group["id"]}-{n:02d}'
                jobs[key] = (mode, hook, n)
    return jobs


def move_jobs():
    jobs = {}
    moves = {move['id'] for move in json.loads((DATA / 'moves.json').read_text())}
    if missing := moves - MOVE_DEMOS.keys():
        raise ValueError(f'Moves without a demo: {sorted(missing)}')
    for index, (move, demo) in enumerate(MOVE_DEMOS.items()):
        hook = {'move': move, **demo}
        for mode in ('short', 'long'):
            jobs[f'move-{mode}-{move}'] = (mode, hook, index)
    return jobs


def build(key):
    """Return (plan, scene function, sound writer) for a preview key."""
    if key.startswith('move-'):
        mode, hook, index = move_jobs()[key]
        plan = Plan(hook, mode, index, demo=True)
    else:
        mode, hook, index = hook_jobs()[key]
        plan = Plan(hook, mode, index)
    return plan, (lambda t: scene(plan, t)), (sound_for(plan) if plan.sound else None)
