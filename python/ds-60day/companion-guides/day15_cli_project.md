# Day 15: Project: A Testable Command-Line Data Tool

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

Complete Days 1-14, especially packages (`python-09`), pytest (`python-10`),
logging (`python-11`), and quality tooling (`python-14`).

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Open `python-15` in the classroom, or `python/ds-60day/notebooks/day15_cli_project.ipynb` on a host; the [Python study guide](../../STUDY-GUIDE.md) explains both.

**Outcome:** Build and test a small command-line tool that summarizes a CSV file.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive: build the idea before the syntax

### Start with one mental picture

A command-line interface (CLI) has three layers: parse external strings,
call ordinary Python logic with typed values, then present a result and
choose an exit status. Keeping the core logic free from `sys.argv`,
printing, and process exit makes it reusable from tests and notebooks.

`argparse` defines flags, help, conversion, and validation close to the
command boundary. A `main(argv: list[str] | None = None) -> int`
function is testable because tests can pass an explicit list rather than
changing the real process arguments. The guarded entry point should do
little more than `raise SystemExit(main())`.

### Vocabulary in plain language

- **CLI:** a text interface driven by command-line arguments and exit status.
- **argument parser:** a component that converts command text into named values.
- **option:** a named flag such as `--limit`.
- **positional argument:** a value identified by its position.
- **exit status:** an integer process result where zero normally means success.
- **entry point:** the small boundary that starts application execution.

### Syntax anatomy

`parser.add_argument("--limit", type=int, default=10)` declares the
spelling, conversion, and fallback. `parser.parse_args(argv)` returns a
namespace of parsed values. Supplying `argv` makes tests deterministic;
`None` tells argparse to read the real process command line.

### Worked example 1: Parse an explicit argument list

Exercise the CLI contract without touching the notebook process arguments. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

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

### Worked example 2: Keep core work independent of printing

A plain function can be tested and reused by the CLI. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def select_names(names: list[str], *, limit: int) -> list[str]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    return [name.strip().title() for name in names[:limit]]


select_names(args.names, limit=args.limit)
```

**Expected observation:** `['Ada', 'Lin']`. Parsing and presentation remain outside the core transformation.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Print or test `vars(args)` when parsed values do not match the declared options.
2. Keep file I/O and transformation out of the parser-building function.
3. Return an exit code from `main`; avoid calling `sys.exit` deep inside reusable logic.
4. Test help, required arguments, invalid conversion, normal output, and output-file behavior separately.

### Practice ramp

Work this lesson's exercises in the five practice modes from the [Python study guide](../../STUDY-GUIDE.md).

**Useful alternative:** A notebook suits interactive exploration; a CLI suits repeatable parameterized execution; a library function should hold shared core logic.

**Boundary to remember:** Paths with spaces, missing files, invalid encodings, empty input, existing output files, and Windows shell quoting need tests.
<!-- END BEGINNER DEEP DIVE -->

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

1. Build the Day 15 CLI with subcommands or flags that read a local CSV/JSON input, perform one documented transformation, and write or print a bounded result. **Architecture:** `build_parser()`, pure core function(s), and `main(argv=None) -> int`. **Constraints:** use `pathlib`, UTF-8, no notebook-only state, and no hard-coded absolute paths.
   **Verify:** assert `--help` exits `0` and names the command/options, a valid fixture exits `0` with the expected bounded output, and invalid input exits nonzero with a useful stderr message.

2. Add options for input path, output path, and a typed transformation parameter such as `--limit`.
   **Expected behavior:** argparse rejects invalid numeric text and the application returns a nonzero status for a missing input without a traceback aimed at beginners. **Constraint:** do not catch programming errors broadly.
   **Verify:** Exercise valid options, invalid integer text, and a missing input; assert parsed Python types and the documented nonzero exit status/message.

3. Write pytest tests that call core logic directly and call `main([...])` with temporary files. **Coverage:** happy path, empty input, missing path, invalid parameter, and output overwrite policy.
   **Verify:** assert return status, captured output, and exact file content without spawning a shell.

4. Package the CLI invocation behind `if __name__ == '__main__': raise SystemExit(main())`.
   **Expected behavior:** importing the module produces no output or process exit; `python -m ... --help` works from the documented package parent.
   **Verify:** test both import and module execution.

5. Create a short README usage block with Bash commands (Linux, macOS, or Ubuntu in Windows WSL 2) that run the tool through the repository interpreter, including an example whose input path contains a space. **Constraint:** quote the path so the shell passes it as a single argument.
   **Verify:** run the documented command, record exit code `0` and the expected output, and confirm that the quoted path with a space arrives as one argument; then remove the quotes once and record the resulting argparse error.

### Additional mastery practice

Keep command parsing and file I/O at thin boundaries around pure, importable transformations. Make failures observable through exit codes.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

6. **Prediction:** Predict the Python types produced by `argparse` when `--input` uses `type=Path` and `--limit` uses `type=int`.
   **Progressive hint:** The parser performs declared conversions before `main` receives values.
   **Verify:** Call `parse_args` with explicit text and assert the parsed input is a `Path`, limit is an `int`, and defaults have the documented types.
7. **Tracing:** Trace one row through read → clean → summarize → write, and label which stages are I/O boundaries versus pure work.
   **Progressive hint:** A pure transform accepts and returns data without reading global state.
   **Verify:** For one fixture row, record the value/shape after every stage and assert only read/write touch files while the middle stages work from passed data.
8. **Implementation:** Add `--overwrite` and refuse to replace an existing output unless the flag is present.
   **Progressive hint:** Check the destination before performing the write.
   **Verify:** Use a temporary existing destination: assert refusal leaves content unchanged without the flag and `--overwrite` deliberately replaces it with the flag.
9. **Debugging:** Repair a module that parses arguments and writes files during import.
   **Progressive hint:** Move behavior into `main(argv)` and use the `__main__` guard.
   **Verify:** Import the module while capturing output/files and assert no parser or write occurs; then assert `main([...])` performs the intended operation.
10. **Edge case and explanation:** Define exit codes/messages for missing input, malformed data, existing output, and unexpected internal failure; decide which layers log.
   **Progressive hint:** Translate expected boundary failures once, without hiding tracebacks in tests.
   **Verify:** Exercise all four failure categories and assert their exit codes/messages; an injected unexpected error must remain visible in tests rather than being mislabeled.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Run the project

Linux, macOS, or Ubuntu in Windows WSL 2:

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
- [Next: Day 16; NumPy fundamentals](day16_numpy_fundamentals.md)

## Ask an AI tutor about this lesson

AI coaching is optional. To use a tutor, copy this prompt from the repository root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-15`
(Day 15: Project: A Testable CLI Data Tool). Direct catalog prerequisites: `python-14`.
I have completed the direct prerequisites: `python-14`. Emphasize a small command-line application with separated boundaries.
Read `python/ds-60day/companion-guides/day15_cli_project.md` and use the learner notebook
`python/ds-60day/notebooks/day15_cli_project.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
