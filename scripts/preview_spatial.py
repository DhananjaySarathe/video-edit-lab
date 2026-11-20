"""Original 3.2-second demonstrations of spatial graphics and screen edits."""

from functools import lru_cache
from math import cos, pi, sin
from PIL import Image, ImageDraw, ImageFilter
from preview_plates import paste_host, shot
from preview_common import W, H, blend, ease, font, progress

INK = (24, 43, 43)
DARK = (12, 31, 36)
NIGHT = (34, 60, 62)
FOREST = (52, 87, 72)
SAGE = (164, 191, 162)
MINT = (199, 222, 193)
PALE = (225, 234, 215)
CREAM = (247, 244, 227)
PAPER = (246, 246, 237)
GOLD = (241, 194, 109)
PEACH = (233, 155, 119)
CLAY = (175, 105, 83)
LINE = (200, 215, 203)
MUTED = (104, 130, 117)
BLUE = (123, 188, 211)


def tween(t, start, end):
    return ease(progress(t, start, end))


def point(x, y, r):
    return (x - r, y - r, x + r, y + r)


def mix_at(a, b, p):
    return tuple(x + (y - x) * p for x, y in zip(a, b))


def label(draw, value, pos, size=16, fill=INK, weight="bold", anchor="la"):
    draw.text(pos, value, fill=fill, font=font(size, weight), anchor=anchor)


def rounded(draw, box, fill, radius=13, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, value, x, y, bg=CREAM, fg=INK, width=None):
    width = width or int(draw.textlength(value, font=font(13))) + 22
    rounded(draw, (x, y, x + width, y + 26), bg, 8)
    label(draw, value, (x + width / 2, y + 13), 13, fg, anchor="mm")


@lru_cache(maxsize=20)
def _background(top, bottom, grid):
    image = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(image)
    for y in range(H):
        draw.line((0, y, W, y), fill=blend(top, bottom, y / H))
    if grid:
        tone = blend(top, bottom, 0.62)
        for x in range(20, W, 24):
            for y in range(20, H, 24):
                draw.ellipse(point(x, y, 0.75), fill=tone)
    return image


def board(top=DARK, bottom=NIGHT, grid=False):
    return _background(top, bottom, grid).copy()


def studio():
    image = board((19, 45, 47), (40, 68, 61))
    draw = ImageDraw.Draw(image)
    draw.ellipse((375, -100, 683, 212), outline=(67, 91, 77), width=1)
    draw.ellipse((402, -75, 655, 179), outline=(67, 91, 77), width=1)
    draw.polygon([(0, 235), (182, 199), (449, 222), (640, 176), (640, 360), (0, 360)], fill=(23, 48, 46))
    draw.line((0, 292, W, 246), fill=(63, 83, 69), width=1)
    return image, draw


def spark(draw, x, y, radius, fill, width=2):
    draw.line((x - radius, y, x + radius, y), fill=fill, width=width)
    draw.line((x, y - radius, x, y + radius), fill=fill, width=width)


def glow(image, center, radius, color, strength=140):
    if radius < 1 or strength <= 0:
        return
    overlay = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(overlay)
    draw.ellipse(point(*center, radius * 0.72), fill=(*color, strength))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius / 3))
    image.paste(overlay, (0, 0), overlay)


def line_to(draw, vertices, portion, color, width=3):
    if portion <= 0:
        return
    lengths = [((x2-x1)**2 + (y2-y1)**2)**0.5 for (x1, y1), (x2, y2) in zip(vertices, vertices[1:])]
    remaining = sum(lengths) * min(portion, 1)
    for a, b, distance in zip(vertices, vertices[1:], lengths):
        if remaining <= 0:
            break
        draw.line((a, mix_at(a, b, min(1, remaining / max(0.01, distance)))), fill=color, width=width)
        remaining -= distance


def smartphone(draw, x, y, scale=1, light=False):
    width, height = 118 * scale, 212 * scale
    box = (x - width / 2, y - height / 2, x + width / 2, y + height / 2)
    rounded(draw, box, (26, 42, 43), int(19 * scale), (103, 132, 116), max(1, int(2 * scale)))
    sx, sy = x - width / 2 + 7 * scale, y - height / 2 + 9 * scale
    rounded(draw, (sx, sy, sx + width - 14 * scale, sy + height - 18 * scale), PAPER if light else (43, 65, 60), int(12 * scale))
    rounded(draw, (x - 17 * scale, sy + 3 * scale, x + 17 * scale, sy + 8 * scale), INK, 3)
    return (sx, sy, sx + width - 14 * scale, sy + height - 18 * scale)


def small_card(draw, box, title, subtype, tint=CREAM, state=FOREST):
    l, top, r, b = box
    rounded(draw, (l + 5, top + 7, r + 5, b + 7), (24, 46, 45), 12)
    rounded(draw, box, tint, 12)
    draw.ellipse(point(l + 25, top + 22, 8), fill=state)
    label(draw, title, (l + 42, top + 16), 14)
    label(draw, subtype, (l + 16, b - 22), 12, MUTED, "regular")


def desk_screen(draw, box, title="Workspace", selected=-1, accent=FOREST, rows=4):
    l, top, r, b = box
    rounded(draw, box, PAPER, 12, LINE)
    draw.line((l, top + 31, r, top + 31), fill=LINE)
    for i, color in enumerate((PEACH, GOLD, SAGE)):
        draw.ellipse(point(l + 15 + 11*i, top + 15, 2.5), fill=color)
    label(draw, title, (l + 54, top + 9), 12, MUTED)
    draw.rectangle((l + 9, top + 38, l + 82, b - 9), fill=PALE)
    for i in range(4):
        draw.rounded_rectangle((l + 20, top + 54 + i * 25, l + 63, top + 58 + i * 25), radius=2, fill=MUTED)
    label(draw, "Overview", (l + 100, top + 45), 21, INK, "serif")
    for i, item in enumerate(("Project title", "Export preset", "Frame size", "Advanced", "Output folder")[:rows]):
        y = top + 83 + i * 32
        if y + 25 >= b:
            break
        rounded(draw, (l + 98, y, r - 14, y + 25), accent if i == selected else PALE, 5)
        label(draw, item, (l + 110, y + 5), 12, CREAM if i == selected else INK, "regular")
        if i == selected:
            label(draw, "Selected", (r - 25, y + 12), 10, CREAM, "regular", "rm")
    return l + 98, top + 115, r - 14, top + 140


def cursor(draw, x, y, p=0):
    if p:
        draw.ellipse(point(x, y, 13 * p + 5), outline=GOLD, width=2)
    draw.polygon([(x,y), (x+3,y+18), (x+8,y+13), (x+13,y+17), (x+16,y+13), (x+10,y+10), (x+17,y+7)], fill=INK, outline=CREAM, width=1)


def tracked_callout(t):
    image, draw = studio()
    x = 254 + 64 * sin(t * 1.82)
    y = 184 - 15 * sin(t * 2.2)
    draw.ellipse((x-84, 268, x+86, 286), fill=(14, 32, 32))
    rounded(draw, (x-70, y-31, x+71, y+59), (137, 161, 135), 21)
    rounded(draw, (x-50, y-44, x+3, y-30), SAGE, 6)
    draw.ellipse(point(x + 13, y + 11, 39), fill=(27, 52, 54), outline=MINT, width=2)
    draw.ellipse(point(x + 13, y + 11, 28), fill=(65, 104, 107), outline=(112, 153, 147), width=2)
    draw.ellipse(point(x + 13, y + 11, 18), fill=(18, 48, 58))
    draw.arc(point(x + 13, y + 11, 13), 203, 300, fill=BLUE, width=3)
    p = tween(t, .24, .7)
    if p > 0:
        line_to(draw, [(x+13, y+11), (x+83, y-71), (x+120, y-71)], p, GOLD, 2)
        draw.ellipse(point(x + 13, y + 11, 5), outline=GOLD, width=2)
        if p > .8:
            pill(draw, "Prime lens", x+118, y-83, CREAM)
    return image


def projected_hud(t):
    im, d = studio()
    x, y = 315, 248
    smartphone(d, x, y, .63)
    tap = tween(t, .1, .6)
    d.line((158, 312, x - 36 + 36*tap, y + 40 - 37*tap), fill=(211, 150, 112), width=17)
    d.ellipse(point(x - 36 + 36*tap, y + 40 - 37*tap, 10), fill=(236, 173, 132))
    p = tween(t, .58, 1.13) * (1-tween(t, 2.72, 3.18))
    if p > 0:
        glow(im, (x, 233), 38 * p, MINT)
        panel = Image.new('RGBA', im.size)
        a = ImageDraw.Draw(panel)
        a.polygon([(x-30,233), (166,110), (474,110), (x+30,233)], fill=(*SAGE, int(33*p)))
        y0 = 78 + 28 * (1-p)
        rounded(a, (163, y0, 477, y0 + 111*p), (*FOREST, int(215*p)), 12, (*MINT, int(230*p)), 2)
        if p > .56:
            label(a, "Field monitor", (183, y0+16), 17, CREAM)
            a.line([(184+i*12, y0+72 + 13*sin(i*1.1+t*5)) for i in range(15)], fill=(*MINT, 240), width=3)
            for idx, value in enumerate(("SIGNAL", "STABLE")):
                if t > 1.05 + idx * .23:
                    label(a, value, (370, y0+40+idx*21), 11, GOLD, "mono")
        im.paste(panel, (0,0), panel)
    return im


def architectural_shot(t):
    im = board((191, 210, 184), (218, 216, 180))
    d = ImageDraw.Draw(im)
    shift = -55 + 104*tween(t, 0, 3.16)
    vp = 320 + shift * .55
    d.polygon([(0, 132), (vp, 211), (640, 135), (640, 360), (0, 360)], fill=(166, 189, 147))
    d.polygon([(vp-7, 177), (vp+24, 177), (585 + shift, 360), (93 + shift, 360)], fill=(228, 216, 181))
    for h in (206, 235, 273, 318, 358):
        k = (h - 177)/183
        d.line((vp-7 + (93+shift - vp+7)*k, h, vp+24 + (585+shift - vp-24)*k, h), fill=(196, 187, 155), width=2)
    d.polygon([(0, 0), (vp, 59), (vp, 177), (0, 260)], fill=(59, 92, 74))
    d.polygon([(vp+24, 59), (W, 5), (W, 261), (vp+24, 177)], fill=(97, 126, 94))
    for side in (-1, 1):
        for i in range(1, 5):
            x = vp + side * (32 + i * i * 14) + (24 if side == 1 else 0)
            y = 59 - i*i*3
            d.line((x, y, x, 177+i*i*5), fill=(123, 150, 111), width=i)
    d.rectangle((vp, 60, vp+24, 179), fill=(235, 226, 195))
    return im, d, shift, vp


def solve(matrix, values):
    rows = [row + [value] for row, value in zip(matrix, values)]
    size = len(values)
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(rows[row][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        factor = rows[col][col]
        rows[col] = [a / factor for a in rows[col]]
        for i, row in enumerate(rows):
            if i != col:
                ratio = row[col]
                rows[i] = [a - ratio*b for a,b in zip(row, rows[col])]
    return [row[-1] for row in rows]


def warp(im, asset, quad):
    w, h = asset.size
    vertices = [(0,0), (w,0), (w,h), (0,h)]
    equations, target = [], []
    for (x,y), (u,v) in zip(quad, vertices):
        equations += [[x,y,1,0,0,0,-x*u,-y*u], [0,0,0,x,y,1,-x*v,-y*v]]
        target += [u,v]
    pane = asset.transform(im.size, Image.Transform.PERSPECTIVE, solve(equations, target), Image.Resampling.BICUBIC)
    im.paste(pane,(0,0),pane)


def world_anchored_graphic(t):
    im, d, shift, _ = architectural_shot(t)
    x = 192 + shift
    top = 77 + 0.11 * shift
    sign = Image.new("RGBA", (210, 99), (*CREAM, 255))
    s = ImageDraw.Draw(sign)
    label(s, "BOTANICAL", (18, 16), 20, FOREST, "serif")
    label(s, "House A", (19, 48), 27, INK)
    s.line((17, 85, 193, 85), fill=MUTED, width=2)
    warp(im, sign, [(x-80,top-10),(x+83,top+19),(x+83,top+99),(x-80,top+120)])
    pole_x = W * (1 - tween(t, .15, 3.12)) + 20
    d.polygon([(pole_x-16,0), (pole_x+8,0), (pole_x+5,360), (pole_x-18,360)], fill=(75, 101, 78))
    d.line((pole_x-13,0,pole_x-15,360),fill=(123, 145, 104),width=3)
    return im


def world_anchored_type(t):
    im, _, shift, _ = architectural_shot(t)
    type_plane = Image.new("RGBA", (420, 102))
    a = ImageDraw.Draw(type_plane)
    label(a, "THE STUDIO", (209, 53), 53, (64, 96, 75), "bold", "mm")
    quad = [(204 + shift, 245), (436 + shift, 222), (519 + shift, 288), (154 + shift, 320)]
    warp(im, type_plane, quad)
    return im


def phone_ui(draw, box, t=0):
    l, top, r, b = box
    w = r - l
    label(draw, "Daily flow", (l+10, top+18), 11, PALE)
    for i in range(3):
        y = top+42+i*35
        if y+24 < b:
            rounded(draw, (l+8,y,r-8,y+25), PALE if i == 1 else (79, 110, 96), 7)
            draw.ellipse(point(l+18,y+12,4), fill=GOLD if i == 1 else SAGE)
            draw.line((l+28,y+13,l+w-17,y+13), fill=FOREST if i == 1 else MINT, width=2)


def floating_interface_layers(t):
    im, d = studio()
    sx = 304 + 16*sin(t*.9)
    box = smartphone(d, sx, 202, 1.08)
    phone_ui(d, box, t)
    for i, (title, detail, base, fg) in enumerate((
        ("Focus", "Active now", PALE, FOREST),
        ("Queue", "3 projects", CREAM, CLAY),
        ("Schedule", "Today", (214, 226, 203), FOREST),
    )):
        p = tween(t, .2 + i*.23, .78 + i*.27) * (1 - .75*tween(t,2.79,3.18))
        if p < .01:
            continue
        tx = sx-63 + (-172 if i == 0 else 96 if i == 1 else -104)*p
        ty = 155+i*35-(45 if i != 2 else -5)*p
        small_card(d, (tx, ty, tx+145, ty+55), title, detail, base, fg)
    return im


def floating_screen(t):
    im, d = studio()
    x = 210 + 19 * sin(t*1.55)
    phone = smartphone(d, x, 211, .88)
    phone_ui(d, phone, t)
    d.arc((x-106, 124, x+112, 340), 36, 166, fill=(90, 119, 90), width=2)
    p = tween(t,.3,.96) * (1-tween(t,2.83,3.19))
    if p > 0:
        x0, y0 = x + 45 + 56*p, 160 - 51*p
        w, h = 245*p, 159*p
        rounded(d,(x0+8,y0+10,x0+w+8,y0+h+10),(15,36,37),11)
        rounded(d,(x0,y0,x0+w,y0+h),CREAM,11,SAGE,2)
        if p > .62:
            label(d,"PROJECT STUDIO",(x0+17,y0+15),11,FOREST,"mono")
            d.line((x0+17,y0+39,x0+w-17,y0+39),fill=LINE)
            for j in range(4):
                height = 21 + 14*j + 4*sin(t*4+j)
                d.rectangle((x0+24+j*43,y0+111-height,x0+54+j*43,y0+111), fill=blend(SAGE, FOREST,j/5))
            label(d,"Activity preview",(x0+18,y0+126),15,FOREST,"serif")
    return im


def floating_notification(t):
    im, d = studio()
    box = smartphone(d, 318, 214, 1.01)
    phone_ui(d, box)
    p = tween(t,.49,.96) * (1-tween(t,2.75,3.18))
    if p > 0:
        up = 99*p + 7*sin(progress(t,.55,1.13)*pi)
        glow(im,(320,160-up),45*p,GOLD,70)
        small_card(d,(205,173-up,436,239-up),"Render finished","Preview is ready",CREAM,FOREST)
        if .53 < t < 1.05:
            spark(d,459,203-up,8*sin(progress(t,.53,1.05)*pi),GOLD)
    return im


def floating_card_carousel(t):
    im, d = studio()
    center = (322, 185)
    d.ellipse((139, 138, 505, 275), outline=(84, 116, 97), width=2)
    turn = min(1, max(0,(t-.26)/2.52)) * pi*1.21
    appear = tween(t,.13,.59)
    if appear > .1:
        names = (("Field notes", SAGE), ("Daylight edit", GOLD), ("Sound bed", BLUE), ("Final pass", PEACH))
        cards = []
        for j,(name,color) in enumerate(names):
            a = turn + j*pi/2
            dep = (sin(a)+1)/2
            cards.append((dep, center[0]+cos(a)*162*appear,center[1]+sin(a)*52*appear,name,color))
        for dep, x, y, name, color in sorted(cards):
            s = (.62+dep*.53) * min(1, appear*1.6)
            w, h = 138*s, 95*s
            rounded(d, (x-w/2+5,y-h/2+6,x+w/2+5,y+h/2+6),(13,33,35),12)
            rounded(d, (x-w/2,y-h/2,x+w/2,y+h/2), blend((84, 112, 97), CREAM, dep),12)
            rounded(d,(x-w/2+10*s,y-h/2+10*s,x+w/2-10*s,y-h/2+43*s),blend(FOREST,color,.32+.65*dep),max(1,int(6*s)))
            if s > .43:
                label(d,name, (x,y+21*s),max(9,int(13*s)),INK,"bold","mm")
    return im


def screen_replacement(t):
    im, d = studio()
    sx = 296 + 27*sin(t*1.65)
    by = 15*sin(t*1.1-.5)
    q = [(sx-67,83),(sx+103,89+by),(sx+74,269+by),(sx-93,249)]
    d.polygon([(x+7,y+8) for x,y in q],fill=(11,30,33))
    d.polygon(q, fill=(41,64,59), outline=MINT, width=2)
    inset = [(q[0][0]+9,q[0][1]+12),(q[1][0]-11,q[1][1]+10),(q[2][0]-7,q[2][1]-12),(q[3][0]+11,q[3][1]-10)]
    screen = Image.new("RGBA", (224, 198), (*PALE, 255))
    s = ImageDraw.Draw(screen)
    if t < .67:
        s.rectangle((0,0,224,198), fill=(65, 126, 104))
        for xy in [(12,12),(210,12),(210,183),(12,183)]:
            spark(s,*xy,7,CREAM)
    else:
        label(s,"Day plan",(20,16),30,FOREST,"serif")
        for j,y in enumerate((66,101,136)):
            rounded(s,(22,y,203,y+25),CREAM,6)
            s.line((40,y+13,164-j*14,y+13),fill=MUTED,width=3)
            s.ellipse(point(31,y+13,3),fill=FOREST)
        s.line((8,188,198,180),fill=MINT,width=2)
    warp(im, screen, inset)
    fx = sx + 19 - 74*sin(t*1.37)
    fy = 244 - 59*tween(t,1.13,1.96) + 28*tween(t,2.48,3.13)
    d.line((489,341,fx,fy), fill=(205, 143, 108), width=26)
    d.ellipse(point(fx,fy,13),fill=(205,143,108))
    d.line((488,334,fx+7,fy+6),fill=(232,171,130),width=5)
    return im


def chat_bubbles(t):
    im = board((32,58,57),(63,90,75))
    d = ImageDraw.Draw(im)
    for i in range(5):
        d.line((40+132*i,0,10+132*i,360),fill=(75,104,86),width=2)
    x = 321 + 33*sin(t*1.24)
    for j, (s, txt, color) in enumerate(((-1,"Are we rolling?",CREAM),(1,"Ready to go.",MINT),(-1,"Take one.",CREAM))):
        p = tween(t,.28+j*.56,.62+j*.56)
        if p < .01:
            continue
        lx = x + s * (79 + 27*p) - (147 if s < 0 else 0)
        ly = 95 + j*52 + (1-p)*19
        rounded(d,(lx,ly,lx+147,ly+38),color,13)
        edge = lx+143 if s < 0 else lx+4
        d.polygon([(edge-7, ly+24),(edge+6,ly+28),(edge-10*s,ly+47)],fill=color)
        label(d,txt,(lx+13,ly+11),15)
    paste_host(im,x,175,1.18)
    smartphone(d,x+40,290,.38)
    return im


def ar_wayfinding(t):
    im, d, shift, vp = architectural_shot(t)
    d.ellipse((493+shift,49,554+shift,126),fill=(154,182,116))
    d.rectangle((520+shift,109,530+shift,179),fill=(100,128,81))
    p = tween(t,.31,.71)*(1-tween(t,2.67,3.19))
    if p > .08:
        for j in range(3):
            k = [.31,.55,.80][j]
            x = vp+(9+shift*.29)*k
            y = 180+171*k
            s = 11+22*k
            color = blend((221,212,170),MINT,p*(.76+.24*sin(t*4-j)))
            d.polygon([(x-s,y+4),(x,y-s*.47),(x+s,y+4),(x+s*.68,y+9),(x,y+1),(x-s*.68,y+9)],fill=color,outline=FOREST,width=1)
        label_x = min(504, 458+shift)
        line_to(d,[(525+shift,116),(525+shift,91),(label_x,89)],p,CREAM,2)
        pill(d,"Garden gate",label_x-96,76)
    return im


def glowing_orb(t):
    im, d = studio()
    x, y = 318 + 31*sin(t*1.6), 162 + 11*cos(t*2.4)
    p = tween(t,.13,.8)
    if p:
        glow(im,(x,y),116*p,(108,200,170),210)
        d.ellipse(point(x,y,52*p),fill=(24,71,71),outline=(151,219,188),width=2)
        for j in range(11):
            pts = []
            for i in range(50):
                a=i*pi/25
                stretch=45*p*(.61 + j*.035)
                pts.append((x+stretch*cos(a+j*.48)*(.64+.36*sin(t*2+j)),y+stretch*sin(a+j*.18) + 8*p*sin(a*3+t*4+j)))
            d.line(pts,fill=blend((60,120,117),(203,242,202),j/10),width=1 if j < 9 else 2)
        d.ellipse(point(x,y,11*p), fill=(227,245,197))
        for j in range(11):
            a=j*pi/5.5+t
            r=(54+9*sin(j*3+t))*p
            px,py=x+cos(a)*r,y+sin(a)*r
            d.ellipse(point(px,py,1.6+1.2*sin(j)),fill=GOLD)
    d.polygon([(28,360),(107,316),(184,280),(230,223),(247,221),(264,233),(239,250),(224,273),(282,246),(295,256),(281,276),(217,318),(159,360)],fill=(115,145,114))
    d.line((184,280,230,223,247,221),fill=blend(SAGE,MINT,p*.7),width=2)
    return im


def grounded_particles(t):
    im, d, shift, vp = architectural_shot(t)
    x = 382+shift*.68
    y = 253 + shift*.10
    d.ellipse((x-55,y-7,x+55,y+16), fill=(92,119,93), outline=FOREST,width=2)
    for i in range(4):
        d.line((x-46+i*24,y-1,x-30+i*24,y+10),fill=(169,186,142),width=2)
    haze=Image.new("RGBA",im.size)
    a=ImageDraw.Draw(haze)
    for i in range(27):
        age = (t*.88 + i*.139)%1
        radius=5+22*age
        dx=sin(i*2.1+age*4)*46*age
        dy=age*102
        alpha=int(128*sin(pi*age)*tween(t,.29,.89))
        a.ellipse(point(x+dx,y-dy,radius), fill=(236,241,207,alpha))
    haze=haze.filter(ImageFilter.GaussianBlur(8))
    im.paste(haze,(0,0),haze)
    post_x = 130+83*tween(t,.1,3.14)
    rounded(d,(post_x,191,post_x+26,308),(53,85,70),6)
    return im


def gesture_triggered_vfx(t):
    im,d=studio()
    lift=tween(t,.1,.9)
    x,y=337+34*sin(t*2),184-55*lift
    d.polygon([(90,360),(182,293),(279,239),(x-34,y+59),(x-8,y+9),(x,y),(x+9,y+6),(x-3,y+38),(x-2,y+51),(x+22,y+50),(x+42,y+74),(x+36,y+96),(281,303),(190,360)],fill=(187,128,98))
    d.line((279,239,x-34,y+59,x-8,y+9,x,y),fill=(228,167,127),width=3)
    p=tween(t,.65,1.05)*(1-tween(t,2.63,3.18))
    glow(im,(x,y),55*p,GOLD,168)
    if p>.04:
        for i in range(8):
            a=i*pi/4+t*.85
            r=p*(16+11*sin(i+t*6))
            p1=(x+r*cos(a),y+r*sin(a))
            p2=(x+(r+11*p)*cos(a),y+(r+11*p)*sin(a))
            d.line((p1,p2),fill=blend(PEACH,GOLD,(i%4)/4),width=2)
        spark(d,x,y,8*p,CREAM,3)
    return im


def product_orbit(t):
    im,d=studio()
    cx,cy=319,185
    d.ellipse((124,123,514,268),outline=(107,138,113),width=2)
    d.ellipse((177,244,462,300),fill=(27,52,50),outline=(114,139,106),width=2)
    parts=[]
    for j,(name,r,tone) in enumerate((("Filter",27,SAGE),("Grip",24,GOLD),("Cap",20,BLUE))):
        a=t*1.65+j*2*pi/3
        depth=sin(a)
        parts.append((depth,cx+181*cos(a),cy+51*depth,name,r*(.8+.18*depth),tone))
    def draw_part(part):
        depth,x,y,name,r,tone=part
        d.ellipse(point(x,y,r),fill=blend(NIGHT,tone,.71+.26*depth),outline=CREAM,width=1)
        d.ellipse(point(x,y,r*.58),outline=FOREST,width=2)
        if depth>-.2:
            label(d,name,(x,y+r+14),12,CREAM,"bold","mm")
    for part in sorted(parts):
        if part[0]<0:
            draw_part(part)
    rounded(d,(239,126,402,232),SAGE,23)
    rounded(d,(258,111,316,133),MINT,9)
    d.ellipse(point(330,178,45),fill=(29,54,52),outline=PALE,width=2)
    d.ellipse(point(330,178,32),fill=(51,91,91),outline=MUTED,width=2)
    d.ellipse(point(330,178,18),fill=(24,56,67))
    d.arc(point(330,178,16), 181,302,fill=BLUE,width=3)
    for part in sorted(parts):
        if part[0]>=0:
            draw_part(part)
    return im


def split_background():
    im = board((231,239,219),(212,224,203))
    d = ImageDraw.Draw(im)
    rounded(d,(54,41,586,319),PAPER,15,LINE)
    return im,d


def side_by_side_callout(t):
    im,d = split_background()
    split = tween(t,.23,.64)*(1-tween(t,2.71,3.18))
    gutter = 15*split
    lw = 490 - 258*split
    original = board((50,78,66),(78,118,99))
    paste_host(original,305,139,1.46)
    panel = original.crop((int(305-lw/2),32,int(305+lw/2),280))
    im.paste(panel,(75,55))
    if split > .08:
        left = 75 + lw + gutter
        d.rectangle((left,56,565,303),fill=PALE)
        if split > .78:
            label(d,"The method", (left+20,74),28,INK,"serif")
            for i,(txt,at) in enumerate((("Capture the scene",.55),("Isolate the subject",1.11),("Place the graphic",1.66))):
                y=130+47*i
                p=tween(t,at,at+.37)
                rounded(d,(left+18,y,545,y+33),blend(PALE,MINT,p),7)
                d.ellipse(point(left+34,y+16,8),fill=blend(SAGE,FOREST,p))
                label(d,str(i+1),(left+34,y+17),10,CREAM,anchor="mm")
                label(d,txt,(left+51,y+9),13,FOREST)
    return im


def valley_scene(w,h,t,grade):
    image=Image.new("RGB",(w,h))
    d=ImageDraw.Draw(image)
    colors = (
        ((157,180,185),(216,223,211),(108,138,135),(89,119,112),(71,106,87),(169,188,155)),
        ((246,188,130),(245,220,170),(171,116,115),(101,108,110),(50,100,89),(207,185,125)),
    )[grade]
    for i in range(h):
        d.line((0,i,w,i), fill=blend(colors[0],colors[1],i/h))
    k=sin(t*1.4)*.027
    d.ellipse((w*(.69+k),h*.16,w*(.85+k),h*.38),fill=colors[-1])
    d.polygon([(0,h*.63),(w*.16,h*.33),(w*.31,h*.53),(w*.48,h*.25),(w*.72,h*.64),(w,h*.48),(w,h),(0,h)],fill=colors[2])
    d.polygon([(0,h*.79),(w*.29,h*.50),(w*.39,h*.58),(w*.56,h*.51),(w*.78,h*.69),(w,h*.54),(w,h),(0,h)],fill=colors[3])
    d.polygon([(0,h*.81),(w*.2,h*.69),(w*.44,h*.79),(w*.7,h*.71),(w,h*.67),(w,h),(0,h)],fill=colors[4])
    d.line([(w*.61,h),(w*.44,h*.94),(w*.44,h*.88),(w*.57,h*.76)], fill=colors[-1],width=max(1,int(w*.023)))
    d.ellipse(point(w*(.45+.13*t/3.2),h*.93,3),fill=CREAM)
    return image


def side_by_side_reference(t):
    im,d=studio()
    for i,title in enumerate(("Original", "Graded")):
        x=43+i*281
        rounded(d,(x,56,x+271,300), (45,68,63),12,(91,117,99))
        shade=0 if i==0 or t<.56 else 1
        im.paste(valley_scene(256,182,t,shade),(x+7,63))
        pill(d,title,x+12,260, MINT if i==1 and shade else CREAM)
    d.line((319,52,319,306), fill=(114,142,119),width=1)
    p=tween(t,.7,2.9)
    d.line((45,320,593,320),fill=MUTED,width=2)
    d.line((45,320,45+548*p,320),fill=GOLD,width=2)
    return im


def picture_in_picture(t):
    if t>2.84:
        im,_ = studio()
        paste_host(im,319,151,1.75)
        return im
    im=board((54,83,75),(26,51,53))
    d=ImageDraw.Draw(im)
    desk_screen(d,(63,48,576,312),"Editor",selected=min(3,int(t*1.5)),rows=5)
    cursor(d,443,135+min(3,int(t*1.5))*34,.55*sin(t*8)**2)
    portrait_crop=board((89,117,97),(53,85,70))
    paste_host(portrait_crop,321,152,1.4)
    sprite=portrait_crop.crop((214,66,429,279)).resize((91,91),Image.Resampling.LANCZOS)
    mask=Image.new("L",sprite.size)
    ImageDraw.Draw(mask).ellipse((0,0,90,90),fill=255)
    cx=507 if t<1.4 else 144
    cy=260
    d.ellipse(point(cx,cy,48), fill=CREAM)
    im.paste(sprite,(int(cx-45),int(cy-45)),mask)
    return im


def coffee_close(t):
    im=board((210,183,146),(187,145,118))
    d=ImageDraw.Draw(im)
    for i in range(6):
        d.line((0,44+i*67,640,56+i*67),fill=(192,154,123),width=1)
    d.ellipse((208,202,433,302),fill=(164,122,96))
    d.ellipse((337,165,427,235),fill=CREAM,outline=(162,146,116),width=3)
    d.ellipse((359,179,408,223),fill=(206,166,132))
    d.ellipse((207,128,394,274),fill=CREAM,outline=(162,146,116),width=3)
    d.ellipse((225,146,377,254),fill=(117,71,49))
    d.ellipse((231,150,367,247),fill=(157,102,68))
    d.arc((241,161,359,238),153,318,fill=(216,153,105),width=5)
    x=287 + 28*sin(t*4)
    d.line((x-11,0,x,190),fill=(230,208,174),width=11)
    for i in range(4):
        p=tween(t,i*.16,i*.16+.63)
        if p > .03:
            d.ellipse((x-10-48*p,185-25*p,x+10+48*p,198+26*p),outline=(241,219,185),width=2)
    return im


def explanatory_b_roll(t):
    if .7 < t < 2.66:
        return coffee_close(t-.7)
    im,d=studio()
    paste_host(im,315,147,1.62)
    for i in range(5):
        y=95+i*33
        d.line((435,y,600,y),fill=(52,80,67),width=2)
    return im


def wide_studio():
    im = board((192,206,178),(213,215,184))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((60,40,306,207),radius=12,fill=(225,237,207),outline=(159,184,147),width=2)
    d.line((181,41,181,208),fill=(159,184,147),width=2)
    d.line((59,129,306,129),fill=(159,184,147),width=2)
    d.polygon([(0,251),(640,184),(640,360),(0,360)],fill=(126,135,99))
    d.line((0,280,640,216),fill=(160,154,112),width=2)
    d.polygon([(155,283),(513,229),(562,264),(202,326)],fill=(224,199,148),outline=(136,126,88),width=3)
    return im,d


def detail_sequence(t):
    if t < .76:
        im,d=wide_studio()
        d.polygon([(262,249),(403,222),(451,258),(305,289)],fill=CREAM,outline=FOREST,width=2)
        d.ellipse((233,243,280,265),fill=PALE,outline=FOREST,width=1)
        d.line((451,111,354,252),fill=FOREST,width=7)
    elif t < 1.91:
        im=board((130,161,115),(175,186,134))
        d=ImageDraw.Draw(im)
        p=tween(t,.79,1.85)
        d.polygon([(160,221),(344,215),(460,304),(265,325)],fill=CREAM,outline=FOREST,width=2)
        d.line((278,258,421,85-50*p),fill=FOREST,width=11)
        d.line((294,238,421,85-50*p),fill=SAGE,width=4)
        d.ellipse((190,252,301,299),fill=PALE)
        pts=[(217+12*i,277-21*sin(i/2)) for i in range(8)]
        line_to(d,pts,p,CLAY,3)
    else:
        im,d=wide_studio()
        d.polygon([(262,249),(403,222),(451,258),(305,289)],fill=CREAM,outline=FOREST,width=2)
        pts=[(311+i*5,262-3*i-8*sin(i)) for i in range(14)]
        d.line(pts,fill=CLAY,width=3)
        d.line((451,110,426,226),fill=FOREST,width=7)
    return im


def arrow(d,x1,y1,x2,y2,p,color=FOREST,width=3):
    if p<=0:
        return
    x,y=mix_at((x1,y1),(x2,y2),p)
    d.line((x1,y1,x,y),fill=color,width=width)
    r=((x-x1)**2+(y-y1)**2)**.5
    if r>9:
        ux,uy=(x-x1)/r,(y-y1)/r
        d.polygon([(x,y),(x-10*ux-5*uy,y-10*uy+5*ux),(x-10*ux+5*uy,y-10*uy-5*ux)],fill=color)


def illustrated_explainer(t):
    if t < .39 or t > 2.87:
        return shot('host-live',t,1.15,-41,-8)
    im=board((231,237,205),(200,221,196))
    d=ImageDraw.Draw(im)
    p=tween(t,.46,1.28)
    sun_x,sun_y=144,135
    d.ellipse(point(sun_x,sun_y,31),fill=GOLD)
    for i in range(10):
        a=i*pi/5
        d.line((sun_x+38*cos(a),sun_y+38*sin(a),sun_x+46*cos(a),sun_y+46*sin(a)),fill=(196,138,56),width=2)
    for i in range(4):
        d.ellipse(point(296+i*18,113+8*sin(i),25),fill=CREAM)
    d.rounded_rectangle((278,108,378,143),radius=17,fill=CREAM)
    arrow(d,195,134,264,134,p)
    q=tween(t,1.19,2.28)
    for j in range(9):
        drop_y=155+65*((q+j*.13)%1)
        if q>.02:
            d.line((291+j*9,drop_y,288+j*9,drop_y+12),fill=(74,128,136),width=2)
    d.ellipse((268,235,392,256),fill=(118,173,160))
    arrow(d,397,239,460,238,q)
    for j in range(3):
        x=482+20*j
        d.line((x,237,x,237-46*q),fill=FOREST,width=3)
        if q>.1:
            d.ellipse((x-10,228-45*q,x+2,240-45*q),fill=FOREST)
            d.ellipse((x-2,221-41*q,x+10,233-41*q),fill=(105,150,100))
    for x,txt in ((145,"Evaporate"),(333,"Rain"),(511,"Grow")):
        label(d,txt,(x,282),17,FOREST,"serif","mm")
    return im


def tool_flow(t):
    im=board((230,239,219),(213,228,202),True);d=ImageDraw.Draw(im)
    nodes=[(91,180,"Capture",.05),(250,103,"Transcribe",.48),(250,251,"Stabilize",.92),(461,179,"Edit-ready",1.55)]
    edges=[(154,174,191,118,.3),(153,190,191,237,.68),(311,110,393,167,1.2),(311,246,393,191,1.51)]
    for x1,y1,x2,y2,start in edges:
        arrow(d,x1,y1,x2,y2,tween(t,start,start+.34))
    for i,(x,y,title,start) in enumerate(nodes):
        p=tween(t,start,start+.33)
        if p <= 0:
            continue
        tint=FOREST if i==3 else PALE
        c=blend((217,232,209),tint,p)
        rounded(d,(x-63,y-29,x+63,y+29),c,10,blend(MINT,FOREST,p),1)
        label(d,title,(x,y+1),18,CREAM if i==3 and p>.6 else INK,"bold","mm")
    return im


def phases(t):
    im=board((36,62,61),(20,43,46),True)
    d=ImageDraw.Draw(im)
    stages=((142,"Select",SAGE),(320,"Arrange",GOLD),(498,"Deliver",BLUE))
    d.line((142,165,498,165),fill=(91,121,106),width=3)
    for i,(x,txt,col) in enumerate(stages):
        p=tween(t,.18+.62*i,.61+.62*i)
        base=blend((61,85,81),col,p)
        d.ellipse(point(x,165,35),fill=base,outline=blend(MUTED,CREAM,p),width=2)
        if i==0:
            d.line([(x-11,165),(x-3,173),(x+13,157)],fill=DARK,width=3)
        elif i==1:
            for j in range(3):
                d.line((x-12+j*5,154+j*10,x+14-j*4,154+j*10),fill=DARK,width=3)
        else:
            d.polygon([(x-11,151),(x+13,151),(x+13,177),(x-11,177)],outline=DARK,width=2)
            arrow(d,x-5,163,x+9,163,1,DARK,2)
        label(d,txt,(x,226),23,blend((148,173,163),CREAM,p),"serif","mm")
    return im


def exploded_cross_section(t):
    im=board((229,237,217),(201,219,201),True)
    d=ImageDraw.Draw(im)
    p=tween(t,.34,1.08)
    d.line((303,54,303,310),fill=(154,181,152),width=2)
    layers=((CREAM,"Lens"),((127,190,194),"Sensor"),((87,131,103),"Board"),(GOLD,"Housing"))
    for i,(color,txt) in enumerate(reversed(layers)):
        y=239-i*(11+34*p)
        x=224
        d.polygon([(x,y),(x+151,y),(x+189,y+26),(x+49,y+26)],fill=color,outline=FOREST,width=2)
        d.polygon([(x+49,y+26),(x+189,y+26),(x+188,y+35),(x+50,y+36)],fill=blend(color,FOREST,.48))
        if i==3:
            d.ellipse((274,y+4,355,y+24),outline=FOREST,width=2)
        else:
            for j in range(4):
                d.line((266+j*24,y+4,290+j*24,y+21),fill=blend(color,FOREST,.48),width=1)
        if t > .89+.20*(3-i):
            line_to(d,[(x+184,y+15),(x+215,y+15),(x+236,y+9)],tween(t,.85+.17*(3-i),1.11+.17*(3-i)),MUTED,1)
            label(d,txt,(466,y+5),16,INK)
    return im


def beat_marker(t):
    im=board((31,57,58),(16,39,44))
    d=ImageDraw.Draw(im)
    tones=(MINT,GOLD,PEACH,BLUE)
    guides=["Open","Reveal","Hold","Resolve"]
    xp=(94,240,391,546)
    y=193
    d.line((94,y,546,y),fill=(85,115,111),width=2)
    d.line((94,y,94+452*progress(t,.12,2.96),y),fill=GOLD,width=3)
    for i,x in enumerate(xp):
        q=tween(t,.17+i*.68,.37+i*.68)
        current=progress(t,.17+i*.68,.9+i*.68)
        d.line((x,y-30,x,y+30),fill=(90,126,118),width=1)
        d.ellipse(point(x,y,7+5*sin(pi*current)),fill=blend((90,120,113),tones[i],q))
        label(d,guides[i],(x,y+57),17,blend((131,160,152),CREAM,q),"serif","mm")
        label(d,f"0:{i+1:02d}",(x,y-58),12,MINT,"mono","mm")
    return im


def guided_zoom(t):
    base=board((56,87,78),(24,52,52))
    d=ImageDraw.Draw(base)
    desk_screen(d,(75,44,566,310),"Video project",selected=2 if t>1.15 else -1,rows=5)
    p=tween(t,.50,.98)*(1-tween(t,2.51,3.16))
    x,y=237,203
    scale=1+.78*p
    margin_x=W/2/scale
    margin_y=H/2/scale
    cx=W/2+(x-W/2)*p
    cy=H/2+(y-H/2)*p
    im=base.crop((int(cx-margin_x),int(cy-margin_y),int(cx+margin_x),int(cy+margin_y))).resize((W,H),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(im)
    if p>.65:
        bx=W/2+(x-cx)*scale
        by=H/2+(y-cy)*scale
        d.ellipse((bx-58,by-24,bx+58,by+24),outline=GOLD,width=3)
        cursor(d,bx+55,by+12)
    return im


def isolated_ui_card(t):
    im=board((66,94,84),(27,55,54));d=ImageDraw.Draw(im)
    desk_screen(d,(73,45,568,310),"Project workspace",selected=1,rows=5)
    p=tween(t,.41,1.02)*(1-tween(t,2.58,3.17))
    if p>.01:
        tint=Image.new("RGB",im.size,(18,39,42))
        im=Image.blend(im,tint,.65*p)
        d=ImageDraw.Draw(im)
        w=198+157*p
        x=320-w/2
        y=156-51*p
        rounded(d,(x-2,y+10,x+w+4,y+101*p+20),(15,34,37),12)
        rounded(d,(x,y,x+w,y+97*p+25),CREAM,13,MUTED,1)
        label(d,"Export preset",(x+19,y+12),17,FOREST)
        if p>.72:
            d.line((x+19,y+45,x+w-19,y+45),fill=LINE)
            label(d,"Social feed · 1080 × 1920",(x+19,y+59),22,INK,"serif")
            pill(d,"Selected",x+19,y+88,PALE,FOREST)
    return im


def title_card(first, second, accent=GOLD):
    im=board((32,64,61),(23,44,49))
    d=ImageDraw.Draw(im)
    d.line((67,68,573,68), fill=(85,111,102),width=1)
    d.line((67,292,573,292), fill=(85,111,102),width=1)
    label(d,first,(320,126),14,accent,"mono","mm")
    label(d,second,(320,184),46,CREAM,"serif","mm")
    return im


def step_breaks(t):
    if t < .58:
        return title_card("STEP 1","Choose a preset")
    if 1.47<t<2.06:
        return title_card("STEP 2","Confirm the size",BLUE)
    im=board((163,193,169),(145,174,149));d=ImageDraw.Draw(im)
    r=1 if t<1.47 else 2
    desk_screen(d,(69,48,578,314),"Export settings",selected=r,rows=5)
    cy=48+83+32*r+10
    cursor(d,474,cy,tween(t,.78 if r==1 else 2.21,1.13 if r==1 else 2.57))
    return im


def time_compression(t):
    im=board((27,53,55),(40,70,63));d=ImageDraw.Draw(im)
    rounded(d,(67,58,573,294),PAPER,12,MUTED)
    d.line((67,102,573,102),fill=LINE)
    label(d,"New folder",(94,74),13,FOREST)
    p=progress(t,.34,1.72)
    items=("A-roll","B-roll","Graphics","Music","Captions","Exports")
    for j,txt in enumerate(items):
        q=tween(p,j*.13,j*.13+.15)
        if q<=0:
            continue
        y=123+(j//3)*68
        x=105+(j%3)*153
        rounded(d,(x,y,x+124,y+53),blend(PAPER,PALE,q),8)
        d.rounded_rectangle((x+10,y+12,x+35,y+32),radius=3,fill=FOREST)
        d.rounded_rectangle((x+11,y+8,x+23,y+14),radius=2,fill=FOREST)
        label(d,txt,(x+43,y+16),13,INK)
    if .38<t<1.76:
        pill(d,"5× speed",460,70, GOLD, INK)
    if t>1.88:
        pill(d,"Folders ready",425,70, PALE, FOREST)
    d.line((69,316,574,316),fill=MUTED,width=1)
    d.line((69,316,69+505*progress(t,.1,3.15),316),fill=GOLD,width=3)
    return im


def hand_drawn_markup(t):
    im=board((220,230,205),(200,217,191));d=ImageDraw.Draw(im)
    rounded(d,(92,35,549,325),PAPER,13,LINE)
    label(d,"Friday release",(120,73),38,INK,"serif")
    label(d,"Here's what the new version includes.",(124,124),15,MUTED,"regular")
    for i,(desc,tag) in enumerate((("Faster renders","Live"),("A new preset","Live"),("Team spaces","Next"))):
        y=164+i*45
        d.line((124,y-9,520,y-9),fill=LINE,width=1)
        label(d,desc,(124,y),17,INK)
        label(d,tag,(471,y+8),13,FOREST,"bold","mm")
    p=tween(t,.49,1.24)
    ink=blend(PAPER,CLAY,1-tween(t,2.54,3.08))
    pts=[]
    for i in range(57):
        a=i*2*pi/56-.12
        pts.append((224+(108+3*sin(i*1.1))*cos(a),217+(23+2*sin(i*.82))*sin(a)))
    if t < 3.08:
        line_to(d,pts,p,ink,4)
    return im


def chapter_cards(t):
    if t <= .66:
        return shot('host-live',t,1.16,-36,-10)
    if t < 1.93:
        p=tween(t,.67,.98)
        im=title_card("CHAPTER 2","Find the right light",GOLD)
        if p < 1:
            im=Image.blend(board((27,51,51),(24,45,49)),im,p)
        return im
    return shot('room',t,1.02+.09*tween(t,1.93,3.15),6,4)


SCENES = {
    "tracked-callout": tracked_callout,
    "projected-hud": projected_hud,
    "world-anchored-graphic": world_anchored_graphic,
    "world-anchored-type": world_anchored_type,
    "floating-interface-layers": floating_interface_layers,
    "floating-screen": floating_screen,
    "floating-notification": floating_notification,
    "floating-card-carousel": floating_card_carousel,
    "screen-replacement": screen_replacement,
    "tracked-chat-bubbles": chat_bubbles,
    "ar-wayfinding": ar_wayfinding,
    "glowing-orb": glowing_orb,
    "grounded-particle-overlay": grounded_particles,
    "gesture-triggered-vfx": gesture_triggered_vfx,
    "product-orbit": product_orbit,
    "side-by-side-callout": side_by_side_callout,
    "side-by-side-reference": side_by_side_reference,
    "picture-in-picture-demo": picture_in_picture,
    "explanatory-b-roll": explanatory_b_roll,
    "detail-sequence": detail_sequence,
    "illustrated-explainer-inserts": illustrated_explainer,
    "animated-tool-diagram": tool_flow,
    "phased-process-diagram": phases,
    "exploded-layer-diagram": exploded_cross_section,
    "beat-marker-graphic": beat_marker,
    "guided-zoom-highlight": guided_zoom,
    "isolated-ui-card": isolated_ui_card,
    "step-breaks-screencast": step_breaks,
    "screencast-time-compression": time_compression,
    "hand-drawn-markup": hand_drawn_markup,
    "chapter-cards": chapter_cards,
}
