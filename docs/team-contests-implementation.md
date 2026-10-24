# Hosted team contests: implemented specification

**Current revision:** team management and judging are independent. Local team contests reuse the original automatic judge without a provider; use [the walkthrough](team-contest-quickstart.md). Organizers can publish without verification and explicitly start a published waiting event's full duration. The [Render guide](hosted-contests.md) describes the provider-free trusted-code Docker deployment; managed judging below remains optional through `RELAY_EXECUTOR=managed`.

This adapts the supplied **Code Relay — Team Sessions & Submission History Implementation Plan** to the existing file-based problem repository. The approved follow-up takes precedence: the initial shared contest window is 210 minutes; team cookies last four hours independently. There are no participant accounts, AI analysis, attempt penalties, or ranking tie-breakers.

## Data and identity

Schema 3 extends `attempts` with nullable team/contest ownership, an idempotency key, request fingerprint, and admission timestamp. New tables store contests, teams, organizers, sessions, audits, persistent login limits, and private provider case progress. Migrations retain legacy source, results, rubric, review, and complexity JSON without reinterpreting scores. SQLite enables WAL, foreign keys, and a five-second busy timeout. All writes use short transactions; Argon2 and network calls occur outside them.

Teams are pre-registered within a contest. Their display names are preserved and their lookup names are trimmed/case-folded. Random join codes are displayed once, stored as Argon2id hashes, and rotated when lost. One browser session is active per team; tabs share its cookie. Session expiry, logout, code rotation, deactivation, and organizer resets revoke access. Organizer credentials are bootstrapped through a local management command, with an independent opaque session. Neither role uses browser storage for credentials or tokens.

Production uses host-only `__Host-` cookies with Secure, HttpOnly, SameSite=Strict, and Path=/. Authenticated mutations require approved Origin, JSON, and a session-bound CSRF header. Both login routes use generic invalid-credential messages, dummy Argon2 verification for unknown principals, and persisted configurable rate limits. Every source, job, history, and compatibility route checks ownership; unowned history is organizer-only in hosted mode.

## Contest behavior

Organizers create the schedule in Asia/Manila, select problems, and publish private, integrity-checked snapshots. Snapshots contain statements, starters, rubric, limits, samples, hidden cases, and complexity targets; they exclude author solutions/notes. The database stores selected versions and checksums. Published snapshots are immutable. Provider approval covers the exact pinned judging content, independently of later repository changes.

The UTC server clock determines waiting/active/ended. Waiting teams cannot retrieve problems. After start, schedule editing preserves the start and can extend the deadline; an explicit confirmed action ends an active event early. Both actions are audited. Runs and new official recordings require an active window. The admission timestamp determines timeliness; finishing after the deadline is allowed. Ended teams retain their own read-only history.

Record Submission confirms and freezes source, and retries reuse the same idempotency key. Matching replay retrieves the original job even after the deadline. Reusing a key for different content conflicts. Distinct Accepted problem IDs count as solved, across languages and repeated acceptances. Total official attempts includes failed/incomplete attempts. Sample/custom runs never create official history.

Draft keys include contest, team, problem version, and language. Logout/revocation clears in-memory identity/workspace without deleting the returning team's browser-local draft. Drafts are local convenience storage, not encrypted protection from someone with access to the same browser profile.

## Execution and assessment

`RELAY_MODE=contest` selects team ownership/authentication and the bounded queue. `RELAY_EXECUTOR=local` uses the original compile-once Registry/Judge through `LocalContestJudge`; this is the provider-free local default. Public deployment requires explicit trusted-code enablement. `RELAY_EXECUTOR=managed` explicitly selects the optional RemoteJudge with independent asynchronous case executions, disabled network and configured limits. Compilation may repeat per case. Managed failures never switch to local execution. Both use the same comparator, category weights, requirement evidence, 50/20/15/15 scoring, and deterministic first-failure verdict.

Official provider tokens and case results persist privately. Restarted jobs poll known tokens, reuse completed case progress, and retain the same official attempt. A persisted creating/delivery-unknown state becomes an infrastructure failure rather than a blind creation retry. Incomplete judging has no finalized automated scores. Hidden-case output and provider credentials/tokens never appear in participant history or polling.

Organizer reviews edit the existing readability/technical dimensions and complexity annotations. Teams can read saved feedback beside immutable source. Reference context stays frozen; measured runtime never becomes a Big-O claim.

## Verification and rollout

Backend tests cover migrations, old ratings, ownership, CSRF, throttling, expiry/revocation, concurrent joins, five teams, queue overload, manual start, deadline eligibility, idempotency, provider-free execution, and optional provider failures/token recovery. Five temporary fixture problems demonstrate five solved versus four without adding production problems. Browser tests use separate organizer/team contexts and real local execution for all three problem suites. Optional managed execution has separate mock tests. Practice-mode content/scoring/complexity and nine example programs remain regression checks.

Only managed execution uses the opt-in live provider checks; contest creation/publication do not require them. Provider-free contests should rehearse installed runtimes and real suites instead. Local unfinished work becomes interrupted on restart rather than being replayed; completed history/reviews survive. Local startup generates a persistent secret and prompts for the initial organizer account. Both deployment models require a private rehearsal and verified backups before the event.
