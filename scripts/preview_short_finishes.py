"""Portrait excerpts that demonstrate four body and finish decisions."""
from array import array
from functools import lru_cache, partial
from math import sin, tau
import sys
import wave

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from preview_common import ease, font, progress
from preview_live_action import GOLD, INK, PAPER, type_at
from preview_plates import shot, source
from preview_sound import RATE, impact

SIZE = (360, 640)
DURATION = 3.2
MINT = '#bce7be'
DARK = '#142722'
STEP_SEAM = 3.15


def label(image, text, x, y, size=23, accent=None):
    draw = ImageDraw.Draw(image, 'RGBA')
    width = draw.textlength(text, font=font(size))
    draw.rounded_rectangle((x, y, x + width + 22, y + size + 14), 7,
                           fill=accent or (15, 28, 24, 236))
    type_at(image, (x + 11, y + (size + 14)/2), text, size, INK if accent else PAPER, 'lm')


def crop(raw, extent):
    return raw.transform(SIZE, Image.Transform.EXTENT, extent, Image.Resampling.BICUBIC)


@lru_cache(maxsize=1)
def index_card():
    card = Image.new('RGBA', (136, 93))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((3, 4, 131, 89), 5, fill='#f6ecce', outline='#927553', width=2)
    draw.rectangle((11, 13, 26, 80), fill='#d99650')
    type_at(card, (37, 30), 'CUT 02', 19, '#1c352d', 'lm')
    type_at(card, (37, 60), 'HOLD', 24, '#1c352d', 'lm')
    return card


def prop_relay(t):
    if t < .91:
        image = shot('host-live', .70 + t*.80, zoom=.99, x=-43, size=SIZE)
        label(image, 'Staged handover', 17, 55, 17)
        label(image, '“Check the note.”', 19, 495, 26)
    elif t < 1.64:
        image = Image.new('RGB', SIZE, DARK)
        size = (177, 384)
        sender = shot('host-live', 1.44 + (t-.91)*.40, zoom=1.05, x=-65, size=size)
        receiver = shot('portrait-live', 2.37 + (t-.91)*.60, size=size)
        image.paste(sender, (0, 95))
        image.paste(ImageOps.mirror(receiver), (183, 95))
        ImageDraw.Draw(image).line((179, 95, 179, 479), fill='#c1d1b9', width=2)
        label(image, 'Host', 16, 118, 16)
        label(image, 'Editor', 207, 118, 16)
        label(image, 'Follow the card', 19, 500, 23)
    else:
        image = ImageOps.mirror(shot('portrait-live', 2.54 + (t-1.64)*.32, size=SIZE))
        label(image, 'Editor', 17, 55, 18)
        if t >= 1.99:
            label(image, '“Give that cut a hold.”', 19, 499, 25, MINT)

    across = ease(progress(t, .35, 1.69))
    x = round(32 + 166*across)
    y = round(375 + 9*sin(across*tau))
    card = index_card().rotate(10 - 18*across, resample=Image.Resampling.BICUBIC, expand=True)
    image.paste(card, (x, y), card)
    return image


def crop_landing(t):
    # Both transforms map the chosen sole/sidewalk point to the same place.
    stamp = .10 + t*.68
    raw = source('walk-live', stamp)
    if t < .89 or t >= 2.44:
        image = crop(raw, (222, 0, 424.5, 360))
        label(image, 'Wide' if t < .89 else 'Same direction', 17, 64, 19)
    else:
        image = crop(raw, (252.45, 94.5, 384.075, 328.5))
        label(image, 'Same contact', 17, 64, 23, MINT)

    # The leading heel settles at source time .70 on the paving line.
    if .57 <= t < 1.57:
        strength = 1-progress(t, 1.04, 1.57)
        draw = ImageDraw.Draw(image, 'RGBA')
        draw.arc((137, 474, 174, 499), 0, 175, fill=(253, 216, 103, round(255*strength)), width=3)
        draw.line((141, 500, 171, 500), fill=(253, 216, 103, round(192*strength)), width=2)
    return image


START_Y = 484
CM = 9.5
TARGET_Y = START_Y - 20*CM
RUN_START = .56
START_SPEED = 52


@lru_cache(maxsize=1)
def measuring_board():
    room = shot('room', size=SIZE).filter(ImageFilter.GaussianBlur(18))
    image = Image.blend(ImageEnhance.Brightness(room).enhance(.49), Image.new('RGB', SIZE, DARK), .56)
    draw = ImageDraw.Draw(image, 'RGBA')
    type_at(image, (19, 62), 'Same start. Same target.', 24, PAPER, 'lm')
    type_at(image, (19, 94), 'Illustrative trials', 16, MINT, 'lm')
    draw.rounded_rectangle((40, 139, 335, 523), 12, fill='#304d43', outline='#9bb09b', width=2)
    for x, color in ((112, '#70877a'), (267, '#9ea891')):
        draw.rounded_rectangle((x-39, 155, x+39, 507), 9, fill=color)
        draw.line((x-28, 169, x-28, 487), fill='#c3c9aa', width=2)
        draw.line((x+28, 169, x+28, 487), fill='#c3c9aa', width=2)
    for distance in range(0, 31, 5):
        y = round(START_Y-distance*CM)
        draw.line((172, y, 186, y), fill='#b4c9ac', width=2)
        type_at(image, (202, y), str(distance), 12, PAPER, 'rm')
    draw.line((51, START_Y, 323, START_Y), fill='#dce4d2', width=2)
    draw.line((51, TARGET_Y, 323, TARGET_Y), fill=GOLD, width=3)
    label(image, '20 cm target', 46, round(TARGET_Y)-37, 17, GOLD)
    type_at(image, (112, 552), 'Felt', 22)
    type_at(image, (267, 552), 'Smooth', 22)
    return image


def measured_travel(t, x, distance, image):
    deceleration = START_SPEED**2/(2*distance)
    elapsed = max(0, min(t-RUN_START, START_SPEED/deceleration))
    traveled = START_SPEED*elapsed - deceleration*elapsed**2/2
    y = round(START_Y-CM*traveled)
    draw = ImageDraw.Draw(image)
    draw.ellipse((x-17, y-7, x+18, y+17), fill='#344839')
    draw.ellipse((x-17, y-11, x+17, y+12), fill='#d5a24e', outline='#ffdd88', width=2)
    draw.ellipse((x-10, y-7, x+10, y+6), fill='#eab866')
    if t >= 1.68:
        label(image, f'{distance} cm', x-36, y+26, 16, MINT if distance >= 20 else None)


def same_ruler(t):
    image = measuring_board().copy()
    measured_travel(t, 112, 14, image)
    measured_travel(t, 267, 24, image)
    return image


LOOP_CROP = (129, 40, 309, 360)


def contact_loop(t):
    if t < 2.39:
        stamp = .75 + t*.70
    else:
        stamp = .16 + (t-2.39)*.72
    image = crop(source('steps-live', stamp), LOOP_CROP)
    if .98 <= t < 2.21:
        label(image, 'One step complete', 19, 64, 24, MINT)
    return image


def contact_sound(cues, path, wrap=False):
    samples = array('h')
    for index in range(round(DURATION*RATE)):
        t = index/RATE
        # A full period count keeps the stationary floor smooth over a replay wrap.
        level = .007*sin(tau*50*t)+.003*sin(tau*90*t)
        for at, frequency, decay in cues:
            level += .22*impact(t, at, decay, frequency)
            level += .049*impact(t, at, 52, frequency*3)
            if wrap:
                level += .22*impact(t + DURATION, at, decay, frequency)
                level += .049*impact(t + DURATION, at, 52, frequency*3)
        samples.append(round(32767*level))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as output:
        output.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(samples.tobytes())


SCENES = {
    'advanced-short-prop-relay': prop_relay,
    'advanced-short-crop-landing': crop_landing,
    'advanced-short-same-ruler': same_ruler,
    'advanced-short-one-contact-loop': contact_loop,
}
POSTERS = {
    'advanced-short-prop-relay': 1.32,
    'advanced-short-crop-landing': .97,
    'advanced-short-same-ruler': 2.43,
    'advanced-short-one-contact-loop': 1.44,
}
AUDIO = {
    'advanced-short-prop-relay': partial(contact_sound, ((1.51, 263, 31),)),
    'advanced-short-crop-landing': partial(contact_sound, ((.89, 92, 24),)),
    'advanced-short-one-contact-loop': partial(contact_sound, ((STEP_SEAM, 76, 14),), wrap=True),
}
