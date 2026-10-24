import logging
import queue
import threading
import time
import uuid
from .judge import Judge
from .storage import Storage


class Jobs:
    def __init__(self, judge: Judge, storage: Storage, capacity=10, retention=3600):
        self.judge, self.storage = judge, storage
        self.retention = retention
        self.queue = queue.Queue(maxsize=capacity)
        self.lock = threading.RLock()
        self.records = {}
        self.stop = threading.Event()
        self.worker = threading.Thread(target=self._work, name="relay-judge", daemon=True)
        self.worker.start()

    def _prune(self):
        cutoff = time.monotonic() - self.retention
        for key in list(self.records):
            finished = self.records[key].get("finished")
            if finished is not None and finished < cutoff:
                del self.records[key]

    def enqueue(self, request, problem, mode):
        with self.lock:
            self._prune()
            if self.stop.is_set() or self.queue.full():
                raise queue.Full
            key = str(uuid.uuid4())
            if mode == "submit":
                self.storage.create(key, request, problem.meta.rubric.model_dump(),
                    problem.meta.reference_complexity.model_dump() if problem.meta.reference_complexity else None)
            self.records[key] = {"id": key, "state": "queued", "result": None, "attempt_id": key if mode == "submit" else None}
            self.queue.put_nowait((key, request, problem, mode))
            return {"job_id": key, "attempt_id": key if mode == "submit" else None}

    def get(self, key):
        with self.lock:
            self._prune()
            record = self.records.get(key)
            return {k: v for k, v in record.items() if k != "finished"} if record else None

    def _work(self):
        while not self.stop.is_set():
            try:
                key, request, problem, mode = self.queue.get(timeout=0.1)
            except queue.Empty:
                with self.lock:
                    self._prune()
                continue
            def progress(state):
                with self.lock:
                    self.records[key]["state"] = state
                if mode == "submit":
                    self.storage.status(key, state)
            try:
                result = self.judge.run(problem, request.language, request.code, mode,
                    getattr(request, "stdin", ""), progress, self.stop)
                if mode == "submit":
                    self.storage.complete(key, result)
                with self.lock:
                    self.records[key].update(state="failed" if result["verdict"] == "Judge Error" else "completed",
                        result=result, finished=time.monotonic())
            except Exception:
                logging.exception("Judge worker infrastructure failed")
                with self.lock:
                    self.records[key].update(state="failed", result={"verdict": "Judge Error",
                        "incomplete_reason": "Judge worker infrastructure failed"}, finished=time.monotonic())
            finally:
                self.queue.task_done()

    def close(self):
        self.stop.set()
        self.worker.join(timeout=20)
        if self.worker.is_alive():
            raise RuntimeError("Judge worker failed to stop")
