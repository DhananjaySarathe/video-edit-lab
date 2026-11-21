"""Landscape preview repairs using local plates and visible editorial cues."""

from bisect import bisect_right
from math import cos, pi, sin
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

from preview_common import H, W, ease, font, progress
from preview_cuts import crop
from preview_plates import shot, source


SIZE = W, H
INK = '#142820'
PAPER = '#fff7e0'
GOLD = '#f4c979'


def cue(frame, value, emphasize=False):
    draw = ImageDraw.Draw(frame)
    width = round(font(19).getlength(value)) + 22
    draw.rounded_rectangle((17, 16, 17 + width, 50), 5, fill=GOLD if emphasize else INK)
    draw.text((28, 33), value, font=font(19), fill=INK if emphasize else PAPER, anchor='lm')


FLOOR_X, FLOOR_Y = 374, 294
_random = Random(624)
PLUME = tuple((_random.uniform(.0, 1.68), _random.uniform(-1, 1), _random.uniform(.7, 1.3))
              for _ in range(29))


def grounded_particles(t):
    room = shot('room')
    amount = ease(progress(t, .43, .98)) * (1 - .56 * ease(progress(t, 2.34, 3.2)))
    if amount:
        contact = Image.new('RGBA', SIZE)
        contact_marks = ImageDraw.Draw(contact)
        contact_marks.ellipse((FLOOR_X - 54, FLOOR_Y - 8, FLOOR_X + 63, FLOOR_Y + 12),
                              fill=(69, 43, 23, round(120 * amount)))
        room.paste(contact, (0, 0), contact.filter(ImageFilter.GaussianBlur(7)))

        vapour = Image.new('RGBA', SIZE)
        wisps = ImageDraw.Draw(vapour)
        points = []
        for index, (offset, drift, weight) in enumerate(PLUME):
            age = (max(0, t - .37) + offset) % 1.68
            x = FLOOR_X + drift * (19 + 46 * age) + 28 * age
            y = FLOOR_Y - (20 * weight + 17 * age) * age
            envelope = sin(pi * age / 1.68) ** 2
            radius = (11 + age * 15) * weight
            opacity = round(110 * amount * envelope)
            wisps.ellipse((x - radius, y - radius * .5, x + radius, y + radius * .37),
                          fill=(225, 208, 169, opacity))
            if index % 2:
                points.append((x, y - 7, round(190 * amount * envelope)))
        vapour = vapour.filter(ImageFilter.GaussianBlur(7))
        room.paste(vapour, (0, 0), vapour)
        dust = ImageDraw.Draw(room, 'RGBA')
        for x, y, opacity in points:
            dust.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(255, 229, 170, opacity))

    if t < 1.24:
        guide = ImageDraw.Draw(room, 'RGBA')
        opacity = round(220 * (1 - ease(progress(t, .56, 1.24))))
        reference = ((FLOOR_X - 52, FLOOR_Y - 11), (FLOOR_X + 46, FLOOR_Y - 8),
                     (FLOOR_X + 68, FLOOR_Y + 13), (FLOOR_X - 61, FLOOR_Y + 6))
        guide.line((*reference, reference[0]), fill=(255, 232, 170, opacity), width=2)
        guide.ellipse((FLOOR_X - 4, FLOOR_Y - 4, FLOOR_X + 4, FLOOR_Y + 4),
                      fill=(255, 232, 170, opacity))

    # The projected floor, contact shadow and emitter all have the same camera transform.
    moved = crop(room, 1.02 + .19 * ease(progress(t, 0, 3.2)), 320 + 45 * t / 3.2, 211)
    cue(moved, 'Track the floor first' if t < .58 else 'Dust stays on the same floor mark', t >= 1.12)
    return moved


HAND_TRACK = ((1.84, 255, 199), (2.00, 240, 197), (2.20, 201, 182), (2.39, 159, 198),
              (2.58, 173, 209), (2.75, 206, 214))
HAND_STAMPS = tuple(k[0] for k in HAND_TRACK)


def hand_point(stamp):
    index = min(len(HAND_TRACK) - 2, max(0, bisect_right(HAND_STAMPS, stamp) - 1))
    start, end = HAND_TRACK[index:index + 2]
    p = progress(stamp, start[0], end[0])
    return start[1] + (end[1] - start[1]) * p, start[2] + (end[2] - start[2]) * p


def gesture_trigger(t):
    stamp = 1.54 + t * .397
    picture = shot('host-live', stamp)
    amount = ease(progress(stamp, 1.83, 1.98)) * (1 - ease(progress(stamp, 2.48, 2.73)))
    if amount:
        x, y = hand_point(stamp)
        layer = Image.new('RGB', SIZE)
        flare = ImageDraw.Draw(layer)
        radius = 18 + 21 * amount
        color = (round(246 * amount), round(182 * amount), round(88 * amount))
        for ray in range(10):
            angle = ray * pi / 5 + t * .75
            reach = radius * (.72 + .25 * sin(ray * 4 + t * 7))
            dx, dy = cos(angle), sin(angle)
            flare.line((x + dx * reach * .27, y + dy * reach * .27, x + dx * reach, y + dy * reach),
                       fill=color, width=3 if ray % 3 == 0 else 2)
        flare.ellipse((x - 5, y - 5, x + 5, y + 5),
                      fill=(round(255 * amount), round(235 * amount), round(172 * amount)))
        light = Image.new('RGB', SIZE)
        light_radius = 19 + 6 * amount
        ImageDraw.Draw(light).ellipse((x - light_radius, y - light_radius, x + light_radius, y + light_radius),
                                      fill=(round(92 * amount), round(53 * amount), round(21 * amount)))
        picture = ImageChops.add(picture, light.filter(ImageFilter.GaussianBlur(15)))
        picture = ImageChops.add(picture, layer)

    framed = crop(picture, 1.19, 263, 166)
    action = 'Wait for the hand' if stamp < 1.83 else 'Spark follows the palm' if stamp < 2.51 else 'Fade as the hand lowers'
    cue(framed, action, 1.95 < stamp < 2.51)
    return framed


ZOOM_CUT = 1.16
FACE = (274, 52)
ANCHOR = (311, 102)


def subject_extent(scale):
    fx, fy = FACE
    ax, ay = ANCHOR
    return fx - ax / scale, fy - ay / scale, fx + (W - ax) / scale, fy + (H - ay) / scale


def cutout_match_zoom(t):
    changed = t >= ZOOM_CUT
    plate_name = 'walk-live' if changed else 'room'
    plate_t = t - ZOOM_CUT + .28 if changed else 0
    picture = shot(plate_name, plate_t, 1.06 if changed else 1.02, 14 if changed else -8, 12 if changed else 4)
    picture = picture.filter(ImageFilter.GaussianBlur(1.3 if changed else .6))
    zoom_up = ease(progress(t, .59, ZOOM_CUT))
    zoom_down = ease(progress(t, ZOOM_CUT, 1.91))
    scale = 1.10 + 1.86 * zoom_up - 1.80 * zoom_down
    stamp = .38 + min(t, .58) + max(0, t - 1.72) * .79
    bounds = subject_extent(scale)
    actor = source('host-live', stamp).transform(SIZE, Image.Transform.EXTENT, bounds, Image.Resampling.BICUBIC)
    matte = source('host-live-matte', stamp).transform(SIZE, Image.Transform.EXTENT, bounds, Image.Resampling.BICUBIC)
    stroke = ease(progress(t, .53, .80)) * (1 - ease(progress(t, 1.22, 1.81)))
    if stroke:
        outline = ImageChops.subtract(matte.filter(ImageFilter.MaxFilter(9)), matte)
        picture.paste(GOLD, (0, 0, W, H), outline.point(lambda p: round(p * stroke)))
    picture.paste(actor, (0, 0), matte)
    step = 'First shot' if t < .59 else 'Scale the cutout' if not changed else 'Match it across the cut' if t < 1.91 else 'Hold the new shot'
    cue(picture, step, .82 < t < 1.67)
    return picture


COLD_OPEN_EXIT = 1.28


def cold_open_before_resolution(t):
    if t < COLD_OPEN_EXIT:
        # This pass ends at 1.70 source seconds, with the pour still in progress.
        frame = shot('coffee-live', .42 + t, 1.43, -56, 24)
        cue(frame, 'Later · the final pour')
        if t > .34:
            draw = ImageDraw.Draw(frame)
            draw.rounded_rectangle((28, 291, 418, 337), 5, fill=INK)
            draw.text((44, 314), 'Will the pattern hold?', font=font(31), fill=PAPER, anchor='lm')
        return frame

    earlier = .10 + .45 * (t - COLD_OPEN_EXIT)
    frame = shot('coffee-live', earlier, 1.03, -6, 2)
    cue(frame, 'Earlier · set the cup angle', True)
    return frame


SCENES = {
    'grounded-particle-overlay': grounded_particles,
    'gesture-triggered-vfx': gesture_trigger,
    'cutout-match-zoom': cutout_match_zoom,
    'long-cold-open': cold_open_before_resolution,
}

POSTERS = {
    'grounded-particle-overlay': 1.7,
    'gesture-triggered-vfx': 1.62,
    'cutout-match-zoom': 1.33,
    'long-cold-open': .74,
}
