"""Worked openings with locally generated, explicitly staged audio."""

from array import array
from functools import lru_cache, partial
from math import exp, sin, tau
from random import Random
import sys
import wave

from PIL import Image, ImageDraw, ImageEnhance

from preview_common import font, progress
from preview_plates import shot
from preview_sound import RATE, voice


WIDE, VERTICAL = (640, 360), (360, 640)
INK, PANEL = '#12241e', '#21372e'
PAPER, MINT = '#fff5e4', '#bce9c2'
GOLD, FADE, CORAL = '#ffd285', '#83a294', '#faad98'
VOICE_LENGTH = 1.28
VOICE_SPLIT = .23
SHORT_PAUSE = .33
FOOT_AT, SOURCE_CONTACT = .40, .70
EARLY_CUT = 4 / 15
FOOT_REPLAYS = (0.0, 1.0, 2.60)
GAP_LOOP, LONG_PAUSE = .55, 1.65
ROOM_REPLAYS = ((.14, 'loop'), (3.02, 'natural'), (15.14, 'loop'), (18.37, 'natural'))
SOLO_REPLAYS = ((6.43, 'loop'), (8.39, 'natural'), (10.35, 'loop'), (12.31, 'natural'))
MASK_REPLAYS = ((.13, 'covered'), (2.65, 'covered'), (6.42, 'clear'),
                (8.61, 'clear'), (11.25, 'clear'), (15.08, 'covered'),
                (19.02, 'after'), (21.62, 'after'))
WORD_BEGIN, WORD_END = .44, .76
CUE_BEGIN, CUE_END = .44, .79
CUE_DELAY = .73


def ns(seconds):
    return round(RATE * seconds)


def caption(draw, x, y, words, size, color=PAPER, anchor='lm'):
    draw.text((x, y), words, font=font(size), fill=color, anchor=anchor)


def badge(draw, x, y, words, size=17):
    width = round(draw.textlength(words, font=font(size)))
    draw.rounded_rectangle((x, y, x + width + 19, y + size + 12), 5, fill=INK)
    caption(draw, x + 9, y + (size + 12) / 2, words, size, MINT)


def blend_window(t, start, end, width):
    return progress(t, start, start + width) * (1 - progress(t, end - width, end))


@lru_cache(maxsize=1)
def voice_source():
    sample = voice()
    return tuple(.67 * sample(.84 + (i + .5) / RATE) for i in range(ns(VOICE_LENGTH)))


def pause_voice(pause):
    source = voice_source()
    cut = ns(VOICE_SPLIT)
    return source[:cut] + (0.0,) * ns(pause) + source[cut:]


@lru_cache(maxsize=2)
def room_source(duration):
    rng = Random(74)
    low = 0.0
    samples = []
    for i in range(ns(duration)):
        t = i / RATE
        noise = rng.uniform(-1, 1)
        low = .91 * low + .09 * noise
        body = .025 * sin(tau * 144 * t) + .02 * sin(tau * 227 * t + .28 * sin(tau * .75 * t))
        flutter = blend_window(t, .14, .31, .075) + .62 * blend_window(t, 1.05, 1.31, .09)
        samples.append(body + low * (.16 + .23 * flutter) + .046 * noise)
    return tuple(samples)


@lru_cache(maxsize=1)
def short_room_takes():
    foreground = pause_voice(SHORT_PAUSE)
    tone = room_source(len(foreground) / RATE)
    before, after = [], []
    for i, (speech, air) in enumerate(zip(foreground, tone)):
        t = i / RATE
        gain = blend_window(t, 0, len(foreground) / RATE, .028)
        hole = blend_window(t, VOICE_SPLIT, VOICE_SPLIT + SHORT_PAUSE, .012)
        before.append(gain * (speech + air * (1 - hole)))
        after.append(gain * (speech + air))
    return tuple(before), tuple(after), tone


@lru_cache(maxsize=1)
def footfall():
    rng = Random(38)
    samples = []
    for i in range(ns(.21)):
        t = i / RATE
        soft_thud = .37 * sin(tau * (91 * t - 57 * t * t)) * exp(-24 * t)
        sole = .26 * rng.uniform(-1, 1) * exp(-66 * t)
        samples.append(progress(t, 0, .003) * (soft_thud + sole))
    return tuple(samples)


@lru_cache(maxsize=1)
def gap_takes():
    wanted = ns(LONG_PAUSE)
    cut = ns(VOICE_SPLIT)
    natural = room_source(VOICE_LENGTH + LONG_PAUSE)[cut:cut + wanted]
    segment = natural[:ns(GAP_LOOP)]
    seam = ns(.013)
    looped = []
    for i in range(wanted):
        j = i % len(segment)
        p = j / seam if i >= len(segment) and j < seam else 1.0
        looped.append(segment[j] * p + natural[len(segment) + j] * (1 - p) if p < 1 else segment[j])
    return {'loop': tuple(looped), 'natural': natural}


@lru_cache(maxsize=1)
def long_room_takes():
    foreground = pause_voice(LONG_PAUSE)
    gap0, gap1 = ns(VOICE_SPLIT), ns(VOICE_SPLIT + LONG_PAUSE)
    context = room_source(len(foreground) / RATE)
    looped = gap_takes()['loop']
    loop, natural = [], []
    for i, (speech, air) in enumerate(zip(foreground, context)):
        t = i / RATE
        gain = blend_window(t, 0, len(foreground) / RATE, .028)
        repair = blend_window(t, VOICE_SPLIT, VOICE_SPLIT + LONG_PAUSE, .013)
        loop_air = air * (1 - repair) + looped[i - gap0] * repair if gap0 <= i < gap1 else air
        loop.append((speech + loop_air) * gain)
        natural.append((speech + air) * gain)
    return {'loop': tuple(loop), 'natural': tuple(natural)}


@lru_cache(maxsize=1)
def masked_takes():
    rng = Random(53)
    effect = []
    for i in range(ns(1.55)):
        t = i / RATE
        noise = rng.uniform(-1, 1)
        fricative = .116 * noise + .1624 * sin(tau * (1130 * t + 408 * t * t))
        effect.append(blend_window(t, CUE_BEGIN, CUE_END, .071) * fricative)
    speech = voice_source() + (0.0,) * (len(effect) - len(voice_source()))
    delayed = (0.0,) * ns(CUE_DELAY) + tuple(effect)[:len(effect) - ns(CUE_DELAY)]
    mixes = {'covered': tuple(a + b for a, b in zip(speech, effect)), 'clear': speech,
             'after': tuple(a + b for a, b in zip(speech, delayed))}
    return speech, tuple(effect), delayed, mixes


def write_track(path, duration, placements):
    mix = [0.0] * ns(duration)
    for start, track in placements:
        offset = ns(start)
        for i, sample in enumerate(track[:len(mix) - offset]):
            mix[offset + i] += sample
    samples = array('h', (round(32767 * max(-.97, min(.97, value))) for value in mix))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        out.writeframes(samples.tobytes())


def write_room_fill(path):
    empty, fixed, tone = short_room_takes()
    air = tuple(s * blend_window(i / RATE, 0, .59, .048) for i, s in enumerate(tone[:ns(.59)]))
    write_track(path, 6., ((0., empty), (1.85, air), (2.70, fixed), (4.31, fixed)))


def write_footfall(path):
    write_track(path, 5.8, ((time + FOOT_AT, footfall()) for time in FOOT_REPLAYS))


def write_room_comparison(path):
    full, gaps = long_room_takes(), gap_takes()
    isolated = {key: tuple(sample * blend_window(i / RATE, 0, LONG_PAUSE, .018)
                           for i, sample in enumerate(gap)) for key, gap in gaps.items()}
    placements = [(at, full[key]) for at, key in ROOM_REPLAYS]
    placements.extend((at, isolated[key]) for at, key in SOLO_REPLAYS)
    write_track(path, 24., placements)


def write_masking(path):
    mixes = masked_takes()[3]
    write_track(path, 24., ((at, mixes[key]) for at, key in MASK_REPLAYS))


def make_peaks(samples, count=100):
    peaks = []
    for i in range(count):
        values = samples[i * len(samples) // count:(i + 1) * len(samples) // count]
        peaks.append((min(values, default=0), max(values, default=0)))
    return tuple(peaks)


def waveform(draw, peaks, x, mid, width, scale=72, color=MINT):
    draw.line((x, mid, x + width, mid), fill='#59796b', width=1)
    for i, (low, high) in enumerate(peaks):
        here = x + i * width / (len(peaks) - 1)
        draw.line((here, mid - high * scale, here, mid - low * scale), fill=color, width=2)


def marker(draw, fraction, x, width, top, bottom, color=GOLD):
    here = round(x + width * max(0.0, min(1.0, fraction)))
    draw.line((here, top, here, bottom), fill=color, width=2)
    draw.polygon(((here - 5, top), (here + 5, top), (here, top + 7)), fill=color)


def active(t, events, duration):
    for start, key in events:
        if 0 <= t - start < duration:
            return key, (t - start) / duration
    return None, None


@lru_cache(maxsize=1)
def fill_peaks():
    bed = short_room_takes()[2]
    dry_bed = tuple(v * (1 - blend_window(i / RATE, VOICE_SPLIT, VOICE_SPLIT + SHORT_PAUSE, .012))
                    for i, v in enumerate(bed))
    return tuple(make_peaks(v) for v in (pause_voice(SHORT_PAUSE), dry_bed, bed))


def room_fill(t):
    frame = Image.new('RGB', VERTICAL, INK)
    photo = ImageEnhance.Brightness(shot('room', size=(360, 230))).enhance(.73)
    frame.paste(photo, (0, 0))
    draw = ImageDraw.Draw(frame)
    badge(draw, 19, 15, 'Staged audio demo')
    if t < .95:
        title, detail = 'Hear the room', 'disappear here.'
    elif t < 2.7:
        title, detail = 'Add matching', 'room tone.'
    else:
        title, detail = 'Same voice.', 'The room stays.'
    caption(draw, 21, 256, title, 39)
    caption(draw, 21, 297, detail, 39)

    x, width, length = 34, 291, VOICE_LENGTH + SHORT_PAUSE
    left, right = x + width * VOICE_SPLIT / length, x + width * (VOICE_SPLIT + SHORT_PAUSE) / length
    draw.rounded_rectangle((19, 334, 341, 547), 9, fill=PANEL)
    fill = t >= 2.70
    ready = t >= 1.68
    dialogue, room_before, room_after = fill_peaks()
    draw.rectangle((left, 368, right, 506), fill='#35594a' if ready else '#523635')
    caption(draw, x, 356, 'Dialogue', 17)
    waveform(draw, dialogue, x, 405, width, 60)
    caption(draw, x, 448, 'Room tone', 17)
    waveform(draw, room_after if ready else room_before, x, 484, width, 131,
             MINT if ready else CORAL)

    _, play = active(t, ((0.0, 'dry'), (2.70, 'fill'), (4.31, 'fill')), length)
    if play is not None:
        marker(draw, play, x, width, 371, 512)
    caption(draw, 180, 527, 'Tone holds through the gap' if fill else
            'Sample from the same bed' if ready else 'Missing tone at the splice',
            17, MINT if ready else CORAL, 'mm')
    caption(draw, 21, 572, 'Same speech level · no music', 17, MINT)
    return frame


@lru_cache(maxsize=1)
def foot_peaks():
    return make_peaks((0.0,) * ns(FOOT_AT) + footfall() + (0.0,) * ns(.18), 94)


def choice_contact(t):
    early = t < 1.0
    followup = t >= 2.55
    start = 0.0 if early else 1.0 if not followup else FOOT_REPLAYS[-1]
    frozen = t - start >= .69
    elapsed = FOOT_AT if frozen else max(0., t - start)
    splice = EARLY_CUT if early else FOOT_AT
    zoom = 1.29 if elapsed >= splice else 1.0
    source_time = SOURCE_CONTACT - FOOT_AT + elapsed
    frame = Image.new('RGB', VERTICAL, INK)
    frame.paste(shot('steps-live', source_time, zoom, -30, 20, (360, 404)), (0, 0))
    draw = ImageDraw.Draw(frame)
    badge(draw, 18, 15, 'Illustrated footstep')
    if frozen:
        badge(draw, 18, 354, 'Contact frame')

    if early:
        title, description = 'Cut before contact', 'A   ·   Picture leads the tap'
    elif followup:
        title, description = 'One visible contact', 'Use it to line up the cut'
    else:
        title, description = 'Cut on contact', 'B   ·   Picture and tap meet'
    caption(draw, 20, 426, title, 32)
    caption(draw, 21, 459, description, 22, MINT)

    x, width, view_length = 23, 314, .79
    draw.rounded_rectangle((18, 486, 341, 565), 6, fill=PANEL)
    waveform(draw, foot_peaks(), x, 531, width, 86)
    marker(draw, elapsed / view_length, x, width, 511, 554, PAPER)
    picture_x = x + width * splice / view_length
    draw.line((picture_x, 500, picture_x, 549), fill=GOLD, width=3)
    caption(draw, 24, 499, 'Gold line · picture cut', 14, GOLD)
    caption(draw, 19, 590, 'Identical tap and gain in both cuts', 18, MINT)
    return frame


@lru_cache(maxsize=1)
def comparison_peaks():
    return ({key: make_peaks(take, 69) for key, take in long_room_takes().items()},
            {key: make_peaks(take, 69) for key, take in gap_takes().items()})


def gap_comparison(t):
    photo = shot('room', size=WIDE)
    frame = ImageEnhance.Brightness(photo).enhance(.42)
    draw = ImageDraw.Draw(frame)
    draw.rectangle((0, 69, 640, 360), fill=INK)
    badge(draw, 20, 12, 'Staged listening test')
    solo, source_check = 6.1 <= t < 14.8, t >= 14.8
    title = 'Listen to both gaps on their own' if solo else 'Find the repeated section' if source_check else 'Which pause sounds like the real room?'
    caption(draw, 20, 99, title, 31)
    full, isolated = comparison_peaks()
    duration = LONG_PAUSE if solo else VOICE_LENGTH + LONG_PAUSE
    state, play = active(t, SOLO_REPLAYS if solo else ROOM_REPLAYS, duration)
    for key, name, x in (('loop', 'A   Looped room tone', 20), ('natural', 'B   Continuous room tone', 327)):
        on = key == state
        draw.rounded_rectangle((x, 132, x + 293, 300), 8, fill=PANEL,
                               outline=MINT if on else '#4b6759', width=2)
        caption(draw, x + 12, 156, name, 19)
        if solo:
            note = '0.55 s repeated × 3' if key == 'loop' else '1.65 s from one passage'
        elif source_check:
            note = 'Short handle copied twice' if key == 'loop' else 'One longer handle'
        else:
            note = 'Same speech and 1.65 s pause'
        caption(draw, x + 13, 186, note, 16, MINT)
        px, width = x + 13, 267
        start = 0 if solo else VOICE_SPLIT / duration
        finish = 1 if solo else (VOICE_SPLIT + LONG_PAUSE) / duration
        draw.rectangle((px + width * start, 214, px + width * finish, 269), fill='#35584a')
        waveform(draw, (isolated if solo else full)[key], px, 243, width, 126 if solo else 67)
        if source_check and key == 'loop':
            for index in (1, 2):
                x_edge = px + width * (VOICE_SPLIT + GAP_LOOP * index) / duration
                draw.line((x_edge, 208, x_edge, 277), fill=GOLD, width=2)
        if on:
            marker(draw, play, px, width, 207, 283)
        caption(draw, x + 13, 284, 'Playing' if on else 'Same source gain', 14, MINT)
    caption(draw, 21, 328, 'Inspect the available handles before looping.' if source_check else
            'Keep the level fixed. Listen for repeated texture.' if solo else 'Listen to the pauses at the same playback gain.', 22)
    return frame


@lru_cache(maxsize=1)
def mask_peaks():
    speech, cue, delayed, mixes = masked_takes()
    return tuple(make_peaks(take, 118) for take in (speech, cue, delayed)), {
        key: make_peaks(take, 118) for key, take in mixes.items()}


def masking_problem(t):
    frame = Image.new('RGB', WIDE, INK)
    draw = ImageDraw.Draw(frame)
    repair = t >= 18.45
    timeline = t >= 14.50
    isolated = 6.0 <= t < 14.5
    badge(draw, 19, 14, 'Staged mix')
    if not timeline:
        photo = ImageEnhance.Brightness(shot('editing-live', t % 3.0, 1.03, size=(197, 92))).enhance(.76)
        frame.paste(photo, (422, 12))
        caption(draw, 20, 67, 'Same line, effect muted' if isolated else 'The effect is covering', 30)
        if not isolated:
            caption(draw, 20, 99, 'the important word.', 30)
    else:
        caption(draw, 20, 74, 'Move the cue past the word' if repair else 'Locate the collision', 32)

    stems, mixes = mask_peaks()
    _, play = active(t, MASK_REPLAYS, 1.55)
    x, width = 153, 460
    word_left, word_right = x + width * WORD_BEGIN / 1.55, x + width * WORD_END / 1.55
    draw.rounded_rectangle((21, 126, 622, 302), 8, fill=PANEL)
    draw.rectangle((word_left, 130, word_right, 293), fill='#39584b' if repair or isolated else '#663e3a')
    caption(draw, 34, 165, 'Voice' if timeline else 'Playback', 20)
    caption(draw, 34, 246, 'Effect cue', 20)
    cue = stems[2] if repair else stems[1]
    playback = stems[0] if timeline else mixes['clear' if isolated else 'covered']
    waveform(draw, playback, x, 171, width, 63)
    if isolated:
        draw.line((x, 250, x + width, 250), fill=FADE, width=2)
    else:
        waveform(draw, cue, x, 250, width, 81, GOLD)

    caption(draw, x, 203, 'Keep the', 17, MINT)
    caption(draw, (word_left + word_right) / 2, 203, 'words' if isolated or timeline else 'masked',
            17, PAPER, 'mm')
    caption(draw, word_right + 16, 203, 'clear.', 17, MINT)
    if play is not None:
        marker(draw, play, x, width, 136, 281)
    note = ('Same cue, placed after the line' if repair else 'The cue peaks over “words”' if timeline else
            'Identical voice level · effect muted' if isolated else 'Listen for the covered word')
    caption(draw, 22, 328, note, 21)
    return frame


SCENES = {
    'hook-short-specific-fix-021': room_fill,
    'hook-short-choice-live-032': choice_contact,
    'hook-long-head-to-head-013': gap_comparison,
    'hook-long-visible-problem-031': masking_problem,
}

AUDIO = {
    'hook-short-specific-fix-021': write_room_fill,
    'hook-short-choice-live-032': write_footfall,
    'hook-long-head-to-head-013': write_room_comparison,
    'hook-long-visible-problem-031': write_masking,
}

POSTERS = {
    'hook-short-specific-fix-021': .45,
    'hook-short-choice-live-032': 1.40,
    'hook-long-head-to-head-013': .92,
    'hook-long-visible-problem-031': .72,
}
