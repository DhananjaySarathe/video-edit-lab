"""Encode the talking-head hook previews and the edit-move previews.

Reels/Shorts hooks, moves and structures go to public/previews/vertical/{creator,moves,structures}/ at 9:16.
Long-form ones go to public/previews/{creator,moves,structures}/ at 16:9.
Structure renders also write src/creator-hooks/structure-timings.json, the start of each beat in the example.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json

from preview_creator import DATA, FPS, Sequence, build, hook_jobs, move_jobs, structure_jobs
from render_previews import PREVIEWS, render


def target(key):
    mode = 'short' if '-short-' in key else 'long'
    if key.startswith('move-'):
        folder, stem = 'moves', key.replace(f'move-{mode}-', '')
    elif key.startswith('structure-'):
        folder, stem = 'structures', key.replace(f'structure-{mode}-', '')
    else:
        folder, stem = 'creator', key
    directory = (PREVIEWS / 'vertical' / folder) if mode == 'short' else (PREVIEWS / folder)
    return directory, stem


def generate(key, force):
    plan, scene, sound = build(key)
    directory, stem = target(key)
    directory.mkdir(parents=True, exist_ok=True)
    return render(stem, scene, sound, force, directory=directory, size=plan.size, poster_at=plan.poster,
                  duration=plan.total, fps=FPS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', action='append', help='Render one or more preview keys (th-… or move-…).')
    parser.add_argument('--kind', choices=('hooks', 'moves', 'structures'), help='Render only one kind of preview.')
    parser.add_argument('--force', action='store_true', help='Replace existing encodes.')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    keys = {}
    if args.kind in (None, 'hooks'):
        keys.update(hook_jobs())
    if args.kind in (None, 'moves'):
        keys.update(move_jobs())
    if args.kind in (None, 'structures'):
        keys.update(structure_jobs())
    selected = args.id or list(keys)
    if unknown := set(selected) - keys.keys():
        parser.error(f'Unknown preview keys: {", ".join(sorted(unknown))}')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        encoded = sum(pool.map(generate, selected, [args.force] * len(selected)))
    print(f'{len(selected)} creator previews available ({encoded} encoded).', flush=True)
    if any(key.startswith('structure-') for key in selected):
        timings = {f'{mode}/{template["id"]}': Sequence(template, mode, index).timings()
                   for mode, template, index in structure_jobs().values()}
        (DATA / 'structure-timings.json').write_text(json.dumps(timings, indent=2) + '\n')
        print(f'Wrote timings for {len(timings)} structures.', flush=True)


if __name__ == '__main__':
    main()
