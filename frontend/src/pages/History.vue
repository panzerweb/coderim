<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
import type { Attempt } from '../types'
import JudgeResults from '../components/JudgeResults.vue'
import ComplexityAnalysis from '../components/ComplexityAnalysis.vue'
const attempts=ref<Attempt[]>([]),selected=ref<Attempt>(),error=ref(''),offset=ref(0)
async function load() {try{attempts.value=await api<Attempt[]>(`/submissions/me?limit=50&offset=${offset.value}`)}catch(e){error.value=(e as Error).message}}
async function inspect(id:string){try{selected.value=await api<Attempt>(`/submissions/${id}`)}catch(e){error.value=(e as Error).message}}
onMounted(load)
</script>
<template><main class="page"><div class="eyebrow">PRIVATE TEAM HISTORY</div><h1>Every recorded attempt.</h1><p class="muted">Only your team’s official submissions appear here. Sample/custom runs are excluded.</p><p v-if="error" role="alert" class="error-box">{{ error }}</p><button @click="load">Refresh history</button>
  <div class="attempt-list global-history"><button v-for="a in attempts" :key="a.id" @click="inspect(a.id)"><span>{{ a.problem_id }} · {{ a.language }}<small>{{ new Date(a.created_at).toLocaleString() }}</small></span><span>{{ a.result?.verdict || a.status }}</span></button><p v-if="!attempts.length" class="empty">No official submissions on this page.</p></div>
  <div class="action-row"><button :disabled="offset===0" @click="offset=Math.max(0,offset-50);load()">Previous</button><button :disabled="attempts.length<50" @click="offset+=50;load()">Next</button></div>
  <section v-if="selected" class="attempt-detail"><h2>Saved source · {{ selected.language }}</h2><pre class="source-snapshot">{{ selected.code }}</pre><JudgeResults v-if="selected.result" :result="selected.result" :rubric="selected.rubric"/><ComplexityAnalysis :reference="selected.reference_complexity" :analysis="selected.review?.complexity"/></section>
</main></template>
