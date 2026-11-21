"""Original long-form editing demonstrations using the lab's licensed footage."""

from array import array
from math import sin, tau
from random import Random
import sys
import wave

from PIL import Image, ImageDraw, ImageEnhance

from preview_common import H, W, ease, font, progress
from preview_live_action import type_at
from preview_plates import shot
from preview_sound import LENGTH, RATE, bed, playhead, wave_track, window


INK = '#172923'
DEEP = '#10221d'
PAPER = '#f6f2e6'
MINT = '#bcdfc4'
GOLD = '#f4c36f'
MARK = '#ffe1a2'
MUTED = '#566c60'
ROUTE = ((0, 0), (48, 0), (78, -39), (122, -39), (154, -12))
SCORE_DOWN, SCORE_BACK = 1.05, 2.55


def stage(image, value):
    draw = ImageDraw.Draw(image)
    width = round(draw.textlength(value, font=font(19)))
    draw.rounded_rectangle((18, 17, 42 + width, 54), 5, fill=DEEP)
    type_at(image, (30, 36), value, 19, PAPER, 'lm')


def footer(image, value, subtitle=None):
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 267, W, H), fill=DEEP)
    type_at(image, (23, 294 if subtitle else 312), value, 35, PAPER, 'lm')
    if subtitle:
        type_at(image, (24, 332), subtitle, 21, MINT, 'lm')


def route_diagram(image, amount=0):
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((355, 67, 614, 247), 10, fill=INK, outline='#688572', width=2)
    type_at(image, (375, 93), 'Walk route', 23, PAPER, 'lm')
    for y in (115, 147, 180, 214):
        draw.line((369, y, 600, y), fill='#344c41')
    for x in (405, 444, 484, 523, 562):
        draw.line((x, 114, x, 211), fill='#344c41')
    points = [(399 + x, 172 + y) for x, y in ROUTE]
    draw.line(points, fill=MINT, width=5, joint='curve')

    if amount:
        path_position = min(amount * (len(points) - 1), len(points) - 1.001)
        index = int(path_position)
        mix = path_position - index
        here = tuple(a + (b - a) * mix for a, b in zip(points[index], points[index + 1]))
        draw.line([*points[:index + 1], here], fill=GOLD, width=5, joint='curve')
        draw.ellipse((here[0] - 7, here[1] - 7, here[0] + 7, here[1] + 7), fill=GOLD)

    for index, name in ((0, 'A'), (-1, 'B')):
        x, y = points[index]
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=MINT if index == 0 else GOLD)
        type_at(image, (x, y + 25), name, 20, PAPER)
    type_at(image, (375, 227), 'A  Corner     B  Steps', 17, '#e5eee4', 'lm')


def model_handoff(t):
    if t < .8:
        image = shot('host-live', t + .32, 1.14, 16, -6)
        stage(image, 'Host')
        line, subtitle = 'Where does the route turn?', 'Set up one thing to look for.'
    elif t < 1.8:
        image = Image.new('RGB', (W, H), PAPER)
        draw = ImageDraw.Draw(image)
        stage(image, 'Source')
        type_at(image, (25, 113), 'Walk log', 47, INK, 'lm')
        draw.line((25, 145, 323, 145), fill='#adbaad', width=2)
        type_at(image, (27, 176), '01  Start at the corner', 22, INK, 'lm')
        type_at(image, (27, 217), '02  Finish at the steps', 22, INK, 'lm')
        line, subtitle = 'The same route in the log', 'Illustrative field record'
    else:
        image = shot('walk-live', t - 1.8 + .4, 1.24, 74, -12)
        stage(image, 'Explanation')
        line, subtitle = 'Follow the turn from A to B', 'The map and landmark stay under your eye.'

    route_diagram(image, ease(progress(t, 1.93, 2.93)))
    footer(image, line, subtitle)
    return image


def source_card(image, t):
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((88, 69, 552, 253), 7, fill=PAPER, outline='#aabaac', width=2)
    type_at(image, (109, 96), 'Sample pour log', 26, INK, 'lm')
    draw.line((110, 120, 530, 120), fill='#aabaac', width=2)
    type_at(image, (111, 144), '3 trials', 22, MUTED, 'lm')
    end = 106 + 362 * ease(progress(t, .73, 1.16))
    if end > 117:
        draw.rounded_rectangle((106, 162, end, 204), 3, fill=MARK)
    type_at(image, (111, 182), '2 patterns held', 33, INK, 'lm')
    type_at(image, (111, 228), '1 pattern broke', 23, INK, 'lm')


def evidence_answer(t):
    if t < .65:
        image = shot('host-live', .40 + t, 1.25, -22, -5)
        stage(image, 'Question')
        footer(image, 'Did it hold every time?')
        return image

    if t < 1.97:
        image = Image.new('RGB', (W, H), '#dbe4d9')
        stage(image, 'Evidence')
        source_card(image, t)
        footer(image, 'Read the observed result')
        return image

    image = shot('host-live', .46 + t, 1.17, 25, -5)
    stage(image, 'Interpretation')
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((358, 96, 613, 210), 7, fill=PAPER, outline='#aabaac', width=2)
    type_at(image, (372, 125), 'Same sample log', 21, MUTED, 'lm')
    draw.rounded_rectangle((369, 147, 602, 191), 3, fill=MARK)
    type_at(image, (376, 169), '2 patterns held', 27, INK, 'lm')
    footer(image, 'Test again before relying on it', 'One result still failed.')
    return image


def intro_proof(t):
    if t < .7 or t >= 2.22:
        image = shot('host-live', .11 + t, 1.18, 23, -4)
        cup = shot('coffee-live', .24 + t * .17, 1.35, -25, 10, (220, 149))
        image.paste(cup, (382, 83))
        ImageDraw.Draw(image).rectangle((381, 82, 602, 232), outline=GOLD, width=2)
        stage(image, 'The attempt')
        if t < .7:
            footer(image, 'Will the swirl hold?')
        else:
            footer(image, 'Pass if the swirl holds 3 seconds', 'Keep the outcome for the test.')
        return image

    if t < 1.48:
        image = shot('coffee-live', .1 + t, 1.20, -26, -10)
        stage(image, 'The brewer')
        footer(image, 'Controls the pour')
        return image

    image = shot('coffee-live', .51 + t * .57, 1.49, -37, -4)
    stage(image, 'The test lead')
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((391, 91, 615, 190), 7, fill=INK)
    type_at(image, (405, 115), 'Hold timer', 21, MINT, 'lm')
    type_at(image, (404, 157), '0.0 / 3 s', 39, PAPER, 'lm')
    footer(image, 'Measures how long it holds')
    return image


def score_gain(t):
    return 1 - window(t, SCORE_DOWN - .05, SCORE_BACK + .09, .09)


def decision_hold(t):
    if t < .40:
        image = shot('host-live', t, 1.11, -15, -10)
    elif t < .72:
        image = shot('host-live', t, 1.68, -41, 33)
    elif t < SCORE_BACK:
        image = shot('host-live', t, 1.33, -95, -15)
    else:
        image = shot('host-live', t, 1.14, -15, -6)

    if SCORE_DOWN <= t < SCORE_BACK:
        stage(image, 'Hold the choice · score out')
    elif t < SCORE_DOWN:
        stage(image, 'Quick cuts · score in')
    else:
        stage(image, 'Action resumes · score in')

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 263, W, H), fill=DEEP)
    type_at(image, (23, 287), 'Score', 19, PAPER, 'lm')
    type_at(image, (23, 333), 'Room', 19, PAPER, 'lm')
    x0, x1 = 104, 616
    cursor = x0 + (x1 - x0) * t / LENGTH
    wave_track(draw, x0, x1, 287, cursor, lambda stamp: .82 * score_gain(stamp), GOLD, '#735b3d', 17)
    wave_track(draw, x0, x1, 333, cursor, lambda stamp: .35, MINT, '#4f6b59', 12)
    playhead(draw, t, x0, x1, 270, 352)
    return image


def decision_audio(path):
    rng = Random(43)
    room = 0
    samples = array('h')
    for index in range(round(RATE * LENGTH)):
        stamp = index / RATE
        room = .93 * room + .07 * rng.uniform(-1, 1)
        tone = .046 * room + .013 * sin(tau * 122 * stamp)
        score = .44 * bed(stamp, shift=2, pace=.27) * score_gain(stamp)
        scale = window(stamp, 0, LENGTH, .08)
        samples.append(round(32767 * (tone + score) * scale))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as output:
        output.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(samples.tobytes())


SCENES = {
    'advanced-model-handoff': model_handoff,
    'advanced-evidence-answer': evidence_answer,
    'advanced-intro-proof': intro_proof,
    'advanced-decision-hold': decision_hold,
}
AUDIO = {'advanced-decision-hold': decision_audio}
