"""Native widescreen examples with inspectable edits, annotations and evidence."""
from math import cos, radians, sin, sqrt

from PIL import Image, ImageDraw, ImageFilter

from preview_common import H, W, ease, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, chip, words
from preview_hook_showcase_long_comparisons import BLUE, DARK, GREEN, ORANGE, RULE, SURFACE, caption, desk
from preview_plates import shot


def screen(title, note, original='Original practice example'):
    frame = Image.new('RGB', (W,H), DARK)
    d = ImageDraw.Draw(frame)
    words(d,(20,27),title,24,PAPER)
    words(d,(20,313),note,16,MINT)
    words(d,(20,339),original,13,PAPER,weight='regular')
    return frame,d


def row(d,x,y,w,label,on=False):
    d.rounded_rectangle((x,y,x+w,y+40),5,fill='#d7e8cf' if on else PAPER)
    words(d,(x+12,y+20),label,16,INK)


def strip(d,x,y,w,marker,names):
    d.rounded_rectangle((x,y,x+w,y+50),5,fill='#36554a')
    gap=4
    unit=(w-2*gap-gap*(len(names)-1))/len(names)
    for i,(name,color) in enumerate(names):
        start=x+gap+i*(unit+gap)
        d.rounded_rectangle((start,y+6,start+unit,y+39),4,fill=color)
        words(d,(start+6,y+22),name,14,PAPER)
    u=x+round(w*marker)
    d.line((u,y-4,u,y+48),fill=GOLD,width=2)


def one_cut(t):
    q=(t%5.6)/5.6
    final=t>=14.1
    cue=t>=5.8
    at=min(2.55,.16+2.37*q)
    frame,d=screen('Only one cut in the whole lesson',
                   'The wide shows where the tool is. Use one closer view for its contact.' if not final else
                   'One cut. Follow the same hand and the same dial through contact.')
    zoom=(1.36 if q>=.47 else 1.01) if final else 1.01
    frame.paste(shot('camera-live',at,zoom,-6,0,(428,181)),(18,58))
    chip(d,(461,66),'0 / 1 cuts' if not (q>=.47 and final) else '1 / 1 cuts',GREEN,PAPER,17)
    if cue:
        d.ellipse((248,115,312,184),outline=GOLD,width=2)
        words(d,(468,163),'Hand meets',16,PAPER)
        words(d,(468,188),'the dial',16,PAPER)
    strip(d,18,245,604,q,[('Wide',GREEN),('Detail',BLUE)] if final else [('One continuous source take',GREEN)])
    return frame


def dated_filter(t):
    show_all=t<1.05 or 6<=t<14.5
    frame,d=screen('The filter hid the first rows of the day',
                   'The displayed date is local. The filter reads UTC.' if t>=14.5 else 'Filter: October 18 / Europe–London (UTC+1)')
    d.rounded_rectangle((20,59,621,282),8,fill=PAPER)
    for x,text in ((32,'Activity'),(235,'Stored timestamp (UTC)'),(454,'Displayed (+01:00)')):
        words(d,(x,90),text,16,INK)
    for idx,(event,utc,local) in enumerate((('First lights','Oct 17 23:05','Oct 18 00:05'),
                                           ('Side room','Oct 17 23:42','Oct 18 00:42'),
                                           ('Run started','Oct 18 03:30','Oct 18 04:30'))):
        if idx<2 and not show_all:
            continue
        y=127+48*(idx if show_all else 0)
        d.rounded_rectangle((27,y-16,614,y+18),4,fill='#eedbca' if idx<2 and t>6 else '#e5ebdd')
        for x,v in ((32,event),(235,utc),(454,local)):
            words(d,(x,y),v,16,INK)
    button='No filter' if show_all else 'UTC date = Oct 18'
    chip(d,(31,242),button,GREEN,PAPER,15)
    return frame


def label_drifts(t):
    freeze=6<=t<14.5
    stage=0 if not freeze or t<10 else 1
    q=(.24 if stage==0 else 2.0) if freeze else (t%4.3)*.54
    frame,d=screen('The callout loses the moving corner',
                   'Compare the same edge in the source and the labeled cut.' if t>=6 else 'Watch the connector move away from the box corner.')
    # Project the label against a single camera crop of the same stock plate.
    for i,x in enumerate((20,330)):
        stamp=q if i==0 else max(.05,q)
        panel=shot('host-live',stamp,1.14,-34,-18,(290,204))
        frame.paste(panel,(x,62))
        label='Applied tracking' if i==0 and t<14.5 else 'Source with feature pin' if i else 'Candidate wall track'
        chip(d,(x+8,69),label,INK,PAPER,13)
        # The background feature supplies a visible reference even as the speaker moves.
        u,v=x+245,117
        d.rectangle((u-4,v-4,u+4,v+4),outline=GOLD,width=2)
        if i==0 and t<14.5:
            dx=round(54*min(1,q/2))
            d.line((u-57+dx,v+66,u+dx,v),fill=GOLD,width=2)
            chip(d,(u-111+min(25,dx),v+60),'Marker',INK,PAPER,13)
        elif t>=14.5:
            d.line((u-53,v+58,u,v),fill=GOLD,width=2)
    return frame


def missing_join(t):
    frame,d=screen('A time-lapse can conceal the whole action',
                   'The source stops between these two model frames.' if t<14.5 else 'Check source coverage before creating a reconstruction.',
                   'Staged assembly and illustrative frame times')
    before = t < 2.1 or t >= 6
    for i,x in enumerate((20,330)):
        d.rounded_rectangle((x,66,x+290,261),6,fill='#d2ae84')
        d.rectangle((x+35,169,x+255,188),fill='#6e7351')
        d.rectangle((x+47,109,x+65,169),fill='#84916a')
        d.rectangle((x+225,109,x+243,169),fill='#84916a')
        if (not before and i==0) or i==1:
            d.rectangle((x+59,121,x+233,139),fill='#b2704e',outline=INK,width=2)
        stamp='14:02:10' if before and i==0 else '14:04:30'
        chip(d,(x+11,73),stamp,INK,PAPER,14)
        if t>=14.5:
            d.line((x+134,100,x+134,137),fill=GOLD,width=3)
        words(d,(x+12,238),('Time-lapse frame','Next available frame')[i],15,INK)
    return frame


def timeline_cue(t):
    corrected=t>=19
    event=.93
    marker=.93 if corrected else .38
    stamp=.80 if 6<=t<14.5 else .32+(t%2.8)*.52
    frame,d=screen('The highlight beats the touch',
                   'Frame-step to the first visible contact.' if t<14.5 else 'Set the marker on the same source frame as the button state.')
    d.rounded_rectangle((20,60,621,235),8,fill=PAPER)
    d.rounded_rectangle((237,104,385,164),9,fill=GREEN if stamp>=event else '#749184')
    words(d,(311,134),'EXPORT',21,PAPER,'mm')
    p=ease(progress(stamp,.15,event))
    x=round(105+206*p)
    y=174-round(40*p)
    d.ellipse((x-13,y-13,x+13,y+13),fill='#c68568',outline=INK,width=2)
    if stamp>=marker:
        d.rounded_rectangle((230,97,392,171),13,outline=ORANGE,width=4)
    strip(d,20,244,600,min(1,stamp/1.8),[('Original touch',GREEN)])
    cuex=20+round(600*(marker/1.8))
    d.line((cuex,237,cuex,260),fill='#ee9e75',width=3)
    return frame


def chart_from_table(t):
    labels=('North door','Studio door','Yard door')
    values=(17,31,22)
    frame,d=screen('Build a chart that answers one question',
                   'Which two doors logged the most check-ins?' if t<12.2 else
                   'Keep count units and source values through the chart.')
    d.rounded_rectangle((20,61,315,280),8,fill=PAPER)
    d.rounded_rectangle((326,61,621,280),8,fill=PAPER)
    words(d,(34,84),'Practice log / check-ins',18,INK)
    words(d,(339,84),'Ordered by count',18,INK)
    for i,(name,v) in enumerate(zip(labels,values)):
        y=131+57*i
        if t>=5.2 and i>0:
            d.rounded_rectangle((28,y-18,307,y+18),4,fill='#dcebd5')
        words(d,(35,y),name,17,INK)
        words(d,(287,y),str(v),19,INK,'rm')
    if t>=12.2:
        p=ease(progress(t,12.2,15.5))
        order = sorted(range(3), key=lambda index: values[index], reverse=True)
        for rank, i in enumerate(order):
            y=131+57*rank
            words(d,(337,y),labels[i],14,INK)
            right=418+round(5.3*values[i]*p)
            d.rectangle((417,y-9,right,y+9),fill=GREEN)
            if p>.65:
                words(d,(right+10,y),str(values[i]),14,INK)
    return frame


def search_passage(t):
    index= int(5.6<=t<13.8)
    query=('late arrival','return window')[index]
    frame,d=screen('Search lands on the source passage',
                   'Both matches open the exact passage.' if t<13.8 else 'Earlier build: the result opened at the document title.')
    d.rounded_rectangle((20,60,235,283),7,fill=SURFACE)
    d.rounded_rectangle((246,60,620,283),7,fill=PAPER)
    row(d,31,72,191,'Query: '+query,True)
    row(d,31,128,191,'Practice handbook')
    row(d,31,175,191,('Page 3 · arrivals','Page 7 · returns')[index],t<13.8)
    if t<13.8:
        words(d,(266,89),('3. Access','7. Returns')[index],23,INK)
        strings=(('Please text the room lead before','a late arrival at the studio.'),
                 ('The return window ends on Friday.','Leave equipment on the left rack.'))[index]
        for i,line in enumerate(strings):
            y=146+47*i
            if i==1-index:
                d.rectangle((262,y-14,606,y+15),fill='#d7e9cd')
            caption(d,270,y,line)
    else:
        words(d,(265,137),'Practice handbook',30,INK)
        caption(d,266,184,'Contents / page 1')
    return frame


def judge_average(t):
    bad=t<8.85
    vals=(18,12,41 if bad else 14)
    frame,d=screen('Follow the warning to the original count',
                   'Sample sum: 18 + 12 + 14 = 44' if t>=13.8 else 'The warning and the total both stay visible.')
    d.rounded_rectangle((20,63,620,278),7,fill=PAPER)
    for i,(day,total) in enumerate(zip(('Monday','Tuesday','Wednesday'),vals)):
        y=103+54*i
        words(d,(38,y),day,18,INK)
        fill='#ead3bd' if i==2 and bad else '#dce9d7'
        d.rounded_rectangle((229,y-19,321,y+19),6,fill=fill)
        words(d,(274,y),str(total),18,INK,'mm')
    words(d,(460,103),'Total',18,INK)
    words(d,(584,118),str(sum(vals)),45,ORANGE if bad else GREEN,'rm')
    cue='Check source: 14 entered as 41' if bad else 'Check passed'
    chip(d,(334,170),cue,ORANGE if bad else GREEN,PAPER,15)
    if t>=13.8:
        chip(d,(354,228),'=SUM(B2:B4)',INK,PAPER,18)
    return frame


def hidden_records(t):
    before=t<6.8
    frame,d=screen('The row labels jump from seven to eleven',
                   'No deleted rows. Original filter: show only open items.' if t>=16 else
                   'Open the reference panel at the same row.')
    d.rounded_rectangle((20,57,343,282),7,fill=PAPER)
    words(d,(34,79),'Current view · open items',17,INK)
    rows=(6,7,11,12) if t<3 else (7,11,12,13)
    for i,n in enumerate(rows):
        y=106+34*i
        words(d,(40,y+11),f'{n:02d}',17,BLUE)
        words(d,(96,y+11),'Open',16,INK)
        d.line((35,y+24,310,y+24),fill=RULE)
    if not before:
        d.rounded_rectangle((354,58,622,283),7,fill=PAPER)
        words(d,(366,80),'Original record state',18,INK)
        for i,n in enumerate((8,9,10)):
            row(d,365,102+52*i,244,f'Row {n} / Closed',t>=16)
    return frame


def lost_quote(t):
    frame,d=desk('Why does the thumbnail remember a line?',
                 'Same slide, two recorded versions.' if t<16 else 'The preview was generated before the revision.')
    for i,x in enumerate((20,330)):
        words(d,(x+12,84),('Cached preview','Open presentation')[i],18,INK)
        scale=1 if t<6.8 else 1.16
        words(d,(x+14,144),'“We open the doors at noon”' if i==0 else '“Doors open at 14:00”',
              round(17*scale),ORANGE if t>=6.8 and i==0 else INK)
        words(d,(x+13,228),('Exported 10:15','Edited 12:30')[i],15,GREEN)
        if t>=16:
            words(d,(x+13,252),('Version 4 render','Version 5 document')[i],16,INK)
    return frame


def chart_before_event(t):
    frame,d=screen('The climb started before the marked event',
                   'The extra period is earlier on the same scale.' if t<13.5 else 'Earlier growth weakens the causal claim.')
    x0,y0,w,h=50,69,546,189
    d.rounded_rectangle((25,54,620,289),7,fill=PAPER)
    for i in range(5):
        y=y0+i*46
        d.line((x0,y,x0+w,y),fill=RULE,width=1)
        words(d,(x0-5,y),str(40-i*10),11,INK,'rm')
    data=(11,14,19,23,28,32,37)
    pts=[(72+i*81,255-round(v*4.6)) for i,v in enumerate(data)]
    event=pts[4][0]
    d.line((event,68,event,255),fill=ORANGE,width=2)
    chip(d,(event-37,84),'July 12',ORANGE,PAPER,15)
    shows_full=t>=5.8
    d.line(pts if shows_full else pts[4:],fill=BLUE,width=4)
    for x,y in pts if shows_full else pts[4:]:
        d.ellipse((x-5,y-5,x+5,y+5),fill=GREEN)
    if t>=13.5:
        words(d,(103,275),'Earlier observations',15,BLUE)
    words(d,(559,274),'Units',14,INK,'rm')
    return frame


def pendulum(t):
    frame,d=screen('Which marker returns to the bottom first?',
                   'Equal mass and starting angle. Pick before both release.' if t<15.5 else
                   'Sample motion uses periods proportional to the square root of length.',
                   'Original animated pendulum model')
    started=t>=15.5
    run=max(0.,t-15.55)
    for x,length,meters in ((175,128,.64),(465,190,.95)):
        angle=radians(28)*cos(run/sqrt(meters/9.81))
        cx=x+length*sin(angle)
        cy=78+length*cos(angle)
        d.line((x,78,x,78+length),fill='#9baba2',width=2)
        d.line((x,78,cx,cy),fill=MINT,width=2)
        d.ellipse((cx-12,cy-12,cx+12,cy+12),fill=GOLD,outline=PAPER,width=2)
        d.ellipse((x-5,73,x+5,83),fill=PAPER)
        words(d,(x+20,97),f'{meters:.2f} m',17,PAPER)
        if started and abs(sin(angle))<.09:
            d.ellipse((x-18,78+length-18,x+18,78+length+18),outline=GOLD,width=2)
    return frame


def pinhole(t):
    frame,d=screen('The pinhole turns the street upside down',
                   'One source street axis. One inverted projected image.',
                   'Original projection model using licensed street footage')
    data=shot('walk-live',.2+(t%4.2)*.6,1,-48,0,(265,168))
    x,y=20,76
    plot=data if t>=13.8 else data.rotate(180)
    if 5.6<=t<13.8:
        plot=plot.filter(ImageFilter.GaussianBlur(2.8*ease(progress(t,5.6,8.4))))
    frame.paste(plot,(x,y))
    if t < 13.8:
        source = data.filter(ImageFilter.GaussianBlur(5 * (1 - ease(progress(t, 5.6, 8.4)))))
    else:
        source = data.rotate(180)
    frame.paste(source,(355,y))
    chip(d,(30,83),'Screen / inverted' if t<13.8 else 'Original source',INK,PAPER,15)
    chip(d,(365,83),'Street / upright' if t < 13.8 else 'Screen / inverted',INK,PAPER,15)
    if t>=13.8:
        d.line((284,105,355,218),fill=GOLD,width=2)
        d.line((284,218,355,105),fill=GOLD,width=2)
        d.ellipse((315,157,325,167),fill=GOLD)
    return frame


SCENES={}
for family, entries in (
    ('constraint-challenge',{1:one_cut}),
    ('visible-problem',{12:dated_filter,23:label_drifts,29:missing_join,30:timeline_cue}),
    ('learning-promise',{24:chart_from_table}),
    ('result-first',{11:search_passage,12:judge_average,27:pinhole}),
    ('mystery',{33:hidden_records,36:lost_quote}),
    ('evidence-led-reversal',{18:chart_before_event}),
    ('prediction',{4:pendulum}),
):
    SCENES.update({f'hook-long-{family}-{n:03}':scene for n,scene in entries.items()})
POSTERS={key:3.2 for key in SCENES}
