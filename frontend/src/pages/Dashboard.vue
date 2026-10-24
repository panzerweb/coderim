<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { clientState } from '../clientState'
import { refreshTeam } from '../session'
const error = ref(''), clock = ref(Date.now())
let timer: ReturnType<typeof setInterval> | undefined
const contest = computed(() => clientState.team?.contest)
const remaining = computed(() => {
  if (!contest.value) return ''
  const target = contest.value.phase === 'waiting' ? contest.value.starts_at : contest.value.ends_at
  const seconds = Math.max(0, Math.floor((Date.parse(target) - clock.value) / 1000))
  return `${Math.floor(seconds/3600)}h ${Math.floor(seconds/60)%60}m ${seconds%60}s`
})
function date(value: string) { return new Date(value).toLocaleString('en-PH', {timeZone:contest.value?.timezone || 'Asia/Manila'}) }
async function refresh() {
  try { await refreshTeam(); if (contest.value) clock.value = Date.parse(contest.value.server_time); error.value = '' } catch(e) { error.value = (e as Error).message }
}
onMounted(() => { void refresh(); let ticks=0; timer=setInterval(() => {clock.value+=1000;if(++ticks%5===0)void refresh()},1000) })
onBeforeUnmount(() => clearInterval(timer))
</script>
<template>
  <main class="page"><div class="eyebrow">TEAM DASHBOARD</div><h1>{{ clientState.team?.team_name }}</h1><p v-if="error" class="error-box" role="alert">{{ error }}</p>
    <template v-if="contest"><section class="event-card"><span class="phase-badge">{{ contest.phase }}</span><h2>{{ contest.name }}</h2><p>{{ date(contest.starts_at) }} → {{ date(contest.ends_at) }} · {{ contest.timezone }}</p><strong class="countdown" v-if="contest.phase !== 'ended'">{{ remaining }}</strong><p v-if="contest.phase === 'waiting'">You’re signed in. Problems will be revealed when the shared contest window begins.</p><p v-else-if="contest.phase === 'ended'">The contest has ended. Your submission history and feedback remain available in read-only mode.</p><p v-else>All teams share this deadline. Recorded submissions admitted before it remain eligible while judging finishes.</p></section>
      <div class="metric-row"><article><strong>{{ clientState.team?.metrics?.solved_problems || 0 }}</strong><span>Distinct problems solved</span></article><article><strong>{{ clientState.team?.metrics?.official_attempts || 0 }}</strong><span>Official attempts</span></article></div>
      <div class="action-row"><RouterLink v-if="contest.phase !== 'waiting'" to="/problems" class="button primary">Problem library ↗</RouterLink><RouterLink to="/history" class="button">Team history</RouterLink></div>
    </template>
  </main>
</template>
