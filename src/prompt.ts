import { byId, type FormatMode, type Technique } from './catalog'
import { beatTime, firstPerson, type EditMove } from './creator-hooks/catalog'
import { platforms, type Edit, type EditItem } from './edit'
import { parseTranscript } from './openers'

export type Compiled = { text: string; warnings: string[]; words: number }

type Picked = { item: EditItem; technique: Technique }

const defaultFormat: Record<FormatMode, string> = { short: 'Vertical · 9:16', long: 'Widescreen · 16:9' }
const formatPhrase: Record<string, string> = {
  'Vertical · 9:16': 'vertical 9:16',
  'Widescreen · 16:9': 'horizontal 16:9',
  'Square · 1:1': 'square 1:1',
}
const canvas: Record<string, [number, number]> = {
  'Vertical · 9:16': [1080, 1920],
  'Widescreen · 16:9': [1920, 1080],
  'Square · 1:1': [1080, 1080],
}

/** One top-level key per line, so the example stays readable without filling the prompt. */
const compactJson = (value: Record<string, unknown>) =>
  `{\n${Object.entries(value).map(([key, item]) => `  "${key}": ${JSON.stringify(item)}`).join(',\n')}\n}`

const UNIT = '(s|secs?|seconds?|m|mins?|minutes?)\\b'

/** Read a length such as "20 seconds", "35s", "1:30" or "8–12 min" as seconds. Ranges give their midpoint. */
export function parseSeconds(text: string): number | undefined {
  const value = text.toLowerCase().replace(/[–—]/g, '-')
  const clock = value.match(/\b(\d{1,2}):(\d{2})\b/)
  if (clock) return Number(clock[1]) * 60 + Number(clock[2])
  const range = parseRange(value)
  if (range) return (range[0] + range[1]) / 2
  const single = value.match(new RegExp(`(\\d+(?:\\.\\d+)?)\\s*${UNIT}`))
  if (single) return Number(single[1]) * (single[2].startsWith('m') ? 60 : 1)
}

function parseRange(text: string): [number, number] | undefined {
  const value = text.toLowerCase().replace(/[–—]/g, '-')
  const match = value.match(new RegExp(`(\\d+(?:\\.\\d+)?)\\s*-\\s*(\\d+(?:\\.\\d+)?)\\s*${UNIT}`))
  if (!match) return
  const scale = match[3].startsWith('m') ? 60 : 1
  return [Number(match[1]) * scale, Number(match[2]) * scale]
}

const firstSentence = (text: string) => (text.match(/^.*?[.!?](\s|$)/)?.[0] ?? text).trim()
const timing = (item: EditItem) => item.cue.trim() ? ` Timing: ${item.cue.trim()}.` : ''

function modeOf(technique: Technique): FormatMode | undefined {
  if (technique.mode) return technique.mode
  if (technique.id.startsWith('short-')) return 'short'
  if (technique.id.startsWith('long-')) return 'long'
}

function hookBlock(picked: Picked, edit: Edit, short: boolean, transcript: boolean) {
  const { technique, item } = picked
  const script = edit.target === 'script'
  const hook = technique.creator
  const vertical = technique.mode !== 'long'
  if (hook) {
    const lineAdvice = edit.opener ? (script ? 'Use it as the pattern for the hook options.' : 'It only shows the pattern. I’m opening on my own line, given above.')
      : script ? 'Write my version for this topic, just as short.'
        : transcript ? 'Open on the line in my transcript that does this job best. Use the model line only if nothing in my take fits.'
          : 'Adapt it to my topic and keep it just as short.'
    const lines = [
      `Type: ${hook.typeTitle}. ${hook.why}`,
      `Model line: “${hook.say}” ${lineAdvice}`,
      `On-screen text: “${hook.text}”, ${vertical
        ? 'one line in the upper third from the first frame to about 2.5 seconds'
        : 'a bold title on the side of the frame away from my face or the main subject, for the first 3–5 seconds'}. Adapt the wording to my topic.`,
    ]
    lines.push(`First frame: ${firstPerson(hook.frame)}`)
    lines.push(`Edit move: ${hook.move.title}.`)
    if (!short) {
      lines.push(`${vertical ? 'Next 3 seconds' : 'By 30 seconds'}: ${firstPerson(hook.next)}`)
      lines.push(`Muted check: ${hook.check}`)
    }
    return lines.join('\n') + timing(item)
  }
  const plan = technique.breakdown
  if (plan?.opener) {
    const lines = [`Model: ${technique.title}. Opening line: “${plan.opener}” Adapt it to what I filmed.`]
    if (!short) {
      lines.push(...plan.beats.map(([time, direction]) => `${time}: ${direction}`))
      if (plan.soundDirection) lines.push(`Sound: ${plan.soundDirection}`)
      lines.push(`Check: ${plan.check}`)
    }
    return lines.join('\n') + timing(item)
  }
  return `${technique.title}: ${short ? firstSentence(technique.prompt) : technique.prompt}${timing(item)}`
}

function outputSection(edit: Edit, format: string, vertical: boolean, hookTypes: string[]) {
  const [width, height] = canvas[format] ?? (vertical ? canvas['Vertical · 9:16'] : canvas['Widescreen · 16:9'])
  switch (edit.target) {
    case 'script':
      return [
        hookTypes.length >= 2
          ? `1. Three hook options, each a different type (${hookTypes.slice(0, 3).join('; ')}). For each: the spoken line, the on-screen text and the first shot. Don’t reuse the model line’s wording.`
          : '1. Three hook options that open in genuinely different ways, not three versions of one line. For each: the spoken line, the on-screen text and the first shot.',
        '2. The full script in the structure above. For each beat: the time, the exact words to say and what is on screen.',
        '3. A shot list of every shot, screen recording and B-roll clip I need, in the order I should film them.',
        'Keep it to those three parts.',
      ]
    case 'capcut':
      return [
        'Step-by-step instructions for CapCut, in the order I should do them, grouped like this:',
        '1. Cut: every split and delete, with timestamps.',
        '2. Captions: auto captions, plus the style settings to change.',
        '3. Text: each text layer with its start time, end time and wording.',
        '4. Zooms: the keyframe scale and time for every punch-in.',
        '5. Cutaways and overlays: what goes on top, from when to when.',
        '6. Sound: each sound effect with its time, and the music level.',
        'Only use features CapCut actually has. If a step needs another app, say so.',
      ]
    case 'premiere':
      return [
        '1. A marker list: timecode (HH:MM:SS:FF at 30 fps unless I say otherwise), marker name and what to do there.',
        '2. The cut list: the in and out points to keep from my main take, in order.',
        '3. Titles and captions: the wording, start time, end time and position of each.',
        '4. Effects: every zoom (scale and position keyframes), transition and sound effect, with its timecode.',
      ]
    case 'descript':
      return [
        '1. Transcript edits: each passage to delete, quoted exactly so I can find it.',
        '2. Scenes and layouts: where each new scene starts and which layout it uses (full frame, split, screenshot with my face in a corner).',
        '3. Captions and text: the caption style, and each on-screen title with the words it appears on.',
        '4. Media to add: B-roll, screenshots and sound effects, each tied to the words they go with.',
      ]
    case 'agent':
      return [
        'One JSON object that a script using ffmpeg, Remotion or MoviePy can render, and nothing else. Use this shape:',
        '```json',
        compactJson({
          canvas: { width, height, fps: 30 },
          clips: [{ source: 'file name from my clip list', in: 0, out: 2.4, start: 0, zoom: 1, layout: 'full' }],
          text: [{ start: 0, end: 2.5, content: 'on-screen text', position: 'top', style: 'plate' }],
          captions: { source: 'transcript', words_per_line: 3, highlight: '#FFD400', position: 'lower-middle' },
          sfx: [{ at: 2.1, type: 'whoosh' }],
          music: { level_db: -12, duck_under_voice: true },
          todo: ['anything you could not place'],
        }),
        '```',
        'Times are in seconds on the output timeline. Use my clip names exactly. If you can run code, render it and tell me what you did.',
      ]
    default:
      return [
        '1. The opening: the exact line I should open on (quoted, with its timestamp), the on-screen text, and one sentence on why it works.',
        '2. An edit plan as a table with these columns: Time | What I say | Picture (shot or layout) | On-screen text | Edit move | Sound. One row for every change on screen.',
        '3. Cuts: every line or pause you would remove, quoted, with its timestamp.',
        '4. Still to get: any shot, screenshot or B-roll the plan needs that is not in my material.',
        'Keep the reply to the plan. No general editing advice.',
      ]
  }
}

export function compilePrompt(edit: Edit): Compiled {
  const picked: Picked[] = edit.items.flatMap(item => {
    const technique = byId.get(item.id)
    return technique ? [{ item, technique }] : []
  })
  if (!picked.length && !edit.opener) return { text: '', warnings: [], words: 0 }

  const warnings: string[] = []
  const short = edit.detail === 'short'
  const script = edit.target === 'script'
  const transcript = edit.transcript.trim()
  const platform = platforms.find(option => option.id === edit.platform && option.id)
  const modes = [...new Set(picked.map(entry => modeOf(entry.technique)).filter((mode): mode is FormatMode => !!mode))]
  if (modes.length > 1) warnings.push('You picked Reels/Shorts and Long Form items together. Remove the ones that don’t match this video.')
  const format = edit.format || (modes.length === 1 ? defaultFormat[modes[0]] : '')
  const vertical = format ? !format.startsWith('Widescreen') : modes[0] !== 'long'
  const mode: FormatMode = vertical ? 'short' : 'long'
  if (edit.platform === 'youtube' && format.startsWith('Vertical')) warnings.push('YouTube videos are usually 16:9, but the format is set to 9:16.')
  if (platform && edit.platform !== 'youtube' && format.startsWith('Widescreen')) warnings.push(`${platform.label} is vertical, but the format is set to 16:9.`)

  const structures = picked.filter(entry => entry.technique.structure)
  if (structures.length > 1) warnings.push(`Only one structure can lead the video. The prompt uses the first: ${structures[0].technique.title}.`)
  const structure = structures[0]?.technique.structure
  const hooks = picked.filter(entry => entry.technique.stage === 'hook')
  const chosenMoves = picked.filter(entry => entry.technique.move)
  const endings = picked.filter(entry => entry.technique.stage === 'finish' && !entry.technique.structure)
  const others = picked.filter(entry => !entry.technique.structure && !entry.technique.move
    && entry.technique.stage !== 'hook' && entry.technique.stage !== 'finish')
  if (!transcript && !script) warnings.push('No transcript yet. Paste one under Your video so the timings come from your take, not guesses.')
  if (edit.target === 'agent' && !edit.clips.trim()) warnings.push('List your clip file names under Your video so the JSON can point at real files.')

  const sections: string[] = []
  const add = (title: string, lines: (string | false | undefined)[]) => {
    const body = lines.filter(Boolean)
    if (body.length) sections.push(`## ${title}\n${body.join('\n')}`)
  }

  const shape = formatPhrase[format] ? `${formatPhrase[format]} ` : ''
  const where = platform ? ` for ${edit.platform === 'youtube' ? 'YouTube' : platform.label}` : ''
  sections.push(script
    ? `Write the script and shot list for my ${shape}video${where}, using the brief below. Reply in the format at the end.`
    : `Plan the edit of my ${shape}video${where}, using the brief below. Reply in the format at the end.`)

  add('About the video', [
    edit.topic.trim() && `Topic: ${edit.topic.trim()}`,
    edit.audience.trim() && `Audience: ${edit.audience.trim()}`,
    platform && `Platform: ${platform.label}`,
    format && `Format: ${format}`,
    (edit.length.trim() || structure) && `Target length: ${edit.length.trim() || `${structure!.length}, from the structure`}`,
    edit.footage.trim() && `Notes: ${edit.footage.trim()}`,
  ])

  const clips = edit.clips.split('\n').map(line => line.trim()).filter(Boolean)
  // A Reel cut from a ten-minute take needs one stretch of it, not a squeeze of the whole thing.
  const targetLength = edit.length.trim() || structure?.length || ''
  const lastStart = transcript ? parseTranscript(transcript).at(-1)?.seconds : undefined
  const takeSeconds = lastStart !== undefined ? lastStart + 4 : undefined
  const wanted = parseSeconds(targetLength)
  const excerpt = !script && !!takeSeconds && !!wanted && takeSeconds > wanted * 2.5
  const clock = (seconds: number) => `${Math.floor(Math.round(seconds) / 60)}:${String(Math.round(seconds) % 60).padStart(2, '0')}`
  add(script ? 'What I have so far' : 'My material', [
    transcript ? (script ? 'My notes or draft are at the end, inside <transcript> tags.'
      : `My transcript is at the end, inside <transcript> tags. Take every timing from it.${transcript.includes('-->') ? ''
        : ' Each timestamp marks where a line starts, so treat the next timestamp as where that line ends.'}`)
      : !script && 'I haven’t pasted a transcript. Mark every timing as approximate, or ask me for the transcript before you start.',
    excerpt && `My take runs about ${clock(takeSeconds)} and this video is ${targetLength}, so build it from one stretch that makes sense on its own, or from a few that join cleanly.${edit.target === 'agent' ? '' : ' Start your reply by naming the stretch you used, with its timestamps.'}`,
    clips.length > 0 && `Clips and B-roll I have:\n${clips.map(clip => `- ${clip}`).join('\n')}`,
  ])

  if (edit.opener) {
    const where = edit.opener.stamp ? ` (it starts at ${edit.opener.stamp})` : ''
    add('Opening line', [
      script ? `Build one of the hook options around this line from my notes${where}: “${edit.opener.text}”`
        : `Open on this line from my transcript${where}: “${edit.opener.text}” Keep it whole. Trimming a leading filler word is fine.`,
    ])
    const plain = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
    if (transcript && !plain(transcript).includes(plain(edit.opener.text).split(' ').slice(0, 8).join(' '))) {
      warnings.push('Your pinned opening line isn’t in the transcript any more. Pick it again or unpin it under Your video.')
    }
  }

  const hookMove = hooks[0]?.technique.creator?.move
  const targetSeconds = parseSeconds(edit.length)
  const scale = structure && targetSeconds ? targetSeconds / structure.total : 1
  const scaled = Math.abs(scale - 1) > 0.05
  const round = (value: number) => mode === 'short' ? Math.round(value * scale * 2) / 2 : Math.round(value * scale)
  if (structure && targetSeconds) {
    const range = parseRange(structure.length)
    if (range && targetSeconds < range[0] * 0.85) {
      warnings.push(`A target of ${edit.length.trim()} is shorter than this structure’s ${structure.length}. The beat times are scaled to fit, so expect a beat or two to go.`)
    } else if (range && targetSeconds > range[1] * 1.15) {
      warnings.push(`A target of ${edit.length.trim()} is longer than this structure’s ${structure.length}. The beat times are scaled to fit, so each beat runs longer.`)
    }
  }
  if (structure) {
    add(`Structure: ${structure.title} (${structure.length})`, [
      structure.bestFor,
      `Pacing: ${structure.rhythm}`,
      hooks.length > 0 && 'Use the hook below for the first beat. Its first frame and edit move replace what is listed for that beat.',
      scaled && `Beat times are scaled from the structure’s ${structure.length} to my target of ${edit.length.trim()}. If a beat can’t fit, merge it with the next one or drop it, and say which.`,
      !script && 'Beat times are targets. Keep my sentences whole and let beats shift a little, but still land on the target length.',
      ...structure.beats.map((beat, index) => {
        const times = scaled ? { start: round(beat.start), end: round(beat.end) } : beat
        const head = `${index + 1}. ${beat.title} (${beatTime(times, structure.mode)}): ${firstPerson(beat.goal)}`
        if (short) return head
        const parts = [head, `On screen: ${firstPerson(beat.show)}`]
        if (beat.moves.length && !script) parts.push(`Moves: ${beat.moves.map(move => move.title).join('; ')}.`)
        if (index === 1 && !script && hookMove && beat.moves.some(move => move.id === hookMove.id)) {
          parts.push(`The hook already uses “${hookMove.title}”, so show this beat a different way.`)
        }
        if (script) parts.push(`Example line: “${beat.line}”`)
        return parts.join(' ')
      }),
      structures[0].item.cue.trim() && `Timing: ${structures[0].item.cue.trim()}`,
    ])
  }

  if (hooks.length) {
    const intro = hooks.length > 1 && (edit.hookPlacement === 'separate'
      ? 'Open with hook 1. Use each later hook at its timing cue, or at the next change of subject.'
      : 'Open with hook 1. Borrow from the others only where my footage supports it.')
    add(hooks.length > 1 ? 'Hooks' : 'Hook', [
      intro,
      ...hooks.map((entry, index) => {
        const block = hookBlock(entry, edit, short, !!transcript)
        return hooks.length > 1 ? `Hook ${index + 1}\n${block}` : block
      }),
    ])
  }

  // Moves the person picked, and the hook's move, get full instructions. Moves that only the structure mentions get one line.
  const moves = new Map<string, { move: EditMove; chosen: boolean; detailed: boolean; cue: string }>()
  for (const entry of chosenMoves) moves.set(entry.technique.move!.id, { move: entry.technique.move!, chosen: true, detailed: true, cue: entry.item.cue.trim() })
  for (const entry of hooks) {
    const move = entry.technique.creator?.move
    if (move && !moves.has(move.id)) moves.set(move.id, { move, chosen: false, detailed: true, cue: '' })
  }
  if (!short) for (const beat of structure?.beats ?? []) for (const move of beat.moves) if (!moves.has(move.id)) moves.set(move.id, { move, chosen: false, detailed: false, cue: '' })
  if (moves.size && !script) {
    add('Edit moves', [
      'Use these wherever the structure or hook calls for them. The ones marked “throughout” apply to the whole video.',
      ...[...moves.values()].map(({ move, chosen, detailed, cue }) => short
        ? `- ${move.title}${chosen ? ' (throughout)' : ''}: ${firstPerson(move.when)}`
        : !detailed ? `- ${move.title}: ${firstPerson(move.when)} How often: ${move.often[mode]}`
        : `- ${move.title}${chosen ? ' (throughout)' : ''}: ${move.prompt} How often: ${move.often[mode]}${cue ? ` Timing: ${cue}.` : ''}`),
    ])
  }

  const block = (entry: Picked) => `- ${entry.technique.title}: ${short ? firstSentence(entry.technique.prompt) : entry.technique.prompt}${timing(entry.item)}`
  add('Other techniques', others.map(block))
  add('Ending', endings.map(block))

  const hasMove = (id: string) => moves.has(id)
  add('Rules for the whole video', [
    script ? '- Write the way I talk: short sentences, no filler, nothing I couldn’t say on camera.'
      : '- Keep my sentences whole and use my own words.',
    '- Only use numbers, names and claims that appear in my transcript, footage or notes. Flag anything you had to assume.',
    !script && targetLength && `- Land within about 10% of the target length (${targetLength}). Cut in this order: pauses and fillers, repeated or restarted lines, then lines that don’t move the point. Cut a line that proves something (a number, a test, a result) only if it still runs long, and say what that costs.`,
    !script && !targetLength && '- Keep lines that prove a point (a number, a test, a result). Cut pauses, repeats and lines that don’t move the point first.',
    !script && !hasMove('word-captions') && (vertical
      ? '- Captions: word by word, 2–4 words at a time, with the spoken word highlighted.'
      : '- Subtitles: optional, as short lines at the bottom of the frame.'),
    !script && vertical && `- Keep text and faces out of the top 13% and bottom 20% of the frame and away from the right edge, where ${platform && edit.platform !== 'youtube' ? platform.label : 'the app'} puts its buttons and caption.`,
    !script && edit.platform === 'youtube' && '- If I add end-screen elements, keep the last 5–20 seconds clear behind them.',
    !script && !hasMove('sfx-layer') && '- Keep music well under my voice and duck it while I talk.',
  ])

  const hookTypeTitles = [...new Set([
    ...hooks.flatMap(entry => entry.technique.creator ? [entry.technique.creator.typeTitle] : []),
    ...(structure?.hookTypes.map(type => type.title) ?? []),
  ])]
  add('What to send back', [
    ...outputSection(edit, format, vertical, hookTypeTitles),
    edit.target !== 'agent' && 'Put any assumptions in a short list at the end, not at the start.',
  ])

  const checks = [...new Set([
    ...(structure?.checks ?? []),
    ...hooks.flatMap(entry => entry.technique.creator ? [entry.technique.creator.check] : []),
  ])]
  add(script ? 'Check the script against these' : 'Check the plan against these', (short ? checks.slice(0, 3) : checks).map(check => `- ${check}`))

  const brief = sections.join('\n\n')
  const words = brief.split(/\s+/).filter(Boolean).length
  const text = transcript ? `${brief}\n\n<transcript>\n${transcript}\n</transcript>` : brief
  return { text, warnings, words }
}
