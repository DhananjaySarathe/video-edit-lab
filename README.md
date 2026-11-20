# Video Edit Lab

A local React and TypeScript library for turning editing techniques into an AI editing brief. The format library has 340 editing recipes. Every recipe includes a prompt, a use case, and a linked demonstration of the core technique. The technique library contains 114 original MP4 demos with poster images.

## Run locally

```sh
npm ci
npm run dev
```

Vite prints the local address. Selections, order, timing cues, and footage details are stored in the current browser. To make a static production build, run `npm run build`. The output is in `dist/`.

Pushes to `main` build and publish the app through the GitHub Pages workflow.

## Browse the library

- **Reels/Shorts** has 100 hooks, 105 editing styles, and 15 finishes.
- **Long Form** has 24 hooks, 24 intros, 60 editing styles, and 12 finishes.

Each format includes a choice of starter workflows. Add a starter or individual techniques to build one editable prompt with timing cues. Each recipe card names the technique its demo illustrates.

## Change the catalog or media

The app reads format recipes from `src/format-content/` and individual techniques from `src/catalog.json`. Each technique ID has a matching MP4 and WebP poster in `public/previews/`. The previews ship with the project. To regenerate them, install Pillow in a Python environment, make FFmpeg available on PATH, and run `python3 scripts/render_previews.py --force`.

## Demo footage

Python and Pillow composite the visuals frame by frame. FFmpeg encodes them as local MP4s, with locally synthesized audio for the sound examples. The gallery serves its own preview files and plays them muted on hover, with a Sound button on clips that have an audio track. Regenerating the previews requires no account, API key, or paid rendering service.

The project uses ImageGen stills and cropped excerpts of free stock from the contributors below. Tutorial references inform the techniques. The previews contain no footage or audio from those tutorials.

- [ANTONI SHKRABA production, studio presenter](https://www.pexels.com/video/a-footage-of-a-man-talking-8134900/) and [vertical presenter](https://www.pexels.com/video/woman-looking-at-camera-and-speaking-8135208/)
- [Emre Vonal, coffee pour](https://www.pexels.com/video/close-up-of-pouring-milk-to-coffee-13662307/)
- [Taryn Elliott, wide walking shot](https://www.pexels.com/video/a-woman-walking-on-a-sidewalk-5665058/) and [footsteps close-up](https://www.pexels.com/video/a-person-walking-on-a-sidewalk-5665059/)
- [Mger Akopian, handheld phone](https://www.pexels.com/video/hand-holding-phone-12280159/)

The stock clips are used under the [Pexels license](https://www.pexels.com/license/). The maps, charts, and documentary examples use sample information.
