# Video Edit Lab

A React and TypeScript library for building a brief for an AI video editor. Its hook collection includes 2,100 original openings. Each has a first shot, an opening line, a timed turn, a handoff into the body, a playback check and an editable prompt. The library also includes 340 other format recipes, 28 edit breakdowns and 117 individual techniques. [Open Video Edit Lab](https://dhananjaysarathe.github.io/video-edit-lab/)

## Run locally

```sh
npm ci
npm run dev
```

Vite prints the local address. Selections, order, timing cues, and footage details are stored in the current browser. To make a static production build, run `npm run build`. The output is in `dist/`.

Pushes to `main` build and publish the app through the GitHub Pages workflow.

## Browse the library

- **Reels/Shorts** opens with 100 samples in each of 10 hook types. All previews in this tab are native 9:16. The body and finish shelves have 112 and 18 entries respectively.
- **Long Form** opens with 100 samples in each of 11 hook types. The previews are 16:9. The intro, body and finish shelves have 25, 67 and 15 entries respectively.

Choose a hook type or filter by the footage you have. The worked shelves contain 93 Reels/Shorts and 53 Long Form demonstrations, including 20 with audio. The other 1,954 samples have timed shot plans showing how to film and assemble those openings. Open the worked examples for [Reels/Shorts](https://dhananjaysarathe.github.io/video-edit-lab/#reels-shorts/worked) or [Long Form](https://dhananjaysarathe.github.io/video-edit-lab/#long-form/worked). Select a time in the cut plan to play from that beat. Use the link button on a sample to share that exact example. More results load as you scroll.

Add techniques, reorder them, enter your footage and goal, and copy the combined prompt. When a brief contains several hooks, the builder can combine them into one opening or place them at different moments. Personal timing cues take precedence.

## Change the catalog or media

Format recipes and breakdowns live in `src/format-content/`. The 21 hook families, their shootable samples and their timings live in `src/hook-library/`. Existing IDs come from each sample's file and row. Keep those positions stable so personal selections and shared links continue to work.

The gallery ships with its MP4s and WebP posters. To regenerate them locally, use Python with Pillow and install FFmpeg on PATH.

```sh
python3 scripts/render_previews.py
python3 scripts/render_vertical_previews.py
python3 scripts/render_hook_samples.py --complete --update-worked-index --update-timings
```

Use `--force` to replace existing media after changing its source. Use `--id` for a single preview, or `--worked-only` to regenerate the individually directed hook examples. Use `python3 scripts/render_hook_samples.py --complete --validate-only` to validate the full hook catalog.

Run `python3 scripts/verify_catalog_media.py` to check every hook movie and poster against the catalog, including aspect ratio, playback length and audio presence.

## Demo footage

Python and Pillow composite the visuals frame by frame. FFmpeg encodes them as local MP4s, with locally synthesized audio for the sound examples. The gallery serves its own preview files and plays them muted on hover, with a Sound button on clips that have an audio track. Regenerating the previews requires no account, API key, or paid rendering service.

The project uses original motion graphics, existing ImageGen stills and short excerpts of licensed stock. Research footage stays outside the gallery. The timed shot plans illustrate shot order and pacing, and their stock shots can stand in for a subject the creator will film. Documentary readouts, performances and experiments staged for a worked example are identified in the demonstration where relevant.

- [ANTONI SHKRABA production, studio presenter](https://www.pexels.com/video/a-footage-of-a-man-talking-8134900/) and [vertical presenter](https://www.pexels.com/video/woman-looking-at-camera-and-speaking-8135208/)
- [Emre Vonal, coffee pour](https://www.pexels.com/video/close-up-of-pouring-milk-to-coffee-13662307/)
- [Taryn Elliott, wide walking shot](https://www.pexels.com/video/a-woman-walking-on-a-sidewalk-5665058/) and [footsteps close-up](https://www.pexels.com/video/a-person-walking-on-a-sidewalk-5665059/)
- [Mger Akopian, handheld phone](https://www.pexels.com/video/hand-holding-phone-12280159/)
- [Tima Miroshnichenko, sanding in a workshop](https://www.pexels.com/video/person-sanding-a-wood-5058605/) and [turning a camera dial](https://www.pexels.com/video/a-photographer-turning-the-knob-of-a-camera-7205326/)
- [Sergei Starostin, editing at a laptop](https://www.pexels.com/video/man-editing-video-on-laptop-touchpad-39425773/)
- [Polina Kovaleva, writing in a notebook](https://www.pexels.com/video/closeup-video-of-writings-on-a-notebook-5546876/)
- [Los Muertos Crew, chopping garlic](https://www.pexels.com/video/person-chopping-garlic-7601423/)
- [Сергей, sewing blue fabric](https://www.pexels.com/video/close-up-of-sewing-machine-and-blue-fabric-9680519/)

The stock clips are used under the [Pexels license](https://www.pexels.com/license/). The maps, charts, and documentary examples use sample information.
