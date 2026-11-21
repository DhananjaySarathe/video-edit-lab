import { ArrowRight, Check, ChevronDown, ChevronUp, Clipboard, Link, Play, Plus } from 'lucide-react'
import { useId, useRef, useState } from 'react'
import type { Technique } from './catalog'
import { beatTime, formatTime, type Structure, type StructureBeat } from './creator-hooks/catalog'
import { Preview, type PreviewHandle, type PreviewProps } from './Preview'

type Props = PreviewProps & {
  selected: boolean
  copied: boolean
  initialExpanded?: boolean
  linkCopied?: boolean
  onSelect: () => void
  onCopy: () => void
  onCopyLink: () => void
  onOpenMove: (id: string) => void
  onOpenHookType: (id: string) => void
}

const roleLabel: Record<string, string> = {
  hook: 'Hook', promise: 'Promise', context: 'Context', point: 'Body', proof: 'Proof', rehook: 'Re-hook',
  payoff: 'Payoff', cta: 'Ask', loop: 'Loop', endscreen: 'End screen',
}

function Strip({ structure, from, to, active, label, onPick }: {
  structure: Structure; from: number; to: number; active: number; label: string; onPick: (index: number) => void
}) {
  const span = to - from
  const beats = structure.beats
    .map((beat, index) => ({ beat, index, start: Math.max(beat.start, from), end: Math.min(beat.end, to) }))
    .filter(part => part.end > part.start)
  const ticks = `${(structure.every / span) * 100}%`
  return (
    <div className="timeline">
      <div className="timeline-head">
        <span>{label}</span>
        <span>{structure.mode === 'short' ? `${formatTime(to, 'short')} s` : formatTime(to, 'long')}</span>
      </div>
      <div className="timeline-bar" role="group" aria-label={`${structure.title}: ${label}`}>
        {beats.map(({ beat, index, start, end }) => {
          const width = ((end - start) / span) * 100
          return (
            <button key={index} type="button" className={`timeline-beat role-${beat.role}${active === index ? ' is-active' : ''}`}
              style={{ flexBasis: `${width}%` }} title={`${beat.title} · ${beatTime(beat, structure.mode)}`}
              aria-pressed={active === index} aria-label={`${beat.title}, ${beatTime(beat, structure.mode)}`}
              onClick={() => onPick(index)}>
              {width >= 13 && <span>{beat.title}</span>}
            </button>
          )
        })}
      </div>
      {span / structure.every <= 40 && <div className="timeline-rhythm" style={{ backgroundSize: `${ticks} 100%` }} aria-hidden="true" />}
    </div>
  )
}

function BeatDetail({ beat, structure, onPlay, onOpenMove }: {
  beat: StructureBeat; structure: Structure; onPlay?: () => void; onOpenMove: (id: string) => void
}) {
  return (
    <div className="beat-detail">
      <div className="beat-detail-head">
        <span className={`beat-role role-${beat.role}`}>{roleLabel[beat.role] ?? beat.role}</span>
        <strong>{beat.title}</strong>
        <span className="beat-time">{beatTime(beat, structure.mode)}</span>
        {onPlay && <button type="button" className="beat-play" onClick={onPlay} aria-label={`Play the example from ${beat.title}`}>
          <Play size={13} /> Example
        </button>}
      </div>
      <p>{beat.goal}</p>
      <p className="beat-line">“{beat.line}”</p>
      <p><strong>On screen</strong> {beat.show}</p>
      {beat.moves.length > 0 && <p className="beat-moves">{beat.moves.map(move => (
        <button key={move.id} type="button" onClick={() => onOpenMove(move.id)}>{move.title} <ArrowRight size={12} aria-hidden="true" /></button>
      ))}</p>}
    </div>
  )
}

export function StructureCard({ technique, vertical, selected, copied, playing, initialExpanded, linkCopied,
  onPlay, onSelect, onCopy, onCopyLink, onOpenMove, onOpenHookType }: Props & { technique: Technique }) {
  const structure = technique.structure!
  const [expanded, setExpanded] = useState(!!initialExpanded)
  const [active, setActive] = useState(0)
  const preview = useRef<PreviewHandle>(null)
  const planId = useId()
  const long = structure.mode === 'long'
  const beat = structure.beats[active]
  const play = (index: number) => {
    const at = structure.beats[index].example
    if (at !== undefined) preview.current?.playFrom(at)
  }
  const pick = (index: number) => {
    setActive(index)
    play(index)
  }

  return (
    <article className={`technique-card is-breakdown is-structure${vertical ? ' is-portrait-card' : ''}${selected ? ' is-selected' : ''}`}
      aria-label={`${technique.title} structure`}>
      <figure className="card-video">
        <Preview ref={preview} technique={technique} playing={playing} vertical={vertical} onPlay={onPlay} />
        <figcaption>{structure.example}{structure.exampleTotal
          ? ` ${long ? `The first ${Math.round(structure.exampleTotal)} seconds` : `${Math.round(structure.exampleTotal)} seconds`}, cut to this structure.` : ''}</figcaption>
      </figure>
      <div className="card-content">
        <p className="card-demo card-kicker">Structure · {structure.length}</p>
        <h3>{technique.title}</h3>
        <p className="card-reason">{structure.bestFor}</p>
        {long && <Strip structure={structure} from={0} to={Math.min(60, structure.total)} active={active} label="First minute" onPick={pick} />}
        <Strip structure={structure} from={0} to={structure.total} active={active} label={long ? 'Whole video' : 'Beat by beat'} onPick={pick} />
        <p className="timeline-note">{long ? 'Ticks on the first minute mark' : 'Each tick marks'} a change on screen. {structure.rhythm}</p>
        <BeatDetail beat={beat} structure={structure} onOpenMove={onOpenMove}
          onPlay={beat.example !== undefined ? () => play(active) : undefined} />
        <div className="structure-hooks">
          <span>Hooks that fit</span>
          {structure.hookTypes.map(type => (
            <button key={type.id} type="button" onClick={() => onOpenHookType(type.id)}>{type.title}</button>
          ))}
        </div>
        <button type="button" className="read-prompt" aria-expanded={expanded} aria-controls={planId}
          onClick={() => setExpanded(value => !value)}>
          {expanded ? 'Hide the full plan' : 'Read the full plan'}
          {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </button>
        <div className="card-actions">
          <button type="button" className="button secondary" onClick={onCopy} aria-label={`Copy prompt for the ${technique.title} structure`}>
            {copied ? <Check size={16} /> : <Clipboard size={16} />}
            {copied ? 'Copied' : 'Copy prompt'}
          </button>
          <button type="button" className={`button ${selected ? 'added' : 'tinted'}`} aria-pressed={selected}
            aria-label={`${selected ? 'Remove' : 'Add'} the ${technique.title} structure ${selected ? 'from' : 'to'} your edit`} onClick={onSelect}>
            {selected ? <Check size={16} /> : <Plus size={16} />}
            {selected ? 'Added' : 'Add'}
          </button>
          <button type="button" className="icon-button sample-link" onClick={onCopyLink}
            aria-label={`Copy link to the ${technique.title} structure`} title={linkCopied ? 'Link copied' : 'Copy link'}>
            {linkCopied ? <Check size={16} /> : <Link size={16} />}
          </button>
        </div>
      </div>
      <div className="breakdown-detail structure-plan" id={planId} hidden={!expanded}>
        <div>
          <h4>The full plan</h4>
          <ol className="structure-beats">
            {structure.beats.map((item, index) => (
              <li key={index} className={active === index ? 'is-active' : ''}>
                <button type="button" className="beat-play" onClick={() => pick(index)}
                  aria-label={`${item.title}, ${beatTime(item, structure.mode)}${item.example !== undefined ? '. Play the example from here' : ''}`}>
                  {item.example !== undefined && <Play size={12} />} {beatTime(item, structure.mode)}
                </button>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.goal}</p>
                  <p className="beat-line">“{item.line}”</p>
                  <p><em>On screen:</em> {item.show}</p>
                  {item.moves.length > 0 && <p className="beat-moves">{item.moves.map(move => (
                    <button key={move.id} type="button" onClick={() => onOpenMove(move.id)}>{move.title}</button>
                  ))}</p>}
                </div>
              </li>
            ))}
          </ol>
        </div>
        <dl className="breakdown-notes">
          <div><dt>Footage you need</dt><dd>{structure.footage}</dd></div>
          <div><dt>Pacing</dt><dd>{structure.rhythm}</dd></div>
          <div><dt>Before you export</dt><dd><ul className="structure-checks">{structure.checks.map(check => <li key={check}>{check}</li>)}</ul></dd></div>
        </dl>
        <div className="breakdown-prompt">
          <h4>AI editor prompt</h4>
          <p>{technique.prompt}</p>
        </div>
      </div>
    </article>
  )
}
