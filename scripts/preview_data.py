"""Original motion-graphic examples for charts, maps, and documentary inserts."""

from functools import lru_cache
from math import dist, sin
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

from preview_common import font
from preview_plates import shot, source

WIDTH, HEIGHT = 640, 360
PAPER = (246, 241, 225)
CREAM = (253, 249, 235)
INK = (31, 51, 44)
MUTED = (84, 103, 91)
FOREST = (38, 89, 70)
SAGE = (167, 190, 155)
DARK = (22, 42, 43)
NIGHT = (15, 29, 33)
PALE = (212, 228, 201)
MIST = (102, 132, 128)
MINT = (140, 226, 192)
GRID = (215, 219, 202)
DARK_GRID = (52, 74, 74)
GOLD = (233, 173, 82)
OCHRE = (162, 92, 43)
RUST = (185, 74, 47)

CHART = (94, 114, 580, 273)
YEARS = ("2019", "2020", "2021", "2022", "2023", "2024")
SERIES = (21, 32, 25, 54, 63, 81)


def clamp(value):
    return min(1.0, max(0.0, value))


def phase(t, start, end):
    value = clamp((t - start) / (end - start))
    return value * value * (3 - 2 * value)


def color(a, b, p):
    return tuple(round(x + (y-x)*p) for x, y in zip(a, b))


def label(draw, xy, value, size=17, fill=INK, weight="regular", anchor="la"):
    draw.text(xy, value, font=font(size, weight), fill=fill, anchor=anchor)


def section(draw, title, subtitle=None, dark=False):
    label(draw, (54, 31), title, 31, CREAM if dark else INK, "serif")
    if subtitle:
        label(draw, (55, 73), subtitle, 17, PALE if dark else MUTED)


def card(draw, box, fill=CREAM, outline=GRID, radius=12):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        (round(x0), round(y0), round(x1), round(y1)),
        radius=radius, fill=fill, outline=outline, width=1
    )


def badge(draw, x, y, value, fill=FOREST, text=CREAM, size=15):
    width = draw.textlength(value, font=font(size, "bold")) + 18
    card(draw, (x - width/2, y-12, x + width/2, y+12), fill, fill, 6)
    label(draw, (x, y+1), value, size, text, "bold", "mm")


def dot(draw, point, radius, fill, outline=None, width=1):
    x, y = point
    draw.ellipse((x-radius, y-radius, x+radius, y+radius),
                 fill=fill, outline=outline, width=width)


def lines_until(points, amount):
    total = sum(dist(a, b) for a, b in zip(points, points[1:]))
    remaining = total * clamp(amount)
    visible = [points[0]]
    for a, b in zip(points, points[1:]):
        length = dist(a, b)
        if remaining >= length:
            visible.append(b)
            remaining -= length
            continue
        fraction = remaining / max(length, 0.001)
        visible.append((a[0] + (b[0] - a[0]) * fraction,
                        a[1] + (b[1] - a[1]) * fraction))
        break
    return visible


def stroke(draw, points, fill, width=3, amount=1.0):
    visible = lines_until(points, amount)
    if len(visible) > 1:
        draw.line(visible, fill, width=width, joint="curve")
    return visible[-1]


def sample_chart(values, box=CHART):
    left, top, right, baseline = box
    return [(left + (right-left)*i/(len(values)-1), baseline - (baseline-top)*v/100)
            for i, v in enumerate(values)]


@lru_cache(maxsize=20)
def base_image(top, bottom, texture=0):
    strip = Image.new("RGB", (1, HEIGHT))
    strip.putdata([color(top, bottom, y/(HEIGHT-1)) for y in range(HEIGHT)])
    canvas = strip.resize((WIDTH, HEIGHT))
    if texture:
        noise = Image.effect_noise(canvas.size, 15)
        warm_noise = ImageOps.colorize(noise, (118, 101, 75), (255, 250, 233))
        canvas = Image.blend(canvas, warm_noise, texture/100)
    return canvas


def plate(dark=False, texture=0):
    colors = (DARK, NIGHT) if dark else (CREAM, PAPER)
    image = base_image(*colors, texture).copy()
    return image, ImageDraw.Draw(image)


def chart_axes(draw, labels=YEARS, box=CHART, dark=False, unit="", centered=False):
    left, top, right, bottom = box
    grid = DARK_GRID if dark else GRID
    text_color = PALE if dark else MUTED
    for value in (0, 25, 50, 75, 100):
        y = bottom - (bottom-top)*value/100
        draw.line((left, y, right, y), fill=grid, width=1)
        label(draw, (left-10, y), f"{value}{unit}", 16, text_color, anchor="rm")
    draw.line((left, top, left, bottom, right, bottom),
              fill=MIST if dark else SAGE, width=2)
    for i, value in enumerate(labels):
        fraction = (i+0.5)/len(labels) if centered else i/max(len(labels)-1, 1)
        x = left + (right-left)*fraction
        label(draw, (x, bottom+13), value, 16, text_color, anchor="mt")


def draw_on_line_chart(t):
    image, draw = plate()
    section(draw, "A signal takes shape", "Weekly listening hours")
    chart_axes(draw, ("W1", "W2", "W3", "W4", "W5", "W6"))
    data = sample_chart(SERIES)
    amount = phase(t, .26, 2.3)
    end_x, _ = stroke(draw, data, FOREST, width=4, amount=amount)
    for index in (0, 2, 5):
        x, y = data[index]
        if end_x >= x - .1 and t > .3:
            dot(draw, (x, y), 5, CREAM, FOREST, 3)
            label(draw, (x-2, y-11), str(SERIES[index]), 18, FOREST, "bold", "mb")
    return image


def chart_tracking_marker(t):
    image, draw = plate(True)
    section(draw, "Follow the signal", "Uplink strength · %", True)
    chart_axes(draw, ("0s", "3s", "6s", "9s", "12s", "15s"), dark=True)
    points = sample_chart((20, 45, 34, 69, 60, 83))
    stroke(draw, points, (57, 94, 88), width=2)
    value = .09 + .78 * phase(t, .2, 2.17)
    if 1.24 < t < 1.58:
        value = .49
    elif 1.58 <= t < 2.17:
        value = .49 + .38 * phase(t, 1.58, 2.17)
    if t < 1.24:
        value = .09 + .40 * phase(t, .2, 1.24)
    x, y = stroke(draw, points, MINT, width=4, amount=value)
    left, top, right, bottom = CHART
    draw.line((left, y, x, y, x, bottom), fill=(101, 154, 139), width=1)
    dot(draw, (x, y), 8, MINT, DARK, 3)
    percent = round((bottom-y)/(bottom-top)*100)
    seconds = round((x-left)/(right-left)*15, 1)
    badge(draw, max(x-2, left+28), y-23, f"{percent}%", MINT, NIGHT, 18)
    badge(draw, min(x+53, right-21), bottom+52, f"{seconds:.1f}s", DARK_GRID, CREAM, 17)
    return image


def glowing_area_chart(t):
    image, draw = plate(True)
    section(draw, "The night shift", "Energy demand · indexed", True)
    chart_axes(draw, dark=True)
    visible = lines_until(sample_chart((24, 37, 31, 48, 72, 92)), phase(t, .18, 2.17))
    baseline = CHART[3]
    left, top, right, _ = CHART
    if len(visible) > 1:
        area = Image.new("L", image.size)
        ImageDraw.Draw(area).polygon([(visible[0][0], baseline), *visible,
                                     (visible[-1][0], baseline)], fill=255)
        glow = Image.new("RGB", image.size)
        glow_draw = ImageDraw.Draw(glow)
        for y in range(top, baseline+1):
            tone = color(NIGHT, (32, 133, 117), (1-(y-top)/(baseline-top))**1.3)
            glow_draw.line((left, y, right, y), fill=tone)
        image.paste(glow, (0, 0), area)
        halo = Image.new("L", image.size)
        ImageDraw.Draw(halo).line(visible, fill=160, width=6, joint="curve")
        halo = halo.filter(ImageFilter.GaussianBlur(7))
        image.paste(MINT, (0, 0, WIDTH, HEIGHT), halo)
        draw.line(visible, fill=MINT, width=4, joint="curve")
        dot(draw, visible[-1], 4, MINT)
    if t > 2.05:
        badge(draw, 549, 109, "Peak 92", MINT, DARK)
    return image


def combo_bars(t):
    image, draw = plate(True)
    section(draw, "Supply and demand", "Indexed activity on one scale", True)
    categories = ("Mon", "Tue", "Wed", "Thu", "Fri")
    chart_axes(draw, categories, dark=True, centered=True)
    left, top, right, bottom = CHART
    step = (right-left)/len(categories)
    xs = [left + (i+.5)*step for i in range(len(categories))]
    values = (24, 55, 43, 64, 70)
    for i, (x, value) in enumerate(zip(xs, values)):
        h = (bottom-top)/100 * value * phase(t, .2+i*.12, .85+i*.12)
        if h:
            draw.rounded_rectangle((x-24, bottom-h, x+24, bottom), radius=4,
                                   fill=(81, 156, 141))
    if t > 1.04:
        line = [(x, bottom - (bottom-top)*v/100)
                for x, v in zip(xs, (38, 39, 60, 70, 91))]
        endpoint = stroke(draw, line, GOLD, width=4, amount=phase(t, 1.04, 2.35))
        dot(draw, endpoint, 4, GOLD)
    draw.rectangle((191, 321, 204, 333), fill=(81, 156, 141))
    label(draw, (212, 319), "Supply", 15, PALE)
    draw.line((330, 327, 349, 327), fill=GOLD, width=3)
    label(draw, (356, 319), "Demand", 15, PALE)
    return image


def animated_bar_chart(t):
    image, draw = plate()
    section(draw, "How viewers found us", "Share of views · %")
    categories = ("Search", "Browse", "Suggested", "Direct")
    chart_axes(draw, categories, unit="%", centered=True)
    left, top, right, bottom = CHART
    step = (right-left)/len(categories)
    xcolors = (FOREST, (81, 121, 96), (129, 159, 117), (179, 193, 147))
    for i, (label_value, c) in enumerate(zip((43, 26, 19, 12), xcolors)):
        x = left+(i+.5)*step
        p = phase(t, .20+i*.27, .83+i*.27)
        h = (bottom-top)*label_value/100*p
        if h >= 1:
            draw.rectangle((x-27, bottom-h, x+27, bottom-1), fill=c)
        if p > .9:
            label(draw, (x, bottom-h-10), f"{label_value}%", 17, INK, "bold", "mb")
    return image


def extruded_bar_chart(t):
    image, draw = plate(True)
    section(draw, "Capacity by region", "Same floor plane · Utilisation %", True)
    origin = (40, 291)
    for i in range(7):
        dx = i*37
        draw.line((origin[0]+dx, origin[1]-i*12, 521+dx, origin[1]-i*12),
                  fill=DARK_GRID, width=1)
    for x in range(45, 604, 66):
        draw.line((x, 291, x+167, 237), fill=DARK_GRID, width=1)
    for i, (x, value, name, tint) in enumerate(zip(
        (118, 290, 462), (48, 82, 64), ("North", "Central", "South"),
        ((95, 176, 158), (237, 174, 92), (122, 150, 171))
    )):
        y = 275
        p = phase(t, .18+i*.27, 1.17+i*.27)
        h = 2.02 * value * p
        if h > 1:
            draw.polygon([(x, y), (x+74, y), (x+74, y-h), (x, y-h)], fill=tint)
            draw.polygon([(x+74, y), (x+104, y-15),
                          (x+104, y-h-15), (x+74, y-h)],
                         fill=color(tint, DARK, .40))
            draw.polygon([(x, y-h), (x+30, y-h-15),
                          (x+104, y-h-15), (x+74, y-h)], fill=color(tint, CREAM, .29))
            if p > .93:
                label(draw, (x+37, y-h+26), f"{value}%", 22, DARK, "bold", "mm")
        label(draw, (x+37, 302), name, 16, PALE, anchor="mt")
    return image


def radial_data_reveal(t):
    image, draw = plate()
    section(draw, "A growing share", "Renewable power · 2024")
    p = phase(t, .19, 2.05)
    cx, cy, r = 202, 212, 94
    arc = (cx-r, cy-r, cx+r, cy+r)
    draw.ellipse(arc, fill=(217, 225, 199))
    draw.pieslice(arc, -90, -90+360*.68*p, fill=FOREST)
    dot(draw, (cx, cy), 65, CREAM)
    dot(draw, (cx, cy), 24, (233, 238, 213))
    draw.line((190, 216, 200, 204, 205, 216, 218, 204), fill=FOREST, width=3, joint="curve")
    label(draw, (346, 143), f"{round(68*p)}%", 72, FOREST, "serif")
    draw.line((351, 225, 540, 225), fill=SAGE, width=2)
    label(draw, (350, 240), "of total generation", 22, INK)
    return image


def count_up_number(t):
    image, draw = plate()
    section(draw, "Registrations to date", "Live tally · Community screenings")
    card(draw, (55, 110, 585, 306), (238, 240, 219), (212, 218, 193))
    p = phase(t, .33, 2.18)
    label(draw, (89, 149), f"{round(620 + 628*p):,}", 80, FOREST, "serif")
    label(draw, (94, 240), "attendees", 22, MUTED)
    for i in range(7):
        x, y = 382+(i%4)*39, 158+(i//4)*57
        fill = color((209, 218, 186), FOREST, phase(t, .3+i*.14, .52+i*.14))
        card(draw, (x, y, x+26, y+45), fill, fill, 6)
        draw.line((x+6, y+27, x+20, y+27), fill=CREAM, width=1)
        dot(draw, (x+13, y+13), 3, CREAM)
    return image


def comparative_chart(t):
    image, draw = plate()
    section(draw, "Two paths, one scale", "Annual recovery · indexed")
    chart_axes(draw)
    a = sample_chart((17, 25, 37, 57, 74, 87))
    b = sample_chart((17, 31, 37, 42, 57, 59))
    stroke(draw, a, FOREST, width=4, amount=phase(t, .12, 1.08))
    if t > .9:
        visible = lines_until(b, phase(t, .9, 2.05))
        if t > 1.88:
            shape = a[2:] + list(reversed(b[2:]))
            draw.polygon(shape, fill=color(PAPER, SAGE, .44*phase(t, 1.88, 2.22)))
            stroke(draw, a, FOREST, width=4)
        stroke(draw, visible, OCHRE, width=4)
    if t > 2.0:
        for y, tone, name in ((a[-1][1], FOREST, "Plan A"), (b[-1][1], OCHRE, "Plan B")):
            dot(draw, (a[-1][0], y), 5, tone)
            badge(draw, 535, y-14, name, tone)
    return image


def chart_cards(t):
    image, draw = plate()
    section(draw, "This week at a glance", "Audience report")
    metrics = (("Reach", "24.8k"), ("Watch time", "8.2h"), ("Completion", "74%"))
    for idx, (name, value) in enumerate(metrics):
        p = phase(t, .13+idx*.38, .67+idx*.38)
        if p == 0:
            continue
        x = 52+idx*182
        offset = 22*(1-p)
        card(draw, (x, 114+offset, x+168, 285+offset), CREAM, GRID)
        label(draw, (x+17, 132+offset), name, 16, MUTED)
        label(draw, (x+16, 157+offset), value, 35, FOREST, "serif")
        q = phase(t, .48+idx*.38, 1.03+idx*.38)
        if idx == 0:
            stroke(draw, [(x+19, 255), (x+46, 239), (x+65, 250), (x+112, 215), (x+147, 221)],
                   FOREST, width=3, amount=q)
        elif idx == 1:
            for j, height in enumerate((18, 24, 29, 48, 44)):
                xx = x + 21+j*25
                draw.rectangle((xx, 263-q*height, xx+14, 263), fill=FOREST)
        else:
            circle = (x+59, 213, x+108, 262)
            draw.arc(circle, -90, 270, GRID, width=7)
            draw.arc(circle, -90, -90+270*q, FOREST, width=7)
    return image


def scorecard(t):
    image, draw = plate(True)
    section(draw, "Edit quality scorecard", "Ratings out of 10", True)
    for i, (criterion, score) in enumerate(
        (("Clarity", 9), ("Pacing", 8), ("Audio", 7), ("Consistency", 9))
    ):
        y = 123+i*49
        label(draw, (153, y+9), criterion, 17, CREAM, anchor="rm")
        card(draw, (172, y, 557, y+19), DARK_GRID, DARK_GRID, 5)
        p = phase(t, .19+i*.27, .9+i*.27)
        if p:
            x = 172 + 385*score/10*p
            fill = (135, 195, 161) if i % 2 == 0 else (188, 202, 136)
            card(draw, (172, y, x, y+19), fill, fill, 5)
        if p > .9:
            label(draw, (579, y+10), str(score), 16, PALE, "bold", "lm")
    for n, tick in enumerate(("0", "2", "4", "6", "8", "10")):
        x = 172 + n*77
        label(draw, (x, 324), tick, 13, PALE, anchor="mt")
    return image

# A fictional coastal region lets the same geographic features stay consistent
# across the map demonstrations.
COAST = [
    (33, 115), (62, 101), (95, 103), (127, 87), (157, 91), (182, 80),
    (222, 95), (249, 87), (281, 99), (307, 91), (350, 92), (380, 106),
    (408, 103), (439, 115), (476, 112), (505, 126), (546, 127), (573, 145),
    (602, 158), (594, 177), (617, 190), (580, 204), (560, 222), (529, 227),
    (509, 247), (472, 254), (448, 268), (413, 264), (386, 285), (356, 281),
    (319, 302), (283, 281), (263, 284), (238, 265), (200, 274), (168, 251),
    (132, 255), (100, 235), (80, 235), (72, 214), (35, 208), (42, 187),
    (21, 169), (40, 147),
]
REGION_WEST = [
    (42, 146), (35, 122), (63, 106), (95, 108), (130, 92), (160, 96), (183, 86),
    (224, 102), (241, 139), (211, 160), (225, 191), (203, 221),
    (210, 265), (173, 247), (132, 250), (102, 229), (82, 229), (74, 208),
    (43, 204), (48, 186), (27, 168),
]
REGION_MID = [
    (224, 102), (251, 93), (281, 104), (307, 97), (351, 98), (383, 112), (408, 109),
    (426, 144), (408, 161), (422, 197), (398, 219), (422, 260), (387, 278),
    (356, 275), (318, 295), (284, 275), (262, 277), (241, 258), (210, 265),
    (203, 221), (225, 191), (211, 160), (241, 139),
]
REGION_EAST = [
    (408, 109), (442, 121), (477, 119), (503, 133), (546, 133), (574, 152),
    (594, 162), (588, 179), (609, 189), (578, 199), (557, 216), (524, 222),
    (506, 241), (472, 249), (449, 260), (422, 260), (398, 219), (422, 197),
    (408, 161), (426, 144),
]
REGIONS = (REGION_WEST, REGION_MID, REGION_EAST)
MAP_NAMES = ("West Reach", "High Ridge", "East Haven")
MAP_POINTS = ((124, 169), (320, 197), (514, 170))
REGION_COLORS = ((172, 192, 149), (213, 171, 104), (140, 177, 172))

ISLETS = (
    [(79, 264), (104, 256), (118, 272), (115, 289), (91, 291), (73, 279)],
    [(444, 299), (469, 281), (494, 292), (487, 309), (467, 319), (444, 313)],
    [(513, 278), (522, 266), (543, 275), (541, 289), (521, 292)],
)
ROUTE = [(90, 204), (116, 188), (143, 193), (172, 211), (200, 204), (232, 176),
         (261, 179), (304, 193), (330, 184), (351, 157), (385, 159), (420, 180),
         (450, 188), (486, 171), (537, 167)]


def map_region(draw, idx, fill, outline):
    draw.polygon(REGIONS[idx], fill=fill)
    draw.line([*REGIONS[idx], REGIONS[idx][0]], fill=outline, width=2, joint="curve")


def map_land(image, textured=False):
    water = (217, 226, 211) if not textured else (206, 213, 190)
    land = (232, 236, 211) if not textured else (229, 221, 188)
    layer = Image.new("RGB", image.size, water)
    geo = ImageDraw.Draw(layer)
    for x in range(33, 640, 38):
        geo.line((x, 81, x, 334), fill=color(water, FOREST, .1))
    for y in range(81, 335, 38):
        geo.line((0, y, 639, y), fill=color(water, FOREST, .1))
    geo.polygon(COAST, fill=land, outline=(160, 174, 141), width=2)
    for islet in ISLETS:
        geo.polygon(islet, fill=land, outline=(160, 174, 141), width=2)
    for pts in REGIONS:
        geo.line([*pts, pts[0]], fill=(190, 197, 167) if not textured else (185, 177, 149),
                 width=1, joint="curve")
    image.paste(layer.crop((0, 81, WIDTH, 335)), (0, 81))
    geo = ImageDraw.Draw(image)
    # Roads and short topographic strokes remain subdued below the active graphic.
    geo.line([(70, 147), (142, 143), (177, 172), (228, 152), (260, 163),
              (323, 145), (396, 151), (454, 133), (555, 153)],
             fill=color(land, MUTED, .29), width=1, joint="curve")
    for n in range(5):
        shift = n*10
        geo.line([(246, 217+shift), (278, 207+shift), (316, 212+shift),
                  (342, 204+shift), (364, 213+shift), (387, 208+shift)],
                 fill=color(land, MUTED, .22), width=1, joint="curve")
    return geo


def map_heading(draw, title, subtitle):
    label(draw, (36, 19), title, 31, INK, "serif")
    label(draw, (38, 58), subtitle, 14, MUTED)
    label(draw, (602, 58), "N", 12, MUTED, "bold", "ra")
    draw.polygon([(610, 61), (620, 61), (615, 48)], fill=FOREST)


def map_region_reveal(t):
    image, draw = plate()
    geo = map_land(image)
    map_heading(geo, "Three coastal districts", "Sample map · regional spotlight")
    for idx, (xy, name, tint) in enumerate(zip(MAP_POINTS, MAP_NAMES, REGION_COLORS)):
        p = phase(t, .2+idx*.61, .61+idx*.61)
        if p:
            map_region(geo, idx, color((232, 236, 211), tint, p), color(GRID, FOREST, .41*p))
        if p > .57:
            label(geo, xy, name, 18, INK, "bold", "mm")
            dot(geo, (89+idx*177, 346), 4, tint)
            label(geo, (100+idx*177, 346), name, 12, MUTED, anchor="lm")
    return image


def animated_map_route(t):
    image, draw = plate()
    geo = map_land(image)
    map_heading(geo, "Across the headlands", "Sample map · harbor to lighthouse")
    p = phase(t, .27, 2.31)
    for i, ((x, y), name) in enumerate(zip((ROUTE[0], ROUTE[7], ROUTE[-1]),
                                          ("Harbor", "Ridge Pass", "Lighthouse"))):
        dot(geo, (x, y), 6, CREAM, FOREST, 2)
        if i != 1 or p > .51:
            badge(geo, x, y+(26 if i < 2 else -25), name, CREAM, INK, 13)
    point = stroke(geo, ROUTE, (244, 239, 207), width=8, amount=p)
    point = stroke(geo, ROUTE, RUST, width=4, amount=p)
    dot(geo, point, 6, RUST, CREAM, 2)
    if p > .97:
        dot(geo, ROUTE[-1], 11, None, RUST, 2)
    return image


@lru_cache(maxsize=1)
def textured_map():
    image, draw = plate(texture=22)
    geo = map_land(image, True)
    for i, (x, y) in enumerate(MAP_POINTS):
        label(geo, (x, y-15), MAP_NAMES[i], 16, MUTED, "serif", "mm")
    noise = ImageOps.colorize(Image.effect_noise(image.size, 22),
                              (113, 90, 55), (255, 237, 201))
    return Image.blend(image, noise, .16)


def textured_documentary_map(t):
    image = textured_map().copy()
    draw = ImageDraw.Draw(image)
    p = phase(t, .26, 1.13)
    if p:
        stroke(draw, [*REGION_MID, REGION_MID[0]], OCHRE, width=4, amount=p)
    zoom = phase(t, .72, 1.55) * (1 - phase(t, 2.2, 3.08))
    # Crop around the highlighted ridge, leaving the coastline in view.
    xpad = 116*zoom
    ypad = 77*zoom
    image = image.transform((WIDTH, HEIGHT), Image.Transform.EXTENT,
                            (xpad*.95, ypad+12*zoom, WIDTH-xpad*1.05, HEIGHT-ypad),
                            resample=Image.Resampling.BILINEAR)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 76), fill=PAPER)
    map_heading(draw, "From shore to ridge", "Sample atlas · northern coast")
    return image


def tower(draw, center, height, fill, cabin=True):
    x, baseline = center
    h = height
    base = h*.24
    top = h*.08
    draw.line((x-base, baseline, x-top, baseline-h, x+top, baseline-h,
               x+base, baseline), fill=fill, width=max(2, round(h/30)))
    for n in range(4):
        y = baseline-h*n/4
        step = base-(base-top)*n/4
        next_step = base-(base-top)*(n+1)/4
        draw.line((x-step, y, x+step, y), fill=fill, width=max(1, round(h/40)))
        draw.line((x-step, y, x+next_step, y-h/4), fill=fill, width=max(1, round(h/55)))
        draw.line((x+step, y, x-next_step, y-h/4), fill=fill, width=max(1, round(h/55)))
    if cabin:
        draw.rectangle((x-h*.14, baseline-h-12, x+h*.14, baseline-h+3), fill=fill)
        draw.polygon([(x-h*.20, baseline-h-11), (x, baseline-h-25),
                      (x+h*.20, baseline-h-11)], fill=fill)


def tree(draw, x, y, h, fill):
    draw.rectangle((x-h*.04, y-h*.26, x+h*.04, y), fill=fill)
    for n in range(3):
        top = y-h+n*h*.23
        span = h*(.22+.05*n)
        draw.polygon([(x, top), (x-span, top+h*.52), (x+span, top+h*.52)], fill=fill)


def hills(draw, width, height, sky, hills_back, hills_mid, fore, shift=0):
    draw.rectangle((0, 0, width, height), fill=sky)
    draw.polygon([
        (-60, height*.74), (width*.13+shift*.22, height*.33), (width*.27+shift*.22, height*.5),
        (width*.42+shift*.22, height*.24), (width*.64+shift*.22, height*.55),
        (width*.76+shift*.22, height*.28), (width+80, height*.59), (width+80, height+5),
        (-60, height+5),
    ], fill=hills_back)
    draw.polygon([
        (-80, height*.78), (width*.18+shift*.63, height*.58), (width*.34+shift*.63, height*.75),
        (width*.58+shift*.63, height*.55), (width*.72+shift*.63, height*.72),
        (width+90, height*.48), (width+90, height+10), (-80, height+10),
    ], fill=hills_mid)
    draw.polygon([
        (-70, height*.80), (width*.19+shift, height*.91), (width*.4+shift, height*.76),
        (width*.68+shift, height*.91), (width+120, height*.85), (width+120, height+20),
        (-70, height+20),
    ], fill=fore)


@lru_cache(maxsize=16)
def archival_image(width, height, variant="street"):
    if variant == "trail":
        scene = source('phone-live',.7).crop((348,25,638,319))
    elif variant == "steps":
        scene = source('steps-live',1.2)
    else:
        scene = source('walk-live',1.8)
    photo = ImageOps.fit(scene,(width,height),Image.Resampling.LANCZOS)
    tint = ImageOps.colorize(ImageOps.autocontrast(photo.convert('L')), (51,47,40), (248,232,192))
    return Image.blend(photo,tint,.72)


def paper_photo(image, x, y, width, height, variant="street", angle=0, caption=None):
    margin = 7
    border = 24 if caption else margin
    tile = Image.new("RGB", (width+margin*2, height+margin+border), CREAM)
    tile.paste(archival_image(width, height, variant), (margin, margin))
    if caption:
        label(ImageDraw.Draw(tile), (margin+1, height+margin+4), caption, 12, INK)
    tile = tile.convert("RGBA").rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    point = (round(x), round(y))
    shadow = Image.new("RGBA", tile.size, (29, 48, 37, 0))
    shadow.putalpha(tile.getchannel("A").filter(ImageFilter.GaussianBlur(4)).point(lambda a: a//4))
    image.paste(shadow, (point[0]+4, point[1]+7), shadow)
    image.paste(tile, point, tile)


def map_evidence_annotation(t):
    image, draw = plate()
    geo = map_land(image)
    map_heading(geo, "Site photo on the map", "Sample map · path survey")
    pin = 301, 184
    p = phase(t, .28, .92) * (1 - phase(t, 2.56, 3.14))
    if p > 0:
        dot(geo, pin, 12+8*sin(phase(t, .3, 1.1)*3.14159), None, (136, 93, 58), 2)
        dot(geo, pin, 5, RUST, CREAM, 2)
        offset = (1-p)*30
        stroke(geo, [pin, (330, 148), (382+offset, 148)], OCHRE,
               width=3, amount=p)
        x, y = 380+offset, 112+offset*.18
        if p > .035:
            before = image.copy()
            paper_photo(image, x, y, 175, 110, "trail", -3, "Photo · north trail")
            image = Image.blend(before,image,p)
    label(ImageDraw.Draw(image), (301, 232), "North trail", 19, INK, "bold", "mm")
    return image


def paper_scrap(draw, x, y, w, h, fill, outline=None):
    rng = Random(917)
    points = [(x, y), (x+w, y), (x+w, y+h)]
    for px in range(round(x+w)-4, round(x), -7):
        points.append((px, y+h+rng.randint(-4, 3)))
    points.append((x, y+h))
    draw.polygon(points, fill=fill, outline=outline)


def archival_paper_collage(t):
    image, draw = plate(texture=25)
    section(draw, "From street to trail", "Sample field archive")
    shift = phase(t, 1.9, 2.75)
    p = phase(t, .14, .79)
    if p:
        paper_scrap(draw, 106-28*(1-p)-12*shift, 114, 393, 164, (221, 209, 170))
    p = phase(t, .6, 1.28)
    if p:
        paper_photo(image, 311+64*(1-p)-15*shift, 129, 197, 122, "street", -8)
    p = phase(t, 1.04, 1.68)
    if p:
        paper_photo(image, 98-78*(1-p)+24*shift, 107+14*(1-p), 221, 145,
                    "trail", 7, "North trail entrance")
    p = phase(t, 1.47, 2.2)
    if p:
        geo = ImageDraw.Draw(image)
        paper_scrap(geo, 337+21*(1-p), 259, 194, 37, (239, 221, 174))
        label(geo, (355+21*(1-p), 269), "Site survey · Field notes", 15, INK, "bold")
    return image


def evidence_board(t):
    image, draw = plate(True, texture=7)
    section(draw, "What connects to the site?", "Sample evidence board", True)
    center = (320, 193)
    card(draw, (247, 134, 393, 253), (233, 224, 192), (233, 224, 192), 5)
    image.paste(archival_image(130, 73), (255, 142))
    label(draw, (320, 231), "Entry street", 17, INK, "bold", "mm")
    satellites = ((53, 111, "Visit log", "08:00 arrival"),
                  (438, 111, "Route map", "North approach"),
                  (53, 235, "Field notes", "Paved access"),
                  (438, 235, "Site photo", "Street entrance"))
    for i, (x, y, title, sub) in enumerate(satellites):
        p = phase(t, .27+i*.44, .64+i*.44)
        if not p:
            continue
        node = (x+126 if x<200 else x, y+23)
        trigger = (247 if x<200 else 393, center[1])
        stroke(draw, [trigger, ((trigger[0]+node[0])/2, node[1]), node], GOLD, width=2, amount=p)
        if p > .22:
            dy = 9*(1-p)
            card(draw, (x, y+dy, x+136, y+61+dy), (44, 75, 67), MIST, 7)
            label(draw, (x+11, y+12+dy), title, 17, CREAM, "bold")
            label(draw, (x+11, y+35+dy), sub, 13, PALE)
            dot(draw, (node[0], node[1]+dy), 3, GOLD)
    return image


def date_and_event_graphic(t):
    image, draw = plate(texture=20)
    section(draw, "The site survey", "Sample event")
    p = phase(t, .26, .98)
    if p:
        y = 104+15*(1-p)
        label(draw, (56, y), "12 August", 29, MUTED, "serif")
        draw.rounded_rectangle((56, y+41, 56+212*p, y+109), radius=5, fill=(235, 189, 108))
        label(draw, (62, y+45), "2024", 66, INK, "serif")
    p = phase(t, 1.02, 1.76)
    if p:
        paper_photo(image, 304+(1-p)*99, 88+16*(1-p), 220, 148, "trail", -5,
                    "North trail entrance")
    p = phase(t, 1.69, 2.32)
    if p:
        label(ImageDraw.Draw(image), (55, 253+8*(1-p)),
              "The team checks", 22, INK, "bold")
        label(ImageDraw.Draw(image), (55, 283+8*(1-p)), "the north entrance", 21, FOREST)
    return image


DOCUMENT_LINES = (
    "Sample document · Northern relay",
    "Inspection report 04",
    "12 August 1948",
    "",
    "The harbor receiver registered a faint tone at dawn.",
    "A signal from the ridge arrived at 06:42.",
    "Operators logged the frequency and opened the line.",
    "The relay held until the afternoon wind picked up.",
    "",
    "Filed with the coastal survey · Report 04",
)


def document_highlight(t):
    image, draw = plate(True)
    p = phase(t, .49, 1.47)
    scale = 1 + p*.34
    width, height = round(467*scale), round(279*scale)
    x, y = (WIDTH-width)/2, 42-27*p
    card(draw, (x, y+5, x+width, y+height+5), (13, 28, 29), (13, 28, 29), 7)
    card(draw, (x, y, x+width, y+height), CREAM, PAPER, 7)
    hs = phase(t, .8, 1.61)
    for i, text in enumerate(DOCUMENT_LINES):
        baseline = y + 19*scale + i*21.3*scale
        if i == 5 and hs:
            draw.rounded_rectangle((x+25*scale, baseline-5, x+(25+335*hs)*scale,
                                    baseline+24*scale), radius=4, fill=(245, 216, 145))
        size = round((21 if i == 1 else 15)*scale)
        fill = INK if i == 5 else color(INK, (127, 128, 101), p)
        if i == 9:
            fill = MUTED
        label(draw, (x+30*scale, baseline), text, size, fill,
              "bold" if i in (1, 5) else "regular")
    return image


def symbol_lit_collage(t):
    image, draw = plate(True, texture=5)
    width, height = image.size
    hills(draw, width, height, (29, 57, 56), (52, 83, 76), (51, 79, 65), (27, 56, 49))
    p = phase(t, .26, 1.19)
    cx, cy = 373, 132
    if p:
        halo = Image.new("L", image.size)
        glow = ImageDraw.Draw(halo)
        for radius, opacity in ((77, 50), (57, 72), (31, 120)):
            dot(glow, (cx, cy), radius*p, round(opacity*p))
        halo = halo.filter(ImageFilter.GaussianBlur(20))
        image.paste(GOLD, (0, 0, WIDTH, HEIGHT), halo)
        draw.ellipse((cx-48*p, cy-48*p, cx+48*p, cy+48*p),
                     outline=color((29, 57, 56), GOLD, p), width=3)
        stroke(draw, [(cx-24, cy+17), (cx+10, cy-25), (cx+26, cy+16), (cx-24, cy+17)],
               GOLD, width=3, amount=p)
    p = phase(t, .81, 1.49)
    if p:
        tower(draw, (329, 321+57*(1-p)), 159, (26, 58, 48))
    for idx, x in enumerate((45, 91, 540, 590)):
        p = phase(t, 1.35+idx*.16, 1.94+idx*.16)
        if p:
            tree(draw, x, 383+50*(1-p), 144+(idx%2)*24, (15, 40, 35))
    label(draw, (41, 31), "Night beacon", 29, CREAM, "serif")
    return image


def chronological_asset_strip(t):
    image, draw = plate(texture=14)
    section(draw, "A morning route", "Sample timeline · hours to scale")
    baseline = 266
    lx, rx = 77, 568
    draw.line((lx, baseline, rx, baseline), fill=(150, 167, 140), width=2)
    events = ((8, "Street", "street"), (9, "Sidewalk", "steps"), (12, "Trail", "trail"))
    for i, (hour, name, variant) in enumerate(events):
        x = lx + ((hour-8)/4)*(rx-lx)
        p = phase(t, .15+i*.56, .66+i*.56)
        dot(draw, (x, baseline), 4, FOREST if p else SAGE)
        label(draw, (x, baseline+16), f"{hour:02d}:00", 18, INK, "bold", "mt")
        if not p:
            continue
        y = 116+35*(1-p)
        tile_left = min(max(x-54, 32), 492)
        paper_photo(image, tile_left, y, 104, 76, variant, 0)
        draw.line((x, y+98, x, baseline), fill=SAGE, width=1)
        label(draw, (tile_left+56, y+108), name, 14, MUTED, anchor="mm")
    if t > 1.95:
        label(draw, (402, 298), "3-hour gap", 16, MUTED, anchor="mt")
    p = phase(t, .14, 1.95)
    if p:
        draw.line((lx, baseline, lx+(rx-lx)*p, baseline), fill=FOREST, width=2)
    return image


def depth_parallax(t):
    p = phase(t,.22,2.77)
    image = shot('room',t,1.1,13*p,0)
    draw = ImageDraw.Draw(image)
    paper_photo(image,363-69*p,72,140,92,'street',-4,'Middle layer')
    paper_photo(image,177-157*p,111,230,148,'trail',8,'Foreground')
    draw.rounded_rectangle((20,17,326,48),6,fill=(27,43,35))
    label(draw,(33,33),"Near layers move farther",19,CREAM,"bold","lm")
    return image


@lru_cache(maxsize=1)
def title_texture():
    size = (590, 214)
    layer = Image.new("L", size)
    draw = ImageDraw.Draw(layer)
    label(draw, (size[0]/2, size[1]/2), "FIELD NOTES", 68, 255, "serif", "mm")
    # Row-wise offsets roughen the edge while preserving the actual contour.
    grain = Image.effect_noise(size, 45).point(lambda a: min(255, max(114, a*2)))
    warped = Image.new("L", size)
    rng = Random(266)
    for y in range(size[1]):
        dx = rng.choice((-1, 0, 0, 0, 1))
        row = layer.crop((0, y, size[0], y+1))
        warped.paste(ImageChops.offset(row, dx, 0), (0, y))
    return layer, Image.composite(warped, Image.new("L", size), grain)


def textured_graphics(t):
    image, draw = plate(texture=13)
    section(draw, "Paper texture on type")
    draw.rectangle((36, 94, 605, 278), fill=(229, 217, 179))
    clean, rough = title_texture()
    p = phase(t, .25, 2.16)
    x = round(clean.width*p)
    mask = clean.copy()
    if x:
        mask.paste(rough.crop((0, 0, x, rough.height)), (0, 0))
    x0, y0 = 25, 80
    image.paste(FOREST, (x0, y0, x0+clean.width, y0+clean.height), mask)
    if 0 < p < 1:
        drag_x = max(38, min(604, x0+x))
        draw.line((drag_x, 100, drag_x, 271), fill=OCHRE, width=1)
        dot(draw, (drag_x, 271), 5, OCHRE)
    label(draw, (37, 303), "Fine paper grain", 16, MUTED)
    label(draw, (603, 303), "Type stays readable", 16, MUTED, anchor="ra")
    return image


SCENES = {
    "draw-on-line-chart": draw_on_line_chart,
    "chart-tracking-marker": chart_tracking_marker,
    "glowing-area-chart": glowing_area_chart,
    "neon-graph-and-bars": combo_bars,
    "animated-bar-chart": animated_bar_chart,
    "extruded-bar-chart": extruded_bar_chart,
    "radial-data-reveal": radial_data_reveal,
    "count-up-number": count_up_number,
    "comparative-chart": comparative_chart,
    "chart-cards": chart_cards,
    "scorecard-reveal": scorecard,
    "map-region-reveal": map_region_reveal,
    "animated-map-route": animated_map_route,
    "textured-documentary-map": textured_documentary_map,
    "map-evidence-annotation": map_evidence_annotation,
    "archival-paper-collage": archival_paper_collage,
    "evidence-board": evidence_board,
    "date-and-event-graphic": date_and_event_graphic,
    "document-highlight": document_highlight,
    "symbol-lit-collage": symbol_lit_collage,
    "chronological-asset-strip": chronological_asset_strip,
    "depth-parallax": depth_parallax,
    "textured-graphics": textured_graphics,
}
