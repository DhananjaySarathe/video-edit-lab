"""Validate the local gallery's published hook media and baseline preview paths."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from PIL import Image


PROJECT = Path(__file__).resolve().parent.parent
HOOK_LIBRARY = PROJECT / 'src' / 'hook-library'
FORMATS = {'short': ('vertical/hooks', (360, 640)), 'long': ('hooks', (640, 360))}
SAMPLES_PER_TYPE = 100
FPS = 15
FRAME_TOLERANCE = Fraction(1, FPS) + Fraction(1, 1_000_000)
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
EXTENSIONS = ('.mp4', '.webp')


@dataclass(frozen=True)
class Hook:
    identifier: str
    stem: Path
    size: tuple[int, int]
    duration: Fraction
    sound: bool


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def time_value(value):
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f'Invalid time value {value!r}') from error


def expected_hooks():
    types = read_json(HOOK_LIBRARY / 'types.json')
    timings = read_json(HOOK_LIBRARY / 'shot-times.json')
    worked = read_json(HOOK_LIBRARY / 'worked-examples.json')
    if types.keys() != FORMATS.keys():
        raise ValueError('Expected short and long categories in types.json.')
    hooks = {}
    groups = set()
    for mode, profiles in types.items():
        folder, size = FORMATS[mode]
        for profile in profiles:
            kind = profile['id']
            group = f'{mode}/{kind}'
            if not SLUG.fullmatch(kind) or group in groups:
                raise ValueError(f'Invalid or repeated hook category {group!r}.')
            groups.add(group)
            seeds = HOOK_LIBRARY / 'seeds' / mode / f'{kind}.txt'
            seed_count = sum(bool(line.strip()) for line in seeds.read_text(encoding='utf-8').splitlines())
            plans = timings.get(group, [])
            if seed_count != SAMPLES_PER_TYPE or len(plans) != seed_count:
                raise ValueError(f'{group} needs {SAMPLES_PER_TYPE} seeds and timing plans; '
                                 f'found {seed_count} seeds and {len(plans)} plans.')
            for index, plan in enumerate(plans, 1):
                identifier = f'hook-{mode}-{kind}-{index:03}'
                times = tuple(map(time_value, plan))
                if len(times) != 3 or not 0 < times[0] < times[1] < times[2]:
                    raise ValueError(f'{identifier} has an invalid shot-time plan.')
                sound = worked.get(identifier, {'sound': False}).get('sound')
                if not isinstance(sound, bool):
                    raise ValueError(f'{identifier} needs a boolean sound flag.')
                hooks[identifier] = Hook(identifier, Path(folder) / identifier, size, times[-1], sound)
    if unknown := timings.keys() - groups:
        raise ValueError(f'Unknown timing groups: {", ".join(sorted(unknown))}')
    if unknown := worked.keys() - hooks.keys():
        raise ValueError(f'Unknown worked example IDs: {", ".join(sorted(unknown))}')
    return hooks


def check_video(path, hook, ffprobe):
    command = [ffprobe, '-v', 'error', '-show_entries',
               'stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,duration:format=format_name',
               '-of', 'json', str(path)]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=20)
        metadata = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        detail = (getattr(error, 'stderr', None) or str(error)).strip().splitlines()[0]
        return [f'cannot probe MP4 ({detail})']

    errors = []
    if 'mp4' not in metadata.get('format', {}).get('format_name', '').split(','):
        errors.append('file is not an MP4 container')
    streams = metadata.get('streams', [])
    pictures = [stream for stream in streams if stream.get('codec_type') == 'video']
    if len(pictures) != 1:
        errors.append(f'expected one video stream, found {len(pictures)}')
    else:
        picture = pictures[0]
        if picture.get('codec_name') != 'h264':
            errors.append(f'expected H.264, found {picture.get("codec_name")}')
        size = picture.get('width'), picture.get('height')
        if size != hook.size:
            errors.append(f'video dimensions {size}, expected {hook.size}')
        for field in ('r_frame_rate', 'avg_frame_rate'):
            try:
                if time_value(picture.get(field)) != FPS:
                    errors.append(f'{field} is {picture.get(field)}, expected {FPS}/1')
            except ValueError:
                errors.append(f'missing or invalid {field}')
        try:
            duration = time_value(picture.get('duration'))
            if abs(duration - hook.duration) > FRAME_TOLERANCE:
                errors.append(f'video lasts {float(duration):.3f}s, expected {float(hook.duration):.3f}s ± one frame')
        except ValueError:
            errors.append('missing or invalid video duration')

    sounds = [stream for stream in streams if stream.get('codec_type') == 'audio']
    if len(sounds) != int(hook.sound):
        errors.append(f'found {len(sounds)} audio streams, expected {int(hook.sound)} from worked-examples.json')
    elif hook.sound and sounds[0].get('codec_name') != 'aac':
        errors.append(f'expected AAC audio, found {sounds[0].get("codec_name")}')
    return errors


def check_poster(path, size):
    try:
        with Image.open(path) as image:
            image.load()
            if image.format != 'WEBP':
                return [f'poster is {image.format}, expected WebP']
            if image.size != size:
                return [f'poster dimensions {image.size}, expected {size}']
    except (OSError, ValueError) as error:
        return [f'cannot decode WebP ({error})']
    return []


def check_hook(hook, destination, ffprobe):
    stem = destination / hook.stem
    video, poster = (stem.with_suffix(extension) for extension in EXTENSIONS)
    errors = check_video(video, hook, ffprobe) if video.is_file() else ['missing MP4']
    errors += check_poster(poster, hook.size) if poster.is_file() else ['missing WebP']
    return [f'{hook.stem}: {message}' for message in errors]


def check_hook_paths(hooks, destination):
    owners = {}
    errors = []
    for hook in hooks:
        alternate = Path(FORMATS['long' if hook.size[0] < hook.size[1] else 'short'][0]) / hook.identifier
        for extension in EXTENSIONS:
            expected = hook.stem.with_suffix(extension)
            resolved = (destination / expected).resolve()
            if previous := owners.get(resolved):
                errors.append(f'{expected} and {previous} resolve to the same media path')
            owners[resolved] = expected
            wrong = alternate.with_suffix(extension)
            if (destination / wrong).is_file():
                errors.append(f'{expected} also appears in the other format as {wrong}')
    return errors


def check_baseline(destination):
    catalog = read_json(PROJECT / 'src' / 'catalog.json')
    identifiers = [row['id'] for row in catalog]
    if len(set(identifiers)) != len(identifiers) or any(not SLUG.fullmatch(key) for key in identifiers):
        raise ValueError('Expected valid, distinct IDs in src/catalog.json.')
    errors = []
    for folder in (Path(), Path('vertical')):
        for identifier in identifiers:
            for extension in EXTENSIONS:
                relative = folder / f'{identifier}{extension}'
                path = destination / relative
                if not path.is_file() or not path.stat().st_size:
                    errors.append(f'{relative}: missing or empty baseline file')
    return len(identifiers), errors


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--destination', type=Path, default=PROJECT / 'public' / 'previews',
                     help='Preview directory to check, such as dist/previews.')
    cli.add_argument('--workers', type=int, default=min(8, os.cpu_count() or 4),
                     help='Number of simultaneous ffprobe processes.')
    cli.add_argument('--id', action='append', help='Check a specific hook instead of the full library. Repeat for more IDs.')
    args = cli.parse_args()
    if args.workers < 1:
        cli.error('--workers must be at least 1')
    if not (ffprobe := shutil.which('ffprobe')):
        cli.error('ffprobe is required and must be on PATH')

    try:
        hooks = expected_hooks()
        if unknown := set(args.id or []) - hooks.keys():
            cli.error(f'Unknown hook IDs: {", ".join(sorted(unknown))}')
        selected = [hook for key, hook in hooks.items() if not args.id or key in args.id]
        errors = check_hook_paths(selected, args.destination)
        baseline_count, baseline_errors = (0, []) if args.id else check_baseline(args.destination)
        errors.extend(baseline_errors)
    except (OSError, KeyError, TypeError, ValueError) as error:
        cli.error(str(error))

    print(f'Checking {len(selected)} of {len(hooks)} hook MP4/WebP pairs.', flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, problems in enumerate(pool.map(lambda hook: check_hook(hook, args.destination, ffprobe), selected), 1):
            errors.extend(problems)
            if index % 500 == 0 and index < len(selected):
                print(f'{index}/{len(selected)} pairs checked.', flush=True)

    if errors:
        for error in errors[:25]:
            print(error, file=sys.stderr)
        if len(errors) > 25:
            print(f'{len(errors) - 25} additional problems omitted.', file=sys.stderr)
        print(f'Found {len(errors)} media problems.', file=sys.stderr)
        return 1

    print(f'Verified {len(selected)} hook MP4/WebP pairs.')
    if baseline_count:
        print(f'Found MP4 and WebP files in both formats for all {baseline_count} baseline techniques.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
