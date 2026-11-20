import { byId } from './catalog'

export type EditItem = { id: string; cue: string }
export type Edit = { items: EditItem[]; format: string; automaticFormat: boolean; footage: string }
const storageKey = 'video-edit-lab:edit:v1'
const newEdit: Edit = { items: [], format: '', automaticFormat: true, footage: '' }

export const formats = ['Vertical · 9:16', 'Widescreen · 16:9', 'Square · 1:1']

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
      footage: typeof saved.footage === 'string' ? saved.footage : '',
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

export function composePrompt(edit: Edit) {
  if (edit.items.length === 0) return ''
  const context = [
    edit.format && `Format: ${edit.format}`,
    edit.footage.trim() && `Footage and goal: ${edit.footage.trim()}`,
  ].filter(Boolean)
  const steps = edit.items.map((item, index) => {
    const technique = byId.get(item.id)!
    const cue = item.cue.trim()
    return `${index + 1}. ${technique.title}${cue ? `\nTiming: ${cue}` : ''}\n${technique.prompt}`
  })
  return [
    'Edit my footage using this brief.',
    ...context,
    'Follow the techniques in the order below. Apply any whole-video rules throughout. Use the supplied assets and flag any missing footage, data, or timing details before rendering.',
    steps.join('\n\n'),
    'Keep the spoken message clear. Preview the edit and flag any technique that conflicts with another at the same moment.',
  ].join('\n\n')
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
