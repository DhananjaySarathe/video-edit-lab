import type { FormatMode, Stage } from './catalog'

export type Breakdown = {
  id: string
  mode: FormatMode
  stage: Stage
  title: string
  useCase: string
  previewId: string
  previewLabel?: string
  previewKind?: 'worked' | 'storyboard'
  duration?: number
  footageGroup?: string
  sound?: boolean
  soundDirection?: string
  opener?: string
  observation?: string
  footage?: string
  beats: readonly (readonly [cue: string, edit: string])[]
  skipWhen?: string
  check: string
  prompt: string
}
