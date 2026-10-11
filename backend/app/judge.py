import tempfile
import stat
import threading
import time
from pathlib import Path
from .execution import execute
from .languages import LANGUAGES, Registry
from .models import Checker
from .problems import Case, Problem


def normalize(text: str, checker: Checker) -> str:
    if checker.normalize_line_endings:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    if checker.trim_trailing_whitespace_per_line:
        text = "\n".join(line.rstrip(" \t") for line in text.split("\n"))
    if checker.ignore_final_newline and text.endswith("\n"):
        text = text[:-1]
    return text


def assessment(problem: Problem, outcomes: list[dict], complete: bool, compile_failed=False):
    categories = []
    by_id = {r["id"]: r for r in outcomes}
    for name, weight in problem.meta.category_weights.items():
        cases = [c for c in problem.cases if c.category == name]
        passed = sum(by_id.get(c.id, {}).get("verdict") == "Accepted" for c in cases)
        attempted = sum(c.id in by_id for c in cases)
        categories.append({"category": name, "weight": weight, "passed": passed,
            "attempted": attempted, "total": len(cases)})
    requirements = []
    for req in problem.meta.requirements:
        cases = [c for c in problem.cases if req.id in c.requirements]
        passed = sum(by_id.get(c.id, {}).get("verdict") == "Accepted" for c in cases)
        attempted = sum(c.id in by_id for c in cases)
        requirements.append({"id": req.id, "text": req.text, "passed": passed, "attempted": attempted,
            "total": len(cases), "demonstrated": complete and passed == len(cases) and not compile_failed})
    correctness = round(sum(c["weight"] * c["passed"] / c["total"] for c in categories), 4) if complete else None
    requirements_score = round(100 * sum(r["demonstrated"] for r in requirements) / len(requirements), 4) if complete else None
    return {"complete": complete, "correctness": correctness, "requirements": requirements_score,
        "readability": None, "technical": None, "final": None, "review_pending": True,
        "categories": categories, "requirement_evidence": requirements}


class Judge:
    def __init__(self, registry: Registry, runtime: Path, job_budget=120.0, compile_timeout=15.0):
        self.registry, self.runtime = registry, runtime
        self.job_budget, self.compile_timeout = job_budget, compile_timeout
        self.runtime.mkdir(parents=True, exist_ok=True)

    def run(self, problem: Problem, language: str, code: str, mode="submit", stdin="",
            progress=lambda state: None, cancel: threading.Event | None = None):
        start = time.monotonic()
        official = mode == "submit"
        cases = problem.cases if official else tuple(c for c in problem.cases if c.visible)
        if mode == "custom":
            cases = (Case("custom", stdin, "", "", (), True),)
        limits = problem.meta.limits
        outcomes = []
        result = {"mode": mode, "verdict": "Judge Error", "attempted": 0, "passed": 0,
            "total": len(cases), "duration_ms": 0, "cases": [], "assessment": None,
            "diagnostics": "", "incomplete_reason": None}
        try:
            with tempfile.TemporaryDirectory(prefix="job-", dir=self.runtime) as temporary:
                directory = Path(temporary)
                build = directory / "build"
                build.mkdir()
                (build / LANGUAGES[language].filename).write_text(code, encoding="utf-8")
                compile_cmd, run_cmd = self.registry.commands(language, build)
                progress("compiling")
                compiled = execute(compile_cmd, build, "", min(self.compile_timeout, self.job_budget),
                    limits.stderr_bytes, limits.stderr_bytes, cancel)
                if cancel and cancel.is_set():
                    raise RuntimeError("Judging interrupted")
                if compiled.verdict != "OK":
                    if compiled.verdict == "Time Limit Exceeded" and self.job_budget <= self.compile_timeout:
                        result["incomplete_reason"] = "Overall job budget exhausted during compilation"
                        if official:
                            result["assessment"] = assessment(problem, [], False)
                        return result
                    result["verdict"] = "Compile Error"
                    result["diagnostics"] = (compiled.stdout + compiled.stderr)[:limits.stderr_bytes] or f"Compilation: {compiled.verdict}"
                    if official:
                        result["assessment"] = assessment(problem, [], True, compile_failed=True)
                    return result
                for artifact in build.rglob("*"):
                    if artifact.is_file():
                        artifact.chmod(artifact.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
                progress("running")
                for index, case in enumerate(cases):
                    remaining = self.job_budget - (time.monotonic() - start)
                    if remaining <= 0 or (cancel and cancel.is_set()):
                        result["incomplete_reason"] = "Overall job budget exhausted or judging interrupted"
                        break
                    cwd = directory / f"case-{index}"
                    cwd.mkdir()
                    case_timeout = min(limits.time_ms / 1000, remaining)
                    executed = execute(run_cmd, cwd, case.stdin, case_timeout,
                        limits.stdout_bytes, limits.stderr_bytes, cancel)
                    if executed.verdict == "Judge Error" or (executed.verdict == "Time Limit Exceeded" and remaining < limits.time_ms / 1000):
                        result["incomplete_reason"] = "Overall job budget exhausted or judging interrupted"
                        break
                    verdict = executed.verdict
                    if verdict == "OK":
                        verdict = "Completed" if mode == "custom" else ("Accepted" if normalize(executed.stdout, problem.meta.checker) == normalize(case.expected, problem.meta.checker) else "Wrong Answer")
                    outcome = {"id": case.id, "verdict": verdict, "duration_ms": executed.duration_ms}
                    outcomes.append(outcome)
                    if case.visible:
                        result["cases"].append({**outcome, "stdout": executed.stdout, "stderr": executed.stderr,
                            "exit_code": executed.exit_code, "input": case.stdin,
                            "expected_output": None if mode == "custom" else case.expected})
                complete = len(outcomes) == len(cases)
                result["attempted"] = len(outcomes)
                result["passed"] = sum(r["verdict"] == "Accepted" for r in outcomes)
                first_failure = next((r["verdict"] for r in outcomes if r["verdict"] not in ("Accepted", "Completed")), None)
                result["verdict"] = (first_failure or ("Completed" if mode == "custom" else "Accepted")) if complete else "Judge Error"
                if official:
                    result["assessment"] = assessment(problem, outcomes, complete)
        except Exception:
            # Infrastructure details can include paths or hidden data. Keep them in operator logs only.
            import logging
            logging.exception("Execution infrastructure failed")
            result["verdict"] = "Judge Error"
            result["incomplete_reason"] = "Execution infrastructure failed or judging was interrupted"
            result["attempted"] = len(outcomes)
            result["passed"] = sum(r["verdict"] == "Accepted" for r in outcomes)
            if official:
                result["assessment"] = assessment(problem, outcomes, False)
        finally:
            result["duration_ms"] = round((time.monotonic() - start) * 1000, 2)
        return result
