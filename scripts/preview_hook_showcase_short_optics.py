"""Original, continuously animated demonstrations of specific visual contradictions."""
from math import cos, radians, sin

from PIL import Image, ImageDraw

from preview_common import ease, progress
from preview_hook_showcase_editing import GOLD, INK, MINT, PAPER, PORTRAIT, chip, words
from preview_plates import shot

GREEN = '#2e715f'
RED = '#a74831'
GRAY = '#c8cabd'
RULE = '#64786d'


def stage(question):
    frame = Image.new('RGB', PORTRAIT, PAPER)
    draw = ImageDraw.Draw(frame)
    for x in range(18, 344, 27):
        draw.line((x, 146, x, 498), fill='#e5e1d3')
    for y in range(147, 499, 27):
        draw.line((18, y, 342, y), fill='#e5e1d3')
    for i, line in enumerate(question):
        words(draw, (20, 67 + 36 * i), line, 30, INK)
    return frame, draw


def ruler(draw, x, y, length, divisions=10, stride=2):
    draw.rounded_rectangle((x, y, x + length + 12, y + 27), 4, fill='#dce9da', outline=RULE)
    for i in range(divisions + 1):
        u = x + 6 + round(i * length / divisions)
        draw.line((u, y + 2, u, y + (13 if i % stride == 0 else 8)), fill=GREEN, width=1)
        if i % stride == 0:
            words(draw, (u, y + 20), str(i), 9, INK, 'mm')


def arrows(t):
    frame, d = stage(('Which bar is', 'longer?'))
    for y, direction in ((240, 1), (386, -1)):
        d.line((83, y, 277, y), fill=INK, width=6)
        if t < 2.8:
            for x, side in ((83, direction), (277, -direction)):
                d.line(((x + side * 45, y - 27), (x, y), (x + side * 45, y + 27)), fill=RED, width=4)
        if t >= 1.2:
            ry = y - 30 - round(50 * (1 - ease(progress(t, 1.2, 1.9))))
            ruler(d, 77, ry, 194)
            if t >= 1.9:
                for x in (83, 277):
                    d.line((x, ry + 14, x, y + 12), fill=GREEN, width=2)
    if t >= 2.8:
        chip(d, (20, 528), 'Same 0–10 span', INK, MINT, 18)
    return frame


def white_card(t):
    frame, d = stage(('Is the card', 'actually blue?'))
    d.rounded_rectangle((17, 172, 343, 479), 8, fill='#425a84')
    d.polygon(((232, 172), (343, 172), (343, 479), (151, 479)), fill='#d4c9ab')
    motion = ease(progress(t, 1.2, 2.73))
    x, y = 30 + round(184 * motion), 242 + round(21 * motion)
    for i in range(104):
        u = x + i
        left_edge = 232 - (y - 172) * 81 / 307
        right_edge = 232 - (y + 132 - 172) * 81 / 307
        edge = min(y + 132, max(y, y + 132 * (left_edge - u) / (left_edge - right_edge)))
        d.line((u, y, u, edge), fill='#a7b7d4')
        if edge < y + 132:
            d.line((u, edge, u, y + 132), fill='#f7f1dd')
    d.rectangle((x, y, x + 104, y + 132), outline=INK, width=2)
    if t >= 2.8:
        d.rectangle((242, 410, 286, 453), fill='#f7f1dd', outline=INK, width=2)
        words(d, (235, 437), 'Reference', 12, INK, 'rm')
    chip(d, (20, 520), 'Lighting model / card stays in view', INK, MINT, 14)
    return frame


SHAPE = ((-49, -38), (42, -38), (42, -10), (8, -10), (8, 40), (-49, 40))


def shape_points(cx, cy, angle):
    c, s = cos(radians(angle)), sin(radians(angle))
    return [(round(cx + x * c - y * s), round(cy + x * s + y * c)) for x, y in SHAPE]


def turn_shape(t):
    frame, d = stage(('Will one cutout', 'fit both?'))
    for cy, angle in ((240, 0), (405, 118)):
        edge = shape_points(179, cy, angle)
        d.line(edge + [edge[0]], fill=GREEN, width=4, joint='curve')
        d.ellipse((173, cy-6, 185, cy+6), outline=RULE, width=1)
    p = ease(progress(t, 1.2, 2.8))
    edge = shape_points(179 + 6*sin(p*3.14), 240 + 165*p, 118*p)
    d.polygon(edge, fill='#d8805d', outline=INK, width=2)
    if t >= 2.8:
        d.line(edge + [edge[0]], fill='#185f4d', width=3, joint='curve')
        chip(d, (20, 527), 'One cutout / one continuous turn', INK, MINT, 15)
    return frame


def circles(t):
    frame, d = stage(('Which center', 'looks bigger?'))
    y = 323
    p = ease(progress(t, 1.2, 2.73))
    for i, x in enumerate((92, 268)):
        surrounding = 16 if i == 0 else 29
        for j in range(6 if t < 2.8 else 0):
            angle = radians(j * 60)
            u = x + (43 + 138*p) * cos(angle)
            v = y + (43 + 138*p) * sin(angle)
            d.ellipse((u-surrounding, v-surrounding, u+surrounding, v+surrounding), fill='#608979')
        d.ellipse((x-19, y-19, x+19, y+19), fill=RED)
    if t >= 2.8:
        d.line((22, y, 338, y), fill=RULE, width=1)
        for x in (92, 268):
            for offset in (-19, 19):
                d.line((x+offset, y-27, x+offset, y+33), fill=INK, width=2)
            words(d, (x, y+62), '38 px', 20, INK, 'mm')
    return frame


def straightedge(t):
    frame, d = stage(('Does the strip', 'actually bend?'))
    p = ease(progress(t, 2.8, 4.0))
    hatch = Image.new('RGBA', (326, 240))
    marks = ImageDraw.Draw(hatch)
    for i, u in enumerate(range(26, 302, 21)):
        side = -1 if i % 2 else 1
        move = round(p * 327)
        marks.line((u - side*40 + move, 0, u + side*40 + move, 239), fill='#94a889', width=3)
    frame.paste(hatch, (18, 205), hatch)
    d.line((35, 327, 325, 327), fill=RED, width=4)
    if t >= 1.2:
        y = 329 + round(98*(1-ease(progress(t, 1.2, 2.2))))
        ruler(d, 29, y, 291)
        if t >= 2.8:
            d.line((34, 327, 326, 327), fill=GREEN, width=2)
            chip(d, (20, 527), 'One edge, all the way across', INK, MINT, 16)
    return frame


def two_faces(t):
    frame, d = stage(('Find a face', 'in the gap.'))
    contour = [(119, 177), (134, 211), (133, 245), (146, 263), (160, 291), (144, 302),
               (145, 320), (154, 330), (138, 340), (149, 351), (138, 378), (122, 394), (121, 422), (152, 473)]
    mirror = [(360-x, y) for x, y in contour]
    d.polygon([(24, 177), *contour, (24, 473)], fill='#365749')
    d.polygon([(336, 177), *mirror, (336, 473)], fill='#365749')
    p = progress(t, 1.2, 2.48)
    if 1.2 <= t < 4.85:
        portion = max(2, round(len(contour) * (p if t < 2.8 else ease(progress(t, 2.8, 3.97)))))
        d.line((contour if t < 2.8 else mirror)[:portion], fill=RED if t < 2.8 else GOLD, width=4)
    if t >= 2.8:
        chip(d, (20, 523), 'Same edge / opposite reading', INK, MINT, 16)
    return frame


def motion_context(t):
    frame, d = stage(('Which way is', 'the dot moving?'))
    d.rounded_rectangle((22, 230, 338, 420), 7, fill='#dce5d6', outline=RULE)
    shift = round(min(t, 1.2) * 117)
    for i in range(-5, 15):
        x = 25 + i * 31 + shift
        if 27 <= x <= 333:
            d.line((x, 235, x, 405), fill='#9bac9f', width=5)
    x = round(50 + 48*t)
    d.ellipse((x-12, 306, x+12, 330), fill=RED)
    d.line((34, 381, 330, 381), fill=INK, width=2)
    for u in range(50, 330, 24):
        d.line((u, 380, u, 389), fill=INK)
    if t >= 2.8:
        for k, u in enumerate((74, 122, 170, 218)):
            if u < x-10:
                d.ellipse((u-4, 349, u+4, 357), fill=GREEN)
                words(d, (u, 370), f'{.5+k:g}s', 10, INK, 'mm')
    chip(d, (20, 511), 'Background stopped' if t >= 1.2 else 'Follow the dot against the ruler', INK, MINT, 16)
    return frame


def speed_compare(t):
    frame, d = stage(('Which walker', 'moves faster?'))
    if t < 1.2:
        source_time = .76*t
    elif t < 2.8:
        source_time = .92
    else:
        source_time = min(1.8,.92+.76*(t-2.8))
    for i, label in enumerate(('Continuous', 'Reframed cuts')):
        y = 145 + i*168
        tight = i == 1 and (int(source_time*9) % 3 != 0)
        frame.paste(shot('steps-live', source_time, 1.34 if tight else 1, 16 if tight else 0, 0, (316, 136)), (22, y))
        chip(d, (29, y+7), label, INK, PAPER, 13)
        d.line((27, y+144, 329, y+144), fill=RULE, width=2)
        x = 27 + round(302 * min(1, source_time/1.8))
        d.line((x, y+136, x, y+150), fill=RED, width=2)
    chip(d, (20, 520), f'Same source frame / {source_time:.2f} s', INK, MINT, 16)
    return frame


def drop_tokens(t):
    frame, d = stage(('Which piece', 'lands first?'))
    d.rectangle((24, 446, 336, 471), fill=GREEN)
    d.line((40, 197, 320, 197), fill=INK, width=4)
    p = progress(t, 1.38, 2.02)
    distance = 249 * p*p
    for x, size in ((106, 29), (254, 44)):
        bottom = 197 + distance
        d.ellipse((x-size, bottom-2*size, x+size, bottom), fill=('#c57051' if size==29 else '#648b72'), outline=INK, width=2)
    if t >= 2.8:
        d.line((31, 445, 328, 445), fill=GOLD, width=3)
        words(d, (180, 492), 'Same contact frame', 20, GREEN, 'mm')
    chip(d, (20, 535), 'Illustrative model / both 20 g', INK, MINT, 16)
    return frame


def bottle_level(t):
    frame, d = stage(('Does the cap', 'move the level?'))
    d.line((33, 331, 331, 331), fill=RED, width=2)
    bottle = Image.new('RGBA', (155, 292))
    r = ImageDraw.Draw(bottle)
    outline = [(20,264),(20,83),(50,54),(57,20),(99,20),(107,55),(136,83),(136,264)]
    r.polygon(outline, fill='#e0e9dc', outline=INK, width=3)
    if t < 2.8:
        r.rectangle((22, 160, 134, 262), fill='#85acb9')
    else:
        angle = 23 * ease(progress(t, 2.8, 3.64))
        offset = round(112*sin(radians(angle))/cos(radians(angle)))
        r.polygon(((22,179-offset//2),(134,179+offset//2),(134,262),(22,262)), fill='#85acb9')
        bottle = bottle.rotate(angle, resample=Image.Resampling.BICUBIC)
    frame.paste(bottle, (104, 171), bottle)
    if t < 2.8:
        p=ease(progress(t,1.2,2.05))
        x,y=155+round(99*p),179-round(38*p)
        d.rounded_rectangle((x,y,x+49,y+17),3,fill=GREEN)
        d.line((34,331,105,331),fill=RED,width=2)
    chip(d, (20, 529), 'Tilt control' if t >= 2.8 else 'Liquid matches the fixed mark', INK, MINT, 16)
    return frame


def mats(t):
    frame, d = stage(('Same release,', 'same stop?'))
    p = progress(t, 1.2, 2.8)
    for i, y in enumerate((255, 401)):
        d.rounded_rectangle((22, y-31, 339, y+30), 5, fill='#e3e9de', outline=RULE)
        d.rectangle((145, y-29, 331, y+28), fill=('#ac9b79','#4f7564')[i])
        d.line((57,y-30,57,y+30),fill=INK,width=3)
        end = (292,221)[i]
        px = 57 + round((end-57)*sin(min(1,p*(1+i*.28))*1.570796))
        d.ellipse((px-15,y-15,px+15,y+15),fill=RED,outline=PAPER,width=2)
        if t>=2.8:
            d.line((end,y-33,end,y+34),fill=GOLD,width=2)
            words(d,(27,y+50),('Smooth mat','Textured mat')[i],18,INK)
    chip(d,(20,535),'Illustrative model / gate at left',INK,MINT,15)
    return frame


def tape_zero(t):
    frame,d = stage(('Where is', 'the real zero?'))
    p=ease(progress(t,1.2,2.8))
    for i,y in enumerate((217,369)):
        x=41 if i==0 else round(29+12*p)
        d.rounded_rectangle((47,y-54,216,y-4),5,fill=GREEN)
        ruler(d,x,y,210)
        if t>=2.8:
            for u in (47,216):
                d.line((u,y-5,u,y+25),fill=RED,width=2)
    chip(d,(20,531),'Both start at printed zero' if t>=2.8 else 'Line up the printed marks',INK,MINT,15)
    return frame


SCENES = {
    f'hook-short-live-contradiction-{index:03}': scene for index, scene in {
        2: arrows, 3:white_card, 4:turn_shape, 5:circles, 6:straightedge, 7:two_faces,
        10:motion_context, 16:speed_compare, 21:drop_tokens, 27:bottle_level, 28:mats, 100:tape_zero,
    }.items()
}
POSTERS = {key: .42 for key in SCENES}
