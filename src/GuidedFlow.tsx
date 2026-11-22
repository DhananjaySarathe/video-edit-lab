import { ArrowLeft, ArrowRight, Check, Clipboard, Film, ListOrdered, Pin, Smartphone, X } from 'lucide-react'
import { useEffect, useMemo, useRef, useState, type RefObject } from 'react'
import { modes, type FormatMode } from './catalog'
import { creatorCollections, hookTypes, structureTechniques } from './creator-hooks/catalog'
import { targets, type Detail, type Edit, type Target } from './edit'
import { suggestOpeners, type OpenerSuggestion } from './openers'
import { compilePrompt } from './prompt'

type Props = {
  dialogRef: RefObject<HTMLDialogElement>
  initialMode: FormatMode
  current: Edit
  copied: boolean
  /** Write the finished edit into the builder (and switch format if needed). */
  onApply: (edit: Edit, mode: FormatMode) => void
  onCopy: (text: string) => void
  onOpenBuilder: () => void
}

const STEPS = ['What you’re making', 'Your take', 'The hook', 'Get the prompt'] as const

export function GuidedFlow({ dialogRef, initialMode, current, copied, onApply, onCopy, onOpenBuilder }: Props) {
  const [step, setStep] = useState(0)
  const [mode, setMode] = useState<FormatMode>(initialMode)
  const [structureId, setStructureId] = useState('')
  const [topic, setTopic] = useState(current.topic)
  const [transcript, setTranscript] = useState(current.transcript)
  const [opener, setOpener] = useState<OpenerSuggestion | null>(null)
  const [hookId, setHookId] = useState('')
  const [target, setTarget] = useState<Target>(current.target)
  const [detail, setDetail] = useState<Detail>(current.detail)
  const [copiedOnce, setCopiedOnce] = useState(false)
  const [fromTake, setFromTake] = useState(false)
  const body = useRef<HTMLDivElement>(null)

  // Each step starts at its top, not wherever the last one was scrolled to.
  useEffect(() => { body.current?.scrollTo(0, 0) }, [step, mode])

  const structures = structureTechniques[mode]
  const structure = structures.find(item => item.id === structureId)?.structure
  const suggestions = useMemo(() => suggestOpeners(transcript, mode), [transcript, mode])
  const hookGroups = (structure?.hookTypes ?? []).map(type => ({
    type,
    hooks: creatorCollections[mode].find(group => group.id === type.id)?.items.slice(0, 2) ?? [],
  }))
  const typeTitle = (id: string) => hookTypes[mode].find(type => type.id === id)?.title ?? ''

  const format = mode === 'short' ? 'Vertical · 9:16' : 'Widescreen · 16:9'
  const draft: Edit = {
    ...current,
    items: [structureId, hookId].filter(Boolean).map(id => ({ id, cue: '' })),
    format,
    automaticFormat: false,
    // A length set for the other format (say 10 minutes, carried into a Reel) would fight the structure.
    length: current.format === format ? current.length : '',
    topic,
    transcript,
    opener: opener ? { text: opener.text, stamp: opener.stamp } : null,
    target,
    detail,
    platform: mode === 'long' ? (current.platform === 'youtube' ? 'youtube' : '') : current.platform === 'youtube' ? '' : current.platform,
  }
  const compiled = step === 3 ? compilePrompt(draft) : null

  function close() {
    dialogRef.current?.close()
  }

  function chooseMode(next: FormatMode) {
    if (next === mode) return
    setMode(next)
    setStructureId('')
    setHookId('')
    setOpener(null)
  }

  function finish(action: 'copy' | 'builder') {
    onApply(draft, mode)
    if (action === 'copy' && compiled?.text) {
      onCopy(compiled.text)
      setCopiedOnce(true)
    }
    if (action === 'builder') {
      close()
      onOpenBuilder()
    }
  }

  /** Same take, same transcript: start over as a Reel/Short. */
  function reelFromTake() {
    chooseMode('short')
    setFromTake(true)
    setCopiedOnce(false)
    setStep(0)
  }

  return (
    <dialog ref={dialogRef} className="guided-dialog" aria-labelledby="guided-title"
      onClick={event => { if (event.target === event.currentTarget) close() }}>
      <div className="guided-panel">
        <div className="guided-head">
          <div>
            <p className="guided-kicker">Step {step + 1} of {STEPS.length}</p>
            <h2 id="guided-title">{STEPS[step]}</h2>
          </div>
          <button type="button" className="icon-button" aria-label="Close" onClick={close}><X size={20} /></button>
        </div>
        <ol className="guided-steps" aria-label="Steps">
          {STEPS.map((name, index) => (
            <li key={name} className={index === step ? 'is-current' : index < step ? 'is-done' : ''}>
              <button type="button" disabled={index > 0 && !structureId} onClick={() => setStep(index)}
                aria-current={index === step ? 'step' : undefined}>
                <span>{index < step ? <Check size={12} /> : index + 1}</span> {name}
              </button>
            </li>
          ))}
        </ol>

        <div className="guided-body" ref={body}>
          {step === 0 && <>
            <div className="guided-format" role="group" aria-label="Format">
              <button type="button" aria-pressed={mode === 'short'} onClick={() => chooseMode('short')}>
                <Smartphone size={16} aria-hidden="true" /> {modes.short.label}
              </button>
              <button type="button" aria-pressed={mode === 'long'} onClick={() => chooseMode('long')}>
                <Film size={16} aria-hidden="true" /> {modes.long.label}
              </button>
            </div>
            <p className="guided-hint">{fromTake && mode === 'short'
              ? 'Your topic and transcript carry over. For one moment from the longer take, try Podcast or interview clip or Talking-head tip.'
              : 'Pick the kind of video. Each one comes with a beat-by-beat plan.'}</p>
            <div className="guided-choices">
              {structures.map(item => (
                <button type="button" key={item.id} className="guided-choice" aria-pressed={structureId === item.id}
                  onClick={() => { setStructureId(item.id); setHookId('') }}>
                  <strong>{item.title} <span>{item.structure!.length}</span></strong>
                  <span>{item.structure!.bestFor}</span>
                </button>
              ))}
            </div>
          </>}

          {step === 1 && <div className="guided-fields">
            <label htmlFor="guided-topic">What it’s about</label>
            <input id="guided-topic" type="text" maxLength={300} value={topic} placeholder="e.g. Why your captions get covered"
              onChange={event => setTopic(event.target.value)} />
            <label htmlFor="guided-transcript">Transcript <span>Optional, but it makes the plan exact</span></label>
            <textarea id="guided-transcript" rows={6} maxLength={60000} value={transcript} spellCheck={false}
              placeholder={'Paste your transcript or .srt. No take yet? Skip this and get a script prompt instead.'}
              onChange={event => { setTranscript(event.target.value); setOpener(null) }} />
            {transcript.trim() && <div className="openers">
              <p className="openers-title">Strongest opening lines in your take</p>
              {suggestions.length === 0 && <p className="guided-hint">No strong opening line yet. Lines with a number, a result,
                a test or a habit the viewer has work best.</p>}
              {suggestions.map(item => {
                const pinned = opener?.text === item.text
                return (
                  <div key={`${item.stamp}-${item.text}`} className={`opener-card${pinned ? ' is-pinned' : ''}`}>
                    <p className="opener-line">“{item.text}” {item.stamp && <span>{item.stamp}</span>}</p>
                    <p className="opener-type">{typeTitle(item.typeId)}</p>
                    <p className="opener-why">{item.reasons.join(' · ')}</p>
                    <div className="opener-actions">
                      <button type="button" className={`button ${pinned ? 'added' : 'tinted'}`} aria-pressed={pinned}
                        onClick={() => setOpener(pinned ? null : item)}>
                        {pinned ? <Check size={15} /> : <Pin size={15} />} {pinned ? 'Opening on this' : 'Open on this'}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>}
          </div>}

          {step === 2 && <>
            <p className="guided-hint">{opener
              ? `You’re opening on your own line. A hook card adds the on-screen text, first frame and edit move around it.`
              : 'These hook types fit this structure. Pick one example as a model, or skip and let the AI find the opening in your take.'}</p>
            <div className="guided-hooks">
              {hookGroups.map(({ type, hooks }) => (
                <div key={type.id} className="guided-hook-group">
                  <p className="guided-hook-type">{type.title}{opener?.typeId === type.id && <span>Fits your line</span>}</p>
                  {hooks.map(hook => (
                    <button type="button" key={hook.id} className="guided-choice" aria-pressed={hookId === hook.id}
                      onClick={() => setHookId(hookId === hook.id ? '' : hook.id)}>
                      <strong className="guided-line">“{hook.creator!.say}”</strong>
                      <span className="layer-text">{hook.creator!.text}</span>
                    </button>
                  ))}
                </div>
              ))}
              <button type="button" className="guided-choice guided-skip" aria-pressed={!hookId} onClick={() => setHookId('')}>
                <strong>{opener ? 'No hook card, just my line' : 'Skip: let the AI pick from my take'}</strong>
              </button>
            </div>
          </>}

          {step === 3 && compiled && <>
            <p className="guided-hint">Where will you paste it?</p>
            <div className="guided-targets" role="radiogroup" aria-label="Where you’ll paste the prompt">
              {targets.map(option => (
                <button type="button" key={option.id} role="radio" aria-checked={target === option.id}
                  className="guided-target" onClick={() => setTarget(option.id)}>
                  <strong>{option.label}</strong>
                  <span>{option.hint}</span>
                </button>
              ))}
            </div>
            <div className="detail-switch" role="group" aria-label="Prompt length">
              <button type="button" aria-pressed={detail === 'full'} onClick={() => setDetail('full')}>Full</button>
              <button type="button" aria-pressed={detail === 'short'} onClick={() => setDetail('short')}>Short</button>
            </div>
            {compiled.warnings.length > 0 && <ul className="prompt-warnings">
              {compiled.warnings.map(warning => <li key={warning}>{warning}</li>)}
            </ul>}
            <label className="guided-preview-label" htmlFor="guided-preview">Your prompt <span>{compiled.words.toLocaleString('en-US')} words
              {transcript.trim() ? ' + transcript' : ''}</span></label>
            <textarea id="guided-preview" className="guided-preview" readOnly rows={8} value={compiled.text} />
            {copiedOnce && mode === 'long' && transcript.trim() ? (
              <div className="guided-next">
                <p><strong>Copied.</strong> Want a Reel from the same take? Your transcript carries over and the site finds the strongest lines for a short.</p>
                <button type="button" className="button tinted" onClick={reelFromTake}>
                  <Smartphone size={16} /> Make a Reel from this take
                </button>
              </div>
            ) : !copiedOnce && current.items.length > 0 && <p className="guided-hint">Finishing replaces the {current.items.length} {current.items.length === 1
              ? 'item' : 'items'} in Your edit.</p>}
          </>}
        </div>

        <div className="guided-foot">
          <button type="button" className="button secondary" onClick={() => step === 0 ? close() : setStep(step - 1)}>
            {step === 0 ? 'Cancel' : <><ArrowLeft size={16} /> Back</>}
          </button>
          {step < 3 ? (
            <button type="button" className="button primary" disabled={step === 0 && !structureId} onClick={() => {
              // With no take yet, the useful prompt is a script prompt.
              if (step === 2 && !transcript.trim() && target === 'plan') setTarget('script')
              setStep(step + 1)
            }}>
              {step === 1 && !transcript.trim() && !topic.trim() ? 'Skip' : 'Next'} <ArrowRight size={16} />
            </button>
          ) : (
            <div className="guided-finish">
              <button type="button" className="button secondary" onClick={() => finish('builder')}>
                <ListOrdered size={16} /> Open in Your edit
              </button>
              <button type="button" className="button primary" onClick={() => finish('copy')} disabled={!compiled?.text}>
                {copied ? <Check size={16} /> : <Clipboard size={16} />} {copied ? 'Copied' : 'Copy prompt'}
              </button>
            </div>
          )}
        </div>
      </div>
    </dialog>
  )
}
