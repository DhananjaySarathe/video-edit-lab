// Sample briefs for testing the compiled prompts in Claude or ChatGPT. Run from the project root:
//   node scripts/prompt-scenarios.mjs <out dir>
// Each scenario is written to <out dir>/<name>.txt. Paste one into a fresh chat and check the reply
// follows the "What to send back" section, takes timings from the transcript and cuts the warm-up,
// the restart and the asides.
import { writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { createServer } from 'vite'

const out = process.argv[2]

// A raw Reels take: a warm-up line, a restart, a real claim the creator makes, filler at the end. About 61 s.
export const reelsTranscript = `00:00 Okay so, um, hi. Today I want to talk about captions.
00:04 So if your captions are at the bottom of the screen... wait, let me start again.
00:08 If your captions sit at the bottom of the screen, half your viewers can't read them.
00:13 Instagram puts its own buttons and the caption text right over that part of the frame.
00:19 I checked my last ten Reels, and in six of them the captions were partly covered.
00:25 The fix is really simple. Move them up to just below the middle of the frame.
00:31 And keep each line to about three words, so it doesn't run under the buttons on the right.
00:37 Here's the same clip, same captions, I only moved them up. And now nothing covers them.
00:44 Oh, and one more thing people forget. The top of the screen.
00:48 Your username and the audio label sit up there, so keep your text below them too.
00:54 So, middle of the frame, three words a line. That's it.
00:58 Now go check your last Reel. Um, yeah. See you.`

// A long-form excerpt in SRT, with a weak intro, an aside about a cat and the payoff.
export const longTranscript = `1
00:00:00,000 --> 00:00:04,200
Hey everyone, welcome back to the channel. Hope you're having a good week.

2
00:00:04,200 --> 00:00:09,800
Today's video is about planning, which I know sounds boring, but stick with me.

3
00:00:09,800 --> 00:00:15,500
So for about two years I used every planning app you can think of, and none of them stuck.

4
00:00:15,500 --> 00:00:21,000
Now I plan my whole week on one page, and it takes me about ten minutes on a Sunday.

5
00:00:21,000 --> 00:00:27,300
By the end of this video you'll have built the same page, starting from a blank sheet of paper.

6
00:00:27,300 --> 00:00:33,900
The page has four sections, and we'll start with the one almost everybody skips.

7
00:00:33,900 --> 00:00:41,000
Section one is the list of things you are not going to do this week. Sounds strange, I know.

8
00:00:41,000 --> 00:00:48,600
But when I write down what I'm dropping, I stop feeling guilty about it on Wednesday.

9
00:00:48,600 --> 00:00:55,200
Um, so, yeah, you just draw a box in the top corner, like this, and fill it in first.

10
00:00:55,200 --> 00:01:03,000
Section two is the real tasks. Three a day, maximum. If it doesn't fit, it goes to next week.

11
00:01:03,000 --> 00:01:09,400
I know three sounds like nothing, but it's three you actually finish.

12
00:01:09,400 --> 00:01:16,800
Sorry, my cat just walked across the desk. Okay. Where was I.

13
00:01:16,800 --> 00:01:24,500
Right, section three. This is the one box for the single thing that has to happen this week.

14
00:01:24,500 --> 00:01:31,000
And section four takes two minutes on Sunday night. It's just a look back at the last week.

15
00:01:31,000 --> 00:01:38,200
Here's my page from this week, all filled in, so you can see how it looks in real life.

16
00:01:38,200 --> 00:01:45,000
If planning isn't your problem but finishing things is, I made a video on that. It's linked here.`

const base = {
  items: [], format: '', automaticFormat: true, footage: '', hookPlacement: 'blend', topic: '', audience: '', platform: '',
  length: '', transcript: '', clips: '', target: 'plan', detail: 'full',
}
const items = ids => ids.map(id => ({ id, cue: '' }))
const reels = {
  ...base,
  items: items(['structure-short-tip', 'th-short-mistake-01', 'move-jump-cut', 'move-word-captions', 'move-punch-in']),
  format: 'Vertical · 9:16', topic: 'Why your captions get covered on Reels', audience: 'New creators who edit on their phone',
  platform: 'instagram', length: '35 seconds', transcript: reelsTranscript,
  clips: 'main-take.mp4 (the whole talking-head take)\nreel-before.mp4 (a Reel with captions at the bottom)\nreel-after.mp4 (the same Reel with captions moved up)\nphone-screen.mov (screen recording of the Instagram app)',
}
export const scenarios = {
  'reels-plan': reels,
  'reels-plan-short': { ...reels, detail: 'short' },
  'reels-capcut': { ...reels, target: 'capcut' },
  'reels-premiere': { ...reels, target: 'premiere' },
  'reels-descript': { ...reels, target: 'descript' },
  'reels-agent': { ...reels, target: 'agent', clips: 'main-take.mp4\nreel-before.mp4\nreel-after.mp4\nphone-screen.mov' },
  'reels-script': {
    ...base, target: 'script', items: items(['structure-short-list', 'th-short-number-list-01']),
    format: 'Vertical · 9:16', topic: 'Three cuts that make a boring talking-head take watchable', audience: 'Creators who film themselves on a phone',
    platform: 'tiktok', length: '40 seconds',
  },
  'long-plan': {
    ...base, items: items(['structure-long-explainer', 'th-long-promise-proof-03', 'move-broll-cutaway', 'move-jump-cut']),
    format: 'Widescreen · 16:9', topic: 'A one-page weekly plan that takes ten minutes', audience: 'People who have tried planning apps and given up',
    platform: 'youtube', transcript: longTranscript,
    clips: 'a-cam.mp4 (main take)\npage-overhead.mp4 (overhead of the page being drawn)\nfinished-page.jpg (photo of this week\'s page)',
    footage: 'This transcript is a shortened version of the video for testing. Plan the edit for what is in it.',
  },
}

if (out) {
  const server = await createServer({ server: { middlewareMode: true }, appType: 'custom', logLevel: 'error' })
  try {
    const { compilePrompt } = await server.ssrLoadModule('/src/prompt.ts')
    for (const [name, edit] of Object.entries(scenarios)) {
      const result = compilePrompt(edit)
      writeFileSync(join(out, `${name}.txt`), result.text)
      console.log(`${name}: ${result.words} words, warnings: ${JSON.stringify(result.warnings)}`)
    }
  } finally {
    await server.close()
  }
}
