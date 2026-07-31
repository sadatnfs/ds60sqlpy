# Day 09 — Solutions: Modules, Packages, Imports, __main__

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**modules, package namespaces, imports, and safe entry points**.

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

### Vocabulary used in the worked answers

- **module:** a loaded Python file and its namespace.
- **package:** an import namespace containing modules or subpackages.
- **namespace:** a mapping from names to objects.
- **absolute import:** an import written from a top-level package name.
- **relative import:** an import written relative to the current package.
- **entry point:** the deliberate location where execution behavior begins.

### Reference pattern 1 — Compare module and attribute imports

Both styles work; the module-qualified call preserves origin.

```python
import statistics as stats
from statistics import median

values = [2, 3, 100]
(stats.mean(values), median(values), stats.__name__)
```

**Expected observation:** `(35, 3, 'statistics')` (the mean may display as `35`). The alias still refers to the module object.

### Reference pattern 2 — Observe the import cache

Repeated imports normally return the same module object.

```python
import json
import sys

first = json
import json as second
(first is second, sys.modules["json"] is first)
```

**Expected observation:** `(True, True)`. Python reuses the successfully loaded module from `sys.modules`.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Create a `textutils` package containing `slug.py` with `slugify(text: str) -> str`, and expose `slugify` from `textutils/__init__.py`. **Expected behavior:** `textutils.slugify(' Data Science ') == 'data-science'`. **Constraints:** keep implementation out of `__init__.py`, use no `sys.path` modification, and test the import from the package's parent directory. **Verify:** From the package parent, import `textutils`, assert the slug result, and print `textutils.slugify.__module__` to prove the public name reaches `slug.py`.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies modules, package namespaces, imports, and safe entry points.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Import a module when origin clarity matters; re-export a small stable public surface from `__init__.py` when users should not depend on internal layout.

**Edge case:** Name shadowing, circular imports, import-time side effects, and direct execution of nested files expose package-context mistakes.

**Solution evidence to inspect:** From the package parent, import `textutils`, assert the slug result, and print `textutils.slugify.__module__` to prove the public name reaches `slug.py`.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Add `textutils/cli.py` that uses an absolute import when called from outside and a package-relative import for an internal sibling example. **Run:** `python -m textutils.cli 'Hello World'`. **Expected output:** `hello-world`. **Constraints:** protect CLI execution with `if __name__ == '__main__':` and demonstrate that `import textutils.cli` produces no CLI output. **Verify:** Capture `hello-world` from module execution and capture no output from ordinary import in a fresh interpreter.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies modules, package namespaces, imports, and safe entry points.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Import a module when origin clarity matters; re-export a small stable public surface from `__init__.py` when users should not depend on internal layout.

**Edge case:** Name shadowing, circular imports, import-time side effects, and direct execution of nested files expose package-context mistakes.

**Solution evidence to inspect:** Capture `hello-world` from module execution and capture no output from ordinary import in a fresh interpreter.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict `__name__` when a file is executed directly versus imported. Which path should run CLI behavior? **Progressive hint:** Direct execution uses `__main__`; imports use the module's name. **Verify:** Capture `__name__` from direct module execution and import; assert CLI output occurs only in the `__main__` case.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying modules, package namespaces, imports, and safe entry points.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Import a module when origin clarity matters; re-export a small stable public surface from `__init__.py` when users should not depend on internal layout.

**Edge case:** Name shadowing, circular imports, import-time side effects, and direct execution of nested files expose package-context mistakes.

**Solution evidence to inspect:** Capture `__name__` from direct module execution and import; assert CLI output occurs only in the `__main__` case.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace two ordinary imports of the same module and explain the role of `sys.modules` in avoiding repeated top-level execution. **Progressive hint:** The module object is cached after its first successful import. **Verify:** Use a top-level counter or identity check to prove two imports return the same module object and top-level initialization runs once.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the modules, package namespaces, imports, and safe entry points model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Import a module when origin clarity matters; re-export a small stable public surface from `__init__.py` when users should not depend on internal layout.

**Edge case:** Name shadowing, circular imports, import-time side effects, and direct execution of nested files expose package-context mistakes.

**Solution evidence to inspect:** Use a top-level counter or identity check to prove two imports return the same module object and top-level initialization runs once.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Sketch a `textutils` package exposing `slugify` from `__init__.py` while keeping implementation in `slug.py`. **Progressive hint:** The public import surface can be smaller than the package tree. **Verify:** From a clean interpreter, assert both `from textutils import slugify` and the internal module call resolve to the same implementation.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies modules, package namespaces, imports, and safe entry points.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Import a module when origin clarity matters; re-export a small stable public surface from `__init__.py` when users should not depend on internal layout.

**Edge case:** Name shadowing, circular imports, import-time side effects, and direct execution of nested files expose package-context mistakes.

**Solution evidence to inspect:** From a clean interpreter, assert both `from textutils import slugify` and the internal module call resolve to the same implementation.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Explain why `python textutils/cli.py` can break a relative import and repair the invocation without modifying `sys.path`. **Progressive hint:** Run the module from its package parent with `python -m textutils.cli`. **Verify:** Show direct nested-file execution fails for the expected package-context reason, then assert `python -m textutils.cli` succeeds without modifying `sys.path`.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in modules, package namespaces, imports, and safe entry points.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Import a module when origin clarity matters; re-export a small stable public surface from `__init__.py` when users should not depend on internal layout.

**Edge case:** Name shadowing, circular imports, import-time side effects, and direct execution of nested files expose package-context mistakes.

**Solution evidence to inspect:** Show direct nested-file execution fails for the expected package-context reason, then assert `python -m textutils.cli` succeeds without modifying `sys.path`.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Break a two-module circular import by moving shared types/constants or by passing dependencies explicitly. **Progressive hint:** Do not hide the cycle with an unexplained import inside every function. **Verify:** Import both modules from a clean process after refactoring; assert neither exposes a partially initialized attribute and describe the removed dependency cycle.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from modules, package namespaces, imports, and safe entry points.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Import a module when origin clarity matters; re-export a small stable public surface from `__init__.py` when users should not depend on internal layout.

**Edge case:** Name shadowing, circular imports, import-time side effects, and direct execution of nested files expose package-context mistakes.

**Solution evidence to inspect:** Import both modules from a clean process after refactoring; assert neither exposes a partially initialized attribute and describe the removed dependency cycle.
<!-- END BEGINNER SOLUTION REVIEW -->

We create a minimal package `textutils` with a `slugify` helper, install it in editable mode, and demonstrate absolute vs relative imports.

Contents
- Exercise 1: Create package `textutils` with function `slugify`
- Exercise 2: Import it from a script using absolute and relative imports

---

Exercise 1 — Create package
Directory layout (recommended modern layout):
```
project/
  pyproject.toml
  src/
    textutils/
      __init__.py
      slug.py
  tests/
```

pyproject.toml (minimal)
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "textutils"
version = "0.1.0"
description = "Tiny text utilities for the DS course"
authors = [{ name = "You" }]
requires-python = ">=3.10"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

src/textutils/__init__.py
```python
from .slug import slugify
__all__ = ["slugify"]
```

src/textutils/slug.py
```python
import re

_slug_chars = re.compile(r"[^a-z0-9-]+")
_multi_dash = re.compile(r"-{2,}")

def slugify(s: str, *, maxlen: int | None = None) -> str:
    """Return a URL-safe slug (lowercase letters, digits, single hyphens).

    Args:
        s: input text
        maxlen: optional maximum length (truncate safely)
    """
    out = s.strip().lower().replace(" ", "-").replace("_", "-")
    out = _slug_chars.sub("-", out)
    out = _multi_dash.sub("-", out).strip("-")
    if maxlen is not None:
        out = out[:maxlen].rstrip("-")
    return out or "n-a"
```

Install in editable mode (within a venv):
```
pip install -e .
python -c "import textutils; print(textutils.slugify('Hello World!'))"
```

---

Exercise 2 — Absolute vs relative imports
Create a script at project root:

main.py
```python
# Absolute import (preferred when installed)
from textutils import slugify

print(slugify("Hello from absolute import"))
```
Run with:
```
python -m textutils.slug      # module as a script
python main.py                # script using installed package
```

Relative import example (inside package only):
```python
# src/textutils/other.py (inside the same package)
from .slug import slugify     # relative import to sibling module

print(slugify("Relative import works inside packages"))
```
Notes
- Prefer absolute imports in application code once your package is installed in the environment.
- Avoid manipulating sys.path manually; use editable installs instead.

---

## Expanded mastery lab solutions

A module is executed once per interpreter process and then cached. Package layout and invocation style determine whether imports resolve.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Import execution

The guard `if __name__ == "__main__":` runs only for direct/module execution,
not for import. Successful imports are cached in `sys.modules`; repeated
ordinary imports reuse the same module object.

### Practices 3–5 — A small, intentional package surface

```text
textutils/
  __init__.py
  slug.py
  cli.py
```

```python
# textutils/slug.py
import re


def slugify(text: str) -> str:
    """Return lowercase words joined by one hyphen."""

    return "-".join(re.findall(r"[a-z0-9]+", text.casefold()))


# textutils/__init__.py
# from .slug import slugify

# textutils/cli.py
# from .slug import slugify
#
# def main() -> int:
#     print(slugify("Data Tools"))
#     return 0
#
# if __name__ == "__main__":
#     raise SystemExit(main())

assert slugify("  Data & Tools  ") == "data-tools"
```

Invoke the CLI from the package's parent:

```text
python -m textutils.cli
```

For a cycle such as `models -> formatting -> models`, move shared protocols or
constants into a third dependency-neutral module. Another sound design is for
`models` to accept a formatter callable rather than importing presentation
logic. Both approaches make dependency direction visible.
