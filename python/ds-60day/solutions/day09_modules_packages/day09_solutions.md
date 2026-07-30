# Day 09 — Solutions: Modules, Packages, Imports, __main__

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Create a `textutils` package with a `slugify` function. **Hint:** begin with the smallest package tree and prove `import textutils` works from its parent.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Import it from an external script with an absolute import and from another `textutils` module with a relative import. **Hint:** run the package context with `python -m ...`; executing a nested file directly loses that context.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict `__name__` when a file is executed directly versus imported. Which path should run CLI behavior?

**Reasoning checkpoint:** Direct execution uses `__main__`; imports use the module's name. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace two ordinary imports of the same module and explain the role of `sys.modules` in avoiding repeated top-level execution.

**Reasoning checkpoint:** The module object is cached after its first successful import. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Sketch a `textutils` package exposing `slugify` from `__init__.py` while keeping implementation in `slug.py`.

**Reasoning checkpoint:** The public import surface can be smaller than the package tree. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Explain why `python textutils/cli.py` can break a relative import and repair the invocation without modifying `sys.path`.

**Reasoning checkpoint:** Run the module from its package parent with `python -m textutils.cli`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Break a two-module circular import by moving shared types/constants or by passing dependencies explicitly.

**Reasoning checkpoint:** Do not hide the cycle with an unexplained import inside every function. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
