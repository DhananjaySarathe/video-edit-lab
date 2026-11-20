import { Pause, Play, Volume2 } from 'lucide-react'
import { useCallback, useEffect, useRef, useState, type PointerEvent } from 'react'
import { mediaUrl, withSound, type Technique } from './catalog'

export type PreviewProps = {
  technique: Technique
  playing: boolean
  onPlay: (id: string, playing: boolean) => void
}

export function Preview({ technique, playing, onPlay, playbackId = technique.id, priority = false }:
PreviewProps & { playbackId?: string; priority?: boolean }) {
  const video = useRef<HTMLVideoElement>(null)
  const mode = useRef<'hover' | 'manual' | null>(null)
  const attempt = useRef(0)
  const [showVideo, setShowVideo] = useState(false)
  const [error, setError] = useState(false)
  const hasSound = withSound(technique)

  const stop = useCallback(() => {
    attempt.current += 1
    mode.current = null
    video.current?.pause()
    setShowVideo(false)
    onPlay(playbackId, false)
  }, [onPlay, playbackId])

  useEffect(() => {
    const player = video.current
    return () => {
      attempt.current += 1
      player?.pause()
    }
  }, [])

  useEffect(() => {
    if (!playing) {
      attempt.current += 1
      mode.current = null
      video.current?.pause()
      setShowVideo(false)
    }
  }, [playing])

  useEffect(() => {
    if (!playing || !video.current) return
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.intersectionRatio < 0.25)) stop()
    }, { threshold: 0.25 })
    observer.observe(video.current)
    const onVisibility = () => { if (document.hidden) stop() }
    document.addEventListener('visibilitychange', onVisibility)
    return () => {
      observer.disconnect()
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [playing, stop])

  async function playPreview(nextMode: 'hover' | 'manual') {
    const player = video.current
    if (!player) return
    const request = ++attempt.current
    const resumeFromHover = mode.current === 'hover' && nextMode === 'manual' && !player.paused
    mode.current = nextMode
    setError(false)
    if (!player.getAttribute('src') || player.error) {
      player.src = mediaUrl(technique.previewId ?? technique.id, 'mp4')
    }
    player.muted = nextMode === 'hover' || !hasSound
    if (!resumeFromHover && player.readyState > 0) player.currentTime = 0
    onPlay(playbackId, true)
    try {
      await player.play()
    } catch (reason) {
      if (request !== attempt.current || (reason instanceof DOMException && reason.name === 'AbortError')) return
      setError(true)
      stop()
    }
  }

  function hoverPreview(event: PointerEvent<HTMLDivElement>) {
    if (event.pointerType === 'mouse' && !mode.current
      && window.matchMedia('(any-hover: hover) and (prefers-reduced-motion: no-preference)').matches) {
      void playPreview('hover')
    }
  }

  return (
      <div className={`preview${priority ? ' spotlight-preview' : ''}`} onPointerEnter={hoverPreview}
        onPointerLeave={() => { if (mode.current === 'hover') stop() }}>
        <img src={mediaUrl(technique.previewId ?? technique.id, 'webp')} alt="" width="640" height="360" loading={priority ? 'eager' : 'lazy'} decoding="async" />
        <video ref={video} className={showVideo ? 'is-playing' : ''} preload="none" playsInline
          aria-hidden="true" onPlaying={() => { if (mode.current) setShowVideo(true) }} onEnded={stop} />
        <button type="button" className="preview-toggle"
          aria-label={`${playing ? 'Pause' : 'Play'} preview for ${technique.title}`}
          onClick={() => { if (playing) stop(); else void playPreview('manual') }}>
          <span className="play-bubble">{playing ? <Pause size={17} /> : <Play size={17} />}</span>
        </button>
        {hasSound && <button type="button" className="sound-badge" aria-label={`Play ${technique.title} with sound`}
          onClick={() => void playPreview('manual')}><Volume2 size={15} /> Sound</button>}
        {error && <span className="preview-error" role="status">Preview couldn't load. Try again.</span>}
      </div>
  )
}
