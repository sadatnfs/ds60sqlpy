# Day 15 — CLI Data Tool Project (Companion Guide)

## Goal
Build a small, testable command‑line tool that ingests a CSV, cleans it, and outputs a summary. Include tests and pass black/flake8/mypy.

## Suggested architecture
```
project/
  src/
    cli.py        # argparse or click entry
    io_utils.py   # read_csv/write_csv, safe loaders
    transforms.py # clean/convert functions
  tests/
    test_transforms.py
```

## Steps
1) Implement core transforms as pure functions (no I/O)
2) Write tests for transforms (happy/edge paths)
3) Wire a CLI with argparse or click
4) Add logging and helpful error messages

## Quality gates
- `pytest -q` passes
- `black .`, `flake8 .`, `mypy .` clean

## Stretch goals
- Add `--schema` option (pandera) to validate input columns
- Support reading from stdin/writing to stdout

## Further reading
- argparse: https://docs.python.org/3/library/argparse.html
- click: https://click.palletsprojects.com
