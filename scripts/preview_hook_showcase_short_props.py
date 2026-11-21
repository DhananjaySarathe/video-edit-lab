"""Animated paper, hardware, and tabletop models with action on the stated frame."""
from math import cos, radians, sin, tau
from random import Random

from PIL import Image, ImageDraw

from preview_common import ease, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, PORTRAIT, chip, words
from preview_hook_showcase_short_evidence import small, conclusion
from preview_hook_showcase_short_optics import GREEN, RED, RULE, stage

WOOD = '#d9b592'
ORANGE = '#d68058'
BLUE = '#386785'


def mark(draw, x, y, name, tip):
    draw.line(((x,y),tip), fill=RED, width=2)
    r=8
    draw.ellipse((tip[0]-r,tip[1]-r,tip[0]+r,tip[1]+r),outline=RED,width=2)
    chip(draw,(x,y),name,INK,PAPER,14)


def gradient_sleeve(t):
    frame,d=stage(('Does the roll', 'fit its sleeve?'))
    d.rounded_rectangle((117,264,301,415),12,fill=BLUE,outline=INK,width=3)
    d.ellipse((97,265,140,414),fill='#233f56',outline=INK,width=2)
    d.line((143,262,309,262),fill=GOLD,width=2)
    p=ease(progress(t,.8,2.66))
    x=round(19+143*p)
    roll=Image.new('RGBA',(340,175))
    r=ImageDraw.Draw(roll)
    r.rounded_rectangle((x,42,x+110,136),11,fill='#a6b98b',outline=INK,width=2)
    r.ellipse((x-2,42,x+26,136),fill='#cbd8ac',outline=INK,width=2)
    r.ellipse((x+3,66,x+19,112),fill='#829365',outline=INK,width=2)
    frame.paste(roll.crop((0,0,117,175)),(0,248),roll.getchannel('A').crop((0,0,117,175)))
    if t>=2.4:
        mark(d,37,440,'Sleeve opening',(117,352))
    conclusion(d,'Staged model / roll clears the rim')
    return frame


def clean_stripe(t):
    frame,d=stage(('One clean pass', 'across the stain.'))
    d.rounded_rectangle((20,175,340,480),7,fill='#e9d4ae',outline=RULE,width=2)
    rng=Random(27)
    x0,x1=48,307
    lower=248+128*ease(progress(t,.74,2.15))
    for _ in range(1150):
        x,y=rng.randrange(33,332),rng.randrange(191,469)
        hue=rng.choice(('#e4c89e','#d5b68b','#f0d9b2'))
        d.point((x,y),fill=hue)
    for _ in range(360):
        x,y=rng.randrange(70,292),rng.randrange(249,382)
        if y>lower or x>228:
            d.ellipse((x,y,x+3,y+2),fill='#b17e54')
    if t<2.4:
        d.rounded_rectangle((x0,lower-50,228,lower+9),7,fill=BLUE,outline=INK,width=2)
        d.line((x0+20,lower-43,212,lower-43),fill='#9ab7c8',width=2)
    else:
        d.line((228,242,228,397),fill=RED,width=2)
        words(d,(98,422),'One pass',17,GREEN,'mm')
        words(d,(278,422),'Untouched',16,RED,'mm')
    conclusion(d,'Staged fabric test / same view')
    return frame


def catch_pencil(t):
    frame,d=stage(('Can the clip', 'stop the pencil?'))
    d.polygon(((21,229),(323,272),(341,438),(32,397)),fill=WOOD,outline=INK,width=3)
    d.line((74,234,83,402),fill=RED,width=3)
    d.rounded_rectangle((242,297,273,360),6,outline=INK,width=4)
    d.rounded_rectangle((248,304,265,353),4,outline=INK,width=2)
    p=progress(t,.83,2.75)**1.3
    x=79+166*p
    y=288+29*p
    d.line((x,y-35,x+8,y+45),fill='#a74630',width=12)
    d.line((x-2,y-35,x+7,y+37),fill='#ee9c6a',width=4)
    d.polygon(((x+2,y+44),(x+15,y+44),(x+10,y+61)),fill='#caaa81')
    d.polygon(((x+7,y+56),(x+12,y+56),(x+10,y+63)),fill=INK)
    if t>=2.7:
        mark(d,39,440,'Contact / held',(245,320))
    conclusion(d,'One continuous illustrated release')
    return frame


def tray_clearance(t):
    frame,d=stage(('Can it pass', 'without tilting?'))
    d.polygon(((29,175),(327,175),(344,474),(16,474)),fill='#dfccaa')
    d.line((18,341,92,341),fill=INK,width=13)
    d.line((268,341,340,341),fill=INK,width=13)
    for x in (89,271):
        d.line((x,315,x,372),fill=GOLD,width=7)
    p=progress(t,0,3.68)
    y=431-192*p
    d.rounded_rectangle((102,y-42,258,y+43),10,fill=BLUE,outline=INK,width=3)
    for x in (145,214):
        d.ellipse((x-22,y-22,x+22,y+22),fill='#a9ced1',outline=PAPER,width=3)
        d.ellipse((x-15,y-15,x+15,y+15),outline=BLUE,width=1)
    if 1.0<=t<2.65:
        d.line((90,341,102,341),fill=RED,width=3)
        d.line((258,341,270,341),fill=RED,width=3)
    if t>=2.4:
        mark(d,34,435,'Both glasses held',(145,431-192*min(1,p)))
    conclusion(d,'Staged overhead / same tray and rim')
    return frame


def pencil_line(t):
    frame,d=stage(('Paper stroke', 'becomes a tool.'))
    digital=t>=1.43
    if digital:
        d.rounded_rectangle((17,159,344,492),9,fill='#e5e9e0',outline=INK,width=2)
        d.rectangle((18,161,342,193),fill=INK)
        words(d,(34,178),'Practice path tool',15,PAPER)
    else:
        d.rounded_rectangle((17,159,344,492),9,fill='#f9f5e6',outline='#c2b9a5',width=2)
        for y in range(208,480,25):
            d.line((21,y,341,y),fill='#e3ded0')
    target=(272,253)
    d.ellipse((target[0]-11,target[1]-11,target[0]+11,target[1]+11),outline=RED,width=2)
    q=progress(t,0,2.45)
    path=[(54+218*i/50,415-162*i/50+23*sin(i/50*tau)) for i in range(51)]
    p=path[min(50,int(50*q))]
    d.line(path[:max(2,int(50*q)+1)],fill=BLUE if digital else INK,width=4)
    if q<1:
        if digital:
            x,y=p;d.polygon(((x,y),(x+5,y+21),(x+16,y+16)),fill=INK,outline=PAPER)
        else:
            x,y=p;d.line((x+48,y-69,x+4,y-5),fill='#b87e45',width=13)
            d.polygon(((x,y),(x+12,y-5),(x+4,y-12)),fill=INK)
    else:
        chip(d,(23,518),'Endpoint selected',INK,MINT,17)
    return frame


def cloth_wipe(t):
    frame,d=stage(('Same plate.', 'One wipe.'))
    d.rectangle((15,165,345,484),fill='#9c7a55')
    for i in range(19):
        d.line((17,169+i*16,344,172+i*16),fill='#ad8963')
    d.ellipse((50,199,310,459),fill=PAPER,outline='#afc2ae',width=5)
    d.ellipse((81,230,279,428),outline='#b3c5b5',width=2)
    if t<1.17:
        for i,(x,y) in enumerate(((140,296),(185,287),(214,316),(131,351),(182,361),(223,350))):
            d.ellipse((x-16,y-11,x+18,y+17),fill=('#8b5341','#c78349','#9d5a42')[i%3],outline='#624938',width=2)
    else:
        for x,y in ((149,337),(157,327),(176,348),(222,291),(209,306)):
            d.ellipse((x,y,x+4,y+4),fill='#9d5a42')
    x=-288+620*progress(t,0,2.5)
    d.polygon(((x,181),(x+326,167),(x+343,471),(x+21,488)),fill='#b2c4a4',outline=INK,width=2)
    for i in range(12):
        d.line((x+i*27,185,x+i*27+23,480),fill='#9bae90')
    if t>=2.55:
        conclusion(d,'Same plate edge / changed contents')
    return frame


def squeezed_bars(t):
    frame,d=stage(('The chart fits', 'between my fingers.'))
    if t<1.95:
        q=ease(progress(t,0,1.67))
        width=255-184*q
        left=180-width*.5
        points=(14,20,26)
        for i,v in enumerate(points):
            x=left+width*(i+.25)/3
            d.rectangle((x,426-v*6,x+width*.25,426),fill=(GREEN,BLUE,ORANGE)[i])
        for x in (left-7,left+width+5):
            d.rounded_rectangle((x-16,248,x+15,411),16,fill='#b97957',outline='#88583b',width=2)
        d.line((39,426,320,426),fill=RULE,width=2)
    else:
        d.line((46,369,323,369),fill=INK,width=2)
        d.rectangle((48,290,318,360),fill=GREEN)
        d.rectangle((111,290,201,360),fill=BLUE)
        d.rectangle((201,290,318,360),fill=ORANGE)
        for x,v in ((80,14),(155,20),(253,26)):
            words(d,(x,325),str(v),22,PAPER,'mm')
        words(d,(180,417),'60 total units',25,INK,'mm')
        conclusion(d,'Widths changed; the values stayed')
    return frame


def template_pocket(t):
    frame,d=stage(('The notebook', 'has a hidden guide.'))
    d.rounded_rectangle((20,162,337,500),7,fill='#4f715b',outline=INK,width=3)
    d.rounded_rectangle((28,171,328,490),6,fill='#ece1c7')
    for y in range(193,480,20):
        d.line((43,y,315,y),fill='#c1c2a6')
    amount=ease(progress(t,.85,1.92))
    x,y=123,302-118*amount
    if t>=2.1:
        x=round(123-58*ease(progress(t,2.1,3.06)))
        y=round(184+120*ease(progress(t,2.1,3.06)))
    d.rounded_rectangle((x,y,x+166,y+133),5,fill='#b6cabb',outline=INK,width=2)
    d.line((x+17,y+43,x+143,y+43),fill=BLUE,width=3)
    for j in range(7):
        d.line((x+17+j*21,y+37,x+17+j*21,y+49),fill=BLUE,width=2)
    words(d,(x+18,y+20),'60 mm GUIDE',15,INK)
    if t<2.1:
        d.polygon(((84,342),(321,310),(322,482),(84,482)),fill='#c8b487',outline=RULE,width=2)
    else:
        d.line((82,347,208,347),fill=RED,width=1)
        mark(d,27,447,'Align both ends',(82,347))
    conclusion(d,'Illustrated practice notebook')
    return frame


def pivot(t):
    frame,d=stage(('Where does the', 'cut start?'))
    center=(177,328)
    paper=(40,247,286,420)
    d.rectangle(paper,fill='#a7bcc1',outline=RULE,width=2)
    spread=24-22*ease(progress(t,.88,1.96)) if t < 2.1 else 22-22*ease(progress(t,2.64,4.3))
    for sign in (-1,1):
        angle=radians(spread*sign)
        c,s=cos(angle),sin(angle)
        pts=[(center[0]+x*c-y*s,center[1]+x*s+y*c) for x,y in ((-132,-4),(114,-8),(126,1),(104,10),(-134,10))]
        d.polygon(pts,fill='#5d7f83' if sign==-1 else '#496a61',outline=INK,width=2)
        x,y=center[0]+125*c,center[1]+125*s
        d.ellipse((x-20,y-17,x+20,y+17),outline=GREEN,width=6)
    d.ellipse((168,319,186,337),fill=GOLD,outline=INK,width=2)
    if t>=.85:
        mark(d,43,198,'Fixed pivot',center)
    if t>=3.23:
        d.line((42,328,169,328),fill='#e1e8da',width=3)
    conclusion(d,'Both blades rotate around one pin')
    return frame


def lens_cap(t):
    frame,d=stage(('What grips', 'the lens rim?'))
    opening=ease(progress(t,.15,1.04))
    flatten=abs(1-2*opening)
    y=319
    d.ellipse((52,y-108*flatten,309,y+108*flatten),fill='#374d4e',outline=INK,width=4)
    if opening>.5:
        d.ellipse((71,y-86*flatten,288,y+86*flatten),outline='#759488',width=8)
        pinch=sin(t*4)**2 if t>=2.1 else 0
        for sign in (-1,1):
            x=180+sign*(100-24*pinch)
            d.rounded_rectangle((x-15,y-31,x+15,y+31),5,fill=GOLD,outline=INK,width=2)
        if t>=2.1:
            d.arc((45,192,316,447),19,159,fill='#7c9780',width=4)
            d.line((54,319,306,319),fill=RULE,width=1)
            conclusion(d,'Squeeze inward / release into rim')
        else:
            mark(d,180,437,'Two linked teeth',(278,319))
    return frame


def physical_chart(t):
    frame,d=stage(('Lift the paper.', 'Keep the same axis.'))
    box=(42,184,320,468)
    d.rectangle(box,fill='#e5ece0',outline=INK,width=2)
    p=ease(progress(t,.38,2.02))
    for x in (91,154,217,280):
        d.line((x,204,x,443),fill='#b4c5b4')
    for y in (229,295,362,428):
        d.line((89,y,294,y),fill='#b4c5b4')
    d.line((90,214,90,428,295,428),fill=INK,width=3)
    words(d,(53,211),'min',14,INK)
    line_t=progress(t,1.95,3.9)
    if t>=1.95:
        pts=[(108,382),(183,337),(256,283)]
        end=min(2,int(line_t*3))
        if end:
            d.line(pts[:end+1],fill=BLUE,width=3)
        for x,y in pts[:end+1]:
            d.ellipse((x-5,y-5,x+5,y+5),fill=BLUE)
    if p<1:
        end=round(455-p*277)
        d.polygon(((44,end-5),(320,end-21),(320,174),(43,178)),fill='#f5ebd3',outline=RULE,width=2)
        d.line((51,end-6,310,end-23),fill=GOLD,width=3)
        if end>248:
            words(d,(82,221),'Notebook',18,INK)
            d.line((90,228,90,end-7),fill=INK,width=3)
    if t>=2.45:
        conclusion(d,'Same baseline / minutes')
    return frame


SCENES={}
for family, entries in (
    ('test-in-motion',{1:tray_clearance,3:gradient_sleeve,4:clean_stripe,9:catch_pencil}),
    ('impossible-move',{56:cloth_wipe,92:squeezed_bars,95:pencil_line,96:physical_chart}),
    ('object-reveal',{3:template_pocket,6:pivot,24:lens_cap}),
):
    SCENES.update({f'hook-short-{family}-{n:03}':scene for n,scene in entries.items()})
POSTERS={key:.65 for key in SCENES}
