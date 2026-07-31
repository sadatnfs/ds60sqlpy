# Day 09 — Solutions: Modules, Packages, Imports, __main__

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **modules, package namespaces, imports, and safe entry points**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **modules, package namespaces, imports, and safe entry points** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Create a `textutils` package containing `slug.py` with `slugify(text: str) -> str`, and expose `slugify` from `textutils/__init__.py`. **Expected behavior:** `textutils.slugify(' Data Science ') == 'data-science'`. **Constraints:** keep implementation out of `__init__.py`, use no `sys.path` modification, and test the import from the package's parent directory. **Verify:** From the package parent, import `textutils`, assert the slug result, and print `textutils.slugify.__module__` to prove the public name reaches `slug.py`.

**Reasoning:** Implement this exact contract as written: Create a `textutils` package containing `slug.py` with `slugify(text: str) -> str`, and expose `slugify` from `textutils/__init__.py`. Expected behavior: `textutils.slugify(' Data Science ') == 'data-science'`. Constraints: keep implementation out of `__init__.py`, use no `sys.path` modification, and test the import from the package's parent directory. Keep the prompt's named data and constraints visible in the code, then establish this specific result: From the package parent, import `textutils`, assert the slug result, and print `textutils.slugify.__module__` to prove the public name reaches `slug.py`. That connects the answer to modules, package namespaces, imports, and safe entry points.

Use this package tree:

```text
textutils/
  __init__.py
  slug.py
```

`slug.py`:

```python
def slugify(text: str) -> str:
    return "-".join(text.strip().lower().split())
```

`__init__.py`:

```python
from .slug import slugify

__all__ = ["slugify"]
```

From the package parent, `import textutils` now exposes one deliberate
public name without moving implementation into `__init__.py`.

**Verification evidence:** From the package parent, import `textutils`, assert the slug result, and print `textutils.slugify.__module__` to prove the public name reaches `slug.py`.

### Exercise 2 — worked answer

**Learner contract:** Add `textutils/cli.py` that uses an absolute import when called from outside and a package-relative import for an internal sibling example. **Run:** `python -m textutils.cli 'Hello World'`. **Expected output:** `hello-world`. **Constraints:** protect CLI execution with `if __name__ == '__main__':` and demonstrate that `import textutils.cli` produces no CLI output. **Verify:** Capture `hello-world` from module execution and capture no output from ordinary import in a fresh interpreter.

**Reasoning:** Implement this exact contract as written: Add `textutils/cli.py` that uses an absolute import when called from outside and a package-relative import for an internal sibling example. Run: `python -m textutils.cli 'Hello World'`. Expected output: `hello-world`. Constraints: protect CLI execution with `if __name__ == '__main__':` and demonstrate that `import textutils.cli` produces no CLI output. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Capture `hello-world` from module execution and capture no output from ordinary import in a fresh interpreter. That connects the answer to modules, package namespaces, imports, and safe entry points.

`textutils/cli.py`:

```python
from __future__ import annotations

import sys

from .slug import slugify


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print("Usage: python -m textutils.cli TEXT")
        return 2
    print(slugify(arguments[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

Run `python -m textutils.cli "Hello World"` from the package parent.
Importing the module does not call `main`.

**Verification evidence:** Capture `hello-world` from module execution and capture no output from ordinary import in a fresh interpreter.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict `__name__` when a file is executed directly versus imported. Which path should run CLI behavior? **Progressive hint:** Direct execution uses `__main__`; imports use the module's name. **Verify:** Capture `__name__` from direct module execution and import; assert CLI output occurs only in the `__main__` case.

**Reasoning:** Predict this named state change before running it: Prediction: Predict `__name__` when a file is executed directly versus imported. Which path should run CLI behavior? Progressive hint: Direct execution uses `__main__`; imports use the module's name. Then compare the prediction with this proof target: Capture `__name__` from direct module execution and import; assert CLI output occurs only in the `__main__` case. This makes modules, package namespaces, imports, and safe entry points observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Capture `__name__` from direct module execution and import; assert CLI output occurs only in the `__main__` case.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace two ordinary imports of the same module and explain the role of `sys.modules` in avoiding repeated top-level execution. **Progressive hint:** The module object is cached after its first successful import. **Verify:** Use a top-level counter or identity check to prove two imports return the same module object and top-level initialization runs once.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace two ordinary imports of the same module and explain the role of `sys.modules` in avoiding repeated top-level execution. Progressive hint: The module object is cached after its first successful import. Record the named value, shape, label, or iterator position needed to establish: Use a top-level counter or identity check to prove two imports return the same module object and top-level initialization runs once. The trace exposes modules, package namespaces, imports, and safe entry points directly.

**Evidence to locate in the grouped implementation:** Use a top-level counter or identity check to prove two imports return the same module object and top-level initialization runs once.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Sketch a `textutils` package exposing `slugify` from `__init__.py` while keeping implementation in `slug.py`. **Progressive hint:** The public import surface can be smaller than the package tree. **Verify:** From a clean interpreter, assert both `from textutils import slugify` and the internal module call resolve to the same implementation.

**Reasoning:** Implement this exact contract as written: Implementation: Sketch a `textutils` package exposing `slugify` from `__init__.py` while keeping implementation in `slug.py`. Progressive hint: The public import surface can be smaller than the package tree. Keep the prompt's named data and constraints visible in the code, then establish this specific result: From a clean interpreter, assert both `from textutils import slugify` and the internal module call resolve to the same implementation. That connects the answer to modules, package namespaces, imports, and safe entry points.

**Evidence to locate in the grouped implementation:** From a clean interpreter, assert both `from textutils import slugify` and the internal module call resolve to the same implementation.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Explain why `python textutils/cli.py` can break a relative import and repair the invocation without modifying `sys.path`. **Progressive hint:** Run the module from its package parent with `python -m textutils.cli`. **Verify:** Show direct nested-file execution fails for the expected package-context reason, then assert `python -m textutils.cli` succeeds without modifying `sys.path`.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Explain why `python textutils/cli.py` can break a relative import and repair the invocation without modifying `sys.path`. Progressive hint: Run the module from its package parent with `python -m textutils.cli`. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Show direct nested-file execution fails for the expected package-context reason, then assert `python -m textutils.cli` succeeds without modifying `sys.path`. The diagnosis depends on modules, package namespaces, imports, and safe entry points.

**Evidence to locate in the grouped implementation:** Show direct nested-file execution fails for the expected package-context reason, then assert `python -m textutils.cli` succeeds without modifying `sys.path`.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Break a two-module circular import by moving shared types/constants or by passing dependencies explicitly. **Progressive hint:** Do not hide the cycle with an unexplained import inside every function. **Verify:** Import both modules from a clean process after refactoring; assert neither exposes a partially initialized attribute and describe the removed dependency cycle.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Break a two-module circular import by moving shared types/constants or by passing dependencies explicitly. Progressive hint: Do not hide the cycle with an unexplained import inside every function. Values below, at, and above the named boundary must produce the evidence Import both modules from a clean process after refactoring; assert neither exposes a partially initialized attribute and describe the removed dependency cycle. Those cases show how modules, package namespaces, imports, and safe entry points behaves at its edge.

**Evidence to locate in the grouped implementation:** Import both modules from a clean process after refactoring; assert neither exposes a partially initialized attribute and describe the removed dependency cycle.

## Expanded mastery lab solutions

A module is executed once per interpreter process and then cached. Package layout and invocation style determine whether imports resolve.

### Shared implementation for Exercises 3–4 — Import execution

The guard `if __name__ == "__main__":` runs only for direct/module execution,
not for import. Successful imports are cached in `sys.modules`; repeated
ordinary imports reuse the same module object.

### Shared implementation for Exercises 5–7 — A small, intentional package surface

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
