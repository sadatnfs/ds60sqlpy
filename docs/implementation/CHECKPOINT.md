# Maintained implementation checkpoint

This file describes the architecture and continuation boundaries of the current
source. It is not a record of a particular developer's machine, test session or
hosted CI run. Use [validation](../validation.md) and the workflow results for
the exact revision being reviewed.

## Delivered application structure

`/classroom` provides one home and workspace for all registered subjects.
`/`, `/learn`, `/journeys` and `/journey-preview` are compatibility aliases for
that shell. The old independent Python/SQL and module pages are retired.
Subject selection, search, themes, lesson navigation, code or reading workspace,
notes and progress belong to this shared interface.

The directory combines the historical Python, PostgreSQL and engineering bridge
catalog with authored module subjects and the statistics/ML tutorial. Identity
and prerequisite metadata are derived from the loaders. Inspect the current
inventory rather than copying a past count:

```sh
python scripts/course.py catalog
python scripts/check_modules.py --json
```

Historical day labels, canonical lesson IDs and language variants remain stable.
The legacy catalog and module manifests are separate authoring contracts that
share one learner experience. See [ADDING_A_MODULE.md](ADDING_A_MODULE.md) before
choosing where an extension belongs.

## Presentation and learning modes

The CUDA subject adds 128 chapters with default reading workspaces, separately
saved CPU-model variants, selected framework/Spark CPU variants and optional
NVIDIA variants. GPU workers are explicitly selected and excluded from ordinary
default/`--all` builds. They require a real allocation/kernel/readback probe.
CPU checks and compiler acceptance never establish device or performance
qualification. See `docs/cuda-classroom.md` for supported preparation and limits.

The web-development subject combines 60 HTML/CSS/PHP lessons. `html-browser`
uses the existing opaque, network-blocked preview and browser observations;
`php-cli` checks syntax then runs `main.php` with a prepared SQLite driver.
The optional HTTP project is separate from the ordinary single-file worker.

Image distribution supports local builds or explicit Docker Hub selection.
Per-project `images.env` stores source, namespace and version; architecture tags
match the engine. Resume never pulls or builds. Publication is an explicit
separate script and optional manual workflow, not a side effect of startup.

The shared renderer provides offline MathML and syntax highlighting. Reviewed
prose normalization runs before reader generation; copying a code block must
preserve source characters. The generated static library remains available
without the application server. Design-preview templates are developer tools,
not a second live classroom.

Practice lessons have progressive exercises, hints and separate solutions.
The statistics book is a theory-and-code tutorial with directly available
worked examples and answered interview discussions. Reading markers and
learner-confirmed completion do not certify understanding.

## Runtime and storage boundaries

The shared `./classroom` launcher resumes existing containers, builds only
missing images, waits for readiness and opens the actual loopback address.
Existing containers are reused. Docker can reassign automatic host ports when
restarting the same PostgreSQL container. If the browser port changes, only the
app is recreated from its existing image to preserve exact Host/Origin checks;
there is no build or pull. PostgreSQL and worker IDs and all volumes are retained.
Fixed browser/database ports preserve the URL and all existing container IDs on
later unchanged resumes. Deliberately changing ports uses `--rebuild`.
The launcher remembers selected profiles and registry mode in
`.classroom/<project>/selection.env` before preparation,
so an interrupted build retains intent. Requested ports are also saved before
preparation; the ready URL is saved only after HTTP acceptance. Older projects
without the selection file infer
recognized profiles from their own worker containers. A new project defaults
to all ordinary CPU and language workers. Explicit `--starter`, `--profile`
and `--all` replace the saved selection; they do not stop unselected running
workers. `resume` and `--no-build` prohibit builds and pulls. `--rebuild` installs
source/configuration updates, and `build` builds without starting. Missing
containers can use existing images and volumes; database recreation repairs
the app's shared network reference and public address. Custom project names
must be supplied explicitly on later commands; there is no global project guess. Windows uses WSL 2 with an
integrated Linux-container engine. Host compilers and databases are unnecessary
for the ordinary classroom route. Linux containers are the supported release
target. Native Windows runtimes, private-ACL integration and executable bundles
are retired from release qualification; retained helpers are compatibility
material. Linux contributor checks and container/browser receipts govern the
current release matrix, as described in [validation](../validation.md).

The app preserves Python/SQL pads, coaching phases and immutable run receipts.
Module lessons preserve source, notes, variants and job history through their
own storage adapter. Viewing a saved result is read-only. Reconnection must not
replay a job whose outcome is unknown, and a receipt-save failure must not hide
a successful execution.

The C17, Go, C#, Rust and Swift workers use fixed single-file compilation and
execution. Rust includes a prepared Arrow dependency; C# includes its fixed
.NET console project. Larger Cargo, Go, .NET and Swift packages are explicitly
separate project workflows. Swift language and Foundation examples run in Linux;
SwiftUI, UIKit, simulators and signing require the documented macOS/Xcode route.

D3 examples use bundled D3 in an opaque-origin browser iframe, with no CDN or
network access. The preview captures initial output and later interaction
errors, supports stopping and fullscreen viewing, and is removed on navigation.
Its observations are saved by `browser_runs.py` separately from worker receipts.
They carry the source hash and `verified: false`; client output is not a trusted
worker verification. Viewing an observation never reruns it or replaces a pad.
The iframe is not a hard CPU sandbox for arbitrary untrusted programs.

Docker and the extended Kubernetes networking units include explicit prepared
lab workflows. The ordinary classroom does not expose the engine socket or
implicitly apply a cluster manifest. The owned Kubernetes adapter admits only
its reviewed operation/verifier set; new networking examples do not expand
that authority merely by appearing in the curriculum.

Named Compose volumes hold learning state and PostgreSQL data. Reuse the same
project name to resume that workspace. Keep volumes when replacing containers
or removing images, and follow the documented backup workflow before moving
machines. Private runtime sessions and credentials are separate from portable
learner exports.

Kubernetes operations require deliberately prepared, owned local resources.
Pretrained models, GPU experiments, external APIs and longer-running services
have separate preparation and capability requirements. A small offline example
demonstrates its mechanism; it does not prove model quality, production capacity
or safety on arbitrary infrastructure.

## Where to make changes

| Change | Maintained source |
| --- | --- |
| Classroom behavior and styles | `src/ds60sqlpy/assets/classroom.*`, `classroom.py`, `lab.py` |
| Module content and admission | `courses/<subject>/`, `modules.py`, `module_extensions.py` |
| Worker execution | `module_jobs.py`, `worker_operations.py`, reviewed adapters, `docker/workers/` |
| Legacy identity and planner | `catalog_builder.py`, `curriculum/extensions/`, `catalog.py`, `study_plan.py` |
| Rendering | `lesson_reader.py`, `reader_math.py`, `reader_content.py` |
| Local build/start | `classroom`, `scripts/classroom.sh`, `compose.classroom.yaml` |
| Tutoring integration | `mcp_server.py`, repository learning skill |
| Future authoring | [Add a learning path skill](../../.agents/skills/add-learning-path/SKILL.md), [content contract](../content-authoring.md) |

Python filenames without a full path are under `src/ds60sqlpy/`.

## Continue and qualify a change

1. Read root and subject guidance; inspect current changes and the selected
   source generator before editing its output.
2. Implement one coherent change, preserving IDs, saved-work namespaces and
   the distinction between content registration and runtime capability.
3. Run focused behavioral checks, relevant reference programs and generated
   document checks. Review a changed learner flow in the browser.
4. Run the grouped parallel suite and applicable CI gates. Keep structural
   checks, live runtime receipts and target-platform results distinct.
5. Record actual commands, revision and environment in release or CI artifacts.
   Do not copy a historical success count into a claim about a new revision.
6. Clean only the resources created for the check and retain learning volumes.

No file here implies that a background process, acceptance project or automation
is running. Discover current runtime state through `./classroom status` and the
container engine before acting on it. No claim of Windows, Linux, architecture
or optional-runtime acceptance follows merely from a Dockerfile or workflow.
