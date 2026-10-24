<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { clientState } from '../clientState'
import type { ContestInfo, TeamIdentity } from '../clientState'
const router = useRouter()
const contests = ref<ContestInfo[]>([]), contestId = ref(''), name = ref(''), code = ref(''), error = ref(''), busy = ref(false)
async function load() {
  try { contests.value = await api<ContestInfo[]>('/contest'); contestId.value = contests.value[0]?.id || '' } catch(e) { error.value = (e as Error).message }
}
async function join() {
  busy.value = true; error.value = ''
  try {
    clientState.team = await api<TeamIdentity>('/teams/join', {method:'POST', body:JSON.stringify({contest_id:contestId.value, team_name:name.value.trim(), join_code:code.value.trim()})})
    code.value = ''; await router.replace('/dashboard')
  } catch(e) { error.value = (e as Error).message }
  finally { busy.value = false }
}
onMounted(load)
</script>
<template>
  <main class="page access-page"><div class="eyebrow">YOUR TEAM / YOUR WORKSPACE</div><h1>Join your contest.</h1><p class="muted">Use the team name and private code provided by your organizer. One active browser session is allowed per team.</p>
    <p v-if="error" class="error-box" role="alert">{{ error }}</p>
    <form class="access-form" @submit.prevent="join"><label for="contest">Contest</label><select id="contest" v-model="contestId" required><option value="" disabled>Select contest</option><option v-for="c in contests" :key="c.id" :value="c.id">{{ c.name }} · {{ c.phase }}</option></select><label for="team-name">Team name</label><input id="team-name" v-model="name" required maxlength="120" autocomplete="username"><label for="join-code">Join code</label><input id="join-code" v-model="code" type="password" required maxlength="200" autocomplete="current-password"><button class="primary" :disabled="busy || !contestId">{{ busy ? 'Joining…' : 'Join team' }}</button></form>
    <p v-if="!contests.length" class="muted">No published contests yet. Ask your organizer when access will open.</p>
  </main>
</template>
