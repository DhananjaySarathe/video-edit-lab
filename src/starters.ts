import type { FormatMode } from './catalog'

type StarterStep = {
  id: string
  stage: string
  cue: string
}

type Starter = {
  title: string
  footage: string
  steps: StarterStep[]
}

export const starters: Record<FormatMode, Starter[]> = {
  short: [
    {
      title: 'Talking-head tip',
      footage: 'A vertical take of you on camera making one point, with one example you can show.',
      steps: [
        { id: 'th-short-mistake-01', stage: 'Hook', cue: 'Open on my strongest line about the mistake, with the stakes on screen from the first frame.' },
        { id: 'move-jump-cut', stage: 'Body', cue: 'Cut every pause and restart, and keep my sentences whole.' },
        { id: 'move-punch-in', stage: 'Body', cue: 'Punch in on the stressed word of each key sentence, at least 3 seconds apart.' },
        { id: 'move-word-captions', stage: 'Body', cue: 'Word-by-word captions for the whole video.' },
        { id: 'move-broll-cutaway', stage: 'Body', cue: 'Show the example as soon as I name it.' },
        { id: 'vertical-safe-zone', stage: 'Finish', cue: 'Check the whole export against the platform overlay at phone size.' },
      ],
    },
    {
      title: 'One-person sketch',
      footage: 'Two takes with different eyelines and the same camera position.',
      steps: [
        { id: 'short-clone-split', stage: 'Hook', cue: 'Put both versions of me on screen in the opening beat and let one interrupt.' },
        { id: 'short-role-reverse', stage: 'Body', cue: 'Use alternating angles for the argument. Hold one silent reaction before the answer.' },
        { id: 'short-match-loop', stage: 'Finish', cue: 'Return to the opening pose on the last beat so the conversation can restart.' },
      ],
    },
    {
      title: 'Fast product demo',
      footage: 'A clean shot of the result, one process shot, and three details.',
      steps: [
        { id: 'short-proof-burst', stage: 'Hook', cue: 'Show the outcome in the first frame and leave it visible long enough to identify.' },
        { id: 'short-hyperedit', stage: 'Body', cue: 'Build a fast sequence from the three process details. Give the successful result a longer hold.' },
        { id: 'short-match-loop', stage: 'Finish', cue: 'Return to the setup gesture just before the cut back to the opening.' },
      ],
    },
  ],
  long: [
    {
      title: 'Talking-head explainer',
      footage: 'One long take of you on camera, a few screen recordings or B-roll shots, and the finished result.',
      steps: [
        { id: 'th-long-promise-proof-01', stage: 'Hook', cue: 'Show the finished result first, then promise exactly what viewers will be able to do.' },
        { id: 'move-jump-cut', stage: 'Body', cue: 'Remove restarts and long pauses. Keep a breath before the big points.' },
        { id: 'move-broll-cutaway', stage: 'Body', cue: 'Cut to the thing I name while my voice carries on.' },
        { id: 'move-rehook', stage: 'Body', cue: 'Open each chapter with a new question and a visual reset.' },
        { id: 'long-payoff-back', stage: 'Finish', cue: 'Return to the opening result and show what changed.' },
      ],
    },
    {
      title: 'Story-led explainer',
      footage: 'Narration, a strong reveal, and evidence that explains how you got there.',
      steps: [
        { id: 'long-cold-open', stage: 'Hook', cue: 'Start with the most telling moment and leave one specific question unanswered.' },
        { id: 'long-chapter-turn', stage: 'Intro', cue: 'Give the viewer the context for the question, then set up the first chapter.' },
        { id: 'explanatory-b-roll', stage: 'Body', cue: 'Show each piece of evidence as the narration makes the claim it supports.' },
        { id: 'long-payoff-back', stage: 'Finish', cue: 'Return to the opening image and show what the answer changes.' },
      ],
    },
    {
      title: 'Tutorial walkthrough',
      footage: 'One presenter take, a screen recording, and an example of the result.',
      steps: [
        { id: 'side-by-side-reference', stage: 'Hook', cue: 'Compare the starting state and finished result so viewers can see what they will learn.' },
        { id: 'step-breaks-screencast', stage: 'Intro', cue: 'Preview the steps briefly and enter the first task as soon as the goal is clear.' },
        { id: 'guided-zoom-highlight', stage: 'Body', cue: 'Zoom only when a control needs reading, then restore the full view.' },
        { id: 'long-payoff-back', stage: 'Finish', cue: 'Play the finished result at full speed and state how to check it.' },
      ],
    },
    {
      title: 'Interview or podcast',
      footage: 'A conversation, a stable wide shot, and audio for each speaker.',
      steps: [
        { id: 'long-cold-open', stage: 'Hook', cue: 'Open with a revealing answer and enough context to make it intelligible.' },
        { id: 'long-audio-bridge', stage: 'Intro', cue: 'Let the host’s first question start under the establishing shot.' },
        { id: 'ducked-music', stage: 'Body', cue: 'Keep dialogue in front and dip music under speaking.' },
        { id: 'music-reverb-tail', stage: 'Finish', cue: 'Let the last cue decay underneath a short closing image.' },
      ],
    },
  ],
}
