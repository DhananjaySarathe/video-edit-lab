import {
  ArrowDown, ArrowRight, BookOpen, Check, ChevronDown, ChevronLeft, ChevronRight,
  Film, ListOrdered, Plus, Search, Smartphone, X,
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { byId, formatCollections, modes, sections, stageLabels, techniques, withSound, type FormatMode, type Stage } from './catalog'
import { addItems, readEdit, removeItem, saveEdit, writeClipboard } from './edit'
import { EditBuilder } from './EditBuilder'
import { Preview } from './Preview'
import { TechniqueCard } from './TechniqueCard'
import { starters } from './starters'

type Shelf = Stage | 'techniques'
const pageSize = 12
const stages: Record<FormatMode, readonly Stage[]> = {
  short: ['hook', 'body', 'finish'],
  long: ['hook', 'intro', 'body', 'finish'],
}

const guide = {
  short: {
    title: 'Edit a Short from hook to payoff.',
    description: 'Find a first-frame hook, then build the whole Reel. Try dual-character scenes, rapid cuts, and endings that loop.',
    spotlight: 'short-clone-split',
    focus: 'Two characters, one performer',
  },
  long: {
    title: 'Shape the whole story.',
    description: 'Open on a reason to stay. Build the intro, guide viewers through the story, and bring the opening promise home.',
    spotlight: 'long-cold-open',
    focus: 'Open inside the story',
  },
}

const searchable = (value: string) => value.toLowerCase().normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim()

function initialMode(): FormatMode {
  return window.location.hash === '#long-form' ? 'long' : 'short'
}

export function App() {
  const [edit, setEdit] = useState(readEdit)
  const [mode, setMode] = useState<FormatMode>(initialMode)
  const [shelf, setShelf] = useState<Shelf>('hook')
  const [collection, setCollection] = useState('')
  const [query, setQuery] = useState('')
  const [media, setMedia] = useState('')
  const [onlySelected, setOnlySelected] = useState(false)
  const [page, setPage] = useState(1)
  const [starterIndex, setStarterIndex] = useState(0)
  const [playing, setPlaying] = useState<string | null>(null)
  const [copied, setCopied] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const library = useRef<HTMLElement>(null)
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
      setMode(initialMode())
      setStarterIndex(0)
      setShelf('hook')
      resetFilters()
      setPlaying(null)
    }
    window.addEventListener('popstate', followFormat)
    return () => {
      desktop.removeEventListener('change', onDesktop)
      window.removeEventListener('popstate', followFormat)
      if (copyTimer.current !== undefined) window.clearTimeout(copyTimer.current)
    }
  }, [])

  const selected = useMemo(() => new Set(edit.items.map(item => item.id)), [edit.items])
  const activeGuide = guide[mode]
  const spotlight = byId.get(activeGuide.spotlight)
  const starterList = starters[mode]
  const starter = starterList[starterIndex]
  const missingSteps = starter.steps.filter(step => !selected.has(step.id))
  const collections = formatCollections[mode]
  const stageCollections = collections.filter(group => group.stage === shelf)
  const options = shelf === 'techniques'
    ? sections.map(section => ({ id: section.name, title: section.label }))
    : stageCollections.map(group => ({ id: group.id, title: group.title }))
  const counts = Object.fromEntries(stages[mode].map(stage => [
    stage, collections.filter(group => group.stage === stage).reduce((total, group) => total + group.items.length, 0),
  ]))
  const queryTerms = searchable(query).split(' ').filter(Boolean)
  const entries = shelf === 'techniques'
    ? techniques.filter(item => !collection || item.section === collection)
    : stageCollections.filter(group => !collection || group.id === collection).flatMap(group => group.items)
  const visible = entries.filter(item =>
    (!onlySelected || selected.has(item.id)) &&
    (!media || withSound(item) === (media === 'sound')) &&
    queryTerms.every(word => searchable(`${item.title} ${item.useCase ?? ''} ${item.section} ${item.prompt}`).includes(word))
  )
  const pageCount = Math.max(1, Math.ceil(visible.length / pageSize))
  const effectivePage = Math.min(page, pageCount)
  const start = (effectivePage - 1) * pageSize
  const pageItems = visible.slice(start, start + pageSize)

  function resetFilters() {
    setQuery('')
    setCollection('')
    setMedia('')
    setOnlySelected(false)
    setPage(1)
  }

  function chooseMode(next: FormatMode) {
    if (next === mode) return
    window.history.pushState(null, '', next === 'long' ? '#long-form' : '#reels-shorts')
    setMode(next)
    setShelf('hook')
    setStarterIndex(0)
    resetFilters()
    setPlaying(null)
    window.scrollTo({ top: 0 })
  }

  function chooseShelf(next: Shelf, reveal = false) {
    setShelf(next)
    resetFilters()
    setPlaying(null)
    if (reveal) revealLibrary()
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
      setMessage(key === 'combined' ? 'Combined prompt copied.' : 'Technique prompt copied.')
      copyTimer.current = window.setTimeout(() => setCopied(null), 1800)
    } catch {
      setError(key === 'combined' ? 'Copy failed. Open Combined prompt to select and copy the text.' : 'Copy failed. Expand the prompt to select and copy the text.')
    }
  }

  function nextPage(next: number) {
    setPage(next)
    setPlaying(null)
    revealLibrary()
  }

  const builderProps = { edit, setEdit, copied: copied === 'combined', onCopy: (text: string) => { void copy('combined', text) } }
  const shelfName = shelf === 'techniques' ? 'Technique library' : stageLabels[shelf]
  const libraryTitle = shelf === 'techniques' ? shelfName : `${modes[mode].label} ${shelfName.toLowerCase()}`

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
              <button className="button hero-action" type="button" onClick={() => chooseShelf('hook', true)}>
                Explore {counts.hook || ''} hooks <ArrowDown size={16} aria-hidden="true" />
              </button>
              <div className="hero-links">
                {mode === 'long' && <button type="button" className="hero-secondary" onClick={() => chooseShelf('intro', true)}>Intros</button>}
                <button type="button" className="hero-secondary" onClick={() => chooseShelf('body', true)}>Editing styles</button>
                <button type="button" className="hero-secondary" onClick={() => chooseShelf('finish', true)}>
                  Finishes <ArrowRight size={14} aria-hidden="true" />
                </button>
              </div>
            </div>
          </div>
          {spotlight && <figure className="hero-spotlight">
            <Preview key={spotlight.id} technique={spotlight} playing={playing === 'hero'} playbackId="hero"
              priority onPlay={updatePlayback} />
            <figcaption>{activeGuide.focus} <span>Hover or tap to play</span></figcaption>
          </figure>}
        </section>

        <section className="starter-strip" aria-label="Starter workflows">
          <div className="starter-choice">
            <h2>Start with a workflow</h2>
            <div className="starter-options" role="group" aria-label="Starter workflow">
              {starterList.map((option, index) => (
                <button type="button" className="button secondary" key={option.title}
                  aria-pressed={starterIndex === index} onClick={() => setStarterIndex(index)}>
                  {option.title}
                </button>
              ))}
            </div>
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
        </section>

        <div className="workspace">
          <section className="library" id="recipe-library" ref={library} tabIndex={-1} aria-labelledby="library-title">
            <nav className="shelf-nav" aria-label="Edit stages">
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
            </div>
            <div className="filters" aria-label="Filter recipes">
              <div className="search-field">
                <Search size={18} aria-hidden="true" />
                <input type="search" aria-label="Search recipes" placeholder={`Search ${shelfName.toLowerCase()}…`} value={query}
                  onChange={event => { setQuery(event.target.value); setPage(1); setPlaying(null) }} />
                {query && <button className="icon-button" type="button" aria-label="Clear search" onClick={() => { setQuery(''); setPage(1) }}><X size={17} /></button>}
              </div>
              <div className="select-wrap collection-select">
                <select aria-label="Filter by collection" value={collection}
                  onChange={event => { setCollection(event.target.value); setPage(1); setPlaying(null) }}>
                  <option value="">All collections</option>
                  {options.map(option => <option value={option.id} key={option.id}>{option.title}</option>)}
                </select>
                <ChevronDown size={16} aria-hidden="true" />
              </div>
            </div>
            <div className="library-meta">
              <p className="result-count" aria-live="polite">
                {visible.length ? `${start + 1}–${start + pageItems.length} of ${visible.length} ${shelf === 'techniques' ? 'techniques' : 'recipes'}` : '0 results'}
              </p>
              <div className="filter-options">
                <div className="select-wrap">
                  <select value={media} aria-label="Filter by preview audio"
                    onChange={event => { setMedia(event.target.value); setPage(1); setPlaying(null) }}>
                    <option value="">All previews</option><option value="visual">Visual only</option><option value="sound">With sound</option>
                  </select>
                  <ChevronDown size={15} aria-hidden="true" />
                </div>
                <label className="selected-filter">
                  <input type="checkbox" checked={onlySelected} onChange={event => { setOnlySelected(event.target.checked); setPage(1); setPlaying(null) }} /> Selected only
                </label>
              </div>
            </div>

            {pageItems.length ? <div className="technique-grid">
              {pageItems.map(technique => (
                <TechniqueCard key={technique.id} technique={technique} selected={selected.has(technique.id)}
                  copied={copied === technique.id} playing={playing === technique.id} onPlay={updatePlayback}
                  onSelect={() => changeSelection(technique.id)} onCopy={() => { void copy(technique.id, technique.prompt) }} />
              ))}
            </div> : <div className="no-results">
              <Search size={24} strokeWidth={1.5} /><h3>No matching recipes</h3>
              <p>Try a different search or clear your filters.</p>
              <button type="button" className="button secondary" onClick={resetFilters}>Clear filters</button>
            </div>}

            {pageCount > 1 && <nav className="pagination" aria-label="Recipe pages">
              <button className="button secondary" type="button" disabled={effectivePage === 1} onClick={() => nextPage(effectivePage - 1)}>
                <ChevronLeft size={17} /> Previous
              </button>
              <span>Page {effectivePage} of {pageCount}</span>
              <button className="button secondary" type="button" disabled={effectivePage === pageCount} onClick={() => nextPage(effectivePage + 1)}>
                Next <ChevronRight size={17} />
              </button>
            </nav>}
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
