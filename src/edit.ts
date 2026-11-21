import { byId } from './catalog'

export type EditItem = { id: string; cue: string }
export type HookPlacement = 'blend' | 'separate'
export type Target = 'plan' | 'script' | 'capcut' | 'premiere' | 'descript' | 'agent'
export type Detail = 'full' | 'short'
export type Platform = '' | 'instagram' | 'tiktok' | 'shorts' | 'youtube'
export type Edit = {
  items: EditItem[]
  format: string
  automaticFormat: boolean
  /** Free notes about the footage and goal. */
  footage: string
  hookPlacement: HookPlacement
  topic: string
  audience: string
  platform: Platform
  length: string
  transcript: string
  clips: string
  target: Target
  detail: Detail
}
const storageKey = 'video-edit-lab:edit:v1'
const newEdit: Edit = {
  items: [], format: '', automaticFormat: true, footage: '', hookPlacement: 'blend',
  topic: '', audience: '', platform: '', length: '', transcript: '', clips: '', target: 'plan', detail: 'full',
}

export const formats = ['Vertical · 9:16', 'Widescreen · 16:9', 'Square · 1:1']

export const targets: readonly { id: Target; label: string; hint: string }[] = [
  { id: 'plan', label: 'Claude or ChatGPT: plan the edit', hint: 'Returns a timed edit plan you can follow in any editor.' },
  { id: 'script', label: 'Claude or ChatGPT: write the script first', hint: 'For before you film: hook options, the script and a shot list.' },
  { id: 'capcut', label: 'CapCut, step by step', hint: 'Returns cuts, captions, text, zooms and sound as CapCut steps.' },
  { id: 'premiere', label: 'Premiere Pro or DaVinci Resolve', hint: 'Returns a marker list, a cut list and every effect with its timecode.' },
  { id: 'descript', label: 'Descript', hint: 'Returns transcript edits, scenes, captions and media to add.' },
  { id: 'agent', label: 'An AI agent that edits with code', hint: 'Returns one JSON timeline that ffmpeg, Remotion or MoviePy can render.' },
]

export const platforms: readonly { id: Platform; label: string }[] = [
  { id: '', label: 'Not sure yet' },
  { id: 'instagram', label: 'Instagram Reels' },
  { id: 'tiktok', label: 'TikTok' },
  { id: 'shorts', label: 'YouTube Shorts' },
  { id: 'youtube', label: 'YouTube video' },
]

const text = (value: unknown, max: number) => typeof value === 'string' ? value.slice(0, max) : ''

export function readEdit(): Edit {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) ?? 'null')
    if (!saved || !Array.isArray(saved.items)) return newEdit
    const ids = new Set<string>()
    const items: EditItem[] = []
    for (const item of saved.items) {
      if (!item || !byId.has(item.id) || ids.has(item.id)) continue
      ids.add(item.id)
      items.push({ id: item.id, cue: typeof item.cue === 'string' ? item.cue : '' })
    }
    const format = formats.includes(saved.format) ? saved.format : ''
    return {
      items,
      format,
      automaticFormat: typeof saved.automaticFormat === 'boolean' ? saved.automaticFormat : !format,
      footage: text(saved.footage, 1400),
      hookPlacement: saved.hookPlacement === 'separate' ? 'separate' : 'blend',
      topic: text(saved.topic, 300),
      audience: text(saved.audience, 300),
      platform: platforms.some(option => option.id === saved.platform) ? saved.platform : '',
      length: text(saved.length, 60),
      transcript: text(saved.transcript, 60000),
      clips: text(saved.clips, 3000),
      target: targets.some(option => option.id === saved.target) ? saved.target : 'plan',
      detail: saved.detail === 'short' ? 'short' : 'full',
    }
  } catch {
    return newEdit
  }
}

export function addItems(edit: Edit, items: EditItem[], defaultFormat: string): Edit {
  const added = items.filter(item => !edit.items.some(existing => existing.id === item.id))
  if (!added.length) return edit
  return {
    ...edit,
    items: [...edit.items, ...added],
    format: !edit.items.length && edit.automaticFormat ? defaultFormat : edit.format,
  }
}

export function removeItem(edit: Edit, id: string): Edit {
  const items = edit.items.filter(item => item.id !== id)
  return { ...edit, items, format: !items.length && edit.automaticFormat ? '' : edit.format }
}

export function saveEdit(edit: Edit) {
  try {
    localStorage.setItem(storageKey, JSON.stringify(edit))
  } catch {
    // The current edit remains usable in memory if storage is disabled.
  }
}

export function moveItem(items: EditItem[], from: number, to: number) {
  if (from === to || from < 0 || to < 0 || from >= items.length || to >= items.length) return items
  const reordered = [...items]
  const [item] = reordered.splice(from, 1)
  reordered.splice(to, 0, item)
  return reordered
}

export async function writeClipboard(text: string) {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text)
      return
    } catch {
      // Embedded browsers may expose the API while blocking writes.
    }
  }
  const active = document.activeElement
  const field = document.createElement('textarea')
  field.value = text
  field.setAttribute('readonly', '')
  field.style.cssText = 'position:fixed;inset:0;opacity:0;pointer-events:none;'
  ;(document.querySelector('dialog[open]') ?? document.body).appendChild(field)
  field.select()
  try {
    if (!document.execCommand('copy')) throw new Error('Clipboard unavailable')
  } finally {
    field.remove()
    if (active instanceof HTMLElement) active.focus({ preventScroll: true })
  }
}
