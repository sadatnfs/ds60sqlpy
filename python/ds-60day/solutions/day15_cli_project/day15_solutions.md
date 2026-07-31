# Day 15 — Solutions: CLI Data Tool Project

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **a small command-line application with separated boundaries**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **a small command-line application with separated boundaries** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–5 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Build the Day 15 CLI with subcommands or flags that read a local CSV/JSON input, perform one documented transformation, and write or print a bounded result. **Architecture:** `build_parser()`, pure core function(s), and `main(argv=None) -> int`. **Constraints:** use `pathlib`, UTF-8, no notebook-only state, and no hard-coded absolute paths. **Verify:** assert `--help` exits `0` and names the command/options, a valid fixture exits `0` with the expected bounded output, and invalid input exits nonzero with a useful stderr message.

**Reasoning:** Implement this exact contract as written: Build the Day 15 CLI with subcommands or flags that read a local CSV/JSON input, perform one documented transformation, and write or print a bounded result. Architecture: `build_parser()`, pure core function(s), and `main(argv=None) -> int`. Constraints: use `pathlib`, UTF-8, no notebook-only state, and no hard-coded absolute paths. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert `--help` exits `0` and names the command/options, a valid fixture exits `0` with the expected bounded output, and invalid input exits nonzero with a useful stderr message. That connects the answer to a small command-line application with separated boundaries.

```python
from pathlib import Path
import json


def read_records(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("input JSON must be a list")
    return payload


def select_records(
    records: list[dict[str, object]], *, limit: int
) -> list[dict[str, object]]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    return records[:limit]
```

These functions separate the file boundary from the deterministic
transformation; `main` coordinates them.

**Verification evidence:** assert `--help` exits `0` and names the command/options, a valid fixture exits `0` with the expected bounded output, and invalid input exits nonzero with a useful stderr message.

### Exercise 2 — worked answer

**Learner contract:** Add options for input path, output path, and a typed transformation parameter such as `--limit`. **Expected behavior:** argparse rejects invalid numeric text and the application returns a nonzero status for a missing input without a traceback aimed at beginners. **Constraint:** do not catch programming errors broadly. **Verify:** Exercise valid options, invalid integer text, and a missing input; assert parsed Python types and the documented nonzero exit status/message.

**Reasoning:** Trace the concrete values in this contract one step at a time: Add options for input path, output path, and a typed transformation parameter such as `--limit`. Expected behavior: argparse rejects invalid numeric text and the application returns a nonzero status for a missing input without a traceback aimed at beginners. Constraint: do not catch programming errors broadly. Record the named value, shape, label, or iterator position needed to establish: Exercise valid options, invalid integer text, and a missing input; assert parsed Python types and the documented nonzero exit status/message. The trace exposes a small command-line application with separated boundaries directly.

```python
import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="record-tool")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=int, default=10)
    return parser


parsed = build_parser().parse_args(["input.json", "--limit", "3"])
assert isinstance(parsed.input, Path)
assert parsed.limit == 3
```

Argparse owns text conversion and produces its own friendly error for an
invalid integer.

**Verification evidence:** Exercise valid options, invalid integer text, and a missing input; assert parsed Python types and the documented nonzero exit status/message.

### Exercise 3 — worked answer

**Learner contract:** Write pytest tests that call core logic directly and call `main([...])` with temporary files. **Coverage:** happy path, empty input, missing path, invalid parameter, and output overwrite policy. **Verify:** assert return status, captured output, and exact file content without spawning a shell.

**Reasoning:** Implement this exact contract as written: Write pytest tests that call core logic directly and call `main([...])` with temporary files. Coverage: happy path, empty input, missing path, invalid parameter, and output overwrite policy. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert return status, captured output, and exact file content without spawning a shell. That connects the answer to a small command-line application with separated boundaries.

```python
import json
from pathlib import Path


def write_records(
    records: list[dict[str, object]],
    path: Path,
    *,
    overwrite: bool,
) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")
```

A pytest test should create an existing temporary file, prove refusal
preserves it, then pass `overwrite=True` and compare the new JSON.

**Verification evidence:** assert return status, captured output, and exact file content without spawning a shell.

### Exercise 4 — worked answer

**Learner contract:** Package the CLI invocation behind `if __name__ == '__main__': raise SystemExit(main())`. **Expected behavior:** importing the module produces no output or process exit; `python -m ... --help` works from the documented package parent. **Verify:** test both import and module execution.

**Reasoning:** Implement this exact contract as written: Package the CLI invocation behind `if __name__ == '__main__': raise SystemExit(main())`. Expected behavior: importing the module produces no output or process exit; `python -m ... --help` works from the documented package parent. Keep the prompt's named data and constraints visible in the code, then establish this specific result: test both import and module execution. That connects the answer to a small command-line application with separated boundaries.

```python
import sys


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    try:
        records = read_records(args.input)
        selected = select_records(records, limit=args.limit)
        if args.output is None:
            print(json.dumps(selected, indent=2))
        else:
            write_records(selected, args.output, overwrite=False)
    except (FileNotFoundError, FileExistsError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Import defines functions only; the guard owns process execution.

**Verification evidence:** test both import and module execution.

### Exercise 5 — worked answer

**Learner contract:** Create a short README usage block for Windows PowerShell and macOS/Linux showing repository-interpreter commands and an example with a path containing spaces. **Constraint:** do not mix Bash syntax into PowerShell. **Verify:** copy the command for your operating system, record exit code `0` and the expected output, and confirm the quoted path with spaces is received as one argument.

**Reasoning:** Implement this exact contract as written: Create a short README usage block for Windows PowerShell and macOS/Linux showing repository-interpreter commands and an example with a path containing spaces. Constraint: do not mix Bash syntax into PowerShell. Keep the prompt's named data and constraints visible in the code, then establish this specific result: copy the command for your operating system, record exit code `0` and the expected output, and confirm the quoted path with spaces is received as one argument. That connects the answer to a small command-line application with separated boundaries.

Copy-ready invocations keep platform syntax separate:

```powershell
& $CoursePython -m your_package.record_tool "data\input records.json" --limit 3
```

```bash
.venv/bin/python -m your_package.record_tool "data/input records.json" --limit 3
```

Both run from the repository root and quote the path containing spaces.

**Verification evidence:** copy the command for your operating system, record exit code `0` and the expected output, and confirm the quoted path with spaces is received as one argument.

## Exercises 6–10 — Expanded mastery answers

### Exercise 6 — answer contract

**Learner contract:** **Prediction:** Predict the Python types produced by `argparse` when `--input` uses `type=Path` and `--limit` uses `type=int`. **Progressive hint:** The parser performs declared conversions before `main` receives values. **Verify:** Call `parse_args` with explicit text and assert the parsed input is a `Path`, limit is an `int`, and defaults have the documented types.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the Python types produced by `argparse` when `--input` uses `type=Path` and `--limit` uses `type=int`. Progressive hint: The parser performs declared conversions before `main` receives values. Then compare the prediction with this proof target: Call `parse_args` with explicit text and assert the parsed input is a `Path`, limit is an `int`, and defaults have the documented types. This makes a small command-line application with separated boundaries observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Call `parse_args` with explicit text and assert the parsed input is a `Path`, limit is an `int`, and defaults have the documented types.

### Exercise 7 — answer contract

**Learner contract:** **Tracing:** Trace one row through read → clean → summarize → write, and label which stages are I/O boundaries versus pure work. **Progressive hint:** A pure transform accepts and returns data without reading global state. **Verify:** For one fixture row, record the value/shape after every stage and assert only read/write touch files while the middle stages work from passed data.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace one row through read → clean → summarize → write, and label which stages are I/O boundaries versus pure work. Progressive hint: A pure transform accepts and returns data without reading global state. Record the named value, shape, label, or iterator position needed to establish: For one fixture row, record the value/shape after every stage and assert only read/write touch files while the middle stages work from passed data. The trace exposes a small command-line application with separated boundaries directly.

**Evidence to locate in the grouped implementation:** For one fixture row, record the value/shape after every stage and assert only read/write touch files while the middle stages work from passed data.

### Exercise 8 — answer contract

**Learner contract:** **Implementation:** Add `--overwrite` and refuse to replace an existing output unless the flag is present. **Progressive hint:** Check the destination before performing the write. **Verify:** Use a temporary existing destination: assert refusal leaves content unchanged without the flag and `--overwrite` deliberately replaces it with the flag.

**Reasoning:** Implement this exact contract as written: Implementation: Add `--overwrite` and refuse to replace an existing output unless the flag is present. Progressive hint: Check the destination before performing the write. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Use a temporary existing destination: assert refusal leaves content unchanged without the flag and `--overwrite` deliberately replaces it with the flag. That connects the answer to a small command-line application with separated boundaries.

**Evidence to locate in the grouped implementation:** Use a temporary existing destination: assert refusal leaves content unchanged without the flag and `--overwrite` deliberately replaces it with the flag.

### Exercise 9 — answer contract

**Learner contract:** **Debugging:** Repair a module that parses arguments and writes files during import. **Progressive hint:** Move behavior into `main(argv)` and use the `__main__` guard. **Verify:** Import the module while capturing output/files and assert no parser or write occurs; then assert `main([...])` performs the intended operation.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a module that parses arguments and writes files during import. Progressive hint: Move behavior into `main(argv)` and use the `__main__` guard. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Import the module while capturing output/files and assert no parser or write occurs; then assert `main([...])` performs the intended operation. The diagnosis depends on a small command-line application with separated boundaries.

**Evidence to locate in the grouped implementation:** Import the module while capturing output/files and assert no parser or write occurs; then assert `main([...])` performs the intended operation.

### Exercise 10 — answer contract

**Learner contract:** **Edge case and explanation:** Define exit codes/messages for missing input, malformed data, existing output, and unexpected internal failure; decide which layers log. **Progressive hint:** Translate expected boundary failures once, without hiding tracebacks in tests. **Verify:** Exercise all four failure categories and assert their exit codes/messages; an injected unexpected error must remain visible in tests rather than being mislabeled.

**Reasoning:** Trace the concrete values in this contract one step at a time: Edge case and explanation: Define exit codes/messages for missing input, malformed data, existing output, and unexpected internal failure; decide which layers log. Progressive hint: Translate expected boundary failures once, without hiding tracebacks in tests. Record the named value, shape, label, or iterator position needed to establish: Exercise all four failure categories and assert their exit codes/messages; an injected unexpected error must remain visible in tests rather than being mislabeled. The trace exposes a small command-line application with separated boundaries directly.

**Evidence to locate in the grouped implementation:** Exercise all four failure categories and assert their exit codes/messages; an injected unexpected error must remain visible in tests rather than being mislabeled.

## Expanded mastery lab solutions

Keep command parsing and file I/O at thin boundaries around pure, importable transformations. Make failures observable through exit codes.

### Shared implementation for Exercises 6–7 — Parsed types and boundaries

`type=Path` produces a `Path`; `type=int` produces an integer or lets argparse
report invalid text. Reading and writing are boundaries; deterministic cleaning
and summarization should be pure enough to test in memory.

### Shared implementation for Exercises 8–10 — Safe overwrite and importable entry point

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
