import { reactive } from 'vue'

export interface ContestInfo {id: string; name: string; starts_at: string; ends_at: string; timezone: string; phase: 'draft' | 'waiting' | 'active' | 'ended'; server_time: string; duration_minutes: number}
export interface TeamIdentity {team_id: string; team_name: string; contest_id: string; csrf_token: string; expires_at?: string; contest?: ContestInfo; metrics?: {solved_problems: number; official_attempts: number}}
export const clientState = reactive({
  mode: 'practice' as 'practice' | 'contest', initialized: false,
  executor: 'local' as 'local' | 'managed', memoryEnforced: false,
  role: 'team' as 'team' | 'organizer', team: null as TeamIdentity | null,
  organizer: null as {username: string; csrf_token: string} | null,
})

export function workspaceScope() {
  return clientState.mode === 'contest' && clientState.team
    ? `contest:${clientState.team.contest_id}:team:${clientState.team.team_id}` : 'practice'
}
