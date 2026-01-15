# Day 9 — Modules, Packages, and the Import System (Companion Guide)

## Learning objectives
- Organize code into modules and packages; understand how Python finds imports
- Use `__main__` to make modules runnable as scripts
- Structure a small package and install it in editable mode

## Why this matters
As projects grow, good structure prevents circular imports, name collisions, and untestable monoliths. A clear layout is a gift to your future self.

## Mental models
- A module is a `.py` file; a package is a directory with `__init__.py`
- `sys.path` controls where Python looks for imports; use virtualenv and install your package (`pip install -e .`) instead of manipulating `sys.path`

## Minimal package layout
```
mypkg/
  pyproject.toml
  src/
    mypkg/
      __init__.py
      utils.py
  tests/
```
`pyproject.toml` with `project` metadata + `pip install -e .` → importable in your venv.

## `__main__` entry point
```python
# mypkg/cli.py
def main():
    ...

if __name__ == '__main__':
    main()
```
Expose console scripts via `pyproject.toml` `[project.scripts]`.

## Common pitfalls
- Importing from a sibling file using relative paths and ad‑hoc `sys.path` hacks
- Circular imports caused by placing runtime code at module import time; wrap in functions
- Name collisions with standard library modules (e.g., naming your `email.py`)

## Practice exercises
1) Create `textutils` with a `slugify` function and unit tests; install with `pip install -e .`
2) Add a CLI entry point `textutils-slugify` that slugs input from the command line
3) Use `__all__` in `__init__.py` to control what `from mypkg import *` exports (and why you rarely need it)

## Further reading
- Packaging tutorial: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- Python import system: https://docs.python.org/3/reference/import.html
