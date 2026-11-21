"""Original widescreen body and ending demonstrations."""

from array import array
from math import exp, sin, tau
from random import Random
import sys
import wave

from PIL import Image, ImageDraw, ImageEnhance

from preview_common import H, W, ease, font, progress
from preview_live_action import type_at
from preview_phone import device
from preview_plates import shot
from preview_sound import LENGTH, RATE


DEEP = '#172924'
INK = '#233b31'
PAPER = '#faf5e8'
MINT = '#c4e5c2'
GOLD = '#ffd188'
ROOM_SWITCH = 1.40
LOG_AT, REVISION_AT = .85, 1.90
DETAIL_AT, REPRISE_AT = .83, 1.74
MAP_AT, RESULT_AT, BOUNDARY_AT = .62, .94, 1.67


def label(image, x, y, value, color=PAPER, background=DEEP):
    draw = ImageDraw.Draw(image)
    width = round(draw.textlength(value, font=font(19)))
    draw.rounded_rectangle((x, y, x + width + 22, y + 32), 5, fill=background)
    type_at(image, (x + 11, y + 16), value, 19, color, 'lm')


def room_owns_sound(t):
    at_bench = t >= ROOM_SWITCH
    if at_bench:
        image = shot('workshop-live', .46 + t - ROOM_SWITCH, 1.01)
    else:
        image = shot('editing-live', .39 + t, 1.02)

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 286, W, H), fill=DEEP)
    type_at(image, (23, 307), 'WORKSHOP' if at_bench else 'EDIT DESK', 19, MINT, 'lm')
    type_at(image, (22, 337), 'Sander motor' if at_bench else 'Keys and room tone', 30, PAPER, 'lm')
    type_at(image, (619, 336), 'Illustrated sound', 19, PAPER, 'rm')
    cut_x = 23 + 594 * ROOM_SWITCH / LENGTH
    head = 23 + 594 * t / LENGTH
    draw.line((23, 281, cut_x, 281), fill=MINT, width=4)
    draw.line((cut_x, 281, 617, 281), fill=GOLD, width=4)
    draw.line((cut_x, 273, cut_x, 288), fill=DEEP, width=3)
    draw.ellipse((head - 4, 277, head + 4, 285), fill=PAPER)
    return image


def illustrated_rooms(path):
    rng = Random(15)
    samples = array('h')
    low_noise = 0.0
    for i in range(round(RATE * LENGTH)):
        t = i / RATE
        noise = rng.uniform(-1, 1)
        low_noise = .94 * low_noise + .06 * noise
        if t < ROOM_SWITCH:
            taps = 0.0
            for contact in (.22, .53, .89, 1.20):
                dt = t - contact
                if 0 <= dt < .09:
                    envelope = min(dt * 900, 1) * exp(-dt * 48)
                    taps += envelope * (.12 * sin(tau * 464 * dt) + .16 * noise)
            gain = min(t * 100, 1, (ROOM_SWITCH - t) * 160)
            sample = gain * (.05 * low_noise + .022 * sin(tau * 57 * t) + taps)
        else:
            dt = t - ROOM_SWITCH
            spin = sin(tau * (116 * dt + .26 * sin(tau * 4 * dt)))
            texture = sin(tau * 234 * dt) * (.5 + .5 * sin(tau * 28 * dt))
            gain = min(dt * 110, 1, (LENGTH - t) * 12)
            sample = gain * (.13 * spin + .09 * texture + .14 * low_noise + .035 * noise)
        samples.append(round(32767 * sample))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as recording:
        recording.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        recording.writeframes(samples.tobytes())


def scope_revision(t):
    image = ImageEnhance.Brightness(shot('notebook-live', .2 + t, 1.11)).enhance(.64)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((19, 17, 621, 343), 10, fill=PAPER)
    revised = t >= REVISION_AT
    label(image, 43, 32, 'Checked wording' if revised else 'Draft headline',
          INK, MINT if revised else GOLD)
    type_at(image, (42, 95), '5 s shorter in this test' if revised else 'Always faster', 41, INK, 'lm')
    draw.line((42, 128, 597, 128), fill='#d3d8c9', width=2)

    for seconds in (0, 4, 8, 12):
        tick_x = 115 + 19 * seconds
        draw.line((tick_x, 157, tick_x, 264), fill='#d8ded2', width=2)
        type_at(image, (tick_x, 282), str(seconds), 19, INK)
    type_at(image, (372, 282), 's', 19, INK)

    for key, y, duration, fill in (('A', 178, 12, '#728c7c'), ('B', 232, 7, '#89ae94')):
        type_at(image, (64, y), key, 28, INK)
        end = 115 + 19 * duration
        draw.rounded_rectangle((115, y - 16, end, y + 16), 4, fill=fill)
        type_at(image, (end - 8, y), f'{duration} s', 21, '#14291d', 'rm')

    if t >= LOG_AT:
        slide = round(12 * (1 - ease(progress(t, LOG_AT, LOG_AT + .17))))
        draw.rounded_rectangle((415 + slide, 147, 596 + slide, 276), 8, fill=DEEP)
        type_at(image, (430 + slide, 170), 'Start/stop log', 23, PAPER, 'lm')
        draw.line((430 + slide, 190, 580 + slide, 190), fill='#759384', width=1)
        type_at(image, (432 + slide, 213), 'A · 1 run', 22, MINT, 'lm')
        type_at(image, (432 + slide, 246), 'B · 1 run', 22, MINT, 'lm')

    type_at(image, (44, 319), 'Illustrative timings', 19, INK, 'lm')
    if revised:
        type_at(image, (595, 319), 'One run per setup', 20, INK, 'rm')
    return image


def frame_reprise(t):
    wide = shot('room')
    if t < DETAIL_AT:
        label(wide, 19, 19, 'Opening wide')
        type_at(wide, (590, 88), 'Where does the light land?', 28, PAPER, 'rm', 1)
        return wide

    if t < REPRISE_AT:
        detail = wide.crop((192, 144, 576, 360)).resize((W, H), Image.Resampling.BICUBIC)
        label(detail, 19, 19, 'Detail')
        draw = ImageDraw.Draw(detail)
        draw.ellipse((358, 225, 382, 249), outline=GOLD, width=3)
        return detail

    label(wide, 19, 19, 'Same wide')
    draw = ImageDraw.Draw(wide)
    draw.ellipse((404, 277, 424, 297), outline=GOLD, width=3)
    reveal = ease(progress(t, REPRISE_AT, REPRISE_AT + .23))
    draw.line((422, 280, 422 + 46 * reveal, 280 - 65 * reveal), fill=GOLD, width=3)
    if t >= REPRISE_AT + .2:
        draw.rounded_rectangle((354, 172, 609, 216), 6, fill=DEEP)
        type_at(wide, (482, 194), 'Light reaches here', 24, PAPER)
    return wide


def route_screen(t):
    screen = Image.new('RGBA', (170, 314), DEEP)
    draw = ImageDraw.Draw(screen)
    type_at(screen, (85, 42), 'Trail map', 23, PAPER)
    type_at(screen, (85, 70), 'ONLINE', 17, MINT)
    if t < MAP_AT:
        type_at(screen, (85, 153), 'Loading…', 20, PAPER)
        draw.rounded_rectangle((17, 177, 153, 184), 3, fill='#405c4e')
        draw.rounded_rectangle((17, 177, 26 + 127 * progress(t, 0, MAP_AT), 184), 3, fill=MINT)
    else:
        draw.rounded_rectangle((12, 93, 158, 246), 9, fill='#42634e')
        draw.line((25, 110, 73, 160, 123, 166, 145, 228), width=2, fill='#63816a')
        draw.line((30, 208, 76, 220, 112, 188, 146, 199), width=2, fill='#63816a')
        draw.line((30, 145, 61, 127, 112, 144, 148, 111), width=2, fill='#63816a')
        route = [(30, 222), (56, 197), (88, 205), (100, 160), (134, 130)]
        draw.line(route, width=5, fill=MINT, joint='curve')
        for x, y in (route[0], route[-1]):
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=GOLD, outline=DEEP, width=1)
        type_at(screen, (85, 276), 'Route ready', 19, PAPER)
    return screen


def verdict(image, y, condition, result, color):
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((354, y, 620, y + 75), 7, fill=DEEP)
    draw.rounded_rectangle((354, y, 361, y + 75), 3, fill=color)
    type_at(image, (375, y + 22), condition, 18, color, 'lm')
    type_at(image, (375, y + 51), result, 30, PAPER, 'lm')


def result_boundary(t):
    image, _ = device(t, route_screen(t))
    label(image, 19, 19, 'Practice screen')
    if t < RESULT_AT:
        verdict(image, 115, 'TRAIL MAP', 'Will it load?', MINT)
    else:
        verdict(image, 115, 'ONLINE MAP', 'Opened', MINT)
    if t >= BOUNDARY_AT:
        verdict(image, 202, 'OFFLINE MAP', 'Untested', GOLD)
    return image


SCENES = {
    'advanced-long-room-owns-sound': room_owns_sound,
    'advanced-long-scope-revision': scope_revision,
    'advanced-long-frame-reprise': frame_reprise,
    'advanced-long-result-boundary': result_boundary,
}

AUDIO = {'advanced-long-room-owns-sound': illustrated_rooms}

POSTERS = {
    'advanced-long-room-owns-sound': 1.90,
    'advanced-long-scope-revision': 2.30,
    'advanced-long-frame-reprise': 2.18,
    'advanced-long-result-boundary': 2.15,
}
