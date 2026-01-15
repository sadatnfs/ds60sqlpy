# Day 58 — Code Review, Refactoring, and Tests (Companion Guide)

## Learning objectives
- Write reviewable code: structure, naming, docs, type hints
- Refactor notebooks into modules; add unit and integration tests
- Use pre-commit hooks and CI for quality gates

## Why this matters
Maintainable code speeds iteration, reduces bugs, and enables collaboration.

## Core concepts and examples
- Structure: src/ package, tests/, config/
- Refactor: move pure transforms to functions; keep I/O thin
- Testing: pytest fixtures, tmp_path, parametrization
- pre-commit: black, isort, flake8, mypy

### Example pre-commit
```yaml
repos:
- repo: https://github.com/psf/black
  rev: 24.8.0
  hooks: [{id: black}]
- repo: https://github.com/pycqa/flake8
  rev: 6.1.0
  hooks: [{id: flake8}]
```

## Common pitfalls
- Large PRs mixing feature + refactor; split into small, focused changes
- Untested refactors; keep tests green
- Overusing mocks; prefer functional seams

## Practice exercises
1) Extract functions from a notebook and add tests
2) Configure pre-commit and run on staged files
3) Set up GitHub Actions to run tests and linters

## Further reading
- pre-commit: https://pre-commit.com
- Pytest: https://docs.pytest.org
