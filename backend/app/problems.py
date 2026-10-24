import json
from dataclasses import dataclass
from pathlib import Path
from pydantic import TypeAdapter
from .models import Manifest, ProblemMetadata, Sample
from .languages import LANGUAGES


MAX_CASES = 100
MAX_PACKAGE_BYTES = 20 * 1024 * 1024


def safe_path(root: Path, name: str) -> Path:
    candidate = Path(name)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Unsafe package path: {name}")
    result = (root / candidate).resolve()
    if not result.is_relative_to(root.resolve()) or not result.is_file():
        raise ValueError(f"Missing or escaping package file: {name}")
    return result


def read_text(root, name):
    path = safe_path(root, name)
    if path.stat().st_size > MAX_PACKAGE_BYTES:
        raise ValueError("Package file is too large")
    with path.open(encoding="utf-8", newline="") as stream:
        return stream.read()


@dataclass(frozen=True)
class Case:
    id: str
    stdin: str
    expected: str
    category: str
    requirements: tuple[str, ...]
    visible: bool = False


@dataclass(frozen=True)
class Problem:
    meta: ProblemMetadata
    statement: str
    samples: tuple[Sample, ...]
    cases: tuple[Case, ...]
    starters: dict[str, str]

    def catalog(self):
        m = self.meta
        return {"id": m.id, "version": m.version, "title": m.title, "difficulty": m.difficulty,
            "tags": m.tags, "suggested_duration_minutes": m.suggested_duration_minutes}

    def public(self):
        return {**self.catalog(), "statement": self.statement,
            "samples": [{"id": s.id, "input": s.input, "expected_output": s.expected_output,
                "explanation": s.explanation} for s in self.samples],
            "limits": {**self.meta.limits.model_dump(), "memory_enforced": False},
            "starters": self.starters, "requirements": [r.model_dump() for r in self.meta.requirements],
            "category_weights": self.meta.category_weights, "rubric": self.meta.rubric.model_dump(),
            "reference_complexity": self.meta.reference_complexity.model_dump() if self.meta.reference_complexity else None}


def load_problem(root: Path) -> Problem:
    meta = ProblemMetadata.model_validate_json(read_text(root, "problem.json"))
    if meta.id != root.name:
        raise ValueError("Problem ID must match its folder")
    samples = TypeAdapter(list[Sample]).validate_json(read_text(root, meta.samples_file))
    manifest = Manifest.model_validate_json(read_text(root, meta.tests_manifest))
    cases = [Case(s.id, s.input, s.expected_output, s.category, tuple(s.requirements), True) for s in samples]
    for c in manifest.cases:
        cases.append(Case(c.id, read_text(root, c.input_file), read_text(root, c.output_file), c.category, tuple(c.requirements)))
    if not cases or len(cases) > MAX_CASES:
        raise ValueError("Official suite must contain 1–100 cases")
    if len({c.id for c in cases}) != len(cases):
        raise ValueError("Duplicate sample/hidden case ID")
    reqs = {r.id for r in meta.requirements}
    seen_requirements, seen_categories = set(), set()
    total_bytes = 0
    for c in cases:
        if c.category not in meta.category_weights or not set(c.requirements) <= reqs:
            raise ValueError("Unknown category or requirement mapping")
        if len(set(c.requirements)) != len(c.requirements):
            raise ValueError("Duplicate requirement mapping")
        seen_categories.add(c.category)
        seen_requirements.update(c.requirements)
        input_bytes, output_bytes = len(c.stdin.encode()), len(c.expected.encode())
        if input_bytes > meta.limits.stdin_bytes or output_bytes > meta.limits.stdout_bytes:
            raise ValueError("Case exceeds configured I/O limits")
        total_bytes += input_bytes + output_bytes
    if total_bytes > MAX_PACKAGE_BYTES or seen_requirements != reqs or seen_categories != set(meta.category_weights):
        raise ValueError("Missing category/requirement coverage or package too large")
    if set(meta.starters) - set(LANGUAGES):
        raise ValueError("Unknown starter language")
    starters = {key: read_text(root, meta.starters[key]) if key in meta.starters else lang.starter
        for key, lang in LANGUAGES.items()}
    return Problem(meta, read_text(root, meta.statement_file), tuple(samples), tuple(cases), starters)


class Repository:
    def __init__(self, root: Path):
        self.problems = {}
        self.errors = {}
        root = root.resolve()
        if not root.is_dir():
            raise ValueError("Problem root does not exist")
        for folder in sorted(root.iterdir()):
            if not folder.is_dir() or folder.name.startswith("."):
                continue
            try:
                if folder.is_symlink() or not folder.resolve().is_relative_to(root):
                    raise ValueError("Problem folders must stay inside the problem root")
                p = load_problem(folder)
                if p.meta.id in self.problems:
                    raise ValueError("Duplicate problem ID")
                self.problems[p.meta.id] = p
            except (ValueError, OSError) as error:
                self.errors[folder.name] = str(error)

    def published(self):
        return sorted((p for p in self.problems.values() if p.meta.status == "published"),
            key=lambda p: (p.meta.order, p.meta.id))

    def get(self, key):
        problem = self.problems.get(key)
        return problem if problem and problem.meta.status == "published" else None
