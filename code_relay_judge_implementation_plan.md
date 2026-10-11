# Code Relay Judge — Project Structure and Implementation Plan

**Status:** Historical architecture blueprint; the application is now implemented. See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the reconciled specification and [README.md](README.md) for setup and verification. Full-suite scoring and SQLite history supersede this document's initial stop-at-first-failure and in-memory-only defaults.  
**Deployment:** Local computer only.  
**Initial content:** One or two machine problems, with support for adding more.  
**Stack:** Vue, TypeScript, FastAPI, and configurable local language runners.  
**AI integration:** None. Problem authoring assistance happens outside the application.

## 1. Project goal

Build a small LeetCode-style workspace where participants read a machine problem, write a complete program, run sample or custom inputs, and submit against official test cases.

Start small while keeping the problem catalog, language runners, and judging engine independent. Adding an ordinary input/output problem should require adding a problem folder, not editing frontend components or creating a new API endpoint.

Here, scalability means maintainable extension to more problems and languages. It does not imply a distributed platform or unlimited simultaneous execution.

## 2. Scope and requirements

### Participant features

- Problem catalog with dynamically discovered, published problems.
- Problem statement, input/output rules, constraints, examples, and explanations.
- Monaco code editor, language selector, and starter code.
- Run all sample cases or one custom input.
- Submit against samples and hidden tests.
- Compilation errors, runtime errors, execution verdicts, and test counts.
- Browser-local drafts keyed by problem, problem version, and language.
- Explicit reset-to-starter action with confirmation if code will be overwritten.
- Resizable statement/editor panels and readable results.
- No login, account, remote service, or AI key.

### Organizer and developer features

- File-based problem packages with schema validation.
- Automatic discovery of new problem folders.
- A problem scaffold command and validation command.
- Reference solutions, test generators, and intentionally incorrect solutions for verification.
- Language availability checks.
- Configurable judge limits within operator-defined bounds.
- Local startup scripts and setup documentation for VS Code and Windows.

### Deferred features

Leaderboards, shared competition sessions, accounts, cloud hosting, interactive problems, function-signature submissions, and a browser-based problem editor are outside the initial scope. Problems are added through the repository.

## 3. Architecture

| Layer | Responsibility |
|---|---|
| Vue frontend | Editor, statements, problem selection, drafts, and results |
| FastAPI API | Validate requests and expose participant-safe problem data |
| Problem repository | Discover, validate, and load versioned problem packages |
| Judge service | Coordinate compilation, execution, comparison, and verdicts |
| Language registry | Map approved language IDs to compilers, interpreters, and starter templates |
| Execution backend | Manage processes or containers, limits, and cleanup |
| Local content | Statements, samples, hidden cases, reference code, and author notes |

The frontend talks only to the API. The judge reads test files from the problem repository. Language adapters do not know problem-specific algorithms.

A submission contains a complete program that reads standard input and writes standard output. Reference solutions provide the problem's algorithm; they are authoring tools, not code injected into participant submissions.

## 4. Proposed repository structure

```text
code-relay-judge/
├── README.md
├── IMPLEMENTATION_PLAN.md
├── .gitignore
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       │   └── index.ts
│       ├── features/
│       │   ├── problems/
│       │   │   ├── api.ts
│       │   │   ├── types.ts
│       │   │   ├── pages/ProblemCatalogPage.vue
│       │   │   └── components/ProblemStatement.vue
│       │   └── workspace/
│       │       ├── api.ts
│       │       ├── types.ts
│       │       ├── stores/workspace.ts
│       │       ├── composables/useDraftStorage.ts
│       │       ├── pages/WorkspacePage.vue
│       │       └── components/
│       │           ├── CodeEditor.vue
│       │           ├── LanguageSelector.vue
│       │           ├── RunControls.vue
│       │           ├── CustomInputPanel.vue
│       │           └── JudgeResults.vue
│       └── shared/
│           ├── api/client.ts
│           └── components/
├── backend/
│   ├── pyproject.toml
│   ├── dependency-lock-file
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── lifespan.py
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   ├── problems.py
│   │   │   ├── languages.py
│   │   │   └── submissions.py
│   │   ├── schemas/
│   │   │   ├── problem.py
│   │   │   ├── submission.py
│   │   │   └── result.py
│   │   ├── problems/
│   │   │   ├── repository.py
│   │   │   ├── loader.py
│   │   │   └── validator.py
│   │   └── judge/
│   │       ├── service.py
│   │       ├── jobs.py
│   │       ├── comparator.py
│   │       ├── verdicts.py
│   │       ├── languages/
│   │       │   ├── base.py
│   │       │   ├── registry.py
│   │       │   ├── python.py
│   │       │   ├── javascript.py
│   │       │   ├── cpp.py
│   │       │   └── java.py
│   │       └── execution/
│   │           ├── base.py
│   │           ├── local.py
│   │           ├── process_control.py
│   │           └── docker.py
│   └── tests/
│       ├── test_problem_loading.py
│       ├── test_comparison.py
│       ├── test_judge_integration.py
│       └── fixtures/
├── problems/
│   └── broken-code-formatter/
│       ├── problem.json
│       ├── statement.md
│       ├── samples.json
│       ├── tests/
│       │   ├── manifest.json
│       │   ├── basic-valid.in
│       │   ├── basic-valid.out
│       │   ├── escaped-quotes.in
│       │   └── escaped-quotes.out
│       ├── starters/
│       │   ├── main.py
│       │   ├── main.js
│       │   ├── main.cpp
│       │   └── Main.java
│       └── author/
│           ├── editorial.md
│           ├── reference.py
│           ├── generate_tests.py
│           └── incorrect_solutions/
├── templates/
│   ├── problem/
│   └── languages/
├── tools/
│   ├── scaffold_problem.py
│   ├── validate_problems.py
│   └── verify_problem.py
├── scripts/
│   ├── setup.ps1
│   ├── start.ps1
│   └── start.sh
└── docs/
    ├── adding-problems.md
    ├── adding-languages.md
    ├── judging-rules.md
    └── local-setup.md
```

The dependency lock filename is chosen when the Python package manager is selected. The Docker executor is a later extension; the first implementation uses the local executor.

Problem content remains outside the frontend's public directory and build assets. Temporary runs and local job artifacts belong in an ignored runtime directory or the operating system's temporary directory.

## 5. Standard problem package

Each problem uses a unique lowercase slug as its folder name and ID. Discovery scans only direct children of the configured problem root.

### problem.json

Example proposed schema:

```json
{
  "schema_version": 1,
  "id": "broken-code-formatter",
  "version": 1,
  "title": "The Broken Code Formatter",
  "difficulty": "intermediate",
  "tags": ["strings", "stacks", "parsing"],
  "status": "published",
  "order": 1,
  "submission_mode": "stdin_stdout",
  "statement_file": "statement.md",
  "samples_file": "samples.json",
  "tests_manifest": "tests/manifest.json",
  "limits": {
    "time_ms": 2000,
    "source_bytes": 65536,
    "stdin_bytes": 1048576,
    "stdout_bytes": 1048576,
    "stderr_bytes": 65536
  },
  "checker": {
    "type": "text",
    "normalize_line_endings": true,
    "trim_trailing_whitespace_per_line": true,
    "ignore_final_newline": true
  },
  "starters": {
    "python": "starters/main.py",
    "javascript": "starters/main.js",
    "cpp": "starters/main.cpp",
    "java": "starters/Main.java"
  }
}
```

All paths are relative to the problem folder and must resolve inside it. Reject traversal, escaping symlinks, duplicate IDs, unsupported schema versions, and unknown checker types.

Separate schema version from content version. Increment content version when statements, tests, or judging rules materially change.

Languages come from the global registry. Provide shared fallback starters when a problem has no language-specific starter.

### statement.md

Use these sections:

1. Title and problem description.
2. Exact task and rules.
3. Input format.
4. Output format.
5. Constraints.
6. Sample explanations.

Store executable sample inputs and outputs in samples.json as the authoritative source. Render sample blocks from that file to avoid conflicting copies in Markdown.

### samples.json

```json
[
  {
    "id": "sample-01",
    "input": "print(\"This [ is not a bracket!\")\n",
    "expected_output": "VALID\n",
    "explanation": "The square bracket is inside a double-quoted string."
  }
]
```

### tests/manifest.json

```json
{
  "cases": [
    {
      "id": "basic-valid",
      "input_file": "tests/basic-valid.in",
      "output_file": "tests/basic-valid.out",
      "category": "basic"
    },
    {
      "id": "escaped-quotes",
      "input_file": "tests/escaped-quotes.in",
      "output_file": "tests/escaped-quotes.out",
      "category": "escaping"
    }
  ]
}
```

Files preserve whitespace, backslashes, and large test data without cumbersome JSON escaping. IDs must be unique. Manifest paths are relative to the problem root, not the manifest directory.

Official judging runs samples plus hidden cases. All cases have equal pass/fail significance in the first release. Acceptance requires passing every case; no weighted scoring is initially needed.

## 6. Adding a new machine problem

The application has no AI connection. When you ask ChatGPT to add a problem, provide the repository or current files so the authoring changes can be made against the actual project.

Suggested request:

> Add this machine problem to Code Relay Judge using the existing problem-package format. Include the statement, exact input/output rules, verified samples, hidden tests, reference solution, starter programs, and author notes. Validate it and preserve the existing judge behavior.

Authoring workflow:

1. Define the task, constraints, deterministic output rules, and edge cases.
2. Create a folder using the scaffold tool.
3. Fill in metadata, statement, samples, and starters.
4. Write a correct reference solution.
5. Add fixed boundary cases and reproducible generated cases.
6. Verify expected outputs, using an independent brute-force oracle for small inputs when practical.
7. Run deliberately incorrect solutions to confirm important tests detect common mistakes.
8. Validate the package, then set status to published.
9. Restart the backend; the catalog discovers the new problem automatically.

Proposed commands, to be implemented:

```text
python tools/scaffold_problem.py delivery-route
python tools/validate_problems.py
python tools/verify_problem.py delivery-route
```

For a standard deterministic stdin/stdout problem, no new route, frontend page, database migration, or judge algorithm is required. A new language, interactive task, or output with many valid answers can require a runner or checker extension.

A generator and reference solution run during authoring. Participant submissions are judged against saved inputs and expected outputs; the judge does not regenerate expected answers for each submission.

## 7. Judging contract

### Run

Two modes: all visible samples, or one custom input.

For custom input, display stdout, stderr, exit status, and execution duration. There is no correctness verdict unless an expected output was explicitly supplied; the first release does not accept a custom expected output.

### Submit

Compile once, then run each case in a fresh process with a fresh working directory. Reuse the compiled artifact as read-only input where supported. Stop at the first failing case in the initial version and report attempted, passed, and total case counts clearly.

Pin the loaded problem version to the job so reloads cannot change its tests mid-submission.

### Comparison

Normalize CRLF and lone CR to LF. Strip spaces and tabs at the end of each line if configured. Ignore one final line terminator if configured. Preserve leading whitespace, internal whitespace, blank lines, letter case, and text content.

Do not use a blanket strip operation that removes meaningful indentation or blank lines. Extra prompts and debug output cause Wrong Answer.

Introduce a checker interface with a text implementation initially. Future numeric-tolerance or special-output checkers must be explicitly configured and separately validated. Do not load arbitrary checker code from participant requests.

### Verdicts

Accepted, Wrong Answer, Compile Error, Runtime Error, Time Limit Exceeded, Output Limit Exceeded, and Judge Error.

Compilation has a separate operator-controlled timeout and diagnostic cap. Memory Limit Exceeded is available only if the execution backend can actually enforce and identify it; do not claim a hard memory limit for the basic cross-platform local runner.

For hidden cases, return verdicts and aggregate counts, not inputs, expected output, or captured program output. Program output can echo hidden input. Sample and custom runs may expose bounded output and diagnostics.

## 8. Language extension

| ID | File | Toolchain |
|---|---|---|
| python | main.py | Python interpreter |
| javascript | main.js | Node.js |
| cpp | main.cpp | C++ compiler and executable |
| java | Main.java | Java compiler and runtime |

Each adapter supplies its source filename, optional compile command, run command, starter template, editor language, and availability probe.

Build commands as argument arrays with shell execution disabled. Accept only registered language IDs; participants cannot supply executable paths or command-line flags.

The backend detects missing toolchains and disables unavailable languages in the UI. Any language is possible through a configured adapter and installed toolchain; arbitrary language support is not automatic.

## 9. API and job lifecycle

| Method and path | Purpose |
|---|---|
| GET /api/problems | Published catalog metadata |
| GET /api/problems/{id} | Statement, samples, version, limits, and starters |
| GET /api/languages | Configured language availability |
| POST /api/runs | Queue a sample or custom-input run |
| POST /api/submissions | Queue official judging |
| GET /api/jobs/{job_id} | Poll job status and permitted results |

Return a job ID immediately. States: queued, compiling, running, completed, failed. Execution infrastructure failure produces Judge Error, distinct from participant Runtime Error.

Use one worker by default to avoid multiple CPU-heavy submissions distorting execution times. Bound the queue, reject overload cleanly, and expire completed jobs after a configurable retention period.

The first release keeps job metadata in memory. Restarting the backend loses job history and cancels active work; this is documented behavior. Browser drafts remain intact.

API validation covers code size, custom-input size, language availability, valid published problem IDs, and supported run modes. CPU-bound or blocking subprocess work must not block the API event loop.

## 10. Local execution and operating model

Bind the backend and frontend to loopback by default. Allow only the intended local frontend origin, validate origins on mutation requests, and serve all editor assets locally after installation.

The local executor is intended for trusted code on the user's own machine. Subprocess execution can read or modify resources available to its operating-system user. Timeouts and temporary directories do not form a security sandbox.

Implement:

- Unique submission and per-case directories.
- Separate compile and execution timeouts.
- Concurrent bounded capture of stdout and stderr.
- Process-tree termination, including Windows-specific handling.
- Cleanup on success, failure, timeout, and application shutdown.
- Configured executable paths, fixed commands, and a minimal controlled environment.
- Bounded queue and maximum cases/bytes per package.

For competition submissions from untrusted participants, implement the Docker executor before enabling organizer-hosted access. Use no network, restricted mounts, a non-root user, process limits, and CPU/memory limits. Containers add resource overhead; benchmark on the actual event machine.

Hidden tests on a participant-owned computer are inspectable. Local practice can hide them in the interface, but organizer-controlled judging is needed to keep them meaningfully private.

After dependencies, editor assets, and toolchains are installed, normal operation should require no internet connection.

## 11. Initial problem: The Broken Code Formatter

Input is exactly one source-code line, containing 1–100,000 ASCII characters excluding the transport line ending. Spaces are preserved. Output is VALID or INVALID.

Rules:

- Match (), [], and {} only outside quoted strings.
- A single or double quote starts the corresponding string outside a string.
- Only the matching quote closes that string.
- Within a string, a backslash escapes exactly the next character.
- Outside strings, a backslash has no escaping effect.
- Comments and backticks have no special syntax.
- Reject incorrect nesting, extra closing brackets, unclosed brackets, unclosed strings, and a dangling escape inside a string.

The reference algorithm uses a bracket stack, active quote state, and escape state. Target time is O(L); worst-case space is O(L).

Test categories: nesting, bracket types, opposite quotes inside strings, escaped quotes, odd/even runs of backslashes, ordinary outside-string backslashes, incomplete input constructs, preserved spaces, and maximum-length input.

Verify every published sample. The prior candidate problems contained inconsistent sliding-window samples; never copy those outputs without independent verification.

## 12. Implementation phases and exit criteria

| Phase | Work | Exit criterion |
|---|---|---|
| 1. Contracts and content | Schemas, package format, first problem, reference solution | Package validates; samples and boundary outputs verified |
| 2. Core judge | Python adapter, comparator, local execution, verdicts | Correct, wrong, crashing, looping, and output-heavy programs receive correct results |
| 3. API and jobs | Catalog, safe DTOs, bounded worker, polling | APIs remain responsive during judging; hidden data is excluded |
| 4. Frontend | Catalog, editor, statement, run/submit panels, drafts | Complete participant flow works; refresh restores drafts |
| 5. Languages | JavaScript, C++, Java, availability probes | Representative programs pass in each installed language |
| 6. Authoring tools | Scaffold, validator, verifier, documentation | A second problem appears without modifying core judge or frontend |
| 7. Packaging | Windows setup/start scripts, README, cleanup | Clean-machine setup documented; local offline runtime verified |
| 8. Optional isolation | Docker executor and enforced resource limits | Isolation and limit behavior tested before untrusted judging |

No database is required initially. Add SQLite only when durable submission history or competition sessions become an actual requirement.

## 13. Verification strategy

- Problem loading: valid package, missing file, duplicate ID, unsupported schema, and unsafe path.
- Comparator: line endings, final newline, trailing spaces, leading spaces, case, and extra blank lines.
- Judge integration: acceptance, wrong output, compile failure, runtime failure, timeout, output overflow, cleanup, and child-process termination.
- API: hidden-test privacy, input limits, unavailable languages, queue overload, and job expiry.
- Content: reference outputs and independent small-case oracle where practical; fixed seed for generated cases.
- Frontend: selecting problems/languages, draft recovery, sample runs, custom input, submission results, and unavailable backend.
- Extension: add a second problem package and confirm discovery and judging without core code changes.

Performance limits are provisional until benchmarked across supported languages on the intended machine. Avoid unsupported promises about equal execution speed across languages.

## 14. Definition of done

The initial release is complete when:

- A participant can select a problem, write code, run tests, and submit without an account.
- Official judging is deterministic for valid deterministic programs.
- Correct and intentionally faulty programs produce the expected verdicts.
- The first problem has verified samples and meaningful hidden cases.
- Configured installed languages work and missing toolchains are clearly indicated.
- Drafts survive page refresh.
- A new ordinary problem can be added solely through a validated problem package.
- The application contains no AI API, cloud dependency, or required database.
- Setup, problem authoring, language extension, limits, and execution assumptions are documented.

## 15. Future implementation request

> Implement Code Relay Judge from this plan using Vue, TypeScript, Monaco Editor, and FastAPI. Start with The Broken Code Formatter and a reusable problem-package loader. Keep execution local, use stdin/stdout submissions, and do not integrate AI. Build and verify the core judge before adding the frontend and additional languages. Include problem-authoring tools, Windows setup instructions, and a second-problem extension check.

