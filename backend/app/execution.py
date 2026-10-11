"""Bounded pipes and whole-process-tree cleanup; trusted local code, not a sandbox."""
import ctypes
import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path


class WindowsJob:
    def __init__(self, process):
        from ctypes import wintypes
        class Basic(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ("ReadOperationCount", "WriteOperationCount",
                "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]
        class Extended(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", IO),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel.SetInformationJobObject.restype = wintypes.BOOL
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        self.kernel = kernel
        self.handle = kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        info = Extended()
        info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())
        # The process can finish before assignment; then there is no live tree to retain.
        if not kernel.AssignProcessToJobObject(self.handle, int(process._handle)) and process.poll() is None:
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


@dataclass
class Execution:
    verdict: str
    stdout: str
    stderr: str
    exit_code: int | None
    duration_ms: float


def execute(command: list[str], cwd: Path, stdin: str, timeout: float,
            stdout_limit: int, stderr_limit: int, cancel: threading.Event | None = None) -> Execution:
    started = time.monotonic()
    env = {key: os.environ[key] for key in ("PATH", "SystemRoot", "WINDIR", "COMSPEC") if key in os.environ}
    env.update({"TEMP": str(cwd), "TMP": str(cwd), "TMPDIR": str(cwd), "PYTHONIOENCODING": "utf-8"})
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=False, start_new_session=os.name != "nt",
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    job = None
    overflow = threading.Event()
    buffers = [bytearray(), bytearray()]

    def read(pipe, buffer, limit):
        try:
            while chunk := pipe.read1(4096):
                remaining = limit - len(buffer)
                buffer.extend(chunk[:max(0, remaining)])
                if len(chunk) > remaining:
                    overflow.set()
        finally:
            pipe.close()

    def write():
        try:
            process.stdin.write(stdin.encode("utf-8"))
            process.stdin.flush()
        except (BrokenPipeError, OSError):
            pass
        finally:
            process.stdin.close()

    def cleanup():
        if os.name == "nt":
            if job:
                job.close()
            if process.poll() is None:
                process.kill()
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    threads = []
    verdict = "OK"
    try:
        if os.name == "nt":
            job = WindowsJob(process)
        threads = [threading.Thread(target=read, args=(process.stdout, buffers[0], stdout_limit), daemon=True),
            threading.Thread(target=read, args=(process.stderr, buffers[1], stderr_limit), daemon=True),
            threading.Thread(target=write, daemon=True)]
        for thread in threads:
            thread.start()
        while process.poll() is None:
            if cancel and cancel.is_set():
                verdict = "Judge Error"
                break
            if overflow.is_set():
                verdict = "Output Limit Exceeded"
                break
            if time.monotonic() - started >= timeout:
                verdict = "Time Limit Exceeded"
                break
            time.sleep(0.005)
    finally:
        cleanup()
        process.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=5)
        if not threads:
            for pipe in (process.stdin, process.stdout, process.stderr):
                pipe.close()
    if any(thread.is_alive() for thread in threads):
        raise RuntimeError("Process pipes did not close after tree termination")
    if verdict == "OK":
        if overflow.is_set():
            verdict = "Output Limit Exceeded"
        elif process.returncode:
            verdict = "Runtime Error"
    return Execution(verdict, buffers[0].decode("utf-8", errors="replace"),
        buffers[1].decode("utf-8", errors="replace"), process.returncode,
        round((time.monotonic() - started) * 1000, 2))
