<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { clientState } from '../clientState'
const username=ref(''),password=ref(''),error=ref(''),busy=ref(false),router=useRouter()
async function login(){busy.value=true;error.value='';try{clientState.organizer=await api('/organizer/login',{method:'POST',body:JSON.stringify({username:username.value,password:password.value})});password.value='';await router.replace('/organizer')}catch(e){error.value=(e as Error).message}finally{busy.value=false}}
</script>
<template><main class="page access-page"><div class="eyebrow">ORGANIZER ACCESS</div><h1>Manage the relay.</h1><p class="muted">Organizer credentials are created through the server bootstrap command. Team join codes cannot access this interface.</p><p v-if="error" role="alert" class="error-box">{{ error }}</p><form class="access-form" @submit.prevent="login"><label for="organizer-username">Organizer username</label><input id="organizer-username" v-model="username" required autocomplete="username"><label for="organizer-password">Organizer password</label><input id="organizer-password" v-model="password" type="password" required autocomplete="current-password"><button class="primary" :disabled="busy">{{ busy?'Signing in…':'Sign in as organizer' }}</button></form></main></template>
