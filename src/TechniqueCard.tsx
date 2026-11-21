import { ArrowRight, Check, ChevronDown, ChevronUp, Clipboard, Link, Play, Plus } from 'lucide-react'
import { useId, useRef, useState } from 'react'
import type { Breakdown } from './breakdown'
import { byId, stageLabels, type Technique } from './catalog'
import { Preview, type PreviewHandle, type PreviewProps } from './Preview'

type CardProps = PreviewProps & {
  selected: boolean
  copied: boolean
  onSelect: () => void
  onCopy: () => void
  initialExpanded?: boolean
  linkCopied?: boolean
  onCopyLink?: () => void
  onOpenMove?: (id: string) => void
}

function HookLayers({ technique, vertical, expanded, id, onOpenMove }: {
  technique: Technique; vertical?: boolean; expanded: boolean; id: string; onOpenMove?: (id: string) => void
}) {
  const hook = technique.creator!
  return (
    <>
      <dl className="hook-layers">
        <div><dt>On screen</dt><dd className="layer-text">{hook.text}</dd></div>
        <div><dt>First frame</dt><dd>{hook.frame}</dd></div>
        <div><dt>Edit move</dt><dd>{onOpenMove
          ? <button type="button" className="layer-move" onClick={() => onOpenMove(hook.move.id)}
            aria-label={`See the edit move ${hook.move.title}`}>{hook.move.title} <ArrowRight size={13} aria-hidden="true" /></button>
          : hook.move.title}</dd></div>
      </dl>
      <div className="card-more" id={id} hidden={!expanded}>
        <dl className="hook-layers">
          <div><dt>{vertical ? 'Next 3 seconds' : 'By 30 seconds'}</dt><dd>{hook.next}</dd></div>
          <div><dt>Formula</dt><dd>{hook.formula}</dd></div>
          <div><dt>Muted check</dt><dd>{hook.check}</dd></div>
        </dl>
        <h4>AI editor prompt</h4>
        <p className="card-prompt">{technique.prompt}</p>
      </div>
    </>
  )
}

function MoveDetails({ technique, vertical, expanded, id }: { technique: Technique; vertical?: boolean; expanded: boolean; id: string }) {
  const move = technique.move!
  return (
    <>
      <dl className="hook-layers">
        <div><dt>When</dt><dd>{move.when}</dd></div>
        <div><dt>How often</dt><dd>{vertical ? move.often.short : move.often.long}</dd></div>
      </dl>
      <div className="card-more" id={id} hidden={!expanded}>
        <dl className="hook-layers">
          <div><dt>Avoid</dt><dd>{move.avoid}</dd></div>
          <div><dt>{vertical ? 'On long form' : 'On Reels and Shorts'}</dt><dd>{vertical ? move.often.long : move.often.short}</dd></div>
        </dl>
        <h4>AI editor prompt</h4>
        <p className="card-prompt">{move.prompt}</p>
      </div>
    </>
  )
}

function BreakdownDetails({ breakdown, id, onCue }: { breakdown: Breakdown; id: string; onCue: (seconds: number) => void }) {
  return (
    <div className="breakdown-detail" id={id}>
      <div className="breakdown-plan">
        <h4>Cut plan</h4>
        <ol className="cut-plan">
          {breakdown.beats.map(([cue, edit]) => (
            <li key={cue}>{breakdown.opener ? <button type="button" className="beat-play"
              aria-label={`Play ${breakdown.title} from ${parseFloat(cue)} seconds`}
              onClick={() => onCue(parseFloat(cue))}><Play size={13} /> {cue}</button> : <span>{cue}</span>}<p>{edit}</p></li>
          ))}
        </ol>
        {breakdown.observation && <>
          <h4>Research observation</h4>
          <p>{breakdown.observation}</p>
        </>}
      </div>
      <dl className="breakdown-notes">
        {breakdown.footage && <div><dt>Footage you need</dt><dd>{breakdown.footage}</dd></div>}
        {breakdown.skipWhen && <div><dt>When to skip it</dt><dd>{breakdown.skipWhen}</dd></div>}
        <div><dt>How to check the cut</dt><dd>{breakdown.check}</dd></div>
      </dl>
      <div className="breakdown-prompt">
        <h4>AI editor prompt</h4>
        <p>{breakdown.prompt}</p>
      </div>
    </div>
  )
}

export function TechniqueCard({ technique, selected, playing, vertical, copied, initialExpanded, linkCopied, onCopyLink, onOpenMove, onSelect, onPlay, onCopy }: CardProps) {
  const [expanded, setExpanded] = useState(!!initialExpanded)
  const promptId = useId()
  const preview = useRef<PreviewHandle>(null)
  const demo = technique.previewId ? byId.get(technique.previewId) : undefined
  const breakdown = technique.breakdown
  const custom = technique.creator || technique.move
  return (
    <article className={`technique-card${breakdown ? ' is-breakdown' : ''}${vertical ? ' is-portrait-card' : ''}${selected ? ' is-selected' : ''}`} aria-label={technique.title}>
      <figure className="card-video">
        <Preview ref={preview} technique={technique} playing={playing} vertical={vertical} onPlay={onPlay} />
        {breakdown?.previewLabel && <figcaption>{breakdown.previewLabel}</figcaption>}
      </figure>
      <div className="card-content">
        <h3>{technique.creator ? `“${technique.title}”` : technique.title}</h3>
        {technique.creator && <p className="card-demo card-kicker">{technique.section} · {technique.creator.presetLabels.join(', ')}</p>}
        {technique.move && <p className="card-demo card-kicker">{technique.section}{technique.sound ? ' · With sound' : ''}</p>}
        {technique.useCase && <p className="card-reason">{technique.move ? <><strong>Fixes</strong> {technique.useCase}</> : technique.useCase}</p>}
        {technique.creator && <HookLayers technique={technique} vertical={vertical} expanded={expanded} id={promptId} onOpenMove={onOpenMove} />}
        {technique.move && <MoveDetails technique={technique} vertical={vertical} expanded={expanded} id={promptId} />}
        {!breakdown && !custom && <p className={expanded || technique.useCase ? 'card-prompt' : 'card-prompt excerpt'} id={promptId}
          hidden={!!technique.useCase && !expanded}>{technique.prompt}</p>}
        {!breakdown && !custom && demo && <p className="card-demo">Demo · {demo.title}</p>}
        {breakdown && <p className="card-demo">{breakdown.opener ? technique.section : stageLabels[breakdown.stage]}
          {breakdown.previewKind && <> · {breakdown.duration} s · {breakdown.previewKind === 'worked' ? 'Worked example' : 'Timed shot plan'}</>}
        </p>}
        {breakdown?.opener && <div className="opening-beat">
          <strong>Opening line</strong>
          <p>“{breakdown.opener}”</p>
        </div>}
        {vertical && breakdown?.stage === 'hook' && !breakdown.opener && !expanded && <div className="opening-beat">
          <strong>Opening shot</strong>
          <p>{breakdown.beats[0][1]}</p>
        </div>}
        <button type="button" className="read-prompt" aria-expanded={expanded} aria-controls={promptId}
          onClick={() => setExpanded(value => !value)}>
          {expanded ? 'Show less' : breakdown ? 'Read cut plan' : technique.creator ? 'Read full hook' : technique.move ? 'Avoid and prompt' : 'Read full prompt'}
          {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </button>
        <div className="card-actions">
          <button type="button" className="button secondary" onClick={onCopy} aria-label={`Copy prompt for ${technique.title}`}>
            {copied ? <Check size={16} /> : <Clipboard size={16} />}
            {copied ? 'Copied' : 'Copy prompt'}
          </button>
          <button type="button" className={`button ${selected ? 'added' : 'tinted'}`}
            aria-pressed={selected} aria-label={`${selected ? 'Remove' : 'Add'} ${technique.title} ${selected ? 'from' : 'to'} your edit`} onClick={onSelect}>
            {selected ? <Check size={16} /> : <Plus size={16} />}
            {selected ? 'Added' : 'Add'}
          </button>
          {onCopyLink && <button type="button" className="icon-button sample-link" onClick={onCopyLink}
            aria-label={`Copy link to ${technique.title}`} title={linkCopied ? 'Link copied' : 'Copy example link'}>
            {linkCopied ? <Check size={16} /> : <Link size={16} />}
          </button>}
        </div>
      </div>
      {breakdown && (expanded ? <BreakdownDetails id={promptId} breakdown={breakdown} onCue={seconds => preview.current?.playFrom(seconds)} /> : <div id={promptId} hidden />)}
    </article>
  )
}
