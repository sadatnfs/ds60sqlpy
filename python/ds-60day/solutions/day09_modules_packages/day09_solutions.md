# Day 9 Solutions: Modules, Packages, and Imports

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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Create a `textutils` package containing `slug.py` with `slugify(text: str) -> str`, and expose `slugify` from `textutils/__init__.py`. **Expected behavior:** `textutils.slugify(' Data Science ') == 'data-science'`. **Constraints:** keep implementation out of `__init__.py`, use no `sys.path` modification, and test the import from the package's parent directory. **Verify:** From the package parent, import `textutils`, assert the slug result, and print `textutils.slugify.__module__` to prove the public name reaches `slug.py`.

**Reasoning:** Keeping `slugify` in `slug.py` and re-exporting it from `__init__.py` separates where the code lives from what callers import: `import textutils` followed by `textutils.slugify(...)` works, and the implementation can move later without changing callers. `__all__` documents the intended public names. `split()` with no argument splits on any run of whitespace and ignores the ends, so `' Data Science '` becomes `['Data', 'Science']` before joining. The import works only from the folder that contains `textutils/`, because Python finds packages through `sys.path`, whose first entry is the starting directory; editing `sys.path` to force it hides a layout problem instead of fixing it.

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

`__init__.py` (shown as text because a relative import works only inside the package):

```text
from .slug import slugify

__all__ = ["slugify"]
```

From the package parent, `import textutils` now exposes one deliberate
public name without moving implementation into `__init__.py`.

### Exercise 2: worked answer

**Learner contract:** Add `textutils/cli.py` that uses an absolute import when called from outside and a package-relative import for an internal sibling example. **Run:** `python -m textutils.cli 'Hello World'`. **Expected output:** `hello-world`. **Constraints:** protect CLI execution with `if __name__ == '__main__':` and demonstrate that `import textutils.cli` produces no CLI output. **Verify:** Extend the pad recipe's `files` with your package, capture `hello-world` from `[sys.executable, "-m", "textutils.cli", "Hello World"]`, and capture no output from `[sys.executable, "-c", "import textutils.cli"]`.

**Reasoning:** The relative import `from .slug import slugify` names a sibling inside the same package, which works only when Python knows the package, as it does under `python -m textutils.cli`. `main` receives the argument list as a parameter and returns an exit status, so it can be tested by calling `main(["Hello World"])` without a terminal. The `if __name__ == "__main__":` guard means that importing `textutils.cli` defines `main` but prints nothing; only module execution calls it. Returning 2 for a wrong argument count follows the command-line convention for usage errors.

`textutils/cli.py` (also shown as text, for the same reason):

```text
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
Importing the module does not call `main`. The block below writes exactly
these three files into a temporary folder and runs both Verify checks as
child processes, the same way the pad recipe does:

```python
import subprocess
import sys
import tempfile
from pathlib import Path

worked_files = {
    "textutils/__init__.py": 'from .slug import slugify\n\n__all__ = ["slugify"]\n',
    "textutils/slug.py": (
        'def slugify(text: str) -> str:\n    return "-".join(text.strip().lower().split())\n'
    ),
    "textutils/cli.py": (
        "from __future__ import annotations\n\nimport sys\n\nfrom .slug import slugify\n\n\n"
        "def main(arguments: list[str]) -> int:\n"
        "    if len(arguments) != 1:\n"
        '        print("Usage: python -m textutils.cli TEXT")\n'
        "        return 2\n"
        "    print(slugify(arguments[0]))\n"
        "    return 0\n\n\n"
        'if __name__ == "__main__":\n'
        "    raise SystemExit(main(sys.argv[1:]))\n"
    ),
}
checks = {
    "public name": ["-c", "import textutils; print(textutils.slugify(' Data Science '))"],
    "defined in": ["-c", "import textutils; print(textutils.slugify.__module__)"],
    "module run": ["-m", "textutils.cli", "Hello World"],
    "plain import": ["-c", "import textutils.cli"],
}
with tempfile.TemporaryDirectory(prefix="day09-worked-") as folder:
    for name, text in worked_files.items():
        path = Path(folder) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    outputs = {
        label: subprocess.run(
            [sys.executable, *arguments], cwd=folder, capture_output=True, text=True, timeout=30
        ).stdout
        for label, arguments in checks.items()
    }
print(outputs)
assert outputs["public name"] == "data-science\n"
assert outputs["defined in"] == "textutils.slug\n"
assert outputs["module run"] == "hello-world\n"
assert outputs["plain import"] == ""  # importing defines main but prints nothing
```

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict `__name__` when a file is executed directly versus imported. Which path should run CLI behavior? **Progressive hint:** Direct execution uses `__main__`; imports use the module's name. **Verify:** Capture `__name__` from direct module execution and import; assert CLI output occurs only in the `__main__` case.

**Reasoning:** Python sets `__name__` to `"__main__"` for the file it was asked to run and to the module's import name, such as `greeter`, when the file is imported. Top-level code runs in both cases, so anything that should happen only when the file runs as a program belongs under the `if __name__ == "__main__":` guard. The shared implementation for Exercises 3-4 runs one small file both ways in child processes: the script run prints `__name__ = __main__` and the CLI line, while the import prints `__name__ = greeter` and no CLI output.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace two ordinary imports of the same module and explain the role of `sys.modules` in avoiding repeated top-level execution. **Progressive hint:** The module object is cached after its first successful import. **Verify:** Use a top-level counter or identity check to prove two imports return the same module object and top-level initialization runs once.

**Reasoning:** The first `import greeter` runs the module's top-level code once and stores the module object in `sys.modules`; a second import finds it there and returns the same object without running the code again. That is why the shared implementation for Exercises 3-4 sees the top-level message only once although it imports twice, and why `again is sys.modules["greeter"]` is `True`. The cache lasts for the life of the process, so a new Run, which is a new process, executes the top-level code again. `importlib.reload` exists for re-executing a module, but a program rarely needs it.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Sketch a `textutils` package exposing `slugify` from `__init__.py` while keeping implementation in `slug.py`. **Progressive hint:** The public import surface can be smaller than the package tree. **Verify:** From a clean interpreter, assert both `from textutils import slugify` and the internal module call resolve to the same implementation.

**Reasoning:** The package exposes one deliberate public name: `textutils/__init__.py` imports `slugify` from `textutils/slug.py`, so `from textutils import slugify` and `textutils.slug.slugify` are the same function object, which the shared implementation for Exercises 5-7 checks with `is` in a fresh interpreter. Keeping the logic in `slug.py` leaves `__init__.py` a short list of exports that loads quickly and has no side effects. The common mistake is copying the function into `__init__.py`, which creates two implementations that can drift apart.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Explain why `python textutils/cli.py` can break a relative import and repair the invocation without modifying `sys.path`. **Progressive hint:** Run the module from its package parent with `python -m textutils.cli`. **Verify:** Show direct nested-file execution fails for the expected package-context reason, then assert `python -m textutils.cli` succeeds without modifying `sys.path`.

**Reasoning:** `python textutils/cli.py` runs the file as a script: Python puts `textutils/` itself on `sys.path` and gives the module no parent package, so `from .slug import slugify` fails with `ImportError: attempted relative import with no known parent package`. `python -m textutils.cli`, started from the folder that contains `textutils/`, imports the module as part of its package, so the relative import resolves. The shared implementation for Exercises 5-7 runs both commands in child processes and checks the error and the `hello-world` output. Adding the parent folder to `sys.path` inside the file would also silence the error, but it hard-codes a layout assumption that breaks elsewhere.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Break a two-module circular import by moving shared types/constants or by passing dependencies explicitly. **Progressive hint:** Do not hide the cycle with an unexplained import inside every function. **Verify:** Import both modules from a clean process after refactoring; assert neither exposes a partially initialized attribute and describe the removed dependency cycle.

**Reasoning:** A circular import fails because the first module is only partly initialized when the second one imports it back, so a name the second module needs may not exist yet. Moving the shared constant or type into a third module that both import removes the cycle and makes the dependency direction explicit; passing the dependency in as an argument, such as a formatter function, removes it too. Importing inside every function also hides the error, but it scatters the dependency and makes the import order fragile. After the refactor, importing either module first in a fresh process must succeed.

## Expanded mastery lab solutions

A module is executed once per interpreter process and then cached. Package layout and invocation style determine whether imports resolve.

### Shared implementation for Exercises 3-4: Import execution

The guard `if __name__ == "__main__":` runs only for direct/module execution,
not for import. Successful imports are cached in `sys.modules`; repeated
ordinary imports reuse the same module object. The block below runs one small
module both ways in child processes, as the Day 9 pad recipe does.

```python
import subprocess
import sys
import tempfile
from pathlib import Path

greeter_source = (
    'print("top level runs, __name__ =", __name__)\n'
    'if __name__ == "__main__":\n'
    '    print("CLI behavior")\n'
)
import_twice = (
    "import sys; import greeter; import greeter as again; print(again is sys.modules['greeter'])"
)

with tempfile.TemporaryDirectory(prefix="day09-") as folder:
    (Path(folder) / "greeter.py").write_text(greeter_source, encoding="utf-8")
    as_script = subprocess.run(
        [sys.executable, "greeter.py"], cwd=folder, capture_output=True, text=True, timeout=30
    )
    as_import = subprocess.run(
        [sys.executable, "-c", import_twice], cwd=folder, capture_output=True, text=True, timeout=30
    )

print(as_script.stdout)
print(as_import.stdout)
assert "__name__ = __main__" in as_script.stdout and "CLI behavior" in as_script.stdout
assert "__name__ = greeter" in as_import.stdout and "CLI behavior" not in as_import.stdout
assert as_import.stdout.count("top level runs") == 1  # the second import reuses the cache
assert as_import.stdout.strip().endswith("True")
```

### Shared implementation for Exercises 5-7: A small, intentional package surface

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

The block below builds the package in a temporary folder and runs the direct
file, the module form, and a fresh-interpreter import check as child processes:

```python
import subprocess
import sys
import tempfile
from pathlib import Path

package_files = {
    "textutils/__init__.py": 'from .slug import slugify\n\n__all__ = ["slugify"]\n',
    "textutils/slug.py": (
        "import re\n\n\ndef slugify(text: str) -> str:\n"
        '    return "-".join(re.findall(r"[a-z0-9]+", text.casefold()))\n'
    ),
    "textutils/cli.py": (
        "import sys\n\nfrom .slug import slugify\n\n\n"
        "def main(arguments: list[str]) -> int:\n"
        '    print(slugify(" ".join(arguments)))\n'
        "    return 0\n\n\n"
        'if __name__ == "__main__":\n'
        "    raise SystemExit(main(sys.argv[1:]))\n"
    ),
}
same_object = (
    "from textutils import slugify; import textutils.slug as s; print(slugify is s.slugify)"
)


def run(arguments: list[str], folder: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments], cwd=folder, capture_output=True, text=True, timeout=30
    )


with tempfile.TemporaryDirectory(prefix="day09-") as folder:
    for name, text in package_files.items():
        path = Path(folder) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    direct = run(["textutils/cli.py", "Hello World"], folder)
    as_module = run(["-m", "textutils.cli", "Hello World"], folder)
    public_name = run(["-c", same_object], folder)

assert "attempted relative import with no known parent package" in direct.stderr
assert as_module.stdout == "hello-world\n"
assert public_name.stdout.strip() == "True"
```

For a cycle such as `models -> formatting -> models`, move shared protocols or
constants into a third dependency-neutral module. Another sound design is for
`models` to accept a formatter callable rather than importing presentation
logic. Both approaches make dependency direction visible.
