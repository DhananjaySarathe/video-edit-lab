"""Original audiovisual demos for the sound techniques."""
from array import array
from functools import lru_cache
import math
from pathlib import Path
import random
import sys
import wave
from PIL import ImageDraw
from preview_common import backdrop, ease, font, progress
from preview_plates import shot

RATE, LENGTH = 24000, 3.2
BEAT_CUES = (.5, 1., 1.5, 2., 2.5, 3.)
IMPACT_CUE = 1.4
LAND_CUE = 1.
MUSIC_CUT = 1.5
CHAPTER_CUT = 1.55
TAU = math.tau
INK, WHITE = '#243c36', '#f8f5e7'
GREEN, MINT, GOLD = '#4d725b', '#b4d3a5', '#e4ba76'

def dark():
    return backdrop((16, 35, 35), (30, 57, 51), True)

def ivory():
    return backdrop((248, 245, 231), (226, 236, 218))

def label(draw, x, y, value, color=WHITE, size=16, weight='bold', anchor='la'):
    draw.text((x, y), value, font=font(size, weight), fill=color, anchor=anchor)

def wave_track(draw, x0, x1, y, current, energy, foreground, background, height=34):
    for x in range(x0, x1, 5):
        t = LENGTH * (x - x0) / (x1 - x0)
        wobble = .27 + .73 * abs(math.sin(x * .973) * math.cos(x * .712))
        span = max(1, height * wobble * min(1, max(0, energy(t))))
        draw.line((x, y - span, x, y + span), fill=foreground if t <= current else background, width=2)

def playhead(draw, t, x0, x1, y0, y1, color=GOLD):
    x = x0 + (x1 - x0) * min(t / LENGTH, 1)
    draw.line((x, y0, x, y1), fill=color, width=2)
    draw.polygon([(x - 5, y0), (x + 5, y0), (x, y0 + 6)], fill=color)

def window(t, begin, end, softness=.12):
    return ease(progress(t, begin, begin + softness)) * (1 - ease(progress(t, end - softness, end)))

def impact(t, at, speed=9, hz=63):
    p = t - at
    return math.sin(TAU * (hz * p - 9 * p * p)) * math.exp(-p * speed) if 0 <= p < 1.1 else 0

def bed(t, shift=0, pace=.5):
    notes = (130.81, 164.81, 196, 261.63, 164.81, 196, 220, 261.63)
    beat = int(max(0, t) / pace)
    phase = max(0, t) % pace
    freq = notes[(beat + shift) % len(notes)]
    env = min(1, phase * 85) * math.exp(-phase * 4.5)
    return env * (.65 * math.sin(TAU * freq * phase) + .29 * math.sin(TAU * freq * 2 * phase))

def swell(t, start, length):
    p = (t - start) / length
    return math.sin(math.pi * p) ** 2 if 0 < p < 1 else 0

def duck_gain(t):
    return 1 - .83 * window(t, .68, 2.48, .26)

@lru_cache(maxsize=1)
def voice():
    with wave.open(str(Path(__file__).with_name('assets') / 'demo-voice.wav'), 'rb') as recording:
        source_rate = recording.getframerate()
        samples = array('h', recording.readframes(recording.getnframes()))
    if sys.byteorder == 'big':
        samples.byteswap()

    def sample(t):
        index = int((t - .84) * source_rate)
        return samples[index] / 32768 if .84 <= t and 0 <= index < len(samples) else 0

    return sample

def mix(id, t, noise):
    if id == 'beat-synced-cuts':
        return sum(.22 * impact(t, at) + .09 * impact(t, at, 32, 472) for at in BEAT_CUES) + .15 * bed(t)
    if id == 'layered-sound-design':
        rise = window(t, .15, IMPACT_CUE, .28) * progress(t, .15, IMPACT_CUE)
        return (.16*rise*noise + .38*impact(t, IMPACT_CUE) +
                .15*impact(t, IMPACT_CUE, 22, 720) + .09*impact(t, IMPACT_CUE+.06, 13, 187))
    if id == 'motion-synced-sound':
        return .27 * swell(t, .48, .52) * noise + .29 * impact(t, LAND_CUE, 24, 420)
    if id == 'place-ambience':
        traffic = .55 * swell(t, .12, 2.6) + .3 * swell(t, 1.14, 1.8)
        return (.053 + traffic * .04) * noise + (.044 + traffic * .095) * math.sin(TAU * (60 * t + 5 * math.sin(t * 2))) + .035 * math.sin(TAU * 119 * t)
    if id == 'music-reverb-tail':
        dry = .32 * bed(t, pace=.5) if t < MUSIC_CUT else 0
        tail = 0
        for delay, strength in ((.083,.21),(.129,.15),(.219,.09),(.337,.07),(.53,.04),(.81,.022)):
            note_time = t-delay
            if 0 <= note_time < MUSIC_CUT:
                tail += strength * bed(note_time, pace=.5)
        return dry+tail
    if id == 'chapter-music-change':
        cross = ease(progress(t, CHAPTER_CUT-.08, CHAPTER_CUT+.12))
        return (.26 * (1-cross)*bed(t, shift=2, pace=.52)
                + .29*cross*bed(max(0,t-CHAPTER_CUT), shift=5, pace=.31))
    return .25 * duck_gain(t) * bed(t, pace=.47) + .54 * voice()(t)

def waveform(id, path):
    rng = random.Random(37)
    low_noise = 0.0
    samples = array('h')
    for n in range(round(RATE * LENGTH)):
        t = n / RATE
        noise = rng.uniform(-1, 1)
        low_noise = .92 * low_noise + .08 * noise
        sample = mix(id, t, .5 * noise + low_noise)
        tail = 1 - ease(progress(t, LENGTH - .13, LENGTH))
        samples.append(round(32767 * max(-.97, min(.97, tail * sample))))
    if sys.byteorder == 'big':
        samples.byteswap()
    with wave.open(str(path), 'wb') as recording:
        recording.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        recording.writeframes(samples.tobytes())

def layered(t):
    im = dark()
    d = ImageDraw.Draw(im)
    if t < IMPACT_CUE:
        clip = shot('walk-live',t,1.1+.22*progress(t,.2,IMPACT_CUE),-26,25,(604,173))
        caption = 'Riser leads into the cut'
    else:
        clip = shot('steps-live',t-IMPACT_CUE+.28,1.04,0,18,(604,173))
        caption = 'Impact + detail as the foot lands'
    im.paste(clip,(18,16))
    d.rounded_rectangle((25,24,343,52),radius=5,fill='#24362d')
    label(d,37,38,caption,size=17,anchor='lm')
    rows = [
        ('Riser', 224, lambda a: window(a, .14, IMPACT_CUE) * progress(a, .14, IMPACT_CUE), '#98cbb4'),
        ('Low impact', 272, lambda a: math.exp(-6*(a-IMPACT_CUE)) if a >= IMPACT_CUE else 0, '#e5b575'),
        ('High detail', 320, lambda a: math.exp(-17*(a-IMPACT_CUE)) if a >= IMPACT_CUE else 0, '#d4e39f'),
    ]
    for name, y, env, color in rows:
        d.rounded_rectangle((18,y-20,622,y+20),radius=6,fill='#26483f',outline='#426052')
        label(d,30,y,name,'#e4ecdd',16,'bold','lm')
        wave_track(d,156,607,y,t,env,color,'#517564',height=17)
    playhead(d,t,156,607,197,341)
    return im


def synced(t):
    im = dark()
    d = ImageDraw.Draw(im, 'RGBA')
    d.rounded_rectangle((49, 40, 593, 258), radius=16, fill='#203f37', outline='#4b6e59')
    d.rounded_rectangle((68, 61, 570, 238), radius=10, fill='#345847')
    x = 100 + 311 * ease(progress(t, .51, LAND_CUE))
    if .51 < t < LAND_CUE:
        for i in range(4):
            d.line((x - 90 + i * 14, 145 + i * 11, x - 19 + i * 14, 145 + i * 11), fill=(204, 227, 185, 150), width=2)
    d.rounded_rectangle((x - 32, 105, x + 92, 188), radius=13, fill='#eef1d7')
    label(d, x + 30, 145, 'PING', INK, 23, 'bold', 'mm')
    if LAND_CUE <= t < 1.5:
        p = progress(t, LAND_CUE, 1.5)
        y = 146
        radius = 40 + 55 * p
        d.ellipse((x + 30 - radius, y - radius, x + 30 + radius, y + radius),
                  outline=(247, 207, 134, round(180 * (1 - p))), width=3)
    wave_track(d, 105, 594, 302, t,
               lambda a: swell(a, .48, .52)*.7 + (math.exp(-10*(a-LAND_CUE)) if a >= LAND_CUE else 0),
               MINT, '#466756', 24)
    label(d, 46, 302, 'SFX', '#d7e4d2', 15, 'bold', 'lm')
    playhead(d, t, 105, 594, 273, 329)
    return im

def ambience(t):
    detail = t >= 1.6
    im = shot('steps-live',t-1.16) if detail else shot('walk-live',t,1.08,0,10)
    d = ImageDraw.Draw(im)
    d.rectangle((0,279,640,360),fill='#19352d')
    label(d,21,305,'Street ambience','#e3ebd8',18,'bold','lm')
    label(d,21,331,'Continuous bed','#c4d8bf',14,'regular','lm')
    wave_track(d,191,613,320,t,lambda a: .37+swell(a,.14,2.82),MINT,'#4d6b54',20)
    at = 402
    d.line((at,293,at,343),fill='#88a58c',width=1)
    playhead(d,t,191,613,291,347)
    return im


def ending(t):
    im = shot('coffee-live',t,1.14,-25,15) if t < MUSIC_CUT else shot('room',t,1.08)
    d = ImageDraw.Draw(im)
    d.rectangle((0,245,640,360),fill='#223a33')
    label(d,21,264,'Music stops at the cut' if t < MUSIC_CUT else 'Reverb trails into the next shot',
          size=21,anchor='lm')
    x0,x1 = 23,617
    boundary = x0+(x1-x0)*MUSIC_CUT/LENGTH
    d.line((boundary,278,boundary,350),fill='#91a58e',width=2)
    wave_track(d,x0,x1,317,t,lambda a: .83 if a < MUSIC_CUT else .59*math.exp(-4.6*(a-MUSIC_CUT)),
               MINT,'#698675',27)
    playhead(d,t,x0,x1,280,351)
    return im


def chapter(t):
    first = t < CHAPTER_CUT
    im = shot('host-live',t,1.12,0,-9) if first else shot('coffee-live',t-.35,1.08,-23,11)
    d = ImageDraw.Draw(im)
    d.rectangle((0,242,640,360),fill='#243f32')
    label(d,21,267,'Setup · cue A' if first else 'Result · cue B',size=24,anchor='lm')
    wave_track(d,23,618,317,t,lambda a: .22+.76*abs(bed(a,shift=2 if a < CHAPTER_CUT else 5)),
               MINT if first else GOLD,'#647866',26)
    x = 23+595*CHAPTER_CUT/LENGTH
    d.line((x,286,x,345),fill='#96a89a',width=1)
    playhead(d,t,23,618,285,351)
    return im


def ducked(t):
    im = ivory()
    d = ImageDraw.Draw(im)
    label(d, 40, 38, 'Voice stays clear', INK, 32, 'serif')
    label(d, 40, 80, 'Music dips when speech begins', INK, 17, 'regular')
    x0, x1 = 180, 583
    d.rounded_rectangle((40, 125, 600, 211), radius=9, fill='#e0eadb', outline='#b3c3ad')
    d.rounded_rectangle((40, 218, 600, 304), radius=9, fill='#e8e2cb', outline='#c9c3aa')
    label(d, 58, 166, 'Dialogue', INK, 17, 'bold', 'lm')
    label(d, 58, 259, 'Music bed', INK, 17, 'bold', 'lm')
    wave_track(d, x0, x1, 167, t, lambda a: window(a, .83, 2.35), '#4e7656', '#a3b6a0', 31)
    wave_track(d, x0, x1, 260, t, duck_gain, '#9a6a3a', '#b9aa80', 27)
    playhead(d, t, x0, x1, 114, 313, GREEN)
    return im

SCENES = {
    'layered-sound-design': layered,
    'motion-synced-sound': synced,
    'place-ambience': ambience,
    'music-reverb-tail': ending,
    'chapter-music-change': chapter,
    'ducked-music': ducked,
}

def sound_for(id):
    return lambda path: waveform(id, path)

AUDIO = {id: sound_for(id) for id in (*SCENES, 'beat-synced-cuts')}
