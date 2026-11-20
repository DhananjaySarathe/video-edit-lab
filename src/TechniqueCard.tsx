import { Check, ChevronDown, ChevronUp, Clipboard, Plus } from 'lucide-react'
import { useId, useState } from 'react'
import { byId } from './catalog'
import { Preview, type PreviewProps } from './Preview'

type CardProps = PreviewProps & {
  selected: boolean
  copied: boolean
  onSelect: () => void
  onCopy: () => void
}

export function TechniqueCard({ technique, selected, playing, copied, onSelect, onPlay, onCopy }: CardProps) {
  const [expanded, setExpanded] = useState(false)
  const promptId = useId()
  const demo = technique.previewId ? byId.get(technique.previewId) : undefined
  return (
    <article className={`technique-card${selected ? ' is-selected' : ''}`} aria-label={technique.title}>
      <Preview technique={technique} playing={playing} onPlay={onPlay} />
      <div className="card-content">
        <h3>{technique.title}</h3>
        {technique.useCase && <p className="card-reason">{technique.useCase}</p>}
        <p className={expanded || technique.useCase ? 'card-prompt' : 'card-prompt excerpt'} id={promptId}
          hidden={!!technique.useCase && !expanded}>{technique.prompt}</p>
        {demo && <p className="card-demo">Demo · {demo.title}</p>}
        <button type="button" className="read-prompt" aria-expanded={expanded} aria-controls={promptId}
          onClick={() => setExpanded(value => !value)}>
          {expanded ? 'Show less' : 'Read full prompt'} {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
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
        </div>
      </div>
    </article>
  )
}
