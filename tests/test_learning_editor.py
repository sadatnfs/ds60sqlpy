"""Check editor data integrity using the actual offline JavaScript helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ASSET = Path(__file__).parents[1] / "src/ds60sqlpy/assets/classroom.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node is an optional developer UI check")


def evaluate_helper(expression: str) -> object:
    document = ASSET.read_text(encoding="utf-8")
    source = document.split("// BEGIN DIAGNOSTIC PURE HELPERS", 1)[1].split(
        "// END DIAGNOSTIC PURE HELPERS", 1
    )[0]
    program = (
        "const vm = require('node:vm');\n"
        'let input = "";\n'
        "process.stdin.setEncoding('utf8');\n"
        "process.stdin.on('data', chunk => input += chunk);\n"
        "process.stdin.on('end', () => {\n"
        "const value = JSON.parse(input);\n"
        "const sandbox = {}; vm.createContext(sandbox);\n"
        "vm.runInContext(value.source, sandbox);\n"
        "console.log(JSON.stringify(vm.runInContext(value.expression, sandbox)));\n"
        "});\n"
    )
    result = subprocess.run(
        [str(NODE), "-e", program],
        input=json.dumps({"source": source, "expression": expression}),
        text=True,
        capture_output=True,
        timeout=5,
        check=True,
    )
    return json.loads(result.stdout)


def test_error_navigation_uses_only_valid_submitted_source_lines() -> None:
    cases = [
        ('  File "/private/.submission-abcdef.py", line 3\nValueError: bad', 5, 3),
        ('  File "practice.py", line 2\n  File "/private/.submission-x.py", line 4\n', 5, 4),
        ('  File "library.py", line 1\n', 5, None),
        ('  File "practice.py", line 20\n', 5, None),
        ('  File "practice.py", line 0\n', 5, None),
        ('ERROR: syntax error at or near ";"\n', 5, None),
        ('  File "C:\\work\\.submission-abc_def.py", line 2\n', 3, 2),
        ('Printed text File "practice.py", line 2\n', 3, None),
        ('  File "/lib/practice.py.bak", line 2\n', 3, None),
    ]
    expression = (
        f"const cases = {json.dumps(cases)};\n"
        "cases.map(([output, count]) => tracebackLine(output, count));"
    )
    assert evaluate_helper(expression) == [expected for _, _, expected in cases]
