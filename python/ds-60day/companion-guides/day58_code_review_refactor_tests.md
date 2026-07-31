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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 58 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — behavior-preserving refactoring, seams, tests, and compatibility review

### The mental model

Refactoring changes internal structure while preserving observable
behavior. Before changing unfamiliar code, a **characterization test**
records what it currently does for representative and boundary inputs.
Then small pure functions and explicit dependencies create seams that
can be tested without files, networks, clocks, or global state.

Code review is risk analysis, not style preference. Trace inputs,
outputs, exceptions, side effects, data/security boundaries, backward
compatibility, and evidence. Static tools catch classes of problems but
cannot prove runtime or domain behavior.

### Worked examples and syntax anatomy

- **characterization test:** locks down important current behavior before extracting or renaming it.
- **pure core + impure shell:** isolates transformations from I/O so normal, boundary, and failure cases are deterministic.
- **Ruff + mypy + pytest:** checks formatting/lint, static type contracts, and executable behavior as complementary evidence.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — capture legacy behavior before extraction

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
def legacy_total(rows):
    return round(sum(float(row["price"]) * int(row["units"]) for row in rows), 2)

sample = [
    {"price": "1.25", "units": "2"},
    {"price": "0.50", "units": "3"},
]
observed = legacy_total(sample)
print(observed)
assert observed == 4.0  # characterization: preserve while restructuring
```

**Expected observation:** The test records the current numeric contract before parsing and calculation are separated.

**Assumption to name:** Rounding only the final total is intended behavior; malformed-row policy still needs a failure test.

### Focused example B — extract a pure boundary with explicit failures

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
from decimal import Decimal, InvalidOperation

def line_total(price_text, units_text):
    try:
        price = Decimal(price_text)
        units = int(units_text)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid sales row") from exc
    if price < 0 or units < 0:
        raise ValueError("price and units must be nonnegative")
    return price * units

assert line_total("1.25", "2") == Decimal("2.50")
try:
    line_total("bad", "2")
except ValueError as exc:
    print(type(exc.__cause__).__name__, str(exc))
```

**Expected observation:** The extracted function is deterministic, uses decimal arithmetic, and translates low-level parse errors into one boundary exception.

**Assumption to name:** Rejecting negative values and translating errors matches the caller's contract.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define behavior-preserving refactoring, seams, tests, and compatibility review in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Changing behavior and structure simultaneously without a regression test or compatibility note.

**Debug it deliberately:** Reduce the diff, identify one observable contract, reproduce the old result, add boundary/failure tests, and run tools after each small extraction.

**Stop condition:** Do not merge a refactor when tests assert implementation steps rather than behavior or when API/data compatibility is unexplained.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Move at least two notebook functions into a `src/` package and add tests.

**Verify:** Practice 1 — behavior-preserving refactoring, seams, tests, and compatibility review — import two moved functions from src in a fresh process and run focused normal/boundary/failure tests with exit code 0; prove the notebook now calls those imports and no copied implementation remains.

2. Add type hints and docstrings, then run mypy.

**Verify:** Practice 2 — behavior-preserving refactoring, seams, tests, and compatibility review — run mypy on the exact src/test paths with exit code 0 and save its transcript; include parameter/return annotations and docstrings that state errors/side effects, plus one negative typing fixture that fails as expected.

3. Write a short maintainer guide in the project root.

**Verify:** Practice 3 — behavior-preserving refactoring, seams, tests, and compatibility review — write a maintainer guide containing clean setup, test/lint/type commands, architecture/data flow, artifact locations, release/rollback, and troubleshooting; have another clean shell execute every command successfully.

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

### Additional mastery practice

Refactor behind tests, review risk at boundaries, and preserve behavior while improving structure. Type checks and formatting support—not replace—domain evidence.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Characterization testing:** Before refactoring a legacy notebook function, capture current behavior for normal, boundary, and known-bug inputs. Mark which behavior is a contract and which bug will intentionally change.
   **Progressive hint:** Characterization tests prevent accidental drift; an intentional fix needs a new expected result and a documented reason.

**Verify:** Characterization testing — save characterization tests and outputs for normal, boundary, and known-bug fixtures before editing; after refactor, assert contract cases match byte/value-for-value and the intentional bug change has a separately approved expected result.

5. **Risk-based review:** Review a data-loading-to-prediction change using a checklist for security, data loss, leakage, schema compatibility, performance, error handling, and cross-platform paths.
   **Progressive hint:** Trace inputs to side effects and downstream consumers. Prioritize high-impact boundaries over cosmetic preferences.

**Verify:** Risk-based review — complete a review matrix for security, data loss, leakage, schema, performance, errors, and Windows/POSIX paths; each row must cite changed lines, a test/measurement result, severity, owner, and disposition.

6. **Compatibility change:** Rename a public function parameter without breaking callers. Implement a deprecation path, tests for old/new usage, and a removal plan.
   **Progressive hint:** Accept the old keyword temporarily, reject ambiguous double use, emit a targeted DeprecationWarning, and update docs/call sites.

**Verify:** Compatibility change — assert old keyword and new keyword produce identical results during the compatibility window, simultaneous/conflicting use raises an error, the old path emits the named deprecation warning, and the removal version/date is documented.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-58` — Day 58 — Code Review, Refactoring, and Tests.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize behavior-preserving refactoring, seams, tests, and compatibility review. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day58_code_review_refactor_tests.md`
- learner artifact: `python/ds-60day/notebooks/day58_code_review_refactor_tests.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-57`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
