"""Drawing primitives for the original motion previews."""
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 640, 360
MAC_FONTS = Path('/System/Library/Fonts/Supplemental')
LINUX_FONTS = Path('/usr/share/fonts/truetype/dejavu')
FONT_NAMES = {
    'regular': ('Arial.ttf', 'DejaVuSans.ttf'),
    'bold': ('Arial Bold.ttf', 'DejaVuSans-Bold.ttf'),
    'serif': ('Georgia.ttf', 'DejaVuSerif.ttf'),
    'mono': ('Courier New.ttf', 'DejaVuSansMono.ttf'),
}

@lru_cache(maxsize=128)
def font(size, weight='bold'):
    mac, linux = FONT_NAMES.get(weight, FONT_NAMES['bold'])
    for path in (MAC_FONTS / mac, LINUX_FONTS / linux):
        if path.is_file():
            return ImageFont.truetype(str(path), max(1, int(size)))
    return ImageFont.load_default(size=max(1, int(size)))

def progress(t, start, end):
    return max(0.0, min(1.0, (t - start) / (end - start)))

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def blend(a, b, x):
    x = max(0.0, min(1.0, x))
    return tuple(round(p + (q - p) * x) for p, q in zip(a, b))

@lru_cache(maxsize=60)
def _backdrop(top, bottom, grid):
    grad = Image.new('RGB', (1, H))
    grad.putdata([blend(top, bottom, i / (H - 1)) for i in range(H)])
    image = grad.resize((W, H))
    if grid:
        draw = ImageDraw.Draw(image, 'RGBA')
        for x in range(0, W, 28):
            draw.line((x, 0, x, H), fill=(180, 186, 160, 29))
        for y in range(0, H, 28):
            draw.line((0, y, W, y), fill=(180, 186, 160, 29))
    return image

def backdrop(top, bottom, grid=False):
    return _backdrop(tuple(top), tuple(bottom), grid).copy()

def ui_frame(draw, box, title=None):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=10, fill='#f4f1e5', outline='#a6b3a6', width=1)
    draw.line((x0, y0 + 24, x1, y0 + 24), fill='#d3d9cb', width=1)
    for i, color in enumerate(('#c78368', '#d7b06b', '#8ca58e')):
        x = x0 + 13 + i * 10
        draw.ellipse((x, y0 + 9, x + 5, y0 + 14), fill=color)
    if title:
        draw.text((x0 + 50, y0 + 12), title, font=font(11, 'regular'), fill='#3d5745', anchor='lm')
