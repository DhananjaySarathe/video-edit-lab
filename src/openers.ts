import type { FormatMode } from './catalog'

/** One line of a pasted transcript, with where it starts when the transcript has timestamps. */
export type Segment = { stamp: string; seconds?: number; text: string }

type Kind = 'test' | 'result' | 'promise' | 'story' | 'confession' | 'challenge' | 'mistake' | 'contrarian' | 'myth'
  | 'cost' | 'number' | 'who' | 'question' | 'statement'

export type OpenerSuggestion = {
  text: string
  stamp: string
  seconds?: number
  kind: Kind
  typeId: string
  reasons: string[]
  footage: string
  score: number
}

const TIME = String.raw`(\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?`

function toSeconds(stamp: string) {
  const parts = stamp.replace(',', '.').split(':').map(Number)
  return parts.reduce((total, part) => total * 60 + part, 0)
}

function shortStamp(stamp: string) {
  const seconds = Math.floor(toSeconds(stamp))
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
}

/** Read SRT, VTT, "00:08 text" lines, or plain text. */
export function parseTranscript(raw: string): Segment[] {
  const text = raw.replace(/\r/g, '').trim()
  if (!text) return []
  const segments: Segment[] = []
  if (/-->/.test(text)) {
    for (const block of text.split(/\n\s*\n/)) {
      const lines = block.split('\n').map(line => line.trim()).filter(Boolean)
      const at = lines.findIndex(line => line.includes('-->'))
      if (at < 0) continue
      const start = lines[at].split('-->')[0].trim()
      const words = lines.slice(at + 1).join(' ').replace(/<[^>]+>/g, '').trim()
      if (words && new RegExp(`^${TIME}$`).test(start)) segments.push({ stamp: shortStamp(start), seconds: toSeconds(start), text: words })
    }
    return segments
  }
  const stamped = new RegExp(`^\\[?(${TIME})\\]?\\s*[-–:]?\\s*(.+)$`)
  const lines = text.split('\n').map(line => line.trim()).filter(Boolean)
  if (lines.some(line => stamped.test(line))) {
    for (const line of lines) {
      const match = line.match(stamped)
      if (match) segments.push({ stamp: shortStamp(match[1]), seconds: toSeconds(match[1]), text: match[3].trim() })
      else if (segments.length) segments[segments.length - 1].text += ` ${line}`
    }
    return segments
  }
  return text.split(/(?<=[.!?])\s+/).map(sentence => ({ stamp: '', text: sentence.trim() })).filter(segment => segment.text)
}

const NUMBER_WORDS = /\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|hundred|thousand|million|half|double|twice)\b/i
const LEADING_FILLER = /^((so|okay|ok|um+|uh+|and|oh|well|right|alright|like|yeah)\b[,.]?\s+)+/i
const WARM_UP = /^(hi|hey|hello|welcome|what's up|today (i|we)|in (this|today's) video|this video is|let's (talk|get started|begin|start)|before we (start|begin)|so today)\b/i
const ASIDE = /(let me start again|start over|one more time|sorry|where was i|hold on|wait,|my cat|can you hear|is this recording)/i
const FILLERS = /\b(um+|uh+|you know|kind of|sort of|basically)\b/gi
const HEDGES = /\b(i think|maybe|probably|i guess|i feel like)\b/gi

const PATTERNS: readonly [Kind, RegExp, number, string][] = [
  ['test', /\bi (tried|tested|checked|compared|asked|timed|ran|spent)\b/i, 4, 'Starts a test'],
  ['result', /\b(i (paid off|built|made|got|grew|went from|doubled|tripled|saved|finished|sold|hit|cut|plan|edit)|took me|takes me|now i)\b/i, 4, 'Leads with a result'],
  ['promise', /\b(by the end of (this|the) video|you'll (have|be able|know|see))\b/i, 3, 'Makes a clear promise'],
  ['story', /^(\w+ (days?|weeks?|months?|years?) (before|ago|later)|last (night|week|month|year)|the day (i|we|my)|on my first day|i was (halfway|about to|in the middle))\b/i, 4, 'Drops into a moment'],
  ['confession', /\bfor (about |almost |over |nearly )?(\w+) (years|months|weeks),? i\b/i, 4, 'Admits something that took a while'],
  ['challenge', /\b(i have (one|two|three|\d+|a|only) \w+ to|can i |in (one|a single|\d+) (hour|day|week)s?)\b/i, 3, 'Sets a challenge'],
  ['mistake', /^(if (you|your)\b|you('re| are) (doing|making|using|filming|posting|editing)|most people)/i, 4, 'Calls out a habit'],
  ['contrarian', /^(stop|don't|never|forget|quit)\b|\b(overrated|is wrong|are wrong|doesn't work)\b/i, 4, 'Takes a clear position'],
  ['myth', /\b(you don't (need|have to)|isn't (true|the problem)|aren't the|is a myth)\b/i, 3, 'Corrects a belief'],
  ['cost', /\b(costs?|costing|wast(e|es|ed|ing)|losing|lost me|ate my)\b/i, 2, 'Puts a price on it'],
  ['number', /^(\d+|one|two|three|four|five|six|seven|eight|nine|ten) (things|ways|cuts|tips|mistakes|reasons|steps|tools|apps|settings|places|habits)\b/i, 4, 'Promises a number'],
  ['who', /^(if you're a|if you are a|anyone who|for anyone)\b/i, 3, 'Names who it’s for'],
  ['question', /\?\s*$/, 2, 'Asks a question'],
]

const TYPE_FOR: Record<FormatMode, Record<Kind, string>> = {
  short: {
    test: 'test', result: 'result-first', promise: 'result-first', story: 'story-cold-open', confession: 'story-cold-open',
    challenge: 'test', mistake: 'mistake', contrarian: 'contrarian', myth: 'myth', cost: 'cost', number: 'number-list',
    who: 'who-its-for', question: 'myth', statement: 'show-first',
  },
  long: {
    test: 'tested', result: 'promise-proof', promise: 'promise-proof', story: 'cold-open-peak', confession: 'confession',
    challenge: 'challenge', mistake: 'mistakes-preview', contrarian: 'contrarian-thesis', myth: 'contrarian-thesis',
    cost: 'contrarian-thesis', number: 'mistakes-preview', who: 'promise-proof', question: 'big-question', statement: 'promise-proof',
  },
}

const FOOTAGE: Record<Kind, string> = {
  test: 'The test itself: the setup and the result, side by side if you can.',
  result: 'The finished result in the first frame, on screen or in your hands.',
  promise: 'The finished result first, then your face making the promise.',
  story: 'A tight shot of your face, plus a photo or clip of the moment.',
  confession: 'Your face, close, then a photo or clip of the old way.',
  challenge: 'The clock or budget on screen, and where you’re starting from.',
  mistake: 'Your face, plus the mistake on screen: the setting, the screenshot or the problem.',
  contrarian: 'Your face, close. A strong opinion lands on eye contact more than B-roll.',
  myth: 'Your face, plus one clip or screenshot that proves the correction.',
  cost: 'A receipt for the cost: a timer, a bill, a calendar or the number on screen.',
  number: 'Your face with a counter, and one shot for each item.',
  who: 'A shot the person you’re naming would recognise straight away.',
  question: 'The puzzle on screen: the thing that makes people ask.',
  statement: 'Your face, close, with the key words on screen.',
}

function score(raw: string) {
  const trimmed = raw.replace(LEADING_FILLER, '').replace(/^[a-z]/, letter => letter.toUpperCase())
  const reasons: string[] = []
  if (ASIDE.test(raw) || WARM_UP.test(trimmed)) return undefined
  const words = trimmed.split(/\s+/).filter(Boolean)
  if (words.length < 5 || words.length > 32) return undefined
  let points = 0
  let kind: Kind = 'statement'
  let best = 0
  for (const [name, pattern, weight, reason] of PATTERNS) {
    if (!pattern.test(trimmed)) continue
    points += weight
    if (weight > best) {
      best = weight
      kind = name
      reasons.unshift(reason)
    } else if (reasons.length < 3) {
      reasons.push(reason)
    }
  }
  if (/\d/.test(trimmed) || NUMBER_WORDS.test(trimmed)) {
    points += 2
    reasons.push('Has a specific number')
  }
  if (/\b(you|your)\b/i.test(words.slice(0, 7).join(' '))) {
    points += 1
    if (kind !== 'mistake') reasons.push('Talks to the viewer')
  }
  if (words.length >= 7 && words.length <= 20) points += 2
  else if (words.length > 26) points -= 2
  points -= (trimmed.match(FILLERS)?.length ?? 0) + (trimmed.match(HEDGES)?.length ?? 0)
  if (trimmed !== raw.trim()) reasons.push(`Trims the opening “${raw.trim().split(/[\s,]+/)[0]}”`)
  return { text: trimmed, points, kind, reasons: [...new Set(reasons)].slice(0, 3) }
}

/** The strongest opening lines in a transcript, with the hook type each one fits. */
export function suggestOpeners(raw: string, mode: FormatMode, count = 3): OpenerSuggestion[] {
  const segments = parseTranscript(raw)
  const candidates: OpenerSuggestion[] = []
  segments.forEach(segment => {
    if (ASIDE.test(segment.text)) return
    const sentences = segment.text.split(/(?<=[.!?])\s+/).filter(Boolean)
    const options = new Set(sentences)
    if (sentences.length > 1 && segment.text.split(/\s+/).length <= 28) options.add(segment.text)
    for (const option of options) {
      const result = score(option)
      if (!result || result.points < 3) continue
      candidates.push({
        text: result.text,
        stamp: segment.stamp,
        seconds: segment.seconds,
        kind: result.kind,
        typeId: TYPE_FOR[mode][result.kind],
        reasons: result.reasons.length ? result.reasons : ['Short and concrete'],
        footage: FOOTAGE[result.kind],
        score: result.points,
      })
    }
  })
  candidates.sort((left, right) => right.score - left.score || (left.seconds ?? 0) - (right.seconds ?? 0))
  const chosen: OpenerSuggestion[] = []
  const overlaps = (a: string, b: string) => a.includes(b) || b.includes(a)
  // Prefer three different kinds of opening unless a same-kind line is clearly stronger.
  for (const candidate of candidates) {
    if (chosen.length >= count) break
    if (chosen.some(pick => overlaps(pick.text, candidate.text))) continue
    const sameKind = chosen.find(pick => pick.kind === candidate.kind)
    const alternative = candidates.find(other => other !== candidate && other.kind !== candidate.kind
      && !chosen.some(pick => pick.kind === other.kind || overlaps(pick.text, other.text)) && candidate.score - other.score <= 2)
    if (sameKind && alternative) continue
    chosen.push(candidate)
  }
  return chosen
}
