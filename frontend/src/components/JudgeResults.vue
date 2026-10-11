<script setup lang="ts">
import type { Result, Rubric } from '../types'
defineProps<{result: Result; rubric: Rubric}>()
function score(value: number | null | undefined) { return value == null ? 'Pending' : `${Number(value.toFixed(2))}%` }
</script>

<template>
  <section class="judge-results" aria-label="Judge results">
    <div class="result-heading"><strong :class="{'success': result.verdict === 'Accepted' || result.verdict === 'Completed', 'failure': result.verdict !== 'Accepted' && result.verdict !== 'Completed'}">{{ result.verdict }}</strong><span v-if="result.mode !== 'custom'">{{ result.passed }} passed · {{ result.attempted }} attempted / {{ result.total }} total</span><span>{{ (result.duration_ms / 1000).toFixed(2) }}s total job</span></div>
    <p v-if="result.incomplete_reason" class="error-box">{{ result.incomplete_reason }}. Automated assessment is incomplete.</p>
    <pre v-if="result.diagnostics" class="diagnostics">{{ result.diagnostics }}</pre>
    <template v-if="result.assessment">
      <div class="score-grid">
        <article><span>Correctness · {{ rubric.weights.correctness }}%</span><strong>{{ score(result.assessment.correctness) }}</strong></article>
        <article><span>Requirements · {{ rubric.weights.requirements }}%</span><strong>{{ score(result.assessment.requirements) }}</strong></article>
        <article><span>Readability · {{ rubric.weights.readability }}%</span><strong>{{ score(result.assessment.readability) }}</strong></article>
        <article><span>Technical quality · {{ rubric.weights.technical }}%</span><strong>{{ score(result.assessment.technical) }}</strong></article>
      </div>
      <div class="final-score"><span>Overall assessment</span><strong>{{ score(result.assessment.final) }}</strong><small>{{ result.assessment.review_pending ? 'Human review required; missing reviews are not zero.' : 'Acceptance is determined by official tests.' }}</small></div>
      <details open><summary>Test categories</summary><div class="category" v-for="group in result.assessment.categories" :key="group.category"><span>{{ group.category }} <small>{{ group.weight }}%</small></span><meter min="0" :max="group.total" :value="group.passed"></meter><span>{{ group.passed }}/{{ group.total }} <small>({{ group.attempted }} attempted)</small></span></div></details>
      <details open><summary>Requirement evidence</summary><p class="muted">Credit means every mapped test passed. This is evidence coverage, not a proof of correctness.</p><div v-for="req in result.assessment.requirement_evidence" :key="req.id" class="requirement"><span :class="req.demonstrated ? 'success' : 'muted'">{{ req.demonstrated ? '✓' : '○' }}</span><div>{{ req.text }}<small>{{ req.passed }}/{{ req.total }} mapped tests passed · {{ req.attempted }} attempted</small></div></div></details>
    </template>
    <details v-for="test in result.cases" :key="test.id" class="test-case"><summary>{{ test.id }} <span :class="test.verdict === 'Accepted' || test.verdict === 'Completed' ? 'success' : 'failure'">{{ test.verdict }}</span><small>{{ test.duration_ms }} ms · exit {{ test.exit_code }}</small></summary><div class="io-grid"><div><label>Input</label><pre>{{ test.input }}</pre></div><div><label>Standard output</label><pre>{{ test.stdout || '(empty)' }}</pre></div><div v-if="test.expected_output !== null"><label>Expected output</label><pre>{{ test.expected_output }}</pre></div><div v-if="test.stderr"><label>Standard error</label><pre>{{ test.stderr }}</pre></div></div></details>
    <p v-if="result.mode === 'custom'" class="muted">Custom input has no expected output, correctness verdict, or assessment score.</p>
  </section>
</template>
