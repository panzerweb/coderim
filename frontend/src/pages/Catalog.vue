<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../api'
import type { CatalogProblem } from '../types'
const problems = ref<CatalogProblem[]>([])
const query = ref('')
const error = ref('')
const loading = ref(true)
const filtered = computed(() => problems.value.filter(p => `${p.title} ${p.tags.join(' ')}`.toLowerCase().includes(query.value.toLowerCase())))
async function load() {
  loading.value = true; error.value = ''
  try { problems.value = await api<CatalogProblem[]>('/problems') } catch (e) { error.value = (e as Error).message }
  finally { loading.value = false }
}
onMounted(load)
</script>

<template>
  <main class="page catalog">
    <div class="eyebrow">01 / THE PROBLEM LIBRARY</div>
    <div class="catalog-title"><div><h1>A good problem.<br>A better next attempt.</h1><p>Choose a challenge and give your ideas somewhere to go.</p></div><span class="catalog-count">{{ problems.length.toString().padStart(2, '0') }}<small>AVAILABLE CHALLENGES</small></span></div>
    <div class="catalog-tools"><label for="search" class="sr-only">Search problems</label><input id="search" v-model="query" placeholder="Search by title or topic…"><span>Complete programs · Standard input / output</span></div>
    <div v-if="error" role="alert" class="error-box">{{ error }} <button @click="load">Retry</button></div>
    <p v-else-if="loading" class="empty">Loading your local library…</p>
    <div v-else class="problem-list">
      <RouterLink v-for="(problem, i) in filtered" :key="problem.id" :to="`/problems/${problem.id}`" class="problem-row">
        <span class="problem-index">{{ String(i + 1).padStart(2, '0') }}</span>
        <div class="problem-info"><div class="problem-meta"><span class="difficulty">{{ problem.difficulty }}</span><span>{{ problem.suggested_duration_minutes }} min suggested</span></div><h2>{{ problem.title }}</h2><div class="tags"><span v-for="tag in problem.tags" :key="tag">{{ tag }}</span></div></div>
        <span class="open-problem">Open workspace <b>↗</b></span>
      </RouterLink>
      <p v-if="!filtered.length" class="empty">{{ problems.length ? 'No matching problems. Try another search.' : 'No published problems. Add and validate a problem package, then restart the backend.' }}</p>
    </div>
    <aside class="library-note"><span>GOOD TO KNOW</span><p>Sample runs help you explore. Official submissions check the full test suite. Your saved attempts show how your solution evolves.</p></aside>
  </main>
</template>
