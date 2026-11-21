"""Original previews for synchronized proof, staged data and opening structure."""
from math import cos, pi, sin

from PIL import Image, ImageDraw, ImageEnhance

from preview_common import H, W
from preview_live_action import GOLD, INK, MINT, PAPER, orb_layer, tag, tween, type_at
from preview_plates import shot
from preview_spatial import warp


def masked_title(frame, matte, t):
    width, height = frame.size
    amount = tween(t, .63, .99)
    plate = ImageEnhance.Brightness(frame).enhance(1 - .31 * amount)
    title = Image.new('RGBA', frame.size)
    y = round(height * (.23 + .12 * (1 - amount)))
    type_at(title, (width * .51, y), 'ONE CUT', round(width * .20), GOLD)
    draw = ImageDraw.Draw(title)
    draw.line((width * .10, y + width * .10, width * .91, y + width * .10), fill=GOLD, width=2)
    alpha = title.getchannel('A').point(lambda value: round(value * amount))
    plate.paste(title, (0, 0), alpha)
    plate.paste(frame, (0, 0), matte)
    return plate


def matched_proof(t):
    if t >= 2.55:
        frame = shot('host-live', t, 1.08, -32, -30)
        matte = shot('host-live-matte', t, 1.08, -32, -30)
        image = masked_title(frame, matte, t)
        tag(image, 'Finished edit', 18, 18, True)
        return image

    image = Image.new('RGB', (W, H), '#18241e')
    panel_size = (297, 286)
    frame = shot('host-live', t, 1.16, -40, -15, panel_size)
    matte = shot('host-live-matte', t, 1.16, -40, -15, panel_size)
    image.paste(frame, (15, 55))
    image.paste(masked_title(frame, matte, t), (328, 55))
    tag(image, 'RAW TAKE', 15, 15)
    tag(image, 'EDITED TAKE', 328, 15, t >= .65)
    return image


def tracking_card(t):
    card = Image.new('RGBA', (370, 196), (14, 32, 34, 250))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((1, 1, 368, 194), 9, outline='#95d3c9', width=2)
    type_at(card, (17, 26), 'Time to render', 25, PAPER, 'lm')
    type_at(card, (352, 27), 'Sample data', 17, MINT, 'rm')
    points = [(57, 73), (101, 88), (143, 84), (187, 108), (232, 102), (274, 130), (333, 118)]
    for position, label in ((75, '8s'), (104, '6s'), (134, '4s')):
        draw.line((50, position, 344, position), fill='#385754', width=1)
        type_at(card, (39, position), label, 16, '#c1dcd4', 'rm')
    pieces = tween(t, .96, 1.59) * (len(points) - 1)
    index = int(pieces)
    if pieces > 0:
        a = points[index]
        b = points[min(index + 1, len(points) - 1)]
        final = tuple(i + (j - i) * (pieces - index) for i, j in zip(a, b))
        draw.line([*points[:index + 1], final], fill=MINT, width=4, joint='curve')
    if t >= 1.65:
        x, y = points[-2]
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=GOLD)
        type_at(card, (x, y - 19), 'New setting', 17, GOLD, 'rm')
    if t >= 2.26:
        type_at(card, (17, 167), 'Timing alone cannot establish cause.', 20, PAPER, 'lm')
    return card


def anchored_answer(t):
    room = ImageEnhance.Brightness(shot('room')).enhance(.76)
    appear = tween(t, .54, 1.02)
    orb_amount = (1 - tween(t, .65, 1.04)) * tween(t, -.23, .25)
    orb_layer(room, t, (273, 142), 49, orb_amount)
    if appear > 0:
        w, h = 173 * appear, 89 * appear
        quad = [(365 - w, 178 - h), (365 + w, 169 - h), (366 + w, 173 + h), (365 - w, 180 + h)]
        warp(room, tracking_card(t), quad)
    scale = 1.04 + .065 * tween(t, .06, 3.05)
    cx = 318 + 17 * sin(t * .95)
    cy = 180 + 7 * sin(t * .84)
    image = room.transform((W, H), Image.Transform.EXTENT,
                           (cx - 320 / scale, cy - 180 / scale, cx + 320 / scale, cy + 180 / scale),
                           Image.Resampling.BICUBIC)
    step = 'Room anchor' if t < .54 else 'Chart opens' if t < 1.65 else 'Point is marked' if t < 2.26 else 'Hold for context'
    tag(image, step, 17, 18, t >= 1.65)
    return image


def clock_chart(t):
    image = Image.new('RGB', (W, H), '#f4eedc')
    draw = ImageDraw.Draw(image)
    cx, cy = 205, 194
    draw.ellipse((cx - 140, cy - 137, cx + 144, cy + 147), fill='#d9d5bf')
    draw.ellipse((cx - 140, cy - 142, cx + 140, cy + 138), fill='#fcf8e9', outline='#243c34', width=3)
    for tick in range(10):
        angle = (tick / 10 - .25) * 2 * pi
        draw.line([(cx + radius * cos(angle), cy + radius * sin(angle)) for radius in (114, 126)],
                  fill='#5e6656', width=3)
    type_at(image, (cx, cy - 99), '0 / 10', 17, '#31483c')
    run_a = tween(t, .60, 1.35)
    run_b = tween(t, 1.59, 2.46)
    angle = (4 * (1 - run_b) + 6 * run_b) / 10 * 360 * run_a
    if t < .60:
        angle = 0
    for radius, ratio, fill in ((93, .4 * run_a, '#a95b2c'), (67, .6 * run_b, '#337760')):
        if ratio > 0:
            draw.arc((cx - radius, cy - radius, cx + radius, cy + radius),
                     -90, -90 + 360 * ratio, fill=fill, width=15)
    a = (angle / 360 - .25) * 2 * pi
    draw.line((cx, cy, cx + 73 * cos(a), cy + 73 * sin(a)), fill='#273c34', width=6)
    draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill='#273c34')
    type_at(image, (366, 87), 'A 10-minute window', 27, '#233930', 'lm')
    type_at(image, (367, 120), 'Illustrative values', 17, '#5a6255', 'lm')
    if t >= 1.12:
        type_at(image, (367, 172), 'Test A', 22, '#743b20', 'lm')
        type_at(image, (589, 172), '4 min', 31, '#743b20', 'rm')
    if t >= 2.1:
        type_at(image, (367, 222), 'Test B', 22, '#275a48', 'lm')
        type_at(image, (589, 222), '6 min', 31, '#275a48', 'rm')
    if t >= 2.46:
        draw.line((367, 248, 590, 248), fill='#a6ab94', width=1)
        type_at(image, (367, 275), 'Difference', 20, '#33463a', 'lm')
        type_at(image, (589, 275), '2 min', 29, '#33463a', 'rm')
    return image


def threshold(t):
    if t < .59:
        image = shot('coffee-live', 1.07 + .5 * t, 1.12, -24, 0)
        tag(image, 'LATER · THE FINAL TEST')
    elif t < 1.45:
        image = shot('coffee-live', 1.35 + .48 * (t - .59), 1.6, -19, 26)
        tag(image, 'LATER · THE FINAL TEST')
        type_at(image, (320, 300), 'Will the edge hold?', 37, PAPER, stroke=2)
    elif t < 1.59:
        image = Image.new('RGB', (W, H), INK)
    else:
        image = shot('coffee-live', .10 + .55 * (t - 1.59), 1.03, -20, -7)
        tag(image, 'EARLIER · THE FIRST POUR', accent=True)
    return image


SCENES = {
    'advanced-matched-proof': matched_proof,
    'advanced-anchored-answer': anchored_answer,
    'advanced-clock-chart': clock_chart,
    'advanced-threshold': threshold,
}
