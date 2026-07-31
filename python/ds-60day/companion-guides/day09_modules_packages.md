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

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day09_modules_packages.md`, then open `python/ds-60day/notebooks/day09_modules_packages.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 9 — modules, packages, imports, and `__main__` to practice modules, package namespaces, imports, and safe entry points
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A module is a Python file loaded into a module object and namespace. An
import locates that code, executes its top level once per interpreter
process, caches the module in `sys.modules`, and binds a name in the
importer. Import-time work should therefore be small and predictable.

A package groups modules under one import namespace. Absolute imports
start at a package available on the import path; relative imports name a
sibling or parent within an already established package context.
`python -m package.module` preserves that context, while directly
executing a nested file often does not. The `if __name__ ==
"__main__":` guard keeps CLI behavior out of ordinary imports.

### Vocabulary in plain language

- **module:** a loaded Python file and its namespace.
- **package:** an import namespace containing modules or subpackages.
- **namespace:** a mapping from names to objects.
- **absolute import:** an import written from a top-level package name.
- **relative import:** an import written relative to the current package.
- **entry point:** the deliberate location where execution behavior begins.

### Syntax anatomy

`from statistics import mean` asks the import system for the
`statistics` module and binds only its `mean` attribute locally.
`import statistics as stats` binds the module under `stats`, preserving
visible ownership at each call. In a module, `__name__` equals
`"__main__"` only when that module is the executed entry point.

### Worked example 1 — Compare module and attribute imports

Both styles work; the module-qualified call preserves origin. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import statistics as stats
from statistics import median

values = [2, 3, 100]
(stats.mean(values), median(values), stats.__name__)
```

**Expected observation**

```text
`(35, 3, 'statistics')` (the mean may display as `35`). The alias still refers to the module object.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Observe the import cache

Repeated imports normally return the same module object. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import json
import sys

first = json
import json as second
(first is second, sys.modules["json"] is first)
```

**Expected observation**

```text
`(True, True)`. Python reuses the successfully loaded module from `sys.modules`.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Print `module.__file__` when the wrong same-named module seems to be imported.
2. Run nested package CLIs with `python -m package.module` from the package parent.
3. Inspect `sys.path` as evidence, but do not patch it in lesson code to hide a broken layout.
4. Move shared definitions to a lower-level module when two modules import each other during initialization.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Import a module when origin clarity matters; re-export a small stable public surface from `__init__.py` when users should not depend on internal layout.

**Boundary to remember:** Name shadowing, circular imports, import-time side effects, and direct execution of nested files expose package-context mistakes.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Create a `textutils` package containing `slug.py` with `slugify(text: str) -> str`, and expose `slugify` from `textutils/__init__.py`.
   **Expected behavior:** `textutils.slugify(' Data Science ') == 'data-science'`. **Constraints:** keep implementation out of `__init__.py`, use no `sys.path` modification, and test the import from the package's parent directory.
   **Verify:** From the package parent, import `textutils`, assert the slug result, and print `textutils.slugify.__module__` to prove the public name reaches `slug.py`.

2. Add `textutils/cli.py` that uses an absolute import when called from outside and a package-relative import for an internal sibling example. **Run:** `python -m textutils.cli 'Hello World'`. **Expected output:** `hello-world`. **Constraints:** protect CLI execution with `if __name__ == '__main__':` and demonstrate that `import textutils.cli` produces no CLI output.
   **Verify:** Capture `hello-world` from module execution and capture no output from ordinary import in a fresh interpreter.

### Additional mastery practice

A module is executed once per interpreter process and then cached. Package layout and invocation style determine whether imports resolve.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict `__name__` when a file is executed directly versus imported. Which path should run CLI behavior?
   **Progressive hint:** Direct execution uses `__main__`; imports use the module's name.
   **Verify:** Capture `__name__` from direct module execution and import; assert CLI output occurs only in the `__main__` case.
4. **Tracing:** Trace two ordinary imports of the same module and explain the role of `sys.modules` in avoiding repeated top-level execution.
   **Progressive hint:** The module object is cached after its first successful import.
   **Verify:** Use a top-level counter or identity check to prove two imports return the same module object and top-level initialization runs once.
5. **Implementation:** Sketch a `textutils` package exposing `slugify` from `__init__.py` while keeping implementation in `slug.py`.
   **Progressive hint:** The public import surface can be smaller than the package tree.
   **Verify:** From a clean interpreter, assert both `from textutils import slugify` and the internal module call resolve to the same implementation.
6. **Debugging:** Explain why `python textutils/cli.py` can break a relative import and repair the invocation without modifying `sys.path`.
   **Progressive hint:** Run the module from its package parent with `python -m textutils.cli`.
   **Verify:** Show direct nested-file execution fails for the expected package-context reason, then assert `python -m textutils.cli` succeeds without modifying `sys.path`.
7. **Edge case and explanation:** Break a two-module circular import by moving shared types/constants or by passing dependencies explicitly.
   **Progressive hint:** Do not hide the cycle with an unexplained import inside every function.
   **Verify:** Import both modules from a clean process after refactoring; assert neither exposes a partially initialized attribute and describe the removed dependency cycle.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-09`
(Day 9 — Modules, Packages, Imports, and `__main__`). Direct catalog prerequisites: `python-08`.
I have completed the direct prerequisites: `python-08`. Emphasize modules, package namespaces, imports, and safe entry points.
Read `python/ds-60day/companion-guides/day09_modules_packages.md` and use the learner notebook
`python/ds-60day/notebooks/day09_modules_packages.ipynb`. Do not open or quote anything under `solutions/` unless
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
