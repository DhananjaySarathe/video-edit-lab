"""Spatial effects tracked to a filmed handheld phone."""
from functools import lru_cache
from math import cos, pi, sin

from PIL import Image, ImageDraw, ImageFilter

from preview_common import H, W, progress
from preview_live_action import GOLD, INK, MINT, PAPER, tag, tween, type_at
from preview_plates import FRAME_RATE, shot, source
from preview_spatial import warp


def fit(points):
    """Fit a line to the inside edge of the green display."""
    n = len(points)
    x = sum(a for a, _ in points)/n
    y = sum(b for _, b in points)/n
    slope = sum((a-x)*(b-y) for a, b in points)/sum((a-x)**2 for a, _ in points)
    return slope, y-slope*x


def cross(edge, side):
    y_slope, y_start = edge
    x_slope, x_start = side
    x = (x_slope*y_start+x_start)/(1-x_slope*y_slope)
    return x, y_slope*x+y_start


@lru_cache(maxsize=64)
def screen_track(frame):
    raw = source('phone-live', frame/FRAME_RATE)
    area = (160, 22, 345, 338)
    sample = raw.crop(area)
    matte = Image.new('L', sample.size)
    matte.putdata([255 if g > 135 and g > 1.5*r+25 and g > 1.5*b+25 else 0
                   for r, g, b in sample.getdata()])
    l, top, r, bottom = matte.getbbox()
    px = matte.load()
    inner_rows = range(top+50, bottom-50, 6)
    left = fit([(y, next(x for x in range(l, r) if px[x,y])) for y in inner_rows])
    right = fit([(y, next(x for x in range(r-1, l, -1) if px[x,y])) for y in inner_rows])
    # The notch is in the middle. Sample the flat outer shoulders of that edge.
    left_top, left_bottom = sorted((left[0]*top+left[1], left[0]*bottom+left[1]))
    columns = [x for x in range(round(left_bottom)+5, r-23, 2)]
    top_points, bottom_points = [], []
    for x in columns:
        first = next(y for y in range(top, bottom) if px[x,y])
        last = next(y for y in range(bottom-1, top, -1) if px[x,y])
        if first < top+16:
            top_points.append((x, first))
        if last > bottom-19:
            bottom_points.append((x, last))
    upper, lower = fit(top_points), fit(bottom_points)
    quad = [(x+area[0], y+area[1]) for x,y in
            (cross(upper, left), cross(upper, right), cross(lower, right), cross(lower, left))]
    full = Image.new('L', (W,H))
    full.paste(matte, area[:2])
    return quad, full.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(.48))


def device(t, screen):
    image = shot('phone-live', t)
    quad, matte = screen_track(min(63, round(t*FRAME_RATE)))
    replacement = Image.new('RGB', (W,H), '#172a2a')
    warp(replacement, screen, quad)
    image.paste(replacement, (0,0), matte)
    return image, quad


def screen_ui(t, setting='Trail guide'):
    panel = Image.new('RGBA', (170,314), '#142b2c')
    d = ImageDraw.Draw(panel)
    type_at(panel, (13,36), setting, 20, anchor='lm')
    d.line((12,60,157,60), fill='#627c75')
    if setting == 'Voice cleanup':
        for i in range(20):
            x = 18+7*i
            y = 12 + (28 if t < 1.62 else 21)*abs(sin(i*(1.55 if t < 1.62 else .57)))
            d.line((x,141-y,x,141+y), fill=MINT, width=3)
        d.rounded_rectangle((16,228,154,263), 6, fill=MINT)
        type_at(panel, (85,246), 'Clean audio' if t < 1.62 else 'Done', 15, INK)
    else:
        d.rounded_rectangle((13,81,157,268), 7, fill='#2b4a42')
        for a in range(6):
            d.line((23,104+a*26,147,104+a*26), fill='#385951')
        path = [(35,232),(49,199),(82,204),(101,160),(122,144),(136,113)]
        d.line(path, fill='#a5d6a9', width=5, joint='curve')
        i = min(4, int(t*1.45))
        f = t*1.45-i
        x = path[i][0]+f*(path[i+1][0]-path[i][0])
        y = path[i][1]+f*(path[i+1][1]-path[i][1])
        d.ellipse((x-6,y-6,x+6,y+6), fill=GOLD)
        type_at(panel,(85,287),'North trail',15)
    return panel


def card(title, note, width=220, height=78, color='#172b2c'):
    panel = Image.new('RGBA', (width,height))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((1,1,width-2,height-2),10,fill=color,outline='#c4ead6',width=1)
    type_at(panel,(15,26),title,20,anchor='lm')
    type_at(panel,(15,53),note,14,MINT,anchor='lm')
    return panel


def place(image, panel, x, y, opacity=1):
    if opacity < 1:
        panel.putalpha(panel.getchannel('A').point(lambda v: round(v*opacity)))
    image.paste(panel,(round(x),round(y)),panel)


def app_tap(image, t, quad):
    p = progress(t, .46, .87)
    if p in (0,1):
        return
    x, y = quad[2]
    r = round(9+20*p)
    draw = ImageDraw.Draw(image, 'RGBA')
    draw.ellipse((x-35-r,y-58-r,x-35+r,y-58+r),
                 outline=(210,255,217,round(225*(1-p))), width=3)


def replace_screen(t):
    image, quad = device(t, screen_ui(t))
    raw = shot('phone-live', t)
    if t < .52:
        tag(raw,'Original: green screen',15,17)
        return raw
    p = tween(t, .52, 1.03)
    if p < 1:
        x = round(160+180*p)
        image.paste(raw.crop((x,0,W,H)), (x,0))
        ImageDraw.Draw(image).line((x,21,x,333), fill=PAPER, width=2)
    elif t < 1.53:
        for x,y in quad:
            ImageDraw.Draw(image).ellipse((x-4,y-4,x+4,y+4), outline=MINT, width=2)
    tag(image,'Tracked screen insert',15,17,True)
    return image


def projected(t):
    image, quad = device(t, screen_ui(t))
    app_tap(image, t, quad)
    p = tween(t,.54,1.15)*(1-tween(t,2.55,3.12))
    if p <= 0:
        return image
    r, top = quad[1]
    panel = Image.new('RGBA',(248,148))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((1,1,246,146),13,fill=(23,51,55,209),outline='#a4eddd',width=2)
    type_at(panel,(16,27),'Trail monitor',24,anchor='lm')
    draw.line([(15+i*11,85+14*sin(i*.72+t*5)) for i in range(13)], fill='#76eaca', width=3)
    if t > 1.3:
        type_at(panel,(163,72),'GPS',15,MINT,anchor='lm')
        type_at(panel,(163,101),'LOCKED',13,anchor='lm')
    x, y = r+36, top+20+(1-p)*112
    glow = Image.new('RGBA',(W,H))
    light = ImageDraw.Draw(glow)
    light.polygon([(r-5,top+172),(x,y+142),(x+246,y+142),(r+25,top+171)],
                  fill=(132,238,210,round(33*p)))
    ellipse = (r-32,top+139,r+46,top+199)
    light.ellipse(ellipse,fill=(122,251,207,round(72*p)))
    image.paste(glow,(0,0),glow.filter(ImageFilter.GaussianBlur(10)))
    place(image,panel,x,y,p)
    return image


def floating_layers(t):
    image, quad = device(t, screen_ui(t))
    r, top = quad[1]
    items = (('Route','North trail'),('Distance','2.4 km'),('Next turn','Keep right'))
    for i,(title,note) in enumerate(items):
        p = tween(t,.55+i*.37,1.1+i*.37)
        if p > 0:
            x = r+24+(i%2)*24-(1-p)*89
            y = top+10+i*90+(1-p)*(89-10*i)
            place(image,card(title,note,222,75),x,y,p)
    return image


def floating_screen(t):
    image, quad = device(t, screen_ui(t,'Voice cleanup'))
    app_tap(image,t,quad)
    p = tween(t,.67,1.19)*(1-tween(t,2.72,3.17))
    if p <= 0:
        return image
    panel = Image.new('RGBA',(244,157))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((1,1,242,155),12,fill='#192e30',outline='#bcebd9',width=2)
    type_at(panel,(15,26),'Voice cleanup',21,anchor='lm')
    for i in range(22):
        x = 17+i*10
        h = 8 + 23*abs(sin(i*(1.7 if t < 1.62 else .65)))
        draw.line((x,82-h,x,82+h), fill=MINT if t >= 1.62 else '#a1b4ae',width=4)
    draw.rounded_rectangle((16,117,226,144),5,fill=MINT if t >= 1.62 else '#394947')
    type_at(panel,(121,131),'Background noise removed' if t >= 1.62 else 'Clean audio',
            14, INK if t >= 1.62 else PAPER)
    r, top = quad[1]
    place(image,panel,r+40-(1-p)*105,top+49+(1-p)*75,p)
    return image


def notification(t):
    image, quad = device(t, screen_ui(t))
    r, top = quad[1]
    p = tween(t,.44,.88)*(1-tween(t,2.35,3.02))
    if p > 0:
        y = top+23+66*(1-p)-7*sin(pi*p)
        place(image,card('Route downloaded','Available offline',237,76),r+10,y,p)
    return image


def carousel(t):
    image, quad = device(t, screen_ui(t))
    r, top = quad[1]
    p = tween(t,.43,.83)*(1-tween(t,2.76,3.18))
    if p <= 0:
        return image
    labels = (('North trail','2.4 km'),('Lake loop','3.8 km'),('Grove path','1.1 km'))
    angles = [(i*2*pi/3+(t-.7)*2.1,i) for i in range(3)]
    for a,i in sorted(angles,key=lambda pair: cos(pair[0])):
        depth = .5+.5*cos(a)
        width, height = round(151+36*depth), round(59+16*depth)
        tile = card(*labels[i],185,78).resize((width,height),Image.Resampling.LANCZOS)
        place(image,tile,r+126+58*sin(a)-width*.5,top+110+59*depth,p*(.55+.45*depth))
    return image


def wayfinding(t):
    image, quad = device(t, screen_ui(t))
    p = tween(t,.35,.84)*(1-tween(t,2.57,3.14))
    if p <= 0:
        return image
    # Track the vanishing point gently with the handheld camera's vertical drift.
    dy = quad[1][1]-screen_track(0)[0][1][1]
    layer = Image.new('RGBA',(W,H))
    draw = ImageDraw.Draw(layer)
    for i,(x,y,w,h) in enumerate(((421,307,40,21),(437,246,28,15),(447,199,19,10))):
        q = p*tween(t,.39+i*.18,.8+i*.18)
        draw.line(((x-w,y+dy+h),(x,y+dy),(x+w,y+dy+h)),
                  fill=(223,255,184,round(235*q)), width=5-i)
    draw.line((456,156+dy,487,116+dy,508,116+dy),fill=(237,252,196,round(230*p)),width=2)
    if p > .5:
        tag(layer,'North trail',507,102+dy,True)
    image.paste(layer,(0,0),layer)
    return image


SCENES = {
    'projected-hud': projected,
    'floating-interface-layers': floating_layers,
    'floating-screen': floating_screen,
    'floating-notification': notification,
    'floating-card-carousel': carousel,
    'screen-replacement': replace_screen,
    'ar-wayfinding': wayfinding,
}
