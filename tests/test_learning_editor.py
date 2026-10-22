"""Check editor data integrity using the actual offline JavaScript helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ASSET = Path(__file__).parents[1] / "src/ds60sqlpy/assets/learning_lab.html"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node is an optional developer UI check")


def evaluate_helper(expression: str) -> object:
    document = ASSET.read_text(encoding="utf-8")
    source = document.split("// BEGIN EDITOR PURE HELPERS", 1)[1].split(
        "// END EDITOR PURE HELPERS", 1
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


def test_visual_tokens_preserve_every_source_character() -> None:
    sources = [
        'print("<img src=x onerror=alert(1)>")\n# hello\n',
        "SELECT 'A''B', 42; -- inspect\n",
        'def f(x):\n\treturn f"{x!r}"\n',
        "s = '''multiline\nstring'''\n",
        "object Main { val x = 3 }\n",
        "apiVersion: v1\n# hello\n",
        "",
        "\n\n",
        "Smile: \U0001f60a <&> \r\n",
        '"unterminated\\',
        "x" * 90000,
    ]
    expression = (
        f"const sources = {json.dumps(sources)};\n"
        'sources.flatMap(source => [".py", ".sql", ".cpp", ".scala", ".yaml", ""]'
        ".map(mode => { const tokens = syntaxTokens(source, mode); return {"
        'equal: tokens.map(token => token.text).join("") === source,'
        'safeKinds: tokens.every(token => ["", "keyword", "number", "string", '
        '"builtin", "comment"].includes(token.kind))}; }));'
    )
    results = evaluate_helper(expression)
    assert isinstance(results, list)
    assert len(results) == len(sources) * 6
    assert all(result == {"equal": True, "safeKinds": True} for result in results)
    classifications = evaluate_helper(
        'syntaxTokens("def f():\\n    return 42 # inspect\\n", ".py")'
        ".filter(token => token.kind).map(token => [token.text, token.kind])"
    )
    assert classifications == [
        ["def", "keyword"],
        ["return", "keyword"],
        ["42", "number"],
        ["# inspect", "comment"],
    ]


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
