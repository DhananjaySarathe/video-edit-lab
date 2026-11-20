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
    {
      title: 'Talking-head tip',
      footage: 'A vertical presenter take with one claim and one concrete example.',
      steps: [
        { id: 'text-behind-subject', stage: 'Hook', cue: 'Reveal a short phrase behind me on the first claim and leave my face clear.' },
        { id: 'caption-hierarchy', stage: 'Body', cue: 'Emphasize one meaningful word per phrase and let the example hold.' },
        { id: 'vertical-safe-zone', stage: 'Finish', cue: 'Check the whole export against the platform overlay at phone size.' },
      ],
    },
  ],
  long: [
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
