"""Original workflow diagrams and illustrative editor previews."""
from math import cos, sin
from PIL import Image, ImageDraw
from preview_common import backdrop, blend, ease, font, progress
from preview_plates import shot
from preview_live_action import behind_subject

INK = (23, 43, 44)
DARK = (19, 43, 46)
DEEP = (29, 58, 57)
FOREST = (64, 104, 83)
MUTED = (106, 139, 121)
SAGE = (159, 191, 160)
MINT = (209, 229, 197)
PALE = (224, 235, 213)
LINE = (190, 208, 190)
CREAM = (249, 244, 225)
PAPER = (246, 244, 235)
GOLD = (235, 182, 101)
BLUE = (123, 182, 195)
CLAY = (218, 147, 109)


def at(t, start, end):
    return ease(progress(t, start, end))


def box(d, xy, color, radius=9, border=None):
    d.rounded_rectangle(xy, radius=radius, fill=color, outline=border, width=1)


def text(d, value, x, y, size=16, color=INK, weight='bold', anchor='lm'):
    d.text((x, y), value, font=font(size, weight), fill=color, anchor=anchor)


def dot(d, x, y, radius, color):
    d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)


def dark():
    image = backdrop(DARK, DEEP, False)
    return image, ImageDraw.Draw(image)


def light():
    image = backdrop((232, 239, 218), (208, 224, 199), False)
    return image, ImageDraw.Draw(image)


def icon_play(d, x, y, color=CREAM, scale=1):
    d.polygon([(x-4*scale,y-6*scale), (x+6*scale,y), (x-4*scale,y+6*scale)], fill=color)


def pane(im, rect, style, t, caption=None):
    x0,y0,x1,y1 = (int(v) for v in rect)
    image = backdrop(DEEP if style==1 else (61,88,71), (61,88,75) if style==1 else (139,163,121))
    d = ImageDraw.Draw(image)
    if style==0:
        image = shot('host-live',t,1.24,-34,-22)
        d = ImageDraw.Draw(image)
    elif style==1:
        d.arc((56,29,573,453),197,356,fill=SAGE,width=3)
        d.arc((105,43,522,428),199,357,fill=MUTED,width=2)
        for i in range(4):
            h=64+i*29+11*sin(t*2+i)
            box(d,(151+i*92,246-h,206+i*92,246),blend(SAGE,GOLD,.34*i),int(9+i))
        d.line((128,249,531,249),fill=CREAM,width=3)
    else:
        image = shot('walk-live',t,1.06,0,9)
        d = ImageDraw.Draw(image)
    if caption:
        width=int(d.textlength(caption,font=font(31)))+44
        u=(640-width)/2
        box(d,(u,294,u+width,344),DARK,11)
        text(d,caption,320,319,31,CREAM,'bold','mm')
    im.paste(image.resize((max(1,x1-x0),max(1,y1-y0)),Image.Resampling.LANCZOS),(x0,y0))


def arrow(d, x1, y1, x2, y2, p, color=FOREST):
    if p <= 0:
        return
    x,y=x1+(x2-x1)*p,y1+(y2-y1)*p
    d.line((x1,y1,x,y),fill=color,width=2)
    angle=((x2-x1)**2+(y2-y1)**2)**.5
    ux,uy=(x2-x1)/angle,(y2-y1)/angle
    d.polygon([(x,y),(x-8*ux-4*uy,y-8*uy+4*ux),(x-8*ux+4*uy,y-8*uy-4*ux)],fill=color)


def reference_plan(t):
    im,d=light()
    box(d,(40,69,288,283),PAPER,13,LINE)
    text(d,"Style sample",57,88,18,FOREST)
    example = behind_subject(t).resize((212,136),Image.Resampling.LANCZOS)
    im.paste(example,(57,107))
    d.line((58,259,265,259),fill=LINE,width=2)
    d.line((58,259,58+207*progress(t,0,3.18),259),fill=FOREST,width=2)
    arrow(d,293,174,338,174,at(t,.39,.88))
    box(d,(342,69,601,283),PAPER,13,LINE)
    text(d,"Edit plan",361,92,19,FOREST,'serif')
    for i,(cue,action) in enumerate((("0:01","Push in on the hook"),("0:04","Put the title behind me"),("0:07","Cut at the sentence end"))):
        q=at(t,.81+i*.39,1.12+i*.39)
        y=120+i*49
        box(d,(358,y,586,y+36),blend(PAPER,MINT,q),7)
        if q > .47:
            text(d,cue,369,y+18,15,FOREST,'mono')
            text(d,action,422,y+18,14,INK)
    return im


def reusable_style(t):
    im,d=dark()
    box(d,(37,61,240,300),PAPER,12,LINE)
    text(d,"Style kit",55,91,23,FOREST,'serif')
    for i,col in enumerate((FOREST,SAGE,GOLD,CREAM)):
        box(d,(55+i*42,110,91+i*42,146),col,5,LINE)
    text(d,"Title",57,175,28,INK,'serif')
    text(d,"Supporting captions",57,209,13,FOREST,'regular')
    d.line((57,235,216,235),fill=LINE)
    text(d,"Soft entrance",57,257,12,FOREST,'mono')
    for i,(caption,style) in enumerate((("A day outside",2),("Four key trends",1))):
        p=at(t,.43+i*.62,1+i*.62)
        if p < .03:
            continue
        y=70+i*119+(1-p)*18
        arrow(d,244,y+44,286,y+44,p,SAGE)
        box(d,(298,y,601,y+97),blend(DEEP,CREAM,.6+p*.4),13)
        pane(im,(306,y+8,424,y+88),style,t)
        text(d,caption,437,y+37,18,FOREST,'serif')
        text(d,"Shared palette & type",437,y+63,12,INK,'regular')
    return im


def waveform(d, x, y, width, amplitude=17, color=CREAM, t=0):
    for i in range(0,int(width),4):
        h=1+amplitude*(.44+.56*abs(sin(i*.084+t)))*(.28+.72*abs(cos(i*.041)))
        d.line((x+i,y-h,x+i,y+h),fill=color,width=1)


def rough_cut(t):
    im,d=dark()
    box(d,(43,45,600,311),(39,69,63),12,MUTED)
    p=at(t,.87,1.83)
    pane(im,(60,63,298,209),0,min(3.12,t*.68+(.74 if p > .55 else 0)))
    text(d,"Rough cut",318,76,22,CREAM,'serif')
    revisions=[("00:00","Keep the introduction",MINT),("00:04","Remove a restart",CLAY),("00:10","Keep the explanation",MINT)]
    for i,(stamp,desc,col) in enumerate(revisions):
        y=110+i*36
        box(d,(319,y,579,y+29),(48,82,73),6)
        text(d,stamp,330,y+15,14,col,'mono')
        text(d,desc,388,y+15,15,CREAM,'regular')
        if i==1 and p>.5:
            d.line((388,y+15,511,y+15),fill=CLAY,width=2)
    d.line((61,222,580,222),fill=MUTED)
    x=61
    for i,(width,col) in enumerate(((149,FOREST),(117*(1-p),CLAY),(235,FOREST))):
        if width>1:
            box(d,(x,244,x+width,279),col,4)
            if width>13:
                waveform(d,x+7,261,width-12,12,CREAM,t)
            x+=width+4
    playhead=61+502*progress(t,.05,3.2)
    d.line((playhead,231,playhead,291),fill=GOLD,width=2)
    d.polygon([(playhead-4,230),(playhead+4,230),(playhead,237)],fill=GOLD)
    return im


def timeline_handoff(t):
    im,d=dark()
    box(d,(40,34,600,325),(34,62,58),13,MUTED)
    pane(im,(58,51,288,187),2,t)
    text(d,"Editable sequence",311,80,24,CREAM,'serif')
    text(d,"Picture, sound, and titles",311,111,13,MINT,'regular')
    tracks=(("Picture",SAGE,[(0,177),(185,186),(379,52)]),
            ("Dialogue",BLUE,[(0,177),(185,246)]),
            ("Captions",GOLD,[(44,96),(287,120)]),
            ("Music",CLAY,[(0,431)]),
            ("Overlays",MINT,[(256,113)]))
    for i,(name,color,ranges) in enumerate(tracks):
        y=192+i*24
        text(d,name,56,y+10,13,MINT,'regular')
        box(d,(140,y,582,y+20),(46,80,72),4)
        row=at(t,.22+i*.26,.57+i*.26)
        for x,w in ranges:
            if row>0:
                box(d,(147+x,y+3,147+x+w*row,y+17),color,3)
                if i in (1,3) and w*row>15:
                    waveform(d,151+x,y+10,w*row-6,5,DARK,t)
    if t>1.04:
        x=146+430*progress(t,1.04,3.17)
        d.line((x,185,x,311),fill=CREAM,width=2)
        d.polygon([(x-4,185),(x+4,185),(x,193)],fill=CREAM)
    return im


def scene_assembly(t):
    im,d=light()
    story=(("Hook",0,"0:03"),("Explain",1,"0:09"),("Close",2,"0:04"))
    for i,(stage,style,run) in enumerate(story):
        x=43+i*189
        p=at(t,.15+i*.46,.48+i*.46)
        box(d,(x,63,x+177,244),blend(PAPER,CREAM,p),10,blend(LINE,FOREST,p*.7))
        if p>.1:
            pane(im,(x+9,74,x+168,166),style,t)
            text(d,stage,x+13,192,20,FOREST,'serif')
            text(d,run,x+163,192,12,FOREST,'mono','rm')
            d.line((x+13,222,x+14+150*p,222),fill=blend(SAGE,FOREST,p),width=3)
        arrow(d,x+88,248,x+88,269,at(t,1.5+i*.20,1.87+i*.20))
    box(d,(43,280,598,303),FOREST,7)
    for i,color in enumerate((MINT,BLUE,GOLD)):
        q=at(t,1.84+i*.20,2.16+i*.19)
        if q>0:
            x=54+i*182
            box(d,(x,286,x+174*q,297),color,4)
    return im


def split_passes(t):
    im,d=light()
    rows=(("Picture pass",54,FOREST,("Dialogue cleanup","Rough cut")),
          ("Motion pass",173,(74,128,133),("Design graphics","Match cues")))
    for name,y,color,stages in rows:
        box(d,(47,y,393,y+102),PAPER,12,LINE)
        text(d,name,65,y+21,18,FOREST,'serif')
        for i,stage in enumerate(stages):
            q=at(t,.19+(y/176)*.38+i*.38,.61+(y/176)*.38+i*.38)
            x=65+i*153
            box(d,(x,y+45,x+135,y+77),blend(PALE,color,q),7)
            text(d,stage,x+66,y+61,12,CREAM if q>.68 else FOREST,'bold','mm')
        arrow(d,404,y+53,442,177,at(t,1.42,2.13),color)
    q=at(t,1.92,2.51)
    if q>.02:
        box(d,(453,105,601,250),blend(PAPER,FOREST,q),11)
        if q>.6:
            pane(im,(463,115,590,202),1,t)
            text(d,"Final edit",525,225,20,CREAM,'serif','mm')
    return im


def batch_chart(t):
    im,d=dark()
    box(d,(37,55,210,307),PAPER,12,LINE)
    text(d,"Data input",55,77,17,FOREST,'serif')
    labels=(("April",(4,7,6)),("May",(5,9,7)),("June",(7,8,10)))
    for i,(month,series) in enumerate(labels):
        y=106+i*55
        p=at(t,.28+i*.56,.60+i*.56)
        box(d,(53,y,192,y+44),blend(CREAM,MINT,p),7)
        text(d,month,64,y+15,13,FOREST)
        text(d," / ".join(map(str,series)),64,y+32,11,INK,'mono')
        arrow(d,197,y+23,234,y+23,p,SAGE)
    for i,(name,series) in enumerate(labels):
        p=at(t,.46+i*.56,.90+i*.56)
        if p < .03:
            continue
        x=239+i*123
        y=97+(1-p)*22
        box(d,(x,y,x+112,y+168),blend(SAGE,PAPER,p),9)
        text(d,name,x+13,y+21,18,FOREST,'serif')
        d.line((x+13,y+133,x+97,y+133),fill=LINE,width=2)
        for j,value in enumerate(series):
            h=value*7.0*p
            box(d,(x+14+27*j,y+132-h,x+32+27*j,y+132),blend(FOREST,GOLD,j*.33),3)
        text(d,name.lower()+".mp4",x+8,y+152,13,FOREST,'mono')
    return im


SCENES = {
    "reference-driven-workflow": reference_plan,
    "reusable-style-system": reusable_style,
    "ai-rough-cut": rough_cut,
    "timeline-first-ai-edit": timeline_handoff,
    "scene-by-scene-animation": scene_assembly,
    "split-editing-passes": split_passes,
    "batch-chart-render": batch_chart,
}
