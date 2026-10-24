import { api, ApiError } from './api'
import { clientState } from './clientState'
import type { TeamIdentity } from './clientState'

let initializing: Promise<void> | undefined
export async function refreshTeam() {
  const previous=clientState.team
  try{
    const identity=await api<TeamIdentity>('/teams/me')
    if(clientState.initialized && previous!==clientState.team)return
    clientState.team=identity
  }
  catch(error){
    if(clientState.initialized && previous!==clientState.team)return
    if(error instanceof ApiError && error.status===401){
      clientState.team=null
      if(clientState.initialized)window.dispatchEvent(new CustomEvent('relay-session-expired',{detail:'team'}))
    }
    throw error
  }
}
export async function initializeSession() {
  if (clientState.initialized) return
  if (!initializing) initializing = (async () => {
    const configuration = await api<{mode: 'practice' | 'contest'; executor?:'local'|'managed'; memory_enforced?:boolean}>('/config')
    clientState.mode = configuration.mode
    clientState.executor = configuration.executor || 'local'
    clientState.memoryEnforced = configuration.memory_enforced || false
    if (configuration.mode === 'contest') {
      await Promise.all([
        refreshTeam().catch(() => { clientState.team = null }),
        api<{username: string; csrf_token: string}>('/organizer/me').then(value => { clientState.organizer = value }).catch(() => { clientState.organizer = null }),
      ])
    }
    clientState.initialized = true
  })().catch(error => { initializing = undefined; throw error })
  return initializing
}
