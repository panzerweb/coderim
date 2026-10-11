# Language setup and extension

Python uses the backend's interpreter. JavaScript requires `node`; C++17 requires `g++`; Java requires both `javac` and `java` from a JDK. Missing or timed-out toolchain probes disable that language in the UI, with a reason.

Use installed toolchains on PATH, or set an absolute path through `RELAY_TOOL_PYTHON`, `RELAY_TOOL_NODE`, `RELAY_TOOL_G++`, `RELAY_TOOL_JAVAC`, or `RELAY_TOOL_JAVA`. For an environment name containing `+`, PowerShell can use `[Environment]::SetEnvironmentVariable('RELAY_TOOL_G++', 'C:\path\g++.exe', 'Process')`. Restart the backend after changing configuration.

Python and JavaScript get syntax checks before execution. C++ compiles with `-std=c++17 -O2`. Java compiles `Main.java`; submitted Java code must use public class `Main`. All modes use complete programs reading stdin and writing stdout. No function-signature harness is injected.

Language adapters and probes are centralized in `backend/app/languages.py`. A new adapter defines source filename, editor mode, starter, fixed compile/run argument arrays, and executable probes. Add its approved ID to the request contract and frontend type if required, then exercise compile errors, acceptance, runtime errors, timeouts, output caps, and cleanup. Participant-controlled executable paths, shell commands, or flags are never accepted.

Performance limits need benchmarking on the actual computer. Runtime measurements include interpreter/VM startup and are not equally comparable across languages. A compiler/interpreter on PATH is not considered available until its probe completes successfully.
