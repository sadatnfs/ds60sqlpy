# Package engineering and a local release workflow

**Stable ID:** `python-pro-01`

**Level:** intermediate

**Estimated time:** 120–180 minutes

## Level and prerequisites

- **Catalog prerequisite:** `python-15`
- Python Days 1–15, especially modules, testing, tooling, and the CLI project
- The repository environment created during connected setup
- Comfort running a Python file from the repository root

The complete lesson is offline after `build`, `pip`, `setuptools`, and `wheel` have
been installed. It does not publish anything or contact a package index.

## Learning objectives

By the end, you can:

1. Explain why a `src/` layout catches accidental working-tree imports.
2. Identify the project, build-system, tool, optional-dependency, and
   dependency-group tables in `pyproject.toml`.
3. explain when an environment marker activates a dependency.
4. Build a wheel and source distribution without fetching build requirements.
5. Install a wheel into a fresh local target and prove its import origin.
6. Expose and inspect a console-script entry point.

### Motivation

A folder that runs on its author's computer is not yet a distributable Python
project. A package needs declared metadata, a build backend, repeatable
artifacts, and evidence that consumers can import the installed artifact. This
workflow also prevents a common false positive: tests passing because Python
found the source checkout instead of the package you built.

## Vocabulary and concepts

- **Distribution package:** the installable project described by metadata, such
  as `ds60-tiny-greeter`.
- **Import package:** the module name used by Python, such as
  `ds60_tiny_greeter`. It need not match the distribution name.
- **`src/` layout:** import packages live below `src/`, so the repository root
  is not itself an import location for them.
- **Build backend:** a tool implementing the standard build hooks. The fixture
  uses `setuptools.build_meta`.
- **Build frontend:** the command that calls those hooks. This lesson uses
  `python -m build`.
- **Wheel:** a built archive intended for installation without executing a
  package build.
- **Source distribution (sdist):** an archive of source and metadata from which
  another build can be performed.
- **Environment marker:** a condition such as `sys_platform == 'win32'` that
  makes a dependency conditional.
- **Dependency group:** development dependencies that are not part of the
  installed runtime metadata.
- **Console script:** metadata mapping a command name to an importable function.
- **Build isolation:** creation of a temporary build environment whose
  requirements may be downloaded. We disable it for the offline exercise.

## Worked example / walkthrough

### Read the project contract

Open
[`fixtures/tiny_package/pyproject.toml`](../fixtures/tiny_package/pyproject.toml).
Notice the roles of its tables:

- `[build-system]` selects the backend and its bootstrap requirements.
- `[project]` is standardized install metadata.
- `[project.scripts]` exposes `ds60-greet`.
- `[project.optional-dependencies]` describes a user-installable feature.
- `[dependency-groups]` keeps test and quality tools out of runtime metadata.
- `[tool.setuptools...]` and `[tool.pytest...]` configure particular tools.

Now run the answer-free learner artifact.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_pro_01_package_engineering.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_pro_01_package_engineering.py
```

Predict whether the name printed from `[project]` contains a hyphen or an
underscore. Then compare it with the import directory under `src/`.

### Wheel versus source distribution

A wheel name ends in `.whl` and contains compatibility tags. Installation
mostly unpacks its files. An sdist usually ends in `.tar.gz`; installing it
requires a build backend and therefore has more opportunities for platform,
tool-version, or offline failures.

Both artifacts are valuable:

- Test the wheel because that is what many users install.
- Inspect or retain the sdist when downstream builders need source.
- Do not assume that successfully importing from the checkout proves either
  artifact works.

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

Work from the repository root. First run the answer-free learner
module named in this guide's original walkthrough. Read each TODO as a
contract: record the input, returned value, raised exception, and side
effect before implementing it. Then run the focused test command in
**Self-check**. Keep exploratory changes in a copy or a new test; the
checked-in solution remains a comparison artifact.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_pro_01_package_engineering.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_pro_01_package_engineering.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

A source tree is not the deliverable. The build backend reads
`pyproject.toml` and creates a wheel containing import packages plus
distribution metadata. The **distribution name** used by installers
may differ from the Python **import name**. A src layout prevents an
accidental import from the repository root from masquerading as a
successful installation.

A release check therefore builds a wheel, inspects its contents and
metadata, installs it into a clean environment, imports it from outside
the source tree, runs tests, and records hashes. Editable installs are
useful for development but do not prove the wheel.

- **`[build-system]`:** declares the backend and bootstrap requirements that turn source into a distribution artifact.
- **`[project]` metadata:** defines distribution identity, version, Python range, dependencies, and entry points.
- **`python -m build` then clean install:** proves the built wheel, not repository-path import behavior.

### Micro-example A — distinguish distribution and import identities

```python
import importlib.util

distribution_name = "beautiful-soup4"
import_name = "bs4"
print({"installer_name": distribution_name, "import_name": import_name})
# The names are contracts for different tools and need not match.
assert distribution_name.replace("-", "_") != import_name
print("installed import available:", importlib.util.find_spec(import_name) is not None)
```

**Expected observation:** Installer and import identifiers can differ; availability must be checked through the intended interface.

**Why it matters:** This mechanics example does not install anything and does not require `bs4` to be present.

### Micro-example B — create a deterministic source manifest digest

```python
import hashlib

files = {
    "src/tiny/__init__.py": b'__version__ = "1.0.0"\n',
    "src/tiny/core.py": b"def add(a, b): return a + b\n",
}
manifest = "\n".join(
    f"{path}:{hashlib.sha256(content).hexdigest()}" for path, content in sorted(files.items())
)
digest = hashlib.sha256(manifest.encode("utf-8")).hexdigest()
print(manifest, digest, sep="\n")
assert len(digest) == 64
```

**Expected observation:** Sorting paths and hashing exact bytes gives a repeatable content identity, not a claim about package quality.

**Why it matters:** The manifest includes every release-relevant file and normalizes no bytes silently.

### Debugging and transfer

**Common mistake:** Running an import from the repo root and concluding that the wheel contains the right packages and data.

**Diagnostic:** Inspect wheel ZIP paths/METADATA/RECORD, install into a new environment, change the working directory, and print `module.__file__` plus distribution version.

**Transfer question:** What extra checks would a package with a console script, typed marker, and package data need before publication?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercises

Work in
[`lessons/py_pro_01_package_engineering.py`](../lessons/py_pro_01_package_engineering.py)
or a copy under `.learning/`.

### Exercise 1 — classify artifacts

Implement `classify_artifact`. Use complete final suffixes and reject
`package.whl.txt`. Add checks for one wheel, one sdist, and one unsupported
file.

Hint: `Path.suffix` handles `.whl`; `Path.name.endswith(".tar.gz")` handles the
two-part sdist suffix.

**Verify:** classify artifacts — assert classify_artifact accepts project-1.0.whl as wheel and project-1.0.tar.gz as sdist, while package.whl.txt and project.zip return the documented unsupported result/error.

### Exercise 2 — create an offline build command

Implement `offline_build_command` as an argument list. Use the running
interpreter, invoke the `build` module, request both formats, disable isolation,
and choose an explicit output directory.

Why an argument list? It avoids a second round of shell parsing and behaves the
same way in PowerShell, Command Prompt, Bash, and zsh.

**Verify:** create an offline build command — assert the argument list starts with sys.executable and contains -m build --no-isolation --sdist --wheel --outdir followed by the explicit destination; execute no shell and test a path containing spaces.

### Exercise 3 — inspect dependency intent

For each fixture entry, decide whether it is:

- a runtime dependency,

- an optional installed feature,

- a development-only dependency group, or

- a build bootstrap requirement.

Explain when `colorama`'s environment marker is true. Confirm that building
metadata does not install the `test` or `quality` groups.

**Verify:** inspect dependency intent — for each fixture entry, decide whether it is: - a runtime dependency, - an optional installed feature, - a development-only dependency group, or - a build bootstrap requirement; explain when colorama's environment marker is true; confirm that building metadata does not install the test or quality groups.

### Exercise 4 — build in a disposable directory

Use a temporary or ignored directory. A production-quality helper should first
copy the source tree to a disposable staging directory because some backends
write metadata beside the source even when `--outdir` is elsewhere. These
commands intentionally prevent online build isolation.

Windows PowerShell:

```powershell
$work = Join-Path $env:TEMP "ds60-package-lab"
New-Item -ItemType Directory -Force -Path $work | Out-Null
.\.venv\Scripts\python.exe -m build --no-isolation --sdist --wheel --outdir $work python\professional\fixtures\tiny_package
Get-ChildItem $work
```

macOS/Linux:

```bash
work_dir="$(mktemp -d)"
.venv/bin/python -m build --no-isolation --sdist --wheel --outdir "$work_dir" python/professional/fixtures/tiny_package
find "$work_dir" -maxdepth 1 -type f
```

If the frontend reports a missing build requirement, return to connected setup
and install the build tools. Do not remove `--no-isolation` merely to make an
offline test pass.

**Verify:** build in a disposable directory — run the platform command in disposable storage with network disabled; require exit code 0, exactly one sdist and one wheel, no build artifacts beside the staged source, and an explicit missing-build-tool error when unavailable.

### Exercise 5 — prove the installed origin

Install the wheel into a fresh target using `pip install --no-index --no-deps
--target <directory> <wheel>`. Start Python from outside the fixture source
tree, put only that target on `PYTHONPATH`, and print:

- `ds60_tiny_greeter.__file__`,
- the installed distribution version,
- its `console_scripts` entry points, and
- `greeting("wheel")`.

Implement `installed_origin_is_safe` so it accepts only a resolved path under
the fresh target.

**Verify:** prove the installed origin — from outside the source tree, install with --no-index --no-deps into a fresh target and assert module.__file__ resolves under that target, version/entry point match metadata, and greeting('wheel') has the expected value.

### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 6 — build a wheel from the source distribution

Build the fixture sdist in disposable storage, unpack it, build a wheel from that unpacked sdist with `--no-isolation`, and compare the result with the direct wheel build. Record every required local tool.

**Progressive hint:** A direct wheel and an sdist exercise different inclusion paths. Use temporary directories and inspect archive members before rebuilding.

**Verify:** build a wheel from the source distribution — build the fixture sdist in disposable storage, unpack it, build a wheel from that unpacked sdist with --no-isolation, and compare the result with the direct wheel build; record every required local tool.

### Exercise 7 — inspect installed metadata without importing

Use `importlib.metadata` against the fresh target to inspect name, version, requirements, extras, and console scripts before importing the package. Reject unexpected or missing metadata.

**Progressive hint:** Distribution metadata and import packages are related but distinct. Place only the target on the child process search path.

**Verify:** inspect installed metadata without importing — use importlib.metadata against the fresh target to inspect name, version, requirements, extras, and console scripts before importing the package; reject unexpected or missing metadata.

### Exercise 8 — separate reproducibility from equivalence

Build twice from the same clean staged source. Compare file hashes, archive member lists, metadata contents, and installed behavior. Explain which differences are harmless and which invalidate the release.

**Progressive hint:** Start with semantic equivalence. Byte-for-byte reproducibility requires controlled timestamps, toolchains, environment variables, and ordering.

**Verify:** separate reproducibility from equivalence — build twice from the same clean staged source; compare file hashes, archive member lists, metadata contents, and installed behavior; explain which differences are harmless and which invalidate the release.

### Exercise 9 — test dependency markers across targets

Create a review matrix for the fixture's build, runtime, optional, development, and environment-marked dependencies across Windows, macOS, Linux, Python 3.11, and Python 3.12.

**Progressive hint:** Parse marker intent with packaging metadata; do not infer it from the developer machine where the lesson happens to run.

**Verify:** test dependency markers across targets — create a review matrix for the fixture's build, runtime, optional, development, and environment-marked dependencies across Windows, macOS, Linux, Python 3.11, and Python 3.12.

### Exercise 10 — design a local release gate

Write an offline release checklist that verifies clean source, tests, type/lint checks, sdist-to-wheel build, artifact contents, fresh install, metadata, hashes, and secret scan without publishing anything.

**Progressive hint:** Every gate should produce bounded evidence and fail closed. Keep index credentials, signing services, and publication outside this local lab.

**Verify:** design a local release gate — write an offline release checklist that verifies clean source, tests, type/lint checks, sdist-to-wheel build, artifact contents, fresh install, metadata, hashes, and secret scan without publishing anything.

## Self-check

You are done when all statements are true:

- The learner file reports all three TODO functions completed.
- A wheel and an sdist exist only in a temporary or ignored directory.
- The imported module path is beneath the fresh install target, not
  `fixtures/tiny_package/src`.
- Installed metadata contains `ds60-greet`.
- `greeting("wheel")` returns `Hello, wheel!`.
- You can explain why `--no-index --no-deps` and `--no-isolation` cover
  different network risks.

Run the reference tests after attempting the exercises.

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_pro_01_package_engineering -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_pro_01_package_engineering -v
```

The end-to-end build test skips with an explicit reason if the optional local
build tools were not bootstrapped.

## Common pitfalls

- **The build tries to access the internet:** build isolation was left on, or
  the backend is absent locally. Re-run with `--no-isolation` after connected
  bootstrap.
- **An import works before installation:** the current directory or
  `PYTHONPATH` points at `src`. Change to a disposable directory and inspect
  `module.__file__`.
- **The distribution cannot be found:** distribution names use metadata
  lookup; import names use Python identifiers. Use
  `distribution("ds60-tiny-greeter")` but `import ds60_tiny_greeter`.
- **PowerShell treats a path as a command:** invoke the interpreter explicitly
  with `.\.venv\Scripts\python.exe`.
- **A dependency group appears at runtime:** it was incorrectly copied into
  `[project.dependencies]`. Development tools should not burden users.
- **Generated `dist/`, `build/`, or `*.egg-info` appears in Git:** the build
  target was the source tree. Move the experiment to a temporary directory and
  remove only those confirmed generated files.

## Next step

- Compare the solution code with your implementation only after the self-check.
- Add a package fixture of your own beneath `.learning/` with two modules and
  one entry point.
- Continue to `python-svc-01` to package a reliable service boundary or
  `python-pro-02` to choose a concurrency model deliberately.

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-pro-01` — Package engineering and a local release workflow.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize src-layout packaging, build artifacts, metadata, and clean installation. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_pro_01_package_engineering.md`
- learner artifact: `python/professional/lessons/py_pro_01_package_engineering.py`

Treat me as a beginner except for these direct catalog prerequisites:
`python-15`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
