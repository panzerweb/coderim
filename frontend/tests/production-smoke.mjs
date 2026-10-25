// Run against the built application started with scripts/start.ps1.
import assert from 'node:assert/strict'
import { chromium } from 'playwright'

const browser = await chromium.launch({headless: true})
try {
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}})
  const external = [], badResponses = [], errors = []
  await context.route('**/*', route => {
    const url = new URL(route.request().url())
    if (!['127.0.0.1', 'localhost'].includes(url.hostname)) {
      external.push(url.toString()); return route.abort()
    }
    return route.continue()
  })
  context.on('response', response => { if (response.status() >= 400) badResponses.push(`${response.status()} ${response.url()}`) })
  const page = await context.newPage()
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('http://127.0.0.1:8000/')
  await page.getByRole('link', {name: /Start practicing/}).click()
  await page.getByRole('link', {name: /The Broken Code Formatter/}).click()
  await page.getByRole('button', {name: 'Submit ↗', exact: true}).waitFor()
  await page.getByTestId('code-editor').locator('.monaco-editor').waitFor()
  // Check the backend's SPA fallback and locally served Monaco workers on reload.
  await page.reload()
  await page.getByTestId('code-editor').locator('.monaco-editor').waitFor()
  await page.getByTestId('code-editor').click({position: {x: 180, y: 50}})
  await page.keyboard.press('Control+End')
  await page.keyboard.type('# production edit')
  const saved = await page.evaluate(() => localStorage.getItem('code-relay:draft:broken-code-formatter:v1:python'))
  assert.ok(saved?.includes('# production edit'), 'Built Monaco must save edited drafts')
  await page.getByLabel('LANGUAGE', {exact: true}).selectOption('javascript')
  await page.getByTestId('code-editor').click({position: {x: 180, y: 50}})
  await page.keyboard.press('Control+End')
  await page.keyboard.type('// local worker check')
  const catalog = await (await page.request.get('http://127.0.0.1:8000/api/problems')).json()
  assert.equal(catalog.length, 10, 'All ten published challenges must be discoverable')
  for (const {id: slug} of catalog) {
    await page.goto(`http://127.0.0.1:8000/problems/${slug}`)
    await page.getByRole('button', {name: 'Submit ↗', exact: true}).waitFor()
    await page.getByTestId('code-editor').locator('.monaco-editor').waitFor()
  }
  await page.screenshot({path: '../.runtime/qa-production.png', fullPage: true})
  assert.deepEqual(external, [], 'Runtime must not request external assets')
  assert.deepEqual(badResponses, [], 'Built assets and routes must load')
  assert.deepEqual(errors, [], 'No browser runtime errors')
  console.log('Production smoke passed: all ten challenges, deep links, Monaco edits/workers, and local-only assets.')
} finally {
  await browser.close()
}
