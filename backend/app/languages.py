"""Only fixed, configured toolchains may execute. No participant command flags."""
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Language:
    id: str
    label: str
    filename: str
    editor: str
    tools: tuple[str, ...]
    starter: str


LANGUAGES = {
    "python": Language("python", "Python 3", "main.py", "python", ("python",),
        "import sys\n\nsource = sys.stdin.readline().rstrip('\\r\\n')\n# Implement your solution here.\n"),
    "javascript": Language("javascript", "JavaScript", "main.js", "javascript", ("node",),
        "const fs = require('fs');\nconst source = fs.readFileSync(0, 'utf8').replace(/\\r?\\n$/, '');\n// Implement your solution here.\n"),
    "cpp": Language("cpp", "C++17", "main.cpp", "cpp", ("g++",),
        "#include <iostream>\n#include <string>\nint main() {\n    std::string source;\n    std::getline(std::cin, source);\n    // Implement your solution here.\n}\n"),
    "java": Language("java", "Java", "Main.java", "java", ("javac", "java"),
        "import java.io.*;\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        String source = new BufferedReader(new InputStreamReader(System.in)).readLine();\n        // Implement your solution here.\n    }\n}\n"),
}


class Registry:
    def __init__(self):
        self.paths = {}
        self.status = {}
        for key, language in LANGUAGES.items():
            paths = []
            reason = ""
            for tool in language.tools:
                path = os.environ.get("RELAY_TOOL_" + tool.upper(), sys.executable if tool == "python" else shutil.which(tool))
                if not path or not Path(path).is_file():
                    reason = f"Missing toolchain: {tool}"
                    break
                try:
                    probe = subprocess.run([path, "-version" if tool in ("java", "javac") else "--version"],
                        capture_output=True, timeout=3, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
                    if probe.returncode:
                        reason = f"Toolchain probe failed: {tool}"
                        break
                except (OSError, subprocess.TimeoutExpired):
                    reason = f"Toolchain probe unavailable or timed out: {tool}"
                    break
                paths.append(str(Path(path).resolve()))
            self.paths[key] = paths
            self.status[key] = {"id": key, "label": language.label, "editor_language": language.editor,
                "available": not reason, "reason": reason, "starter": language.starter}

    def public(self):
        return list(self.status.values())

    def commands(self, language: str, directory: Path):
        paths = self.paths[language]
        source = str(directory / LANGUAGES[language].filename)
        if language == "python":
            return [paths[0], "-I", "-m", "py_compile", source], [paths[0], "-I", source]
        if language == "javascript":
            return [paths[0], "--check", source], [paths[0], source]
        if language == "cpp":
            binary = str(directory / ("program.exe" if os.name == "nt" else "program"))
            return [paths[0], "-std=c++17", "-O2", source, "-o", binary], [binary]
        return [paths[0], "-encoding", "UTF-8", "-d", str(directory), source], [paths[1], "-cp", str(directory), "Main"]
