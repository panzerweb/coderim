const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/+$/, "");
import { clientState, workspaceScope } from './clientState'

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message) }
}

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  const role = path.startsWith('/organizer') ? 'organizer' : path.startsWith('/teams') ? 'team' : clientState.role;
  const csrf = role === 'organizer' ? clientState.organizer?.csrf_token : clientState.team?.csrf_token;
  const headers = new Headers(options?.headers);
  headers.set('Content-Type', 'application/json');
  if (clientState.mode === 'contest') {
    headers.set('X-Relay-Role', role);
    if (csrf && options?.method && !['GET', 'HEAD'].includes(options.method.toUpperCase())) headers.set('X-CSRF-Token', csrf);
  }
  try {
    response = await fetch(`${API_BASE}/api${path}`, {
      ...options,
      credentials: 'include', headers,
    });
  } catch {
    throw new Error(
      clientState.mode === 'contest' ? 'Cannot reach the contest API. Your draft remains saved on this device.' : "Cannot reach the local judge. Start the backend and try again.",
    );
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message =
      typeof data.detail === "string"
        ? data.detail
        : "The request could not be processed.";
    if (response.status === 401 && clientState.mode === 'contest' && !['/teams/me', '/organizer/me', '/teams/join', '/organizer/login'].includes(path)) {
      window.dispatchEvent(new CustomEvent('relay-session-expired', {detail: role}));
    }
    throw new ApiError(`${message} (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
}

export function draftKey(id: string, version: number, language: string) {
  const prefix = clientState.mode === 'contest' ? `code-relay:${workspaceScope()}:draft` : 'code-relay:draft';
  return `${prefix}:${id}:v${version}:${language}`;
}
