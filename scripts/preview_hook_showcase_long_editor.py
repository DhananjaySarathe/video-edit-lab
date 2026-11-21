"""Native widescreen cut walkthroughs using original models and licensed plates."""
from math import sin, tau

from PIL import Image, ImageDraw, ImageFilter

from preview_common import H, W, ease, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, chip, words
from preview_hook_showcase_long_comparisons import BLUE, GREEN, ORANGE, RULE, SURFACE, caption, desk
from preview_hook_showcase_long_motion import screen, strip
from preview_plates import shot


def embedded_focus(t):
    footer=('Near label first. Watch the far door.' if t<5.2 else 'Open the focus on the far door only.'
            if t<12.2 else 'Return to the same start and check the order.')
    frame,d=screen('Foreground first, background second',footer,'Original optical demonstration using a licensed room plate')
    size=(568,222)
    x,y=36,58
    local = t if t<12.2 else t-12.2
    far=ease(progress(local,5.2 if t<12.2 else 2.2,7.55 if t<12.2 else 4.2))
    base=shot('room',0,1,0,0,size).filter(ImageFilter.GaussianBlur((1-far)*6))
    frame.paste(base,(x,y))
    plaque=Image.new('RGBA',(252,94))
    p=ImageDraw.Draw(plaque)
    p.rounded_rectangle((12,9,228,82),6,fill='#e9e2c6',outline=GREEN,width=3)
    words(p,(120,47),'CHECK THE SILL',22,INK,'mm')
    plaque=plaque.filter(ImageFilter.GaussianBlur(far*7))
    frame.paste(plaque,(64,124),plaque)
    if t>=5.2:
        chip(d,(43,61),'Far plane' if far>.5 else 'Near plane',INK,MINT,14)
    return frame


def logo_anchor(t):
    frame,d=screen('Find one anchor for all three logo pieces',
                   'Mark where the three pieces meet.' if t<12.2 else 'The compass center stays fixed while the lockup shrinks.')
    for i,size in enumerate((1,1-ease(progress(t,12.2,16))*.47)):
        cx,cy=165+i*308,160
        d.rounded_rectangle((cx-131,65,cx+131,267),7,fill=PAPER,outline=RULE)
        r=41*size
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=GREEN,width=max(2,round(5*size)))
        d.polygon(((cx,cy-36*size),(cx+15*size,cy+18*size),(cx,cy+13*size),(cx-15*size,cy+18*size)),fill=ORANGE)
        words(d,(cx,cy+62*size),'NORTH',round(27*size),INK,'mm')
        if t>=5.2:
            d.line((cx-17,cy,cx+17,cy),fill=BLUE,width=1)
            d.line((cx,cy-17,cx,cy+17),fill=BLUE,width=1)
    return frame


def show_thumb(t):
    frame,d=screen('The thumbnail must come from the opening',
                   'Compare the real opening frames at the same crop.' if t>=14.1 else 'Choose a frame with the subject and its action together.',
                   'Licensed footage / illustrated source timeline')
    at=.31 if t<5.8 else 1.88 if t<14.1 else 2.63
    size=(357,192)
    full=shot('coffee-live',at,1,0,1,size)
    frame.paste(full,(19,65))
    if t<5.8:
        d.rounded_rectangle((398,84,615,226),8,outline=MINT,width=2)
        words(d,(506,149),'Empty cover',20,PAPER,'mm')
    else:
        frame.paste(shot('coffee-live',at,1.27,-38,2,(215,142)),(398,84))
        chip(d,(404,91),'Thumbnail crop',INK,PAPER,14)
    strip(d,19,255,596,at/3.2,[('Opening clip 0–3.2 s',GREEN)])
    chip(d,(27,74),f'Source {at:.2f} s',INK,PAPER,14)
    return frame


def avoid_label(t):
    q=(t%4.2)/4.2
    frame,d=screen('The product label has to stay readable',
                   'The bottle crosses the callout. Move the annotation above its path.'
                   if t<14.1 else 'The label is clear for the entire same movement.',
                   'Original moving product mock-up')
    d.rounded_rectangle((24,59,617,280),10,fill='#e5e8de')
    x=round(135+370*q)
    d.rounded_rectangle((x-43,103,x+43,258),19,fill=BLUE,outline=INK,width=2)
    d.rounded_rectangle((x-19,79,x+19,117),8,fill='#a3b79d',outline=INK)
    d.rounded_rectangle((x-38,164,x+38,212),5,fill=PAPER)
    words(d,(x,186),'SAMPLE',16,INK,'mm')
    if 5.8<=t<14.1:
        chip(d,(244,171),'Recycle the sleeve',INK,PAPER,16)
    elif t>=14.1:
        chip(d,(244,68),'Recycle the sleeve',INK,PAPER,16)
        d.line((333,98,333,140),fill=GREEN,width=3)
    return frame


def arrow_side(t):
    frame,d=screen('Which face actually carries the arrow?',
                   'The two faces align when viewed head-on.' if t<13.5 else 'The side view separates the transparent layers.',
                   'Original two-plane display model')
    turn=ease(progress(t,5.8,9.8)) if t<13.5 else .83
    front=100+55*turn
    back=front+127*turn
    for x,color in ((back,'#b2cfbf'),(front,'#d7e5d7')):
        d.polygon(((x,115),(x+287,102),(x+304,222),(x+12,242)),fill=color,outline='#6f9784',width=3)
    # Show the rear mark through the transparent front where the two masks overlap.
    x=back+164
    d.line((x-59,169,x+51,166),fill=BLUE,width=7)
    d.polygon(((x+53,166),(x+26,153),(x+27,181)),fill=BLUE)
    if t>=5.8:
        d.line((x+7,166,508,271),fill=GOLD,width=2)
        words(d,(469,255),'Rear ink layer',15,PAPER)
    return frame


def near_horizon(t):
    frame,d=screen('Can the lettering survive the push?',
                   'Inspect the start and target.' if t<15.5 else 'Follow the real crop while the lettering stays fixed to the object.')
    p=0 if t<6.5 else 1 if t<15.5 else ease(progress(t,15.5,19.5))
    d.rectangle((20,59,618,275),fill='#dcd9c3')
    x=round(320+25*p)
    y=162
    r=68+42*p
    d.rounded_rectangle((x-r,y-74-p*17,x+r,y+75+p*16),13,fill='#245a63',outline=INK,width=3)
    d.rectangle((x-r+8,y-14,x+r-8,y+36),fill=PAPER)
    words(d,(x,y+8),'CUTTER No. 5',round(15+9*p),INK,'mm')
    chip(d,(29,68),'Start' if p==0 else 'Target' if p==1 else 'Camera moves',INK,PAPER,14)
    return frame


def stage_lantern(t):
    frame,d=screen('The first lantern is about to light',
                   'Hold at the approach, then leave before the light.' if t<17.5 else 'Return to the same reach and play the switch.',
                   'Original staged animation')
    earlier=17.5<=t<22.0
    lit=t>=23.15
    d.rectangle((23,63,617,279),fill='#1b2628' if not lit else '#5a4830')
    d.polygon(((24,240),(617,240),(617,279),(24,279)),fill='#41534d' if earlier else '#292d27')
    x,y=(208,141) if t<7 or earlier else (269,132)
    if lit:
        glow=Image.new('RGBA',(W,H))
        g=ImageDraw.Draw(glow)
        for size,alpha in ((111,30),(95,35),(75,60),(52,89)):
            g.ellipse((x-size,y+41-size,x+size,y+41+size),fill=(250,187,100,alpha))
        glow=glow.filter(ImageFilter.GaussianBlur(20))
        frame.paste(glow,(0,0),glow)
    d.rounded_rectangle((x-28,y,x+28,y+82),7,fill='#edc776' if lit else '#3a5452',outline=GOLD,width=3)
    d.arc((x-25,y-32,x+25,y+28),170,370,fill=PAPER,width=5)
    if not earlier:
        p=progress(t,7,14) if t<17.5 else progress(t,22,23.15)
        px=round(429+(x+21-429)*p)
        d.rounded_rectangle((px,y+13,px+138,y+27),7,fill='#ab7656')
    else:
        d.line((x-29,251,x+29,251),fill=GOLD,width=5)
        d.line((x,230,x,273),fill=GOLD,width=5)
        chip(d,(370,82),'Earlier blocking',INK,PAPER,16)
    if 14<=t<17.5:
        chip(d,(380,81),'Cut before it lights',INK,PAPER,16)
    return frame


def puzzle_marbles(t):
    frame,d=screen('Which marble reaches the shared line first?',
                   'Both marbles leave one starting gate. Choose a lane before release.'
                   if t<15.5 else 'Follow both paths on the single illustrated run.',
                   'Original model / times describe this animation')
    p=progress(t,15.5,22.25)
    for i,(y,col) in enumerate(((123,GREEN),(230,BLUE))):
        d.rounded_rectangle((29,y-29,609,y+31),6,fill='#dbe5d9')
        path=lambda q: (70+475*q,y+18*sin(q*tau)*(1 if i==0 else .42))
        d.line([path(j/45) for j in range(46)],fill=col,width=8)
        end=min(1,p*(1.12 if i==0 else 1.02))
        x,py=path(end)
        d.ellipse((x-11,py-11,x+11,py+11),fill=ORANGE,outline=PAPER,width=2)
        words(d,(52,y-20),('Inside bend','Outside bend')[i],12,INK)
        if end==1:
            words(d,(597,y+14),('6.0 s','6.6 s')[i],14,INK,'rm')
    d.line((71,86,71,263),fill=GOLD,width=4)
    d.line((545,86,545,263),fill=GOLD,width=4)
    return frame


def swapped_crop(t):
    frame,d=desk('The source still has the missing detail',
                 'Both panels start from the same source frame.' if t<13.5 else 'The display crop caused the loss.')
    source=.26+(t%4.16)*.57
    wide=shot('camera-live',source,1,0,0,(290,176))
    narrow=shot('camera-live',source,1.53,-73,-29,(290,176))
    frame.paste(narrow if t<5.8 else wide,(20,64))
    frame.paste(wide,(330,64))
    words(d,(30,260),'Camera A / display crop' if t<5.8 else 'Camera A / source',17,INK)
    words(d,(342,260),'Original frame',17,INK)
    if t>=13.5:
        d.rectangle((31,75,228,222),outline=GOLD,width=3)
        chip(d,(31,206),'Displayed crop',INK,PAPER,14)
    return frame


SCENES = {}
for family, entries in (
    ('learning-promise',{22:logo_anchor,37:embedded_focus}),
    ('constraint-challenge',{8:show_thumb,9:avoid_label}),
    ('evidence-led-reversal',{19:swapped_crop,20:arrow_side}),
    ('prediction',{2:puzzle_marbles,18:near_horizon}),
    ('decisive-moment',{8:stage_lantern}),
):
    SCENES.update({f'hook-long-{family}-{n:03}':scene for n,scene in entries.items()})
POSTERS={key:3.6 for key in SCENES}
