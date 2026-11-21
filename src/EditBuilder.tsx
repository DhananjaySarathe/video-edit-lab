import { Check, ChevronDown, ChevronUp, Clipboard, GripVertical, Layers3, X } from 'lucide-react'
import { useId, useRef, useState, type Dispatch, type PointerEvent, type SetStateAction } from 'react'
import { byId } from './catalog'
import { composePrompt, formats, moveItem, removeItem, type Edit } from './edit'

type BuilderProps = {
  edit: Edit
  setEdit: Dispatch<SetStateAction<Edit>>
  copied: boolean
  onCopy: (text: string) => void
  headingId?: string
  onClose?: () => void
}

export function EditBuilder({ edit, setEdit, copied, onCopy, headingId, onClose }: BuilderProps) {
  const id = useId()
  const [view, setView] = useState<'order' | 'prompt'>('order')
  const [expandedCue, setExpandedCue] = useState<string | null>(null)
  const [custom, setCustom] = useState<{ base: string; text: string } | null>(null)
  const [dropTarget, setDropTarget] = useState<string | null>(null)
  const dragging = useRef<{ id: string; origin: number; target: string | null } | null>(null)
  const generated = composePrompt(edit)
  const prompt = custom?.base === generated ? custom.text : generated
  const count = edit.items.length
  const hasMultipleHooks = edit.items.filter(item => byId.get(item.id)?.stage === 'hook').length > 1
  const selectedLabel = count === 1 ? '1 technique' : `${count} techniques`

  function move(from: number, to: number) {
    setEdit(current => ({ ...current, items: moveItem(current.items, from, to) }))
  }

  function moveTo(source: string, target: string) {
    setEdit(current => {
      const from = current.items.findIndex(item => item.id === source)
      const to = current.items.findIndex(item => item.id === target)
      return { ...current, items: moveItem(current.items, from, to) }
    })
  }

  function trackDrag(event: PointerEvent<HTMLSpanElement>) {
    const drag = dragging.current
    if (!drag || Math.abs(event.clientY - drag.origin) < 4 && !drag.target) return
    const row = document.elementFromPoint(event.clientX, event.clientY)?.closest<HTMLElement>('li[data-edit-id]')
    const order = event.currentTarget.closest('.edit-order')
    const target = row && order?.contains(row) ? row.dataset.editId ?? null : null
    drag.target = target === drag.id ? null : target
    setDropTarget(drag.target)
  }

  function endDrag(commit: boolean) {
    const drag = dragging.current
    dragging.current = null
    setDropTarget(null)
    if (commit && drag?.target) moveTo(drag.id, drag.target)
  }

  return (
    <div className="builder-panel">
      <div className="builder-heading">
        <div>
          <h2 id={headingId}>Your edit</h2>
          <p>{selectedLabel} selected</p>
        </div>
        {onClose && <button type="button" className="icon-button" aria-label="Close your edit" onClick={onClose}><X size={20} /></button>}
      </div>

      <div className="builder-tabs" role="group" aria-label="Edit builder view">
        <button type="button" aria-pressed={view === 'order'} onClick={() => setView('order')}>Edit order</button>
        <button type="button" aria-pressed={view === 'prompt'} onClick={() => setView('prompt')}>Combined prompt</button>
      </div>

      {view === 'order' ? (
        <div className="builder-body">
          {count === 0 ? (
            <div className="builder-empty">
              <Layers3 size={22} strokeWidth={1.5} />
              <p>Add a technique to start your edit.</p>
            </div>
          ) : (
            <ol className="edit-order" aria-label="Selected technique order">
              {edit.items.map((item, index) => {
                const technique = byId.get(item.id)!
                const cueOpen = expandedCue === item.id
                return (
                  <li className={dropTarget === item.id ? 'drop-target' : ''} key={item.id} data-edit-id={item.id}>
                    <div className="order-row">
                      <span className="order-grip" aria-hidden="true" title="Drag to reorder"
                        onPointerDown={event => {
                          if (event.button !== 0) return
                          event.currentTarget.setPointerCapture(event.pointerId)
                          dragging.current = { id: item.id, origin: event.clientY, target: null }
                        }}
                        onPointerMove={trackDrag} onPointerUp={event => {
                          trackDrag(event)
                          endDrag(true)
                        }}
                        onPointerCancel={() => endDrag(false)}><GripVertical size={16} /></span>
                      <span className="order-index" aria-hidden="true">{index + 1}</span>
                      <div className="order-label">
                        <strong>{technique.title}</strong>
                        <button type="button" className="cue-link" aria-expanded={cueOpen}
                          onClick={() => setExpandedCue(cueOpen ? null : item.id)}
                          aria-label={`Set timing cue for ${technique.title}`}>
                          {item.cue || 'Set timing cue'}
                        </button>
                      </div>
                      <div className="order-controls">
                        <button type="button" className="icon-button" disabled={index === 0}
                          aria-label={`Move ${technique.title} up`} title="Move up" onClick={() => move(index, index - 1)}><ChevronUp size={16} /></button>
                        <button type="button" className="icon-button" disabled={index === count - 1}
                          aria-label={`Move ${technique.title} down`} title="Move down" onClick={() => move(index, index + 1)}><ChevronDown size={16} /></button>
                        <button type="button" className="icon-button" aria-label={`Remove ${technique.title} from order`}
                          title="Remove" onClick={() => setEdit(current => removeItem(current, item.id))}><X size={15} /></button>
                      </div>
                    </div>
                    {cueOpen && <input type="text" autoFocus maxLength={180} value={item.cue}
                      aria-label={`Timing for ${technique.title}`} placeholder="e.g. When I show the result"
                      onChange={event => {
                        const cue = event.target.value
                        setEdit(current => ({ ...current, items: current.items.map(entry => entry.id === item.id ? { ...entry, cue } : entry) }))
                      }} />}
                  </li>
                )
              })}
            </ol>
          )}

          <div className="edit-context">
            {hasMultipleHooks && <>
              <label htmlFor={`${id}-hooks`}>How to use your hooks</label>
              <div className="select-wrap">
                <select id={`${id}-hooks`} value={edit.hookPlacement} onChange={event => {
                  const hookPlacement = event.target.value === 'separate' ? 'separate' : 'blend'
                  setEdit(current => ({ ...current, hookPlacement }))
                }}>
                  <option value="blend">Combine into one opening</option>
                  <option value="separate">Use at different moments</option>
                </select>
                <ChevronDown size={16} aria-hidden="true" />
              </div>
            </>}
            <label htmlFor={`${id}-format`}>Video format</label>
            <div className="select-wrap">
              <select id={`${id}-format`} value={edit.format} onChange={event => {
                const format = event.target.value
                setEdit(current => ({ ...current, format, automaticFormat: false }))
              }}>
                <option value="">Any format</option>
                {formats.map(format => <option key={format}>{format}</option>)}
              </select>
              <ChevronDown size={16} aria-hidden="true" />
            </div>
            <label htmlFor={`${id}-footage`}>Footage and goal <span>Optional</span></label>
            <textarea id={`${id}-footage`} rows={3} maxLength={1400} value={edit.footage}
              placeholder="e.g. A talking-head Reel explaining a chart"
              onChange={event => {
                const footage = event.target.value
                setEdit(current => ({ ...current, footage }))
              }} />
          </div>
        </div>
      ) : (
        <div className="builder-body prompt-body">
          {count === 0 ? (
            <div className="builder-empty"><Clipboard size={21} strokeWidth={1.5} /><p>Add a technique to generate the combined prompt.</p></div>
          ) : (
            <>
              <label htmlFor={`${id}-prompt`}>Edit your prompt</label>
              <textarea rows={11} id={`${id}-prompt`} value={prompt}
                onChange={event => setCustom({ base: generated, text: event.target.value })} spellCheck={false} />
              {custom?.base === generated && <button className="text-button" type="button" onClick={() => setCustom(null)}>Reset to generated prompt</button>}
            </>
          )}
        </div>
      )}
      <div className="builder-footer">
        <button type="button" className="button primary" onClick={() => onCopy(prompt)} disabled={!prompt.trim()}>
          {copied ? <Check size={17} /> : <Clipboard size={17} />}
          {copied ? 'Copied to clipboard' : 'Copy combined prompt'}
        </button>
      </div>
    </div>
  )
}
