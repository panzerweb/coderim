# Adding a problem

```text
python tools/scaffold_problem.py your-problem
python tools/validate_problems.py
python tools/verify_problem.py your-problem
```

The scaffold creates an unpublished echo example. Replace its statement, metadata, sample data, hidden files, reference solution, and author notes. Add deliberately incorrect Python solutions under `author/incorrect_solutions/` so verification proves that common errors are detected. Run authoring tools only on trusted content.

`problem.json` is schema version 1. A lowercase hyphenated ID must equal the folder name. The metadata includes content version, title, difficulty (Easy/Medium/Hard), tags, published/draft status, category weights totaling 100, a nonempty requirement checklist, limits, and a versioned human rubric. Full defaults and validation are in `backend/app/models.py`.

`samples.json` is authoritative for sample inputs, expected outputs, explanations, categories, and requirement mappings. Do not duplicate executable samples in statement Markdown. `tests/manifest.json` lists hidden IDs, category, requirement IDs, and input/output paths relative to the problem root. Each official case belongs to exactly one category and at least one requirement. All weighted categories and all requirements must have evidence. Samples and hidden tests share one unique-ID namespace.

Keep `author/` private: it contains reference algorithms, generation scripts, and organizer notes. Starters are complete-program input scaffolds, not reference solutions. Missing language starters fall back to shared runner templates. All package paths must remain inside the problem folder, including resolved symlinks. The loader bounds cases (100), package case bytes (20 MB), and I/O size.

Verify fixed and reproducibly generated outputs, then test the reference against an independent small-input oracle when practical. Set status to `published` only after validation/verification succeeds; restart the backend for discovery. Invalid packages are excluded and reported in operator logs. Ordinary stdin/stdout problems require no API, frontend, or judge changes.

Increment `version` when statements, tests, mappings, limits, or judging rules materially change. Increment `rubric.version` when review criteria change. History stores the original versions and rubric; browser drafts and trajectories are separated by content version and language. Historical versions remain queryable through the history API even if they are no longer published.
