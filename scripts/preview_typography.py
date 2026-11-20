"""Original motion studies for hook, title, and caption techniques."""

from functools import lru_cache
from math import cos, pi, radians, sin

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

from preview_common import H, W, backdrop, blend, ease, font, progress
from preview_plates import paste_host as person, shot


PAPER = (245, 239, 219)
INK = (28, 48, 42)
FOREST = (33, 65, 53)
MOSS = (99, 136, 101)
LEAF = (189, 215, 155)
AMBER = (246, 188, 108)
PEACH = (212, 134, 103)
TEAL = (22, 41, 44)
BLUE = (32, 49, 67)
WHITE = (255, 251, 236)
MUTED = (163, 191, 172)
LINE = (93, 122, 110)


def stage(t, start, end):
    return ease(progress(t, start, end))


def mark(draw, x, y, value, size=12, color=MUTED):
    draw.text((x, y), value, font=font(size, 'mono'), fill=color, anchor='lm')


def title(draw, x, y, value, size, color=PAPER, *, weight='bold', anchor='mm', stroke=0):
    draw.text((x, y), value, font=font(size, weight), fill=color, anchor=anchor,
              stroke_width=stroke, stroke_fill=TEAL)


def box(draw, coords, fill, radius=12, outline=None, width=1):
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)


def opening_slate(dark=True, grid=False):
    im = backdrop((28, 54, 47), (17, 33, 38), grid=grid) if dark else backdrop(
        (250, 245, 224), (220, 221, 193), grid=grid
    )
    draw = ImageDraw.Draw(im)
    tone = (68, 96, 83) if dark else (194, 203, 177)
    draw.line((34, 42, 606, 42), fill=tone)
    draw.line((34, 318, 606, 318), fill=tone)
    return im


def stroke_ticks(draw, x, y, width, color):
    draw.line((x, y, x + width, y), fill=color)
    for at in (0, width // 2, width):
        draw.line((x + at, y - 4, x + at, y + 4), fill=color)


@lru_cache(maxsize=16)
def set_plate(theme):
    top, low, window = {
        'sage': ((65, 98, 81), (26, 47, 45), (181, 193, 150)),
        'amber': ((107, 76, 61), (44, 43, 38), (229, 173, 115)),
        'blue': ((68, 93, 112), (24, 39, 51), (148, 190, 192)),
    }[theme]
    image = backdrop(top, low)
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((380, 34, 593, 266), radius=62, fill=blend(top, window, .31))
    d.rounded_rectangle((390, 45, 582, 255), radius=52, fill=window)
    d.line((488, 44, 488, 256), fill=blend(top, window, .48), width=4)
    d.line((392, 145, 581, 145), fill=blend(top, window, .48), width=4)
    d.polygon(((391, 212), (439, 161), (480, 210), (528, 152), (580, 207),
               (580, 233), (402, 252)), fill=blend(top, window, .68))
    d.rectangle((0, 298, 640, 360), fill=blend(low, (17, 29, 33), .34))
    d.line((0, 297, 640, 297), fill=blend(low, window, .35), width=3)
    d.line((79, 172, 79, 296), fill=(147, 129, 91), width=4)
    d.polygon(((49, 179), (112, 179), (97, 124), (63, 124)), fill=(203, 179, 123))
    d.ellipse((48, 174, 112, 185), fill=(238, 211, 148))
    d.rounded_rectangle((514, 275, 571, 298), radius=5, fill=(132, 96, 64))
    for stem in range(5):
        x = 525 + stem * 8
        reach = -12 + 9 * stem
        d.line((541, 276, x + reach, 228 - (stem % 2) * 11), fill=(53, 88, 63), width=3)
        d.ellipse((x + reach - 7, 221 - (stem % 2) * 11,
                   x + reach + 8, 238 - (stem % 2) * 11), fill=(80, 117, 80))
    return image


def footage(t, x=320, eyes=138, theme='sage', scale=1.08):
    # Reframe the filmed host to leave the space each caption example needs.
    return shot('host-live', t, max(1.12, scale + .13), (266-x)/1.4, -39)


def caption_label(image, phrase, y=284, opacity=1, blur=0, scale=1):
    if opacity <= 0:
        return
    layer = Image.new('RGBA', image.size)
    d = ImageDraw.Draw(layer)
    f = font(round(31 * scale))
    width = d.textlength(phrase, font=f)
    box(d, (320 - width / 2 - 20, y - 25, 320 + width / 2 + 20, y + 24),
        (15, 30, 30, 222), radius=9)
    title(d, 320, y, phrase, round(31 * scale), WHITE)
    if blur > 0:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    if opacity < 1:
        alpha = layer.getchannel('A').point(lambda a: round(a * opacity))
        layer.putalpha(alpha)
    image.paste(layer, (0, 0), layer)


def coffee(t, detail=False):
    image = backdrop((116, 74, 52), (58, 40, 36))
    d = ImageDraw.Draw(image)
    for i in range(8):
        y = i * 49 - 20
        d.line((0, y + 20, W, y - 54), fill=(116, 78, 57), width=2)
    if detail:
        d.ellipse((224, 52, 592, 396), fill=(58, 40, 35))
        d.ellipse((209, 34, 564, 377), fill=(223, 223, 189), outline=(237, 233, 200), width=6)
        d.ellipse((236, 64, 534, 355), fill=(135, 78, 44))
        d.arc((250, 80, 520, 346), 215, 540, fill=(198, 133, 64), width=6)
        for index in range(7):
            pull = stage(t, index * .045, .38 + index * .045)
            top = 139 + 19 * index
            width = (84 - index * 9) * pull
            if width > 1:
                d.ellipse((384 - width, top, 384 + width, top + 34), fill=(221, 184, 119))
        d.line((385, 145, 377, 289), fill=(239, 210, 146), width=6)
        return image
    d.ellipse((211, 78, 450, 310), fill=(61, 41, 35))
    d.ellipse((184, 61, 423, 293), fill=(185, 182, 146), outline=(205, 205, 173), width=5)
    d.ellipse((378, 127, 448, 198), fill=(214, 220, 183), outline=(239, 233, 195), width=5)
    d.ellipse((392, 139, 436, 184), fill=(103, 65, 46))
    d.ellipse((211, 80, 400, 269), fill=(237, 235, 202), outline=(254, 249, 219), width=5)
    d.ellipse((223, 93, 387, 258), fill=(137, 85, 49), outline=(201, 147, 79), width=4)
    for i in range(7):
        size = 46 - i * 5
        y = 127 + i * 12
        d.ellipse((306 - size, y, 306 + size, y + 18), fill=(218, 182, 120))
        d.line((306, 129, 300, 223), fill=(247, 215, 152), width=3)
    for x, y in ((130, 243), (149, 224), (175, 245), (463, 262), (471, 242), (477, 279)):
        d.ellipse((x - 10, y - 5, x + 10, y + 5), fill=(69, 43, 35))
        d.arc((x - 9, y - 3, x + 9, y + 3), 180, 352, fill=(153, 98, 59), width=1)
    for i in range(3):
        phase = .8 * i + t * 5
        points = [(270 + i * 30 + sin(phase + k / 9) * 8, 89 - k) for k in range(53)]
        d.line(points, fill=(220, 197, 148), width=2)
    return image


def payoff_montage(t):
    if t < .67:
        return coffee(t)
    if t < 1.32:
        return coffee(t - .67, detail=True)
    im = footage(t, x=402, theme='amber', scale=1.02)
    d = ImageDraw.Draw(im)
    title(d, 48, 112, 'Pour a leaf', 43, PAPER, weight='serif', anchor='lm')
    title(d, 49, 154, 'in three steps.', 30, AMBER, weight='serif', anchor='lm')
    return im


def stacked_hook(t):
    im = set_plate('blue').copy()
    person(im, 458 + 6 * sin(t * 3), 138, 1.15)
    d = ImageDraw.Draw(im)
    for word, base, at, color, face in (
        ('Make the', 37, .16, PAPER, 'serif'),
        ('ordinary', 29, .52, WHITE, 'regular'),
        ('CINEMATIC', 49, .95, AMBER, 'bold'),
    ):
        a = stage(t, at, at + .35)
        y = {'Make the': 107, 'ordinary': 153, 'CINEMATIC': 205}[word]
        if a > .02:
            title(d, 43, y + (1 - a) * 16, word, round(base * (.76 + a * .24)),
                  blend((49, 75, 88), color, a), weight=face, anchor='lm')
    d.line((44, 246, 44 + 174 * stage(t, 1.12, 1.6), 246), fill=LEAF, width=2)
    return im


def kinetic_title(t):
    im = opening_slate(grid=True)
    d = ImageDraw.Draw(im)
    drift = 36 * stage(t, 1.12, 1.96)
    terms = [('Cut', 87, 124, 63, PAPER), ('on', 206, 124, 46, MUTED),
             ('the', 284, 124, 52, PAPER), ('BEAT', 88, 219, 101, AMBER)]
    for i, (value, x, y, size, color) in enumerate(terms):
        reveal = stage(t, .1 + i * .16, .48 + i * .16)
        if reveal > 0:
            title(d, x + drift + (1 - reveal) * (50 if i % 2 else -38),
                  y + (1 - reveal) * 36, value, size, blend(FOREST, color, reveal), anchor='lm')
    stroke_ticks(d, int(339 + drift), 266, 148, LINE)
    return im


def rolling_letters(t):
    im = opening_slate(False)
    letters = 'STILL LIFE'
    d = ImageDraw.Draw(im)
    box(d, (53, 124, 587, 238), (222, 226, 198), radius=12)
    text_canvas = Image.new('RGB', (534, 96), (222, 226, 198))
    td = ImageDraw.Draw(text_canvas)
    f = font(62)
    total = td.textlength(letters, font=f)
    x = (534 - total) / 2
    for i, char in enumerate(letters):
        amount = stage(t, .23 + i * .068, .71 + i * .068)
        if amount > 0:
            offset = (1 - amount) * (68 if i % 2 == 0 else -68)
            title(td, x, 48 + offset, char, 62, FOREST, anchor='lm')
            if amount < .58:
                title(td, x, 48 + offset + (-65 if offset > 0 else 65), char, 62, MOSS, anchor='lm')
        x += td.textlength(char, font=f)
    window = (0, 21, 534, 75)
    im.paste(text_canvas.crop(window), (53, 151))
    d.line((79, 150, 563, 150), fill=(177, 191, 155))
    d.line((79, 207, 563, 207), fill=(177, 191, 155))
    return im


@lru_cache(maxsize=140)
def glyph_image(ch, size, shade, outline=False):
    layer = Image.new('RGBA', (size * 2 + 6, size * 2 + 6))
    d = ImageDraw.Draw(layer)
    kwargs = {'stroke_width': 1, 'stroke_fill': shade} if outline else {}
    d.text((layer.width / 2, layer.height / 2), ch, font=font(size), anchor='mm',
           fill=(0, 0, 0, 0) if outline else shade, **kwargs)
    return layer


def place_glyph(im, ch, x, y, size, turn, shade, outline=False):
    if ch == ' ':
        return
    glyph = glyph_image(ch, size, shade, outline).rotate(
        turn, resample=Image.Resampling.BICUBIC, expand=True
    )
    im.paste(glyph, (round(x - glyph.width / 2), round(y - glyph.height / 2)), glyph)


def typography_tunnel(t):
    im = backdrop((26, 47, 62), (17, 28, 31))
    d = ImageDraw.Draw(im)
    phrase = 'KEEP CUTTING / KEEP CUTTING / '
    depth = stage(t, 0, 2.0)
    fade = 1 - stage(t, 1.66, 2.18)
    if fade > .03:
        for ring in range(4):
            radius = 44 + ring * 38 + depth * (24 + ring * 22)
            width = max(8, round(10 + ring * 4 + depth * 3))
            shade = blend(TEAL, (105 + 27 * ring, 148 + 19 * ring, 135 + 15 * ring), fade)
            for index, char in enumerate(phrase):
                angle = index / len(phrase) * 2 * pi + t * (.6 if ring % 2 == 0 else -.47)
                y = 183 + sin(angle) * radius * .64
                x = 320 + cos(angle) * radius * 1.24
                if -20 < x < W + 20 and -20 < y < H + 20:
                    place_glyph(im, char, x, y, width, 270 - angle * 180 / pi, shade, ring % 2 == 1)
    resolved = stage(t, 1.79, 2.23)
    if resolved > 0:
        title(d, 320, 182 + round((1 - resolved) * 13), 'KEEP CUTTING', 57,
              blend(TEAL, LEAF, resolved))
        d.line((220, 228, 220 + int(resolved * 200), 228), fill=blend(TEAL, LINE, resolved))
    return im


def icon_insert(t):
    if t < .55 or t > 2.57:
        return footage(t, theme='blue')
    im = opening_slate(False)
    d = ImageDraw.Draw(im)
    enter = stage(t, .55, .9)
    y = 132 + round((1 - enter) * 24)
    color = blend(PAPER, FOREST, enter)
    d.ellipse((278, y - 43, 362, y + 41), fill=(222, 228, 194), outline=(185, 203, 160))
    d.arc((292, y - 27, 348, y + 27), 170, 319, fill=color, width=4)
    d.ellipse((313, y - 8, 327, y + 6), outline=color, width=3)
    d.line((305, y + 20, 335, y - 20), fill=color, width=3)
    text_in = stage(t, .93, 1.42)
    title(d, 320, 226 + round((1 - text_in) * 10), 'Guide the eye', 53,
          blend(PAPER, FOREST, text_in), weight='serif')
    d.line((248, 264, 248 + round(144 * text_in), 264), fill=MOSS, width=2)
    return im


def matching_cards(t):
    if 1.14 <= t < 2.03:
        im = footage(t, x=368)
        caption_label(im, 'Keep a steady pace.')
        return im
    im = opening_slate(False)
    d = ImageDraw.Draw(im)
    d.arc((124, 66, 512, 436), 186, 351, fill=(173, 191, 157), width=2)
    d.arc((146, 89, 490, 413), 187, 353, fill=(204, 212, 182), width=2)
    d.ellipse((312, 80, 327, 95), fill=PEACH)
    a = stage(t, 0 if t < 1.14 else 2.03, .4 if t < 1.14 else 2.45)
    color = blend(PAPER, INK, a)
    title(d, 320, 180 + round((1 - a) * 18), 'In the edit' if t < 1.14 else 'See you in the edit',
          59 if t < 1.14 else 50, color, weight='serif')
    stroke_ticks(d, 233, 239, 173, MOSS)
    return im


def reusable_captions(t):
    im = footage(t, theme='sage')
    d = ImageDraw.Draw(im)
    phrases = ['Start with the result.', 'Explain the change.', 'Show it once more.']
    step = min(2, int(t / 1.05))
    p = stage(t % 1.05, 0, .24)
    caption_label(im, phrases[step], y=278 + int((1 - p) * 12), opacity=p, scale=.95)
    for i in range(3):
        x = 204 + i * 79
        box(d, (x, 323, x + 66, 328), AMBER if step == i else LINE, radius=2)
    return im


def blur_slide(t):
    im = footage(t, theme='amber', x=355)
    local = t % 1.52
    enter = stage(local, .04, .37)
    exit_amount = stage(local, 1.09, 1.51)
    caption_label(im, 'Look at the detail.' if t < 1.52 else 'Then pull back.',
                  y=274 + round((1 - enter) * 24),
                  opacity=enter * (1 - exit_amount), blur=exit_amount * 11)
    return im


def focus_pull(t):
    im = ImageEnhance.Brightness(shot('host-live', t, 1.38, -27, -61)).enhance(.69)
    overlay = Image.new('RGBA', im.size)
    d = ImageDraw.Draw(overlay)
    amount = stage(t, .38, 1.08)
    title(d, 608, 159, 'Find the', 38, PAPER, weight='serif', anchor='rm')
    title(d, 610, 215, 'FOCUS', 64, LEAF, anchor='rm')
    overlay = overlay.filter(ImageFilter.GaussianBlur((1 - amount) * 16))
    overlay.putalpha(overlay.getchannel('A').point(lambda a: round(a * stage(t, .34, .67))))
    im.paste(overlay, (0, 0), overlay)
    return im


def caption_hierarchy(t):
    im = footage(t, theme='sage', x=351)
    d = ImageDraw.Draw(im)
    group = int(t >= 1.52)
    weak = 'Give the shot' if group == 0 else 'Then make it'
    strong = 'DEPTH' if group == 0 else 'MOVE'
    accent = stage(t % 1.52, .27, .61)
    box(d, (160, 218, 480, 328), (20, 38, 41), radius=13)
    title(d, 320, 244, weak, 25, PAPER, weight='regular')
    if accent > .02:
        title(d, 320, 289, strong, round(45 + 9 * accent), LEAF)
    return im


def title_mask(words, size=74, y=188, anchor='mm', x=320):
    mask = Image.new('L', (W, H))
    ImageDraw.Draw(mask).text((x, y), words, font=font(size), anchor=anchor, fill=255)
    return mask


def gradient_caption(t):
    im = ImageEnhance.Brightness(shot('room',t,1.02+.09*stage(t,0,3.15))).enhance(.51)
    d = ImageDraw.Draw(im)
    mask = title_mask('Golden hour', 71)
    amount = stage(t, .44, 1.38)
    colors = Image.new('RGB', (W, H))
    c = ImageDraw.Draw(colors)
    for y in range(H):
        p = progress(y, 154, 216)
        shade = blend((253, 224, 146), (216, 117, 97), p)
        c.line((0, y, W, y), fill=blend((218, 222, 192), shade, amount))
    im.paste(colors, (0, 0), mask)
    for i, shade in enumerate(((253, 224, 146), (216, 117, 97))):
        d.ellipse((305 + i * 21, 257, 316 + i * 21, 268),
                  fill=blend(FOREST, shade, amount))
    return im


def bounce_caption(t):
    im = footage(t, theme='blue', x=380)
    local = t % 1.5
    phase = stage(local, .12, .67)
    y = 270 + (1 - phase) * 80 - 112 * sin(phase * pi) * (1 - phase * .75)
    caption_label(im, 'Stay with me.' if t < 1.5 else 'Here comes the cut.',
                  y=round(y), opacity=stage(local, .06, .23))
    d = ImageDraw.Draw(im)
    d.line((98, 307, 176, 307), fill=MUTED)
    return im


def highlighter(t):
    im = footage(t, theme='sage', x=345)
    d = ImageDraw.Draw(im)
    box(d, (118, 241, 524, 307), (22, 37, 35), radius=9)
    a = stage(t, .56, 1.37)
    length = round(155 * a)
    if length > 0:
        box(d, (321, 250, 321 + length, 296), AMBER, radius=min(6, length / 2))
    title(d, 144, 273, 'Keep it', 38, PAPER, weight='regular', anchor='lm')
    letters = Image.new('RGBA', (W, H))
    ld = ImageDraw.Draw(letters)
    title(ld, 335, 273, 'simple.', 38, LEAF, anchor='lm')
    im.paste(letters, (0, 0), letters)
    ld.rectangle((0, 0, W, H), fill=(0, 0, 0, 0))
    title(ld, 335, 273, 'simple.', 38, TEAL, anchor='lm')
    if length > 0:
        dark = letters.crop((321, 246, 321 + length, 300))
        im.paste(dark, (321, 246), dark)
    return im


def sheen_caption(t):
    im = ImageEnhance.Brightness(shot('steps-live',t,1.1,0,-6)).enhance(.33)
    d = ImageDraw.Draw(im)
    word = 'CLEAN CUT'
    mask = title_mask(word, 83)
    title(d, 320, 188, word, 83, (151, 185, 158))
    highlight = Image.new('L', (W, H))
    hd = ImageDraw.Draw(highlight)
    x = round(-80 + stage(t, .54, 2.17) * 790)
    hd.polygon(((x + 24, 106), (x + 57, 106), (x - 35, 248), (x - 68, 248)), fill=250)
    highlight = highlight.filter(ImageFilter.GaussianBlur(11))
    im.paste((255, 247, 209), (0, 0, W, H), ImageChops.multiply(mask, highlight))
    return im


def flicker_caption(t):
    im = ImageEnhance.Brightness(shot('coffee-live', t, 1.15, -12, 8)).enhance(.75)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((280, 219, 613, 291), radius=10, fill=INK, outline=LINE, width=2)
    amplitude = stage(t, .34, .58)
    if .67 < t < .87:
        amplitude *= .4 + (abs(t - .77) / .1) * .58
    if 1.03 < t < 1.18:
        amplitude *= .6 + abs(t - 1.105) / .075 * .4
    title(d, 447, 254, 'FRAME BY FRAME', 32, blend(INK, PAPER, amplitude))
    return im


def rim_caption(t):
    im = ImageEnhance.Brightness(shot('walk-live',t,1.08,0,-17)).enhance(.36)
    d = ImageDraw.Draw(im)
    title(d, 320, 106, 'Let it', 30, PAPER, weight='regular')
    a = stage(t, .16, .6)
    title(d, 322, 191, 'B R E A T H E', 57, blend(TEAL, LEAF, a))
    title(d, 320, 194, 'B R E A T H E', 57, blend(TEAL, (92, 142, 112), a))
    glow = stage(t, .68, 1.12) * (1 - stage(t, 1.12, 1.61))
    if glow > 0:
        x = 162 + stage(t, .58, 1.65) * 316
        y, ray = 169, round(16 * glow)
        d.line((x - ray, y, x + ray, y), fill=AMBER, width=2)
        d.line((x, y - ray, x, y + ray), fill=AMBER, width=2)
    return im


def social_frame(t, adjusted):
    im = footage(t, theme='amber', x=320).crop((218, 0, 421, 360))
    d = ImageDraw.Draw(im)
    correction = stage(t, .45, 1.41) if adjusted else 0
    if adjusted and .25 < t < 2.35:
        d.rounded_rectangle((12, 25, 161, 284), radius=8, outline=LEAF, width=2)
    title(d, 85, 21 + 36 * correction, 'LOOK HERE', 17, PAPER, stroke=1)
    title(d, 85, 320 - 75 * correction, 'The key detail', 18, LEAF, stroke=1)
    for cy in (195, 224, 253):
        d.ellipse((170, cy, 185, cy + 15), outline=PAPER, width=2)
    d.line((17, 303, 107, 303), fill=PAPER, width=3)
    d.line((17, 319, 141, 319), fill=PAPER, width=3)
    d.line((17, 332, 114, 332), fill=PAPER, width=2)
    return im.resize((142, 252), Image.Resampling.LANCZOS)


def vertical_safe(t):
    im = opening_slate(False)
    d = ImageDraw.Draw(im)
    for x, safe in ((145, False), (353, True)):
        box(d, (x - 5, 47, x + 147, 307), TEAL, radius=15)
        im.paste(social_frame(t, safe), (x, 51))
        mark(d, x + 2, 328, 'Overlays collide' if not safe else 'Safe framing', 13,
             (109, 68, 54) if not safe else FOREST)
    a = stage(t, .55, 1.27)
    d.rounded_rectangle((350, 48, 497, 305), radius=8, outline=blend((203, 205, 179), MOSS, a),
                        width=3)
    return im


def behind_subject(t):
    image = set_plate('sage').copy()
    d = ImageDraw.Draw(image)
    emerge = stage(t, .12, .73)
    title(d, 320, 177 + round((1 - emerge) * 24), 'GO DEEPER', 92,
          blend((54, 89, 73), (241, 203, 135), emerge))
    person(image, 320 + 75 * sin(t * 1.65), 130, 1.26)
    return image


def curved_subject(t):
    im = backdrop((44, 71, 75), (21, 35, 43), grid=True)
    d = ImageDraw.Draw(im)
    x0, y0 = 315 + 34 * sin(t * 1.85), 192
    sweep = .48 * sin(t * 1.21)
    amount = stage(t, .18, .9)
    guide = (round(x0 - 166), 55, round(x0 + 166), 329)
    d.arc(guide, 180, 355, fill=blend(TEAL, MOSS, amount), width=2)
    letters = 'WORDS THAT FOLLOW'
    for i, char in enumerate(letters):
        angle = radians(193 + 9.5 * i) + sweep
        x, y = x0 + cos(angle) * 167, y0 + sin(angle) * 100
        place_glyph(im, char, x, y, 25, 270 - angle * 180 / pi,
                    blend(TEAL, AMBER, amount))
    person(im, x0, 157, 1.07)
    return im


def crosshair(draw, x, y, color, radius=25):
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = x + sx * radius, y + sy * radius
        draw.line((px, py - sy * 11, px, py, px - sx * 11, py), fill=color, width=2)


def subject_locked(t):
    im = opening_slate(False)
    d = ImageDraw.Draw(im)
    shift = 49 * sin(t * 2.04)
    for index, x in enumerate((39, 331)):
        left = index == 0
        crop_shift = 0 if left else shift
        source = footage(t, x=320 + shift, eyes=135, theme='blue')
        panel = source.crop((round(98 + crop_shift), 32, round(542 + crop_shift), 300))
        panel = panel.resize((268, 162), Image.Resampling.LANCZOS)
        box(d, (x - 3, 96, x + 271, 264), INK, radius=7)
        im.paste(panel, (x, 99))
        marker_x = x + 134 + (shift * .60 if left else 0)
        crosshair(d, marker_x, 163, AMBER if left else LEAF, 29)
        mark(d, x + 1, 82, 'Camera frame' if left else 'Tracked reframe', 13, FOREST)
    return im


def silhouette(t):
    if t < .53 or t > 2.68:
        return footage(t, theme='sage', x=320 + 22 * sin(t * 2))
    im = open_silhouette(t)
    motion = 34 * sin(t * 3)
    person(im, 319 + motion, 150, 1.13, matte=(222, 151, 111), outline=True)
    return im


def open_silhouette(t):
    im = backdrop((53, 61, 72), (24, 34, 44))
    d = ImageDraw.Draw(im)
    a = stage(t, .53, 1.15)
    for i in range(3):
        radius = (89 + i * 27) * a
        if radius > 1:
            d.arc((320 - radius, 178 - radius, 320 + radius, 178 + radius),
                  195, 338, fill=blend((49, 62, 74), (124, 142, 129), 1 - i * .22), width=2)
    return im


SCENES = {
    'payoff-montage': payoff_montage,
    'stacked-hook-text': stacked_hook,
    'staggered-kinetic-title': kinetic_title,
    'rolling-letter-reveal': rolling_letters,
    'typography-tunnel': typography_tunnel,
    'icon-and-text-insert': icon_insert,
    'intro-outro-pair': matching_cards,
    'animated-caption-layers': reusable_captions,
    'blur-slide-caption': blur_slide,
    'focus-pull-text': focus_pull,
    'caption-hierarchy': caption_hierarchy,
    'gradient-caption': gradient_caption,
    'bounce-settle-caption': bounce_caption,
    'highlight-sweep-caption': highlighter,
    'sheen-caption': sheen_caption,
    'brief-text-flicker': flicker_caption,
    'rim-lit-caption': rim_caption,
    'vertical-safe-zone': vertical_safe,
    'text-behind-subject': behind_subject,
    'curved-tracked-text': curved_subject,
    'subject-locked-reframe': subject_locked,
    'stylized-silhouette': silhouette,
}
