"""Encode 9:16 previews for the Reels/Shorts catalog."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import importlib
import json
import subprocess

from PIL import Image

from preview_vertical_catalog import SCENES as NATIVE_CATALOG, SIZE, reframe
from render_previews import FPS, POSTERS, PREVIEWS, PROJECT, load_scenes, render

VERTICAL = PREVIEWS / 'vertical'
MODULES = ('preview_vertical_hooks', 'preview_vertical_evidence', 'preview_vertical_styles',
           'preview_short_finishes', 'preview_new_techniques_vertical')
OPENING_POSTERS = {
    'advanced-test-start': .20,
    'advanced-matched-proof': .50,
    'advanced-rule-retest': .20,
    'advanced-live-score': .00,
    'advanced-artifact-evidence': .00,
    'advanced-contradiction': .00,
    'short-clone-split': .64,
    'short-role-reverse': 1.85,
    'short-hyperedit': 2.56,
    'short-match-loop': 1.91,
    'advanced-hidden-seam': .57,
    'short-screen-world': .21,
    'advanced-anchored-answer': 1.88,
    'short-proof-burst': .10,
    'payoff-montage': .10,
}


def decoded_scene(key):
    frames = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-threads', '1', '-i', str(PREVIEWS / f'{key}.mp4'),
        '-an', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1',
    ])
    w, h = 640, 360
    size = w * h * 3
    view = memoryview(frames)

    def scene(t):
        index = min(round(t * FPS), len(frames) // size - 1) * size
        return Image.frombytes('RGB', (w, h), view[index:index + size].tobytes())

    return scene


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', action='append', help='Render one or more preview IDs.')
    parser.add_argument('--force', action='store_true', help='Replace existing vertical encodes.')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()

    records = json.loads((PROJECT / 'src' / 'catalog.json').read_text())
    catalog = {record['id']: record for record in records}
    _, audio = load_scenes()
    native = dict(NATIVE_CATALOG)
    for name in MODULES:
        module = importlib.import_module(name)
        if overlap := native.keys() & module.SCENES.keys():
            raise ValueError(f'Duplicate vertical scenes: {sorted(overlap)}')
        native.update(module.SCENES)
        audio.update(getattr(module, 'AUDIO', {}))
        OPENING_POSTERS.update(getattr(module, 'POSTERS', {}))

    repairs = importlib.import_module('preview_vertical_repairs')
    if missing := repairs.SCENES.keys() - (native.keys() | catalog.keys()):
        raise ValueError(f'Repaired scenes missing from the catalog: {sorted(missing)}')
    native.update(repairs.SCENES)
    audio.update(getattr(repairs, 'AUDIO', {}))
    OPENING_POSTERS.update(getattr(repairs, 'POSTERS', {}))

    keys = tuple(dict.fromkeys(args.id or [*catalog, *native]))
    if missing := set(keys) - (catalog.keys() | native.keys()):
        parser.error(f'Unknown preview IDs: {", ".join(sorted(missing))}')
    VERTICAL.mkdir(parents=True, exist_ok=True)

    def generate(key):
        if not args.force and all((VERTICAL / f'{key}.{ext}').is_file() for ext in ('mp4', 'webp')):
            return 0
        if key in native:
            scene = native[key]
        else:
            record = catalog[key]
            scene = partial(reframe, key, record['section'], record['title'], decoded_scene(key))
        time = OPENING_POSTERS.get(key, POSTERS.get(key, .45))
        count = render(key, scene, audio.get(key), args.force, directory=VERTICAL, size=SIZE, poster_at=time)
        if count:
            print(key, flush=True)
        return count

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        encoded = sum(pool.map(generate, keys))
    print(f'{len(keys)} vertical previews available ({encoded} encoded).', flush=True)


if __name__ == '__main__':
    main()
