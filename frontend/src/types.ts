export interface CatalogProblem {
  id: string; version: number; title: string; difficulty: string; tags: string[]; suggested_duration_minutes: number;
}
export interface Rubric {
  version: number; weights: Record<string, number>; readability: string[]; technical: string[];
}
export interface Problem extends CatalogProblem {
  statement: string;
  samples: {id: string; input: string; expected_output: string; explanation: string}[];
  limits: {time_ms: number; source_bytes: number; stdin_bytes: number; stdout_bytes: number; memory_mb: number; memory_enforced: boolean};
  starters: Record<string, string>;
  requirements: {id: string; text: string}[];
  category_weights: Record<string, number>;
  rubric: Rubric;
}
export interface Language {id: string; label: string; editor_language: string; available: boolean; reason: string; starter: string}
export interface Assessment {
  complete: boolean; correctness: number | null; requirements: number | null; readability: number | null; technical: number | null;
  final: number | null; review_pending: boolean;
  categories: {category: string; weight: number; passed: number; attempted: number; total: number}[];
  requirement_evidence: {id: string; text: string; passed: number; attempted: number; total: number; demonstrated: boolean}[];
}
export interface Result {
  mode: string; verdict: string; attempted: number; passed: number; total: number; duration_ms: number;
  diagnostics: string; incomplete_reason: string | null; assessment: Assessment | null;
  cases?: {id: string; verdict: string; duration_ms: number; stdout: string; stderr: string; input: string; expected_output: string | null; exit_code: number | null}[];
}
export interface Review {readability: number[]; technical: number[]; rationale: string; updated_at?: string}
export interface Attempt {
  id: string; created_at: string; problem_id: string; problem_version: number; language: string; code?: string;
  status: string; rubric: Rubric; result: Result | null; review: Review | null;
}
export interface Job {id: string; state: string; result: Result | null; attempt_id: string | null}
