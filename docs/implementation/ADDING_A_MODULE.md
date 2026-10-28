# Add or extend a learning module

New subjects belong in the existing `/classroom` home and workspace. Content,
runtime execution and presentation have separate contracts. Reuse a prepared
runtime when it fits and preserve stable IDs and progress. Read the
[content contract](../content-authoring.md),
[extension playbook](../curriculum-extension-playbook.md) and closest subject
`AGENTS.md` before editing. The
[authoring skill](../../.agents/skills/add-learning-path/SKILL.md) provides the
repeatable contributor workflow.

## Route metadata and authored admission

For a new subject, `courses/<subject>/track.json` uses schema version 1, an ID
matching its directory, a title, a summary and `lessons`. Optional track-level
`learning_mode` accepts only `practice` or `tutorial`; omission means `practice`.
It applies to that route and its variants. Each lesson row has:

| Field | Meaning |
| --- | --- |
| `id` | Unique stable ID ending in a three-digit suffix, such as `java-001` |
| `title`, `level`, `minutes` | Learner title, `beginner`/`intermediate`/`advanced`, bounded estimate |
| `prerequisites` | Existing stable lesson IDs, with no duplicates or graph cycles |
| `runtime` | A registered profile name, including `reading` when appropriate |
| `concepts` | Searchable, nonempty concept labels |
| `outcome`, `lab`, `verification` | Observable learning goal, concrete task and expected evidence |

The additive loader requires a route to cover all three stages. A partial
proposal belongs in design documentation until its complete route is ready;
do not pad the plan with meaningless entries to satisfy validation. Plan rows
can describe not-yet-authored work, but only complete authored bundles may enter
`lessons.json`. Learners must be able to distinguish planned from authored work.

For the original Kubernetes, TensorFlow, LLM theory, C++ and Scala/Spark
subjects, edit their existing `docs/expansion/plans/` metadata instead of adding
a second plan. `module_plans.load_core_plans` validates these five core plans before the module
catalog validates their complete prerequisite graph. They are maintained route
inputs, not a design-preview application. Java is a
useful additive example; inspect `courses/java/track.json` and `lessons.json`.

`courses/<subject>/lessons.json` has `schema_version`, `track_id` and `lessons`.
Each admitted practice record has exactly these fields:

```json
{
  "id": "java-001",
  "status": "authored",
  "language": "java",
  "runtime_profile": "java21",
  "guide_path": "courses/java/guides/java-001.md",
  "source_path": "courses/java/lessons/java-001.java",
  "solution_paths": [
    "courses/java/solutions/java-001_solution.java",
    "courses/java/solutions/java-001_solutions.md"
  ],
  "verification_id": null
}
```

This is an existing schema example, not a command to overwrite Java content.
Use actual relative paths with exact case. `ModuleCatalog` validates ownership,
suffixes, size limits and registered language/profile pairs, and revalidates
paths on reads. There are no command, endpoint or compiler-flag fields.

A registered verifier is optional. Keep `verification_id: null` unless the
trusted verifier exists and is meaningfully tested. Exit code zero or printed
success text must not be presented as a behavioral verifier.

## Content and variants

Keep guides, learner source, executable references, explanations and small
fixtures separate. Follow the subject's authoring sources when they exist.
Define vocabulary, explain mechanisms and syntax, show worked examples,
progress through distinct practice, and state expected behavior and failures.
Six exercises are the ordinary module floor; quantity is not a substitute for
teaching quality. Do not use empty headings or repeated task wording.

A reading-only practice lesson uses `language: markdown` and
`runtime_profile: reading`, plus a separate explanatory solution. It has no
invented Run action. For an implementation of the same objective in another
language, use the exact `variants` schema in `modules.py`. The curated
`spark-013@pyspark` pattern has separate saved source and jobs while retaining
one canonical lesson count. A different learning objective needs a new lesson.

The statistics tutorial uses its dedicated `manifest.json` contract, exposed
by `module_extensions.py`. Its chapter/example pairs are directly available,
without exams, problem sets, verifiers or solution gates. Preserve its source
outline and coverage identities. New tutorial subjects use the normal additive
`track.json` plus `lessons.json` contract with `learning_mode: "tutorial"` on
the track, as in Applied Science and Bayesian Computing. They keep complete
worked source in `source_path`; `solution_paths` may be empty or expose extra
worked examples, without a hidden-answer gate. Tutorial mode does not bypass
path, language, runtime, prerequisite or artifact validation. An arbitrary
`manifest.json` still does not register a new loader.

## Existing execution contracts

Read `LANGUAGES` in `modules.py`, `SERVICES` in `module_jobs.py` and `PROFILES`
in `worker_operations.py` before choosing a profile. Examples include:

| Profile | Artifact contract |
| --- | --- |
| `python-core`, `tensorflow-cpu`, `llm-torch-cpu` | Python source with the profile's prepared packages and small CPU fixtures |
| `data-engineering` | `main.py` with prepared Polars/Arrow/DuckDB, real dbt and ML engineering packages |
| `dbt-duckdb` | `model.sql`, one SQL/Jinja model in the fixed local dbt project; full configuration uses a separate project |
| `stan-cpu` | `main.stan`, self-contained transformed-data fixture; fixed native compile and two short sampling chains |
| `julia` | `main.jl`, Julia 1.13.3 and its read-only prepared project/depot, two threads and a fresh process |
| `cpp20` | `main.cpp`, C++20, bounded compile and execution |
| `c17` | `main.c`, C17 with prepared compiler and standard library |
| `go` | `main.go`, prepared standard-library import configuration, bounded compile/link/run |
| `csharp-dotnet` | `Program.cs`, immutable trusted .NET project and offline restore configuration |
| `rust-stable` | `main.rs`, Rust 2024 edition with prepared Arrow dependency; no ad hoc Cargo downloads |
| `swift-linux` | `main.swift`, Swift 6 Linux/Foundation compilation; Apple SDKs require a separate macOS project |
| `javascript-browser` | `main.js`, opaque browser preview with bundled D3 7.9.0 and inline local data |
| `html-browser` | One complete HTML document with embedded CSS and bounded inline JavaScript in the isolated offline preview |
| `php-cli` | `main.php`, PHP syntax check then execution with prepared PDO SQLite; no HTTP server or Composer channel |
| `cuda-cpp` | `main.cu`, reviewed CUDA C++20 compilation and device execution; optional NVIDIA profile |
| `cuda-python` | Python with prepared CuPy; optional NVIDIA profile with real device probing |
| `pytorch-cuda`, `tensorflow-cuda` | Python with the named prepared framework, explicit GPU allocation and no silent CPU readiness fallback |
| `java21` | `Main.java`, public `Main` class, no package declaration, Java 21 assertions |
| `javascript-node` | `main.mjs` in Node; browser DOM APIs are unavailable |
| `typescript-node` | `main.mts`, strict NodeNext checking and compilation before Node execution |
| `scala-jvm` | `Main.scala`, `object Main` entrypoint |
| `spark-local-scala`, `spark-local-python` | Bounded local Spark with deterministic fixtures and explicit session cleanup |
| `k8s-kind` | Reviewed operations on an explicitly owned disposable cluster target |

Language support is specific to the profile. Inspect the actual arguments,
standard-input, file and multi-file channels before promising an interactive
CLI or project build. Existing pads submit source to fixed runtime operations;
package managers, custom argv and project archives are not implied. Provide a
bounded supported path or clearly label a separately prepared external workflow.

Do not assume external libraries, multi-file builds, package installs, a GPU
or ambient credentials. Browser DOM
examples need the documented browser route or reading mode, not a fake Node
execution claim. Runtime readiness and actual lesson execution are separate
checks.

## Add a backend deliberately

A new execution language or external operation must update and test these
boundaries as applicable:

| Layer | Source |
| --- | --- |
| Profile/language, source suffix and verifier admission | `modules.py` (`LANGUAGES`, `SOURCE_SUFFIXES`), `module_extensions.py` |
| App routing and durable jobs | `module_jobs.py`, `module_service.py` |
| Fixed argv, preparation and typed checks | `worker_operations.py`, `gpu_runtime.py` and reviewed adapters |
| External resource ownership | A dedicated adapter such as `kubernetes_module.py` |
| Image, packages and resource budget | `docker/workers/`, locks and Compose profiles |
| Shared launch defaults | `scripts/classroom.sh` profile/service map and launcher tests |
| Image selection and distribution | `scripts/classroom_images.sh`, `docker/classroom-images.tsv`, publisher tests and AMD64/ARM64 publication groups for marked main commits |
| Formatting and static checks | `scripts/format_repo.py`, `scripts/lint_repo.py`, `docker/formatting/` and their tests |
| Portable packaging | `course_paths.py`, `scripts/course_payload.py`, `scripts/build_starter.py` and packaging tests |

Python filenames are under `src/ds60sqlpy/`. A new subject that reuses an
existing profile does not need a new image or launcher service.

Use non-shell argument arrays, controlled working directories, bounded work
and cleanup deadlines, output/file limits, cancellation and descendant cleanup.
Test compiler errors, invalid inputs, timeout, interrupted or unknown job
outcomes and saved-work preservation. No browser or ordinary learner worker
receives an engine socket, host kubeconfig or arbitrary host command.

Optional external resources need exact identity and ownership, no ambient
selection, and cleanup after failure. Prepare dependencies explicitly and
separate offline fixtures from optional network, hardware or model assets.
Never fetch dependencies merely by opening a lesson.

## Integrate and qualify the learner experience

`classroom.py` derives subjects, lessons and guide links from the loaders.
`classroom.js` supplies their common interface. Add a distinct accessible theme
keyed by subject ID, a visible label and both light/dark checks. Save or retain
recoverable drafts before switching contexts. Viewing an earlier result must
not execute code or replace current source.

Use explicit LaTeX and tagged code fences. Run the subject authoring generator
when relevant, then `python scripts/normalize_lesson_prose.py --write`,
`python scripts/compile_lesson_tex.py`, shared generation and the publication rendering gate. Do not hand-edit HTML or change
reference code to resolve a display defect.

Run `python scripts/check_modules.py`, relevant subject tests, actual reference
programs and typed verifiers in the prepared runtime. Review browser guide,
source, reveal, error output, variant switching and save/reload behavior.
Registration changes also need read-only MCP discovery and prerequisite checks.
Run the grouped suite with `python -m pytest -n 4 --dist loadgroup` after
integration. See [validation](../validation.md) for all release gates.

Browser-only profiles require a real browser path instead of an ordinary worker
claim. HTML documents preserve native parsing, classic lexical scope and lifecycle
behavior. Preview text in a guide must stay escaped, not executed. Live mode is
an explicit page-session opt-in: it debounces edits, preserves editor focus,
cancels on navigation, and never automatically writes immutable observations.
Manual Run and Save observation have separately tested source identities. The D3 precedent uses `javascript-browser`, a sandboxed opaque-origin
iframe, bundled library, source-bound client observations and dedicated UI
qualification. Such records remain explicitly unverified and have no worker
return code or typed checks. Preserve drafts and history without automatic
replay. A Docker/cluster reading lesson must never gain engine or ambient
cluster access merely to make its Run button available.

When introducing a new ordinary runtime profile, add a small deterministic
cataloged reference to `CASES` in `scripts/check_classroom_profiles.py` and to
the container workflow's grouped profile matrix. The check requires actual
source-bound reference execution, declared typed checks and readback after
container replacement without rerunning. Generic references validate their
assertions and expected output; specialized typed checks are an additional
contract only where registered. A subject reusing an existing runtime needs its
lesson tests, not another runtime image. The supported implementation and
release target is Linux containers, with Windows using WSL 2. Do not add native
Windows runtime, private-ACL or executable-build gates for a new subject.

Optional GPU profiles are deliberately outside ordinary defaults and `--all`.
Use explicit device selection, version/capability checks and real allocation,
kernel and readback probes. Keep reading and CPU-model alternatives available
without calling them CUDA execution. Compile-only acceptance, device correctness,
profiling and multi-GPU operation require different evidence. GPU Spark is an
owned external workflow with compatible plugin/Spark/Scala/JDK/CUDA versions;
supported SQL/DataFrame operators are not arbitrary accelerated UDFs.

Record what ran, on which revision and platform, and what remains unverified.
A configured profile, container build or one architecture's success is not
acceptance on every operating system. Preserve learning volumes and unrelated
workloads when removing test resources.

## Structured scientific results and authoring tools

Use `publish_table` and `publish_report` from `ds60sqlpy.plot_artifacts` for
bounded data results alongside captured PNG/Plotly charts. All kinds share the
two-output budget, with 180,000 bytes per output and 384,000 bytes combined.
Tables allow 12 columns and 100 rows. Finite JSON values and exact integer
representation are required; large identifiers belong in strings. A result
publication warning must preserve the actual computation status. Read saved
results without replay and keep their source identity visible.

Declare required reference outputs in the subject's `figure-contracts.json`.
The corpus checker validates kind/count, descriptions and accessible tables
through `scripts/declared_outputs.py`; a successful exit with missing declared
outputs fails qualification. This contract describes expected output, not
permission to execute code. See [plotting and reports](../plotting.md).

Stan formatting/static checks use the pinned stanc adapter; Julia uses
JuliaFormatter and parse checks in its prepared tool image. dbt `.sql` uses the
SQLfmt adapter rather than the PostgreSQL formatter because Jinja is part of
the language. Preserve each generator's source-to-guide contract, then regenerate
shared TeX/readers after source formatting. None of these syntax checks replaces
real compilation, dbt execution, numerical assertions or browser readback.
