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
