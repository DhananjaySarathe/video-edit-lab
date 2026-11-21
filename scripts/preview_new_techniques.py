"""Three exact editing demonstrations for the technique library."""

from array import array
from math import exp, sin, tau
from random import Random
import sys
import wave

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from preview_common import H, W, ease, font, progress
from preview_plates import FRAME_RATE, shot, source
from preview_sound import LENGTH, RATE


SIZE = W, H
PETROL = '#142820'
PAPER = '#faf5e8'
MINT = '#b5efcf'
GOLD = '#f9cd79'
DIM = '#5c7668'
# Contact onsets selected from the best-readable source frames at 20 fps.
FOOTFALL_CUES = (.10, .65, 1.25, 1.85, 2.45, 3.05)
PICTURE_CUT = 1.4
HAND_SAMPLE = .35
REPLAY_IN, REPLAY_OUT = 1.05, 2.15


def label(draw, at, value, size, fill=PAPER, anchor='lm', weight='bold'):
    draw.text(at, value, font=font(size, weight), fill=fill, anchor=anchor)


def chip(draw, at, value, color=PAPER, fill=PETROL, size=19):
    x, y = at
    width = round(font(size).getlength(value)) + 20
    draw.rounded_rectangle((x, y, x + width, y + size + 14), 5, fill=fill)
    label(draw, (x + 10, y + (size + 14) / 2), value, size, color)


def distance_amount(t):
    return ease(progress(t, PICTURE_CUT - .055, PICTURE_CUT + .055))


def perspective_audio(path):
    """A single Foley timeline with level and high-frequency changes at the cut."""
    samples = array('h')
    rng = Random(871)
    floor_noise = 0.0
    for i in range(round(RATE * LENGTH)):
        t = i / RATE
        white = rng.uniform(-1, 1)
        floor_noise = .985 * floor_noise + .015 * white
        near = 0.0
        far = 0.0
        for contact in FOOTFALL_CUES:
            delay = t - contact
            if 0 <= delay < .30:
                thud = sin(tau * (115 * delay - 107 * delay * delay)) * exp(-30 * delay)
                scruff = white * exp(-58 * delay) * .17
                onset = min(delay * 810, 1)
                near += onset * (.48 * thud + scruff)
                far += onset * (.17 * thud + .028 * scruff)
                if delay > .043:
                    room_tail = delay - .043
                    far += .018 * sin(tau * 86 * room_tail) * exp(-27 * room_tail)
        mix = distance_amount(t)
        signal = .15 * floor_noise + far * (1 - mix) + near * mix
        fade = min(1.0, t * 35) * (1 - ease(progress(t, 3.15, 3.2)))
        samples.append(round(32767 * signal * fade))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as output:
        output.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(samples.tobytes())


def perspective_foley(t, size=SIZE):
    width, height = size
    portrait = height > width
    close = t >= PICTURE_CUT
    zoom = 1.43 if close else 1.04
    x = -35 if portrait else (-19 if close else 0)
    y = 35 if close else 3
    panel = 485 if portrait else 280
    frame = Image.new('RGB', size, PETROL)
    frame.paste(shot('steps-live', t, zoom, x, y, (width, panel)), (0, 0))
    draw = ImageDraw.Draw(frame)
    inset = 16
    chip(draw, (inset, 38 if portrait else 16), 'Close mix' if close else 'Far mix',
         PETROL if close else PAPER, MINT if close else PETROL, size=20 if portrait else 19)

    label(draw, (inset, panel + 20), 'Same contact times', 20)
    left, right = inset + 4, width - inset - 4
    center = panel + (72 if portrait else 59)
    draw.line((left, center, right, center), fill=DIM, width=2)
    cut_x = left + (right - left) * PICTURE_CUT / LENGTH
    draw.line((cut_x, center - 23, cut_x, center + 4), fill=GOLD, width=2)
    for contact in FOOTFALL_CUES:
        at = left + (right - left) * contact / LENGTH
        bar_height = 24 if contact >= PICTURE_CUT else 10
        color = MINT if contact <= t else DIM
        draw.line((at, center - bar_height, at, center + 2), fill=color, width=3)
    cursor = left + (right - left) * t / LENGTH
    draw.ellipse((cursor - 4, center + 5, cursor + 4, center + 13), fill=PAPER)
    if portrait:
        label(draw, (inset, panel + 112), 'Same footsteps.', 22, MINT)
        label(draw, (inset, panel + 139), 'Different listening distance.', 19, PAPER)
    else:
        label(draw, (width - inset, panel + 20), 'Different listening distance', 19, MINT, 'rm')
    return frame


def inspect_hand(size):
    width, height = size
    portrait = height > width
    frame = Image.new('RGB', size, PETROL)
    draw = ImageDraw.Draw(frame)
    area = (316, 145, 408, 220)
    detail = source('host-live', HAND_SAMPLE).crop(area)
    cutout = source('host-live-matte', HAND_SAMPLE).crop(area)
    matte_detail = ImageOps.colorize(cutout, '#132820', PAPER)
    panes = ((24, 92, 312, 226), (24, 358, 312, 226)) if portrait else ((18, 82, 293, 229), (329, 82, 293, 229))
    for (x, y, pane_w, pane_h), picture, caption in zip(panes, (detail, matte_detail), ('Original hand', 'Foreground mask')):
        photo = ImageOps.fit(picture, (pane_w, pane_h), method=Image.Resampling.LANCZOS)
        frame.paste(photo, (x, y))
        chip(draw, (x + 8, y + 8), caption, size=19)
    label(draw, (18, 39), 'Inspect the finger gaps', 27 if portrait else 31, MINT)
    return frame


def hand_mask(t, size=SIZE):
    width, height = size
    portrait = height > width
    if .58 <= t < 1.28:
        return inspect_hand(size)

    stamp = HAND_SAMPLE if t < .58 else HAND_SAMPLE + (t - 1.28) * 1.22
    zoom = 1.04
    x, y = (13, -8) if portrait else (-18, -7)
    raw = shot('host-live', stamp, zoom, x, y, size)
    source_matte = shot('host-live-matte', stamp, zoom, x, y, size)
    frame = ImageEnhance.Brightness(raw).enhance(.73)
    draw = ImageDraw.Draw(frame)
    start, baseline = (169, 355) if portrait else (333, 191)
    type_size = 53 if portrait else 68
    label(draw, (start, baseline), 'EDGE', type_size, GOLD)
    if t >= 1.28:
        frame.paste(raw, (0, 0), source_matte)
    chip(draw, (17, 39 if portrait else 16), 'Text sits in front' if t < .58 else 'Fingers cover the letters',
         PAPER if t < .58 else PETROL, PETROL if t < .58 else MINT)
    return frame


def replay_source(t):
    if t < REPLAY_IN:
        return .3 + t, 'Original', 1
    if t < REPLAY_OUT:
        return .69 + (t - REPLAY_IN) * .60, 'Replay · 0.6×', .6
    return .3 + REPLAY_IN + (t - REPLAY_OUT), 'Continue', 1


def source_clock_replay(t, size=SIZE):
    width, height = size
    portrait = height > width
    stamp, state, rate = replay_source(t)
    stamp = round(stamp * FRAME_RATE) / FRAME_RATE
    close = rate < 1
    if portrait:
        zoom, x, y = (1.46, -64, 39) if close else (1.10, -83, 7)
    else:
        zoom, x, y = (1.70, -80, 31) if close else (1.08, -33, 3)
    frame = shot('coffee-live', stamp, zoom, x, y, size)
    draw = ImageDraw.Draw(frame)
    chip(draw, (16, 42 if portrait else 15), state,
         PETROL if close else PAPER, GOLD if close else PETROL, size=21)

    panel = 495 if portrait else 275
    draw.rectangle((0, panel, width, height), fill=PETROL)
    label(draw, (17, panel + 24), 'SOURCE  ·  POUR A', 17, MINT)
    label(draw, (17, panel + 54), f'00:{stamp:05.2f}', 30, PAPER, weight='mono')
    decision = 'Same pour, earlier frames' if close else ('Back to the original time' if t >= REPLAY_OUT else 'Real-time pass')
    if portrait:
        label(draw, (17, panel + 109), decision, 21, GOLD if close else PAPER)
    else:
        draw.line((227, panel + 17, 227, panel + 68), fill=DIM)
        label(draw, (254, panel + 42), decision, 23, GOLD if close else PAPER)
    return frame


SCENES = {
    'tech-perspective-foley': perspective_foley,
    'tech-foreground-hand-mask': hand_mask,
    'tech-replay-source-clock': source_clock_replay,
}

AUDIO = {'tech-perspective-foley': perspective_audio}

POSTERS = {
    'tech-perspective-foley': 1.86,
    'tech-foreground-hand-mask': 1.32,
    'tech-replay-source-clock': 1.60,
}
