"""Render format-specific hook animatics from original shot plans and local plates."""
import argparse
from bisect import bisect_right
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from hashlib import blake2s
import importlib
import json
from math import sin
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from preview_common import font
from preview_plates import shot
from render_previews import PREVIEWS, PROJECT, render

CATALOG = PROJECT / 'src' / 'hook-library'
FRAMES_PER_SECOND = 15
SIZE = {'short': (360, 640), 'long': (640, 360)}
READ_DETAIL = re.compile(r'\b(read|inspect|label|labels|date|units|scale|receipt|signature|compare|side by side|legend|ingredients|count)\b', re.I)
QUICK_ACTION = re.compile(r'\b(already|drops?|tap|taps|clicks?|snaps?|touches|strikes|grabs?|on contact|first step)\b', re.I)
REAL_HOLD = re.compile(r'\b(pause|hold|listen|trace|compare|match|replay|in real time|without cutting)\b', re.I)
# Plates are existing licensed footage or original art belonging to the lab.
# An animatic illustrates the pacing and editorial treatment of the shot plan.
# It does not present generic stock as footage of the specified event.
PLATES = {
    'presenter': ('host-live', 'desk', 'host-live'),
    'portrait': ('portrait-live', 'host-live', 'portrait-live'),
    'coffee': ('coffee-live', 'coffee-live', 'coffee'),
    'phone': ('phone-live', 'desk', 'phone-live'),
    'street': ('walk-live', 'steps-live', 'street'),
    'steps': ('steps-live', 'walk-live', 'steps-live'),
    'desk': ('editing-live', 'notebook-live', 'host-live'),
    'room': ('room', 'host-live', 'room'),
    'screen': ('editing-live', 'phone-live', 'editing-live'),
    'document': ('notebook-live', 'notebook-live', 'editing-live'),
    'chart': ('editing-live', 'notebook-live', 'host-live'),
    'map': ('walk-live', 'street', 'walk-live'),
    'object': ('workshop-live', 'notebook-live', 'workshop-live'),
    'process': ('workshop-live', 'editing-live', 'workshop-live'),
    'compare': ('editing-live', 'workshop-live', 'notebook-live'),
    'timer': ('steps-live', 'walk-live', 'steps-live'),
    'roles': ('host-live', 'portrait-live', 'host-live'),
    'hands': ('notebook-live', 'workshop-live', 'notebook-live'),
    'archive': ('notebook-live', 'street', 'host-live'),
    'result': ('workshop-live', 'notebook-live', 'workshop-live'),
    'interview': ('host-live', 'portrait-live', 'host-live'),
}
DOMAIN_PLATES = (
    (re.compile(r'\b(coffee|espresso|latte|cappuccino|mug|pour[- ]over)\b'), PLATES['coffee']),
    (re.compile(r'\b(garlic|vegetables?|onion|garnish|tomatoes|recipe|cutting board|food prep|ingredient|kitchen|chef|cooking)\b'), ('cooking-live', 'cooking-live', 'cooking-live')),
    (re.compile(r'\b(camera body|lens|film camera|shutter|dial|aperture|focus ring|viewfinder|tripod|camera strap)\b'), ('camera-live', 'camera-live', 'camera-live')),
    (re.compile(r'\b(fabric|thread|sewing|stitches|hem|presser foot|seam allowance|quilt|zipper|textile)\b'), ('sewing-live', 'sewing-live', 'sewing-live')),
    (re.compile(r'\b(timeline|playhead|keyboard|interface|cursor|screencast|spreadsheet|keyframe)\b'), PLATES['screen']),
    (re.compile(r'\b(ruler|vise|clamp|wooden|woodwork|drill|workbench|sanding|workshop)\b'), PLATES['object']),
    (re.compile(r'\b(notebook|paper|receipt|handwriting|letter|ledger|signature)\b'), PLATES['document']),
    (re.compile(r'\b(phone|notification|smartphone|message|texting)\b'), PLATES['phone']),
    (re.compile(r'\b(footstep|sidewalk|crosswalk|walking|hike|stride|shoe|footpath)\b'), PLATES['street']),
)
PALETTES = (
    ('#eff6d9', '#152719', '#c5dc93'),
    ('#fdf3d8', '#28281e', '#eccb87'),
    ('#eef5ff', '#182331', '#9dccf2'),
    ('#fff4ee', '#352723', '#f1bca3'),
    ('#f5f4e7', '#1e2b29', '#a4d4c4'),
)
PHASE_LABELS = {
    'timer': ('The condition', 'The first action', 'The next attempt'),
    'rewind': ('The result', 'What proves it', 'Earlier'),
    'continuity': ('The prediction', 'Same shot', 'What changed'),
    'match': ('The move', 'The match', 'The new state'),
    'reverse': ('First role', 'Other role', 'The reply'),
    'reaction': ('The reaction', 'What it means', 'The consequence'),
    'reveal': ('The object', 'A closer look', 'The first lead'),
    'fix': ('Before the change', 'The adjustment', 'The retest'),
    'score': ('The options', 'The first test', 'Compare the outcome'),
    'interrupt': ('The decision', 'The turning point', 'What followed'),
    'lesson': ('The promise', 'The working view', 'The first step'),
    'prediction': ('The setup', 'Make a prediction', 'Begin the test'),
    'reversal': ('The original claim', 'New evidence', 'Check the difference'),
}


@dataclass(frozen=True)
class Sample:
    id: str
    mode: str
    kind: str
    title: str
    visual: str
    words: str
    opening: str
    turn: str
    bridge: str
    check: str
    times: tuple
    effect: str


def planned_times(mode, profile, fields, worked):
    base = profile['time']
    if worked:
        return tuple(base)
    opening, turn, bridge = fields[3:6]
    short = mode == 'short'
    durations = [base[i + 1] - base[i] for i in range(3)]
    if READ_DETAIL.search(opening):
        durations[0] += .35 if short else 1.3
    elif QUICK_ACTION.search(opening):
        durations[0] -= .1 if short else .6
    if READ_DETAIL.search(turn) or REAL_HOLD.search(turn):
        durations[1] += .35 if short else 1.7
    elif QUICK_ACTION.search(turn):
        durations[1] -= .15 if short else .8
    if REAL_HOLD.search(bridge):
        durations[2] += .5 if short else 1.5
    times = [0]
    for duration in durations:
        times.append(round(times[-1] + duration, 2))
    return tuple(times)


def read_samples(complete):
    profiles = json.loads((CATALOG / 'types.json').read_text())
    directed, _, _ = worked_examples()
    known = set()
    titles = {}
    examples = []
    for mode, types in profiles.items():
        for profile in types:
            kind = profile['id']
            path = CATALOG / 'seeds' / mode / f'{kind}.txt'
            known.add(path)
            if not path.is_file():
                if complete:
                    raise ValueError(f'Missing sample file {mode}/{path.name}')
                continue
            lines = [line for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
            if len(lines) != 100:
                if complete:
                    raise ValueError(f'{mode}/{path.name} has {len(lines)} rows, expected 100')
                continue
            for i, line in enumerate(lines, 1):
                fields = tuple(part.strip() for part in line.split('|'))
                if len(fields) != 7 or any(not field for field in fields):
                    raise ValueError(f'{mode}/{path.name}:{i} must have seven nonempty fields')
                if fields[1] not in PLATES:
                    raise ValueError(f'{mode}/{path.name}:{i} has unknown visual key {fields[1]!r}')
                identifier = f'hook-{mode}-{kind}-{i:03}'
                title_key = ' '.join(fields[0].casefold().split())
                if title_key in titles:
                    raise ValueError(f'Duplicate title {fields[0]!r} in {identifier} and {titles[title_key]}')
                titles[title_key] = identifier
                times = planned_times(mode, profile, fields, identifier in directed)
                examples.append(Sample(identifier, mode, kind, *fields, times, profile['effect']))
    if unknown := set((CATALOG / 'seeds').glob('*/*.txt')) - known:
        raise ValueError(f'Unknown hook seed files: {sorted(str(path) for path in unknown)}')
    return examples


@lru_cache(maxsize=360)
def view(name, size, frame_number, level, side):
    zoom, bias = ((1.04, 0), (1.24, -24), (1.12, 17))[level]
    if name == 'host-live':
        bias -= 30
    plate = 'phone-board' if name == 'phone-live' else name
    return shot(plate, frame_number / 20, zoom, bias + 12 * side, -16 if name == 'host-live' else 4, size)


def wrap_words(value, typeface, width, max_lines):
    lines = ['']
    for word in value.split():
        candidate = (lines[-1] + ' ' + word).strip()
        if lines[-1] and typeface.getlength(candidate) > width:
            if len(lines) == max_lines:
                while typeface.getlength(lines[-1] + '…') > width and lines[-1]:
                    lines[-1] = lines[-1][:-1]
                lines[-1] = lines[-1].rstrip(' .,:;') + '…'
                break
            lines.append(word)
        else:
            lines[-1] = candidate
    return lines


def evidence_panel(draw, sample, phase, colors, pad, top):
    kind = sample.visual
    if phase != 1 or kind not in {'document', 'chart', 'map', 'screen'}:
        return
    text, ink, color = colors
    short = sample.mode == 'short'
    panel_w, panel_h = (235, 102) if short else (245, 98)
    x, y = pad, top + (124 if short else 49)
    draw.rounded_rectangle((x, y, x + panel_w, y + panel_h), 9, fill=ink)
    if kind == 'screen':
        for index, (start, end) in enumerate(((20, 138), (45, 197), (111, 212))):
            track_y = y + 27 + 17 * index
            draw.rounded_rectangle((x + start, track_y, x + end, track_y + 11), 4,
                                   fill=color if index == 1 else '#637b69')
        draw.line((x + 112, y + 16, x + 112, y + 81), fill=text, width=2)
    elif kind == 'document':
        draw.rounded_rectangle((x + 12, y + 14, x + panel_w - 13, y + 82), 6, fill='#e8eddb')
        for index, extent in enumerate((155, 142, 176, 124)):
            line_y = y + 28 + 12 * index
            if index == 1:
                draw.rectangle((x + 21, line_y - 3, x + 162, line_y + 4), fill=color)
            draw.line((x + 23, line_y, x + 23 + extent, line_y), fill='#374c40', width=1)
    else:
        points = [(x + 21, y + 71), (x + 70, y + 59), (x + 106, y + 69),
                  (x + 144, y + 44), (x + 180, y + 39), (x + 208, y + 22)]
        draw.line(points, fill=color, width=3)
        for px, py in (points[0], points[3], points[-1]):
            draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=text)


def phase_overlay(sample, phase, accent):
    width, height = SIZE[sample.mode]
    short = sample.mode == 'short'
    text, ink, highlight = accent
    pad = 23 if short else 22
    overlay = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(overlay)
    top = 55 if short else 22
    label = 'Timed shot plan'
    label_size = font(14, 'bold')
    label_width = round(label_size.getlength(label)) + 18
    draw.rounded_rectangle((pad, top, pad + label_width, top + 25), 5, fill=ink)
    draw.text((pad + 9, top + 13), label, font=label_size, anchor='lm', fill=text)
    evidence_panel(draw, sample, phase, accent, pad, top)
    board = 382 if short else 224
    draw.rectangle((0, board, width, height), fill=ink)
    stage = PHASE_LABELS[sample.effect][phase]
    stamp = f'{sample.times[phase]:g}–{sample.times[phase + 1]:g} s'
    draw.text((pad, board + 23), stage, font=font(17 if short else 16), fill=highlight, anchor='lm')
    draw.text((width - (48 if short else pad), board + 23), stamp, font=font(14, 'mono'), fill=text, anchor='rm')
    line = (sample.opening, sample.turn, sample.bridge)[phase]
    available = width - pad - (49 if short else pad)
    maximum_rows = 5 if short else 3
    size = 24 if short else 25
    while True:
        face = font(size, 'regular')
        rows = wrap_words(line, face, available, maximum_rows)
        if not rows[-1].endswith('…') or size <= 16:
            break
        size -= 1
    for i, row in enumerate(rows):
        compact = not short and len(rows) >= 3
        y = board + (45 if compact else 50) + i * (size + (2 if compact else 5))
        draw.text((pad, y), row, font=face, anchor='lm', fill=text)
    if phase == 0:
        face, line_height = font(28 if short else 28), 32
        rows = wrap_words(sample.words, face, available - 12, 3 if short else 2)
        anchor_y = board - 27
        for i, row in enumerate(rows):
            y = anchor_y + (i - len(rows) + 1) * line_height
            draw.text((pad, y), row, font=face, anchor='lm', fill=text,
                      stroke_width=2, stroke_fill=ink)
    x0, x1 = pad, width - (48 if short else pad)
    track_y = height - (53 if short else 14)
    track_width = (x1 - x0 - 8) / 3
    for i in range(3):
        start = round(x0 + i * (track_width + 4))
        draw.rectangle((start, track_y, round(start + track_width), track_y + 3), fill=highlight if i == phase else '#607064')
    return overlay, overlay.getchannel('A')


def shared_frame(names, mode, effect, phase, elapsed, variant, times):
    size = SIZE[mode]
    width, height = size
    short = mode == 'short'
    phase_length = times[phase + 1] - times[phase]
    head = 1 + variant * 4
    scaled = round(elapsed * 20 * (.72 if short else .36))
    stamp = min(63, head + scaled)
    name = names[phase]
    if effect in ('continuity', 'match') and phase <= 1:
        name = names[0]
        if phase == 1:
            stamp = min(63, stamp + round(times[1] * 12))
    angle = (0, 1, 2)[phase] if effect != 'continuity' else 0
    frame = view(name, size, stamp, angle, variant - 1).copy()
    if effect == 'fix' and phase == 0:
        frame = ImageEnhance.Brightness(frame).enhance(.82)
    if effect in ('prediction', 'score') and phase <= 1:
        left = view(names[0], size, min(63, head + scaled), 0, -1)
        right = view(names[1], size, min(63, head + scaled), 0, 1)
        if short:
            shared = height // 2
            frame.paste(left.crop((0, 36, width, 36 + shared)), (0, 0))
            frame.paste(right.crop((0, 46, width, 46 + shared)), (0, shared))
        else:
            shared = width // 2
            frame.paste(left.crop((110, 0, 110 + shared, height)), (0, 0))
            frame.paste(right.crop((145, 0, 145 + shared, height)), (shared, 0))
    if effect == 'reverse' and phase == 1:
        frame = ImageOps.mirror(frame)
    if effect == 'match' and phase == 1 and elapsed < .23:
        joined = view(names[1], size, stamp, 0, variant - 1)
        edge = round(width * min(1, elapsed / .23))
        if edge:
            frame.paste(joined.crop((0, 0, edge, height)), (0, 0))
    if effect == 'interrupt' and phase == 2 and elapsed < (.14 if short else .37):
        return Image.new('RGB', size, '#101813')
    if effect == 'rewind' and phase == 2 and elapsed < .34:
        frame = ImageEnhance.Color(frame).enhance(.32)
    if phase_length > 8 and stamp == 63:
        wobble = round(sin(elapsed * .9) * 3)
        if wobble:
            frame = ImageOps.fit(frame.crop((3 + wobble, 3, width - 3 + wobble, height - 3)), size)
    return frame


def cue_layer(frame, mode, effect, phase, elapsed, color):
    draw = ImageDraw.Draw(frame)
    w, h = frame.size
    short = mode == 'short'
    if effect == 'timer' and phase <= 1:
        y = 94 if short else 26
        counter = f'{int(elapsed):02}:{int(elapsed * 10) % 10}'
        x = w - (63 if short else 75)
        draw.rounded_rectangle((x - 43, y, x + 28, y + 30), 5, fill='#182520')
        draw.text((x - 8, y + 15), counter, font=font(17, 'mono'), anchor='mm', fill=color)
    elif effect in ('prediction', 'score') and phase <= 1:
        mid = h // 2 if short else w // 2
        line = (0, mid, w, mid) if short else (mid, 0, mid, h)
        draw.line(line, fill=color, width=2)
        for letter, pos in zip(('A', 'B'), ((w - 42, 101), (w - 42, mid + 14)) if short else ((w // 2 - 26, 40), (w // 2 + 26, 40))):
            x, y = pos
            draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill='#182520')
            draw.text(pos, letter, font=font(14), anchor='mm', fill=color)
    elif effect in ('reveal', 'continuity') and phase == 1:
        x, y = round(w * .56), round(h * (.37 if short else .41))
        length = round(9 + min(1, elapsed * 3) * 15)
        for a, b in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            draw.line(((x + a * length, y + b * 6),
                       (x + a * length, y + b * length),
                       (x + a * 6, y + b * length)), fill=color, width=2)
    return frame


def planned_shots(sample):
    intent = ' '.join((sample.title, sample.opening, sample.turn)).lower()
    return next((plates for rule, plates in DOMAIN_PLATES if rule.search(intent)), PLATES[sample.visual])


def make_scene(sample):
    salt = blake2s(sample.id.encode(), digest_size=2).digest()
    accent = PALETTES[salt[0] % len(PALETTES)]
    variant = salt[1] % 3
    shots = planned_shots(sample)
    shades = [phase_overlay(sample, phase, accent) for phase in range(3)]

    def scene(t):
        phase = min(2, bisect_right(sample.times, t) - 1)
        elapsed = t - sample.times[phase]
        frame = shared_frame(shots, sample.mode, sample.effect, phase, elapsed, variant, sample.times)
        cue_layer(frame, sample.mode, sample.effect, phase, elapsed + (sample.times[phase] if sample.effect == 'timer' else 0), accent[2])
        image, alpha = shades[phase]
        frame.paste(image, (0, 0), alpha)
        return frame

    return scene


@lru_cache(maxsize=1)
def worked_examples():
    scenes, sound, posters = {}, {}, {}
    for path in sorted(Path(__file__).parent.glob('preview_hook_showcase_*.py')):
        module = importlib.import_module(path.stem)
        if duplicate := scenes.keys() & module.SCENES.keys():
            raise ValueError(f'Duplicate worked examples: {sorted(duplicate)}')
        scenes.update(module.SCENES)
        sound.update(getattr(module, 'AUDIO', {}))
        posters.update(getattr(module, 'POSTERS', {}))
    return scenes, sound, posters


def render_sample(sample, force, destination):
    root = destination / 'vertical' if sample.mode == 'short' else destination
    directory = root / 'hooks'
    directory.mkdir(parents=True, exist_ok=True)
    if not force and all((directory / f'{sample.id}.{ext}').exists() for ext in ('mp4', 'webp')):
        return 0
    scenes, sound, posters = worked_examples()
    scene = scenes.get(sample.id) or make_scene(sample)
    return render(sample.id, scene, sound.get(sample.id), force, directory=directory,
                  size=SIZE[sample.mode], poster_at=posters.get(sample.id, 0), duration=sample.times[-1],
                  fps=FRAMES_PER_SECOND, preset='veryfast', quality=23 if sample.id in scenes else 29)


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--format', choices=('short', 'long'))
    cli.add_argument('--id', action='append', help='Render an individual sample ID.')
    cli.add_argument('--type', action='append', dest='types')
    cli.add_argument('--per-type', type=int, help='Render an initial sample of each type.')
    cli.add_argument('--force', action='store_true')
    cli.add_argument('--validate-only', action='store_true')
    cli.add_argument('--complete', action='store_true', help='Require all types to contain exactly 100 examples.')
    cli.add_argument('--worked-only', action='store_true', help='Render the individually directed worked examples.')
    cli.add_argument('--update-worked-index', action='store_true', help='Update the gallery index after adding a worked example.')
    cli.add_argument('--update-timings', action='store_true', help='Write exact shot and playback times for the React cards.')
    cli.add_argument('--workers', type=int, default=5)
    cli.add_argument('--destination', type=Path, default=PREVIEWS)
    args = cli.parse_args()
    samples = read_samples(args.complete)
    scenes, sound, _ = worked_examples()
    index = CATALOG / 'worked-examples.json'
    expected = {key: {'sound': key in sound} for key in sorted(scenes)}
    timing_path = CATALOG / 'shot-times.json'
    timing_data = {}
    for sample in samples:
        group = timing_data.setdefault(f'{sample.mode}/{sample.kind}', [])
        group.append(list(sample.times[1:]))
    if args.update_timings:
        timing_path.write_text(json.dumps(timing_data, separators=(',', ':')) + '\n')
    if args.complete and timing_data != json.loads(timing_path.read_text()):
        raise ValueError('Shot plans and gallery times differ. Refresh --update-timings.')
    if args.update_worked_index:
        index.write_text(json.dumps(expected, indent=2) + '\n')
    if args.complete and (expected != json.loads(index.read_text()) or scenes.keys() - {row.id for row in samples}):
        raise ValueError('Worked examples and catalog index differ. Check registered ids and refresh --update-worked-index.')
    if args.validate_only:
        print(f'Validated {len(samples)} samples in {len({(row.mode, row.kind) for row in samples})} type files.')
        return
    if unknown := set(args.id or []) - {row.id for row in samples}:
        cli.error(f'Unrecognized sample ids: {sorted(unknown)}')
    wanted = [row for row in samples
              if (not args.format or args.format == row.mode) and (not args.types or row.kind in args.types)
              and (not args.worked_only or row.id in scenes)
              and (not args.id or row.id in args.id)
              and (not args.per_type or int(row.id[-3:]) <= args.per_type)]
    print(f'Rendering {len(wanted)} original sample previews.', flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        count = 0
        for i, done in enumerate(pool.map(lambda row: render_sample(row, args.force, args.destination), wanted), 1):
            count += done
            if i % 25 == 0 or i == len(wanted):
                print(f'{i}/{len(wanted)} verified ({count} encoded).', flush=True)


if __name__ == '__main__':
    main()
