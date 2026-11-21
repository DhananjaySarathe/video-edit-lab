"""Original opening edits built from the project's licensed live-action plates."""
from array import array
import sys
import wave

from PIL import Image, ImageDraw

from preview_common import H, W, blend, ease, font, progress
from preview_plates import source
from preview_sound import LENGTH, RATE, impact

PAPER = '#f8f3e4'
MINT = '#c4f2cf'
INK = '#142921'
GOLD = '#ffd478'
PHOTO_WIDTH = 403

SCORE_INSERT = .75
SCORE_UPDATE = 1.2
GESTURE_START = .25
GESTURE_HOLD = 1.55
ARTIFACT_INSERT = .6
FLOW_EVIDENCE = 1.75
ARTIFACT_CROP = (69, 0, 420, 313)


def photo_panel(name, timestamp, area):
    image = Image.new('RGB', (W, H), INK)
    crop = source(name, timestamp).crop(area)
    image.paste(crop.resize((PHOTO_WIDTH, H), Image.Resampling.BICUBIC), (0, 0))
    return image


def live_score(t):
    source_time = min(GESTURE_HOLD, GESTURE_START + t)
    area = (68, 0, 468, 357) if t < SCORE_INSERT else (120, 115, 393, 359)
    image = photo_panel('host-live', source_time, area)
    draw = ImageDraw.Draw(image)
    draw.text((429, 64), 'Next move?', fill=PAPER, font=font(32), anchor='lm')

    confirmed = t >= SCORE_UPDATE
    settle = ease(progress(t, SCORE_UPDATE, SCORE_UPDATE + .23))
    active_color = blend((255, 212, 120), (196, 242, 207), settle)
    for index, (choice, y) in enumerate((('Together', 147), ('Apart', 247))):
        selected = index == 0 and confirmed
        background = active_color if selected else '#253e32'
        color = INK if selected else PAPER
        draw.rounded_rectangle((421, y - 41, 621, y + 41), 8, fill=background)
        draw.text((438, y), choice, font=font(23), fill=color, anchor='lm')
        draw.text((603, y - 2), '1' if selected else '0', font=font(42), fill=color, anchor='rm')
    return image


def score_audio(path):
    samples = array('h', (round(32767 * .22 * impact(i / RATE, SCORE_UPDATE, 36, 485))
                          for i in range(round(RATE * LENGTH))))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as recording:
        recording.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        recording.writeframes(samples.tobytes())


def spout_pin(t):
    # The lip is hand-tracked in the close crop of the plate, in source pixels.
    keys = ((.75, 267, 96), (1.20, 269, 95), (1.45, 278, 94),
            (1.60, 291, 88), (1.70, 298, 75), (FLOW_EVIDENCE, 306, 70))
    for (start, x, y), (end, next_x, next_y) in zip(keys, keys[1:]):
        if t <= end:
            fraction = progress(t, start, end)
            x += (next_x - x) * fraction
            y += (next_y - y) * fraction
            break
    left, top, right, bottom = ARTIFACT_CROP
    return (round((x - left) * PHOTO_WIDTH / (right - left)),
            round((y - top) * H / (bottom - top)))


def artifact_evidence(t):
    if t < ARTIFACT_INSERT:
        image = source('coffee-live', t).copy()
        draw = ImageDraw.Draw(image, 'RGBA')
        draw.rounded_rectangle((22, 283, 409, 337), 7, fill=(16, 33, 28, 245))
        draw.text((38, 309), 'Where does the flow break?', font=font(27), fill=PAPER, anchor='lm')
        return image

    # Hold a readable gap at frame offset 35 in the 20 fps source.
    source_time = min(t, FLOW_EVIDENCE)
    image = photo_panel('coffee-live', source_time, ARTIFACT_CROP)
    draw = ImageDraw.Draw(image, 'RGBA')
    label = ease(progress(t, .77, .98))
    if label:
        x, y = spout_pin(source_time)
        alpha = round(255 * label)
        draw.line(((415, 102), (356, 102), (x, y)), fill=(255, 212, 120, alpha), width=3)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 212, 120, alpha))
        draw.text((430, 101), 'Spout', font=font(29), fill=(248, 243, 228, alpha), anchor='lm')
    if t >= FLOW_EVIDENCE:
        draw.line((429, 155, 612, 155), fill='#456356', width=1)
        draw.text((429, 187), 'Visible gap', font=font(22), fill=PAPER, anchor='lm')
        draw.text((427, 241), f'{FLOW_EVIDENCE:.2f} s', font=font(48), fill=MINT, anchor='lm')
        draw.text((429, 281), 'In this clip', font=font(20, 'regular'), fill=PAPER, anchor='lm')
    return image


SCENES = {
    'advanced-live-score': live_score,
    'advanced-artifact-evidence': artifact_evidence,
}
AUDIO = {'advanced-live-score': score_audio}
