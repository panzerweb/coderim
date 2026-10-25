import { test,expect,type Page } from '@playwright/test'
import fs from 'node:fs'
const formatterSource=fs.readFileSync('../problems/broken-code-formatter/author/reference.py','utf8')

async function teamNavigation(page:Page,name:string){
  const nav=page.getByRole('navigation',{name:'Main navigation'})
  await expect(nav.getByRole('link',{name,exact:true})).toBeVisible()
  await expect(nav.getByRole('link',{name:'History',exact:true})).toBeVisible()
  await expect(nav.getByRole('button',{name:'Log out',exact:true})).toBeVisible()
  await expect(nav.getByRole('link',{name:'Organizer',exact:true})).toHaveCount(0)
}
async function refreshTeamNavigation(page:Page,name:string){
  let release!:()=>void
  let intercepted!:()=>void
  let continued!:()=>void
  let held=false
  const pending=new Promise<void>(resolve=>{release=resolve})
  const requested=new Promise<void>(resolve=>{intercepted=resolve})
  const handled=new Promise<void>(resolve=>{continued=resolve})
  const handler=async(route:import('@playwright/test').Route)=>{
    held=true;intercepted();await pending
    try{await route.continue()}finally{continued()}
  }
  await page.route('**/api/teams/me',handler,{times:1})
  try{
    await page.reload({waitUntil:'domcontentloaded'})
    await requested
    await expect(page.getByRole('link',{name:'Code Relay home'})).toBeVisible()
    await expect(page.getByRole('navigation',{name:'Main navigation'}).locator('.local-tag')).toHaveCount(0)
    await expect(page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Organizer',exact:true})).toHaveCount(0)
  }finally{
    release();if(held)await handled
    await page.unroute('**/api/teams/me',handler)
  }
  await teamNavigation(page,name)
}
async function organizer(page:Page){
  await page.goto('/organizer/login')
  await page.getByLabel('Organizer username',{exact:true}).fill('test-organizer')
  await page.getByLabel('Organizer password',{exact:true}).fill('browser-test-password')
  await page.getByRole('button',{name:'Sign in as organizer',exact:true}).click()
  await expect(page.getByRole('heading',{name:'Run the relay.'})).toBeVisible()
  await expect(page.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Organizer',exact:true})).toBeVisible()
  // The heading renders before the console's async catalog/session load finishes.
  await expect(page.locator('#event-start')).not.toHaveValue('')
}
async function createTeam(page:Page,name:string){
  await page.getByLabel('Team name',{exact:true}).fill(name)
  await page.getByRole('button',{name:'Create team',exact:true}).click()
  await expect(page.locator('.one-time-code')).toContainText(name)
  const code=await page.locator('.one-time-code code').innerText()
  await page.getByRole('button',{name:'Hide code',exact:true}).click()
  return code
}
async function join(page:Page,contest:string,name:string,code:string){
  await page.goto('/join');await page.getByLabel('Contest',{exact:true}).selectOption({label:contest})
  await page.getByLabel('Team name',{exact:true}).fill(name);await page.getByLabel('Join code',{exact:true}).fill(code)
  await page.getByRole('button',{name:'Join team',exact:true}).click();await expect(page).toHaveURL(/\/dashboard$/)
  await teamNavigation(page,name)
}
async function draft(page:Page,source:string){
  await page.getByTestId('code-editor').locator('.monaco-editor').waitFor()
  await page.context().grantPermissions(['clipboard-read','clipboard-write'])
  await page.evaluate(value=>navigator.clipboard.writeText(value),source)
  await page.getByTestId('code-editor').click({position:{x:250,y:100}})
  await page.keyboard.press('ControlOrMeta+A');await page.keyboard.press('ControlOrMeta+V')
}
test('organizer publishes, teams wait, record privately, preserve drafts, receive reviews, and retain ended history',async({browser,page:admin})=>{
  const errors:string[]=[];admin.on('pageerror',e=>errors.push(e.message))
  await organizer(admin)
  const name=`Browser relay ${Date.now()}`
  await admin.getByLabel('Contest name',{exact:true}).fill(name)
  await expect(admin.getByLabel('Hours',{exact:true})).toHaveValue('3')
  await expect(admin.getByLabel('Minutes',{exact:true})).toHaveValue('30')
  await admin.getByRole('button',{name:'Create contest',exact:true}).click()
  // This regression intentionally pins only the original three challenges.
  for(const id of ['add-two-numbers','longest-rising-streak','most-frequent-reading','palindrome-check','g-tree-ancestor-query','shortest-grid-route','longest-unique-segment']){
    await admin.locator(`.problem-check input[value="${id}"]`).uncheck()
  }
  admin.once('dialog',d=>d.accept());await admin.getByRole('button',{name:'Publish contest',exact:true}).click()
  await expect(admin.getByRole('status')).toContainText('Contest published')
  const alpha=await createTeam(admin,'Alpha'),beta=await createTeam(admin,'Beta')
  const aContext=await browser.newContext(),bContext=await browser.newContext()
  const a=await aContext.newPage(),b=await bContext.newPage()
  a.on('pageerror',e=>errors.push(e.message));b.on('pageerror',e=>errors.push(e.message))
  await join(a,`${name} · waiting`,'Alpha',alpha)
  await expect(a.getByText('Problems will be revealed',{exact:false})).toBeVisible()
  await a.goto('/problems');await expect(a).toHaveURL(/\/dashboard$/)
  // Organizer starts the full configured duration immediately.
  await expect(admin.getByText('No provider account is needed.',{exact:false})).toBeVisible()
  admin.once('dialog',d=>d.accept());await admin.getByRole('button',{name:'Start contest now',exact:true}).click()
  await expect(admin.getByRole('status')).toContainText('Contest started')
  await a.reload();await expect(a.getByRole('link',{name:'Problem library ↗',exact:true})).toBeVisible()
  await teamNavigation(a,'Alpha')
  await a.goto('/problems');await expect(a.locator('.problem-row')).toHaveCount(3)
  await teamNavigation(a,'Alpha')
  await a.goto('/');await teamNavigation(a,'Alpha')
  await refreshTeamNavigation(a,'Alpha')
  await join(b,`${name} · active`,'Beta',beta)
  await a.goto('/problems/broken-code-formatter');await draft(a,formatterSource)
  await teamNavigation(a,'Alpha')
  // Default dialog dismissal cancels recording and creates no attempt.
  await a.getByRole('button',{name:'Record Submission',exact:true}).click()
  expect(await a.request.get('/api/submissions/me').then(r=>r.json())).toEqual([])
  // Lose the response after admission, then retry the frozen source/key.
  await a.route('**/api/submissions',async route=>{await route.fetch();await route.abort()},{times:1})
  a.once('dialog',d=>d.accept());await a.getByRole('button',{name:'Record Submission',exact:true}).click()
  await expect(a.getByRole('button',{name:'Retry pending recording',exact:true})).toBeVisible()
  await draft(a,'WRONG')
  await a.reload()
  await a.getByRole('button',{name:'Retry pending recording',exact:true}).click()
  await expect(a.getByText('65 passed · 65 attempted / 65 total',{exact:true})).toBeVisible({timeout:45_000})
  await draft(a,formatterSource)
  const saved=await a.request.get('/api/submissions/me').then(r=>r.json())
  expect(saved).toHaveLength(1)
  // A persisted interrupted poll must release the editor after a restart.
  const identity=await a.request.get('/api/teams/me').then(r=>r.json())
  const jobKey=`code-relay:job:contest:${identity.contest_id}:team:${identity.team_id}:broken-code-formatter:v1:python`
  await a.route(`**/api/jobs/${saved[0].id}`,route=>route.fulfill({json:{
    id:saved[0].id,state:'interrupted',attempt_id:saved[0].id,
    result:{mode:'submit',verdict:'Judge Error',attempted:0,passed:0,total:65,duration_ms:0,cases:[],assessment:null,diagnostics:'',incomplete_reason:'Backend restarted before judging completed'},
  }}),{times:1})
  await a.evaluate(({key,id})=>sessionStorage.setItem(key,id),{key:jobKey,id:saved[0].id})
  await a.reload()
  await expect(a.getByLabel('Judge results').getByText('Judge Error',{exact:true}).first()).toBeVisible()
  await expect(a.getByRole('button',{name:'Record Submission',exact:true})).toBeEnabled()
  expect(await a.evaluate(key=>sessionStorage.getItem(key),jobKey)).toBeNull()
  expect((await b.request.get(`/api/attempts/${saved[0].id}`)).status()).toBe(404)
  await b.goto('/history');await expect(b.getByText('No official submissions on this page.')).toBeVisible()
  await a.goto('/history');await a.locator('.global-history button').first().click()
  await teamNavigation(a,'Alpha')
  await expect(a.locator('.source-snapshot')).toHaveText(formatterSource)
  await expect(a.getByRole('heading',{name:'Organizer code review'})).toHaveCount(0)
  await admin.getByRole('button',{name:'Refresh console',exact:true}).click()
  await admin.getByLabel('Team submissions',{exact:true}).selectOption({label:'Beta'})
  await expect(admin.locator('.organizer-submissions .attempt-list button')).toHaveCount(0)
  await admin.getByLabel('Team submissions',{exact:true}).selectOption({label:'Alpha'})
  await expect(admin.locator('.organizer-submissions .attempt-list button')).toHaveCount(1)
  await admin.locator('.organizer-submissions .attempt-list button').first().click()
  await expect(admin.locator('.review-form fieldset:not(.complexity-form) select')).toHaveCount(8)
  for(const select of await admin.locator('.review-form fieldset:not(.complexity-form) select').all())await select.selectOption('4')
  await admin.getByLabel('Analysis status',{exact:true}).selectOption('unable_to_assess')
  await admin.getByLabel('Complexity reasoning',{exact:true}).fill('This review deliberately leaves the complexity bound unassessed.')
  await admin.getByLabel('Review rationale',{exact:true}).fill('Browser test review of the immutable snapshot.')
  await admin.getByRole('button',{name:'Save organizer review',exact:true}).click()
  await expect(admin.getByRole('status')).toContainText('Organizer review saved')
  await a.reload();await a.locator('.global-history button').first().click()
  await expect(a.getByLabel('Reviewed complexity',{exact:true})).toContainText('Unable to assess')
  // Logout clears memory, but a returning team's namespaced draft remains.
  await a.getByRole('button',{name:'Log out',exact:true}).click()
  const betaRow=admin.locator('.team-management').filter({hasText:'Beta'})
  admin.once('dialog',d=>d.accept());await betaRow.getByRole('button',{name:'Reset session',exact:true}).click()
  await join(a,`${name} · active`,'Beta',beta)
  await a.goto('/problems/broken-code-formatter')
  await expect(a.getByTestId('code-editor').locator('.monaco-editor')).toBeVisible()
  expect(await a.getByTestId('code-editor').innerText()).not.toContain('def validate(')
  await a.getByRole('button',{name:'Log out',exact:true}).click()
  await join(a,`${name} · active`,'Alpha',alpha)
  await a.goto('/problems/broken-code-formatter')
  await expect(a.getByTestId('code-editor')).toContainText('def validate(')
  for(const id of ['longest-rising-streak-updates','g-tree-changing-root']){
    const source=fs.readFileSync(`../problems/${id}/author/reference.py`,'utf8')
    await a.goto('/problems/'+id);await draft(a,source)
    a.once('dialog',d=>d.accept());await a.getByRole('button',{name:'Record Submission',exact:true}).click()
    await expect(a.getByLabel('Judge results').getByText('Accepted',{exact:true}).first()).toBeVisible({timeout:45_000})
  }
  await a.goto('/dashboard');await expect(a.locator('.metric-row article').first()).toContainText('3')
  await teamNavigation(a,'Alpha')
  await admin.screenshot({path:'../.runtime/qa-organizer-contest.png',fullPage:true})
  admin.once('dialog',d=>d.accept());await admin.getByRole('button',{name:'End contest now',exact:true}).click()
  await a.reload();await expect(a.getByText('The contest has ended.',{exact:false})).toBeVisible()
  await teamNavigation(a,'Alpha')
  await a.goto('/problems/broken-code-formatter');await expect(a.getByRole('button',{name:'Record Submission',exact:true})).toBeDisabled()
  await teamNavigation(a,'Alpha')
  await a.goto('/history');await expect(a.locator('.global-history button')).toHaveCount(3)
  await teamNavigation(a,'Alpha')
  await a.screenshot({path:'../.runtime/qa-team-history.png',fullPage:true})
  // Both cookies may exist in one browser; the active interface controls the link.
  await organizer(a)
  await a.getByRole('link',{name:'Code Relay home'}).click()
  await teamNavigation(a,'Alpha')
  await refreshTeamNavigation(a,'Alpha')
  await a.goto('/dashboard');await teamNavigation(a,'Alpha')
  await a.goto('/organizer')
  await expect(a.getByRole('heading',{name:'Run the relay.'})).toBeVisible()
  await expect(a.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Organizer',exact:true})).toBeVisible()
  await a.getByRole('button',{name:'Log out',exact:true}).click()
  await expect(a).toHaveURL(/\/organizer\/login$/)
  await a.goto('/dashboard');await teamNavigation(a,'Alpha')
  await a.getByRole('button',{name:'Log out',exact:true}).click()
  await expect(a).toHaveURL(/\/join$/)
  await expect(a.getByRole('navigation',{name:'Main navigation'}).getByRole('link',{name:'Organizer',exact:true})).toBeVisible()
  await a.goto('/organizer/login')
  await expect(a.getByRole('button',{name:'Sign in as organizer',exact:true})).toBeVisible()
  expect(errors).toEqual([])
  await aContext.close();await bContext.close()
})

test('organizer selects seven introductory problems and reviews a team testing submission',async({browser,page:admin})=>{
  test.setTimeout(240_000)
  const ids=['add-two-numbers','longest-rising-streak','most-frequent-reading','palindrome-check','g-tree-ancestor-query','shortest-grid-route','longest-unique-segment']
  await organizer(admin)
  const name=`Introductory relay ${Date.now()}`
  await admin.getByLabel('Contest name',{exact:true}).fill(name)
  await admin.getByRole('button',{name:'Create contest',exact:true}).click()
  await expect(admin.locator('.problem-check input[type="checkbox"]')).toHaveCount(10)
  for(const id of ['broken-code-formatter','longest-rising-streak-updates','g-tree-changing-root']){
    await admin.locator(`.problem-check input[value="${id}"]`).uncheck()
  }
  admin.once('dialog',d=>d.accept());await admin.getByRole('button',{name:'Publish contest',exact:true}).click()
  await expect(admin.getByRole('status')).toContainText('Contest published')
  const code=await createTeam(admin,'Testing team')
  admin.once('dialog',d=>d.accept());await admin.getByRole('button',{name:'Start contest now',exact:true}).click()
  await expect(admin.getByRole('status')).toContainText('Contest started')
  const context=await browser.newContext(),team=await context.newPage()
  try{
    await join(team,`${name} · active`,'Testing team',code)
    await team.goto('/problems');await expect(team.locator('.problem-row')).toHaveCount(7)
    for(const id of ids){
      const source=fs.readFileSync(`../problems/${id}/author/reference.py`,'utf8')
      await team.goto('/problems/'+id);await draft(team,source)
      const run=team.getByRole('button',{name:'▷ Run Code',exact:true})
      await expect(run).toBeEnabled();await run.click()
      await expect(team.getByLabel('Judge results').getByText('Accepted',{exact:true}).first()).toBeVisible({timeout:45_000})
      await expect(team.getByText('3 passed · 3 attempted / 3 total',{exact:true})).toBeVisible()
      await teamNavigation(team,'Testing team')
    }
    await team.goto('/history');await expect(team.getByText('No official submissions on this page.')).toBeVisible()
    await team.goto('/problems/add-two-numbers')
    team.once('dialog',d=>d.dismiss());await team.getByRole('button',{name:'Record Submission',exact:true}).click()
    expect(await team.request.get('/api/submissions/me').then(r=>r.json())).toHaveLength(0)
    team.once('dialog',d=>d.accept());await team.getByRole('button',{name:'Record Submission',exact:true}).click()
    await expect(team.getByText('23 passed · 23 attempted / 23 total',{exact:true})).toBeVisible({timeout:45_000})
    const source=fs.readFileSync('../problems/add-two-numbers/author/reference.py','utf8')
    await admin.getByRole('button',{name:'Refresh console',exact:true}).click()
    await admin.locator('.organizer-submissions .attempt-list button').first().click()
    await expect(admin.locator('.source-snapshot')).toHaveText(source)
    for(const select of await admin.locator('.review-form fieldset:not(.complexity-form) select').all())await select.selectOption('4')
    await admin.getByLabel('Review rationale',{exact:true}).fill('Both operands are parsed and added correctly.')
    await admin.getByLabel('Analysis status',{exact:true}).selectOption('assessed')
    for(const label of ['Worst-case time','Auxiliary space','Space including stored input/output'])await admin.getByLabel(label,{exact:true}).fill('O(1)')
    await admin.getByLabel('Complexity reasoning',{exact:true}).fill('Only two bounded integers and their result are retained.')
    await admin.getByRole('button',{name:'Save organizer review',exact:true}).click()
    await expect(admin.getByRole('status')).toContainText('Organizer review saved')
    await team.goto('/history');await team.locator('.global-history button').first().click()
    await expect(team.locator('.source-snapshot')).toHaveText(source)
    await expect(team.getByLabel('Reviewed complexity',{exact:true})).toContainText('O(1)')
    await expect(team.locator('.attempt-detail .final-score strong')).toHaveText('100%')
    await team.reload();await team.locator('.global-history button').first().click()
    await expect(team.getByLabel('Reviewed complexity',{exact:true})).toContainText('Only two bounded integers')
  }finally{await context.close()}
})
