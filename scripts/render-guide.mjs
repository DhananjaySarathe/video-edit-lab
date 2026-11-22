// Renders the one-page guide to public/guide/video-edit-lab-guide.pdf and .png.
// It walks the "Build my prompt" flow in headless Chrome to take fresh screenshots, then prints scripts/guide/guide.html.
// Start the site first (npm run dev), then: npm run guide -- [site URL, default http://127.0.0.1:5179/]
// Set CHROME to the Chrome or Chromium binary if it isn't in the usual macOS place.
import { spawn } from 'node:child_process'
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const root = fileURLToPath(new URL('..', import.meta.url))
const site = process.argv[2] ?? 'http://127.0.0.1:5179/'
const shots = join(root, 'scripts/guide/shots')
const out = join(root, 'public/guide')
const chromePath = process.env.CHROME ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const scenarios = readFileSync(join(root, 'scripts/prompt-scenarios.mjs'), 'utf8')
const sample = name => scenarios.match(new RegExp(`export const ${name} = \`([^\`]+)\``))[1]
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

mkdirSync(shots, { recursive: true })
mkdirSync(out, { recursive: true })
const profile = mkdtempSync(join(tmpdir(), 'video-edit-lab-guide-'))
const port = 9300 + Math.floor(Math.random() * 500)
const chrome = spawn(chromePath, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--mute-audio', 'about:blank'], { stdio: 'ignore' })

try {
  for (let i = 0; i < 50; i++) {
    try { await fetch(`http://127.0.0.1:${port}/json/version`); break } catch { await sleep(200) }
  }
  const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json()
  const ws = new WebSocket(target.webSocketDebuggerUrl)
  await new Promise((resolve, reject) => { ws.addEventListener('open', resolve); ws.addEventListener('error', reject) })
  let id = 0
  const pending = new Map()
  ws.addEventListener('message', event => {
    const message = JSON.parse(event.data)
    pending.get(message.id)?.(message)
    pending.delete(message.id)
  })
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const n = ++id
    pending.set(n, message => message.error ? reject(new Error(`${method}: ${message.error.message}`)) : resolve(message.result))
    ws.send(JSON.stringify({ id: n, method, params }))
  })
  const run = async expression => {
    const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description ?? result.exceptionDetails.text)
    return result.result.value
  }
  // React only re-renders after the click's task ends, so each step waits before the next click.
  const click = async (selector, text = '') => {
    await run(`(() => { const el = [...document.querySelectorAll(${JSON.stringify(selector)})].find(el => el.textContent.includes(${JSON.stringify(text)}));
      if (!el) throw new Error('Not found: ${selector} ${text}'); el.click(); return true })()`)
    await sleep(350)
  }
  const type = async (selector, value) => {
    await run(`(() => { const el = document.querySelector(${JSON.stringify(selector)});
      const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, ${JSON.stringify(value)});
      el.dispatchEvent(new Event('input', { bubbles: true })); return true })()`)
    await sleep(350)
  }
  const capture = async (name, selector) => {
    await sleep(400)
    let clip
    if (selector) {
      const box = await run(`(() => { const r = document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height } })()`)
      clip = { ...box, scale: 1 }
    }
    const { data } = await send('Page.captureScreenshot', { format: 'png', ...(clip && { clip }) })
    writeFileSync(join(shots, `${name}.png`), Buffer.from(data, 'base64'))
  }
  const openFlow = async (mode, structure) => {
    await send('Page.navigate', { url: site })
    await sleep(3000)
    await click('button.hero-action')
    await click('.guided-format button', mode)
    await click('.guided-choice', structure)
  }
  const next = () => click('.guided-foot .button.primary')
  const scrollBody = to => run(`(() => { const body = document.querySelector('.guided-body'); body.scrollTop = ${to}; return true })()`)

  await send('Page.enable')
  await send('Runtime.enable')
  // A phone, short enough that each shot shows the step's header, the choice and the buttons.
  // The height matches the .phone frame in guide.html, so nothing gets cropped.
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 565, deviceScaleFactor: 2, mobile: true })

  await openFlow('Reels', 'Talking-head tip')
  await capture('1-kind')
  await next()
  await type('#guided-topic', 'Why your captions get covered')
  await type('#guided-transcript', sample('reelsTranscript'))
  await click('.opener-card .button')
  await run(`(() => { const body = document.querySelector('.guided-body'); const gap = document.querySelector('.openers').getBoundingClientRect().top - body.getBoundingClientRect().top; body.scrollTop += gap - 12; return true })()`)
  await capture('2-take')
  await next()
  await click('.guided-hook-group .guided-choice')
  await scrollBody(0)
  await capture('3-hook')
  await next()
  await scrollBody(0)
  await capture('4-prompt')

  // The guide itself: A4 at 96 px per inch, PNG at twice that.
  await send('Emulation.setDeviceMetricsOverride', { width: 794, height: 1123, deviceScaleFactor: 2, mobile: false })
  await send('Page.navigate', { url: pathToFileURL(join(root, 'scripts/guide/guide.html')).href })
  await sleep(800)
  await run('document.fonts.ready.then(() => Promise.all([...document.images].map(img => img.decode()))).then(() => true)')
  const overflow = await run('document.querySelector(".page").scrollHeight - document.querySelector(".page").clientHeight')
  if (overflow > 0) console.warn(`The guide runs ${overflow}px past one page. Trim the copy in scripts/guide/guide.html.`)
  const png = await send('Page.captureScreenshot', { format: 'png' })
  writeFileSync(join(out, 'video-edit-lab-guide.png'), Buffer.from(png.data, 'base64'))
  const pdf = await send('Page.printToPDF', { printBackground: true, preferCSSPageSize: true })
  writeFileSync(join(out, 'video-edit-lab-guide.pdf'), Buffer.from(pdf.data, 'base64'))
  console.log(`Wrote ${join('public/guide', 'video-edit-lab-guide.pdf')} and .png`)
  ws.close()
} finally {
  const exited = new Promise(resolve => chrome.once('exit', resolve))
  chrome.kill()
  await exited
  rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 })
}
