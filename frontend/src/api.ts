export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, { ...options, headers: {'Content-Type': 'application/json', ...options?.headers} });
  } catch {
    throw new Error('Cannot reach the local judge. Start the backend and try again.');
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message = typeof data.detail === 'string' ? data.detail : 'The request could not be processed.';
    throw new Error(`${message} (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function draftKey(id: string, version: number, language: string) {
  return `code-relay:draft:${id}:v${version}:${language}`;
}
