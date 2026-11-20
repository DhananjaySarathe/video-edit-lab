"""Original short-form and long-form examples using the project's licensed footage."""
from array import array
from bisect import bisect_right
from functools import partial
import wave

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from preview_common import H, W, font, progress
from preview_cuts import clip_track, crop
from preview_live_action import GOLD, INK, PAPER, tag, type_at
from preview_phone import device
from preview_plates import shot
from preview_sound import LENGTH, RATE, bed, impact, voice
from preview_spatial import title_card

DARK = '#1a2823'
HYPER_CUTS = (.35, .65, .9, 1.15, 1.45, 1.8, 2.18)
BRIDGE_CUTS = (.91, 1.54)
BRIDGE_SPEECH = (.40, 1.69)


def caption(image, phrase, x, y, accent=False):
    draw = ImageDraw.Draw(image)
    width = draw.textlength(phrase, font=font(24))
    draw.rounded_rectangle((x-width/2-13,y-21,x+width/2+13,y+21),7,fill=GOLD if accent else '#1b2720')
    type_at(image,(x,y),phrase,24,INK if accent else PAPER)


def actor(stamp, flip=False):
    area = (83, 4, 438, H)
    image = shot('host-live',stamp).crop(area)
    matte = shot('host-live-matte',stamp).crop(area)
    if flip:
        image, matte = ImageOps.mirror(image), ImageOps.mirror(matte)
        red, green, _ = image.split()
        cyan = ImageChops.subtract(green,red).point(lambda v: min(255, int(v*1.61)))
        dark = ImageOps.colorize(image.convert('L'), '#1c1733', '#ead2ff')
        image.paste(dark,(0,0),ImageChops.multiply(cyan,matte))
    return image, matte


def clone_split(t):
    plate = ImageEnhance.Brightness(shot('room',t,1.04)).enhance(.79)
    shadow = Image.new('L',(W,H))
    marks = ImageDraw.Draw(shadow)
    for x in (198,451):
        marks.ellipse((x-104,300,x+119,367),fill=108)
    plate.paste('#171b18',(0,0,W,H),shadow.filter(ImageFilter.GaussianBlur(18)))
    for right, x, stamp in ((False,24,t*.75), (True,318, .52+t*.8)):
        crop_shot, mask = actor(stamp,right)
        crop_shot = crop_shot.resize((301,302),Image.Resampling.LANCZOS)
        mask = mask.resize(crop_shot.size,Image.Resampling.LANCZOS)
        plate.paste(crop_shot,(x,59),mask)
    tag(plate,'Creator',19,15)
    tag(plate,'Editor',W-76,15,t >= 1.31)
    if t >= .22:
        caption(plate,'We need more edits.' if t < 1.31 else 'We need one good edit.',
                189 if t < 1.31 else 451, 305, t >= 1.31)
    return plate


def role_reverse(t):
    role = 0 if t < 1.02 or 1.92 <= t < 2.32 else 1
    raw = shot('host-live', t*.67 + .21*role, 1.27, -29, -29)
    image = ImageOps.mirror(raw) if role else raw
    if role:
        image = Image.blend(image,ImageOps.colorize(raw.convert('L'),'#141d20','#f7debf').transpose(Image.Transpose.FLIP_LEFT_RIGHT),.18)
    tag(image, 'Editor' if role else 'Creator',18,18,bool(role))
    if t < 1.02:
        caption(image,'Can this be faster?',320,276)
    elif t < 1.92:
        caption(image,'Which part?',320,276,True)
    elif t >= 2.32:
        caption(image,'Let the result land.',320,276,True)
    clip_track(image,t,(1.02,1.92,2.32))
    return image


def hyperedit(t):
    index = bisect_right(HYPER_CUTS,t)
    starts = (0,*HYPER_CUTS)
    phase = t-starts[index]
    clips = (
        ('coffee-live',2.85,1.69,-35,16),
        ('steps-live',1.22,1.26,0,16),
        ('coffee-live',.15,1.02,0,0),
        ('coffee-live',.65,1.78,-23,-9),
        ('coffee-live',1.11,2.03,-53,28),
        ('coffee-live',1.70,1.12,-21,13),
        ('coffee-live',2.21,1.51,-48,19),
        ('coffee-live',2.75,1.16,-18,16),
    )
    name, stamp, zoom, x, y = clips[index]
    frame = shot(name,stamp+phase*(1.4 if index < 7 else .68),zoom,x,y)
    if index in (1,3,6) and phase < .12:
        frame = frame.filter(ImageFilter.GaussianBlur(5*(1-progress(phase,0,.12))))
    if index in (0,4,7):
        words = 'THE RESULT' if index == 0 else 'CONTROL THE POUR' if index == 4 else 'HOLD THE PAYOFF'
        caption(frame, words,320,275,index == 7)
    clip_track(frame,t,HYPER_CUTS,pulses=True)
    return frame


def match_loop(t):
    if t < .82:
        return shot('coffee-live',.74+t,1.25,-29,15)
    if t >= 2.46:
        return shot('coffee-live', t-2.46,1.25,-29,15)
    image = shot('coffee-live', 2.34+.66*(t-.82),1.39,-38,20)
    caption(image,'One clean pour',320,291,True)
    return image


def proof_burst(t):
    if t < .49:
        image = shot('coffee-live', 2.9+t*.3, 1.52, -36, 19)
        tag(image, 'Finished result', accent=True)
    elif t < 1.04:
        image = shot('coffee-live', .27+t*.65, 1.16, -24, 12)
        tag(image, '1  Watch the surface')
    elif t < 1.52:
        image = shot('coffee-live', 1.4+(t-1.04), 1.81, -35, 22)
        tag(image, '2  See the pattern form')
    else:
        image = shot('coffee-live', 2.57+.65*(t-1.52), 1.27,-30,15)
        tag(image, 'Proof: the final pattern', accent=True)
    return image


def locked_roles(t):
    cut = bisect_right((.94, 1.98), t)
    source_time = (t*.8, 1.5+(t-.94)*.67, .76+(t-1.98)*.69)[cut]
    frame = shot('host-live',source_time,1.07,-26,-12)
    if cut:
        color = ImageOps.colorize(frame.convert('L'),'#182733' if cut == 1 else '#292221',
                                  '#f1eaff' if cut == 1 else '#ffe1ae')
        frame = Image.blend(frame,color,.25)
    tag(frame, ('THE OPTIMIST','THE SKEPTIC','THE EDITOR')[cut], 20, 18, cut==2)
    caption(frame, ('“Easy.”','“Show me.”','“Watch this.”')[cut],320,272,cut==2)
    clip_track(frame,t,(.94,1.98),pulses=True)
    return frame


def screen_world(t):
    inset = shot('coffee-live',t*.88,size=(170,314))
    image, corners = device(t,inset.convert('RGBA'))
    center = tuple(sum(point[i] for point in corners)/4 for i in range(2))
    p = progress(t,.53,1.36)
    if t < 1.36:
        image = crop(image,1+3.4*p*p,*center)
        if t < .59:
            tag(image,'Start inside the screen',18,18)
        return image
    image = shot('coffee-live',t*.88,1+.62*(1-progress(t,1.36,2.2)), -18, 14)
    tag(image,'Continue the same action',18,18,True)
    return image


def cold_open(t):
    if t < .97:
        image = shot('coffee-live', 2.51+.86*t, 1.68,-45,24)
        tag(image,'Cold open · the result')
        return image
    if t < 1.64:
        image = ImageEnhance.Brightness(shot('coffee-live', 2.81, 1.57,-36,16)).enhance(.41)
        type_at(image,(320,174),'Why does it hold?',52)
        return image
    image = shot('coffee-live', (t-1.64)*.62, 1.03,-2,0)
    tag(image,'Earlier · the first pour')
    return image


def audio_bridge(t):
    index = bisect_right(BRIDGE_CUTS,t)
    name = ('room','host-live','coffee-live')[index]
    image = shot(name,t,1 if index == 0 else 1.12,0,-15)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,273,640,360),fill=DARK)
    play = 154+450*t/3.2
    for y,c,label in ((294,'#b8cdad','Picture'),(331,GOLD,'Dialogue')):
        type_at(image,(18,y),label,16,PAPER,'lm')
        draw.rounded_rectangle((154,y-5,604,y+5),3,fill='#435447')
        if y == 294:
            draw.rounded_rectangle((154,y-5,604,y+5),3,fill=c)
        else:
            start, end = [154+450*point/LENGTH for point in BRIDGE_SPEECH]
            draw.rounded_rectangle((start,y-5,end,y+5),3,fill=c)
    for cut in BRIDGE_CUTS:
        cue = 154+450*cut/3.2
        draw.line((cue,282,cue,307),fill=DARK,width=3)
    draw.line((play,279,play,347),fill=PAPER,width=2)
    tag(image, ('Dialogue starts early', 'Cut to the speaker', 'Dialogue carries over')[index],16,16,index != 1)
    return image


def chapter_turn(t):
    if t < .75:
        image = shot('host-live',t,1.19,-28,-28)
        caption(image,'First, control the angle.',320,296)
        return image
    if t < 1.82:
        return title_card('CHAPTER 2','Control the pour')
    image = shot('coffee-live',(t-1.82)*.89)
    caption(image,'Now watch the surface.',320,296,True)
    return image


def payoff_back(t):
    image = Image.new('RGB',(W,H),DARK)
    if t < .86:
        image = shot('host-live',t,1.14,-35,-17)
        caption(image,'Can the pattern hold?',320,296)
    elif t < 2.15:
        image = shot('coffee-live',2.53+(t-.86)*.54,1.32,-37,16)
        tag(image,'Return to the opening image',accent=True)
    else:
        left = shot('coffee-live',.29,1.1,0,16,(303,277))
        right = shot('coffee-live',t+ .21,1.07,-16,21,(303,277))
        image.paste(left,(12,61))
        image.paste(right,(325,61))
        tag(image,'Before the pour',12,20)
        tag(image,'The finished result',325,20,True)
    return image


def soundtrack(name, path):
    src = voice()
    samples = array('h')
    for i in range(round(RATE*LENGTH)):
        t = i/RATE
        if name == 'bridge':
            # Reuse the local narration. Its original start is at .84 seconds.
            sample = .035*bed(t,pace=.56)+.63*src(t+.44)
        else:
            sample = .095*bed(t,pace=.30)
            sample += sum(.25*impact(t,cue,11,67)+.082*impact(t,cue,31,396) for cue in HYPER_CUTS)
        samples.append(round(32767*min(.95,max(-.95,sample))))
    with wave.open(str(path),'wb') as output:
        output.setparams((1,2,RATE,0,'NONE','not compressed'))
        output.writeframes(samples.tobytes())


SCENES = {
    'short-clone-split': clone_split,
    'short-role-reverse': role_reverse,
    'short-hyperedit': hyperedit,
    'short-match-loop': match_loop,
    'short-proof-burst': proof_burst,
    'short-locked-roles': locked_roles,
    'short-screen-world': screen_world,
    'long-cold-open': cold_open,
    'long-audio-bridge': audio_bridge,
    'long-chapter-turn': chapter_turn,
    'long-payoff-back': payoff_back,
}
AUDIO = {
    'short-hyperedit': partial(soundtrack,'hyper'),
    'long-audio-bridge': partial(soundtrack,'bridge'),
}
