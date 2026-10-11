<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <header class="app-header">
    <RouterLink to="/" class="brand" aria-label="Code Relay home"><span class="brand-mark">[↗]</span> CODE<span>RELAY</span></RouterLink>
    <nav aria-label="Main navigation">
      <RouterLink to="/problems" :class="{active: route.path.startsWith('/problems')}">Problem library</RouterLink>
      <span class="local-tag"><i></i> LOCAL PRACTICE</span>
    </nav>
  </header>
  <RouterView :key="route.params.id as string" />
  <footer class="app-footer"><span>Built for the next iteration.</span><span>Offline after setup · No account required</span></footer>
</template>
