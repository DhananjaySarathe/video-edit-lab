"""Photographic and live-action plates shared by the demo scenes."""
from functools import lru_cache
from math import sin
from pathlib import Path
import subprocess

from PIL import Image, ImageFilter, ImageOps

from preview_common import H, W

PLATES = Path(__file__).resolve().parent / 'assets' / 'plates'
LIVE_SIZES = {'host-live': (640, 360), 'portrait-live': (216, 384),
              'coffee-live': (640, 360), 'walk-live': (640, 360),
              'phone-live': (640, 360), 'steps-live': (640, 360),
              'host-live-matte': (640, 360)}
FRAME_RATE = 20


@lru_cache(maxsize=None)
def still(name):
    regions = {'desk': (0, 0), 'phone': (1, 0), 'coffee': (0, 1), 'street': (1, 1)}
    if name in regions:
        image = still('b-roll')
        x, y = regions[name]
        w, h = image.width // 2, image.height // 2
        return image.crop((x*w + 2, y*h + 2, (x+1)*w - 2, (y+1)*h - 2))
    with Image.open(PLATES / f'{name}.webp') as image:
        return image.copy()


@lru_cache(maxsize=None)
def movie(name):
    w, h = LIVE_SIZES[name]
    is_mask = name == 'host-live-matte'
    pixel_format, mode, channels = ('gray', 'L', 1) if is_mask else ('rgb24', 'RGB', 3)
    frames = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-threads', '1', '-i', str(PLATES / f'{name}.mp4'),
        '-an', '-pix_fmt', pixel_format, '-f', 'rawvideo', 'pipe:1',
    ])
    size = w * h * channels
    return tuple(Image.frombytes(mode, (w, h), frames[i:i+size])
                 for i in range(0, len(frames), size))


def source(name, t):
    if name in LIVE_SIZES:
        frames = movie(name)
        return frames[max(0, min(len(frames) - 1, round(t * FRAME_RATE)))]
    return still(name)


def shot(name, t=0, zoom=1, x=0, y=0, size=(W, H)):
    image = source(name, t)
    width, height = size
    ratio = min(image.width/width, image.height/height) / zoom
    sw, sh = ratio * width, ratio * height
    cx = min(image.width-sw/2, max(sw/2, image.width/2+x*ratio))
    cy = min(image.height-sh/2, max(sh/2, image.height/2+y*ratio))
    return image.transform(size, Image.Transform.EXTENT,
                           (cx-sw/2, cy-sh/2, cx+sw/2, cy+sh/2), Image.Resampling.BICUBIC)


def host_pair(t):
    zoom = 1.26 + .038 * t
    x = -49 + 7*sin(t*1.25)
    return (shot('host-live', t, zoom, x, -52),
            shot('host-live-matte', t, zoom, x, -52))


@lru_cache(maxsize=1)
def foreground():
    image = still('host').convert('RGBA')
    image.putalpha(still('host-matte').getchannel('A'))
    return image


def paste_host(image, x, eyes, scale=1, matte=None, outline=False):
    """Place the same photographed subject at the scene's intended eye position."""
    full = foreground()
    width = max(1, round(565*scale))
    height = max(1, round(width * full.height / full.width))
    cut = full.resize((width, height), Image.Resampling.LANCZOS)
    mask = cut.getchannel('A')
    at = (round(x-width*.5), round(eyes-height*.297))
    if outline:
        edge = ImageOps.expand(mask, border=4)
        edge = edge.filter(ImageFilter.MaxFilter(7))
        image.paste('#f2e3c9', (at[0]-4, at[1]-4), edge)
    if matte is not None:
        image.paste(matte, at, mask)
    else:
        image.paste(cut, at, mask)
