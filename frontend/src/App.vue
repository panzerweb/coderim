<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { clientState, workspaceScope } from './clientState'
import { api, ApiError } from './api'
const logoutError=ref('')
const route = useRoute()
const router = useRouter()
const showOrganizerLink = computed(() => clientState.initialized && (
  !clientState.team || (clientState.role === 'organizer' && !!clientState.organizer)
))
async function logout() {
  const kind = route.path.startsWith('/organizer') ? 'organizer' : 'teams'
  logoutError.value=''
  try { await api(`/${kind}/logout`, {method:'POST',body:'{}'}) } catch(error) {
    if(!(error instanceof ApiError) || error.status!==401){logoutError.value=(error as Error).message;return}
  }
    if(kind==='organizer')clientState.organizer=null;else clientState.team=null
    await router.replace(kind==='organizer'?'/organizer/login':'/join')
}
function expired(event: Event) {
  const role=(event as CustomEvent).detail
  if(role==='organizer'){clientState.organizer=null;void router.replace('/organizer/login')}
  else{clientState.team=null;void router.replace('/join')}
}
onMounted(()=>window.addEventListener('relay-session-expired',expired))
onBeforeUnmount(()=>window.removeEventListener('relay-session-expired',expired))
</script>

<template>
  <header class="app-header">
    <RouterLink to="/" class="brand" aria-label="Code Relay home"><span class="brand-mark">[↗]</span> CODE<span>RELAY</span></RouterLink>
    <nav aria-label="Main navigation">
      <template v-if="clientState.mode==='contest'">
        <RouterLink v-if="clientState.team" to="/dashboard">{{ clientState.team.team_name }}</RouterLink>
        <RouterLink v-if="clientState.team" to="/history">History</RouterLink>
        <RouterLink v-if="showOrganizerLink" to="/organizer">Organizer</RouterLink>
        <RouterLink v-if="!clientState.team && !clientState.organizer" to="/join">Join team</RouterLink>
        <button v-if="route.path.startsWith('/organizer') ? !!clientState.organizer : !!clientState.team" class="quiet" @click="logout">Log out</button>
      </template>
      <template v-else><RouterLink to="/problems" :class="{active: route.path.startsWith('/problems')}">Problem library</RouterLink><span class="local-tag"><i></i> LOCAL PRACTICE</span></template>
    </nav>
  </header>
  <p v-if="logoutError" role="alert" class="error">{{ logoutError }}</p>
  <RouterView :key="`${route.params.id || ''}:${workspaceScope()}`" />
  <footer class="app-footer"><span>Built for the next iteration.</span><span>{{ clientState.mode==='contest'?'Private team sessions · Shared contest deadline':'Offline after setup · No account required' }}</span></footer>
</template>
