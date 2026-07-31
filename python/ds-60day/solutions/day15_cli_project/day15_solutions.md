# Day 15 — Solutions: CLI Data Tool Project

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**a small command-line application with separated boundaries**.

A command-line interface (CLI) has three layers: parse external strings,
call ordinary Python logic with typed values, then present a result and
choose an exit status. Keeping the core logic free from `sys.argv`,
printing, and process exit makes it reusable from tests and notebooks.

`argparse` defines flags, help, conversion, and validation close to the
command boundary. A `main(argv: list[str] | None = None) -> int`
function is testable because tests can pass an explicit list rather than
changing the real process arguments. The guarded entry point should do
little more than `raise SystemExit(main())`.

### Vocabulary used in the worked answers

- **CLI:** a text interface driven by command-line arguments and exit status.
- **argument parser:** a component that converts command text into named values.
- **option:** a named flag such as `--limit`.
- **positional argument:** a value identified by its position.
- **exit status:** an integer process result where zero normally means success.
- **entry point:** the small boundary that starts application execution.

### Reference pattern 1 — Parse an explicit argument list

Exercise the CLI contract without touching the notebook process arguments.

```python
import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rowtool")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("names", nargs="+")
    return parser

args = build_parser().parse_args(["--limit", "2", "Ada", "Lin", "Grace"])
(args.limit, args.names)
```

**Expected observation:** `(2, ['Ada', 'Lin', 'Grace'])`. Argparse converted `2` to an integer and collected positional names.

### Reference pattern 2 — Keep core work independent of printing

A plain function can be tested and reused by the CLI.

```python
def select_names(names: list[str], *, limit: int) -> list[str]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    return [name.strip().title() for name in names[:limit]]

select_names(args.names, limit=args.limit)
```

**Expected observation:** `['Ada', 'Lin']`. Parsing and presentation remain outside the core transformation.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Build the Day 15 CLI with subcommands or flags that read a local CSV/JSON input, perform one documented transformation, and write or print a bounded result. **Architecture:** `build_parser()`, pure core function(s), and `main(argv=None) -> int`. **Constraints:** use `pathlib`, UTF-8, no notebook-only state, and no hard-coded absolute paths. **Verify:** run `--help`, one successful command, and one invalid invocation.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a small command-line application with separated boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** run `--help`, one successful command, and one invalid invocation.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Add options for input path, output path, and a typed transformation parameter such as `--limit`. **Expected behavior:** argparse rejects invalid numeric text and the application returns a nonzero status for a missing input without a traceback aimed at beginners. **Constraint:** do not catch programming errors broadly. **Verify:** Exercise valid options, invalid integer text, and a missing input; assert parsed Python types and the documented nonzero exit status/message.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the a small command-line application with separated boundaries model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** Exercise valid options, invalid integer text, and a missing input; assert parsed Python types and the documented nonzero exit status/message.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Write pytest tests that call core logic directly and call `main([...])` with temporary files. **Coverage:** happy path, empty input, missing path, invalid parameter, and output overwrite policy. **Verify:** assert return status, captured output, and exact file content without spawning a shell.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a small command-line application with separated boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** assert return status, captured output, and exact file content without spawning a shell.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** Package the CLI invocation behind `if __name__ == '__main__': raise SystemExit(main())`. **Expected behavior:** importing the module produces no output or process exit; `python -m ... --help` works from the documented package parent. **Verify:** test both import and module execution.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a small command-line application with separated boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** test both import and module execution.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** Create a short README usage block for Windows PowerShell and macOS/Linux showing repository-interpreter commands and an example with a path containing spaces. **Constraint:** do not mix Bash syntax into PowerShell. **Verify:** copy and run the command appropriate to your operating system.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a small command-line application with separated boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** copy and run the command appropriate to your operating system.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the Python types produced by `argparse` when `--input` uses `type=Path` and `--limit` uses `type=int`. **Progressive hint:** The parser performs declared conversions before `main` receives values. **Verify:** Call `parse_args` with explicit text and assert the parsed input is a `Path`, limit is an `int`, and defaults have the documented types.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying a small command-line application with separated boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** Call `parse_args` with explicit text and assert the parsed input is a `Path`, limit is an `int`, and defaults have the documented types.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace one row through read → clean → summarize → write, and label which stages are I/O boundaries versus pure work. **Progressive hint:** A pure transform accepts and returns data without reading global state. **Verify:** For one fixture row, record the value/shape after every stage and assert only read/write touch files while the middle stages work from passed data.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the a small command-line application with separated boundaries model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** For one fixture row, record the value/shape after every stage and assert only read/write touch files while the middle stages work from passed data.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Add `--overwrite` and refuse to replace an existing output unless the flag is present. **Progressive hint:** Check the destination before performing the write. **Verify:** Use a temporary existing destination: assert refusal leaves content unchanged without the flag and `--overwrite` deliberately replaces it with the flag.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a small command-line application with separated boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** Use a temporary existing destination: assert refusal leaves content unchanged without the flag and `--overwrite` deliberately replaces it with the flag.

### Exercise 9 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a module that parses arguments and writes files during import. **Progressive hint:** Move behavior into `main(argv)` and use the `__main__` guard. **Verify:** Import the module while capturing output/files and assert no parser or write occurs; then assert `main([...])` performs the intended operation.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in a small command-line application with separated boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** Import the module while capturing output/files and assert no parser or write occurs; then assert `main([...])` performs the intended operation.

### Exercise 10 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Define exit codes/messages for missing input, malformed data, existing output, and unexpected internal failure; decide which layers log. **Progressive hint:** Translate expected boundary failures once, without hiding tracebacks in tests. **Verify:** Exercise all four failure categories and assert their exit codes/messages; an injected unexpected error must remain visible in tests rather than being mislabeled.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the a small command-line application with separated boundaries model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Edge case:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.

**Solution evidence to inspect:** Exercise all four failure categories and assert their exit codes/messages; an injected unexpected error must remain visible in tests rather than being mislabeled.
<!-- END BEGINNER SOLUTION REVIEW -->

We scaffold a small CLI that loads a CSV, cleans it, and writes a summary and cleaned output, with tests.

Contents
- Project layout
- Core transforms with tests
- CLI wired with argparse

---

Project layout
```
project/
  pyproject.toml
  src/
    cli.py
    io_utils.py
    transforms.py
  tests/
    test_transforms.py
```

src/transforms.py
```python
from __future__ import annotations
from typing import Sequence
import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    # Example cleaning: drop NA rows in key cols and convert types
    d = d.rename(columns=str.lower)
    if "date" in d.columns:
        d["date"] = pd.to_datetime(d["date"], errors="coerce", utc=True)
    for c in ("price", "qty"):
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=[c for c in ("price","qty") if c in d.columns])
    return d


def summarize(d: pd.DataFrame) -> pd.DataFrame:
    # Example summary: total revenue by day (if present)
    if {"price","qty"}.issubset(d.columns):
        d = d.assign(revenue=d["price"] * d["qty"])
    if "date" in d.columns:
        return d.groupby(d["date"].dt.date).agg(revenue=("revenue","sum"))
    return d.agg(revenue=("revenue","sum")).to_frame().T
```

src/io_utils.py
```python
from pathlib import Path
import pandas as pd

def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
```

src/cli.py
```python
import argparse
from pathlib import Path
from .io_utils import read_csv, write_csv
from .transforms import clean, summarize

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=False)
    args = ap.parse_args(argv)

    df = read_csv(args.input)
    tidy = clean(df)
    write_csv(tidy, args.out)
    if args.summary:
        summ = summarize(tidy)
        write_csv(summ, args.summary)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

tests/test_transforms.py
```python
import pandas as pd
from src.transforms import clean, summarize

def test_clean_and_summary():
    df = pd.DataFrame({"date":["2025-01-01","bad"],"price":["10","x"],"qty":[2,3]})
    tidy = clean(df)
    assert list(tidy.columns) >= ["date","price","qty"]
    assert tidy["price"].dtype.kind in "fi"   # numeric
    summ = summarize(tidy)
    assert "revenue" in summ.columns
```

Run
```bash
pytest -q
python -m src.cli --input data.csv --out out.csv --summary summary.csv
```
Notes
- Keep transforms pure and I/O thin for testability.
- Extend as needed (schemas, logging, error handling).

---

## Expanded mastery lab solutions

Keep command parsing and file I/O at thin boundaries around pure, importable transformations. Make failures observable through exit codes.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Parsed types and boundaries

`type=Path` produces a `Path`; `type=int` produces an integer or lets argparse
report invalid text. Reading and writing are boundaries; deterministic cleaning
and summarization should be pure enough to test in memory.

### Practices 3–5 — Safe overwrite and importable entry point

```python
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean a course CSV")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def ensure_writable_output(path: Path, *, overwrite: bool) -> None:
    """Reject accidental replacement before any output is opened."""

    if path.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if not args.input.is_file():
            raise FileNotFoundError(f"input not found: {args.input}")
        ensure_writable_output(args.out, overwrite=args.overwrite)
        # read -> clean -> summarize -> write belongs here.
    except (FileNotFoundError, FileExistsError, ValueError) as error:
        print(f"error: {error}")   # One user-facing boundary translation.
        return 2
    return 0


parsed = parse_args(["--input", "in.csv", "--out", "out.csv", "--limit", "10"])
assert isinstance(parsed.input, Path) and parsed.limit == 10

# Production module only:
# if __name__ == "__main__":
#     raise SystemExit(main())
```

Expected user/data errors can return `2`; unexpected programming failures
should propagate during tests and normally produce a controlled top-level log
with a distinct nonzero code in a production application.
