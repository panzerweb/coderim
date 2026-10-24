"""Reuse the original compile-once judge behind the team-owned job queue."""
from .judge import Judge


class LocalContestJudge:
    def __init__(self, registry, runtime, job_budget=120):
        self.judge = Judge(registry, runtime, job_budget)

    def run(self, problem, language, code, mode='submit', stdin='',
            progress=lambda state: None, cancel=None, attempt_id=None):
        return self.judge.run(problem, language, code, mode, stdin, progress, cancel)
