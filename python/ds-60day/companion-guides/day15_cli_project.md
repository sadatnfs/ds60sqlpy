# Day 15 — Project: A Testable CLI Data Tool

**Level:** Beginner checkpoint

This checkpoint combines the first 14 days into a small command-line program
that reads CSV, cleans data, writes output, and remains testable.

## Learning objectives

By the end of this project, you can:

- separate parsing, I/O, transformation, and presentation concerns;
- build a standard-library `argparse` interface;
- pass paths into pure, testable core functions;
- return a meaningful process exit code;
- run Ruff, mypy, and pytest before treating the project as complete.

## Prerequisites

Complete Days 1–14, especially packages (`python-09`), pytest (`python-10`),
logging (`python-11`), and quality tooling (`python-14`).

## Vocabulary and mental model

- **CLI:** command-line interface.
- **Argument parser:** converts command text into validated program options.
- **Pure transform:** computes output from input without performing file I/O.
- **Boundary:** point where untrusted input, files, or operating-system behavior
  enters the program.
- **Exit code:** `0` for success and nonzero for a reported failure.

Keep a thin shell around a testable core:

```text
arguments -> read -> clean -> summarize -> write
               boundaries | pure work | boundary
```

## Worked example

This tiny parser demonstrates the interface without solving the data project:

```python
import argparse
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect an input path")
    parser.add_argument("--input", required=True, type=Path)
    return parser.parse_args(argv)
```

Passing `argv` makes parser behavior testable without changing global process
arguments.

## Exercises and progressive hints

1. Read a CSV with pandas, drop or handle required missing values, and convert
   documented column types. **Hint:** make `clean(frame)` return a copy so a
   caller's input is not silently mutated.
2. Compute summary statistics and save a cleaned CSV. **Hint:** keep read/write
   functions separate from transforms and create parent directories
   deliberately.
3. Provide `--input` and `--out` with `argparse`; the intended invocation is
   `python tool.py --input data.csv --out out.csv`. **Hint:** use `type=Path`
   and `required=True`; do not introduce Click.
4. Test core functions and one parser path. **Hint:** use tiny in-memory frames
   and pytest's `tmp_path`, not large external data.
5. Run Ruff lint/format checks, mypy, and pytest. **Hint:** use the same commands
   as Day 14 and inspect the first failure before continuing.

Store practice source in a tracked project directory. Put disposable generated
files under ignored `artifacts/`; never commit `.venv`, caches, secrets, or a
machine-specific `.env`.

### Additional mastery practice

Keep command parsing and file I/O at thin boundaries around pure, importable transformations. Make failures observable through exit codes.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

6. **Prediction:** Predict the Python types produced by `argparse` when `--input` uses `type=Path` and `--limit` uses `type=int`.
   **Progressive hint:** The parser performs declared conversions before `main` receives values.
7. **Tracing:** Trace one row through read → clean → summarize → write, and label which stages are I/O boundaries versus pure work.
   **Progressive hint:** A pure transform accepts and returns data without reading global state.
8. **Implementation:** Add `--overwrite` and refuse to replace an existing output unless the flag is present.
   **Progressive hint:** Check the destination before performing the write.
9. **Debugging:** Repair a module that parses arguments and writes files during import.
   **Progressive hint:** Move behavior into `main(argv)` and use the `__main__` guard.
10. **Edge case and explanation:** Define exit codes/messages for missing input, malformed data, existing output, and unexpected internal failure; decide which layers log.
   **Progressive hint:** Translate expected boundary failures once, without hiding tracebacks in tests.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Run the project

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe tool.py --input data.csv --out artifacts\out.csv
.\.venv\Scripts\python.exe -m pytest
```

macOS/Linux:

```bash
.venv/bin/python tool.py --input data.csv --out artifacts/out.csv
.venv/bin/python -m pytest
```

## Self-check

- Can transformation tests run without reading a real file?
- Does `--help` explain required arguments and their purpose?
- What happens for a missing path, malformed number, or empty input?
- Can another module import the code without running the CLI?

Expected behavior: valid input produces deterministic cleaned/summary output,
invalid input fails clearly, and all quality gates pass.

## Common pitfalls and diagnosis

- **The CLI runs during import:** put execution in `main()` and guard it with
  `if __name__ == "__main__"`.
- **Tests need subprocesses for every case:** move logic behind pure functions
  and test the parser with an explicit `argv`.
- **Pandas mutates caller data:** call `.copy()` at the transform boundary.
- **A traceback is shown for an ordinary user error:** catch the narrow boundary
  exception in `main`, log a concise message, and return nonzero.
- **Windows output paths use manual string concatenation:** use `Path` and `/`
  composition.

## Continue

- [Open the learner notebook](../notebooks/day15_cli_project.ipynb)
- [Check the separate project solution](../solutions/day15_cli_project/day15_solutions.md)
- [Next: Day 16 — NumPy fundamentals](day16_numpy_fundamentals.md)
