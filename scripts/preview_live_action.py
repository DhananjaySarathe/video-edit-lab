"""Finished edit examples composed over live footage and photographic plates."""
from bisect import bisect_right
from functools import lru_cache
from math import cos, degrees, pi, radians, sin

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from preview_common import H, W, ease, font, progress
from preview_plates import host_pair, shot
from preview_cuts import clip_track, crop
from preview_sound import BEAT_CUES
from preview_spatial import cursor, desk_screen, warp
from preview_typography import crosshair, place_glyph

PAPER = '#fff6e3'
MINT = '#c3ffd6'
GOLD = '#ffd56c'
INK = '#171b18'


def tween(t, start, end):
    return ease(progress(t, start, end))


def type_at(image, xy, value, size, fill=PAPER, anchor='mm', stroke=0):
    ImageDraw.Draw(image).text(xy, value, fill=fill, font=font(size),
                               anchor=anchor, stroke_width=stroke, stroke_fill='#191713')


def tag(image, value, x=18, y=18, accent=False):
    draw = ImageDraw.Draw(image)
    width = round(draw.textlength(value, font=font(14))) + 22
    draw.rounded_rectangle((x, y, x+width, y+28), 6, fill=GOLD if accent else '#202622')
    type_at(image, (x+11, y+14), value, 14, INK if accent else PAPER, 'lm')


def behind_subject(t):
    raw, matte = host_pair(t)
    p = tween(t, .42, .93)
    if p == 0:
        tag(raw, 'Before')
        return raw
    image = ImageEnhance.Brightness(raw).enhance(1-.32*p)
    text = Image.new('RGBA', (W, H))
    y = 98+42*(1-p)
    type_at(text, (166, y), 'LESS', 82, GOLD)
    type_at(text, (488, y), 'NOISE', 80, GOLD)
    ImageDraw.Draw(text).line((45, y+49, 595, y+49), fill=GOLD, width=3)
    text.putalpha(text.getchannel('A').point(lambda a: int(a*p)))
    image.paste(text, (0, 0), text)
    image.paste(raw, (0, 0), matte)
    tag(image, 'Text behind the speaker', accent=True)
    return image


def vertical_safe(t):
    panel_w, panel_h = 174, 310
    image = Image.new('RGB', (W, H), '#181f1e')
    for x, safe in ((128, False), (338, True)):
        panel = shot('portrait-live', t, size=(panel_w, panel_h))
        y = round(287-55*tween(t,.51,1.31)) if safe else 287
        draw = ImageDraw.Draw(panel, 'RGBA')
        draw.rounded_rectangle((10, y-13, 149, y+13), 5, fill=(17, 22, 20, 225))
        type_at(panel, (80, y), 'It saves time', 18, MINT if safe else PAPER)
        show_ui = not safe or t < 2.79
        if safe and show_ui:
            draw.rounded_rectangle((5, 40, 139, 258), radius=8, outline=(181, 245, 171, 225), width=1)
        if show_ui:
            draw.rectangle((0, 271, 174, 311), fill=(15, 19, 21, 157))
            for radius, cy in ((6, 191), (6, 214), (6, 238)):
                draw.ellipse((154-radius, cy-radius, 154+radius, cy+radius), outline=(255, 251, 239, 215), width=2)
            draw.line((13, 294, 105, 294), fill=(255, 252, 242, 202), width=2)
            draw.line((13, 302, 77, 302), fill=(255, 252, 242, 170), width=2)
        image.paste(panel, (x, 37))
        tag(image, 'Export crop' if not show_ui else 'Inside safe area' if safe else 'Under app controls', x, 5, safe)
    return image


def emphasis(t):
    image = shot('host-live', t, 1.11, -32, -12)
    if t < .72:
        prefix, word, suffix, p = 'Take', 'one', 'tip', 0
    elif t < 2.37:
        prefix, word, suffix, p = 'Save', '10×', 'more time', tween(t, .72, .93)
    else:
        prefix, word, suffix, p = 'Start', 'here', '', tween(t, 2.37, 2.54)
    draw = ImageDraw.Draw(image, 'RGBA')
    word_size = round(32 + 34*p)
    widths = [draw.textlength(prefix, font=font(29)), draw.textlength(word, font=font(word_size)),
              draw.textlength(suffix, font=font(29))]
    width = sum(widths) + 36
    x = (W-width)/2
    draw.rounded_rectangle((x-14, 237, x+width+10, 307), 9, fill=(17, 20, 18, 215))
    type_at(image, (x, 273), prefix, 29, anchor='lm')
    type_at(image, (x+widths[0]+12, 271), word, word_size, GOLD, 'lm')
    type_at(image, (x+widths[0]+widths[1]+24, 273), suffix, 29, anchor='lm')
    return image


def face_track(t):
    # Center of the glasses from a manual track of this source clip.
    points = ((266, 54), (256, 54), (268, 55), (280, 57),
              (277, 54), (278, 55), (278, 56))
    frame = min(t*2, len(points)-1.001)
    i = int(frame)
    fraction = frame - i
    return tuple(round(a+(b-a)*fraction) for a, b in zip(points[i], points[i+1]))


def tracked_face(t):
    image = shot('host-live', t)
    x, y = face_track(t)
    draw = ImageDraw.Draw(image)
    for a, b in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        draw.line([(x+21*a, y+32*b), (x+34*a, y+32*b), (x+34*a, y+20*b)], fill=MINT, width=2)
    offset = (x+83, y+65)
    draw.line((x+36, y+29, *offset, offset[0]+23, offset[1]), fill=MINT, width=2)
    tag(image, 'Eyes in focus', offset[0]+23, offset[1]-14, True)
    return image


def silhouette(t):
    raw, matte = host_pair(t)
    if t < .72 or t >= 2.55:
        return raw
    image = Image.new('RGB', (W, H), '#f4c56a')
    draw = ImageDraw.Draw(image)
    for i in range(10):
        y = (i*52 + round(t*122)) % 520 - 90
        draw.polygon(((0, y+72), (640, y), (640, y+11), (0, y+94)),
                     fill=('#ec7f53', '#fcdf96', '#d9934a')[i % 3])
    type_at(image, (320, 132), 'CUT THE NOISE', 74, '#562318')
    shadow = ImageOps.colorize(raw.convert('L'), '#201a2b', '#69403b')
    image.paste(shadow, (0, 0), matte)
    type_at(image, (320, 296), 'Make one point.', 34, PAPER, stroke=2)
    return image


def anchored(t):
    # Apply a single camera move to the room plate and the composited world layer.
    stage = shot('room')
    p = tween(t, .25, 1.04)
    fade = 1-tween(t, .86, 1.4)
    if fade > 0:
        orb_layer(stage, t, (391, 145), 44, p*fade)
    if p > .38:
        card = Image.new('RGBA', (300, 150), (17, 23, 43, 225))
        draw = ImageDraw.Draw(card)
        draw.rounded_rectangle((1, 1, 298, 148), 8, outline='#a7c9ff', width=2)
        type_at(card, (16, 22), 'Average watch time', 18, '#eff7ff', 'lm')
        for y in (55, 78, 102, 126):
            draw.line((21, y, 280, y), fill=(120, 150, 183, 98))
        points = [(23, 122), (64, 113), (102, 115), (143, 93), (183, 97), (225, 68), (274, 53)]
        path = tween(t, 1.0, 2.18)*(len(points)-1)
        whole = int(path)
        final = points[-1]
        if whole < len(points)-1:
            a, b = points[whole], points[whole+1]
            final = tuple(i+(j-i)*(path-whole) for i, j in zip(a, b))
        draw.line([*points[:whole+1], final], fill='#83efef', width=4, joint='curve')
        x, y = final
        draw.ellipse((x-5, y-5, x+5, y+5), fill='#f7fdff', outline='#83efef', width=2)
        if t >= 2.18:
            type_at(card, (272, 35), '+18%', 24, '#bbffd5', 'rm')
        w = 154*p
        h = 77*p
        warp(stage, card, [(391-w, 145-h), (391+w, 145-h-13),
                           (391+w+4, 145+h-8), (391-w, 145+h+8)])
    scale = 1.05 + .06 * tween(t, .15, 3.2)
    cx = 320 + 12*sin(t*1.26)
    cy = 180 + 4*sin(t*1.1)
    return stage.transform((W, H), Image.Transform.EXTENT,
                           (cx-320/scale, cy-180/scale, cx+320/scale, cy+180/scale),
                           Image.Resampling.BICUBIC)


def orb_layer(image, t, center, radius, amount):
    if amount <= 0:
        return
    x, y = center
    light = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(light)
    r = radius * (.86 + .14*amount)
    draw.ellipse((x-r, y-r, x+r, y+r), fill=(round(61*amount), round(40*amount), round(120*amount)))
    image.paste(ImageChops.add(image, light.filter(ImageFilter.GaussianBlur(23))))
    glints = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(glints)
    tones = [(79, 184, 230), (121, 103, 222), (212, 152, 244), (116, 218, 244)]
    for i, tone in enumerate(tones):
        points = []
        for step in range(97):
            a = 2*pi*step/96
            px = r*cos(a)
            py = r*sin(a)*(.32 + .22*sin(t*2+i)) + 2*sin(3*a+t*4+i)
            angle = t*.8 + i*.8
            points.append((x+px*cos(angle)-py*sin(angle), y+px*sin(angle)+py*cos(angle)))
        draw.line(points, fill=tuple(int(c*amount) for c in tone), width=2)
    draw.ellipse((x-r, y-r, x+r, y+r), outline=(round(65*amount), round(125*amount), round(136*amount)), width=1)
    image.paste(ImageChops.add(image, glints.filter(ImageFilter.GaussianBlur(4))))
    image.paste(ImageChops.add(image, glints))


def orb(t):
    image = ImageEnhance.Brightness(shot('room', t, 1.12, t*6)).enhance(.73)
    orb_layer(image, t, (372 - 6*t, 159 + 5*sin(t*2)), 72, tween(t, .19, .82))
    return image


def grade_comparison(t):
    image = Image.new('RGB', (W,H), '#18211e')
    frame = shot('walk-live', t, 1.04, 2, 15, (300,287))
    original = ImageEnhance.Contrast(ImageEnhance.Color(frame).enhance(.36)).enhance(.81)
    grade = ImageEnhance.Contrast(ImageEnhance.Color(frame).enhance(1.24)).enhance(1.13)
    image.paste(original,(14,57))
    image.paste(grade,(326,57))
    tag(image, 'Before', 14, 17)
    tag(image, 'After color grade', 326, 17, True)
    return image


def b_roll(t):
    if t < .72 or t > 2.52:
        image = shot('host-live', t)
        tag(image, 'Let the milk meet the surface' if t < .72 else 'Back to the explanation')
    else:
        image = shot('coffee-live', t-.72, 1.08 + .19*tween(t, 1.0, 2.15), -19, 10)
        tag(image, 'Cutaway: milk hits the surface', accent=True)
    return image


def payoff(t):
    if t < .58:
        image = shot('coffee-live', 2.6+t, 1.18)
        tag(image, 'Show the result', accent=True)
    elif t < 1.1:
        image = shot('coffee-live', 1.8+t, 1.43, -28, 14)
        type_at(image, (320, 178), 'Clean pour', 50, stroke=2)
    else:
        image = shot('coffee-live', t-1.1)
        tag(image, 'Then show how')
    return image


def wide_detail(t):
    if t < 1.13:
        return shot('coffee-live', t)
    return shot('coffee-live', t, 1.66 if t < 2.18 else 2.15, 12, 27)


def punch(t):
    image = shot('host-live', t, 1.44, -58, -37) if .87 <= t < 2.34 else shot('host-live', t)
    if .87 <= t < 2.34:
        type_at(image, (430, 253), 'This part.', 31, GOLD, stroke=2)
    return image


def slow_push(t):
    p = tween(t, .1, 2.57) if t < 2.79 else 0
    return shot('host-live', t, 1.05 + .34*p, -52, -27)


def on_action(t):
    cut = 1.08
    if t < cut:
        image = shot('walk-live', t+.15, 1.2, -17, 21)
    else:
        image = shot('steps-live', t-cut+.57)
    clip_track(image, t, (cut,), pulses=True)
    tag(image, 'Wide: the foot swings' if t < cut else 'Close: the same step lands', accent=t >= cut)
    return image


def directional(t):
    cut = 1.31
    if t < cut:
        image = shot('steps-live', t+.2, 1.09, -12*t, 0)
    else:
        image = shot('walk-live', t-cut+1.14, 1.14, -13*(t-cut), 21)
    draw = ImageDraw.Draw(image)
    alpha = tween(t,.13,.44)*(1-tween(t,2.45,2.9))
    if alpha > .12:
        draw.rounded_rectangle((19,268,174,308),7,fill='#24372e')
        draw.line((50,286,33,286,41,279),fill=MINT,width=2)
        draw.line((33,286,41,293),fill=MINT,width=2)
        type_at(image,(61,288),'Same direction',14,anchor='lm')
    clip_track(image,t,(cut,),pulses=True)
    return image


def jump(t):
    cuts = (.77,1.54,2.31)
    i = bisect_right(cuts,t)
    src = .57*t + (0,.44,.88,1.29)[i]
    image = shot('host-live', min(3.15, src))
    tag(image, f'{src:.2f}s  Source time', accent=i > 0)
    clip_track(image,t,cuts,pulses=True)
    return image


def side_by_side(t):
    host = shot('host-live', t)
    p = tween(t,.37,.68)*(1-tween(t,2.66,3.14))
    if p < .04:
        return host
    image = Image.new('RGB',(W,H),'#202925')
    image.paste(shot('host-live',t,1.10,-32,-24,(305,327)),(10,17))
    image.paste(shot('coffee-live',t*.9,1.55,-37,10,(305,237)),(325,17))
    y = 258
    draw = ImageDraw.Draw(image)
    for i,(cue,text) in enumerate(((.54,'01  Tilt the glass'),(1.42,'02  Pour at the surface'))):
        active = t >= cue and (i == 1 or t < 1.42)
        draw.rounded_rectangle((325,y,630,y+39),7,fill=GOLD if active else '#33423a')
        type_at(image,(339,y+19),text,19,INK if active else PAPER,'lm')
        y += 45
    return Image.blend(host,image,p)


def pip(t):
    host = shot('host-live', t, 1.15, -35, -15)
    if t < .38 or t > 2.77:
        return host
    image = Image.new('RGB', (W,H), '#182422')
    draw = ImageDraw.Draw(image)
    desk_screen(draw, (34, 34, 606, 326), 'Export settings', selected=1 if t > 1.33 else -1, rows=5)
    cursor(draw, 392+47*tween(t,.77,1.4), 107+33*tween(t,.77,1.4), tween(t,1.28,1.56))
    r = round(12+49*tween(t,.39,.79))
    cut = shot('host-live', t, 2.18, -40, -85, (2*r, 2*r))
    mask = Image.new('L', cut.size)
    ImageDraw.Draw(mask).ellipse((0, 0, 2*r-1, 2*r-1), fill=255)
    at = 533-r, 250-r
    draw.ellipse((at[0]-3, at[1]-3, at[0]+2*r+3, at[1]+2*r+3), fill=PAPER)
    image.paste(cut, at, mask)
    return image


def speed_ramp(t):
    p = progress(t, .42, 2.55)
    # Smooth acceleration and deceleration through the middle of the shot.
    src = .52*t + 2.6*ease(p)
    image = shot('walk-live', src)
    speed = .52 + 2.6*6*p*(1-p)/2.13
    tag(image, f'{speed:.1f}× speed', accent=speed > 1)
    return image


def monochrome(t):
    if .77 < t < 2.28:
        return ImageOps.colorize(shot('walk-live', t).convert('L'), '#171820', '#fff8eb')
    return shot('host-live', t)


def beat(t):
    index = bisect_right(BEAT_CUES, round(t, 4))
    names = ('host-live', 'walk-live', 'coffee-live', 'steps-live')
    image = shot(names[index % len(names)], t, 1.16 if index % 2 else 1.03)
    clip_track(image,t,BEAT_CUES,pulses=True)
    return image


def stack_hook(t):
    raw, matte = host_pair(t)
    image = ImageEnhance.Brightness(raw).enhance(.57)
    image.paste(raw,(0,0),matte)
    for i,(word, size, y, tone) in enumerate((('Make the',32,126,PAPER),('ordinary',30,162,PAPER),
                                             ('CINEMATIC',50,221,GOLD))):
        p = tween(t,.19+i*.31,.52+i*.39)*(1-tween(t,2.67,3.17))
        if p > 0:
            overlay = Image.new('RGBA',(W,H))
            type_at(overlay,(610,y+19*(1-p)),word,round(size*(.8+.2*p)),tone,'rm',1)
            overlay.putalpha(overlay.getchannel('A').point(lambda a: round(a*p)))
            image.paste(overlay,(0,0),overlay)
    return image


def curved(t):
    raw, matte = host_pair(t)
    p = tween(t,.38,.9)*(1-tween(t,2.69,3.13))
    if p < .001:
        return raw
    image = ImageEnhance.Brightness(raw).enhance(1-.28*p)
    cx = 321 + 1.05*(face_track(t)[0]-267)
    phrase = 'WORDS      FOLLOW'
    for i, letter in enumerate(phrase):
        angle = radians(200+8.6*i+16*(1-p)+7*sin(t*1.5))
        x, y = cx+202*cos(angle), 226+112*sin(angle)
        place_glyph(image,letter,x,y,26,270-degrees(angle),(255,218,127))
    ImageDraw.Draw(image).arc((cx-192,131,cx+192,337),204,332,fill='#b69759',width=2)
    image.paste(raw,(0,0),matte)
    return Image.blend(raw,image,p)


def locked_reframe(t):
    result = Image.new('RGB',(W,H),'#192822')
    eye_x, eye_y = face_track(t)
    drift = 51*sin(t*2.65)
    for left, x in ((True,13),(False,328)):
        frame_x = 267+drift if left else eye_x
        center_offset = (frame_x-320)*1.24*290/301
        frame = shot('host-live',t,1.24,center_offset,-34,(299,278))
        draw = ImageDraw.Draw(frame)
        cx = 149+((eye_x-frame_x)*1.18 if left else 0)
        crosshair(draw,round(cx),round(65+(eye_y-54)*1.15), (255,210,106) if left else (178,251,212),22)
        if not left:
            draw.line((149,0,149,35),fill=(176,239,189),width=2)
        result.paste(frame,(x,60))
        tag(result,'Original camera drift' if left else 'Face stays centered',x,17,not left)
    return result


def room_move(image,t):
    return crop(image,1.02+.21*tween(t,0,3.2),345+36*sin(t*1.24),211)


def floor_type(t):
    image = shot('room')
    p = tween(t,.38,.93)
    title = Image.new('RGBA',(410,115))
    type_at(title,(207,55),'THE STUDIO',66,(249,237,207,round(p*245)))
    warp(image,title,[(239,263),(473,270),(561,335),(146,326)])
    return room_move(image,t)


def dust(t):
    image = shot('room')
    p = tween(t,.42,1.25)
    x0,y0 = 392,296
    layer = Image.new('RGBA',(W,H))
    draw = ImageDraw.Draw(layer)
    for i in range(38):
        clock = .18*(i%9)
        age = (t+clock)%1.76
        r = 12+17*age
        spread = (14+16*age)*sin(i*2.7+t*.6)
        x = x0+spread+17*age
        y = y0-49*age-8*sin(i)
        strength = round(58*p*sin(pi*progress(age,0,1.76))**2)
        draw.ellipse((x-r,y-r*.5,x+r,y+r*.5), fill=(236,222,186,strength))
    layer = layer.filter(ImageFilter.GaussianBlur(11))
    image.paste(layer,(0,0),layer)
    draw = ImageDraw.Draw(image,'RGBA')
    for i in range(52):
        a = (t + i*.072) % 1.94
        x = x0 + 29*a + sin(i*6.7+t*.6)*40*a
        y = y0 - 45*a + 7*sin(i*2.3)
        r = 1+.92*(i%3)/2
        draw.ellipse((x-r,y-r,x+r,y+r),fill=(250,225,177,round(171*p*sin(pi*a/1.94)**2)))
    return room_move(image,t)


def gesture(t):
    # Keyframes from the raised hand in the original shot.
    keyframes = ((1.84,255,199),(2.0,240,197),(2.2,201,182),(2.39,159,198),
                 (2.58,173,209),(2.75,206,214))
    source_t = 1.23+.5*t
    image = shot('host-live',source_t)
    p = tween(source_t,1.87,2.13)*(1-tween(source_t,2.48,2.73))
    if p <= 0:
        return image
    index = min(len(keyframes)-2,max(0,bisect_right([key[0] for key in keyframes],source_t)-1))
    a,b = keyframes[index:index+2]
    f = progress(source_t,a[0],b[0])
    x,y = a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f
    fx = Image.new('RGB',(W,H))
    draw = ImageDraw.Draw(fx)
    for j in range(8):
        angle = j*pi/4 + t*1.5
        radius = (7+(j%3)*8)*p
        dx,dy = radius*cos(angle),radius*sin(angle)
        draw.line((x+dx*.13,y+dy*.13,x+dx,y+dy),fill=(round(251*p),round(184*p),round(97*p)),width=2)
    draw.ellipse((x-4,y-4,x+4,y+4),fill='#ffefae')
    image = ImageChops.add(image, fx.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255,round(v*1.9))))
    return ImageChops.add(image, fx)


def match_shape(t):
    cut = 1.4
    if t < cut:
        image = Image.new('RGB',(W,H),'#1c252c')
        draw = ImageDraw.Draw(image)
        x = 252+42*(1-tween(t,.05,1.11))
        draw.ellipse((x-61,195,x+61,239), fill='#ddb481',outline='#faf0c3',width=4)
        if t < 1.07:
            tag(image,'Ellipse in a title card')
            type_at(image,(x,275),'THE MORNING EDIT',22)
    else:
        image = shot('coffee-live',2.59+(t-cut)*.55)
        tag(image,'Same shape: the rim',accent=True)
    return image


def smash_cut(t):
    if t < .42:
        image = shot('steps-live',t*1.6,1.25)
    elif t < .84:
        image = shot('coffee-live',t,1.65,-46,8)
    elif t < 1.17:
        image = shot('walk-live',t,1.30,-17,9)
    else:
        image = ImageEnhance.Color(shot('room',t,1.05)).enhance(.72)
    return image


def variable_pace(t):
    cuts=(.38,.78,1.2)
    i = bisect_right(cuts,t)
    names=('walk-live','steps-live','coffee-live','coffee-live')
    image = shot(names[i],t if i < 3 else 2.31+.46*(t-1.2),1.22 if i < 3 else 1.05)
    tag(image,'Quick setup' if i < 3 else 'Hold on the result',accent=i == 3)
    clip_track(image,t,cuts,pulses=True)
    return image


def diagonal(t):
    a,b = shot('walk-live',t,1.07),shot('steps-live',t)
    p = tween(t,.83,2.04)
    x = -188+1016*p
    mask = Image.new('L',(W,H))
    ImageDraw.Draw(mask).polygon(((0,0),(x,0),(x-188,H),(0,H)),fill=255)
    a.paste(b,(0,0),mask.filter(ImageFilter.GaussianBlur(2.5)))
    return a


def zoom_cutout(t):
    raw, mask = host_pair(t)
    if t < .51:
        return raw
    p = tween(t,.51,1.47)
    q = 1-tween(t,1.47,2.36)
    replacing = t >= 1.47
    next_shot = shot('host-live',t,1.36,-36,-36)
    background = ImageEnhance.Color(next_shot).enhance(.44) if replacing else raw.copy()
    if q > .001:
        zoom = 1+2.5*p*q
        layer = crop(raw,zoom,317,111)
        matte = crop(mask,zoom,317,111)
        if not replacing:
            border = matte.filter(ImageFilter.MaxFilter(7))
            background.paste('#ffe7ad',(0,0,W,H),border)
        matte = matte.point(lambda v: round(v*(q if replacing else 1)))
        background.paste(layer,(0,0),matte)
    return background


def pull_in(t):
    cut = 1.54
    if t < cut:
        image = shot('walk-live',t,1.14,0,-9)
        zoom = 1+2.1*tween(t,1.0,cut)
        return crop(image,zoom,335,159)
    image = shot('room')
    zoom = 1+1.9*(1-tween(t,cut,2.13))
    return crop(image,zoom,321,154)


def chat(t):
    raw, matte = host_pair(t)
    image = ImageEnhance.Brightness(raw).enhance(.77)
    x_face, _ = face_track(t)
    shift = (x_face-266)*.85
    messages = (
        (.34, 31, 119, 192, 'Ready to record?', '#f7eedc'),
        (.99, 379, 170, 228, 'Ready when you are.', '#d0f0d2'),
        (1.67, 29, 237, 129, 'Let’s go.', '#f7eedc'),
    )
    overlay = Image.new('RGBA',(W,H))
    for start, x, y, width, value, color in messages:
        p = tween(t,start,start+.33)*(1-tween(t,2.71,3.12))
        if p <= 0:
            continue
        canvas = Image.new('RGBA',(width,60))
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle((0,0,width-2,46),9,fill=color)
        tip = width-26 if x < 320 else 14
        d.polygon(((tip-8,42),(tip+9,42),(tip+6,55)),fill=color)
        type_at(canvas,(16,24),value,19,INK,'lm')
        canvas.putalpha(canvas.getchannel('A').point(lambda a: round(a*p)))
        overlay.paste(canvas,(round(x+shift),round(y+(1-p)*18)),canvas)
    image.paste(overlay,(0,0),overlay)
    image.paste(raw,(0,0),matte)
    return image


@lru_cache(maxsize=1)
def cup_cutout():
    frame = shot('coffee-live',2.6)
    alpha = Image.new('L',(W,H))
    ImageDraw.Draw(alpha).polygon(((192,219),(194,210),(205,202),(222,197),(248,195),
                                   (272,196),(292,200),(307,207),(313,218),(311,230),
                                   (304,243),(295,256),(287,268),(277,278),(275,294),
                                   (264,309),(248,316),(229,313),(219,305),(218,287),
                                   (209,269),(203,249),(195,231)),fill=255)
    frame = frame.convert('RGBA')
    frame.putalpha(alpha.filter(ImageFilter.GaussianBlur(1.0)))
    return frame.crop((188,190,317,319))


def product_orbit(t):
    image = ImageEnhance.Brightness(shot('room',t,1.07)).enhance(.46)
    draw = ImageDraw.Draw(image)
    tag(image,'Latte details',accent=True)
    draw.ellipse((130,116,510,296),outline='#bfbc95',width=1)
    p = tween(t,.34,2.55)
    shots = (
        ('Pour',.52,(125,15,370,190)),
        ('Texture',1.37,(175,124,354,239)),
        ('Finish',2.61,(197,190,321,277)),
    )
    objects = []
    for i,(label,stamp,window) in enumerate(shots):
        a = i*2*pi/3 + 3.0*p + .15
        z = sin(a)
        w = int(101+24*z)
        h = int(66+17*z)
        surface = shot('coffee-live',stamp).crop(window).resize((w,h),Image.Resampling.LANCZOS)
        tile = Image.new('RGBA',(w+10,h+29),'#f5e9cb')
        tile.paste(surface,(5,5))
        type_at(tile,((w+10)/2,h+17),label,14,INK)
        intensity = .66+.34*(z+1)/2
        tile.putalpha(round(255*intensity*tween(t,.12+i*.18,.56+i*.19)))
        objects.append((z,tile,320+180*cos(a)-(w+10)/2,205+82*z-(h+29)/2))
    hero = cup_cutout().resize((183,183),Image.Resampling.LANCZOS)
    objects.append((0,hero,228,110))
    for _,asset,x,y in sorted(objects,key=lambda item:item[0]):
        image.paste(asset,(round(x),round(y)),asset)
    return image


SCENES = {
    'text-behind-subject': behind_subject,
    'vertical-safe-zone': vertical_safe,
    'caption-hierarchy': emphasis,
    'tracked-callout': tracked_face,
    'stylized-silhouette': silhouette,
    'world-anchored-graphic': anchored,
    'glowing-orb': orb,
    'payoff-montage': payoff,
    'side-by-side-reference': grade_comparison,
    'side-by-side-callout': side_by_side,
    'picture-in-picture-demo': pip,
    'explanatory-b-roll': b_roll,
    'detail-sequence': wide_detail,
    'punch-in': punch,
    'slow-push-in': slow_push,
    'cut-on-action': on_action,
    'motion-flow-cut': directional,
    'intentional-jump-cut': jump,
    'speed-ramp': speed_ramp,
    'monochrome-flashback': monochrome,
    'beat-synced-cuts': beat,
    'stacked-hook-text': stack_hook,
    'curved-tracked-text': curved,
    'subject-locked-reframe': locked_reframe,
    'world-anchored-type': floor_type,
    'grounded-particle-overlay': dust,
    'gesture-triggered-vfx': gesture,
    'visual-match-cut': match_shape,
    'smash-cut': smash_cut,
    'variable-pacing': variable_pace,
    'diagonal-mask-wipe': diagonal,
    'cutout-match-zoom': zoom_cutout,
    'pull-in-transition': pull_in,
    'tracked-chat-bubbles': chat,
    'product-orbit': product_orbit,
}
