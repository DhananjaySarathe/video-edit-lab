import shortTypes from './short.json'
import longTypes from './long.json'
import moveList from './moves.json'
import structureData from './structures.json'
import structureTimings from './structure-timings.json'
import type { Collection, FormatMode, Technique } from '../catalog'

export type Preset = 'talking-head' | 'screen' | 'podcast' | 'faceless' | 'product' | 'vlog'

export const presets: readonly { id: Preset; label: string }[] = [
  { id: 'talking-head', label: 'Talking head' },
  { id: 'screen', label: 'Talking head + screen' },
  { id: 'podcast', label: 'Podcast or interview' },
  { id: 'faceless', label: 'Faceless: voiceover + B-roll' },
  { id: 'product', label: 'Product or hands-on' },
  { id: 'vlog', label: 'Vlog or on the move' },
]
const presetLabel = new Map(presets.map(preset => [preset.id, preset.label]))

type RawHook = {
  say: string
  text: string
  frame: string
  move: string
  next: string
  for: string[]
}
type RawType = { id: string; title: string; why: string; formula: string; check: string; hooks: RawHook[] }

export type EditMove = (typeof moveList)[number]

export type CreatorHook = {
  say: string
  text: string
  frame: string
  next: string
  presets: Preset[]
  presetLabels: string[]
  move: EditMove
  typeId: string
  typeTitle: string
  why: string
  formula: string
  check: string
}

export type HookType = { id: string; title: string; why: string; formula: string; check: string; count: number }

export const moves: readonly EditMove[] = moveList
export const moveById = new Map(moves.map(move => [move.id, move]))
const soundMoves = new Set(['sfx-layer', 'kinetic-slam', 'freeze-frame', 'rehook', 'reaction-insert'])
export const moveGroups = [...new Set(moves.map(move => move.group))]

export const moveTechniqueId = (id: string) => `move-${id}`

const keepCase = (match: string, word: string) => match[0] === match[0].toUpperCase() ? word[0].toUpperCase() + word.slice(1) : word

/** Cards talk to the creator ("your face"); prompts speak as the creator ("my face"). */
function firstPerson(text: string) {
  return text
    .replace(/\byou weren't\b/gi, "I wasn't")
    .replace(/\byou were\b/gi, 'I was')
    .replace(/\byou're\b/gi, "I'm")
    .replace(/\byou've\b/gi, "I've")
    .replace(/\byou'd\b/gi, "I'd")
    .replace(/\byou'll\b/gi, "I'll")
    .replace(/\byourself\b/gi, match => keepCase(match, 'myself'))
    .replace(/\byours\b/gi, match => keepCase(match, 'mine'))
    .replace(/\byour\b/gi, match => keepCase(match, 'my'))
    .replace(/\b(behind|with|message|told|held|for|beside|affected|to|surprised|needs|in)\s+you\b/gi, '$1 me')
    .replace(/\byou(?=\s+(?:in|with)\b|\s+\w+ing\b)/gi, match => keepCase(match, 'me'))
    .replace(/\byou\b/gi, 'I')
}

function hookPrompt(mode: FormatMode, type: RawType, hook: RawHook, move: EditMove) {
  const short = mode === 'short'
  return [
    short
      ? 'Edit the opening of my vertical 9:16 video around this hook. If my take has a stronger version of the line, use my words, and keep my sentences whole.'
      : 'Edit the first 30 seconds of my horizontal 16:9 video around this hook. If my take has a stronger version of the line, use my words, and keep my sentences whole.',
    `Hook type — ${type.title}. ${type.why}`,
    `${short ? 'Spoken line, from the first frame' : 'Spoken opening, first 10 seconds'} — “${hook.say}” Start on me already talking, with no logo, title card or fade-in.`,
    short
      ? `On-screen text — “${hook.text}” One short line in the upper third from the first frame until about 2.5 seconds, clear of my face.`
      : `On-screen title — “${hook.text}” Bold, on the side of the frame away from my face, for the first 3–5 seconds.`,
    `First frame — ${firstPerson(hook.frame)}`,
    `Edit move — ${move.title}. ${move.prompt}`,
    `${short ? 'Next 3 seconds' : 'By 30 seconds'} — ${firstPerson(hook.next)}`,
    short
      ? 'Captions — Word by word, 2–4 words at a time, with the spoken word highlighted, kept above the app’s caption area.'
      : 'Subtitles — Short lines at the bottom of the frame, if I use them.',
    `Check — ${type.check} The numbers in this example are placeholders. Only use figures that appear in my footage or notes, and flag anything I still need to film.`,
  ].join('\n\n')
}

function build(mode: FormatMode, types: RawType[]) {
  return types.map(type => {
    const items: Technique[] = type.hooks.map((hook, index) => {
      const id = `th-${mode}-${type.id}-${String(index + 1).padStart(2, '0')}`
      const move = moveById.get(hook.move)
      if (!move) throw new Error(`Unknown edit move ${hook.move} in ${id}`)
      const hookPresets = hook.for as Preset[]
      const creator: CreatorHook = {
        say: hook.say,
        text: hook.text,
        frame: hook.frame,
        next: hook.next,
        presets: hookPresets,
        presetLabels: hookPresets.map(preset => presetLabel.get(preset) ?? preset),
        move,
        typeId: type.id,
        typeTitle: type.title,
        why: type.why,
        formula: type.formula,
        check: type.check,
      }
      return {
        id,
        mode,
        stage: 'hook',
        section: type.title,
        title: hook.say,
        previewId: `creator/${id}`,
        prompt: hookPrompt(mode, type, hook, move),
        creator,
        sound: move.id === 'sfx-layer',
      }
    })
    return { id: type.id, title: type.title, stage: 'hook', question: type.why, items } satisfies Collection
  })
}

export const creatorCollections: Record<FormatMode, Collection[]> = {
  short: build('short', shortTypes as RawType[]),
  long: build('long', longTypes as RawType[]),
}

export const hookTypes: Record<FormatMode, HookType[]> = {
  short: (shortTypes as RawType[]).map(({ hooks, ...type }) => ({ ...type, count: hooks.length })),
  long: (longTypes as RawType[]).map(({ hooks, ...type }) => ({ ...type, count: hooks.length })),
}

export const creatorHooks: Record<FormatMode, Technique[]> = {
  short: creatorCollections.short.flatMap(group => group.items),
  long: creatorCollections.long.flatMap(group => group.items),
}

export const moveTechniques: Technique[] = moves.map(move => ({
  id: moveTechniqueId(move.id),
  title: move.title,
  section: move.group,
  useCase: move.fixes,
  previewId: `moves/${move.id}`,
  prompt: [
    move.prompt,
    `How often — Reels and Shorts: ${move.often.short} Long form: ${move.often.long}`,
    `Avoid — ${move.avoid}`,
  ].join('\n'),
  move,
  sound: soundMoves.has(move.id),
}))

export function creatorHash(id: string): string | undefined {
  const match = /^th-(short|long)-/.exec(id)
  if (match) return `#${match[1] === 'short' ? 'reels-shorts' : 'long-form'}/hook/${id}`
}

type RawBeat = { role: string; title: string; t: number[]; goal: string; show: string; moves: string[]; line: string; render?: object }
type RawStructure = {
  id: string; title: string; bestFor: string; length: string; footage: string; example: string; for: string[]
  hookTypes: string[]; rhythm: string; every: number; checks: string[]; beats: RawBeat[]
}

export type StructureBeat = {
  role: string
  title: string
  start: number
  end: number
  goal: string
  show: string
  moves: EditMove[]
  line: string
  /** Where this beat starts in the rendered example, when the example includes it. */
  example?: number
}

export type Structure = {
  id: string
  mode: FormatMode
  title: string
  bestFor: string
  length: string
  footage: string
  example: string
  hookTypes: HookType[]
  rhythm: string
  every: number
  checks: string[]
  beats: StructureBeat[]
  total: number
  exampleTotal?: number
}

const timings: Record<string, { beats: Record<string, number>; total: number }> = structureTimings

export function formatTime(seconds: number, mode: FormatMode) {
  if (mode === 'short') return `${Number(seconds.toFixed(1))}`
  const whole = Math.round(seconds)
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, '0')}`
}

export const beatTime = (beat: { start: number; end: number }, mode: FormatMode) =>
  mode === 'short' ? `${formatTime(beat.start, mode)}–${formatTime(beat.end, mode)} s` : `${formatTime(beat.start, mode)}–${formatTime(beat.end, mode)}`

function structurePrompt(structure: Structure) {
  const short = structure.mode === 'short'
  return [
    `Edit my footage into a ${short ? 'vertical 9:16' : 'horizontal 16:9'} video, ${structure.length} long, using this structure: ${structure.title}. Use my own words and keep my sentences whole. The example lines show the shape of each beat, not a script to read.`,
    `Pacing — ${structure.rhythm}`,
    structure.beats.map((beat, index) => [
      `${index + 1}. ${beat.title} (${beatTime(beat, structure.mode)}) — ${firstPerson(beat.goal)}`,
      `On screen: ${firstPerson(beat.show)}`,
      beat.moves.length ? `Edit moves: ${beat.moves.map(move => move.title).join('; ')}.` : '',
    ].filter(Boolean).join(' ')).join('\n'),
    `Before export — ${structure.checks.join(' ')}`,
    'List any beat my footage can’t support, and the shots I’d need to film for it.',
  ].join('\n\n')
}

function buildStructures(mode: FormatMode): Technique[] {
  const types = new Map(hookTypes[mode].map(type => [type.id, type]))
  return ((structureData as Record<FormatMode, RawStructure[]>)[mode]).map(raw => {
    const timing = timings[`${mode}/${raw.id}`]
    const beats = raw.beats.map((beat, index) => ({
      role: beat.role,
      title: beat.title,
      start: beat.t[0],
      end: beat.t[1],
      goal: beat.goal,
      show: beat.show,
      line: beat.line,
      moves: beat.moves.map(id => {
        const move = moveById.get(id)
        if (!move) throw new Error(`Unknown edit move ${id} in structure ${raw.id}`)
        return move
      }),
      example: timing?.beats[String(index)],
    }))
    const structure: Structure = {
      id: raw.id,
      mode,
      title: raw.title,
      bestFor: raw.bestFor,
      length: raw.length,
      footage: raw.footage,
      example: raw.example,
      hookTypes: raw.hookTypes.map(id => {
        const type = types.get(id)
        if (!type) throw new Error(`Unknown hook type ${id} in structure ${raw.id}`)
        return type
      }),
      rhythm: raw.rhythm,
      every: raw.every,
      checks: raw.checks,
      beats,
      total: beats[beats.length - 1].end,
      exampleTotal: timing?.total,
    }
    return {
      id: `structure-${mode}-${raw.id}`,
      mode,
      title: raw.title,
      section: 'Structures',
      useCase: raw.bestFor,
      previewId: `structures/${raw.id}`,
      prompt: structurePrompt(structure),
      structure,
      sound: true,
    }
  })
}

export const structureTechniques: Record<FormatMode, Technique[]> = {
  short: buildStructures('short'),
  long: buildStructures('long'),
}

export function structureHash(id: string): string | undefined {
  const match = /^structure-(short|long)-(.+)$/.exec(id)
  if (match) return `#${match[1] === 'short' ? 'reels-shorts' : 'long-form'}/structure/${match[2]}`
}
