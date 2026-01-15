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
