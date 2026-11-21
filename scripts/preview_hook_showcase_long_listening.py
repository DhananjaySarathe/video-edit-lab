"""Widescreen listening comparisons from locally rendered practice audio."""
from array import array
from functools import lru_cache, partial
from math import sin, tau
from sys import byteorder
import wave

from preview_common import ease, progress
from preview_hook_showcase_editing import GOLD, INK, PAPER, chip, words
from preview_hook_showcase_long_motion import screen
from preview_plates import shot
from preview_sound import RATE, bed, impact, voice

PASS = 2.7


def source_sound(t, variant, alternative):
    """Return channels for the selected version of the same local practice take."""
    speech = .65 * voice()(.53 + t)
    music = .36 * bed(t, pace=.34) if t < 1.14 else 0.
    low = .21 * sin(tau * 43 * t)
    hum = .10 * sin(tau * 143 * t)
    if variant == 'rumble':
        comparison = speech + (low if alternative else 0.) + (0. if alternative else hum)
        return comparison, comparison
    if variant == 'tail':
        if alternative:
            for delay, gain in ((.06,.27),(.12,.23),(.24,.18),(.45,.09)):
                at = t - delay
                if 0 < at < 1.14:
                    music += gain * bed(at, pace=.34) * (1 - ease(progress(t, 1.18, 1.57)))
        comparison = speech + music
        return comparison, comparison
    if variant == 'impact':
        cue = 1.15 if alternative else .80
        sound = .43 * impact(t, cue, 16, 196) + .24 * impact(t, 1.15, 45, 361)
        return sound, sound
    if variant == 'mono':
        return (0., 0.) if alternative else (speech, -speech)
    raise ValueError(variant)


@lru_cache(maxsize=None)
def take(variant, alternative):
    data = []
    for i in range(round(PASS * RATE)):
        t = i / RATE
        envelope = min(1., t / .017, (PASS - t) / .04)
        l, r = source_sound(t, variant, alternative)
        data.append((l * envelope, r * envelope))
    return tuple(data)


AUDITIONS = (0.15, 3.18, 6.5, 9.57, 15.33, 19.29)


def state_at(t):
    for i, begin in reversed(tuple(enumerate(AUDITIONS))):
        if t >= begin:
            return i % 2, min(PASS, t - begin)
    return 0, 0.


def write_audio(path, variant):
    audio = array('h')
    takes = (take(variant, False), take(variant, True))
    for i in range(24 * RATE):
        mode, at = state_at(i / RATE)
        j = round(RATE * at)
        channels = takes[mode][j] if j < len(takes[mode]) else (0., 0.)
        audio.extend(round(32767 * min(.97, max(-.97, amplitude))) for amplitude in channels)
    if byteorder == 'big':
        audio.byteswap()
    with wave.open(str(path), 'wb') as stream:
        stream.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
        stream.writeframes(audio.tobytes())


@lru_cache(maxsize=None)
def envelopes(variant, mode):
    data = take(variant, mode)
    hop = len(data) // 230
    return [max(abs(l) for l, _ in data[i*hop:(i+1)*hop]) for i in range(230)]


def waveform(draw, variant, mode, accent, y, at):
    data = envelopes(variant, mode)
    draw.rounded_rectangle((147,y-20,616,y+20),6,fill='#365149')
    for j,gain in enumerate(data):
        x=152+2*j
        up=round(min(17,max(1,35*gain)))
        draw.line((x,y-up,x,y+up),fill=accent,width=1)
    if at is not None:
        x=151+round(460*at/PASS)
        draw.line((x,y-18,x,y+18),fill=GOLD,width=2)


def visual(t, variant, title, labels, note):
    use, stamp = state_at(t)
    frame, draw = screen(title, note if t >= 14.5 else 'Listen to both passes at the same playback volume.',
                         'Local practice audio / enable Sound')
    if variant == 'impact':
        local = stamp
        draw.rectangle((21,58,621,188),fill='#b28b60')
        draw.rectangle((21,133,621,185),fill='#906c4e')
        p = ease(progress(local, .18, 1.15))
        x, y = round(380 - 135 * p), round(68 + 42 * p)
        draw.rounded_rectangle((x+24,y-9,x+122,y+26),8,fill='#446258',outline=INK,width=2)
        draw.rounded_rectangle((x-19,y,x+64,y+27),12,fill='#ac795d',outline=INK,width=2)
        for j in range(3):
            draw.arc((x-15+6*j,y+4,x+1+6*j,y+25),180,290,fill='#634c37')
        if local>=1.15:
            draw.line((237,134,300,134),fill=GOLD,width=3)
        if t>=6.1:
            chip(draw,(31,68),'Contact at 1.15 s',INK,PAPER,15)
    else:
        frame.paste(shot('host-live', .22+stamp*.74, 1.05,-19,-17,(600,131)),(21,58))
        if variant == 'mono':
            chip(draw,(28,67),'L = +speech / R = −speech' if use==0 else 'Mono = (L + R) / 2',INK,PAPER,15)
        elif variant == 'rumble' and t >= 6.1:
            chip(draw,(28,67),'Original contaminants / 43 Hz and 143 Hz',INK,PAPER,14)
    for mode,y in enumerate((219,271)):
        label=labels[mode]
        playhead=stamp if use==mode else None
        words(draw,(20,y),label,16,PAPER)
        waveform(draw,variant,bool(mode),('#7ab7a1' if mode==0 else '#edb78d') if use==mode else '#829289',y,playhead)
    return frame


CASES = {
    'hook-long-head-to-head-012': ('rumble','Which cleanup keeps the voice clearer?',
                                  ('Low cut','Tone cut'), 'Low cut removes 43 Hz. Tone cut removes 143 Hz.'),
    'hook-long-head-to-head-014': ('tail','Stop the music or let the tail decay?',
                                  ('Hard stop','Short tail'), 'Same speech and stop. Only the short music tail differs.'),
    'hook-long-head-to-head-020': ('impact','Accent the cut or the contact?',
                                  ('At the cut','At contact'), 'Contact at 1.15 s. The early accent lands at 0.80 s.'),
    'hook-long-visible-problem-036': ('mono','The voice disappears in mono',
                                     ('Stereo','Mono sum'), 'Equal and opposite channels cancel in the mono sum.'),
}
SCENES = {
    key: partial(visual,variant=variant,title=title,labels=labels,note=note)
    for key,(variant,title,labels,note) in CASES.items()
}
AUDIO = {key:partial(write_audio,variant=variant) for key,(variant,*_) in CASES.items()}
POSTERS = {key:.95 for key in CASES}
