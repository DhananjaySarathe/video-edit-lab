"""Widescreen A/B edits. Both versions use the same source at the same elapsed time."""
from PIL import Image, ImageDraw

from preview_common import H, W, ease, font, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, chip, words
from preview_plates import shot

SURFACE = '#e5e9dc'
RULE = '#a6b4a8'
GREEN = '#306650'
BLUE = '#315f87'
ORANGE = '#a34e32'
DARK = '#192c25'
PANEL_X = (20, 330)
PANEL_Y = 66
PANEL_SIZE = (290, 208)


def desk(heading, footer, *, worked_label='Original practice comparison'):
    frame = Image.new('RGB', (W,H), SURFACE)
    draw = ImageDraw.Draw(frame)
    words(draw, (20,28),heading,26,INK)
    for x in PANEL_X:
        draw.rounded_rectangle((x,59,x+290,279),7,fill=PAPER,outline=RULE,width=2)
    words(draw,(20,306),footer,17,INK)
    words(draw,(20,334),worked_label,13,GREEN,weight='regular')
    return frame,draw


def caption(draw,x,y,txt,color=INK):
    words(draw,(x,y),txt,16,color,weight='regular')


def caption_before(t):
    source_at = .7 if 6.1<=t<14.8 else .25 + (t%3.1)*.73
    footer = ('Watch the hand reach the dial.' if t<6.1 else 'Paused on the same source frame.'
              if t<14.8 else 'Early cue: 0.30–1.00 s. Late cue: 1.53–2.23 s.')
    frame,d=desk('Does the caption spoil the reveal?',footer)
    for i,x in enumerate(PANEL_X):
        frame.paste(shot('camera-live',source_at,1.06,-3,-1,(290,174)),(x,68))
        visible = (.3<=source_at<=1.0) if i==0 else (1.53<=source_at<=2.23)
        if visible:
            chip(d,(x+13,187),'The dial clicks into place',INK,PAPER,14)
        words(d,(x+10,259),('A / Caption first','B / Action first')[i],16,INK)
        if t>=14.8:
            timeline=x+65+round(190*min(source_at,2.45)/2.45)
            d.line((x+65,222,x+255,222),fill=PAPER,width=3)
            d.line((timeline,211,timeline,231),fill=GOLD,width=2)
    return frame


def replay_or_freeze(t):
    frame,d=desk('Which replay tells you where contact starts?',
                 'Same dial. Same source moment.' if t<14.8 else 'Ask viewers to point to the first contact.')
    stamp=.65 if 6.1<=t<14.8 else .25+min(1.2,t%3.3*.32)
    for i,x in enumerate(PANEL_X):
        at=stamp if i==0 else .65
        frame.paste(shot('camera-live',at,1.17,0,0,(290,174)),(x,68))
        words(d,(x+10,259),('Slow replay','One freeze')[i],16,INK)
        if i or 6.1<=t<14.8:
            center=(x+174,158)
            d.ellipse((center[0]-20,center[1]-20,center[0]+20,center[1]+20),outline=GOLD,width=3)
            d.line((x+245,114,*center),fill=GOLD,width=2)
        if t>=14.8:
            chip(d,(x+8,72),'3.3 s to inspect',INK,PAPER,12)
    return frame


def plot(d,x,qualifier,expanded):
    p=((x+33,212),(x+92,190),(x+153,166),(x+214,126),(x+250,138))
    for y in range(110,220,25):
        d.line((x+20,y,x+271,y),fill=RULE)
    d.line(p,fill=BLUE,width=4)
    d.ellipse((p[3][0]-6,p[3][1]-6,p[3][0]+6,p[3][1]+6),fill=ORANGE)
    word_x, word_y = (x+27,248) if qualifier==0 else (x+60,100)
    if qualifier:
        d.line((x+212,103,x+212,124),fill=ORANGE,width=2)
    chip(d,(word_x,word_y),'8 of the 10 teams replied',GREEN if expanded else INK,PAPER,13)


def qualifier_at_point(t):
    frame,d=desk('Where will readers notice the caveat?',
                 'Same chart and wording in both versions.' if t<14.8 else 'Ask how many replied before naming the peak.')
    for i,x in enumerate(PANEL_X):
        words(d,(x+10,78),('A / Source note','B / On the measured point')[i],16,INK)
        plot(d,x,i,6.1<=t<14.8)
    return frame


TABLE=(('Studio',18,25),('Workshop',12,28),('Gallery',21,20))


def numbers_table(t):
    frame,d=desk('Which layout finds the workshop difference?',
                 'Which two counts belong to the Workshop?' if t<14.8 else 'Practice answer: 28 − 12 = 16 visits.')
    for i,x in enumerate(PANEL_X):
        words(d,(x+10,79),('A / Table','B / Grouped bars')[i],16,INK)
        caption(d,x+147,105,'Mon',GREEN)
        caption(d,x+208,105,'Tue',ORANGE)
        for j,(name,a,b) in enumerate(TABLE):
            y=143+55*j
            if j==1 and t>=6.1:
                d.rounded_rectangle((x+6,y-22,x+283,y+22),4,fill='#e0ebd8')
            caption(d,x+13,y,name)
            if i==0:
                caption(d,x+158,y,str(a),GREEN)
                caption(d,x+221,y,str(b),ORANGE)
            else:
                for k,(val,color) in enumerate(((a,GREEN),(b,ORANGE))):
                    top=y-10+12*k
                    right=x+110+4.5*val
                    d.rectangle((x+110,top,right,top+8),fill=color)
                    words(d,(right+7,top+4),str(val),11,INK)
    return frame


def poster_hierarchy(t):
    frame,d=desk('At a glance, when is the open studio?',
                 'Same wording, size, contrast and viewing distance.' if t<14.8 else 'Record time and date recall with each poster.')
    for i,x in enumerate(PANEL_X):
        shot_width=round(202-40*ease(progress(t,14.8,18)))
        y=74
        left=x+(290-shot_width)//2
        d.rounded_rectangle((left,y,left+shot_width,271),2,fill='#204233')
        labels=('OPEN STUDIO','SATURDAY','12 OCTOBER','10 AM–4 PM')
        for j,label in enumerate(labels):
            size=20 if i==0 else (18,13,25,13)[j]
            size-=round(3*ease(progress(t,14.8,18)))
            words(d,(x+145,106+43*j),label,size,PAPER,'mm')
        if t>=6.1 and t<14.8:
            d.line((left+14,210,left+shot_width-14,210),fill=GOLD,width=3)
    return frame


def second_place(t):
    frame,d=desk('When did Alder move into second?',
                 'Same three dated readings. No inferred crossover date.' if t>=6.1 else 'Read second place from both views.')
    when=0 if t<2 else 1 if t<4 else 2
    if 6.1<=t<14.8: when=1
    if t>=14.8: when=min(2,int((t-14.8)//2.4))
    values=((38,16,20),(40,25,22),(43,29,23))
    names=('Elm','Alder','Birch')
    colors=(GREEN,ORANGE,BLUE)
    order=sorted(range(len(names)),key=lambda i:values[when][i],reverse=True)
    for mode,x in enumerate(PANEL_X):
        words(d,(x+13,77),('A / Moving bars','B / Ranked table')[mode],16,INK)
        words(d,(x+268,109),f'July {8+when*7}',17,INK,'rm')
        for j,i in enumerate(order):
            y=139+49*j
            v=values[when][i]
            if mode:
                if j==1 and t>=6.1:
                    d.rectangle((x+9,y-16,x+276,y+15),fill='#ede1cb')
                caption(d,x+16,y,f'{j+1}. {names[i]}')
                words(d,(x+265,y),str(v),17,colors[i],'rm')
            else:
                row=v
                if (t<6.1 or t>=14.8) and when>0:
                    local=(t-(14.8 if t>=14.8 else 0))-(2.4*when if t>=14.8 else when*2)
                    p=ease(progress(local,0,.6))
                    row=values[when-1][i]+(v-values[when-1][i])*p
                r=x+78+round(row*4.15)
                d.rectangle((x+77,y-12,r,y+12),fill=colors[i])
                caption(d,x+12,y,names[i])
                words(d,(r+8,y),str(v),13,INK)
    return frame


def place_title(t):
    frame,d=desk('Where can the title sit during the first line?',
                 'Same title, frame size and elapsed reading time.' if t<14.8 else 'Check recall of the title and of the expression.')
    at=.28+min(2.3,t%3*.79) if t<6.1 or t>=14.8 else 1.38
    frame.paste(shot('host-live',at,1.06,-44,-15,(290,174)),(PANEL_X[1],68))
    x=PANEL_X[0]
    title_visible = t % 5 < 2.5 or 6.1 <= t < 14.8
    if title_visible:
        d.rectangle((x,68,x+290,242),fill=DARK)
        words(d,(x+145,155),'The workshop',26,PAPER,'mm')
    else:
        frame.paste(shot('host-live',at,1.06,-44,-15,(290,174)),(x,68))
    if title_visible:
        chip(d,(PANEL_X[1]+151,193),'The workshop',INK,PAPER,15)
    for i,x in enumerate(PANEL_X):
        words(d,(x+12,259),('Separate title','In-scene title')[i],16,INK)
    return frame


def paint_parallax(draw, x, position, tracking, show):
    r=290
    if tracking:
        camera_shift = 53 * position
        far = x + 217 - .35 * camera_shift
        near = x + 93 - .92 * camera_shift
        near_half = 16 + 5 * position
        far_half = 28 + 2 * position
    else:
        zoom = 1 + .31 * position
        pan = 26 * position
        far = x + 145 + (217 - 145) * zoom - pan
        near = x + 145 + (93 - 145) * zoom - pan
        near_half = 16 * zoom
        far_half = 28 * zoom
    draw.rectangle((x,68,x+r,238),fill='#d0d9c9')
    draw.rectangle((x,209,x+r,238),fill='#ccbd9d')
    for i in range(6):
        xx = far - 192 + 45 * i
        if x <= xx <= x + r:
            draw.line((xx,87,xx,211),fill='#a8b9a8')
    draw.rectangle((far-far_half,108,far+far_half,208),fill='#7c9885',outline=INK,width=2)
    draw.rectangle((near-near_half,88,near+near_half,235),fill='#9b6549',outline=INK,width=2)
    if show:
        for u,label in ((near,'Near'),(far,'Far')):
            draw.line((u,111,u,215),fill=GOLD,width=2)
            words(draw,(u,225),label,13,PAPER,'mm')


def compare_parallax(t,predict=False):
    start,end=(6.5,15.5) if predict else (6.1,14.8)
    p=0 if predict and t<end else ease(progress(t,end if t>=end else 0,end+4.8 if t>=end else 4.8))
    if not predict and start<=t<end:
        p=.68
    header='Which move shifts the distant landmark?'
    footer='Pick before the movement.' if predict and t<end else 'Compare the near and far edges through the same duration.'
    frame,d=desk(header,footer,worked_label='Original animated camera and crop models')
    for i,x in enumerate(PANEL_X):
        paint_parallax(d,x,p,i==0,t>=start)
        words(d,(x+9,258),('Camera translates','Digital crop')[i],16,INK)
    return frame


def agenda(t):
    frame,d=desk('Which two rehearsals share the room?',
                 'Both schedules use the same practice entries and local time.' if t<14.8 else '15:30–16:00 overlaps for 30 minutes.')
    x=20
    for i,label in enumerate(('14:00','15:00','16:00','17:00')):
        y=118+45*i
        d.line((x+57,y,x+273,y),fill=RULE,width=1)
        caption(d,x+8,y,label)
    for x0,y0,y1,text,col in ((90,164,209,'Piano',GREEN),(195,187,232,'Strings',BLUE)):
        d.rounded_rectangle((x0,y0,x0+79,y1),4,fill=col)
        words(d,(x0+7,y0+12),text,12,PAPER)
    for i,(time,name,end) in enumerate((('15:00','Piano','16:00'),('15:30','Strings','16:30'))):
        y=136+55*i
        d.line((345,y+18,606,y+18),fill=RULE)
        words(d,(354,y),time,15,INK)
        caption(d,421,y,name)
        words(d,(577,y),end,15,INK,'rm')
    if t>=6.1:
        d.line((175,187,175,209),fill=ORANGE,width=3)
        d.rectangle((342,117,613,211),outline=ORANGE,width=2)
    for x, label in zip(PANEL_X,('Week grid','Agenda')):
        words(d,(x+10,82),label,19,INK)
    return frame


SCENES={f'hook-long-head-to-head-{i:03}':scene for i,scene in {
    4:caption_before,10:replay_or_freeze,22:qualifier_at_point,23:numbers_table,
    25:poster_hierarchy,27:second_place,29:place_title,35:compare_parallax,49:agenda,
}.items()}
def prediction_parallax(t):
    return compare_parallax(t, predict=True)
SCENES['hook-long-prediction-017']=prediction_parallax
POSTERS={key:4.1 for key in SCENES}
