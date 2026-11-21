import { AlertTriangle, Check, ChevronDown, ChevronUp, Clipboard, FileUp, GripVertical, Layers3, X } from 'lucide-react'
import { useId, useRef, useState, type ChangeEvent, type Dispatch, type PointerEvent, type SetStateAction } from 'react'
import { byId } from './catalog'
import { formats, moveItem, platforms, removeItem, targets, type Edit, type Platform, type Target } from './edit'
import { compilePrompt } from './prompt'

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
  const [view, setView] = useState<'order' | 'video' | 'prompt'>('order')
  const [fileNote, setFileNote] = useState('')
  const [expandedCue, setExpandedCue] = useState<string | null>(null)
  const [custom, setCustom] = useState<{ base: string; text: string } | null>(null)
  const [dropTarget, setDropTarget] = useState<string | null>(null)
  const dragging = useRef<{ id: string; origin: number; target: string | null } | null>(null)
  const compiled = compilePrompt(edit)
  const generated = compiled.text
  const prompt = custom?.base === generated ? custom.text : generated
  const target = targets.find(option => option.id === edit.target) ?? targets[0]
  const update = <K extends keyof Edit>(key: K, value: Edit[K]) => setEdit(current => ({ ...current, [key]: value }))

  function loadTranscript(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    if (file.size > 400_000) {
      setFileNote('That file is too large. Paste the transcript text instead.')
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      const text = String(reader.result ?? '').slice(0, 60000)
      update('transcript', text)
      setFileNote(`Loaded ${file.name}. It stays in this browser.`)
    }
    reader.onerror = () => setFileNote('That file couldn’t be read. Paste the transcript text instead.')
    reader.readAsText(file)
  }
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
        <button type="button" aria-pressed={view === 'order'} onClick={() => setView('order')}>Order</button>
        <button type="button" aria-pressed={view === 'video'} onClick={() => setView('video')}>Your video</button>
        <button type="button" aria-pressed={view === 'prompt'} onClick={() => setView('prompt')}>Prompt</button>
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

          {hasMultipleHooks && <div className="edit-context">
            <label htmlFor={`${id}-hooks`}>How to use your hooks</label>
            <div className="select-wrap">
              <select id={`${id}-hooks`} value={edit.hookPlacement} onChange={event =>
                update('hookPlacement', event.target.value === 'separate' ? 'separate' : 'blend')}>
                <option value="blend">Combine into one opening</option>
                <option value="separate">Use at different moments</option>
              </select>
              <ChevronDown size={16} aria-hidden="true" />
            </div>
          </div>}
          {count > 0 && <button type="button" className="text-button next-step" onClick={() => setView('video')}>
            Next: tell it about your video
          </button>}
        </div>
      ) : view === 'video' ? (
        <div className="builder-body">
          <div className="edit-context">
            <p className="builder-hint">The more the AI knows, the less it guesses. Everything stays in this browser.</p>
            <label htmlFor={`${id}-topic`}>What it’s about</label>
            <input id={`${id}-topic`} type="text" maxLength={300} value={edit.topic}
              placeholder="e.g. Why your captions get covered" onChange={event => update('topic', event.target.value)} />
            <label htmlFor={`${id}-audience`}>Who it’s for <span>Optional</span></label>
            <input id={`${id}-audience`} type="text" maxLength={300} value={edit.audience}
              placeholder="e.g. New creators editing on their phone" onChange={event => update('audience', event.target.value)} />
            <label htmlFor={`${id}-platform`}>Platform</label>
            <div className="select-wrap">
              <select id={`${id}-platform`} value={edit.platform} onChange={event => update('platform', event.target.value as Platform)}>
                {platforms.map(option => <option key={option.id} value={option.id}>{option.label}</option>)}
              </select>
              <ChevronDown size={16} aria-hidden="true" />
            </div>
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
            <label htmlFor={`${id}-length`}>Target length <span>Optional</span></label>
            <input id={`${id}-length`} type="text" maxLength={60} value={edit.length}
              placeholder="e.g. 35 seconds" onChange={event => update('length', event.target.value)} />
            <label htmlFor={`${id}-transcript`}>Transcript <span>Best with timestamps</span></label>
            <textarea id={`${id}-transcript`} rows={6} maxLength={60000} value={edit.transcript} spellCheck={false}
              placeholder={'Paste your transcript or .srt here.\n00:00 If your captions sit at the bottom…'}
              onChange={event => update('transcript', event.target.value)} />
            <div className="file-row">
              <label className="file-button">
                <FileUp size={15} aria-hidden="true" /> Load .srt, .vtt or .txt
                <input type="file" accept=".srt,.vtt,.txt,text/plain" onChange={loadTranscript} />
              </label>
              {edit.transcript && <button type="button" className="text-button" onClick={() => { update('transcript', ''); setFileNote('') }}>Clear</button>}
            </div>
            {fileNote && <p className="builder-hint" role="status">{fileNote}</p>}
            <label htmlFor={`${id}-clips`}>Clips and B-roll you have <span>One per line</span></label>
            <textarea id={`${id}-clips`} rows={3} maxLength={3000} value={edit.clips}
              placeholder={'main-take.mp4\nscreen-recording.mov\nlatte-closeup.mp4'} onChange={event => update('clips', event.target.value)} />
            <label htmlFor={`${id}-footage`}>Anything else <span>Optional</span></label>
            <textarea id={`${id}-footage`} rows={3} maxLength={1400} value={edit.footage}
              placeholder="e.g. Keep my intro joke. Brand colour is #0B5FFF."
              onChange={event => update('footage', event.target.value)} />
          </div>
          <button type="button" className="text-button next-step" onClick={() => setView('prompt')}>Next: get the prompt</button>
        </div>
      ) : (
        <div className="builder-body prompt-body">
          {count === 0 ? (
            <div className="builder-empty"><Clipboard size={21} strokeWidth={1.5} /><p>Add a technique to generate the combined prompt.</p></div>
          ) : (
            <>
              <label htmlFor={`${id}-target`}>Where will you paste it?</label>
              <div className="select-wrap">
                <select id={`${id}-target`} value={edit.target} onChange={event => update('target', event.target.value as Target)}>
                  {targets.map(option => <option key={option.id} value={option.id}>{option.label}</option>)}
                </select>
                <ChevronDown size={16} aria-hidden="true" />
              </div>
              <p className="builder-hint">{target.hint}</p>
              <div className="detail-switch" role="group" aria-label="Prompt length">
                <button type="button" aria-pressed={edit.detail === 'full'} onClick={() => update('detail', 'full')}>Full</button>
                <button type="button" aria-pressed={edit.detail === 'short'} onClick={() => update('detail', 'short')}>Short</button>
              </div>
              {compiled.warnings.length > 0 && <ul className="prompt-warnings">
                {compiled.warnings.map(warning => <li key={warning}><AlertTriangle size={14} aria-hidden="true" /> {warning}</li>)}
              </ul>}
              <label htmlFor={`${id}-prompt`}>Edit your prompt <span>{compiled.words.toLocaleString('en-US')} words{edit.transcript.trim() ? ' + transcript' : ''}</span></label>
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
