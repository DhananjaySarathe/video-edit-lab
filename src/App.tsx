import {
  ArrowDown, ArrowRight, BookOpen, Check, ChevronDown, ChevronRight,
  Film, ListOrdered, Plus, Search, Smartphone, X,
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { byId, formatBreakdowns, formatCollections, modes, sections, stageLabels, techniques, withSound, type FormatMode, type Stage } from './catalog'
import { addItems, readEdit, removeItem, saveEdit, writeClipboard } from './edit'
import { footageGroups, hookCollections, hookExamples, hookGuidance, hookHash } from './hook-library/catalog'
import { EditBuilder } from './EditBuilder'
import { Preview } from './Preview'
import { TechniqueCard } from './TechniqueCard'
import { starters } from './starters'

type Shelf = Stage | 'breakdowns' | 'techniques'
const initialShelf: Shelf = 'hook'
const batchSize = (shelf: Shelf) => shelf === 'breakdowns' ? 6 : 12
const stages: Record<FormatMode, readonly Stage[]> = {
  short: ['hook', 'body', 'finish'],
  long: ['hook', 'intro', 'body', 'finish'],
}

const guide = {
  short: {
    title: 'Edit a Short from hook to payoff.',
    description: 'Build a hook that reads in one shot, pace the middle, and give viewers a payoff worth the setup.',
    spotlight: 'short-clone-split',
    focus: 'Two characters, one performer',
  },
  long: {
    title: 'Shape the whole story.',
    description: 'Earn the opening promise with evidence, guide viewers through the story, and bring the ending back to the first scene.',
    spotlight: 'long-cold-open',
    focus: 'Open inside the story',
  },
}

const searchable = (value: string) => value.toLowerCase().normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim()

function readLocation() {
  const [format, type, ordinal] = window.location.hash.slice(1).split('/')
  const mode: FormatMode = format === 'long-form' ? 'long' : 'short'
  const collection = hookCollections[mode].some(group => group.id === type) ? type : ''
  const id = collection && ordinal ? `hook-${mode}-${collection}-${ordinal}` : ''
  return { mode, collection, sample: byId.has(id) ? id : '' }
}

export function App() {
  const [edit, setEdit] = useState(readEdit)
  const [mode, setMode] = useState<FormatMode>(() => readLocation().mode)
  const [shelf, setShelf] = useState<Shelf>(initialShelf)
  const [collection, setCollection] = useState(() => readLocation().collection)
  const [linkedSample, setLinkedSample] = useState(() => readLocation().sample)
  const [query, setQuery] = useState('')
  const [media, setMedia] = useState('')
  const [footage, setFootage] = useState('')
  const [onlySelected, setOnlySelected] = useState(false)
  const [limit, setLimit] = useState(() => batchSize(initialShelf))
  const [starterIndex, setStarterIndex] = useState(0)
  const [playing, setPlaying] = useState<string | null>(null)
  const [copied, setCopied] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const library = useRef<HTMLElement>(null)
  const moreResults = useRef<HTMLDivElement>(null)
  const builder = useRef<HTMLElement>(null)
  const dialog = useRef<HTMLDialogElement>(null)
  const copyTimer = useRef<number>()

  const updatePlayback = useCallback((id: string, active: boolean) => {
    setPlaying(current => active ? id : current === id ? null : current)
  }, [])

  useEffect(() => saveEdit(edit), [edit])
  useEffect(() => {
    const desktop = window.matchMedia('(min-width: 1100px)')
    const onDesktop = (event: MediaQueryListEvent) => { if (event.matches) dialog.current?.close() }
    desktop.addEventListener('change', onDesktop)
    const followFormat = () => {
      const route = readLocation()
      setMode(route.mode)
      setStarterIndex(0)
      setShelf(initialShelf)
      resetFilters(initialShelf)
      setCollection(route.collection)
      setLinkedSample(route.sample)
    }
    window.addEventListener('popstate', followFormat)
    return () => {
      desktop.removeEventListener('change', onDesktop)
      window.removeEventListener('popstate', followFormat)
      if (copyTimer.current !== undefined) window.clearTimeout(copyTimer.current)
    }
  }, [])

  useEffect(() => {
    if (linkedSample) library.current?.scrollIntoView({ block: 'start' })
  }, [linkedSample])

  const selected = useMemo(() => new Set(edit.items.map(item => item.id)), [edit.items])
  const activeGuide = guide[mode]
  const spotlight = byId.get(activeGuide.spotlight)
  const starterList = starters[mode]
  const starter = starterList[starterIndex]
  const missingSteps = starter.steps.filter(step => !selected.has(step.id))
  const collections = formatCollections[mode]
  const breakdowns = formatBreakdowns[mode]
  const stageCollections = collections.filter(group => group.stage === shelf)
  const activeType = shelf === 'hook' ? hookCollections[mode].find(group => group.id === collection) : undefined
  const options = shelf === 'techniques'
    ? sections.map(section => ({ id: section.name, title: section.label }))
    : shelf === 'breakdowns'
      ? stages[mode].map(stage => ({ id: stage, title: stageLabels[stage] }))
      : stageCollections.map(group => ({ id: group.id, title: group.question ? `${group.title} (${group.items.length})` : group.title }))
  const counts = Object.fromEntries(stages[mode].map(stage => [
    stage, collections.filter(group => group.stage === stage).reduce((total, group) => total + group.items.length, 0),
  ]))
  const entries = useMemo(() => {
    if (shelf === 'techniques') return techniques.filter(item => !collection || item.section === collection)
    if (shelf === 'breakdowns') return breakdowns.filter(item => !collection || item.breakdown.stage === collection)
    const current = collections.filter(group => group.stage === shelf && (!collection || group.id === collection))
    if (shelf === 'hook' && !collection) return [...hookExamples[mode], ...current.filter(group => !group.question).flatMap(group => group.items)]
    const matches = current.flatMap(group => group.items)
    const linked = linkedSample && matches.find(item => item.id === linkedSample)
    return linked ? [linked, ...matches.filter(item => item.id !== linkedSample)] : matches
  }, [shelf, collection, breakdowns, collections, mode, linkedSample])
  const visible = useMemo(() => {
    const queryTerms = searchable(query).split(' ').filter(Boolean)
    return entries.filter(item => {
      if (onlySelected && !selected.has(item.id)) return false
      if (footage && item.breakdown?.footageGroup !== footage) return false
      if ((media === 'worked' || media === 'storyboard') && item.breakdown?.previewKind !== media) return false
      if ((media === 'sound' || media === 'visual') && withSound(item) !== (media === 'sound')) return false
      if (!queryTerms.length) return true
      const words = searchable([item.title, item.useCase, item.section, item.prompt, item.breakdown?.footage].join(' '))
      return queryTerms.every(word => words.includes(word))
    })
  }, [entries, onlySelected, selected, media, footage, query])
  const shown = visible.slice(0, limit)
  const hasMore = shown.length < visible.length

  useEffect(() => {
    const target = moreResults.current
    if (!hasMore || !target) return
    if (typeof IntersectionObserver === 'undefined') {
      setLimit(visible.length)
      return
    }
    let active = true
    const observer = new IntersectionObserver(events => {
      if (!active || !events.some(event => event.isIntersecting)) return
      active = false
      observer.disconnect()
      setLimit(current => Math.min(current + batchSize(shelf), visible.length))
    }, { rootMargin: '0px 0px 360px' })
    observer.observe(target)
    return () => {
      active = false
      observer.disconnect()
    }
  }, [hasMore, limit, shelf, mode, query, collection, media, footage, onlySelected, visible.length])

  function resetFilters(nextShelf = shelf) {
    setQuery('')
    setCollection('')
    setLinkedSample('')
    setMedia('')
    setFootage('')
    setOnlySelected(false)
    setLimit(batchSize(nextShelf))
    setPlaying(null)
  }

  function chooseMode(next: FormatMode) {
    if (next === mode) return
    window.history.pushState(null, '', next === 'long' ? '#long-form' : '#reels-shorts')
    setMode(next)
    setShelf(initialShelf)
    setStarterIndex(0)
    resetFilters(initialShelf)
    window.scrollTo({ top: 0 })
  }

  function chooseShelf(next: Shelf) {
    const format = mode === 'long' ? '#long-form' : '#reels-shorts'
    if (window.location.hash.includes('/')) window.history.replaceState(null, '', format)
    setShelf(next)
    resetFilters(next)
    revealLibrary()
  }

  function chooseCollection(next: string) {
    setCollection(next)
    setLinkedSample('')
    if (shelf === 'hook') {
      const format = mode === 'long' ? '#long-form' : '#reels-shorts'
      const type = hookCollections[mode].some(group => group.id === next)
      window.history.replaceState(null, '', `${format}${type ? `/${next}` : ''}`)
    }
    resetResults()
  }

  function revealLibrary() {
    library.current?.focus({ preventScroll: true })
    library.current?.scrollIntoView({ block: 'start' })
  }

  function changeSelection(id: string) {
    const alreadySelected = selected.has(id)
    setEdit(current => current.items.some(item => item.id === id)
      ? removeItem(current, id)
      : addItems(current, [{ id, cue: '' }], modes[mode].format))
    setMessage(alreadySelected ? 'Removed from your edit.' : 'Added to your edit.')
  }

  function addStarter() {
    setEdit(current => addItems(current, starter.steps.map(({ id, cue }) => ({ id, cue })), modes[mode].format))
    setMessage(`${missingSteps.length} steps from ${starter.title} added to your edit.`)
  }

  function openBuilder() {
    if (window.matchMedia('(min-width: 1100px)').matches) {
      builder.current?.focus({ preventScroll: true })
      builder.current?.scrollIntoView({ block: 'start' })
    } else {
      dialog.current?.showModal()
    }
  }

  async function copy(key: string, text: string) {
    try {
      await writeClipboard(text)
      if (copyTimer.current !== undefined) window.clearTimeout(copyTimer.current)
      setCopied(key)
      setError('')
      setMessage(key === 'combined' ? 'Combined prompt copied.' : key.startsWith('link:') ? 'Example link copied.' : 'Technique prompt copied.')
      copyTimer.current = window.setTimeout(() => setCopied(null), 1800)
    } catch {
      setError(key.startsWith('link:') ? `Copy this example link manually. ${text}` :
        key === 'combined' ? 'Copy failed. Open Combined prompt to select and copy the text.' : 'Copy failed. Expand the prompt to select and copy the text.')
    }
  }

  function resetResults() {
    setLimit(batchSize(shelf))
    setPlaying(null)
  }

  const builderProps = { edit, setEdit, copied: copied === 'combined', onCopy: (text: string) => { void copy('combined', text) } }
  const shelfName = shelf === 'techniques' ? 'Technique library' : shelf === 'breakdowns' ? 'Edit breakdowns' : stageLabels[shelf]
  const libraryTitle = shelf === 'techniques' || shelf === 'breakdowns' ? shelfName : `${modes[mode].label} ${shelfName.toLowerCase()}`
  const resultNoun = shelf === 'techniques' ? 'techniques' : shelf === 'breakdowns' ? 'breakdowns' : 'recipes'

  return (
    <>
      <a className="skip-link" href="#recipe-library" onClick={event => { event.preventDefault(); revealLibrary() }}>Skip to recipes</a>
      <header className="site-header">
        <div className="site-header-inner">
          <a className="brand" href="./" aria-label="Video Edit Lab home">
            <span className="brand-mark" aria-hidden="true">r<span>.</span></span>
            <span className="brand-name">Video Edit Lab</span>
          </a>
          <nav className="format-nav" aria-label="Video formats">
            <button type="button" aria-pressed={mode === 'short'} onClick={() => chooseMode('short')}>
              <Smartphone size={16} aria-hidden="true" /> Reels/Shorts
            </button>
            <button type="button" aria-pressed={mode === 'long'} onClick={() => chooseMode('long')}>
              <Film size={16} aria-hidden="true" /> Long Form
            </button>
          </nav>
          <button type="button" className="button primary header-edit" onClick={openBuilder}>
            <ListOrdered size={17} aria-hidden="true" /> Your edit
            <span className="edit-count">{edit.items.length}</span>
          </button>
        </div>
      </header>

      <main className="main-content">
        <section className={`format-hero format-hero-${mode}`} aria-labelledby="mode-title">
          <div className="hero-copy">
            <h1 id="mode-title">{activeGuide.title}</h1>
            <p>{activeGuide.description}</p>
            <div className="hero-actions">
              <button className="button hero-action" type="button" onClick={() => chooseShelf('hook')}>
                Explore hooks <ArrowDown size={16} aria-hidden="true" />
              </button>
              <div className="hero-links">
                <button type="button" className="hero-secondary" onClick={() => chooseShelf('breakdowns')}>Breakdowns</button>
                <button type="button" className="hero-secondary" onClick={() => chooseShelf('body')}>Editing styles</button>
                <button type="button" className="hero-secondary" onClick={() => chooseShelf('finish')}>
                  Finishes <ArrowRight size={14} aria-hidden="true" />
                </button>
              </div>
            </div>
          </div>
          {spotlight && <figure className="hero-spotlight">
            <Preview key={spotlight.id} technique={spotlight} playing={playing === 'hero'} vertical={mode === 'short'} playbackId="hero"
              priority onPlay={updatePlayback} />
            <figcaption>{activeGuide.focus} <span>Hover or tap to play</span></figcaption>
          </figure>}
        </section>

        <details className="starter-disclosure">
          <summary>Start with a workflow <ChevronDown size={16} aria-hidden="true" /></summary>
          <div className="starter-strip">
            <div className="starter-options" role="group" aria-label="Starter workflow">
              {starterList.map((option, index) => (
                <button type="button" className="button secondary" key={option.title}
                  aria-pressed={starterIndex === index} onClick={() => setStarterIndex(index)}>
                  {option.title}
                </button>
              ))}
            </div>
            <div className="starter-summary">
              <p>{starter.footage}</p>
              <ol className="starter-steps">
                {starter.steps.map((step, index) => (
                  <li key={step.id}>{index > 0 && <ChevronRight size={14} aria-hidden="true" />} {step.stage}</li>
                ))}
              </ol>
              {missingSteps.length < starter.steps.length && <p>Existing steps keep their timing cues.</p>}
            </div>
            <button className="button primary starter-add" type="button" disabled={!missingSteps.length} onClick={addStarter}>
              {missingSteps.length ? <Plus size={16} /> : <Check size={16} />}
              {missingSteps.length ? `Add ${missingSteps.length} ${missingSteps.length < starter.steps.length ? 'remaining ' : ''}${missingSteps.length === 1 ? 'step' : 'steps'}` : 'Steps already in your edit'}
            </button>
          </div>
        </details>

        <div className="workspace">
          <section className="library" id="recipe-library" ref={library} tabIndex={-1} aria-labelledby="library-title">
            <nav className="shelf-nav" aria-label="Edit stages">
              <button type="button" aria-pressed={shelf === 'breakdowns'} onClick={() => chooseShelf('breakdowns')}>
                Breakdowns <span>{breakdowns.length}</span>
              </button>
              {stages[mode].map(stage => (
                <button type="button" key={stage} aria-pressed={shelf === stage} onClick={() => chooseShelf(stage)}>
                  {stageLabels[stage]} <span>{counts[stage]}</span>
                </button>
              ))}
              <button type="button" aria-pressed={shelf === 'techniques'} onClick={() => chooseShelf('techniques')}>
                <BookOpen size={16} aria-hidden="true" /> Technique library
              </button>
            </nav>
            <div className="library-heading">
              <h2 id="library-title">{libraryTitle}</h2>
              {shelf === 'techniques' && <p>Original technique demonstrations for either format.</p>}
              {shelf === 'breakdowns' && <p>See the shot order, the timing, and what to check in your own cut.</p>}
              {shelf === 'hook' && <p>{activeType ? activeType.question : `Choose from ${hookCollections[mode].length} hook types. Worked examples demonstrate the edit. Timed shot plans use stand-in footage to show what to film and when to cut.`}</p>}
            </div>
            {shelf === 'hook' && (activeType ? <div className="hook-type-note">
              <p><strong>Footage to look for</strong> {hookGuidance[activeType.id].footage}</p>
              <p><strong>Playback check</strong> {hookGuidance[activeType.id].check}</p>
            </div> : !collection && <details className="hook-finder" key={mode}>
              <summary>Which hook suits my footage? <ChevronDown size={15} aria-hidden="true" /></summary>
              <div className="hook-type-choices">
                {hookCollections[mode].map(type => <button key={type.id} type="button" onClick={() => {
                  chooseCollection(type.id); setFootage(''); setMedia(''); setQuery(''); revealLibrary()
                }}>
                  <strong>{type.title} <ArrowRight size={13} aria-hidden="true" /></strong>
                  <span>{hookGuidance[type.id].footage}</span>
                </button>)}
              </div>
            </details>)}
            <div className="filters" aria-label="Filter recipes">
              <div className="search-field">
                <Search size={18} aria-hidden="true" />
                <input type="search" aria-label="Search recipes" placeholder={`Search ${shelfName.toLowerCase()}…`} value={query}
                  onChange={event => { setQuery(event.target.value); resetResults() }} />
                {query && <button className="icon-button" type="button" aria-label="Clear search" onClick={() => { setQuery(''); resetResults() }}><X size={17} /></button>}
              </div>
              <div className="select-wrap collection-select">
                <select aria-label={shelf === 'breakdowns' ? 'Filter by edit stage' : shelf === 'hook' ? 'Filter by hook type' : 'Filter by collection'} value={collection}
                  onChange={event => chooseCollection(event.target.value)}>
                  <option value="">{shelf === 'breakdowns' ? 'All edit stages' : shelf === 'hook' ? 'All hook types' : 'All collections'}</option>
                  {shelf === 'hook' ? <>
                    <optgroup label="Hook types">{options.filter(option => hookCollections[mode].some(group => group.id === option.id)).map(option =>
                      <option value={option.id} key={option.id}>{option.title}</option>)}</optgroup>
                    <optgroup label="More opening recipes">{options.filter(option => !hookCollections[mode].some(group => group.id === option.id)).map(option =>
                      <option value={option.id} key={option.id}>{option.title}</option>)}</optgroup>
                  </> : options.map(option => <option value={option.id} key={option.id}>{option.title}</option>)}
                </select>
                <ChevronDown size={16} aria-hidden="true" />
              </div>
            </div>
            <div className="library-meta">
              <p className="result-count" aria-live="polite">
                {`${visible.length} ${visible.length === 1 ? resultNoun.slice(0, -1) : resultNoun}`}
              </p>
              <div className="filter-options">
                {shelf === 'hook' && <div className="select-wrap">
                  <select value={footage} aria-label="Filter by footage you have"
                    onChange={event => { setFootage(event.target.value); resetResults() }}>
                    <option value="">Any footage</option>
                    {footageGroups.map(group => <option key={group.title}>{group.title}</option>)}
                  </select>
                  <ChevronDown size={15} aria-hidden="true" />
                </div>}
                <div className="select-wrap">
                  <select value={media} aria-label="Filter previews"
                    onChange={event => { setMedia(event.target.value); resetResults() }}>
                    <option value="">All previews</option>
                    {shelf === 'hook' && <><option value="worked">Worked examples</option><option value="storyboard">Timed shot plans</option></>}
                    <option value="visual">Visual only</option><option value="sound">With sound</option>
                  </select>
                  <ChevronDown size={15} aria-hidden="true" />
                </div>
                <label className="selected-filter">
                  <input type="checkbox" checked={onlySelected} onChange={event => { setOnlySelected(event.target.checked); resetResults() }} /> Selected only
                </label>
              </div>
            </div>

            {shown.length ? <div className="technique-grid">
              {shown.map(technique => (
                <TechniqueCard key={`${mode}-${technique.id}${linkedSample === technique.id ? '-linked' : ''}`}
                  initialExpanded={linkedSample === technique.id} technique={technique} vertical={mode === 'short'} selected={selected.has(technique.id)}
                  copied={copied === technique.id} playing={playing === technique.id} onPlay={updatePlayback}
                  linkCopied={copied === `link:${technique.id}`}
                  onCopyLink={technique.breakdown?.opener ? () => {
                    const link = new URL(window.location.href)
                    link.hash = hookHash(technique.id)!
                    void copy(`link:${technique.id}`, link.href)
                  } : undefined}
                  onSelect={() => changeSelection(technique.id)} onCopy={() => { void copy(technique.id, technique.prompt) }} />
              ))}
            </div> : <div className="no-results">
              <Search size={24} strokeWidth={1.5} /><h3>No matching recipes</h3>
              <p>Try a different search or clear your filters.</p>
              <button type="button" className="button secondary" onClick={() => { chooseCollection(''); resetFilters() }}>Clear filters</button>
            </div>}

            {visible.length > batchSize(shelf) && <div className="results-end" ref={moreResults}>
              {hasMore && <ArrowDown size={15} aria-hidden="true" />}
              {hasMore ? `${shown.length} of ${visible.length} shown` : `All ${visible.length} ${resultNoun} shown`}
            </div>}
          </section>

          <aside className="desktop-builder" aria-label="Edit builder" ref={builder} tabIndex={-1}>
            <EditBuilder {...builderProps} />
          </aside>
        </div>
      </main>

      <dialog ref={dialog} className="builder-dialog" aria-labelledby="mobile-builder-title"
        onClick={event => { if (event.target === event.currentTarget) dialog.current?.close() }}>
        <EditBuilder {...builderProps} headingId="mobile-builder-title" onClose={() => dialog.current?.close()} />
        {error && <div className="dialog-error" role="alert">{error}</div>}
      </dialog>

      <div className="sr-only" role="status" aria-live="polite">{message}</div>
      {error && <div className="toast" role="alert">{error}<button type="button" className="icon-button"
        aria-label="Dismiss error" onClick={() => setError('')}><X size={16} /></button></div>}
    </>
  )
}
