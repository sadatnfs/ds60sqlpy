# Day 14 — Solutions: Code Quality with Ruff and mypy

This solution configures the repository’s actual quality tools and explains
what each signal can—and cannot—prove.

Contents
- Exercise: Apply Ruff and mypy to your utilities, then run tests

---

Sample `pyproject.toml`
```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
```

Commands
```text
python -m ruff check .          # lint and import checks
python -m ruff format --check . # verify formatting without changing files
python -m mypy .                # static type checking
python -m pytest                # behavioral checks
```

Typical fixes

- Ruff: remove unused imports, fix undefined names, simplify suspicious code,
  and sort imports.
- mypy: annotate public boundaries, handle `None`, and narrow values before use.
- pytest: repair behavior or the test contract after understanding the failure.

Example: before/after
```python
# BEFORE
import json

def load(path):
    f = open(path)
    return json.load(f)

# AFTER
import json
from pathlib import Path
from typing import Any

def load(path: str | Path) -> Any:
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        return json.load(f)
```
Why better

- Imports and accepted path types are explicit.
- The context manager closes the file if decoding fails.
- The encoding does not depend on the operating-system default.

`Any` is honest for arbitrary JSON but deliberately gives up downstream type
checking. A production boundary could validate the decoded value and return a
more precise type.

CI tip

Run the same lock, lint, format, type, and test commands locally and in
continuous integration. A clean formatter or type checker does not replace
tests; the tools catch different classes of defects.
