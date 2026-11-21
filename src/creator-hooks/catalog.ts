import shortTypes from './short.json'
import longTypes from './long.json'
import moveList from './moves.json'
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
    .replace(/\b(behind|with|message|told|held|for|beside|affected|to)\s+you\b/gi, '$1 me')
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
