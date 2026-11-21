"""Native portrait repairs for misleading original technique previews."""
from functools import lru_cache
from math import cos, degrees, exp, pi, radians, sin

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from preview_common import blend, ease, font, progress
from preview_data import lines_until
from preview_landscape_repairs import FLOOR_X, FLOOR_Y, PLUME
from preview_live_action import GOLD, INK, MINT, PAPER, cup_cutout, face_track, gesture, type_at
from preview_phone import device, screen_track, screen_ui
from preview_plates import FRAME_RATE, shot, source
from preview_sound import IMPACT_CUE, LAND_CUE, duck_gain, playhead, swell, wave_track, window
from preview_spatial import warp
from preview_typography import place_glyph

SIZE = (360, 640)
W, H = SIZE


def tag(frame, text, x=18, y=56, size=20, accent=None):
    draw = ImageDraw.Draw(frame, 'RGBA')
    width = draw.textlength(text, font=font(size))
    draw.rounded_rectangle((x, y, x + width + 22, y + size + 13), 7,
                           fill=accent or (14, 26, 24, 235))
    type_at(frame, (x + 11, y + (size + 13)/2), text, size, INK if accent else PAPER, 'lm')


def crop(raw, bounds):
    return raw.transform(SIZE, Image.Transform.EXTENT, bounds, Image.Resampling.BICUBIC)


def guide_box(frame, x, y):
    draw = ImageDraw.Draw(frame, 'RGBA')
    for dx, dy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        outside = (x + 30*dx, y + 24*dy)
        draw.line(((x + 18*dx, outside[1]), outside, (outside[0], y + 15*dy)), fill=GOLD, width=2)


def subject_locked(t):
    stamp = .08 + .94*t
    face_x, face_y = face_track(stamp)
    amount = ease(progress(t, .78, 1.19))
    scale = W/H
    original_left = 217
    final_left = face_x - 176*scale
    left = original_left + (final_left-original_left)*amount
    image = crop(source('host-live', stamp), (left, 0, left + W*scale, 360))
    if t < 2.48:
        guide_box(image, (face_x-left)/scale, face_y/scale)
        tag(image, 'Fixed crop' if t < .78 else 'Track follows the face', 19, 501, 21,
            MINT if t >= .78 else None)
    return image


def player_guide(frame):
    draw = ImageDraw.Draw(frame, 'RGBA')
    draw.rectangle((287, 306, W, H), fill=(32, 47, 46, 147))
    draw.rectangle((0, 489, W, H), fill=(14, 23, 22, 227))
    draw.rounded_rectangle((15, 96, 284, 484), 7, outline=(212, 239, 199, 217), width=2)
    for y in (342, 391, 440):
        draw.ellipse((306, y-12, 330, y+12), outline=(245, 249, 236, 235), width=2)
    draw.line((19, 574, 164, 574), fill=(239, 246, 230, 206), width=3)
    draw.line((19, 592, 132, 592), fill=(239, 246, 230, 164), width=2)
    draw.line((0, 616, W, 616), fill=(229, 239, 218, 160), width=2)


def safe_zone(t):
    image = shot('portrait-live', .16 + .88*t, size=SIZE)
    align = ease(progress(t, .59, 1.21))
    x, y = round(90 - 68*align), round(500-71*align)
    tag(image, 'Both hands are visible.', x, y, 23, GOLD)
    if t < 2.20:
        player_guide(image)
        tag(image, 'Player guide', 17, 55, 18)
        status = 'Obscured' if t < .59 else 'Move the caption'
        inside = t >= 1.21
        tag(image, 'Inside the safe area' if inside else status, 17, 534, 21,
            MINT if inside else None)
    else:
        tag(image, 'Clean export', 17, 55, 18, MINT)
    return image


RIM = (79, 268, 294, 345)
MATCH_CUT = 1.14


@lru_cache(maxsize=1)
def morning_graphic():
    frame = Image.new('RGB', SIZE, '#192923')
    draw = ImageDraw.Draw(frame)
    draw.ellipse(RIM, fill='#b38454', outline='#f5d9a3', width=4)
    inset = (RIM[0]+12, RIM[1]+9, RIM[2]-12, RIM[3]-9)
    draw.arc(inset, 187, 344, fill='#fae2b6', width=2)
    type_at(frame, (184, 201), 'MORNING POUR', 28, PAPER)
    type_at(frame, (184, 491), 'Graphic shape', 21, '#d2e4ca')
    return frame


def visual_match(t):
    if t < MATCH_CUT:
        return morning_graphic().copy()
    elapsed = t-MATCH_CUT
    stamp = 1.61 + elapsed*.78
    drift = 26*ease(progress(elapsed, .72, 1.82))
    image = crop(source('coffee-live', stamp), (154-drift, 0, 356.5-drift, 360))
    if elapsed < 1.13:
        tag(image, 'Same rim', 19, 58, 20, MINT)
    return image


def tracked_callout(t):
    raw = source('host-live', t)
    left = 208
    frame = crop(raw, (left, 0, left+202.5, 360))
    if .29 <= t <= 2.72:
        fx, fy = face_track(t)
        x, y = (fx-left)*W/202.5, fy*H/360
        guide_box(frame, x, y)
        x_end, y_end = x+59, y+105
        ImageDraw.Draw(frame).line(((x+31, y+25), (x_end, y_end), (x_end+16, y_end)),
                                   fill=MINT, width=3)
        tag(frame, 'Eyes in focus', x_end+11, y_end-18, 17, MINT)
    return frame


def visible_gesture(t):
    frame = crop(gesture(t), (124, 0, 326.5, 360))
    if 1.52 <= t < 2.63:
        tag(frame, 'Spark follows the hand', 17, 518, 19)
    return frame


def visible_wayfinding(t):
    image, quad = device(t, screen_ui(t))
    left = 354
    frame = crop(image, (left, 0, left+202.5, 360))
    amount = ease(progress(t, .42, 1.11))*(1-ease(progress(t, 2.44, 3.02)))
    if amount > 0:
        delta = quad[1][1]-screen_track(0)[0][1][1]
        draw = ImageDraw.Draw(frame, 'RGBA')
        for x,y,w,h in ((421,307,38,22), (436,249,25,16), (446,203,18,11)):
            marks = tuple(((px-left)*W/202.5, (py+delta)*H/360)
                          for px,py in ((x-w,y+h), (x,y), (x+w,y+h)))
            draw.line(marks, fill=(249, 223, 152, round(232*amount)), width=4, joint='curve')
        if amount >= .69:
            x, y = (447-left)*W/202.5, (194+delta)*H/360
            draw.line(((x, y), (x+43, y-62), (x+31, y-62)), fill=MINT, width=2)
            tag(frame, 'Trail ahead', 132, round(y-103), 18, MINT)
    return frame


def portrait_tunnel(t):
    frame = Image.new('RGB', SIZE, '#192933')
    phrase = 'KEEP CUTTING / KEEP CUTTING / '
    forward = ease(progress(t, 0, 1.90))
    fade = 1-ease(progress(t, 1.57, 2.03))
    if fade > .025:
        for ring in range(4):
            radius = 31 + ring*32 + forward*(28 + ring*25)
            size = 10 + ring*3
            shade = blend((25, 41, 51), (91+ring*28, 144+ring*18, 126+ring*14), fade)
            for index,char in enumerate(phrase):
                angle = 2*pi*index/len(phrase) + t*(.62 if ring % 2 == 0 else -.49)
                x, y = 178 + cos(angle)*radius, 314 + sin(angle)*radius
                if -22 < x < W+22 and -22 < y < H+22:
                    place_glyph(frame, char, x, y, size, 270-angle*180/pi, shade, ring % 2 == 1)
    settle = ease(progress(t, 1.72, 2.14))
    if settle > 0:
        type_at(frame, (180, 311+14*(1-settle)), 'KEEP CUTTING', 37,
                blend((25, 41, 51), (220, 238, 198), settle))
        ImageDraw.Draw(frame).line((108, 350, 108+142*settle, 350), fill='#b3c995', width=2)
    return frame


def portrait_icon(t):
    if t < .56 or t >= 2.52:
        return shot('host-live', t, x=-61, size=SIZE)
    base = (238, 237, 212)
    frame = Image.new('RGB', SIZE, base)
    draw = ImageDraw.Draw(frame)
    appear = ease(progress(t, .56, .97))
    y = 231 + 23*(1-appear)
    draw.ellipse((136, y-44, 224, y+44), fill=blend(base, (206, 222, 189), appear))
    color = blend(base, (43, 88, 63), appear)
    draw.arc((151, y-27, 209, y+31), 164, 319, fill=color, width=4)
    draw.line((163, y+18, 196, y-17), fill=color, width=4)
    draw.ellipse((175, y-4, 185, y+6), fill=color)
    text = ease(progress(t, .93, 1.32))
    if text > 0:
        type_at(frame, (180, 339), 'Guide the', 37, blend(base, (53, 78, 66), text))
        type_at(frame, (180, 390), 'eye', 44, blend(base, (64, 105, 69), text))
    return frame


def portrait_title_pair(t):
    if 1.04 <= t < 2.06:
        frame = shot('host-live', .63+(t-1.04)*.83, x=-63, size=SIZE)
        tag(frame, 'Keep a steady pace.', 21, 494, 25)
        return frame
    opener = t < 1.04
    p = ease(progress(t, 0 if opener else 2.06, .36 if opener else 2.44))
    bg = (240, 236, 213)
    frame = Image.new('RGB', SIZE, bg)
    draw = ImageDraw.Draw(frame)
    draw.arc((35, 182, 325, 483), 192, 349, fill='#91ac89', width=2)
    draw.arc((54, 207, 306, 462), 190, 349, fill='#c0ccac', width=2)
    draw.ellipse((174, 186, 186, 198), fill='#b97455')
    draw.line((112, 405, 248, 405), fill='#9eac8e', width=2)
    words = ('In the edit',) if opener else ('See you in', 'the edit')
    for i,word in enumerate(words):
        type_at(frame, (180, 317+50*i+11*(1-p)), word, 41, blend(bg, (39, 65, 54), p))
    return frame


def portrait_cold_open(t):
    if t < 1.24:
        # Stop on the approach, one source frame before the lead shoe lands.
        stamp = min(.65, .37 + t*.245)
        frame = crop(source('steps-live', stamp), (132, 39, 312.5625, 360))
        if t >= .24:
            tag(frame, 'Where should the cut land?', 17, 496, 21)
        return frame
    frame = crop(source('walk-live', .13+(t-1.24)*.69), (219, 0, 421.5, 360))
    tag(frame, 'Earlier on the route', 17, 69, 23, MINT)
    return frame


def portrait_payoff(t):
    if t < 1.24:
        stamp = .62+t*.39
        message = 'Will the pattern hold?'
    else:
        stamp = 1.89+(t-1.24)*.55
        message = 'The pattern holds.'
    start_x = 154 - 16*ease(progress(t, 1.35, 2.95))
    frame = crop(source('coffee-live', stamp), (start_x, 0, start_x+202.5, 360))
    tag(frame, message, 17, 516, 25, MINT if t >= 1.24 else None)
    return frame


def point_series(values):
    return [(58+47*i, 526-3.5*y) for i,y in enumerate(values)]


def portrait_comparison(t):
    frame = Image.new('RGB', SIZE, '#eee9d5')
    draw = ImageDraw.Draw(frame)
    type_at(frame, (19, 63), 'Two plans, one scale', 31, '#263f32', 'lm')
    type_at(frame, (20, 105), 'Sample index', 20, '#475e4f', 'lm')
    for value in (0, 25, 50, 75, 100):
        y = 526-3.5*value
        draw.line((57, y, 300, y), fill='#b8c1a5')
        type_at(frame, (48, y), str(value), 15, '#3a5344', 'rm')
    for i,year in enumerate(('2019', '20', '21', '22', '23', '24')):
        type_at(frame, (58+47*i, 551), year, 15, '#3a5344')

    a = point_series((17, 25, 37, 57, 74, 87))
    b = point_series((17, 31, 37, 42, 57, 59))
    if t >= 2.12:
        draw.polygon(a[2:] + list(reversed(b[2:])), fill='#d4dfba')
    for points, onset, ending, color in ((a, .08, 1.06, '#1e6149'), (b, .96, 2.09, '#a65333')):
        amount = progress(t, onset, ending)
        if amount > 0:
            draw.line(lines_until(points, amount), fill=color, width=5, joint='curve')
    if t >= 2.12:
        for points, text, color in ((a, 'A', '#1e6149'), (b, 'B', '#a65333')):
            x,y = points[-1]
            draw.ellipse((x-5, y-5, x+5, y+5), fill=color)
            type_at(frame, (319, y), text, 23, color)
        type_at(frame, (20, 142), '28-point gap in 2024', 21, '#263f32', 'lm')
    return frame


def portrait_sound_contact(t):
    frame = Image.new('RGB', SIZE, '#172e2a')
    draw = ImageDraw.Draw(frame, 'RGBA')
    draw.rounded_rectangle((19, 157, 340, 425), 12, fill='#263e34', outline='#678378', width=2)
    draw.rounded_rectangle((107, 264, 253, 357), 10, outline='#7b9d86', width=3)
    settle = ease(progress(t, .51, LAND_CUE))
    x,y = -83+(180+83)*settle, 310
    draw.rounded_rectangle((x-64, y-40, x+64, y+40), 8, fill='#e6ebd4')
    type_at(frame, (x, y), 'PING', 29, '#233a32')
    if LAND_CUE <= t < 1.39:
        p = progress(t, LAND_CUE, 1.39)
        r = 67 + 43*p
        draw.ellipse((180-r, y-r, 180+r, y+r), outline=(247, 205, 111, round(225*(1-p))), width=3)
    tag(frame, 'Sound at the landing', 19, 68, 22)
    x0,x1,mid = 35,323,507
    wave_track(draw, x0, x1, mid, t,
               lambda a: .7*swell(a, .48, .52) + (exp(-10*(a-LAND_CUE)) if a >= LAND_CUE else 0),
               MINT, '#557463', 27)
    hit = x0+(x1-x0)*LAND_CUE/3.2
    draw.line((hit, 462, hit, 549), fill=GOLD, width=3)
    head = x0+(x1-x0)*min(t/3.2, 1)
    draw.line((head, 480, head, 535), fill=PAPER, width=2)
    type_at(frame, (hit, 573), 'Contact', 16, GOLD)
    return frame


def slide_phrase(t):
    frame = shot('portrait-live', t, size=SIZE)
    change = 1.45
    elapsed = t if t < change else t-change
    first = t < change
    enter = ease(progress(elapsed, .02, .26))
    exit = ease(progress(elapsed, 1.12 if first else 1.49, 1.39 if first else 1.74))
    layer = Image.new('RGBA', SIZE)
    y = round(467+28*(1-enter)-11*exit)
    tag(layer, 'Here is the change' if first else 'Now give it time', 26, y, 29)
    if exit > 0:
        layer = layer.filter(ImageFilter.GaussianBlur(6*exit))
    alpha = round(255*enter*(1-exit))
    frame.paste(layer, (0, 0), layer.getchannel('A').point(lambda value: value*alpha//255))
    return frame


def rolling_title(t):
    frame = shot('portrait-live', t, size=SIZE)
    phrase = 'THE QUICK TEST'
    layer = Image.new('RGBA', (W, 55))
    box = ImageDraw.Draw(frame, 'RGBA')
    box.rounded_rectangle((16, 445, 344, 508), 8, fill=(13, 25, 23, 221))
    x = 29
    face = font(33)
    for i,char in enumerate(phrase):
        amount = ease(progress(t, .11+.046*i, .38+.046*i))
        if amount > 0:
            type_at(layer, (x, 28+43*(1-amount)), char, 33, MINT, 'lm')
        x += face.getlength(char)
    frame.paste(layer, (0, 449), layer)
    return frame


def fade_paste(frame, layer, x, y, opacity=1):
    matte = layer.getchannel('A')
    if opacity < 1:
        matte = matte.point(lambda value: round(value*opacity))
    frame.paste(layer, (round(x), round(y)), matte)


PHONE_LEFT = 109
PHONE_SCALE = W/294
PHONE_TOP = 200


@lru_cache(maxsize=1)
def phone_feather():
    length = round(360*PHONE_SCALE)
    ramp = Image.new('L', (1, length))
    ramp.putdata([round(255*ease(y/26)) for y in range(length)])
    return ramp.resize((W, length))


def phone_stage(t, screen):
    # The upper area uses another crop of the same moving trail so the large
    # overlays can clear the real screen and the fingers in the lower crop.
    image, corners = device(t, screen)
    trail = crop(source('phone-live', t), (350, 0, 552.5, 360))
    trail = ImageEnhance.Brightness(trail.filter(ImageFilter.GaussianBlur(3.1))).enhance(.72)
    plate = image.crop((PHONE_LEFT, 0, PHONE_LEFT+294, 360))
    plate = plate.resize(phone_feather().size, Image.Resampling.LANCZOS)
    trail.paste(plate, (0, PHONE_TOP), phone_feather())
    return trail, tuple(((x-PHONE_LEFT)*PHONE_SCALE, PHONE_TOP+y*PHONE_SCALE) for x, y in corners)


def phone_card(title, note, width=276, height=74, fill='#172e2a', accent=MINT):
    card = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((1, 1, width-2, height-2), 10, fill=fill, outline=accent, width=2)
    type_at(card, (15, height*.34), title, 24, PAPER, 'lm')
    type_at(card, (15, height*.71), note, 17, accent, 'lm')
    return card


def phone_origin(frame, at, p):
    if 0 < p < 1:
        x, y = at
        radius = 9+32*p
        draw = ImageDraw.Draw(frame, 'RGBA')
        draw.ellipse((x-radius, y-radius, x+radius, y+radius),
                     outline=(204, 250, 206, round(240*(1-p))), width=4)


def portrait_hud(t):
    frame, quad = phone_stage(t, screen_ui(t))
    x, y = quad[1]
    phone_origin(frame, (x-33, y+66), progress(t, .30, .74))
    amount = ease(progress(t, .43, .98))*(1-ease(progress(t, 2.53, 3.11)))
    if amount <= 0:
        return frame
    panel = Image.new('RGBA', (296, 138))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((1, 1, 294, 136), 12, fill=(18, 47, 51, 225), outline=MINT, width=2)
    type_at(panel, (15, 26), 'Trail monitor', 27, PAPER, 'lm')
    draw.line([(17+i*11, 92+17*sin(i*.74+t*4)) for i in range(14)], fill=MINT, width=4)
    if t >= 1.14:
        type_at(panel, (199, 74), 'GPS', 18, PAPER, 'lm')
        type_at(panel, (199, 105), 'LOCKED', 19, GOLD, 'lm')
    left, top = x-181, y-174 + 59*(1-amount)
    light = Image.new('RGBA', SIZE)
    light_draw = ImageDraw.Draw(light)
    light_draw.polygon(((x-43, y+58), (left+22, top+138), (left+269, top+132), (x-25, y+57)),
                       fill=(146, 236, 215, round(80*amount)))
    light_draw.ellipse((x-66, y+39, x-7, y+78), fill=(196, 251, 200, round(106*amount)))
    fade_paste(frame, light.filter(ImageFilter.GaussianBlur(10)), 0, 0)
    panel.putalpha(panel.getchannel('A').point(lambda value: round(value*amount)))
    warp(frame, panel, [(left, top+9), (left+296, top), (left+292, top+129), (left+4, top+138)])
    return frame


LAYER_ITEMS = (('Route', 'North trail'), ('Distance', '2.4 km'), ('Next turn', 'Keep right'))


def portrait_interface_layers(t):
    screen = Image.new('RGBA', (170, 314), '#142b2c')
    draw = ImageDraw.Draw(screen)
    type_at(screen, (14, 37), 'Trail guide', 23, PAPER, 'lm')
    for i, (name, detail) in enumerate(LAYER_ITEMS):
        top = 65+77*i
        draw.rounded_rectangle((10, top, 160, top+65), 7, fill='#2c5140')
        type_at(screen, (19, top+21), name, 18, PAPER, 'lm')
        type_at(screen, (19, top+45), detail, 15, GOLD if i == 2 else MINT, 'lm')
    frame, quad = phone_stage(t, screen)
    x, y = quad[1]
    for i, (name, detail) in enumerate(LAYER_ITEMS):
        enter = ease(progress(t, .30+.28*i, .76+.29*i))
        fade = 1-.72*ease(progress(t, 2.62, 3.08)) if i < 2 else 1
        if enter > 0:
            panel = phone_card(name, detail, 262, 65, accent=GOLD if i == 2 else MINT)
            left = x-120-65*enter+8*i
            origin = y+23+i*64
            final = y-196+69*i
            top = origin + (final-origin)*enter
            fade_paste(frame, panel, left, top, enter*fade)
    return frame


def cleanup_panel(t):
    done = t >= 1.62
    panel = Image.new('RGBA', (296, 157))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((1, 1, 294, 155), 10, fill='#192e30', outline=MINT, width=2)
    type_at(panel, (15, 27), 'Voice cleanup', 27, PAPER, 'lm')
    for i in range(21):
        x = 19+13*i
        height = 6 + (18 if done else 27)*abs(sin(i*(.62 if done else 1.71)))
        draw.line((x, 82-height, x, 82+height), fill=MINT if done else '#aec4b8', width=5)
    draw.rounded_rectangle((15, 117, 281, 145), 6, fill=MINT if done else '#374c44')
    type_at(panel, (148, 131), 'Noise removed' if done else 'Clean audio', 20, INK if done else PAPER)
    return panel


def portrait_floating_screen(t):
    panel = cleanup_panel(t)
    ui = Image.new('RGBA', (170, 314), '#142b2c')
    type_at(ui, (85, 48), 'Audio settings', 20, PAPER)
    embedded = panel.resize((158, 84), Image.Resampling.LANCZOS)
    fade_paste(ui, embedded, 6, 106)
    frame, quad = phone_stage(t, ui)
    x, y = quad[1]
    phone_origin(frame, (x-27, y+132), progress(t, .46, .86))
    amount = ease(progress(t, .55, 1.09))*(1-ease(progress(t, 2.68, 3.12)))
    if amount > 0:
        left, top = x-191+(1-amount)*70, y-190+(1-amount)*225
        draw = ImageDraw.Draw(frame, 'RGBA')
        draw.line(((x-27, y+132), (x+45, y+90), (left+271, top+148)),
                  fill=(190, 242, 214, round(200*amount)), width=2)
        fade_paste(frame, panel, left, top, amount)
    return frame


def portrait_notification(t):
    frame, quad = phone_stage(t, screen_ui(t))
    x, y = quad[1]
    amount = ease(progress(t, .48, .91))*(1-ease(progress(t, 2.37, 3.06)))
    phone_origin(frame, (x-36, y+25), progress(t, .32, .72))
    if amount > 0:
        left = x-169
        top = y-119*amount-10*sin(amount*pi)
        panel = phone_card('Route downloaded', 'Available offline', 276, 81, accent=GOLD)
        panel.putalpha(panel.getchannel('A').point(lambda value: round(value*amount)))
        warp(frame, panel, [(left, top+10), (left+276, top), (left+276, top+81), (left, top+91)])
    return frame


def portrait_card_carousel(t):
    frame, quad = phone_stage(t, screen_ui(t))
    x, y = quad[1]
    amount = ease(progress(t, .35, .79))*(1-ease(progress(t, 2.67, 3.14)))
    if amount <= 0:
        return frame
    cards = []
    labels = (('North trail', '2.4 km'), ('Lake loop', '3.8 km'), ('Grove path', '1.1 km'))
    for i, (title, note) in enumerate(labels):
        angle = (t-.82)*2.96 + i*2*pi/3 + pi/2
        depth = (sin(angle)+1)/2
        panel = phone_card(title, note, 169, 75, accent=GOLD if depth > .62 else MINT)
        scale = .69+.35*depth
        panel = panel.resize((round(panel.width*scale), round(panel.height*scale)), Image.Resampling.LANCZOS)
        if depth < .55:
            panel = panel.filter(ImageFilter.GaussianBlur(1.4*(1-depth)))
        cx = x-36+83*cos(angle)
        cy = y-141*amount+46*sin(angle)
        cards.append((depth, panel, cx-panel.width/2, cy-panel.height/2))
    for depth, panel, left, top in sorted(cards, key=lambda card: card[0]):
        fade_paste(frame, panel, left, top, amount*(.55+.45*depth))
    return frame


def portrait_screen_replacement(t):
    left = 144
    pane = (left, 0, left+202.5, 360)
    raw = crop(source('phone-live', t), pane)
    if t < .63:
        tag(raw, 'Original display', 18, 28, 20)
        if t >= .29:
            corners, _ = screen_track(round(t*20))
            draw = ImageDraw.Draw(raw)
            for x, y in corners:
                x, y = (x-left)*W/202.5, y*H/360
                draw.ellipse((x-6, y-6, x+6, y+6), outline=PAPER, width=2)
        return raw
    image, _ = device(t, screen_ui(t))
    frame = crop(image, pane)
    wipe = ease(progress(t, .63, 1.03))
    if wipe < 1:
        x = round(37+310*wipe)
        frame.paste(raw.crop((x, 0, W, H)), (x, 0))
        ImageDraw.Draw(frame).line((x, 82, x, 551), fill=PAPER, width=2)
    tag(frame, 'Tracking the corners' if wipe < 1 else 'Screen replaced', 18, 28, 20, MINT)
    return frame


def host_portrait(t, left=179):
    pane = (left, 0, left+202.5, 360)
    return crop(source('host-live', t), pane), crop(source('host-live-matte', t), pane)


def portrait_chat(t):
    frame, matte = host_portrait(t, 165)
    raw = frame.copy()
    offset = (face_track(t)[0]-269)*.57
    for i, (start, left, top, width, text, tone) in enumerate((
            (.24, 229, 62, 122, 'Rolling?', '#ecf3cc'),
            (.79, 14, 63, 130, 'Ready.', '#c4e8bd'),
            (1.37, 242, 144, 108, 'Take 1.', '#ecf3cc'))):
        amount = ease(progress(t, start, start+.28))*(1-ease(progress(t, 2.57, 3.08)))
        if amount <= 0:
            continue
        panel = Image.new('RGBA', (width, 58))
        draw = ImageDraw.Draw(panel)
        draw.rounded_rectangle((0, 0, width-1, 46), 11, fill=tone)
        edge = 17 if i != 1 else width-16
        draw.polygon(((edge-9, 41), (edge+11, 41), (edge-4 if i != 1 else edge+6, 57)), fill=tone)
        type_at(panel, (width/2 if i == 1 else width-7, 24), text, 22, INK, 'mm' if i == 1 else 'rm')
        fade_paste(frame, panel, left+offset, top+12*(1-amount), amount)
    frame.paste(raw, (0, 0), matte)
    return frame


def portrait_curved(t):
    raw, matte = host_portrait(t, 169)
    amount = ease(progress(t, .35, .84))*(1-ease(progress(t, 2.62, 3.11)))
    if amount <= 0:
        return raw
    frame = ImageEnhance.Brightness(raw).enhance(.72)
    center_x = 176 + .72*(face_track(t)[0]-269)
    center_y = 246
    draw = ImageDraw.Draw(frame)
    draw.arc((center_x-126, center_y-131, center_x+126, center_y+131), 192, 342, fill=GOLD, width=2)
    for word, start in (('KEEP', 198), ('PACE', 305)):
        for i, char in enumerate(word):
            angle = radians(start + 9*i + 8*(1-amount)+3*sin(2*t))
            x, y = center_x+142*cos(angle), center_y+146*sin(angle)
            place_glyph(frame, char, x, y, 30, 270-degrees(angle), GOLD)
    frame.paste(raw, (0, 0), matte)
    return Image.blend(raw, frame, amount)


def portrait_silhouette(t):
    raw, matte = host_portrait(t)
    if t < .59 or t >= 2.46:
        return raw
    frame = Image.new('RGB', SIZE, '#f5c574')
    draw = ImageDraw.Draw(frame)
    for i in range(13):
        y = (i*58+round(t*134))%758-90
        draw.polygon(((0, y+79), (W, y), (W, y+17), (0, y+99)),
                     fill=('#d57d59', '#ffdb8d', '#eaa668')[i%3])
    enter = ease(progress(t, .59, 1.03))
    type_at(frame, (180, 135+77*enter), 'FOCUS', 82, '#6e352a')
    frame.paste(ImageOps.colorize(raw.convert('L'), '#1c1830', '#875347'), (0, round(178*(1-enter))), matte)
    tag(frame, 'Make one point.', 18, 520, 29, GOLD)
    return frame


def room_portrait(image, t):
    center = 365+25*ease(progress(t, .02, 2.93))
    return crop(image, (center-101.25, 0, center+101.25, 360))


def portrait_room_graphic(t):
    room = shot('room')
    stage = ease(progress(t, .23, .73))
    if stage > 0:
        panel = Image.new('RGBA', (230, 146))
        draw = ImageDraw.Draw(panel)
        draw.rounded_rectangle((1, 1, 228, 144), 8, fill=(17, 39, 42, 235), outline=MINT, width=2)
        type_at(panel, (13, 26), 'Watch time', 22, PAPER, 'lm')
        for y in (60, 86, 113):
            draw.line((14, y, 214, y), fill='#55746b')
        values = [(14, 121), (52, 112), (83, 114), (113, 94), (145, 99), (175, 70), (212, 52)]
        amount = progress(t, .54, 2.11)
        if amount > 0:
            trace = lines_until(values, amount)
            draw.line(trace, fill=MINT, width=5, joint='curve')
            x, y = trace[-1]
            draw.ellipse((x-4, y-4, x+4, y+4), fill=PAPER)
        if t >= 2.11:
            type_at(panel, (214, 32), '+18%', 24, GOLD, 'rm')
        panel.putalpha(panel.getchannel('A').point(lambda value: round(value*stage)))
        warp(room, panel, [(294, 101), (448, 94), (446, 197), (296, 187)])
    return room_portrait(room, t)


def portrait_floor_type(t):
    room = shot('room')
    amount = ease(progress(t, .34, .90))
    if amount > 0:
        title = Image.new('RGBA', (384, 107))
        type_at(title, (194, 54), 'STUDIO', 78, (41, 34, 22, round(160*amount)))
        warp(room, title.filter(ImageFilter.GaussianBlur(3)), [(305, 276), (442, 276), (467, 332), (288, 326)])
        title = Image.new('RGBA', (384, 107))
        type_at(title, (194, 52), 'STUDIO', 78, (254, 239, 203, round(248*amount)))
        warp(room, title, [(304, 272), (441, 272), (466, 328), (287, 322)])
    return room_portrait(room, t)


def portrait_grounded_particles(t):
    room = shot('room')
    x, y = FLOOR_X, FLOOR_Y
    marked = ease(progress(t, .58, 1.08))
    if marked < 1:
        draw = ImageDraw.Draw(room, 'RGBA')
        opacity = round(218*(1-marked))
        edge = ((x-44, y-10), (x+35, y-8), (x+62, y+13), (x-54, y+9))
        draw.line((*edge, edge[0]), fill=(255, 234, 183, opacity), width=2)
        draw.ellipse((x-4, y-4, x+4, y+4), fill=(255, 234, 183, opacity))
    amount = ease(progress(t, .40, 1.00))*(1-.50*ease(progress(t, 2.52, 3.17)))
    if amount > 0:
        haze = Image.new('RGBA', room.size)
        draw = ImageDraw.Draw(haze)
        draw.ellipse((x-35, y-4, x+39, y+10), fill=(64, 44, 25, round(153*amount)))
        fade_paste(room, haze.filter(ImageFilter.GaussianBlur(4)), 0, 0)
        haze = Image.new('RGBA', room.size)
        draw = ImageDraw.Draw(haze)
        flecks = []
        for i, (offset, drift, weight) in enumerate(PLUME):
            age = (t-.40+offset)%1.68
            px = x+drift*(12+35*age)+15*age
            py = y-(19*weight+19*age)*age
            alpha = sin(pi*age/1.68)**2*amount
            radius = (9+age*10)*weight
            draw.ellipse((px-radius, py-.56*radius, px+radius, py+.51*radius),
                         fill=(240, 221, 178, round(131*alpha)))
            if i%3 == 1:
                flecks.append((px, py-4, alpha))
        fade_paste(room, haze.filter(ImageFilter.GaussianBlur(5)), 0, 0)
        draw = ImageDraw.Draw(room, 'RGBA')
        for px, py, alpha in flecks:
            draw.ellipse((px-1.5, py-1.5, px+1.5, py+1.5), fill=(255, 233, 179, round(220*alpha)))
    frame = room_portrait(room, t)
    tag(frame, 'Track the floor' if t < 1.12 else 'Dust stays put', 18, 54, 23, MINT if t >= 1.12 else None)
    return frame


def portrait_split_explanation(t):
    if t < .37 or t >= 2.86:
        return shot('host-live', t, x=-64, size=SIZE)
    frame = Image.new('RGB', SIZE, '#21342d')
    presenter = shot('host-live', t, 1.17, -44, -27, (W, 251))
    example = shot('coffee-live', .21+.85*t, 1.14, -35, 30, (W, 264))
    frame.paste(presenter, (0, 0))
    frame.paste(example, (0, 255))
    draw = ImageDraw.Draw(frame)
    draw.rectangle((0, 250, W, 255), fill='#bfd3af')
    for i, message in enumerate(('01  Tilt the cup', '02  Pour at the surface')):
        at = (i == 0 and t < 1.50) or (i == 1 and t >= 1.50)
        y = 518+47*i
        draw.rounded_rectangle((12, y, W-13, y+40), 6, fill=GOLD if at else '#3a5548')
        type_at(frame, (24, y+20), message, 23, INK if at else PAPER, 'lm')
    return frame


def portrait_synced_compare(t):
    frame = Image.new('RGB', SIZE, '#142925')
    stamp = .24 + .85*t
    original = shot('walk-live', stamp, 1.08, -15, 5, (W, 252))
    corrected = ImageEnhance.Color(ImageEnhance.Contrast(original).enhance(1.25)).enhance(1.36)
    corrected = Image.blend(corrected, Image.new('RGB', original.size, '#caa86f'), .10)
    frame.paste(original, (0, 35))
    frame.paste(Image.blend(original, corrected, ease(progress(t, .30, .62))), (0, 324))
    type_at(frame, (15, 17), 'Original', 21, PAPER, 'lm')
    type_at(frame, (15, 304), 'Graded', 21, MINT, 'lm')
    type_at(frame, (180, 604), f'Same source frame  {stamp:.2f}s', 19, GOLD)
    return frame


@lru_cache(maxsize=3)
def coffee_detail(index):
    title, stamp, bounds = (
        ('Pour', .52, (125, 15, 370, 190)),
        ('Texture', 1.37, (175, 124, 354, 239)),
        ('Finish', 2.61, (197, 190, 321, 277)),
    )[index]
    tile = Image.new('RGBA', (116, 100), '#f2e9c7')
    picture = source('coffee-live', stamp).crop(bounds)
    tile.paste(ImageOps.fit(picture, (104, 68), Image.Resampling.LANCZOS), (6, 5))
    type_at(tile, (58, 86), title, 20, INK)
    return tile


def portrait_product_orbit(t):
    frame = ImageEnhance.Brightness(shot('room', size=SIZE)).enhance(.43)
    ImageDraw.Draw(frame).ellipse((32, 240, 328, 499), outline='#b7c39b', width=2)
    tag(frame, 'Latte details', 20, 68, 24, MINT)
    objects = []
    for i in range(3):
        angle = i*2*pi/3 + 4.2*ease(progress(t, .23, 2.60)) - .58
        depth = sin(angle)
        tile = coffee_detail(i)
        scale = .91+.18*depth
        tile = tile.resize((round(tile.width*scale), round(tile.height*scale)), Image.Resampling.LANCZOS)
        x, y = 180+105*cos(angle)-tile.width/2, 367+111*depth-tile.height/2
        opacity = (.73+.27*(depth+1)/2)*ease(progress(t, .12+i*.16, .59+i*.15))
        objects.append((depth, tile, x, y, opacity))
    hero = cup_cutout().resize((169, 169), Image.Resampling.LANCZOS)
    objects.append((0, hero, 96, 276, 1))
    for _, image, x, y, opacity in sorted(objects, key=lambda tile: tile[0]):
        fade_paste(frame, image, x, y, opacity)
    return frame


@lru_cache(maxsize=1)
def inset_matte():
    mask = Image.new('L', (110, 110))
    ImageDraw.Draw(mask).ellipse((0, 0, 109, 109), fill=255)
    return mask


def portrait_pip(t):
    if t < .34 or t >= 2.84:
        return shot('host-live', t, x=-68, size=SIZE)
    frame = Image.new('RGB', SIZE, '#142824')
    frame.paste(shot('coffee-live', .17+t*.75, 1.30, -39, 28, (W, 260)), (0, 102))
    draw = ImageDraw.Draw(frame)
    type_at(frame, (20, 60), 'Export settings', 32, PAPER, 'lm')
    revealed = ease(progress(t, 1.18, 1.48))
    if revealed > 0:
        draw.rounded_rectangle((20, 393, 341, 584), 8, fill='#243e34', outline='#587363')
        type_at(frame, (36, 422), 'Resolution', 21, PAPER, 'lm')
        draw.rounded_rectangle((176, 479, 319, 529), 8, fill=MINT if t >= 1.71 else '#4d6b57')
        type_at(frame, (247, 504), '1080p', 27, INK if t >= 1.71 else PAPER)
        tip = (270-36*revealed, 550-32*revealed)
        draw.polygon((tip, (tip[0]+7, tip[1]+31), (tip[0]+24, tip[1]+20)), fill=GOLD)
    left = round(229-205*revealed)
    top = round(462-188*revealed)
    inset = shot('host-live', t, 1.90, -54, -76, (110, 110))
    draw.ellipse((left-3, top-3, left+112, top+112), fill=PAPER)
    frame.paste(inset, (left, top), inset_matte())
    return frame


def portrait_ducked(t):
    frame = Image.new('RGB', SIZE, '#f2efdc')
    draw = ImageDraw.Draw(frame)
    type_at(frame, (18, 68), 'Music under speech', 30, '#263b30', 'lm')
    x0, x1 = 31, 329
    voiced = .83 < t < 2.35
    status = 'Voice in front' if voiced else 'Music rises' if t >= 2.35 else 'Music starts'
    tag(frame, status, 18, 117, 22, MINT)
    draw.rounded_rectangle((18, 202, 342, 347), 12, fill='#dbe9d4', outline='#b4c6af')
    draw.rounded_rectangle((18, 374, 342, 532), 12, fill='#eaddbd', outline='#d0c1a0')
    type_at(frame, (30, 230), 'Dialogue', 22, '#305a45', 'lm')
    type_at(frame, (30, 401), 'Music bed', 22, '#735334', 'lm')
    wave_track(draw, x0, x1, 285, t, lambda stamp: window(stamp, .83, 2.35), '#397358', '#9aaf94', 36)
    wave_track(draw, x0, x1, 462, t, duck_gain, '#9d602e', '#bea97c', 34)
    gain = [round(100*duck_gain(i*3.2/80)) for i in range(81)]
    draw.line([(x0+(x1-x0)*i/80, 518-level*.22) for i, level in enumerate(gain)], fill='#936235', width=2)
    playhead(draw, t, x0, x1, 251, 526, '#44564a')
    type_at(frame, (180, 565), f'Music level  {round(100*duck_gain(t))}%', 23, '#735334')
    return frame


def portrait_layered_sound(t):
    hit = t >= IMPACT_CUE
    if hit:
        stamp = .70+(t-IMPACT_CUE)*.73
        frame = crop(source('steps-live', stamp), (132, 39, 312.5625, 360))
    else:
        frame = shot('walk-live', .14+t*.65, x=-12, size=SIZE)
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((13, 428, 347, 603), 10, fill='#152f28')
    tag(frame, 'Impact on contact' if hit else 'Riser into the cut', 17, 56, 22, MINT if hit else None)
    rows = (
        ('Riser', 471, lambda stamp: window(stamp, .15, IMPACT_CUE, .28)*progress(stamp, .15, IMPACT_CUE), MINT),
        ('Low hit', 521, lambda stamp: exp(-9*(stamp-IMPACT_CUE)) if stamp >= IMPACT_CUE else 0, GOLD),
        ('Click', 574, lambda stamp: exp(-22*(stamp-IMPACT_CUE)) if stamp >= IMPACT_CUE else 0, PAPER),
    )
    for name, mid, energy, color in rows:
        type_at(frame, (23, mid), name, 17, color, 'lm')
        wave_track(draw, 94, 328, mid, t, energy, color, '#688379', 16)
    playhead(draw, t, 94, 328, 448, 591, '#b0c4a3')
    return frame


def portrait_chart_marker(t):
    frame = Image.new('RGB', SIZE, '#1b342e')
    draw = ImageDraw.Draw(frame)
    type_at(frame, (19, 64), 'Follow the signal', 32, PAPER, 'lm')
    type_at(frame, (20, 106), 'Uplink strength (%)', 22, MINT, 'lm')
    values = (20, 45, 34, 69, 60, 83)
    points = [(57+53*i, 522-3.55*value) for i, value in enumerate(values)]
    for value in (0, 25, 50, 75, 100):
        y = 522-3.55*value
        draw.line((56, y, 322, y), fill='#476459')
        type_at(frame, (47, y), str(value), 15, PAPER, 'rm')
    for i, sec in enumerate((0, 3, 6, 9, 12, 15)):
        type_at(frame, (57+53*i, 550), f'{sec}s', 16, PAPER)
    index = 2*ease(progress(t, .12, .96)) + 3*ease(progress(t, 1.47, 2.47))
    i = min(4, int(index))
    x = 57 + index*53
    value = values[i] + (values[i+1]-values[i])*(index-i)
    y = 522-3.55*value
    draw.line(points, fill='#507168', width=3)
    draw.line((57, y, x, y, x, 522), fill='#8eaf99', width=2)
    draw.line([*points[:i+1], (x, y)], fill=MINT, width=5, joint='curve')
    draw.ellipse((x-7, y-7, x+7, y+7), fill=GOLD, outline=PAPER, width=2)
    tag(frame, f'{round(value)}% at {index*3:.1f}s', 18, 582, 20, GOLD)
    return frame


@lru_cache(maxsize=1)
def trail_photo():
    still = source('phone-live', .83).crop((350, 25, 640, 310))
    return ImageOps.fit(still, (255, 161), Image.Resampling.LANCZOS)


def portrait_map_evidence(t):
    frame = Image.new('RGB', SIZE, '#e6ead3')
    draw = ImageDraw.Draw(frame)
    type_at(frame, (17, 60), 'North trail survey', 29, '#284b3c', 'lm')
    type_at(frame, (18, 99), 'Sample map', 20, '#526b57', 'lm')
    draw.polygon(((0, 244), (92, 196), (151, 166), (218, 171), (330, 133),
                  (359, 169), (359, 596), (1, 620)), fill='#d2dfba')
    for i in range(5):
        draw.arc((21+i*14, 125+i*14, 333+i*8, 409+i*24), 165, 335,
                 fill='#b9cda4', width=2)
    draw.line(((56, 542), (74, 453), (129, 389), (132, 307), (176, 262), (198, 221), (253, 186)),
              fill='#739370', width=8, joint='curve')
    tag(frame, 'North trail', 111, 201, 19)
    p = ease(progress(t, .35, .96))*(1-ease(progress(t, 2.60, 3.11)))
    if p > 0:
        pin_x, pin_y = 176, 262
        draw.ellipse((pin_x-15, pin_y-15, pin_x+15, pin_y+15), outline='#ab6846', width=3)
        draw.ellipse((pin_x-6, pin_y-6, pin_x+6, pin_y+6), fill='#ab6846', outline='#fff3d8', width=2)
        card_y = 350+31*(1-p)
        draw.line(((pin_x, pin_y+15), (pin_x+20, card_y-16), (pin_x+20, card_y+2)), fill='#8c6948', width=3)
        sheet = Image.new('RGBA', (273, 203), '#fff3d8')
        sheet.paste(trail_photo(), (9, 8))
        type_at(sheet, (11, 185), 'Illustrative trail photo', 19, '#394e3c', 'lm')
        fade_paste(frame, sheet, 46, card_y, p)
    return frame


def portrait_document(t):
    page = Image.new('RGB', SIZE, '#213830')
    draw = ImageDraw.Draw(page)
    draw.rounded_rectangle((20, 52, 340, 575), 10, fill='#f4edd7')
    depth = ease(progress(t, .52, 1.43))
    ink = blend((54, 67, 48), (137, 135, 109), depth)
    type_at(page, (38, 95), 'Inspection report 04', 24, ink, 'lm')
    type_at(page, (38, 132), '12 August 1948', 19, ink, 'lm')
    for ypos, words in ((186, 'The harbor receiver registered'), (211, 'a faint tone at dawn.'),
                         (363, 'Operators logged the frequency'), (389, 'and opened the line.'),
                         (426, 'The relay held until the'), (451, 'afternoon wind picked up.')):
        type_at(page, (37, ypos), words, 17, ink, 'lm')
    q = ease(progress(t, .70, 1.38))
    if q > 0:
        draw.rounded_rectangle((30, 250, 30+266*q, 319), 4, fill='#f1d28c')
    type_at(page, (37, 269), 'A signal from the ridge', 21, '#304e3d', 'lm')
    type_at(page, (37, 298), 'arrived at 06:42.', 21, '#304e3d', 'lm')
    type_at(page, (37, 500), 'Filed with the coastal survey', 17, '#4b6754', 'lm')
    type_at(page, (37, 525), 'Sample document · Report 04', 17, '#4b6754', 'lm')
    draw.line((36, 475, 323, 475), fill='#a9b28d', width=1)
    return crop(page, (17*depth, 37*depth, W-17*depth, H-23*depth))


def portrait_timeline(t):
    frame = Image.new('RGB', SIZE, '#152c27')
    draw = ImageDraw.Draw(frame)
    type_at(frame, (15, 56), 'Editable sequence', 29, PAPER, 'lm')
    y_min, x0, x1 = 329, 109, 344
    head = x0+(x1-x0)*progress(t, 0, 3.2)
    move = ease(progress(t, 1.47, 2.04))
    caption_left = 151+44*move
    preview = shot('coffee-live', .19+t*.76, 1.18, -38, 28, (330, 212))
    if caption_left <= head < caption_left+64:
        tag(preview, 'First pour', 14, 153, 19, GOLD)
    elif head >= 278:
        tag(preview, 'Finished latte', 14, 153, 19, GOLD)
    frame.paste(preview, (15, 87))
    rows = (
        ('Picture', '#b0ccab', [(111,72), (188,154)]),
        ('Dialogue', '#9dc9ca', [(111,131), (248,94)]),
        ('Captions', GOLD, [(caption_left,64), (278,64)]),
        ('Music', '#c79673', [(111,231)]),
        ('Overlays', MINT, [(183,91)]),
    )
    for i, (name, color, blocks) in enumerate(rows):
        y = y_min+45*i
        type_at(frame, (15, y+16), name, 16, PAPER, 'lm')
        draw.rounded_rectangle((x0, y, x1, y+31), 5, fill='#39564c')
        opacity = ease(progress(t, .05+.13*i, .37+.13*i))
        for left, width in blocks:
            if opacity > 0:
                draw.rounded_rectangle((left, y+4, left+width*opacity, y+27), 4, fill=color)
                if i in (1, 3) and width*opacity > 19:
                    for dx in range(8, int(width*opacity)-5, 7):
                        height = 4+5*abs(sin(dx*.43))
                        draw.line((left+dx, y+15-height, left+dx, y+15+height), fill='#5b7164', width=2)
    playhead(draw, t, x0, x1, 320, 551, PAPER)
    type_at(frame, (18, 580), 'Move only the caption' if t < 2.04 else 'Picture and audio stay put',
            23, GOLD, 'lm')
    return frame


def portrait_payoff_montage(t):
    if t < .52:
        stamp = 2.53+.75*t
        return crop(source('coffee-live', stamp), (127, 0, 329.5, 360))
    if t < 1.01:
        return shot('walk-live', .41+1.08*(t-.52), x=-10, size=SIZE)
    if t < 1.50:
        center = 330+30*ease(progress(t, 1.01, 1.50))
        return crop(source('notebook-live', t-.81), (center-101.25, 0, center+101.25, 360))
    frame = shot('portrait-live', .25+(t-1.50)*.89, size=SIZE)
    tag(frame, 'Let’s cut a morning', 18, 461, 28)
    tag(frame, 'in three shots.', 18, 510, 28)
    return frame


STEP_APPROACH = .65
STEP_CONTACT = .70


def step_proof(stamp, tight=False):
    pane = (132, 39, 312.5625, 360) if tight else (110, 0, 312.5, 360)
    return crop(source('steps-live', stamp), pane)


def portrait_proof_burst(t):
    replay = t >= 2.15
    if t < .57 or replay:
        elapsed = t-2.15 if replay else t
        stamp = round((.60+elapsed/1.5)*FRAME_RATE)/FRAME_RATE
        if replay:
            stamp = min(stamp, STEP_CONTACT)
        landed = stamp >= STEP_CONTACT
        frame = step_proof(stamp, tight=landed)
        tag(frame, 'Cut on contact', 17, 54, 23, GOLD if landed else None)
        if replay and landed:
            tag(frame, 'Edit point  0.70s', 17, 516, 21, MINT)
        return frame
    if t < 1.72:
        before = t < 1.13
        frame = step_proof(STEP_APPROACH if before else STEP_CONTACT)
        tag(frame, 'The sole is still in the air' if before else 'The sole meets the ground',
            17, 54, 23, None if before else GOLD)
        tag(frame, 'Source  0.65s' if before else 'Source  0.70s', 17, 516, 21)
        return frame
    frame = Image.new('RGB', SIZE, '#182c26')
    for i, (stamp, label) in enumerate(((STEP_APPROACH, '0.65s  Before contact'), (STEP_CONTACT, '0.70s  First contact'))):
        y = i*300
        proof = shot('steps-live', stamp, 1.29, -95, 18, (W, 240))
        frame.paste(proof, (0, y+53))
        type_at(frame, (17, y+28), label, 22, PAPER if i == 0 else GOLD, 'lm')
    return frame


def portrait_slow_push(t):
    return_to_wide = t >= 2.66
    stamp = .11+t*.89
    eye_x, eye_y = face_track(stamp)
    point = 0 if return_to_wide else ease(progress(t, .31, 2.58))
    ratio = .55-.084*point
    left = eye_x-176*ratio
    top = eye_y-91*ratio
    frame = crop(source('host-live', stamp), (left, top, left+W*ratio, top+H*ratio))
    if return_to_wide:
        tag(frame, 'Back to the wide shot', 17, 511, 24)
    else:
        tag(frame, 'Let the pause land.', 17, 462, 25)
        tag(frame, f'Gradual push  {round(100*.55/ratio)}%', 17, 516, 19, MINT)
    return frame


def portrait_punch_in(t):
    tight = .90 <= t < 1.76
    stamp = 1.65+.83*t if t < 1.76 else .68*(t-1.76)+.46
    face = source('portrait-live', stamp)
    frame = crop(face, (17, 14, 188, 318)) if tight else face.resize(SIZE, Image.Resampling.LANCZOS)
    if tight:
        tag(frame, 'Exactly.', 17, 511, 30, GOLD)
    elif t < .90:
        tag(frame, 'Wait for the reaction.', 17, 511, 24)
    else:
        tag(frame, 'Then finish the thought.', 17, 511, 24)
    return frame


SCENES = {
    'subject-locked-reframe': subject_locked,
    'vertical-safe-zone': safe_zone,
    'visual-match-cut': visual_match,
    'tracked-callout': tracked_callout,
    'gesture-triggered-vfx': visible_gesture,
    'ar-wayfinding': visible_wayfinding,
    'typography-tunnel': portrait_tunnel,
    'icon-and-text-insert': portrait_icon,
    'intro-outro-pair': portrait_title_pair,
    'long-cold-open': portrait_cold_open,
    'long-payoff-back': portrait_payoff,
    'comparative-chart': portrait_comparison,
    'motion-synced-sound': portrait_sound_contact,
    'blur-slide-caption': slide_phrase,
    'rolling-letter-reveal': rolling_title,
    'projected-hud': portrait_hud,
    'floating-interface-layers': portrait_interface_layers,
    'floating-screen': portrait_floating_screen,
    'floating-notification': portrait_notification,
    'floating-card-carousel': portrait_card_carousel,
    'screen-replacement': portrait_screen_replacement,
    'tracked-chat-bubbles': portrait_chat,
    'curved-tracked-text': portrait_curved,
    'stylized-silhouette': portrait_silhouette,
    'world-anchored-graphic': portrait_room_graphic,
    'world-anchored-type': portrait_floor_type,
    'grounded-particle-overlay': portrait_grounded_particles,
    'side-by-side-callout': portrait_split_explanation,
    'side-by-side-reference': portrait_synced_compare,
    'product-orbit': portrait_product_orbit,
    'picture-in-picture-demo': portrait_pip,
    'ducked-music': portrait_ducked,
    'layered-sound-design': portrait_layered_sound,
    'chart-tracking-marker': portrait_chart_marker,
    'map-evidence-annotation': portrait_map_evidence,
    'document-highlight': portrait_document,
    'timeline-first-ai-edit': portrait_timeline,
    'payoff-montage': portrait_payoff_montage,
    'short-proof-burst': portrait_proof_burst,
    'slow-push-in': portrait_slow_push,
    'punch-in': portrait_punch_in,
}
POSTERS = {
    'subject-locked-reframe': 1.49,
    'vertical-safe-zone': 1.66,
    'visual-match-cut': 1.32,
    'tracked-callout': 1.28,
    'gesture-triggered-vfx': 2.16,
    'ar-wayfinding': 1.68,
    'typography-tunnel': 1.23,
    'icon-and-text-insert': 1.69,
    'intro-outro-pair': .63,
    'long-cold-open': .91,
    'long-payoff-back': 2.14,
    'comparative-chart': 2.67,
    'motion-synced-sound': 1.14,
    'blur-slide-caption': .80,
    'rolling-letter-reveal': .89,
    'projected-hud': 1.62,
    'floating-interface-layers': 1.62,
    'floating-screen': 1.88,
    'floating-notification': 1.33,
    'floating-card-carousel': 1.03,
    'screen-replacement': 1.64,
    'tracked-chat-bubbles': 1.74,
    'curved-tracked-text': 1.27,
    'stylized-silhouette': .73,
    'world-anchored-graphic': 2.31,
    'world-anchored-type': 1.53,
    'grounded-particle-overlay': 1.66,
    'side-by-side-callout': 1.88,
    'side-by-side-reference': 1.32,
    'product-orbit': 1.28,
    'picture-in-picture-demo': 1.98,
    'ducked-music': 1.47,
    'layered-sound-design': 1.83,
    'chart-tracking-marker': 1.26,
    'map-evidence-annotation': 1.73,
    'document-highlight': 1.62,
    'timeline-first-ai-edit': 2.17,
    'payoff-montage': .18,
    'short-proof-burst': 1.89,
    'slow-push-in': 1.79,
    'punch-in': 1.08,
}
