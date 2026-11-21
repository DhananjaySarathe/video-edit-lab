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
           'preview_cuts', 'preview_sound', 'preview_workflows', 'preview_formats',
           'preview_advanced', 'preview_advanced_short', 'preview_advanced_hooks', 'preview_advanced_long',
           'preview_long_finishes', 'preview_new_techniques')
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
    'advanced-test-start': .12,
    'advanced-rule-retest': 2.82,
    'advanced-hidden-seam': .42,
    'advanced-contradiction': 1.50,
    'advanced-live-score': 1.60,
    'advanced-artifact-evidence': 1.90,
    'advanced-matched-proof': 1.83,
    'advanced-anchored-answer': 2.45,
    'advanced-clock-chart': 2.57,
    'advanced-threshold': 1.20,
    'advanced-model-handoff': 2.66,
    'advanced-evidence-answer': 2.42,
    'advanced-intro-proof': 2.56,
    'advanced-decision-hold': 1.88,
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
        POSTERS.update(getattr(module, 'POSTERS', {}))
    from preview_live_action import SCENES as filmed_scenes
    from preview_phone import SCENES as device_scenes
    import preview_landscape_repairs as repairs
    revised_scenes = {**filmed_scenes, **device_scenes, **repairs.SCENES}
    POSTERS.update(repairs.POSTERS)
    audio.update(getattr(repairs, 'AUDIO', {}))
    if missing := revised_scenes.keys() - functions.keys():
        raise ValueError(f'Updated scenes without an original entry: {sorted(missing)}')
    functions.update(revised_scenes)
    return functions, audio

def render(technique, scene, sound, force, *, directory=PREVIEWS, size=(W, H), poster_at=None,
           duration=DURATION, fps=FPS, preset='fast', quality=24):
    stem = directory / technique
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
            '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', f'{size[0]}x{size[1]}',
            '-framerate', str(fps), '-i', 'pipe:0',
        ]
        if sound:
            waveform = temp / 'audio.wav'
            sound(waveform)
            command += ['-i', str(waveform), '-c:a', 'aac', '-b:a', '96k']
        command += [
            '-c:v', 'libx264', '-threads', '2', '-preset', preset, '-crf', str(quality),
            '-pix_fmt', 'yuv420p', '-t', str(duration), '-movflags', '+faststart', str(video),
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for frame in range(round(fps * duration)):
                image = scene(frame / fps)
                if image.size != size:
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

        poster_time = POSTERS.get(technique, 2.45) if poster_at is None else poster_at
        scene(poster_time).convert('RGB').save(poster, 'WEBP', quality=83, method=3)
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
    scenes, audio = load_scenes()
    sections = {item['id']: item['section'] for item in catalog}
    sections.update((key, 'Edit breakdowns') for key in scenes if key.startswith('advanced-'))
    sections.update((key, 'Advanced techniques') for key in scenes if key.startswith('tech-'))
    if extras := scenes.keys() - sections.keys():
        raise ValueError(f'Media without a catalog technique: {sorted(extras)}')
    if unknown := set(args.id or []) - sections.keys():
        parser.error(f'Unknown technique IDs: {", ".join(sorted(unknown))}')
    ids = [key for key, section in sections.items()
           if (not args.section or section in args.section) and (not args.id or key in args.id)]
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
