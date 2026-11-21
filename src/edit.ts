import { byId, type Technique } from './catalog'

export type EditItem = { id: string; cue: string }
export type HookPlacement = 'blend' | 'separate'
export type Edit = { items: EditItem[]; format: string; automaticFormat: boolean; footage: string; hookPlacement: HookPlacement }
const storageKey = 'video-edit-lab:edit:v1'
const newEdit: Edit = { items: [], format: '', automaticFormat: true, footage: '', hookPlacement: 'blend' }

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
      hookPlacement: saved.hookPlacement === 'separate' ? 'separate' : 'blend',
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

function hookBrief(technique: Technique, accent: boolean) {
  const plan = technique.breakdown
  if (!plan?.opener) return accent
    ? `Use the following direction as a reference for a single accent inside the lead hook. Keep the lead hook's timing and action.\n${technique.prompt}`
    : technique.prompt
  if (accent) {
    return [
      `Borrow the turn from “${technique.title}” for the lead opening. ${plan.beats[1][1]}`,
      `Use this detail only where my footage supports it. Check the result. ${plan.check}`,
    ].join('\n')
  }
  return [
    `Adapt this sample to my footage. A possible first line is “${plan.opener}”`,
    ...plan.beats.map(([time, direction]) => `${time} — ${direction}`),
    plan.soundDirection && `Sound — ${plan.soundDirection}`,
    `Check — ${plan.check}`,
  ].filter(Boolean).join('\n')
}

export function composePrompt(edit: Edit) {
  if (edit.items.length === 0) return ''
  const hooks = edit.items.filter(item => byId.get(item.id)?.stage === 'hook')
  const multiple = hooks.length > 1
  const blend = edit.hookPlacement !== 'separate'
  const context = [
    edit.format && `Deliver in ${edit.format}. Keep this canvas throughout and reframe borrowed techniques for it.`,
    edit.footage.trim() && `My footage and goal — ${edit.footage.trim()}`,
    multiple && (blend
      ? 'Build one opening around the first selected hook. Fit the other hook ideas into its existing shots. Give any hook with its own timing cue that separate moment.'
      : 'Use the first hook to open. Place each later hook at its timing cue or the next change of subject. Count its shot times from that point in the edit.'),
  ].filter(Boolean)
  const steps = edit.items.map((item, index) => {
    const technique = byId.get(item.id)!
    const cue = item.cue.trim()
    const hook = technique.stage === 'hook'
    const accent = hook && multiple && blend && hooks[0].id !== item.id && !cue
    const position = hook && multiple ? (accent ? 'Opening accent' : hooks[0].id === item.id ? 'Lead hook' : 'Later hook') : ''
    return `${index + 1}. ${technique.title}${position ? ` · ${position}` : ''}${cue ? `\nTiming — ${cue}` : ''}\n${hook ? hookBrief(technique, accent) : technique.prompt}`
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
