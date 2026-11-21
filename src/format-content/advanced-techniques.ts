import type { Technique } from '../catalog'

export const advancedTechniques: Technique[] = [
  {
    id: 'tech-perspective-foley',
    title: 'Change sound distance without restarting the action',
    section: 'Sound and music',
    useCase: 'A cut from a wide view to a detail during a continuous action, such as footsteps in a street or a hand operating a tool.',
    prompt: "Find the real contact frames in my continuous action and mark the corresponding sound onsets. Keep one set of contact cues and one continuous location bed across the wide and close views. Before the cut, mix the action the way it would sound from farther away, with less sharp detail and a little more room around it. After the cut, bring the clear contact forward. Crossfade only the distance treatment over about 60–120 milliseconds around the picture change. Keep a cut on contact to one onset, even if two microphone tracks are available. Compare the two pictures and the sound together, then play the passage audio-only. The cadence should stay continuous and the change in distance should be audible at a safe listening level. If usable original sound is missing, mark any replacement Foley in the edit notes.",
  },
  {
    id: 'tech-foreground-hand-mask',
    title: 'Let real fingers cover a tracked title',
    section: 'Assets and spatial graphics',
    useCase: 'A gesture crosses one part of a headline and the edit needs to keep the real hand, its gaps and its soft moving edges.',
    prompt: "Pin my short title to a clear surface in the original shot. Find the exact frames where the hand enters, crosses and leaves the letters. Put the title between the source picture and a foreground layer made from the same take. Use a reliable subject matte and refine the hand locally, preserving the openings between fingers. Inspect the isolated matte at the narrowest gap and the fastest movement. Match any feather or blur to the recorded hand edge. Keep the title's position and perspective tied to the background while the hand moves independently. Play the result at full speed and check that letters vanish only where fingers cover them and reappear cleanly in the gaps. If the edge is too soft or detail was lost in capture, keep that part of the word out of the gesture path and flag the shot.",
  },
  {
    id: 'tech-replay-source-clock',
    title: 'Keep the source clock visible across a replay',
    section: 'Cuts, pacing and transitions',
    useCase: 'An instructional or documentary replay where people need to see a small detail without mistaking it for another action.',
    prompt: "Show the original action through its readable outcome at normal speed. Select a short source interval that contains a detail we could not easily see the first time. Reuse that exact source interval in a tighter crop or a clearly labeled slower replay. Keep a visible source-time label tied to the actual frames. Reset that label to the first replay frame and advance it at the true replay rate. On returning to the story, pick up after the last source-time point reached in the first pass. Identify the replay before any duplicated action or extra sound cue could suggest a second event. Compare the replay to the corresponding full source frame and check that the clip ID, direction and action agree. Keep the replay only if it makes a specific detail easier to see.",
  },
]
