# Day 58 — Solutions: Code Review, Refactoring, and Tests

We refactor notebook logic into a module, write unit tests, configure pre‑commit hooks, and add a CI workflow.

Contents
- Exercise 1: Extract functions and add tests
- Exercise 2: Configure pre‑commit
- Exercise 3: GitHub Actions CI for lint+tests

---

Exercise 1 — Extract and test
```python
# src/myproj/fe.py
from __future__ import annotations
from typing import Iterable

def scale_minmax(xs: Iterable[float]) -> list[float]:
    xs = list(xs)
    mn, mx = min(xs), max(xs)
    if mx == mn:  # avoid divide by zero
        return [0.0 for _ in xs]
    return [(x-mn)/(mx-mn) for x in xs]
```

```python
# tests/test_fe.py
import pytest
from myproj.fe import scale_minmax

def test_scale_happy():
    assert scale_minmax([0,5,10]) == [0.0, 0.5, 1.0]

def test_scale_constant():
    assert scale_minmax([3,3,3]) == [0.0,0.0,0.0]
```
Run tests
```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS or Linux
.venv/bin/python -m pytest -q
```

---

Exercise 2 — pre‑commit
```yaml
# .pre-commit-config.yaml
repos:
- repo: local
  hooks:
  - id: ruff-check
    name: Ruff check
    entry: ruff check --fix
    language: system
    types: [python]
  - id: ruff-format
    name: Ruff format
    entry: ruff format
    language: system
    types: [python]
```
Core setup already installs pre-commit. Install the local hook and run it:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pre_commit install
.\.venv\Scripts\python.exe -m pre_commit run --all-files
```

```bash
# macOS or Linux
.venv/bin/python -m pre_commit install
.venv/bin/python -m pre_commit run --all-files
```

---

Exercise 3 — CI workflow
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v6
    - uses: actions/setup-python@v6
      with: { python-version: '3.12' }
    - run: python -m pip install -e ".[quality]"
    - run: ruff check .
    - run: ruff format --check .
    - run: pytest -q
```
Notes
- Keep PRs small and focused; require reviews
- Enforce status checks before merge
