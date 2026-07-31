# Package engineering solution reasoning

This is the reasoning companion for `python-pro-01`. Attempt the learner file
before reading it; the executable reference is
[`py_pro_01_package_engineering_solution.py`](py_pro_01_package_engineering_solution.py).

## Why the solution is structured this way

`summarize_project` reads TOML with `tomllib`, so inspecting metadata needs no
third-party parser. It validates table shapes before indexing them; a malformed
file therefore produces a useful packaging error rather than a mysterious
`TypeError`.

`build_distributions` checks the frontend and backend tools before starting.
It copies the fixture into a caller-owned disposable staging directory because
setuptools may write egg metadata beside its input source even when the final
artifacts use a separate output path. `--no-isolation` is essential to the
offline contract: the build frontend must use already-installed requirements.
Together, staging and the explicit output path keep `dist/`, `build/`, and egg
metadata out of the repository.

`install_wheel_and_prove` addresses a different boundary:

- `--no-index` forbids consulting a package index.
- `--no-deps` prevents dependency resolution.
- `--target` keeps installation out of the course environment.
- `--no-compile` plus `PYTHONDONTWRITEBYTECODE=1` avoids cache files.

The proof runs in a child interpreter whose working directory is outside the
source fixture and whose `PYTHONPATH` contains only the fresh target. Checking
`package.__file__` beneath that target turns “the import worked” into evidence
that the wheel supplied it.

## Exercise decisions

### Artifact classification

The solution checks `.whl` and the complete `.tar.gz` ending. A substring check
would incorrectly accept `backup.whl.txt`; a single `Path.suffix` check sees
only `.gz` for an sdist.

### Tables and dependency boundaries

Build requirements make the backend runnable. Runtime dependencies are exposed
to every installer. Optional dependencies add user-selected features.
Dependency groups support development workflows without becoming installed
package metadata. An environment marker is evaluated for a particular target
environment; it is not an instruction to import the package unconditionally.

### Console scripts

`[project.scripts]` records `ds60-greet =
"ds60_tiny_greeter.cli:main"`. Installers create platform-appropriate launchers
from that metadata. Inspecting the installed entry-point metadata is portable;
hard-coding `bin/ds60-greet` would fail on Windows, where launcher layout and
suffixes differ.

## Alternatives

- A project may use Hatchling, Flit, PDM, Poetry, or another standards-based
  backend. The frontend workflow remains similar, but its preinstalled backend
  requirements change.
- An editable install is convenient while developing. It deliberately points
  at source and therefore cannot replace a wheel-install proof.
- A virtual environment is a stronger end-user simulation than `--target`.
  The target approach is much faster and still proves import and metadata
  location without modifying the repository environment.

## Edge cases

- Native extensions create platform-specific wheels and need compilers or
  prebuilt artifacts. This pure-Python fixture intentionally isolates packaging
  concepts from compiler setup.
- An sdist can omit required files even when a wheel succeeds. Real projects
  should build a wheel *from the sdist* in release automation.
- Markers can depend on Python version, platform, implementation, or extras.
  Test the target combinations you actually support.
- A successful local build does not prove a public release is safe. Publishing,
  signing, provenance, and index credentials remain intentionally out of scope.

## Expected result

With local build tools installed, the solution reports one wheel, one sdist, an
import path under a temporary `site` directory, version `0.1.0`, console script
`ds60-greet`, and `Hello, wheel!`. Without those optional tools, it identifies
the missing bootstrap dependency without attempting a download.

---

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Reasoning before implementation

The reference workflow separates source, build, artifact inspection, installation, and runtime proof so each failure has a clear owner.

1. **`[build-system]`:** declares the backend and bootstrap requirements that turn source into a distribution artifact.
2. **`[project]` metadata:** defines distribution identity, version, Python range, dependencies, and entry points.
3. **`python -m build` then clean install:** proves the built wheel, not repository-path import behavior.
4. **Prove the failure boundary:** Exercise one normal case, one boundary case, and one injected failure without relying on hidden state.

**Alternative:** A single-module project or application bundle may not need a published library, but it still benefits from explicit dependency and artifact identity.

**Trade-off:** Dynamic versioning and broad build automation reduce repetition while making source-of-truth and reproducibility harder to inspect.

**Failure boundary:** Missing package data, stale editable installs, namespace packages, platform wheels, incorrect Python ranges, and undeclared imports can pass source tests but fail consumers.

**Verification:** Build twice, inspect wheel metadata/content, install in a clean environment from outside the repo, run entry points/tests, and compare artifact hashes.

### Verification micro-example

Run this small, deterministic case before adapting the reference to a
larger system. It gives the reasoning above an executable anchor:

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

The reference implementation is one defensible contract, not a license
to copy internal steps into every system. Preserve the observable
guarantees and repeat the failure tests when adapting it.

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_pro_01_package_engineering_solution.py`](py_pro_01_package_engineering_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — classify artifacts

**Prompt recap:** Implement `classify_artifact`. Use complete final suffixes and reject `package.whl.txt`. Add checks for one wheel, one sdist, and one unsupported file.

**Reference reasoning:** Packaging evidence must come from standards metadata and a fresh installed artifact, never from an import that can fall back to the source tree. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `classify artifacts`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 2 — create an offline build command

**Prompt recap:** Implement `offline_build_command` as an argument list. Use the running interpreter, invoke the `build` module, request both formats, disable isolation, and choose an explicit output directory. Why an argument list? It avoids a second round of shell parsing and behaves the same way in PowerShell, Command Prompt, Bash, and zsh.

**Reference reasoning:** Packaging evidence must come from standards metadata and a fresh installed artifact, never from an import that can fall back to the source tree. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `create an offline build command`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 3 — inspect dependency intent

**Prompt recap:** For each fixture entry, decide whether it is: 1. a runtime dependency, 2. an optional installed feature, 3. a development-only dependency group, or 4. a build bootstrap requirement. Explain when `colorama`'s environment marker is true. Confirm that building metadata does not install the `test` or `quality` groups.

**Reference reasoning:** Packaging evidence must come from standards metadata and a fresh installed artifact, never from an import that can fall back to the source tree. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `inspect dependency intent`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior.







### Exercise 4 — build in a disposable directory

**Prompt recap:** Use disposable staging and output directories because a backend may write metadata beside its source. Invoke the running interpreter with `-m build --no-isolation --sdist --wheel --outdir <temporary-dir> <fixture>`. If a backend requirement is missing, return to connected setup instead of weakening the offline policy.

**Reference reasoning:** Packaging evidence must come from standards metadata and a fresh installed artifact, never from an import that can fall back to the source tree. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `build in a disposable directory`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 5 — prove the installed origin

**Prompt recap:** Install the wheel into a fresh target using `pip install --no-index --no-deps --target <directory> <wheel>`. Start Python outside the fixture source tree, expose only the target, and inspect the module origin, distribution version, console entry points, and greeting behavior. `installed_origin_is_safe` must accept only a resolved path beneath that fresh target.

**Reference reasoning:** Packaging evidence must come from standards metadata and a fresh installed artifact, never from an import that can fall back to the source tree. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `prove the installed origin`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 6 — build a wheel from the source distribution

**Prompt recap:** Build the fixture sdist in disposable storage, unpack it, build a wheel from that unpacked sdist with `--no-isolation`, and compare the result with the direct wheel build. Record every required local tool.

**Reasoning path:** A direct wheel and an sdist exercise different inclusion paths. Use temporary directories and inspect archive members before rebuilding.

The sdist is the published source contract. Build it from a copied staging
tree, inspect that `pyproject.toml`, README, package sources, and required
metadata are present, then invoke the same local build frontend on the unpacked
archive. Install the resulting wheel into a fresh target and rerun the origin,
version, entry-point, and behavior proof.

Compare normalized wheel member names and installed behavior rather than
requiring byte-identical archives: ZIP timestamps and tool versions can vary.
If the sdist-built wheel fails, the release is incomplete even when a direct
wheel succeeded.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `build a wheel from the source distribution`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 7 — inspect installed metadata without importing

**Prompt recap:** Use `importlib.metadata` against the fresh target to inspect name, version, requirements, extras, and console scripts before importing the package. Reject unexpected or missing metadata.

**Reasoning path:** Distribution metadata and import packages are related but distinct. Place only the target on the child process search path.

Query the installed distribution by its normalized project name and assert the
declared version and console-script target. Evaluate marker text as metadata;
do not import optional dependencies merely to inspect it. Then perform the
separate module-origin and behavior proof.

This catches a wheel that contains importable code but incorrect release
metadata. It also avoids using `package.__version__` as the only authority when
the project intentionally derives version from distribution metadata.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `inspect installed metadata without importing`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 8 — separate reproducibility from equivalence

**Prompt recap:** Build twice from the same clean staged source. Compare file hashes, archive member lists, metadata contents, and installed behavior. Explain which differences are harmless and which invalidate the release.

**Reasoning path:** Start with semantic equivalence. Byte-for-byte reproducibility requires controlled timestamps, toolchains, environment variables, and ordering.

Record build frontend/backend versions, Python version, source hash, archive
members, and artifact SHA-256. If hashes differ, unpack both artifacts and
compare normalized file content and metadata. A changed source file,
dependency declaration, entry point, or installed behavior is substantive;
timestamp-only ZIP metadata may not be.

Do not claim reproducible builds until identical bytes are demonstrated under
a documented controlled procedure. Semantic equivalence is useful evidence
but a narrower claim.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `separate reproducibility from equivalence`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 9 — test dependency markers across targets

**Prompt recap:** Create a review matrix for the fixture's build, runtime, optional, development, and environment-marked dependencies across Windows, macOS, Linux, Python 3.11, and Python 3.12.

**Reasoning path:** Parse marker intent with packaging metadata; do not infer it from the developer machine where the lesson happens to run.

For each target, state whether the marker selects the dependency and which
workflow installs it. Build requirements bootstrap the backend, runtime
requirements follow normal installation, extras require explicit selection,
and dependency groups remain development tooling.

The matrix is a test plan, not proof of every target. CI or local target
environments must actually build, install, and exercise the declared supported
combinations. Avoid unconditional imports of platform-selected packages.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `test dependency markers across targets`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 10 — design a local release gate

**Prompt recap:** Write an offline release checklist that verifies clean source, tests, type/lint checks, sdist-to-wheel build, artifact contents, fresh install, metadata, hashes, and secret scan without publishing anything.

**Reasoning path:** Every gate should produce bounded evidence and fail closed. Keep index credentials, signing services, and publication outside this local lab.

Order the gate so cheap correctness checks run before builds. Use disposable
directories, `--no-isolation`, `--no-index`, and `--no-deps`; capture tool
versions and artifact hashes in a manifest. The final child-process smoke test
must execute outside the source tree.

Signing, attestations, and index upload are separate authorized workflows.
Document them as future controls without inventing credentials or claiming the
unsigned local fixture has supply-chain provenance.

**Common trap:** A successful local command can still use cached files, online build isolation, or the working tree; prove paths, inputs, and offline flags explicitly.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `design a local release gate`, produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.
