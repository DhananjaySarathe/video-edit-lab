import profiles from './types.json'
import workedIndex from './worked-examples.json'
import guidance from './guidance.json'
import shotTimes from './shot-times.json'
import type { Breakdown } from '../breakdown'
import type { Collection, FormatMode, Technique } from '../catalog'

const files = import.meta.glob<string>('./seeds/*/*.txt', {
  query: '?raw',
  import: 'default',
  eager: true,
})

type HookType = {
  id: string
  title: string
  question: string
  time: readonly number[]
  picture: readonly string[]
  audio: string
}

const worked = new Map<string, { sound: boolean }>(Object.entries(workedIndex))
const timings: Readonly<Record<string, number[][]>> = shotTimes
export const hookGuidance: Readonly<Record<string, { footage: string; check: string }>> = guidance

export const footageGroups = [
  { title: 'People and conversations', keys: ['presenter', 'portrait', 'roles', 'interview'] },
  { title: 'Hands, objects and processes', keys: ['hands', 'object', 'process', 'coffee', 'result'] },
  { title: 'Screens and devices', keys: ['screen', 'phone', 'desk'] },
  { title: 'Maps, charts and documents', keys: ['map', 'chart', 'document', 'archive'] },
  { title: 'Places and movement', keys: ['room', 'street', 'steps'] },
  { title: 'Comparisons and timed tests', keys: ['compare', 'timer'] },
]
const footageByKey = new Map(footageGroups.flatMap(group => group.keys.map(key => [key, group.title] as const)))

function samples(mode: FormatMode, type: HookType, text: string): Technique[] {
  return text.trim().split(/\r?\n/).filter(Boolean).map((line, index) => {
    const [title, footage, opener, first, turn, bridge, check] = line.split('|').map(field => field.trim())
    const id = `hook-${mode}-${type.id}-${String(index + 1).padStart(3, '0')}`
    const format = mode === 'short' ? 'vertical 9:16' : 'horizontal 16:9'
    const previewId = `hooks/${id}`
    const example = worked.get(id)
    const authoredTimes = timings[`${mode}/${type.id}`]?.[index]
    const time = authoredTimes ? [0, ...authoredTimes] : type.time
    const beats = [first, turn, bridge].map((shot, i) => [
      `${time[i]}–${time[i + 1]} s`,
      `${shot} ${type.picture[i]}`,
    ] as const)
    const prompt = [
      `Edit my footage for a ${format} opening. Give the viewer one question to follow. “${type.question}”`,
      `Use “${title}” as a model. Match the subject, action and evidence to what I actually filmed. A possible opening line is “${opener}” Adapt it to my material.`,
      ...beats.map(([time, shot]) => `${time} — ${shot}`),
      `Sound and pacing — ${type.audio}`,
      `Review — ${check} Use the footage, words and measurements I supply. Flag any missing source before building the cut.`,
    ].join('\n\n')
    const breakdown: Breakdown = {
      id,
      mode,
      stage: 'hook',
      title,
      previewId,
      previewKind: example ? 'worked' : 'storyboard',
      duration: time[time.length - 1],
      sound: example?.sound,
      soundDirection: type.audio,
      footageGroup: footageByKey.get(footage),
      useCase: first,
      opener,
      beats,
      check,
      prompt,
    }
    return {
      id, mode, title, previewId, prompt, breakdown, stage: 'hook',
      section: type.title,
      useCase: first,
    }
  })
}

function groups(mode: FormatMode): Collection[] {
  return profiles[mode].flatMap(type => {
    const seed = files[`./seeds/${mode}/${type.id}.txt`]
    if (!seed?.trim()) return []
    const items = samples(mode, type, seed)
    items.sort((left, right) => Number(right.breakdown?.previewKind === 'worked') - Number(left.breakdown?.previewKind === 'worked'))
    return [{ id: type.id, title: type.title, stage: 'hook', question: type.question, items }]
  })
}

export const hookCollections = { short: groups('short'), long: groups('long') }

export function hookHash(id: string): string | undefined {
  const match = /^hook-(short|long)-(.+)-(\d{3})$/.exec(id)
  if (match) return `#${match[1] === 'short' ? 'reels-shorts' : 'long-form'}/${match[2]}/${match[3]}`
}

function interleave(collections: Collection[]) {
  const count = Math.max(0, ...collections.map(group => group.items.length))
  return Array.from({ length: count }, (_, index) =>
    collections.flatMap(group => group.items[index] ? [group.items[index]] : [])
  ).flat()
}

export const hookExamples = {
  short: interleave(hookCollections.short),
  long: interleave(hookCollections.long),
}
