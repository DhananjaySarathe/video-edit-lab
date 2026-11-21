"""Individually directed 9:16 examples for five Shorts openings."""
from array import array
from functools import lru_cache, partial
from math import cos, pi, sin
import sys
import wave

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from preview_common import ease, font, progress
from preview_live_action import GOLD, INK, PAPER, type_at
from preview_plates import shot, source
from preview_sound import RATE, impact
from preview_spatial import warp

SIZE = (360, 640)
MINT = '#bdebc3'
DARK = '#17231f'


def label(frame, words, x, y, size=20, accent=None):
    draw = ImageDraw.Draw(frame, 'RGBA')
    width = draw.textlength(words, font=font(size))
    draw.rounded_rectangle((x, y, x+width+24, y+size+15), 7,
                           fill=accent or (13, 25, 22, 236))
    type_at(frame, (x+12, y+(size+15)/2), words, size, INK if accent else PAPER, 'lm')


def heading(frame, lines, y=98, size=35):
    for line in lines:
        type_at(frame, (22, y), line, size, anchor='lm', stroke=1)
        y += size+5


def crop_to(frame, bounds, size=SIZE):
    return frame.transform(size, Image.Transform.EXTENT, bounds, Image.Resampling.BICUBIC)


@lru_cache(maxsize=2)
def worktop(tone):
    # Sample the existing licensed still as a photograph-backed tabletop texture.
    table = source('coffee', 0)
    w, h = table.size
    sample = table.crop((round(w*.78), round(h*.66), w, h))
    table = ImageOps.fit(sample, SIZE).filter(ImageFilter.GaussianBlur(6))
    return Image.blend(table, Image.new('RGB', SIZE, tone), .62)


PIECE_AT = (88, 192)
PIECE_SIZE = (183, 247)
WINDOW = (122, 223, 239, 431)


@lru_cache(maxsize=1)
def puzzle_parts():
    board_at = (20, 134)
    board = shot('room', size=(320, 390))
    marks = ImageDraw.Draw(board, 'RGBA')
    marks.line((0, 118, 78, 118), fill=(231, 227, 189, 165), width=2)
    marks.line((261, 217, 320, 217), fill=(231, 227, 189, 165), width=2)
    marks.line((148, 0, 148, 69), fill=(231, 227, 189, 165), width=2)
    marks.line((148, 304, 148, 390), fill=(231, 227, 189, 165), width=2)

    mask = Image.new('L', PIECE_SIZE)
    cut = ImageDraw.Draw(mask)
    cut.rounded_rectangle((4, 12, 164, 229), 8, fill=255)
    cut.ellipse((137, 103, 181, 148), fill=255)
    cut.ellipse((56, 0, 101, 36), fill=255)
    cut.ellipse((62, 206, 109, 246), fill=0)
    cut.ellipse((0, 76, 26, 118), fill=0)

    frame = worktop('#3a2c24').copy()
    layout = ImageDraw.Draw(frame, 'RGBA')
    layout.rounded_rectangle((14, 131, 346, 538), 9, fill=(21, 15, 12, 123))
    frame.paste(board, board_at)
    frame.paste('#221d18', PIECE_AT, mask)
    sx, sy = PIECE_AT[0]-board_at[0], PIECE_AT[1]-board_at[1]
    tile = board.crop((sx, sy, sx+PIECE_SIZE[0], sy+PIECE_SIZE[1]))
    x0,y0,x1,y1 = (WINDOW[0]-PIECE_AT[0], WINDOW[1]-PIECE_AT[1],
                    WINDOW[2]-PIECE_AT[0], WINDOW[3]-PIECE_AT[1])
    opening = (x0, y0, x1, y1)
    frame_edge = (x0-7, y0-7, x1+7, y1+7)
    return frame, tile, mask, opening, frame_edge


def puzzle_room(t):
    if t >= 1.95:
        move = 1+.18*ease(progress(t, 1.95, 4.7))
        return shot('room', zoom=move, y=12*(move-1), size=SIZE)

    base, tile, mask, opening, frame_edge = puzzle_parts()
    tile = tile.copy()
    draw = ImageDraw.Draw(tile)
    draw.rectangle(frame_edge, fill='#48382b', outline='#d1ae7e', width=2)
    target = shot('room', size=(opening[2]-opening[0], opening[3]-opening[1]))
    tile.paste(target, opening[:2])
    pivot = ease(progress(t, .67, 1.20))
    x,y,right,bottom = opening
    pane_edge = round(right-(right-x)*pivot)
    if pane_edge > x+2:
        draw.polygon(((x, y), (pane_edge, y+15*pivot),
                      (pane_edge, bottom-14*pivot), (x, bottom)), fill='#342c25')
        draw.line((pane_edge, y+15*pivot, pane_edge, bottom-14*pivot), fill='#c19e68', width=3)
    frame = base.copy()
    offset = round(-150*(1-ease(progress(t, -.12, .64))))
    frame.paste(tile, (PIECE_AT[0], PIECE_AT[1]+offset), mask)
    if t < .65:
        heading(frame, ('The piece opens', 'a room.'), y=62, size=29)
    move = ease(progress(t, .92, 1.95))
    extent = tuple(start+(end-start)*move for start,end in zip((0, 0, *SIZE), WINDOW))
    return crop_to(frame, extent) if move > 0 else frame


def timeline(frame, y, durations, colors, width=312):
    draw = ImageDraw.Draw(frame, 'RGBA')
    x = 24
    draw.rounded_rectangle((x-4, y-5, x+width+4, y+50), 7, fill=(8, 17, 17, 239))
    total = sum(durations)
    for amount,color in zip(durations,colors):
        length = round(amount*width/total)
        draw.rounded_rectangle((x+2, y, x+length-2, y+21), 3, fill=color)
        draw.line((x+4, y+30, x+length-4, y+30), fill=color, width=2)
        x += length


def price_panel(frame, t, y, price, rushed):
    panel = shot('coffee-live', t, zoom=1.10, x=-30, y=16, size=(312, 178))
    frame.paste(panel, (24, y))
    if price:
        label(frame, 'Single cup $6', 38, y+107, 29, GOLD)
    label(frame, 'First cut' if rushed else 'With a hold', 36, y+12, 17)


def opposing_roles(t):
    if t < .9:
        frame = shot('host-live', .63+t*.82, zoom=1.0, x=-55, size=SIZE)
        label(frame, 'Client · staged', 199, 58, 18)
        heading(frame, ('Can we make', 'this faster?'), y=380, size=34)
        timeline(frame, 494, (1, 1, 1.1, .8, .9, .8), (MINT, GOLD, MINT, GOLD, MINT, GOLD))
        return frame

    if t < 2.45:
        raw = shot('portrait-live', 2.02+(t-.9)*.58, size=SIZE)
        frame = ImageOps.mirror(raw)
        label(frame, 'Editor · staged', 19, 58, 18)
        label(frame, 'I missed the price.', 19, 293, 27)
        price_panel(frame, .59+(t-.9)*.69, 352, 1.41 <= t < 1.61, True)
        return frame

    elapsed = t-2.45
    stamp = .70+min(elapsed, 2.5)*.88
    frame = shot('coffee-live', stamp, zoom=1.08, x=-59, y=12, size=SIZE)
    label(frame, 'With a hold', 19, 58, 20)
    if .34 <= elapsed < 2.21:
        label(frame, 'Single cup $6', 24, 443, 42, GOLD)
    if elapsed >= 2.21:
        label(frame, 'Same price. More time.', 22, 455, 25)
    return frame


PHONE_REGION = (119, 0, 439, 360)


def portrait_fit(raw):
    matched = crop_to(raw, PHONE_REGION, (360, 405))
    fill = ImageOps.fit(raw, SIZE).filter(ImageFilter.GaussianBlur(21))
    frame = ImageEnhance.Brightness(fill).enhance(.62)
    frame.paste(matched, (0, 116))
    return frame


def portrait_reaction(t):
    if t < 1.1:
        raw = source('host-live', 2.53+t*.56)
        frame = portrait_fit(raw)
        label(frame, 'Staged playback', 19, 62, 19)
        heading(frame, ('My hands are', 'still in frame.'), y=437, size=32)
        return frame

    if t < 2.65:
        raw = source('host-live', .67+(t-1.1)*.55)
        frame = Image.new('RGB', SIZE, '#1b2623')
        label(frame, 'Same take', 19, 62, 20)
        heading(frame, ('The wide source',), y=151, size=28)
        left, top, width, height = 16, 211, 328, 184
        frame.paste(raw.resize((width,height), Image.Resampling.LANCZOS), (left,top))
        x0,_,x1,_ = PHONE_REGION
        draw = ImageDraw.Draw(frame, 'RGBA')
        draw.rectangle((left+width*x0/640, top+1, left+width*x1/640, top+height-2),
                       outline=GOLD, width=3)
        label(frame, 'Keep both hands inside.', 19, 448, 24)
        return frame

    stamp = 1.13+(t-2.65)*.64
    frame = portrait_fit(source('host-live', stamp))
    label(frame, '9:16 fit', 19, 62, 19, GOLD)
    if t >= 4.1:
        label(frame, 'Both hands stay visible.', 19, 508, 23)
    return frame


MAP_SIZE = (300, 370)
MAP_AT = (30, 134)
FOLD = 176
ROUTE = ((27,283), (79,267), (106,218), (140,221), (176,179),
         (212,151), (244,155), (275,119))


@lru_cache(maxsize=1)
def printed_map():
    paper = Image.new('RGB', MAP_SIZE, '#ece2c4')
    draw = ImageDraw.Draw(paper, 'RGBA')
    draw.polygon(((0,22),(104,18),(117,133),(77,185),(0,167)), fill='#c3d2a8')
    draw.polygon(((137,254),(211,198),(300,190),(300,370),(159,370)), fill='#bacda8')
    draw.line(((0,185),(49,185),(98,156),(152,158),(215,121),(250,111),(300,113)),
              fill='#91b8b3', width=13, joint='curve')
    for start in (35,82,111,155,209,262,320):
        draw.line(((0,start),(66,start+17),(135,start-13),(206,start-11),(300,start+7)),
                  fill=(119, 112, 86, 61), width=2, joint='curve')
    draw.line(ROUTE, fill='#205c68', width=6, joint='curve')
    draw.line(((103,103), (133,135), (138,170), ROUTE[4]), fill='#af6d38', width=5, joint='curve')
    for x,y in (ROUTE[0], ROUTE[4], ROUTE[-1]):
        draw.ellipse((x-5,y-5,x+5,y+5), fill='#273b2d', outline='#fbf1cc', width=2)
    type_at(paper, (19, 48), 'CREEK LOOP', 20, '#273b2d', 'lm')
    type_at(paper, (27, 311), 'Start', 17, '#273b2d', 'lm')
    type_at(paper, (213, 101), 'Lookout', 17, '#273b2d', 'lm')
    return paper


@lru_cache(maxsize=1)
def map_reverse():
    paper = Image.new('RGBA', (MAP_SIZE[0]-FOLD, MAP_SIZE[1]), '#c8b38a')
    draw = ImageDraw.Draw(paper, 'RGBA')
    for y in range(13, 365, 12):
        draw.line((3, y, paper.width-4, y-1), fill=(236, 213, 173, 93), width=1)
    return paper


def trace_route(frame, t):
    end = progress(t, 2.16, 4.50)*(len(ROUTE)-1)
    i = min(int(end), len(ROUTE)-2)
    amount = end-i
    a,b = ROUTE[i:i+2]
    tip = tuple(x+(y-x)*amount for x,y in zip(a,b))
    points = [(MAP_AT[0]+x, MAP_AT[1]+y) for x,y in (*ROUTE[:i+1], tip)]
    draw = ImageDraw.Draw(frame)
    draw.line(points, fill='#d15d3e', width=4, joint='curve')
    x,y = points[-1]
    draw.ellipse((x-6,y-6,x+6,y+6), fill='#d15d3e', outline='#fff3cc', width=2)


def map_reveal(t):
    frame = worktop('#423c2a').copy()
    x,y = MAP_AT
    w,h = MAP_SIZE
    draw = ImageDraw.Draw(frame, 'RGBA')
    amount = ease(progress(t, .78, 2.03))
    angle = (1-amount)*pi
    px = x+FOLD
    span = (w-FOLD)*cos(angle)
    lift = 19*sin(angle)
    paper = printed_map()
    draw.rectangle((x+4, y+5, max(px,px+span)+4, y+h+8), fill=(15, 17, 12, 102))
    frame.paste(paper.crop((0,0,FOLD,h)), (x,y))
    if abs(span) > 2:
        if span < 0:
            side = map_reverse()
        else:
            side = paper.crop((FOLD,0,w,h)).convert('RGBA')
        quad = ((px,y), (px+span,y+lift), (px+span,y+h-lift), (px,y+h))
        warp(frame, side, quad)
    draw.line((px, y, px, y+h), fill=(78, 59, 34, 107), width=2)
    if t < .85:
        heading(frame, ('The fold hides', 'the connection.'), y=53, size=27)
    elif t >= 2.1:
        trace_route(frame, t)
        junction = (MAP_AT[0]+ROUTE[4][0], MAP_AT[1]+ROUTE[4][1])
        draw.ellipse((junction[0]-12,junction[1]-12,junction[0]+12,junction[1]+12),
                     outline=GOLD, width=3)
        label(frame, 'Paths meet here', 24, 529, 22, GOLD)
    return frame


def edit_monitor(t, plate):
    frame = shot('editing-live', .28+t*.45, size=SIZE)
    frame = ImageEnhance.Brightness(frame).enhance(.46)
    draw = ImageDraw.Draw(frame, 'RGBA')
    draw.rounded_rectangle((16, 131, 344, 390), 12, fill='#14221f', outline='#829586', width=2)
    if plate:
        clip = shot(plate, .28+t*.50, size=(306, 179))
        frame.paste(clip, (27, 149))
    else:
        draw.rectangle((27, 149, 333, 328), fill='#0e1817')
        type_at(frame, (180, 234), 'No picture', 30, PAPER)
    return frame


def permissions(t):
    if t < 1.05:
        plate = 'walk-live'
    elif t < 2.55:
        plate = None
    else:
        plate = 'steps-live'
    frame = edit_monitor(t, plate)
    draw = ImageDraw.Draw(frame, 'RGBA')
    label(frame, 'Staged edit', 20, 61, 18)
    draw.rounded_rectangle((17, 424, 342, 551), 9, fill='#13211d', outline='#5b7264', width=2)
    for x,key in ((28,'Before'),(240,'After')):
        draw.rounded_rectangle((x, 476, x+90, 520), 4, fill='#536c62')
        type_at(frame, (x+45, 498), key, 18)

    if t < 1.05:
        label(frame, 'Clip permission withheld', 25, 343, 20, GOLD)
        draw.rounded_rectangle((120, 476, 238, 520), 4, fill='#c28673', outline='#f1ae90', width=2)
        type_at(frame, (179, 498), 'Street wide', 16, INK)
    elif t < 2.55:
        lift = ease(progress(t, 1.05, 1.49))
        draw.rounded_rectangle((120, 476, 238, 520), 4, outline='#dc9e86', width=2)
        type_at(frame, (179, 498), '1.3 s gap', 17)
        if lift < 1:
            amount = round(70*lift)
            draw.rounded_rectangle((120, 476-amount, 238, 520-amount), 4,
                                   fill=(194, 134, 115, round(235*(1-lift))))
        label(frame, 'Clip lifted', 25, 343, 24)
    else:
        settle = ease(progress(t, 2.55, 3.04))
        amount = round(38*(1-settle))
        label(frame, 'Approved detail', 25, 343, 24, MINT)
        draw.rounded_rectangle((120, 476-amount, 238, 520-amount), 4, fill='#9fc89d')
        type_at(frame, (179, 498-amount), 'Footsteps', 18, INK)
    return frame


def contact_track(duration, cues, path):
    frames = array('h')
    for i in range(round(RATE*duration)):
        t = i/RATE
        sample = sum(.20*impact(t, at, 36, hz)+.071*impact(t, at, 66, hz*2)
                     for at,hz in cues)
        frames.append(round(32767*sample))
    if sys.byteorder == 'big':
        frames.byteswap()
    with wave.open(str(path), 'wb') as output:
        output.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(frames.tobytes())


SCENES = {
    'hook-short-impossible-move-001': puzzle_room,
    'hook-short-character-collision-001': opposing_roles,
    'hook-short-reaction-first-047': portrait_reaction,
    'hook-short-object-reveal-089': map_reveal,
    'hook-short-turning-point-001': permissions,
}
POSTERS = {
    'hook-short-impossible-move-001': .31,
    'hook-short-character-collision-001': .39,
    'hook-short-reaction-first-047': 1.68,
    'hook-short-object-reveal-089': 1.86,
    'hook-short-turning-point-001': .60,
}
AUDIO = {
    'hook-short-impossible-move-001': partial(contact_track, 5.3, ((.64, 130), (1.20, 270))),
    'hook-short-object-reveal-089': partial(contact_track, 5.5, ((.85, 170), (2.00, 145))),
    'hook-short-turning-point-001': partial(contact_track, 6.0, ((1.05, 260), (3.04, 390))),
}
