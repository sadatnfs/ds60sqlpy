# Day 14 — Solutions: Code Quality with Black, Flake8, and Mypy

We configure tools and fix typical issues surfaced by each.

Contents
- Exercise: Apply black/flake8/mypy to your utilities and fix issues

---

Sample pyproject.toml
```toml
[tool.black]
line-length = 88

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203"]

[tool.mypy]
python_version = "3.10"
warn_unused_ignores = true
warn_redundant_casts = true
strict_optional = true
```

Commands
```bash
black .            # reformat code
flake8 .           # style and simple correctness checks
mypy .             # type checking
```

Typical fixes
- flake8: remove unused imports, fix undefined names, limit line length
- mypy: add type hints, handle Optional properly, narrow exceptions

Example: before/after
```python
# BEFORE
from typing import *
import json, os

def load(path):
    f = open(path)      # resource leak, missing encoding
    return json.load(f) # type of return unknown

# AFTER
from pathlib import Path
from typing import Any
import json

def load(path: str | Path) -> Any:
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        return json.load(f)
```
Why better
- Explicit imports, explicit types, safe file handling, encoding specified.

CI tip
- Add a GitHub Actions workflow to run these on every push/PR.
