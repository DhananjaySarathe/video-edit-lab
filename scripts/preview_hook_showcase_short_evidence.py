"""Phone-sized edits using internally consistent sample data and source documents."""
from PIL import Image, ImageDraw

from preview_common import ease, font, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, PORTRAIT, chip, words
from preview_hook_showcase_short_optics import GREEN, RED, RULE, stage

PALE = '#e1e9d9'
GRAY = '#d3d7c9'
BLUE = '#325a86'
ORANGE = '#ca6a43'


def card(d, box):
    d.rounded_rectangle(box, 7, fill='#fffcf2', outline=GRAY, width=2)


def small(d, at, message):
    words(d, at, message, 16, INK, weight='regular')


def conclusion(d, message):
    chip(d, (20, 526), message, INK, MINT, 16)


def axes(d, box, ticks, unit):
    x0,y0,x1,y1=box
    for i, tick in enumerate(ticks):
        y = y1 - round((y1-y0)*i/(len(ticks)-1))
        d.line((x0,y,x1,y), fill=GRAY, width=1)
        words(d,(x0-9,y),str(tick),12,INK,'rm')
    d.line((x0,y0,x0,y1,x1,y1),fill=RULE,width=2)
    words(d,(x0,y0-17),unit,14,INK)


def zoom_points(t):
    frame,d=stage(('Does zoom make', 'more data?'))
    card(d,(18,173,342,482))
    axes(d,(58,230,316,437),(0,10,20,30),'Stops per hour')
    scale=84+round(33*ease(progress(t,1.2,2.8)))
    values=(11,23,16)
    positions=[(187+(i-1)*scale,437-val*207/30) for i,val in enumerate(values)]
    for i,(x,y) in enumerate(positions):
        words(d,(x,454),('Mon','Tue','Wed')[i],13,INK,'mm')
    d.line(positions,fill=BLUE,width=3)
    d.line((187,232,187,434),fill=RED,width=1)
    for x,y in positions:
        d.ellipse((x-6,y-6,x+6,y+6),fill=GREEN)
    conclusion(d,'3 points before and after zoom')
    return frame


def blank_mean(t):
    frame,d=stage(('Blank and zero', 'change the mean.'))
    p = t >= 1.85
    for i,y in enumerate((191,351)):
        card(d,(19,y,341,y+130))
        small(d,(30,y+23),('Original row','Test row')[i])
        for j,val in enumerate(('6','12','0' if i==1 and p else '')):
            l=29+j*63
            d.rectangle((l,y+45,l+51,y+82),fill=PALE if j==2 else PAPER,outline=GRAY)
            words(d,(l+25,y+64),val,20,BLUE,'mm')
        words(d,(327,y+64), 'Mean 6' if i==1 and p else 'Mean 9',21, GREEN,'rm')
        if t>=2.8:
            small(d,(33,y+106),'(6 + 12 + 0) ÷ 3' if i==1 else '(6 + 12) ÷ 2')
    conclusion(d,'The third cell enters the divisor' if p else 'Both rows start with two inputs')
    return frame


def price_per_gram(t):
    frame,d=stage(('Which pack costs', 'less per gram?'))
    for i,y in enumerate((183,341)):
        weight,cents=(100,280) if i==0 else (200,420)
        card(d,(20,y,337,y+131))
        d.rounded_rectangle((32,y+14,111,y+114),6,fill=('#a74f37','#3a6c5a')[i])
        words(d,(72,y+40),f'PACK {i+1}',13,PAPER,'mm')
        words(d,(72,y+70),f'{weight} g',20,PAPER,'mm')
        words(d,(130,y+36),f'${cents/100:.2f}',27,INK)
        if t>=1.2:
            small(d,(132,y+68),f'{cents}¢ ÷ {weight} g')
        if t>=2.8:
            words(d,(133,y+101),f'{cents/weight:.1f}¢/g',23,GREEN)
    conclusion(d,'Same shop and date / sample prices')
    return frame


def growth(t):
    frame,d=stage(('Which grew', 'fastest?'))
    card(d,(18,172,342,491))
    percentage=t>=1.95
    axes(d,(60,229,320,436),(0,25,50,75,100),'Growth (%)' if percentage else 'Finish (units)')
    pairs=((10,18),(36,50),(62,74))
    for i,(start,finish) in enumerate(pairs):
        x=87+i*80
        val=round(100*(finish-start)/start) if percentage else finish
        y=436-round(207*val/100)
        d.rectangle((x,y,x+38,436),fill=ORANGE if i==0 and percentage else GREEN)
        words(d,(x+19,y-11),f'{val}%' if percentage else str(val),13,INK,'mm')
        words(d,(x+19,456),chr(65+i),15,INK,'mm')
        if t>=2.8:
            words(d,(x+19,475),f'{start} → {finish}',12,BLUE,'mm')
    if t>=2.8:
        conclusion(d,'A started at 10 / +8 is +80%')
    return frame


def interval(t):
    frame,d=stage(('How certain is', 'the apparent lead?'))
    lines=((57,45,69),(65,52,78))
    reveal=ease(progress(t,1.2,2.3))
    X=lambda value: 47+round((value-35)*278/50)
    d.line((47,441,325,441),fill=INK,width=2)
    for v in range(35,86,10):
        x=X(v)
        d.line((x,241,x,448),fill=GRAY,width=1)
        words(d,(x,464),str(v),13,INK,'mm')
    if t>=2.8:
        d.rectangle((X(52),249,X(69),423),fill=PALE)
    for i,(v,lo,hi) in enumerate(lines):
        y=283+i*101
        d.line((X(v+(lo-v)*reveal),y,X(v+(hi-v)*reveal),y),fill=GREEN,width=5)
        d.ellipse((X(v)-7,y-7,X(v)+7,y+7),fill=ORANGE)
        small(d,(22,y-25),f'Group {i+1} · {v}')
    conclusion(d,'Shared range: 52–69' if t>=2.8 else 'Practice estimates / percent')
    return frame


def outlier(t):
    frame,d=stage(('One row changes', 'the average.'))
    source=(120,12,13,10,15)
    ordered=sorted(source) if t>=1.6 else list(source)
    d.line((39,448,327,448),fill=RULE,width=2)
    for i,v in enumerate(ordered):
        x=41+i*57
        y=448-2*v
        d.rectangle((x,y,x+39,448),fill=ORANGE if v==120 else GREEN)
        words(d,(x+19,y-13),str(v),14,INK,'mm')
    small(d,(23,479),'All 5 rows · total 170')
    conclusion(d,'Mean 34   |   Median 13' if t>=2.8 else 'Sort the rows; keep all five')
    return frame


def axis_caption(t):
    frame,d=stage(('Keep the units', 'in the picture.'))
    card(d,(20,176,340,490))
    axes(d,(59,245,315,431),(0,2,4,6,8),'Minutes')
    vals=[2,3,5,6]
    points=[(62+82*i,431-23*v) for i,v in enumerate(vals)]
    p=progress(t,2.7,4.6)*3 if t>=2.7 else 3
    i=min(2,int(p))
    end=tuple(a+(b-a)*(p-i) for a,b in zip(points[i],points[i+1]))
    d.line([*points[:i+1],end],fill=GREEN,width=4)
    if t<.95:
        chip(d,(25,216),'Time per check',INK,PAPER,18)
    else:
        chip(d,(174,185),'Time per check',INK,PAPER,15)
    small(d,(70,463),'Source: original sample timings')
    conclusion(d,'Axis and source visible together' if t>=2.7 else 'Move the caption off the axis')
    return frame


def gap_dates(t):
    frame,d=stage(('That line crosses', 'missing dates.'))
    card(d,(18,164,341,484))
    axes(d,(49,226,319,425),(0,10,20,30),'Entries per day')
    P=[(64,385),(115,345),(260,310),(307,274)]
    for label,x in zip(('1','2','3','4','5','6'),(64,115,164,211,260,307)):
        words(d,(x,446),label,13,INK,'mm')
    if t < .95:
        d.line(P,fill=BLUE,width=3)
    else:
        d.rectangle((149,240,224,424),fill='#edddc8')
        words(d,(187,390),'No data',13,RED,'mm')
        if t>=2.7:
            d.line((260,316,260,424),fill=GREEN,width=2)
        d.line(P[:2],fill=BLUE,width=3)
        d.line(P[2:],fill=BLUE,width=3)
    for x,y in P:
        d.ellipse((x-5,y-5,x+5,y+5),fill=GREEN)
    conclusion(d,'Four observations / no estimate')
    return frame


def axes_match(t):
    frame,d=stage(('Same data,', 'same scale.'))
    for i,y in enumerate((168,344)):
        pad=(20,y,341,y+150)
        card(d,pad)
        zoom=i==1 and t<1.9
        low,high=(18,25) if zoom else (0,30)
        words(d,(30,y+20),('Export A','Export B')[i],16,INK)
        words(d,(327,y+20),f'{low}–{high} min',15,RED if zoom else GREEN,'rm')
        pts=[(58+80*j,y+125-round((v-low)*90/(high-low))) for j,v in enumerate((19,22,24,23))]
        d.line((48,y+39,48,y+126,305,y+126),fill=RULE,width=2)
        end=round(3*progress(t,2.7,4.1))+1 if t>=2.7 else 4
        points=pts[:end]
        if len(points)>1:
            d.line(points,fill=BLUE,width=3)
        for px,py in points:
            d.ellipse((px-4,py-4,px+4,py+4),fill=GREEN)
    conclusion(d,'Same 4 values: 19 · 22 · 24 · 23')
    return frame


def survey(t):
    frame,d=stage(('How many', 'people answered?'))
    p=progress(t,0,.58)
    words(d,(180,241),f'{round(70*p)}%',84,BLUE,'mm')
    if t>=.95:
        small(d,(38,302),'“Would you keep the second cut?”')
        words(d,(180,346),'14 of 20 sample responses',21,INK,'mm')
    if t>=2.7:
        for i in range(20):
            x=44+(i%10)*30
            y=405+(i//10)*34
            d.ellipse((x-9,y-9,x+9,y+9),fill=GREEN if i<14 else GRAY,outline=RULE)
        small(d,(25,484),'14 keep · 6 change')
    conclusion(d,'Illustrative survey')
    return frame


def reason_before_rule(t):
    frame,d=stage(('One number', 'before the rule.'))
    card(d,(19,193,343,468))
    if t<.95:
        for i,s in enumerate(('For a frame-based conversion,','multiply the duration by the','frame rate, accounting for','units and the cutoff frame.')):
            small(d,(36,240+i*38),s)
    else:
        words(d,(180,265),'2 seconds',38,INK,'mm')
        words(d,(180,328),'× 30 frames/second',24,BLUE,'mm')
        d.line((51,359,315,359),fill=RULE,width=2)
        if t>=2.7:
            words(d,(180,410),'60 frames',42,GREEN,'mm')
    conclusion(d,'Duration × frame rate')
    return frame


def qualified_sentence(t):
    frame,d=stage(('Read the line', 'below the fold.'))
    page=Image.new('RGB',(306,340), '#fffcf2')
    paper=ImageDraw.Draw(page)
    words(paper,(17,50),'PRACTICE NOTICE',14,GREEN)
    words(paper,(17,120),'You may film the rehearsal',22,INK)
    words(paper,(17,267),'if every performer opts in.',22,BLUE)
    paper.line((17,284,268,284),fill=BLUE,width=2)
    y0=round(115*ease(progress(t,1.2,2.46)))
    frame.paste(page.crop((0,y0,306,y0+216)),(27,174))
    if t>=2.8:
        chip(d,(20,422),'Full line',GREEN,PAPER,14)
        small(d,(24,480),'“You may film the rehearsal')
        small(d,(24,505),'if every performer opts in.”')
    return frame


def duplicate_score(t):
    frame,d=stage(('One answer', 'was counted twice.'))
    duplicate = t<2.05
    rows=[('04.1','Question 1 / correct'),('08.2','Question 2 / correct')]
    if duplicate:
        rows.append(('08.2','Question 2 / correct'))
    for i,(time,line) in enumerate(rows):
        y=190+i*63
        card(d,(20,y,337,y+50))
        words(d,(32,y+25),time,16,RED if i==2 else RULE)
        words(d,(103,y+25),line,17,INK)
        if i==2 and t>=1.05:
            d.rounded_rectangle((22,y+1,335,y+48),6,outline=RED,width=3)
    words(d,(26,437),'Score',21,INK)
    words(d,(311,438),f'{len(rows)} / 3',44,RED if duplicate else GREEN,'rm')
    if t >= 2.55:
        small(d,(27,477),'Other editor: 2 points')
        conclusion(d,'Tie-break required / 2 is a tie')
    return frame


def direction(t):
    frame,d=stage(('The arrow', 'points backwards.'))
    card(d,(19,168,342,473))
    d.rectangle((37,271,322,377),fill=PALE)
    for i,x in enumerate((68,180,292)):
        d.line((x,273,x,375),fill=RULE,width=1)
        words(d,(x,409),('Feed','Guide','Exit')[i],15,INK,'mm')
    reverse=t<1.65
    d.line((83,244,277,244),fill=RED if reverse else GREEN,width=4)
    x=83 if reverse else 277
    s=16 if reverse else -16
    d.polygon(((x,244),(x+s,234),(x+s,254)),fill=RED if reverse else GREEN)
    q=progress(t,2.55,4.55)
    x=68+224*q
    d.rounded_rectangle((x-18,309,x+18,345),5,fill=ORANGE,outline=INK,width=2)
    if t>=2.55:
        conclusion(d,'Motion now follows feed → exit')
    return frame


def convert_axis(t):
    frame,d=stage(('Same duration,', 'two source units.'))
    card(d,(20,185,338,478))
    fixed=t>=1.9
    for i,(source,val) in enumerate((('Camera A','32 s'),('Camera B','0.75 min'))):
        y=225+i*118
        words(d,(33,y),source,18,INK)
        words(d,(316,y),('32 s','45 s')[i] if fixed else val,23,BLUE,'rm')
        length=(147,204)[i] if fixed else (147,17)[i]
        d.rounded_rectangle((33,y+26,33+length,y+54),4,fill=GREEN if i==0 else ORANGE)
    if t>=2.55:
        small(d,(33,440),'0.75 min × 60 s/min = 45 s')
    conclusion(d,'Camera B runs 13 s longer' if fixed else 'Original axes use mixed units')
    return frame


SCENES={}
for family, entries in (
    ('live-contradiction',{64:zoom_points,68:blank_mean,72:price_per_gram,73:growth,75:qualified_sentence,77:interval,80:outlier}),
    ('specific-fix',{18:axis_caption,71:gap_dates,74:reason_before_rule,77:axes_match,83:survey}),
    ('turning-point',{31:convert_axis,32:direction,36:duplicate_score}),
):
    SCENES.update({f'hook-short-{family}-{n:03}':scene for n,scene in entries.items()})
POSTERS={key:.61 for key in SCENES}
