# Day 58 — Code Review, Refactoring, and Tests

**Lesson ID:** `python-58` · **Level:** advanced · **Dependencies:** `data` · **Network:** offline

Refactoring changes structure while preserving intended behavior. Today you move
notebook logic behind importable interfaces, add focused tests, and use Ruff,
mypy, and pytest as complementary evidence.

## Learning objectives

By the end of the lesson, you can:

- identify separable data, feature, model, and evaluation responsibilities;
- extract small typed functions from a notebook into `src/`;
- test normal, boundary, and failure behavior with local fixtures;
- run Ruff formatting/linting, mypy, and pytest; and
- write a maintainer guide that explains contracts and safe change workflow.

## Prerequisites

- Complete `python-57` (security, privacy, and ethics).
- Recall modules, pytest, logging, and type hints from `python-05`, `python-09`,
  `python-10`, `python-11`, and `python-14`.
- Install the `quality` dependency group.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Refactoring | Internal structural change intended to preserve observable behavior |
| Pure function | Output depends only on arguments and has no side effects |
| Unit test | Fast test of one small contract |
| Integration test | Test of collaborating components or an external boundary |
| Fixture | Reusable test setup/data |
| Regression test | Test preserving behavior after a defect is found |
| Static analysis | Checks source without executing all runtime paths |
| Code review | Human evaluation of correctness, clarity, risk, and evidence |

Tools divide responsibilities: Ruff enforces format and many source-level rules,
mypy checks declared type contracts, and pytest executes behavioral tests.
Passing one does not imply the others pass.

## Worked example: extract a testable boundary

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Metrics:
    rows: int
    positive_rate: float


def summarize_labels(labels: list[int]) -> Metrics:
    """Return count and positive rate for nonempty binary labels."""
    if not labels:
        raise ValueError("labels must not be empty")
    if not set(labels) <= {0, 1}:
        raise ValueError("labels must be binary")
    return Metrics(rows=len(labels), positive_rate=sum(labels) / len(labels))
```

This function has explicit inputs, output, and failure behavior. It can be
tested without downloading data, opening a notebook, or fitting a model.

## Run quality checks

macOS/Linux:

```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/mypy src tests
.venv/bin/python -m pytest -q
```

Windows PowerShell:

```powershell
.\.venv\Scripts\ruff.exe check src tests
.\.venv\Scripts\ruff.exe format --check src tests
.\.venv\Scripts\mypy.exe src tests
.\.venv\Scripts\python.exe -m pytest -q
```

Ruff is the repository's sole Python formatter and linter; keep its checked-in
configuration as the source of truth.

## Learner exercises

1. Move at least two notebook functions into a `src/` package and add tests.
2. Add type hints and docstrings, then run mypy.
3. Write a short maintainer guide in the project root.

### Progressive hints

1. Start with deterministic transformation/build functions. Create tiny
   synthetic DataFrames in fixtures so tests remain offline.
2. Type public boundaries first. A type-ignore requires a narrow reason;
   replacing every value with `Any` defeats the check.
3. Document setup, architecture, tests, formatting, data contracts, artifact
   locations, security rules, and review gates.

The separate solution demonstrates a small extraction, local pre-commit hooks,
and GitHub Actions. Treat CI as remote repetition of checks you can already run
locally.

## Self-check

- Which behavior proves the refactor preserved the old contract?
- What should happen for empty, missing, or malformed input?
- Why is a network-backed Seaborn fixture inappropriate for an offline unit test?
- Which change belongs in a separate PR because it changes behavior rather than
  structure?

Expected behavior: all four local commands exit successfully, tests use
generated fixtures, and no learner artifact or cache is added to source control.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Refactor and behavior change mixed | Review cannot isolate risk | Separate steps/commits and add characterization tests |
| Tests assert only “no exception” | Wrong outputs pass | Assert contract, invariants, and failure behavior |
| Notebook imports hidden state | Module works only after cell order | Make dependencies explicit arguments/imports |
| Formatter rewrites generated/notebook files | Noisy or corrupt diff | Scope tool configuration deliberately |
| Type errors silenced broadly | Static evidence disappears | Use precise types and narrow documented exceptions |

Small modules can improve review and reuse; excessive fragmentation creates
navigation cost. Extract around stable concepts and side-effect boundaries.

## Next step

- Work in the [Day 58 learner notebook](../notebooks/day58_code_review_refactor_tests.ipynb).
- Then consult the
  [Day 58 solution](../solutions/day58_code_review_refactor_tests/day58_solutions.md).
- Continue to [Day 59 — Capstone Kickoff](day59_capstone_kickoff.md).
