<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { api, ApiError, draftKey } from '../api'
import type { Attempt, Job, Language, Problem, Result, ReviewedComplexity } from '../types'
import CodeEditor from '../components/CodeEditor.vue'
import JudgeResults from '../components/JudgeResults.vue'
import Trajectory from '../components/Trajectory.vue'
import ComplexityAnalysis from '../components/ComplexityAnalysis.vue'
import { clientState, workspaceScope } from '../clientState'
import { refreshTeam } from '../session'

const route = useRoute()
const problem = ref<Problem>()
const languages = ref<Language[]>([])
const language = ref('')
const code = ref('')
const customInput = ref('')
const custom = ref(false)
const loading = ref(true)
const error = ref('')
const storageWarning = ref('')
const busy = ref(false)
const state = ref('')
const result = ref<Result>()
const tab = ref<'results' | 'history'>('results')
const attempts = ref<Attempt[]>([])
const selected = ref<Attempt>()
const currentAttemptId = ref<string | null>(null)
const currentAttempt = ref<Attempt>()
const pendingRecord = ref<{key:string;payload:unknown}|null>(null)
const isHosted = computed(()=>clientState.mode==='contest')
const canExecute = computed(()=>!isHosted.value || clientState.team?.contest?.phase==='active')
const pendingKey = computed(()=>`code-relay:${workspaceScope()}:pending:${route.params.id}`)
const ratingsRead = ref<(number | null)[]>([null, null, null, null])
const ratingsTech = ref<(number | null)[]>([null, null, null, null])
const rationale = ref('')
const complexityStatus = ref<'not_assessed' | 'assessed' | 'unable_to_assess'>('not_assessed')
const complexityTime = ref('')
const complexityAuxiliary = ref('')
const complexityTotal = ref('')
const complexityReasoning = ref('')
const reviewing = ref(false)
const reviewNotice = ref('')
const split = ref(39)
let disposed = false
let inspection = 0
let pollTimer: ReturnType<typeof setTimeout> | undefined
let contestTimer: ReturnType<typeof setInterval> | undefined
const activeJob = ref<string | null>(null)
const md = new MarkdownIt({html: false, linkify: false})
const statement = computed(() => DOMPurify.sanitize(md.render(problem.value?.statement || '')))
const editorLanguage = computed(() => languages.value.find(l => l.id === language.value)?.editor_language || 'plaintext')
const available = computed(() => languages.value.some(l => l.id === language.value && l.available))
const groupKey = computed(() => problem.value ? `code-relay:job:${workspaceScope()}:${problem.value.id}:v${problem.value.version}:${language.value}` : '')

function storageGet(key: string) {
  try { return localStorage.getItem(key) } catch { storageWarning.value = 'Browser storage is unavailable. Copy your draft before leaving.'; return null }
}
function storageSet(key: string, value: string) {
  try { localStorage.setItem(key, value) } catch { storageWarning.value = 'Draft could not be saved in this browser. Copy your code before leaving.' }
}
function loadDraft() {
  if (!problem.value || !language.value) return
  code.value = storageGet(draftKey(problem.value.id, problem.value.version, language.value)) ?? problem.value.starters[language.value] ?? ''
}
watch(code, value => {
  if (problem.value && language.value) storageSet(draftKey(problem.value.id, problem.value.version, language.value), value)
})
watch(language, () => {
  if (!problem.value) return
  storageSet(`code-relay:language:${problem.value.id}`, language.value)
  result.value = undefined; selected.value = undefined; currentAttemptId.value = null; currentAttempt.value = undefined
  loadDraft(); void loadHistory()
})
async function loadHistory() {
  if (!problem.value || !language.value) return
  const lang = language.value
  try {
    const items = await api<Attempt[]>(`/attempts?problem_id=${encodeURIComponent(problem.value.id)}&problem_version=${problem.value.version}&language=${encodeURIComponent(lang)}`)
    if (!disposed && language.value === lang) attempts.value = items
  } catch (e) { if (!disposed) error.value = (e as Error).message }
}
function rememberJob(id: string | null) {
  try { id ? sessionStorage.setItem(groupKey.value, id) : sessionStorage.removeItem(groupKey.value) } catch { /* History still preserves official attempts. */ }
}
async function poll(id: string) {
  if (disposed) return
  try {
    const job = await api<Job>(`/jobs/${id}`)
    if (disposed) return
    state.value = job.state
    if (job.state === 'completed' || job.state === 'failed' || job.state === 'interrupted') {
      result.value = job.result ?? undefined; currentAttemptId.value = job.attempt_id
      if (job.attempt_id) currentAttempt.value = await api<Attempt>(`/attempts/${job.attempt_id}`)
      if (disposed) return
      busy.value = false; activeJob.value = null; rememberJob(null)
      await loadHistory()
    } else {
      pollTimer = setTimeout(() => void poll(id), 250)
    }
  } catch (e) {
    if (!disposed) { error.value = (e as Error).message; busy.value = false; await loadHistory() }
  }
}
function retryPoll() { if (activeJob.value) { error.value = ''; busy.value = true; void poll(activeJob.value) } }
async function execute(mode: 'samples' | 'custom' | 'submit') {
  if (!problem.value || busy.value || !available.value || !canExecute.value) return
  if (!code.value.trim()) { error.value = 'Write a solution before running or submitting.'; return }
  if (isHosted.value && pendingRecord.value) { error.value='Resolve the pending recording before running or recording again.'; return }
  if (isHosted.value && mode==='submit' && !window.confirm(`Record an official submission for ${clientState.team?.team_name} on ${problem.value.title}? This immutable source snapshot counts as an official attempt.`)) return
  error.value = ''; busy.value = true; state.value = 'queued'; result.value = undefined; tab.value = 'results'; currentAttempt.value = undefined
  const payload = {problem_id: problem.value.id, problem_version: problem.value.version, language: language.value, code: code.value,
    ...(mode !== 'submit' ? {mode, stdin: mode === 'custom' ? customInput.value : ''} : {})}
  try {
    let key: string|undefined
    if (isHosted.value && mode==='submit') {
      key=crypto.randomUUID();pendingRecord.value={key,payload}
      try{sessionStorage.setItem(pendingKey.value,JSON.stringify(pendingRecord.value))}catch{/* Current-page retry remains available. */}
    }
    const response = await api<{job_id: string; attempt_id: string | null}>(mode === 'submit' ? '/submissions' : '/runs', {method: 'POST', body: JSON.stringify(payload), headers:key?{'Idempotency-Key':key}:{}})
    pendingRecord.value=null;try{sessionStorage.removeItem(pendingKey.value)}catch{/* no-op */}
    currentAttemptId.value = response.attempt_id; activeJob.value = response.job_id; rememberJob(activeJob.value)
    await poll(activeJob.value)
  } catch (e) { if (!disposed) { clearRejectedRecord(e); error.value = (e as Error).message; busy.value = false } }
}
function clearRejectedRecord(error:unknown){
  if(error instanceof ApiError && error.status>=400 && error.status<500 && error.status!==401){
    pendingRecord.value=null;try{sessionStorage.removeItem(pendingKey.value)}catch{/* no-op */}
  }
}
async function retryRecord() {
  if(!pendingRecord.value||busy.value)return
  busy.value=true;error.value=''
  try {
    const response=await api<{job_id:string;attempt_id:string}>('/submissions',{method:'POST',body:JSON.stringify(pendingRecord.value.payload),headers:{'Idempotency-Key':pendingRecord.value.key}})
    pendingRecord.value=null;try{sessionStorage.removeItem(pendingKey.value)}catch{/* no-op */}
    currentAttemptId.value=response.attempt_id;activeJob.value=response.job_id;rememberJob(response.job_id);tab.value='results';await poll(response.job_id)
  }catch(e){clearRejectedRecord(e);error.value=(e as Error).message;busy.value=false}
}
function reset() {
  if (problem.value && window.confirm('Replace your current draft with the starter program?')) {
    code.value = problem.value.starters[language.value] || ''; error.value = ''
  }
}
async function inspect(id: string) {
  if (reviewing.value) return
  const token = ++inspection
  error.value = ''; reviewNotice.value = ''; selected.value = undefined
  try {
    const attempt = await api<Attempt>(`/attempts/${id}`)
    if (disposed || token !== inspection) return
    selected.value = attempt
    ratingsRead.value = attempt.review ? [...attempt.review.readability] : [null, null, null, null]
    ratingsTech.value = attempt.review ? [...attempt.review.technical] : [null, null, null, null]
    rationale.value = attempt.review?.rationale || ''
    const analysis = attempt.review?.complexity
    complexityStatus.value = analysis?.status || 'not_assessed'
    complexityTime.value = analysis?.worst_case_time || ''
    complexityAuxiliary.value = analysis?.auxiliary_space || ''
    complexityTotal.value = analysis?.total_space || ''
    complexityReasoning.value = analysis?.reasoning || ''
  } catch (e) { error.value = (e as Error).message }
}
function restore() {
  if (selected.value?.code !== undefined && window.confirm('Replace your current draft with this attempt’s saved source?')) code.value = selected.value.code
}
async function saveReview() {
  if (!selected.value || ratingsRead.value.includes(null) || ratingsTech.value.includes(null) || !rationale.value.trim()) {
    error.value = 'Rate every dimension and provide a short review rationale.'; return
  }
  let complexity: ReviewedComplexity | undefined
  if (complexityStatus.value !== 'not_assessed') {
    if (!complexityReasoning.value.trim() || (complexityStatus.value === 'assessed' &&
        [complexityTime.value, complexityAuxiliary.value, complexityTotal.value].some(value => !value.trim()))) {
      error.value = 'Provide complexity bounds and reasoning, or choose Unable to assess with an explanation.'; return
    }
    const assessed = complexityStatus.value === 'assessed'
    complexity = {status: complexityStatus.value,
      worst_case_time: assessed ? complexityTime.value.trim() : null,
      auxiliary_space: assessed ? complexityAuxiliary.value.trim() : null,
      total_space: assessed ? complexityTotal.value.trim() : null,
      reasoning: complexityReasoning.value.trim()}
  }
  reviewing.value = true; error.value = ''; reviewNotice.value = ''
  try {
    const updated = await api<Attempt>(`/attempts/${selected.value.id}/review`, {method: 'PUT', body: JSON.stringify({
      readability: ratingsRead.value, technical: ratingsTech.value, rationale: rationale.value.trim(),
      ...(complexity ? {complexity} : {})})})
    selected.value = updated
    if (currentAttemptId.value === updated.id) { result.value = updated.result ?? undefined; currentAttempt.value = updated }
    reviewNotice.value = 'Review saved to this source snapshot.'
    await loadHistory()
  } catch (e) { error.value = (e as Error).message }
  finally { reviewing.value = false }
}
function reviewCurrent() { if (currentAttemptId.value) { tab.value = 'history'; void inspect(currentAttemptId.value) } }
function date(value: string) { return new Date(value).toLocaleString() }
function keyboard(event: KeyboardEvent) {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); void execute(event.shiftKey ? 'submit' : 'samples') }
}
async function load() {
  loading.value = true; error.value = ''
  try {
    const [p, langs] = await Promise.all([api<Problem>(`/problems/${encodeURIComponent(String(route.params.id))}`), api<Language[]>('/languages')])
    if (disposed) return
    problem.value = p; languages.value = langs
    if(isHosted.value){try{const saved=sessionStorage.getItem(pendingKey.value);pendingRecord.value=saved?JSON.parse(saved):null}catch{pendingRecord.value=null}}
    const pendingLanguage=(pendingRecord.value?.payload as {language?:string})?.language
    const savedLanguage = storageGet(`code-relay:language:${p.id}`)
    language.value = langs.find(l=>l.id===pendingLanguage)?.id || langs.find(l => l.id === savedLanguage && l.available)?.id || langs.find(l => l.available)?.id || langs[0]?.id || ''
    loadDraft(); await loadHistory()
    try { activeJob.value = sessionStorage.getItem(groupKey.value) } catch { activeJob.value = null }
    if (activeJob.value) { busy.value = true; void poll(activeJob.value) }
  } catch (e) { error.value = (e as Error).message }
  finally { loading.value = false }
}
onMounted(() => { void load(); window.addEventListener('keydown', keyboard);if(isHosted.value)contestTimer=setInterval(()=>{void refreshTeam().catch(()=>{/* The API displays execution errors and handles expiry. */})},5000) })
onBeforeUnmount(() => { disposed = true; clearTimeout(pollTimer);clearInterval(contestTimer); window.removeEventListener('keydown', keyboard) })
</script>

<template>
  <main class="workspace">
    <div v-if="loading" class="empty">Opening your workspace…</div>
    <div v-else-if="!problem" class="page error-box" role="alert">{{ error }} <button @click="load">Retry</button> <RouterLink to="/problems">Back to library</RouterLink></div>
    <template v-else>
      <div class="workspace-heading"><div><RouterLink to="/problems" class="back-link">← Problem library</RouterLink><h1>{{ problem.title }}</h1></div><div class="workspace-meta"><span class="difficulty">{{ problem.difficulty }}</span><span>{{ problem.suggested_duration_minutes }} min suggested</span><span>v{{ problem.version }}</span></div></div>
      <div v-if="error" class="error-box workspace-error" role="alert">{{ error }} <button v-if="activeJob && !busy" @click="retryPoll">Retry job status</button><button @click="error = ''" aria-label="Dismiss error">×</button></div>
      <div v-if="storageWarning" class="warning-box" role="status">{{ storageWarning }}</div>
      <div v-if="pendingRecord" class="warning-box" role="status">A recording request needs reconciliation. Retrying uses its frozen source and original request key.<button @click="retryRecord" :disabled="busy">Retry pending recording</button></div>
      <p v-if="isHosted && !canExecute" class="warning-box">This contest is read-only. Existing admitted submissions may still finish judging.</p>
      <div class="workspace-panels" :style="{'--statement-width': `${split}%`}">
        <section class="statement-panel" aria-label="Problem statement">
          <div class="panel-title"><span>THE CHALLENGE</span><span>{{ problem.tags.join(' / ') }}</span></div>
          <div class="statement-scroll"><div class="prose" v-html="statement"></div>
            <article v-for="(sample, i) in problem.samples" :key="sample.id" class="sample"><h3>Sample {{ i + 1 }}</h3><label>Input</label><pre>{{ sample.input }}</pre><label>Output</label><pre>{{ sample.expected_output }}</pre><p>{{ sample.explanation }}</p></article>
          </div>
          <label class="resize-control">Panel width <input v-model.number="split" aria-label="Statement panel width" type="range" min="25" max="55"></label>
        </section>
        <section class="solution-panel" aria-label="Solution workspace">
          <div class="editor-toolbar"><label for="language">LANGUAGE</label><select id="language" v-model="language" :disabled="busy || !!pendingRecord"><option v-for="lang in languages" :key="lang.id" :value="lang.id" :disabled="!lang.available">{{ lang.label }}{{ lang.available ? '' : ' — unavailable' }}</option></select><button class="quiet" @click="reset" :disabled="busy">Reset starter</button><span class="draft-status">{{ storageWarning ? 'Draft not saved' : '● Draft saved locally' }}</span></div>
          <CodeEditor v-model="code" :language="editorLanguage" />
          <div class="run-toolbar"><label><input v-model="custom" type="checkbox"> Custom input</label><span v-if="busy" class="job-state" role="status">{{ state }}…</span><button :disabled="busy || !available || !canExecute || !!pendingRecord" @click="execute(custom ? 'custom' : 'samples')">▷ {{ custom ? 'Run input' : isHosted ? 'Run Code' : 'Run samples' }}</button><button class="primary" :disabled="busy || !available || !canExecute || !!pendingRecord" @click="execute('submit')">{{ isHosted?'Record Submission':'Submit ↗' }}</button></div>
          <div v-if="custom" class="custom-input"><label for="stdin">Standard input</label><textarea id="stdin" v-model="customInput" spellcheck="false" placeholder="Enter the exact input to send to your program…"></textarea></div>
          <div class="results-tabs" role="tablist" aria-label="Workspace output"><button role="tab" :aria-selected="tab === 'results'" :class="{active: tab === 'results'}" @click="tab = 'results'">Results</button><button role="tab" :aria-selected="tab === 'history'" :class="{active: tab === 'history'}" @click="tab = 'history'; loadHistory()">History & review <span>{{ attempts.length }}</span></button><span>Ctrl+Enter to run · Ctrl+Shift+Enter to submit</span></div>
          <div class="results-content">
            <template v-if="tab === 'results'">
              <JudgeResults v-if="result" :result="result" :rubric="problem.rubric" />
              <ComplexityAnalysis v-if="result?.assessment && currentAttempt" :reference="currentAttempt.reference_complexity" :analysis="currentAttempt.review?.complexity" />
              <div v-if="!result" class="results-empty"><span>[ ]</span><h3>Your next result starts here.</h3><p>Try the samples, explore an edge case, or submit against the full test suite.</p></div>
              <button v-if="currentAttemptId && result?.assessment" class="review-link" @click="reviewCurrent">{{ isHosted?'View saved source & feedback →':'Review this attempt’s code quality →' }}</button>
            </template>
            <template v-else>
              <Trajectory :attempts="attempts" />
              <div class="section-heading"><h3>Saved attempts</h3><button class="quiet" @click="loadHistory">Refresh</button></div>
              <div class="attempt-list"><button v-for="(attempt, i) in attempts" :key="attempt.id" :class="{selected: selected?.id === attempt.id}" @click="inspect(attempt.id)"><span>#{{ attempts.length - i }} <small>{{ date(attempt.created_at) }}</small></span><span>{{ attempt.result?.verdict || attempt.status }}<small>{{ attempt.result?.assessment?.final == null ? 'Overall pending' : `${attempt.result.assessment.final}% overall` }}</small></span></button><p v-if="!attempts.length" class="muted">Official submissions appear here. Sample and custom runs do not create attempts.</p></div>
              <section v-if="selected" class="attempt-detail" aria-label="Selected attempt">
                <div class="section-heading"><h3>Saved source · {{ date(selected.created_at) }}</h3><button @click="restore" :disabled="busy">Restore to editor</button></div><pre class="source-snapshot">{{ selected.code }}</pre>
                <JudgeResults v-if="selected.result" :result="selected.result" :rubric="selected.rubric" />
                <ComplexityAnalysis :reference="selected.reference_complexity" :analysis="selected.review?.complexity" />
                <form v-if="selected.result?.assessment && !isHosted" class="review-form" @submit.prevent="saveReview">
                  <h3>Human code review</h3><p>Review the saved source above. 0 = missing, 1 = weak, 2 = partial, 3 = good, 4 = strong. Useful clarity matters; extra comments or abstraction do not earn automatic credit.</p>
                  <fieldset><legend>Readability and maintainability · {{ selected.rubric.weights.readability }}%</legend><label v-for="(dimension, i) in selected.rubric.readability" :key="dimension">{{ dimension }}<select v-model="ratingsRead[i]" :aria-label="`Readability: ${dimension}`" required><option :value="null" disabled>Select rating</option><option v-for="n in [0, 1, 2, 3, 4]" :key="n" :value="n">{{ n }}</option></select></label></fieldset>
                  <fieldset><legend>Organization and technical quality · {{ selected.rubric.weights.technical }}%</legend><label v-for="(dimension, i) in selected.rubric.technical" :key="dimension">{{ dimension }}<select v-model="ratingsTech[i]" :aria-label="`Technical quality: ${dimension}`" required><option :value="null" disabled>Select rating</option><option v-for="n in [0, 1, 2, 3, 4]" :key="n" :value="n">{{ n }}</option></select></label></fieldset>
                  <fieldset class="complexity-form"><legend>Reviewer complexity analysis</legend>
                    <p class="muted">Use the saved code above. Account for library operations, recursion, and retained input/output. Use this reasoning as evidence for Technical Quality; the four grading weights stay unchanged.</p>
                    <label for="complexity-status">Analysis status</label><select id="complexity-status" v-model="complexityStatus"><option value="not_assessed" :disabled="!!selected.review?.complexity">Not assessed</option><option value="assessed">Assessed</option><option value="unable_to_assess">Unable to assess</option></select>
                    <template v-if="complexityStatus === 'assessed'">
                      <label for="complexity-time">Worst-case time</label><input id="complexity-time" v-model="complexityTime" required maxlength="240" placeholder="e.g. O(N + Q log N)">
                      <label for="complexity-auxiliary">Auxiliary space</label><input id="complexity-auxiliary" v-model="complexityAuxiliary" required maxlength="240" placeholder="e.g. O(N), including any recursion stack">
                      <label for="complexity-total">Space including stored input/output</label><input id="complexity-total" v-model="complexityTotal" required maxlength="240" placeholder="e.g. O(N + Q) if all answers are retained">
                    </template>
                    <template v-if="complexityStatus !== 'not_assessed'"><label for="complexity-reasoning">Complexity reasoning</label><textarea id="complexity-reasoning" v-model="complexityReasoning" required maxlength="4000" placeholder="Explain the dominant work and allocations, or why a bound cannot be assessed."></textarea></template>
                  </fieldset>
                  <label for="rationale">Review rationale</label><textarea id="rationale" v-model="rationale" required maxlength="4000" placeholder="Explain your ratings with concrete observations about this source…"></textarea>
                  <div class="review-actions"><button class="primary" :disabled="reviewing">{{ reviewing ? 'Saving…' : 'Save review' }}</button><span role="status">{{ reviewNotice }}</span></div>
                </form>
              </section>
            </template>
          </div>
        </section>
      </div>
      <div class="workspace-footnote"><span>{{ problem.limits.time_ms / 1000 }}s per case · {{ problem.limits.memory_mb }} MB {{ clientState.memoryEnforced?'managed judge limit':'target (unenforced locally)' }}</span><span>{{ isHosted?'Private team history · Organizer-reviewed code quality':'Trusted local code · human reviews are local assessments' }}</span></div>
      <p v-for="lang in languages.filter(l => !l.available)" :key="lang.id" class="language-note">{{ lang.label }} unavailable: {{ lang.reason }}</p>
    </template>
  </main>
</template>
