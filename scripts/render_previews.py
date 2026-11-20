"""Encode the original technique demonstrations and their gallery posters."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from preview_common import W, H
from preview_plates import FRAME_RATE

PROJECT = Path(__file__).resolve().parent.parent
PREVIEWS = PROJECT / 'public' / 'previews'
FPS, DURATION = FRAME_RATE, 3.2
MODULES = ('preview_typography', 'preview_spatial', 'preview_data',
           'preview_cuts', 'preview_sound', 'preview_workflows', 'preview_formats')
POSTERS = {
    'payoff-montage': .43,
    'typography-tunnel': 1.1,
    'intro-outro-pair': .76,
    'sheen-caption': 1.35,
    'blur-slide-caption': .7,
    'motion-synced-sound': 1.53,
    'ducked-music': 1.45,
    'smash-cut': .56,
    'variable-pacing': .65,
    'diagonal-mask-wipe': 1.45,
    'pull-in-transition': 1.6,
    'caption-hierarchy': 1.55,
    'stylized-silhouette': 1.5,
    'projected-hud': 1.9,
    'floating-notification': 1.45,
    'floating-card-carousel': 1.63,
    'ar-wayfinding': 1.65,
    'explanatory-b-roll': 1.66,
    'picture-in-picture-demo': 1.74,
    'gesture-triggered-vfx': 2.15,
    'chapter-cards': 1.28,
    'short-clone-split': 1.65,
    'short-role-reverse': 1.53,
    'short-hyperedit': 2.34,
    'short-match-loop': 1.71,
    'long-cold-open': 1.18,
    'long-audio-bridge': 1.1,
    'long-chapter-turn': 1.21,
}

def load_scenes():
    functions, audio = {}, {}
    for name in MODULES:
        if not (PROJECT / 'scripts' / f'{name}.py').exists():
            continue
        module = importlib.import_module(name)
        overlap = set(module.SCENES) & functions.keys()
        if overlap:
            raise ValueError(f'Duplicate scenes: {sorted(overlap)}')
        functions.update(module.SCENES)
        audio.update(getattr(module, 'AUDIO', {}))
    from preview_live_action import SCENES as filmed_scenes
    from preview_phone import SCENES as device_scenes
    revised_scenes = {**filmed_scenes, **device_scenes}
    if missing := revised_scenes.keys() - functions.keys():
        raise ValueError(f'Updated scenes without an original entry: {sorted(missing)}')
    functions.update(revised_scenes)
    return functions, audio

def render(technique, scene, sound, force):
    stem = PREVIEWS / technique
    final_video = stem.with_suffix('.mp4')
    final_poster = stem.with_suffix('.webp')
    if not force and final_video.is_file() and final_poster.is_file():
        return 0

    with TemporaryDirectory(prefix='video-edit-lab-') as tmp:
        temp = Path(tmp)
        video = temp / 'demo.mp4'
        poster = temp / 'poster.webp'
        command = [
            'ffmpeg', '-hide_banner', '-v', 'error', '-y',
            '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', f'{W}x{H}',
            '-framerate', str(FPS), '-i', 'pipe:0',
        ]
        if sound:
            waveform = temp / 'audio.wav'
            sound(waveform)
            command += ['-i', str(waveform), '-c:a', 'aac', '-b:a', '96k']
        command += [
            '-c:v', 'libx264', '-threads', '2', '-preset', 'fast', '-crf', '24',
            '-pix_fmt', 'yuv420p', '-t', str(DURATION), '-movflags', '+faststart', str(video),
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for frame in range(round(FPS * DURATION)):
                image = scene(frame / FPS)
                if image.size != (W, H):
                    raise ValueError(f'{technique} frame {frame} was {image.size}')
                process.stdin.write(image.convert('RGB').tobytes())
            process.stdin.close()
            errors = process.stderr.read().decode()
            if process.wait():
                raise RuntimeError(f'{technique}: ffmpeg failed: {errors}')
        except BaseException:
            if process.poll() is None:
                process.kill()
            process.wait()
            raise

        scene(POSTERS.get(technique, 2.45)).convert('RGB').save(poster, 'WEBP', quality=83, method=3)
        video.replace(final_video)
        poster.replace(final_poster)
    return 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--available', action='store_true', help='Render scenes whose modules are available.')
    parser.add_argument('--section', action='append', help='Render one or more named catalog sections.')
    parser.add_argument('--id', action='append', help='Render one or more technique IDs.')
    parser.add_argument('--force', action='store_true', help='Replace existing encodes.')
    parser.add_argument('--workers', type=int, default=5)
    args = parser.parse_args()
    catalog = json.loads((PROJECT / 'src' / 'catalog.json').read_text())
    catalog_ids = {r['id'] for r in catalog}
    scenes, audio = load_scenes()
    if extras := set(scenes) - catalog_ids:
        raise ValueError(f'Media without a catalog technique: {sorted(extras)}')
    if unknown := set(args.id or []) - catalog_ids:
        parser.error(f'Unknown technique IDs: {", ".join(sorted(unknown))}')
    ids = [r['id'] for r in catalog
           if (not args.section or r['section'] in args.section) and (not args.id or r['id'] in args.id)]
    if args.available:
        ids = [key for key in ids if key in scenes]
    if missing := set(ids) - scenes.keys():
        raise ValueError(f'Techniques without media: {sorted(missing)}')
    PREVIEWS.mkdir(parents=True, exist_ok=True)

    def generate(key):
        result = render(key, scenes[key], audio.get(key), args.force)
        if result:
            print(key, flush=True)
        return result

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        encoded = sum(pool.map(generate, ids))
    print(f'{len(ids)} previews available ({encoded} encoded).', flush=True)

if __name__ == '__main__':
    main()
