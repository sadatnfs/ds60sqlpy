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

### Exercise 2 — create an offline build command

Implement `offline_build_command` as an argument list. Use the running
interpreter, invoke the `build` module, request both formats, disable isolation,
and choose an explicit output directory.

Why an argument list? It avoids a second round of shell parsing and behaves the
same way in PowerShell, Command Prompt, Bash, and zsh.

### Exercise 3 — inspect dependency intent

For each fixture entry, decide whether it is:

1. a runtime dependency,
2. an optional installed feature,
3. a development-only dependency group, or
4. a build bootstrap requirement.

Explain when `colorama`'s environment marker is true. Confirm that building
metadata does not install the `test` or `quality` groups.

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

### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 6 — build a wheel from the source distribution

Build the fixture sdist in disposable storage, unpack it, build a wheel from that unpacked sdist with `--no-isolation`, and compare the result with the direct wheel build. Record every required local tool.

**Progressive hint:** A direct wheel and an sdist exercise different inclusion paths. Use temporary directories and inspect archive members before rebuilding.

### Exercise 7 — inspect installed metadata without importing

Use `importlib.metadata` against the fresh target to inspect name, version, requirements, extras, and console scripts before importing the package. Reject unexpected or missing metadata.

**Progressive hint:** Distribution metadata and import packages are related but distinct. Place only the target on the child process search path.

### Exercise 8 — separate reproducibility from equivalence

Build twice from the same clean staged source. Compare file hashes, archive member lists, metadata contents, and installed behavior. Explain which differences are harmless and which invalidate the release.

**Progressive hint:** Start with semantic equivalence. Byte-for-byte reproducibility requires controlled timestamps, toolchains, environment variables, and ordering.

### Exercise 9 — test dependency markers across targets

Create a review matrix for the fixture's build, runtime, optional, development, and environment-marked dependencies across Windows, macOS, Linux, Python 3.11, and Python 3.12.

**Progressive hint:** Parse marker intent with packaging metadata; do not infer it from the developer machine where the lesson happens to run.

### Exercise 10 — design a local release gate

Write an offline release checklist that verifies clean source, tests, type/lint checks, sdist-to-wheel build, artifact contents, fresh install, metadata, hashes, and secret scan without publishing anything.

**Progressive hint:** Every gate should produce bounded evidence and fail closed. Keep index credentials, signing services, and publication outside this local lab.

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
