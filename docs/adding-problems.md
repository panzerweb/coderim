# Adding a problem

```text
python tools/scaffold_problem.py your-problem
python tools/validate_problems.py
python tools/verify_problem.py your-problem
```

The scaffold creates an unpublished echo example. Replace its statement, metadata, sample data, hidden files, reference solution, and author notes. Add deliberately incorrect Python solutions under `author/incorrect_solutions/` so verification proves that common errors are detected. Run authoring tools only on trusted content.

`problem.json` is schema version 1. A lowercase hyphenated ID must equal the folder name. The metadata includes content version, title, difficulty (Easy/Medium/Hard), tags, published/draft status, category weights totaling 100, a nonempty requirement checklist, limits, and a versioned human rubric. Full defaults and validation are in `backend/app/models.py`.

Optional `reference_complexity` metadata contains `variables` (symbol-to-meaning mapping), `time_by_phase` (phase/operation-to-bound mapping), `auxiliary_space`, and `notes`. This is author guidance, never an inferred property of a participant program. The target is frozen for new submissions; existing attempts keep their saved context or remain without context. Adding reference annotations to the unchanged formatter does not alter its content version or tests.

Input limits may be configured up to 8 MiB and stdout up to 2 MiB, within operator ceilings. Keep full generated suites within the existing 100-case/20 MiB limits. Use an independent small-case oracle and explicit expected samples; scale cases should also have independently checkable patterns where possible. `tools/verify_hard_problems.py` checks every installed reference language and starter through the real judge and records authoring-only timings under `.runtime/content-verification/`.

`samples.json` is authoritative for sample inputs, expected outputs, explanations, categories, and requirement mappings. Do not duplicate executable samples in statement Markdown. `tests/manifest.json` lists hidden IDs, category, requirement IDs, and input/output paths relative to the problem root. Each official case belongs to exactly one category and at least one requirement. All weighted categories and all requirements must have evidence. Samples and hidden tests share one unique-ID namespace.

Keep `author/` private: it contains reference algorithms, generation scripts, and organizer notes. Starters are complete-program input scaffolds, not reference solutions. Missing language starters fall back to shared runner templates. All package paths must remain inside the problem folder, including resolved symlinks. The loader bounds cases (100), package case bytes (20 MB), and I/O size.

Verify fixed and reproducibly generated outputs, then test the reference against an independent small-input oracle when practical. Set status to `published` only after validation/verification succeeds; restart the backend for discovery. Invalid packages are excluded and reported in operator logs. Ordinary stdin/stdout problems require no API, frontend, or judge changes.

The seven introductory packages are reproducible with `tools/practice_problem_content.py` and verified across installed languages with `tools/verify_practice_problems.py`. See [their contracts and verification notes](introductory-problems.md). Published contests retain their pinned selections; adding packages does not add them to an existing event.

For function-based JSON challenges, see [the function-problem guide](function-problems.md). The seven packages use `tools/leetcode_problem_content.py` and `tools/verify_function_problems.py`; the four array/string additions also have `tools/array_function_content.py`. Starters provide the complete driver; participants implement the named function's return or mutation contract.

The existing text checker remains the default with unchanged normalization and serialized fields. For JSON integer arrays in any order, use `{"type":"json","value_type":"integer_array","unordered":true}`. Other supported value types are boolean, string_array, integer, and deduplicated_array, with unordered:false (the default). The deduplication shape requires exactly an integer k and an integer-array nums prefix of length k; duplicate or extra object fields are invalid. Scalar integer values exclude booleans and floats. unordered:true is allowed only for integer arrays and preserves duplicate counts during comparison. String arrays remain ordered; spaces inside strings are significant. Expected JSON is type-checked during package loading. Submission and result API shapes remain unchanged; outputs are still strings containing the serialized result. Checker metadata is frozen with contest snapshots and included in managed content fingerprints.

Increment `version` when statements, tests, mappings, limits, or judging rules materially change. Increment `rubric.version` when review criteria change. History stores the original versions and rubric; browser drafts and trajectories are separated by content version and language. Historical versions remain queryable through the history API even if they are no longer published.
