import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './pages/Home.vue'
import Catalog from './pages/Catalog.vue'
import './style.css'
import './complexity.css'
import './contest.css'
import { clientState } from './clientState'
import { initializeSession, refreshTeam } from './session'

const router = createRouter({history: createWebHistory(), routes: [
  {path: '/', component: Home},
  {path: '/problems', component: Catalog},
  {path: '/problems/:id', component: () => import('./pages/Workspace.vue')},
  {path: '/join', component: () => import('./pages/Join.vue')},
  {path: '/dashboard', component: () => import('./pages/Dashboard.vue')},
  {path: '/history', component: () => import('./pages/History.vue')},
  {path: '/organizer/login', component: () => import('./pages/OrganizerLogin.vue')},
  {path: '/organizer', component: () => import('./pages/Organizer.vue')},
  {path: '/:pathMatch(.*)*', redirect: '/'},
]})
router.beforeEach(async to => {
  clientState.role = to.path.startsWith('/organizer') ? 'organizer' : 'team'
  try { await initializeSession() } catch { return true }
  if (clientState.mode !== 'contest') return true
  if (to.path === '/organizer' && !clientState.organizer) return '/organizer/login'
  if (['/join', '/', '/organizer/login', '/organizer'].includes(to.path)) return true
  try { await refreshTeam() } catch { clientState.team=null; return '/join' }
  if (to.path.startsWith('/problems') && clientState.team?.contest?.phase === 'waiting') return '/dashboard'
  return true
})
createApp(App).use(router).mount('#app')
