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
```bash
pytest -q
```

---

Exercise 2 — pre‑commit
```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/psf/black
  rev: 24.8.0
  hooks: [{id: black}]
- repo: https://github.com/pycqa/isort
  rev: 5.13.2
  hooks: [{id: isort}]
- repo: https://github.com/pycqa/flake8
  rev: 6.1.0
  hooks: [{id: flake8}]
```
Install and run
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
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
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: { python-version: '3.11' }
    - run: pip install -r requirements.txt -r requirements-dev.txt
    - run: pre-commit run --all-files
    - run: pytest -q
```
Notes
- Keep PRs small and focused; require reviews
- Enforce status checks before merge
