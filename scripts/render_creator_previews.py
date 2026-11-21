"""Encode the talking-head hook previews and the edit-move previews.

Reels/Shorts hooks and moves go to public/previews/vertical/{creator,moves}/ at 9:16.
Long-form hooks and moves go to public/previews/{creator,moves}/ at 16:9.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor

from preview_creator import FPS, build, hook_jobs, move_jobs
from render_previews import PREVIEWS, render


def target(key):
    mode = 'short' if '-short-' in key else 'long'
    folder = 'moves' if key.startswith('move-') else 'creator'
    stem = key.replace(f'move-{mode}-', '') if key.startswith('move-') else key
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
    parser.add_argument('--kind', choices=('hooks', 'moves'), help='Render only hooks or only moves.')
    parser.add_argument('--force', action='store_true', help='Replace existing encodes.')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    keys = {}
    if args.kind != 'moves':
        keys.update(hook_jobs())
    if args.kind != 'hooks':
        keys.update(move_jobs())
    selected = args.id or list(keys)
    if unknown := set(selected) - keys.keys():
        parser.error(f'Unknown preview keys: {", ".join(sorted(unknown))}')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        encoded = sum(pool.map(generate, selected, [args.force] * len(selected)))
    print(f'{len(selected)} creator previews available ({encoded} encoded).', flush=True)


if __name__ == '__main__':
    main()
