import { test, expect } from '@playwright/test'
import fs from 'node:fs'

async function submit(page: import('@playwright/test').Page, slug: string) {
  const code = fs.readFileSync(`../problems/${slug}/author/reference.py`, 'utf8')
  await page.goto(`/problems/${slug}`)
  await expect(page.getByRole('button', {name: 'Submit ↗', exact: true})).toBeEnabled()
  await page.evaluate(({slug, code}) => localStorage.setItem(`code-relay:draft:${slug}:v1:python`, code), {slug, code})
  await page.reload()
  await expect(page.getByRole('button', {name: 'Submit ↗', exact: true})).toBeEnabled()
  await page.getByRole('button', {name: 'Submit ↗', exact: true}).click()
  await expect(page.getByLabel('Judge results').getByText('Accepted', {exact: true}).first()).toBeVisible({timeout: 45_000})
}

test('both hard challenge flows and reviewer-only annotations', async ({page}) => {
  await page.goto('/problems')
  await expect(page.locator('.problem-row')).toHaveCount(10)
  await submit(page, 'longest-rising-streak-updates')
  await expect(page.getByText('28 passed · 28 attempted / 28 total', {exact: true})).toBeVisible()
  await expect(page.getByLabel('Reviewed complexity', {exact: true})).toContainText('Not assessed')
  await page.getByLabel('Reference complexity targets').getByText('Reference targets', {exact: false}).first().click()
  await expect(page.getByLabel('Reference complexity targets')).toContainText('O(log N)')
  await page.getByRole('button', {name: /Review this attempt’s code quality/}).click()
  await expect(page.getByRole('heading', {name: 'Human code review'})).toBeVisible()
  for (const select of await page.locator('.review-form fieldset:not(.complexity-form) select').all()) await select.selectOption('3')
  await page.getByLabel('Review rationale', {exact: true}).fill('Working solution. Assess efficiency from source reasoning separately.')
  await page.getByLabel('Analysis status', {exact: true}).selectOption('unable_to_assess')
  await page.getByLabel('Complexity reasoning', {exact: true}).fill('This test deliberately records uncertainty rather than copying the reference bounds.')
  await page.getByRole('button', {name: 'Save review', exact: true}).click()
  await expect(page.getByText('Review saved to this source snapshot.')).toBeVisible()
  await expect(page.getByLabel('Reviewed complexity', {exact: true})).toContainText('Unable to assess')
  await page.reload()
  await page.getByRole('tab', {name: /History & review/}).click()
  await page.locator('.attempt-list button').first().click()
  await expect(page.getByLabel('Analysis status', {exact: true})).toHaveValue('unable_to_assess')
  await expect(page.getByLabel('Complexity reasoning', {exact: true})).toHaveValue('This test deliberately records uncertainty rather than copying the reference bounds.')
  await page.getByLabel('Complexity analysis', {exact: true}).screenshot({path: '../.runtime/qa-complexity-panel.png'})
  await page.getByLabel('Analysis status', {exact: true}).scrollIntoViewIfNeeded()
  await page.screenshot({path: '../.runtime/qa-complexity-review.png', fullPage: true})
  await submit(page, 'g-tree-changing-root')
  await expect(page.getByText('23 passed · 23 attempted / 23 total', {exact: true})).toBeVisible()
  await expect(page.getByLabel('Reviewed complexity', {exact: true})).toContainText('Not assessed')
  await page.getByRole('button', {name: /Review this attempt’s code quality/}).click()
  await expect(page.getByLabel('Analysis status', {exact: true})).toHaveValue('not_assessed')
  await expect(page.getByLabel('Complexity reasoning', {exact: true})).toHaveCount(0)
})

test('historical attempts show missing context without borrowing the current reference', async ({page, request}) => {
  const response = await request.post('/api/submissions', {data: {problem_id: 'broken-code-formatter', problem_version: 1,
    language: 'javascript', code: 'console.log("INVALID")'}})
  const {attempt_id: id} = await response.json()
  await expect.poll(async () => (await (await request.get(`/api/jobs/${id}`)).json()).state).toBe('completed')
  const original = await (await request.get(`/api/attempts/${id}`)).json()
  // The storage migration is exercised by backend tests. These are its nullable
  // legacy DTO fields, isolated here to verify rendering of an old snapshot.
  const legacy = {...original, reference_complexity: null, review: null}
  await page.route('**/api/attempts?*', route => route.fulfill({json: [{...legacy, code: undefined}]}))
  await page.route(`**/api/attempts/${id}`, route => route.fulfill({json: legacy}))
  await page.addInitScript(() => localStorage.setItem('code-relay:language:broken-code-formatter', 'javascript'))
  await page.goto('/problems/broken-code-formatter')
  await page.getByRole('tab', {name: /History & review/}).click()
  await page.locator('.attempt-list button').first().click()
  await expect(page.getByLabel('Reviewed complexity', {exact: true})).toContainText('Not assessed')
  await page.getByLabel('Reference complexity targets').locator('summary').click()
  await expect(page.getByLabel('Reference complexity targets')).toContainText('No reference context was saved')
  await expect(page.getByLabel('Reference complexity targets')).not.toContainText('O(L)')
})
