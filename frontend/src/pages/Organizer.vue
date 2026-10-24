<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { clientState } from '../clientState'
import type { ContestInfo } from '../clientState'
import type { Attempt, CatalogProblem } from '../types'
import JudgeResults from '../components/JudgeResults.vue'
import ComplexityAnalysis from '../components/ComplexityAnalysis.vue'
import ReviewForm from '../components/ReviewForm.vue'
interface Team {id:string;name:string;is_active:boolean;metrics:{solved_problems:number;official_attempts:number}}
const contests=ref<ContestInfo[]>([]),selectedId=ref(''),problems=ref<CatalogProblem[]>([]),problemIds=ref<string[]>([]),teams=ref<Team[]>([]),submissions=ref<Attempt[]>([]),selected=ref<Attempt>()
const name=ref('Code Relay'),start=ref(''),hours=ref(3),minutes=ref(30),teamName=ref(''),error=ref(''),notice=ref(''),secretCode=ref(''),secretTeam=ref(''),verified=ref(false),creating=ref(true),busy=ref(false)
const submissionOffset=ref(0)
const submissionTeam=ref('')
function submissionsUrl(offset=0){
  const query=new URLSearchParams({limit:'100',offset:String(offset)})
  if(selectedId.value)query.set('contest_id',selectedId.value)
  if(submissionTeam.value)query.set('team_id',submissionTeam.value)
  return '/organizer/submissions?'+query.toString()
}
async function submissionPage(delta:number){
  const offset=Math.max(0,submissionOffset.value+delta)
  try{
    submissions.value=await api<Attempt[]>(submissionsUrl(offset))
    submissionOffset.value=offset;selected.value=undefined
  }catch(e){error.value=(e as Error).message}
}
function asia(value:string){const d=new Date(value);return new Date(d.getTime()+8*3600000).toISOString().slice(0,16)}
function chosenStart():string{const current=contests.value.find(c=>c.id===selectedId.value);return current&&['active','ended'].includes(current.phase)?current.starts_at:new Date(start.value+':00+08:00').toISOString()}
async function load(){try{[contests.value,problems.value]=await Promise.all([api<ContestInfo[]>('/organizer/contests'),api<CatalogProblem[]>('/problems')]);const provider=await api<{verified:boolean}>('/organizer/provider');verified.value=provider.verified;if(selectedId.value)await select(selectedId.value)}catch(e){error.value=(e as Error).message}}
function newContest(){submissionTeam.value='';submissionOffset.value=0;creating.value=true;selectedId.value='';name.value='Code Relay';start.value=asia(new Date(Date.now()+3600000).toISOString());hours.value=3;minutes.value=30;teams.value=[];submissions.value=[];selected.value=undefined;problemIds.value=problems.value.map(p=>p.id)}
async function select(id:string){submissionTeam.value='';submissionOffset.value=0;selectedId.value=id;creating.value=false;secretCode.value='';selected.value=undefined;const c=contests.value.find(c=>c.id===id);if(!c)return;name.value=c.name;start.value=asia(c.starts_at);hours.value=Math.floor(c.duration_minutes/60);minutes.value=c.duration_minutes%60;try{[teams.value,submissions.value]=await Promise.all([api<Team[]>(`/organizer/teams?contest_id=${id}`),api<Attempt[]>(`/organizer/submissions?contest_id=${id}`)])}catch(e){error.value=(e as Error).message}}
async function save(){busy.value=true;error.value='';notice.value='';try{const data={name:name.value,starts_at:chosenStart(),duration_minutes:hours.value*60+minutes.value,timezone:'Asia/Manila'};if(!creating.value&&!window.confirm('Save this schedule? For an active event, the deadline may only be extended.'))return;const result=await api<ContestInfo>(creating.value?'/organizer/contests':`/organizer/contests/${selectedId.value}`,{method:creating.value?'POST':'PUT',body:JSON.stringify(data)});selectedId.value=result.id;await load();notice.value='Contest schedule saved.'}catch(e){error.value=(e as Error).message}finally{busy.value=false}}
async function publish(){if(!window.confirm('Publish and freeze these problem versions? Later repository edits will not change this contest.'))return;try{await api(`/organizer/contests/${selectedId.value}/publish`,{method:'POST',body:JSON.stringify({problem_ids:problemIds.value})});await load();notice.value='Contest published. Teams can join; problems are revealed at the scheduled start.'}catch(e){error.value=(e as Error).message}}
async function startNow(){
  if(!window.confirm('Start this contest now for all teams? The full configured duration will begin immediately.'))return
  try{
    await api(`/organizer/contests/${selectedId.value}/start`,{method:'POST',body:'{"confirm":true}'})
    await load();notice.value='Contest started. All teams share the configured deadline.'
  }catch(e){error.value=(e as Error).message}
}
async function end(){if(!window.confirm('End the contest now for every team? Already admitted submissions remain eligible.'))return;try{await api(`/organizer/contests/${selectedId.value}/end`,{method:'POST',body:'{"confirm":true}'});await load();notice.value='Contest ended; team history remains read-only.'}catch(e){error.value=(e as Error).message}}
async function createTeam(){error.value='';try{const result=await api<{name:string;join_code:string}>(`/organizer/contests/${selectedId.value}/teams`,{method:'POST',body:JSON.stringify({name:teamName.value})});await select(selectedId.value);secretTeam.value=result.name;secretCode.value=result.join_code;teamName.value=''}catch(e){error.value=(e as Error).message}}
async function teamAction(t:Team,action:string){if(!window.confirm(`${action==='rotate-code'?'Rotate the join code and revoke sessions':action==='reset-session'?'Revoke the active session':t.is_active?'Deactivate this team':'Reactivate this team'} for ${t.name}?`))return;try{const result=await api<{join_code?:string}>(action==='activity'?`/organizer/teams/${t.id}`:`/organizer/teams/${t.id}/${action}`,{method:action==='activity'?'PUT':'POST',body:JSON.stringify(action==='activity'?{is_active:!t.is_active}:{})});await select(selectedId.value);if(result.join_code){secretTeam.value=t.name;secretCode.value=result.join_code}}catch(e){error.value=(e as Error).message}}
async function inspect(id:string){try{selected.value=await api<Attempt>(`/attempts/${id}`)}catch(e){error.value=(e as Error).message}}
async function reviewed(value:Attempt){selected.value=value;notice.value='Organizer review saved.';submissions.value=await api<Attempt[]>(submissionsUrl(submissionOffset.value))}
async function legacy(){submissionTeam.value='';creating.value=false;selectedId.value='';selected.value=undefined;submissionOffset.value=0;await submissionPage(0);notice.value='Showing all submissions, including legacy unowned records.'}
onMounted(async()=>{await load();newContest()})
</script>
<template><main class="page organizer-page"><div class="eyebrow">ORGANIZER CONSOLE</div><div class="section-heading"><h1>Run the relay.</h1><button @click="load">Refresh console</button></div><p v-if="error" class="error-box" role="alert">{{ error }}</p><p v-if="notice" class="notice" role="status">{{ notice }}</p><p v-if="clientState.executor==='local'" class="notice">Automatic judging uses the installed language toolchains. No provider account is needed.</p><p class="warning-box" v-else-if="!verified">Managed judge not verified. You can publish and register teams; running code requires managed-provider verification.</p>
  <div class="organizer-columns"><aside><h2>Events</h2><button @click="newContest">New contest</button><button class="event-choice" v-for="c in contests" :key="c.id" @click="select(c.id)">{{ c.name }} <small>{{ c.phase }}</small></button><button class="quiet" @click="legacy">All / legacy submissions</button></aside>
  <section v-if="creating || selectedId"><h2>{{ creating?'Create event':'Event schedule' }}</h2><form class="access-form" @submit.prevent="save"><label for="event-name">Contest name</label><input id="event-name" v-model="name" required maxlength="150"><label for="event-start">Start (Asia/Manila · UTC+08:00)</label><input id="event-start" v-model="start" :disabled="['active','ended'].includes(contests.find(c=>c.id===selectedId)?.phase||'')" type="datetime-local" required><div class="duration-fields"><label for="event-hours">Hours<input id="event-hours" v-model.number="hours" type="number" min="0" max="168" required></label><label for="event-minutes">Minutes<input id="event-minutes" v-model.number="minutes" type="number" min="0" max="59" required></label></div><button class="primary" :disabled="busy">{{ creating?'Create contest':'Save schedule' }}</button></form>
    <template v-if="selectedId"><template v-if="contests.find(c=>c.id===selectedId)?.phase==='draft'"><h3>Problems to freeze</h3><label class="problem-check" v-for="p in problems" :key="p.id"><input type="checkbox" v-model="problemIds" :value="p.id">{{ p.title }} · v{{ p.version }}</label><button @click="publish" :disabled="!problemIds.length">Publish contest</button></template><div v-else class="action-row"><button v-if="contests.find(c=>c.id===selectedId)?.phase==='waiting'" class="primary" @click="startNow">Start contest now</button><button class="quiet" :disabled="contests.find(c=>c.id===selectedId)?.phase!=='active'" @click="end">End contest now</button></div>
    <hr><h2>Teams</h2><form class="team-create" @submit.prevent="createTeam"><label for="new-team">Team name</label><input id="new-team" v-model="teamName" required maxlength="120"><button>Create team</button></form>
    <div v-if="secretCode" class="one-time-code" role="status"><strong>Join code for {{ secretTeam }} — shown once</strong><code>{{ secretCode }}</code><p>Copy and distribute it privately. Closing this view hides it; a lost code must be rotated.</p><button @click="secretCode=''">Hide code</button></div>
    <article class="team-management" v-for="t in teams" :key="t.id"><div><strong>{{ t.name }}</strong><small>{{ t.is_active?'Active':'Inactive' }} · {{ t.metrics.solved_problems }} solved · {{ t.metrics.official_attempts }} attempts</small></div><div class="action-row"><button @click="teamAction(t,'reset-session')">Reset session</button><button @click="teamAction(t,'rotate-code')">Rotate code</button><button @click="teamAction(t,'activity')">{{ t.is_active?'Deactivate':'Reactivate' }}</button></div></article>
    </template>
  </section></div>
  <section class="organizer-submissions"><h2>Official submissions</h2><label v-if="selectedId" class="problem-check">Team submissions<select aria-label="Team submissions" v-model="submissionTeam" @change="submissionPage(-submissionOffset)"><option value="">All teams</option><option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option></select></label><div class="attempt-list"><button v-for="a in submissions" :key="a.id" @click="inspect(a.id)"><span>{{ a.problem_id }} · {{ a.language }}<small>{{ a.team_name || a.team_id || 'Legacy unowned record' }} · {{ new Date(a.created_at).toLocaleString() }}</small></span><span>{{ a.result?.verdict || a.status }}</span></button></div>
    <div class="action-row"><button :disabled="submissionOffset===0" @click="submissionPage(-100)">Previous submissions</button><button :disabled="submissions.length<100" @click="submissionPage(100)">Next submissions</button></div>
    <section v-if="selected" class="attempt-detail"><h2>Saved source · {{ selected.team_name || 'Legacy unowned record' }} · {{ selected.problem_id }} · {{ selected.language }}</h2><pre class="source-snapshot">{{ selected.code }}</pre><JudgeResults v-if="selected.result" :result="selected.result" :rubric="selected.rubric"/><ComplexityAnalysis :reference="selected.reference_complexity" :analysis="selected.review?.complexity"/><ReviewForm v-if="selected.result?.assessment" :attempt="selected" @saved="reviewed"/></section>
  </section>
</main></template>
