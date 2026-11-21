"""Audible before/after cuts with waveforms drawn from the sound actually played."""
from array import array
from functools import lru_cache, partial
from math import exp, sin, tau
from random import Random
from sys import byteorder
import wave

from PIL import ImageDraw

from preview_common import ease, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, PORTRAIT, chip, words
from preview_hook_showcase_short_optics import GREEN, RED, RULE, stage
from preview_plates import shot
from preview_sound import RATE, bed, impact, voice


@lru_cache(maxsize=1)
def texture():
    rng=Random(321)
    values=[]
    previous=0
    for _ in range(2*RATE):
        noise=rng.uniform(-1,1)
        previous=.91*previous+.09*noise
        values.append((noise,previous))
    return values


def mix(t,kind,fixed):
    i=min(len(texture())-1,max(0,int(t*RATE)))
    grain, low = texture()[i]
    speech=.7*voice()(t+.76)
    room=.018*grain+.025*low
    if kind=='gate':
        factor=1 if fixed else 1-progress(t,.77,.81)
        return speech*factor+room
    if kind=='music':
        gain=1-.86*ease(progress(t,.04,.18)) if fixed else 1
        return speech+.5*gain*bed(t,pace=.35)+room
    if kind=='hum':
        return room+.095*sin(tau*120*t)+(.008 if fixed else .40)*sin(tau*60*t)
    if kind=='paper':
        event=t-.42
        if 0<=event<.39:
            if fixed:
                return room+.52*(.6*grain+.4*low)*exp(-5*event)*sin(event*64)**4
            return room+.50*impact(t,.42,34,780)
        return room
    if kind=='accent':
        expressive=.69
        return room+.48*impact(t,expressive+(.08 if fixed else -.38),16,252)
    if kind=='slate':
        onset=.62 if fixed else .38
        return room+(.55*grain*exp(-29*(t-onset)) if onset<=t<onset+.22 else 0)
    if kind=='two-mics':
        amplitude=(.61 if fixed else .22) if t<.84 else .67
        take=t if t<.84 else t-.84
        return amplitude*voice()(.80+take)+room
    if kind=='breath':
        inhaling = max(0,1-abs(t-.18)/.13)
        speech=.71*voice()(t+(.80 if not fixed else .57))
        return speech+room+(inhaling*.24*low if fixed else 0)
    raise ValueError(kind)


@lru_cache(maxsize=32)
def track(kind,fixed):
    return tuple(mix(i/RATE,kind,fixed) for i in range(round(1.65*RATE)))


def placement(t,middle):
    if t < middle[0]:
        return False,t
    if t < middle[1]:
        return None,t-middle[0]
    return True,(t-middle[1])%1.8


def make_waveform(path,kind,middle,duration):
    out=array('h')
    max_index=round(1.65*RATE)
    for frame in range(round(duration*RATE)):
        t=frame/RATE
        fixed, source=placement(t,middle)
        idx=round(source*RATE)
        envelope=min(1,source/.013,max(0,(1.65-source)/.03),max(0,(duration-t)/.08))
        sample=track(kind,fixed)[idx]*envelope if fixed is not None and idx<max_index else 0
        out.append(round(max(-.97,min(.97,sample))*32767))
    if byteorder=='big':
        out.byteswap()
    with wave.open(str(path),'wb') as stream:
        stream.setparams((1,2,RATE,0,'NONE','not compressed'))
        stream.writeframes(out.tobytes())


@lru_cache(maxsize=36)
def peaks(kind, fixed):
    array=track(kind,fixed)
    width=134
    stride=len(array)//width
    return tuple(max(abs(x) for x in array[i*stride:(i+1)*stride]) for i in range(width))


def make_frame(t,kind,middle,heading,cut,clean):
    frame,d=stage(heading)
    fixed, at=placement(t,middle)
    q=min(at,1.65)
    if kind=='paper':
        d.rectangle((17,164,342,365),fill='#8c6c4d')
        tilt=ease(progress(q,.25,.65))
        d.polygon(((38,224),(214,204),(305,253+50*tilt),(131,316)),fill='#f5e8cd',outline=INK,width=3)
        d.polygon(((214,204),(305,253+50*tilt),(218,306),(131,316)), fill='#e1cfab',outline=RULE,width=2)
        if q>.42:
            d.line((214,204,131,316),fill=RED,width=2)
    elif kind=='slate':
        d.rectangle((19,167,341,354),fill='#e2e4d0')
        d.rounded_rectangle((62,239,298,328),8,fill=INK)
        words(d,(180,277),'PRACTICE TAKE',21,PAPER,'mm')
        y=round(172+69*ease(progress(q,.18,.62)))
        d.polygon(((60,225),(280,y),(298,y+24),(62,248)),fill=GREEN,outline=INK,width=2)
        if q>=.62:
            d.line((66,239,290,239),fill=GOLD,width=4)
    else:
        source = 'portrait-live' if kind=='accent' else 'host-live'
        stamp=.25+q if kind!='accent' else min(2.15,.36+q*1.1)
        frame.paste(shot(source,stamp,1.08,-28,-145 if kind=='accent' else -5,(324,188)),(18,164))
        chip(d,(23,170),'Demo picture / practice audio',INK,PAPER,13)
    if fixed is None:
        rows=(False,True)
    else:
        rows=(fixed,)
    for i,state in enumerate(rows):
        y=412+i*76
        d.rounded_rectangle((22,y-31,336,y+30),6,fill='#e2eadc',outline=RULE,width=1)
        words(d,(34,y-13),clean if state else cut,14,GREEN if state else RED)
        data=peaks(kind,state)
        for j,value in enumerate(data):
            span=max(1,min(15,round(value*23)))
            d.line((35+j*2,y+10-span,35+j*2,y+10+span),fill=GREEN if state else RED)
        if fixed is not None:
            x=35+round(267*q/1.65)
            d.line((x,y-1,x,y+26),fill=INK,width=2)
    if kind=='hum' and fixed:
        words(d,(22,534),'60 Hz attenuated / 120 Hz remains',16,INK)
    else:
        chip(d,(21,529),'Same source / turn Sound on',INK,MINT,15)
    return frame


CASES={
    'hook-short-specific-fix-001':('breath',(.95,2.7),6.,('The cut stole', 'the inhale.'),'Hard cut to the word','Inhale preserved'),
    'hook-short-specific-fix-022':('gate',(.95,2.7),6.,('Can you hear', 'the ending?'),'Gate closes early','Longer release'),
    'hook-short-specific-fix-023':('music',(.95,2.7),6.,('The beat covers', 'the sentence.'),'Music at full level','Lower music under words'),
    'hook-short-specific-fix-024':('hum',(.95,2.7),6.,('Remove one', 'low hum.'),'Original 60 Hz hum','Reduce just 60 Hz'),
    'hook-short-specific-fix-025':('paper',(.95,2.7),6.,('That click is', 'the wrong sound.'),'Hard click','Soft paper fold'),
    'hook-short-specific-fix-026':('accent',(.95,2.7),6.,('The sting gives', 'the moment away.'),'Sting before reaction','Sting after reaction'),
    'hook-short-specific-fix-027':('two-mics',(.95,2.7),6.,('Why does the', 'second mic jump?'),'First mic quieter','Playback levels aligned'),
    'hook-short-specific-fix-029':('slate',(.95,2.7),6.,('The clap lands', 'too early.'),'Slate clap early','Clap at visual contact'),
}
SCENES={}
AUDIO={}
for key,(kind,middle,duration,heading,cut,clean) in CASES.items():
    SCENES[key]=partial(make_frame,kind=kind,middle=middle,heading=heading,cut=cut,clean=clean)
    AUDIO[key]=partial(make_waveform,kind=kind,middle=middle,duration=duration)
POSTERS={key:.69 for key in CASES}
