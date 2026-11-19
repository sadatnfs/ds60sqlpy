# Day 15 Solutions: Project: A Testable Command-Line Data Tool

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

## Exercises 1-5: Worked answers

### Exercise 1: worked answer

**Learner contract:** Build the Day 15 CLI with subcommands or flags that read a local CSV/JSON input, perform one documented transformation, and write or print a bounded result. **Architecture:** `build_parser()`, pure core function(s), and `main(argv=None) -> int`. **Constraints:** use `pathlib`, UTF-8, no notebook-only state, and no hard-coded absolute paths. **Verify:** assert `--help` exits `0` and names the command/options, a valid fixture exits `0` with the expected bounded output, and invalid input exits nonzero with a useful stderr message.

**Reasoning:** The design keeps file access at the edges and the decision in the middle: `read_records` is the only function that opens a file, and `select_records` is a pure function of its inputs, so it can be tested with an in-memory list. Validating that the JSON is a list and that `limit` is non-negative turns a confusing later failure into a clear `ValueError` at the boundary. The keyword-only `limit` (after `*`) forces callers to name it, so `select_records(records, 3)` cannot be misread. `main` then coordinates the pieces, as the fourth worked answer shows.

```python
from pathlib import Path
import json


def read_records(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("input JSON must be a list")
    return payload


def select_records(records: list[dict[str, object]], *, limit: int) -> list[dict[str, object]]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    return records[:limit]
```

These functions separate the file boundary from the deterministic
transformation; `main` coordinates them.

### Exercise 2: worked answer

**Learner contract:** Add options for input path, output path, and a typed transformation parameter such as `--limit`. **Expected behavior:** argparse rejects invalid numeric text and the application returns a nonzero status for a missing input without a traceback aimed at beginners. **Constraint:** do not catch programming errors broadly. **Verify:** Exercise valid options, invalid integer text, and a missing input; assert parsed Python types and the documented nonzero exit status/message.

**Reasoning:** Declaring `type=Path` and `type=int` moves conversion into argparse: `main` receives a `Path` and an `int`, never raw strings. When text cannot be converted, argparse prints a usage message with an error such as `invalid int value: 'three'` and exits with status 2, so the application needs no `try` around parsing. The positional `input` is required, while `--output` defaults to `None`, which means print to the terminal. Catching every exception around the whole program to print a friendly message is the trap: it would also hide programming errors.

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

### Exercise 3: worked answer

**Learner contract:** Write pytest tests that call core logic directly and call `main([...])` with temporary files. **Coverage:** happy path, empty input, missing path, invalid parameter, and output overwrite policy. **Verify:** assert return status, captured output, and exact file content without spawning a shell.

**Reasoning:** Calling `main([...])` directly with temporary files tests the real entry point without starting a shell: the return value is the exit status, and printed output can be captured with `contextlib.redirect_stdout` (or `capsys` inside pytest). The checks after `main` in the fourth worked answer cover the happy path, an empty input file, a missing path (status 2), invalid `--limit` text (argparse exits with 2), and the overwrite refusal that leaves an existing file unchanged. `write_records` checks the destination before writing anything, which is what makes the refusal safe.

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

### Exercise 4: worked answer

**Learner contract:** Package the CLI invocation behind `if __name__ == '__main__': raise SystemExit(main())`. **Expected behavior:** importing the module produces no output or process exit; `python -m ... --help` works from the documented package parent. **Verify:** test both import and module execution.

**Reasoning:** The `if __name__ == "__main__":` guard makes the module safe to import: tests and other modules get the functions, and only running the module as a program calls `main()`. `raise SystemExit(main())` turns the integer `main` returns into the process exit status, so shells and CI see 0 for success and 2 for a handled user error. `main` catches only the expected boundary failures (missing file, existing output, invalid data) and prints them to stderr; anything else is a bug and keeps its traceback. Running `python -m your_package.record_tool --help` from the package parent confirms the module form.

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
```

The module file ends with the entry-point guard. It is shown as text because
a notebook kernel also sets `__name__` to `"__main__"`, so running the guard in
a notebook would call `main()` with the kernel's own arguments:

```text
if __name__ == "__main__":
    raise SystemExit(main())
```

Import defines functions only; the guard owns process execution. The checks
below call `main` the way the third exercise's tests would:

```python
import contextlib
import io
import tempfile

with tempfile.TemporaryDirectory() as folder:
    source = Path(folder) / "records.json"
    source.write_text(json.dumps([{"id": 1}, {"id": 2}, {"id": 3}]), encoding="utf-8")
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        assert main([str(source), "--limit", "2"]) == 0
    assert json.loads(printed.getvalue()) == [{"id": 1}, {"id": 2}]

    empty = Path(folder) / "empty.json"
    empty.write_text("[]", encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        assert main([str(empty)]) == 0

    with contextlib.redirect_stderr(io.StringIO()):
        assert main([str(Path(folder) / "missing.json")]) == 2
        try:
            main([str(source), "--limit", "three"])
        except SystemExit as exit_error:
            assert exit_error.code == 2  # argparse rejects invalid integer text
        else:
            raise AssertionError("argparse should reject --limit three")

    existing = Path(folder) / "out.json"
    existing.write_text("keep me", encoding="utf-8")
    with contextlib.redirect_stderr(io.StringIO()):
        assert main([str(source), "--output", str(existing)]) == 2
    assert existing.read_text(encoding="utf-8") == "keep me"
```

### Exercise 5: worked answer

**Learner contract:** Create a short README usage block with Bash commands (Linux, macOS, or Ubuntu in Windows WSL 2) that run the tool through the repository interpreter, including an example whose input path contains a space. **Constraint:** quote the path so the shell passes it as a single argument. **Verify:** run the documented command, record exit code `0` and the expected output, and confirm that the quoted path with a space arrives as one argument; then remove the quotes once and record the resulting argparse error.

**Reasoning:** The shell splits a command line at spaces before Python sees it, so an unquoted `data/input records.json` arrives as two arguments and argparse reports `unrecognized arguments: records.json`. Double quotes keep the path together as one argument. `shlex.split` applies the same POSIX shell rules from Python, which the block below uses to show both cases and the resulting argparse error without running a shell. Windows learners use the same Bash quoting, because the classroom and the contributor route both run inside WSL 2.

The maintained contributor route uses the prepared POSIX/WSL environment:

```sh
uv run --no-sync python -m your_package.record_tool "data/input records.json" --limit 3
```

Run it from the repository root with the named package prepared. Host files
are separate from Docker classroom pads and progress. Without the quotes, the
shell splits the path at the space; `shlex.split` applies the same POSIX rules
and shows the argument lists that argparse would receive:

```python
import contextlib
import io
import shlex

quoted = shlex.split('record-tool "data/input records.json" --limit 3')
unquoted = shlex.split("record-tool data/input records.json --limit 3")
assert quoted[1] == "data/input records.json"
assert unquoted[1:3] == ["data/input", "records.json"]

errors = io.StringIO()
with contextlib.redirect_stderr(errors):
    try:
        build_parser().parse_args(unquoted[1:])
    except SystemExit as exit_error:
        assert exit_error.code == 2
assert "unrecognized arguments: records.json" in errors.getvalue()
```

## Exercises 6-10: Expanded mastery answers

### Exercise 6: answer contract

**Learner contract:** **Prediction:** Predict the Python types produced by `argparse` when `--input` uses `type=Path` and `--limit` uses `type=int`. **Progressive hint:** The parser performs declared conversions before `main` receives values. **Verify:** Call `parse_args` with explicit text and assert the parsed input is a `Path`, limit is an `int`, and defaults have the documented types.

**Reasoning:** argparse applies each option's `type` before `parse_args` returns, so `--input data/in.csv` becomes a `Path` and `--limit 5` becomes the integer 5. An absent option gets its `default`, which is `None` unless declared otherwise, so code must handle `limit is None` explicitly. The shared implementation for Exercises 6-7 asserts both types and the missing-option default. Converting inside `main` with `int(args.limit)` would duplicate argparse's job and produce a traceback instead of a usage message for bad input.

### Exercise 7: answer contract

**Learner contract:** **Tracing:** Trace one row through read → clean → summarize → write, and label which stages are I/O boundaries versus pure work. **Progressive hint:** A pure transform accepts and returns data without reading global state. **Verify:** For one fixture row, record the value/shape after every stage and assert only read/write touch files while the middle stages work from passed data.

**Reasoning:** Tracing one row shows where the program touches the outside world: `read_rows` and `write_summary` are I/O boundaries, while `clean` and `summarize` are pure functions that take data and return data. In the shared implementation for Exercises 6-7, the row `' Ada ', '10.5'` becomes `{'name': 'Ada', 'amount': 10.5}`, then the summary `{'rows': 1, 'total': 10.5}`, then the line `rows=1 total=10.50`. Using `io.StringIO` at both ends lets the whole pipeline run in memory, which is exactly why the pure middle is easy to test.

### Exercise 8: answer contract

**Learner contract:** **Implementation:** Add `--overwrite` and refuse to replace an existing output unless the flag is present. **Progressive hint:** Check the destination before performing the write. **Verify:** Use a temporary existing destination: assert refusal leaves content unchanged without the flag and `--overwrite` deliberately replaces it with the flag.

**Reasoning:** The destination check happens before anything is opened for writing, so a refused run cannot truncate or partly overwrite an existing file. `--overwrite` is a `store_true` flag: absent means `False`, present means `True`, and the check passes only when replacement was requested. The shared implementation for Exercises 8-10 runs `main` against an existing file twice: without the flag it returns 2 and the content is still `old`; with the flag it returns 0 and the file is replaced. Checking after opening the file in `"w"` mode would be too late, because opening truncates it.

### Exercise 9: answer contract

**Learner contract:** **Debugging:** Repair a module that parses arguments and writes files during import. **Progressive hint:** Move behavior into `main(argv)` and use the `__main__` guard. **Verify:** Import the module while capturing output/files and assert no parser or write occurs; then assert `main([...])` performs the intended operation.

**Reasoning:** Module-level code runs on import, so a module that parses arguments and writes files at the top level does both whenever a test or another module imports it, and argparse may even exit the process because the importer's arguments are not the tool's. Moving the work into `main(argv)` and calling it only under the `__main__` guard makes import side-effect free, and `main([...])` then runs the same behavior with explicit arguments. The shared implementation for Exercises 8-10 has this shape: importing defines `parse_args`, `ensure_writable_output`, and `main`, and nothing runs until `main` is called.

### Exercise 10: answer contract

**Learner contract:** **Edge case and explanation:** Define exit codes/messages for missing input, malformed data, existing output, and unexpected internal failure; decide which layers log. **Progressive hint:** Translate expected boundary failures once, without hiding tracebacks in tests. **Verify:** Exercise all four failure categories and assert their exit codes/messages; an injected unexpected error must remain visible in tests rather than being mislabeled.

**Reasoning:** Each expected failure gets one translation at the boundary: a missing input, malformed data, and an existing output become a one-line `error: ...` message and exit status 2, which users and scripts can act on. An unexpected internal failure, such as a `KeyError` from a bug, is not caught, so tests show its full traceback and a production application can log it once at the top level with a different nonzero status. Catching `Exception` in `main` to turn every failure into status 2 would mislabel bugs as user errors; the shared implementation for Exercises 8-10 keeps the `except` clause narrow.

## Expanded mastery lab solutions

Keep command parsing and file I/O at thin boundaries around pure, importable transformations. Make failures observable through exit codes.

### Shared implementation for Exercises 6-7: Parsed types and boundaries

`type=Path` produces a `Path`; `type=int` produces an integer or lets argparse
report invalid text. Reading and writing are boundaries; deterministic cleaning
and summarization should be pure enough to test in memory.

```python
import argparse
import csv
import io
from pathlib import Path

option_parser = argparse.ArgumentParser()
option_parser.add_argument("--input", type=Path)
option_parser.add_argument("--limit", type=int)
options = option_parser.parse_args(["--input", "data/in.csv", "--limit", "5"])
assert isinstance(options.input, Path) and options.limit == 5
assert option_parser.parse_args([]).limit is None  # absent option -> default


def read_rows(handle: io.StringIO) -> list[dict[str, str]]:  # I/O boundary
    return list(csv.DictReader(handle))


def clean(rows: list[dict[str, str]]) -> list[dict[str, object]]:  # pure
    return [{"name": row["name"].strip(), "amount": float(row["amount"])} for row in rows]


def summarize(rows: list[dict[str, object]]) -> dict[str, float]:  # pure
    return {"rows": len(rows), "total": sum(float(str(row["amount"])) for row in rows)}


def write_summary(summary: dict[str, float], handle: io.StringIO) -> None:  # I/O boundary
    handle.write(f"rows={summary['rows']} total={summary['total']:.2f}\n")


raw = read_rows(io.StringIO("name,amount\n Ada ,10.5\n"))
cleaned = clean(raw)
summary = summarize(cleaned)
sink = io.StringIO()
write_summary(summary, sink)
assert raw == [{"name": " Ada ", "amount": "10.5"}]
assert cleaned == [{"name": "Ada", "amount": 10.5}]
assert summary == {"rows": 1, "total": 10.5}
assert sink.getvalue() == "rows=1 total=10.50\n"
```

### Shared implementation for Exercises 8-10: Safe overwrite and importable entry point

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
        # read -> clean -> summarize -> write belongs here; copying stands in for it.
        args.out.write_text(args.input.read_text(encoding="utf-8"), encoding="utf-8")
    except (FileNotFoundError, FileExistsError, ValueError) as error:
        print(f"error: {error}")  # One user-facing boundary translation.
        return 2
    return 0


parsed = parse_args(["--input", "in.csv", "--out", "out.csv", "--limit", "10"])
assert isinstance(parsed.input, Path) and parsed.limit == 10

import contextlib
import io
import tempfile

with tempfile.TemporaryDirectory() as folder:
    source = Path(folder) / "in.csv"
    source.write_text("name\nAda\n", encoding="utf-8")
    existing = Path(folder) / "out.csv"
    existing.write_text("old", encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["--input", str(source), "--out", str(existing)]) == 2
    assert existing.read_text(encoding="utf-8") == "old"  # refused, unchanged
    assert main(["--input", str(source), "--out", str(existing), "--overwrite"]) == 0
    assert existing.read_text(encoding="utf-8") == "name\nAda\n"  # replaced on request

# Production module only:
# if __name__ == "__main__":
#     raise SystemExit(main())
```

Expected user/data errors can return `2`; unexpected programming failures
should propagate during tests and normally produce a controlled top-level log
with a distinct nonzero code in a production application.
