# Day 9 — Modules, Packages, Imports, and `__main__`

**Level:** Beginner

Moving code out of a notebook makes it reusable, testable, and callable from
more than one entry point.

## Learning objectives

By the end of this lesson, you can:

- distinguish a module, a package, and an importable name;
- organize reusable code separately from code that runs the program;
- use absolute and intra-package relative imports appropriately;
- explain the `if __name__ == "__main__"` guard;
- run a package module from the repository root.

## Prerequisites

Complete Day 8 (`python-08`): functions, paths, and file boundaries.

## Vocabulary and mental model

- **Module:** one importable Python file.
- **Package:** a directory of importable modules (normally containing
  `__init__.py` for this course).
- **Import path:** dotted module name resolved from Python's search path.
- **Entry point:** code intentionally invoked to start a program.
- **`__name__`:** a module attribute; it is `"__main__"` only for the module
  being executed as the entry point.

Importing should define reusable objects, not unexpectedly run the application.

## Worked example

```text
demo/
  __init__.py
  formatters.py
  __main__.py
```

```python
# demo/formatters.py
def title(text: str) -> str:
    return text.strip().title()


# demo/__main__.py
from demo.formatters import title

print(title("  daily report  "))
```

Run from the directory containing `demo`.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m demo
```

macOS/Linux:

```bash
.venv/bin/python -m demo
```

## Exercises and progressive hints

1. Create a `textutils` package with a `slugify` function. **Hint:** begin with
   the smallest package tree and prove `import textutils` works from its parent.
2. Import it from an external script with an absolute import and from another
   `textutils` module with a relative import. **Hint:** run the package context
   with `python -m ...`; executing a nested file directly loses that context.

### Additional mastery practice

A module is executed once per interpreter process and then cached. Package layout and invocation style determine whether imports resolve.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict `__name__` when a file is executed directly versus imported. Which path should run CLI behavior?
   **Progressive hint:** Direct execution uses `__main__`; imports use the module's name.
4. **Tracing:** Trace two ordinary imports of the same module and explain the role of `sys.modules` in avoiding repeated top-level execution.
   **Progressive hint:** The module object is cached after its first successful import.
5. **Implementation:** Sketch a `textutils` package exposing `slugify` from `__init__.py` while keeping implementation in `slug.py`.
   **Progressive hint:** The public import surface can be smaller than the package tree.
6. **Debugging:** Explain why `python textutils/cli.py` can break a relative import and repair the invocation without modifying `sys.path`.
   **Progressive hint:** Run the module from its package parent with `python -m textutils.cli`.
7. **Edge case and explanation:** Break a two-module circular import by moving shared types/constants or by passing dependencies explicitly.
   **Progressive hint:** Do not hide the cycle with an unexplained import inside every function.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- What code runs the first time a module is imported?
- Why should a library module avoid prompting for input at import time?
- What does `python -m package.module` preserve that `python module.py` may not?
- When is `from .formatters import title` valid?

Expected behavior: the package imports from its parent directory, importing it
does not run a CLI, and module execution uses the intended entry point.

## Common pitfalls and diagnosis

- **`ModuleNotFoundError`:** print the working directory and confirm you are
  running from the project root or have installed the package.
- **"attempted relative import with no known parent package":** use
  `python -m package.module` instead of executing the file directly.
- **A local file shadows a package:** rename files such as `json.py`,
  `pandas.py`, or `pytest.py`, then remove the local cache.
- **Circular imports:** move shared definitions to a lower-level module and keep
  dependency direction one-way.
- **Work runs during import:** move entry-point behavior into `main()` and guard
  the call.

## Continue

- [Open the learner notebook](../notebooks/day09_modules_packages.ipynb)
- [Check the separate solution](../solutions/day09_modules_packages/day09_solutions.md)
- [Next: Day 10 — Testing with pytest](day10_testing_pytest.md)
