"""Edit demonstrations that keep a specific moving source, edge or mask in view."""
from PIL import ImageDraw, ImageEnhance

from preview_common import ease, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, PORTRAIT, chip, words
from preview_hook_showcase_short_evidence import BLUE, GREEN, ORANGE, RED, RULE, card, conclusion, stage
from preview_plates import shot


def keyboard(t):
    frame,d=stage(('Watch the focus', 'move by keyboard.'))
    card(d,(20,167,339,476))
    words(d,(36,199),'Export panel',23,INK)
    at = (0 if .85<=t<2.15 else min(2,int(t/.27)) if t<.85
          else min(2,int((t-2.15)/.77)))
    for i,name in enumerate(('Save draft','Choose folder','Export copy')):
        y=236+i*66
        d.rounded_rectangle((33,y,322,y+49),5,fill='#e1e9da')
        words(d,(55,y+24),name,21,INK)
        if i==at:
            d.rounded_rectangle((30,y-3,325,y+52),7,outline='#bac7b8' if .85<=t<2.15 else BLUE,width=1 if .85<=t<2.15 else 4)
    conclusion(d,'Tab → Tab → Tab' if t>=2.15 else 'One stop / weak focus' if t>=.85 else 'Final edit / visible focus')
    return frame


def sparkline(t):
    frame,d=stage(('This number', 'has a history.'))
    card(d,(22,173,338,478))
    data=(12,18,14,27,31)
    for i,(v,name) in enumerate(zip(data,('Mon','Tue','Wed','Thu','Fri'))):
        y=198+i*42
        if i==4:
            d.rectangle((28,y-15,327,y+19),fill='#e0ebd5')
        words(d,(43,y),name,17,INK)
        words(d,(136,y),str(v),17,INK,'rm')
    if t < .85 or t >= 2.15:
        p=1 if t < .85 else progress(t,2.15,3.45)
        coords=[(186+i*32,406-3.2*v) for i,v in enumerate(data)]
        d.line((176,409,322,409),fill=RULE)
        end=min(4,int(p*5))
        if end>=1:
            d.line(coords[:end+1],fill=BLUE,width=3)
        for i,(x,y) in enumerate(coords[:end+1]):
            d.ellipse((x-4,y-4,x+4,y+4),fill=ORANGE if i==4 else GREEN)
    conclusion(d,'Original example / check-ins per day')
    return frame


def drag_valid(t):
    frame,d=stage(('Where can', 'this tile land?'))
    card(d,(24,165,335,470))
    y=318
    bad=t>=3.55
    if t<.85:
        p=progress(t,0,.50)
    elif t<2.15:
        p=.86
    else:
        p=progress(t,3.55 if bad else 2.15,4.15 if bad else 2.92)
    allowed=not bad
    x=round(61+190*p) if allowed else round(61+127*p)
    if p>=1 and not allowed:
        x=61
    for i,u in enumerate((174,251)):
        ok=i==1 and p>=.7 and allowed
        bad_hover=i==0 and bad and p>=.7
        fill='#e0ecd9' if ok else '#ecd8cb' if bad_hover else '#e3e8db'
        d.rounded_rectangle((u-35,y-32,u+35,y+32),6,fill=fill,outline=GREEN if ok else RED if bad_hover else RULE,width=3 if ok or bad_hover else 1)
        words(d,(u,y+58),('Locked','Open')[i],16,INK,'mm')
    d.rounded_rectangle((x-24,y-25,x+24,y+25),5,fill=ORANGE,outline=INK,width=2)
    words(d,(x,y),'A',22,PAPER,'mm')
    conclusion(d,'Locked slot returns tile' if bad else 'Allowed slot highlights before release')
    return frame


def crop_action(t):
    stamp=.38+t*.34 if t<2.45 else .51+(t-2.45)*.54
    frame,d=stage(('Where did the', 'foot action go?'))
    actor='portrait-live' if .9<=t<2.45 else 'host-live'
    if .9<=t<2.45:
        frame.paste(shot(actor,stamp,1.05,-2,-145,(313,146)),(23,167))
        chip(d,(27,173),'Camera / keep the first step',INK,PAPER,15)
        frame.paste(shot('steps-live',.76,1.04,0,0,(313,139)),(23,332))
        d.line((77,428,293,428),fill=GOLD,width=2)
    else:
        frame.paste(shot('steps-live',stamp,1.08 if t>=2.45 else 1.72,-30,7 if t>=2.45 else -82,(313,300)),(23,168))
        chip(d,(30,176),'Action crop' if t>=2.45 else 'Editor / crop test',INK,PAPER,15)
    conclusion(d,'Rehearsed exchange / same source step')
    return frame


def same_proof(t):
    frame,d=stage(('Where is the', 'original shot?'))
    source = shot('host-live',.48+t*.29,1.08,-34,0,(305,158))
    grade=ImageEnhance.Color(ImageEnhance.Brightness(source).enhance(.76)).enhance(1.33)
    if t<.9:
        frame.paste(grade,(27,180))
        chip(d,(36,187),'Presenter / final grade',INK,PAPER,16)
    elif t<2.45:
        frame.paste(shot('portrait-live',.85+t*.18,1.11,-20,-145,(305,158)),(27,174))
        chip(d,(36,181),'Producer / source frame?',INK,PAPER,16)
        frame.paste(source,(27,346))
    else:
        for i,tile in enumerate((grade,source)):
            y=150+166*i
            frame.paste(tile,(27,y))
            chip(d,(33,y+6),'Grade' if i==0 else 'Original',INK,PAPER,14)
    conclusion(d,'Rehearsed exchange / same time and crop')
    return frame


def grade_split(t):
    stamp = .48 if t < 2.15 else .48 + min(1.5, (t - 2.15) * .7)
    original=shot('host-live',stamp,1.18,-63,-38,PORTRAIT)
    selective=original.point(lambda p: round(255*(p/255)**.91))
    selective=ImageEnhance.Color(selective).enhance(1.17)
    if t<.85:
        frame=selective.copy()
        chip(ImageDraw.Draw(frame),(23,501),'Finished shadow lift',INK,PAPER,16)
    elif t < 2.15:
        frame=original.copy()
        draw=ImageDraw.Draw(frame)
        chip(draw,(23,501),'Same frame / original',INK,PAPER,16)
        for x,y in ((108,205),(146,238)):
            draw.rectangle((x-6,y-6,x+6,y+6),outline=GOLD,width=2)
    else:
        split=round(360*ease(progress(t,2.16,3.9)))
        frame=original.copy()
        frame.paste(selective.crop((0,0,split,640)),(0,0))
        draw=ImageDraw.Draw(frame)
        draw.line((split,140,split,475),fill=GOLD,width=2)
        chip(draw,(23,501),'Curve comparison / identical source',INK,MINT,15)
    return frame


def trace_handwriting(t):
    frame,d=stage(('A note redraws', 'in its own hand.'))
    card(d,(21,174,339,475))
    stroke=[(54,350),(55,275),(59,258),(82,252),(96,262),(87,280),(55,287),(81,288),
            (108,330),(126,322),(135,301),(129,286),(117,298),(117,319),(128,328),(151,308),
            (164,296),(175,304),(173,329),(192,323),(211,302),(222,300),(232,307),(225,318),
            (208,322),(217,336),(239,334),(274,309)]
    p=1 if .85<=t<2.15 else progress(t,0,.72) if t<.85 else progress(t,2.15,4.31)
    end=max(2,int((len(stroke)-1)*p)+1)
    d.line(stroke[:end],fill=INK,width=5,joint='curve')
    if .85<=t<2.15:
        x,y=stroke[0]
        d.ellipse((x-6,y-6,x+6,y+6),fill=ORANGE)
        d.line((x,y,x+54,y+46),fill=ORANGE,width=2)
        words(d,(110,y+46),'Stroke start',17,INK)
    elif p<1:
        x,y=stroke[end-1]
        d.ellipse((x-6,y-6,x+6,y+6),fill=ORANGE)
    conclusion(d,'Original lettering / reveal the actual stroke')
    return frame


def role_timeline(t):
    frame,d=stage(('Which shot', 'actually comes first?'))
    if t<2.45:
        source = 'host-live' if t < .9 else 'portrait-live'
        top = -45 if t < .9 else -145
        frame.paste(shot(source,.5+t*.38,1.15,-30,top,(315,152)),(22,162))
        chip(d,(29,170),'Student / outcome first' if t<.9 else 'Peer / put the cause back',INK,PAPER,14)
    stamps=(1.92,.6,1.2) if t<.9 else (.6,1.2,1.92)
    if t>=2.45:
        at=stamps[min(2,int(progress(t,2.45,4.5)*3))]
        frame.paste(shot('coffee-live',at,1.0,0,2,(315,152)),(22,162))
    for i,stamp in enumerate(stamps):
        x=23+i*106
        frame.paste(shot('coffee-live',stamp,1.03,0,4,(104,95)),(x,347))
        name={.6:'First pour',1.2:'Stream',1.92:'Settled'}[stamp]
        words(d,(x+1,460),name,15,INK)
    conclusion(d,'Rehearsed example / same pour')
    return frame


SCENES={}
for family, entries in (
    ('proof-first',{16:grade_split,22:keyboard,26:sparkline,28:drag_valid,70:trace_handwriting}),
    ('character-collision',{4:crop_action,7:same_proof,71:role_timeline}),
):
    SCENES.update({f'hook-short-{family}-{n:03}':scene for n,scene in entries.items()})
POSTERS={key:.54 for key in SCENES}
