import catalog from './catalog.json'
import { shortHooks } from './format-content/short-hooks'
import { shortBody } from './format-content/short-body'
import { longForm } from './format-content/long-form'

export type FormatMode = 'short' | 'long'
export type Stage = 'hook' | 'intro' | 'body' | 'finish'
export type Technique = (typeof catalog)[number] & {
  previewId?: string
  useCase?: string
  mode?: FormatMode
}
type RecipeEntry = readonly [title: string, previewId: string, useCase: string, prompt: string]
type RecipeSource = {
  title: string
  entries: readonly RecipeEntry[]
  stage?: Stage
}
export type Collection = { id: string; title: string; stage: Stage; items: Technique[] }

export const modes = {
  short: { label: 'Reels/Shorts', format: 'Vertical · 9:16' },
  long: { label: 'Long Form', format: 'Widescreen · 16:9' },
} as const

export const stageLabels = {
  hook: 'Hooks',
  intro: 'Intros',
  body: 'Editing styles',
  finish: 'Finishes',
} as const

const slug = (value: string) => value.toLowerCase().normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

function createCollections(mode: FormatMode, records: readonly RecipeSource[]): Collection[] {
  return records.map(record => ({
    id: slug(record.title),
    title: record.title,
    stage: record.stage ?? 'hook',
    items: record.entries.map(([title, previewId, useCase, prompt]) => ({
      id: `${mode}-recipe-${slug(title)}`,
      title,
      previewId,
      useCase,
      prompt,
      section: record.title,
      mode,
    })),
  }))
}

export const formatCollections = {
  short: createCollections('short', [...shortHooks, ...shortBody]),
  long: createCollections('long', longForm),
}

export const techniques: Technique[] = catalog
const recipes = Object.values(formatCollections).flatMap(list => list.flatMap(group => group.items))
export const byId = new Map([...techniques, ...recipes].map(technique => [technique.id, technique]))

export const sections = [
  ['Hooks and typography', 'Hooks and typography'],
  ['Captions and framing', 'Captions and framing'],
  ['Assets and spatial graphics', 'Assets and overlays'],
  ['Explanations and screen recordings', 'Explanations'],
  ['Charts and infographics', 'Charts'],
  ['Maps and documentary graphics', 'Maps and documentary'],
  ['Cuts, pacing and transitions', 'Cuts and transitions'],
  ['Sound and music', 'Sound and music'],
  ['AI editing workflows', 'AI workflows'],
].map(([name, label]) => ({ name, label, count: techniques.filter(technique => technique.section === name).length }))

export function withSound(technique: Technique) {
  const id = technique.previewId ?? technique.id
  return byId.get(id)?.section === 'Sound and music' || id === 'beat-synced-cuts' || id === 'short-hyperedit'
}

export const mediaUrl = (id: string, extension: 'mp4' | 'webp') =>
  `${import.meta.env.BASE_URL}previews/${id}.${extension}`
