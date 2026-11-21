import { Check, ChevronDown, ChevronUp, Clipboard, Link, Play, Plus } from 'lucide-react'
import { useId, useRef, useState } from 'react'
import type { Breakdown } from './breakdown'
import { byId, stageLabels } from './catalog'
import { Preview, type PreviewHandle, type PreviewProps } from './Preview'

type CardProps = PreviewProps & {
  selected: boolean
  copied: boolean
  onSelect: () => void
  onCopy: () => void
  initialExpanded?: boolean
  linkCopied?: boolean
  onCopyLink?: () => void
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

export function TechniqueCard({ technique, selected, playing, vertical, copied, initialExpanded, linkCopied, onCopyLink, onSelect, onPlay, onCopy }: CardProps) {
  const [expanded, setExpanded] = useState(!!initialExpanded)
  const promptId = useId()
  const preview = useRef<PreviewHandle>(null)
  const demo = technique.previewId ? byId.get(technique.previewId) : undefined
  const breakdown = technique.breakdown
  return (
    <article className={`technique-card${breakdown ? ' is-breakdown' : ''}${vertical ? ' is-portrait-card' : ''}${selected ? ' is-selected' : ''}`} aria-label={technique.title}>
      <figure className="card-video">
        <Preview ref={preview} technique={technique} playing={playing} vertical={vertical} onPlay={onPlay} />
        {breakdown?.previewLabel && <figcaption>{breakdown.previewLabel}</figcaption>}
      </figure>
      <div className="card-content">
        <h3>{technique.title}</h3>
        {technique.useCase && <p className="card-reason">{technique.useCase}</p>}
        {!breakdown && <p className={expanded || technique.useCase ? 'card-prompt' : 'card-prompt excerpt'} id={promptId}
          hidden={!!technique.useCase && !expanded}>{technique.prompt}</p>}
        {!breakdown && demo && <p className="card-demo">Demo · {demo.title}</p>}
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
          {expanded ? 'Show less' : breakdown ? 'Read cut plan' : 'Read full prompt'}
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
