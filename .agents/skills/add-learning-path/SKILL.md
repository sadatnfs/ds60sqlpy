---
name: add-learning-path
description: Add or extend DS60 lessons, learning paths or execution languages with prerequisite-aware teaching, maintained authoring sources and verified classroom integration. Use for curriculum implementation, not ordinary learner tutoring.
---

# Add a learning path

Build a coherent route from the learner's actual starting point to independent,
bounded work. Preserve the user's requested subject and scope. Adding a lesson
need not create a new subject, language profile or service.

## Choose the contract before writing

Read [root guidance](../../../AGENTS.md), the closest subject `AGENTS.md`, the
[content contract](../../../docs/content-authoring.md) and the existing subject's
`authoring/README.md` when present. Inspect the working tree and preserve other
work. Use parallel agents with explicit ownership for independent authoring,
runtime and review tasks.

Use [integration boundaries](references/integration.md) when choosing among
legacy Python/SQL/bridge, a modern module, a language variant, reading practice,
the statistics tutorial or a new backend. Subject and runtime are separate.
Original core-module plans remain in `docs/expansion/plans/`; new additive
subjects normally use `courses/<subject>/track.json` and `lessons.json`.
Do not invent another learner UI or revive retired desktop/portal launchers.

Inspect one beginner, intermediate and advanced unit in a suitable existing
route. Reuse direct prerequisites and successful teaching patterns, not another
language's terminology or arbitrary lesson count. Read the
[scientist roadmap](../../../docs/scientist-roadmap.md) before describing an
existing statistical method, ecosystem or system lesson as missing. Read the
[progression reference](references/progression.md) for a zero-to-independent arc
and language-specific mechanisms, including web development and GPU computing.

## Write a complete teaching unit

Specify starting knowledge, observable outcome, exact environment and the
evidence a learner can produce. Explain vocabulary and syntax before using them.
Include at least two worked cases that change a meaningful condition, expected
observations, plausible mistakes and a concrete next step. Practice progresses
through prediction, guided change, independent work, debugging and transfer.
Keep learner attempts, executable references and explanatory solutions distinct.
An editable worked example is not an answer to every independent exercise.

Reading practice uses derivations, traces and written reasoning without an
invented Run operation. The statistics book is a tutorial with complete worked
answers and no exams, exercise quota or hidden-solution gate. New additive
tutorials use validated track-level `learning_mode: "tutorial"`; omission means
practice. Applied Science, Bayesian Computing and Data and ML Engineering are
examples. Keep complete worked source in `source_path`; empty `solution_paths`
is allowed for tutorials.
An arbitrary `manifest.json` still does not create a supported loader.

Use small deterministic offline fixtures. Label optional downloads, hardware,
services and separately prepared projects. Use explicit LaTeX delimiters and
accurate code-fence languages. Compile lesson TeX before rebuilding readers.
Use professional factual copy with no motivational slogans. Preserve literal source and copy/paste behavior.
Write original, self-contained prose; a tutor cannot compensate for an empty
chapter or repeated generic filler.

## Register only what exists

Follow the exact [module schema](../../../docs/implementation/ADDING_A_MODULE.md).
Preserve stable IDs, prerequisites, variant aliases and saved-state namespaces.
Keep proposals outside authored admission until real guides, artifacts and
solutions exist. Use `verification_id: null` unless a trusted, tested verifier
is actually registered. A zero exit code is not a typed behavioral verifier.

Edit the durable authoring source before its generated output. Run only that
subject's generator, then its check mode where provided. The CUDA route assembles
separate owned fragments; web development generates from chapter data and source
templates. The original plans are loaded by `module_plans.load_core_plans`, not
a design-preview renderer. Shared HTML remains generated through `make generate`.
Rebuild the [accomplishment index](../../../accomplishments/INDEX.md) after
track, lesson, variant, package, model, reference or study registry changes:
`python accomplishments/index.py build --repo .`, then
`python accomplishments/index.py check --repo .`. The generated lookup is
source and evidence metadata. Edit `RUNNING.md` only when a reviewed evidence
tier changes; it is never generated.

Use the existing `/classroom` directory, accessible theme and capability notice.
Keep drafts and results separate for every lesson/variant/language. Navigation
must preserve recoverable edits; viewing history must not run or restore source.

## Add execution deliberately

Inspect the actual profile's filename, prepared packages, argv, input, file and
multi-file boundaries before promising a capstone. Ordinary workers use Linux
containers; Windows uses WSL 2. A larger project or external resource needs its
own bounded, documented contract. Manifests cannot supply arbitrary commands,
compiler flags, endpoints, engine sockets or cluster credentials.

HTML/CSS and browser JavaScript/D3 have a real opaque preview with source-bound
client observations, not server verification. Live preview is opt-in, does not
automatically create receipts, and stops on navigation/reload. PHP CLI is distinct
from the separately owned HTTP/session project. CUDA CPU models and compilation
are distinct from real GPU correctness and profiling. GPU workers are optional,
require an explicitly selected compatible NVIDIA device and remain outside
ordinary default/`--all` preparation. GPU Spark requires actual compatible
operators, plans and metrics; arbitrary UDFs do not become GPU code automatically.

A new ordinary profile must update reviewed runtime code, image/dependency locks,
launcher and image catalog, formatter/linter, source packaging and the ordinary
CI matrix. Optional hardware or cluster profiles need separate real-capability
gates. Read only the applicable details in [integration](references/integration.md).

## Reuse the scientific and offline patterns

Use JAX's dedicated CPU profile for transformations and state-explicit numerical
work; label optional accelerators and multi-host execution separately. R has a
prepared Rscript profile, explicit script plotting, S3/S4/R6/S7 examples and a
separate compatible formatting tool image. Bayesian examples target their pinned
PyMC/ArviZ data-object API. Do not combine incompatible framework environments
merely because their lessons all use Python.

For custom distributed likelihoods, extend the canonical independent
[package](../../../packages/spark-likelihood/README.md) and its explicit registry,
not the old application compatibility imports. Declare row versus complete-unit
factorization, support, parameter/feature order, weights and prediction semantics.
Compare independent mathematical oracles at changed inputs, invalid support and
extreme numerical regimes before distribution. Named callable/source/configuration
identities and Python minor compatibility must survive wheel installation and
executor import. Test a non-editable wheel without classroom or R imports.
Keep low-dimensional driver optimization separate from TorchDistributor/Lightning
training. The optional R/TMB reference requires prepared native artifacts and its
own API/ABI/compiler receipts; it does not make R a package requirement.

The independent [Spark/TMBad package](../../../packages/spark-tmbad/README.md)
provides a separate prepared C++/JVM route with Scala and Python driver APIs.
Its sources were added after the accepted classroom 1.1.0 publisher. Read its
current artifact-bound qualification before integrating lessons; an existing
native gallery or same-host executor test does not establish the later dedicated
Compose topology, controlled worker-loss recovery, AMD64 or cloud deployment.
Both independent package folders need their own copied-project installation,
dependencies, build/Docker tooling, examples and qualification. Keep native and
Torch execution contracts separate. Do not promise arbitrary Torch programs
become distributed without an explicit supported mode.

New simulation/modeling lessons must bind the actual generator, fitted model,
parameterization and prediction target. Compare independent numerical references,
report replication counts and Monte Carlo uncertainty, and preserve leakage-safe
forecast splits. Coefficient-only ridge, exact nonsmooth lasso and selected priors
need their own implemented, tested semantics. Optimizing with priors gives MAP,
not posterior samples; a successful fit alone does not establish posterior
inference. Keep unimplemented study designs outside admitted lesson claims.

Python web lessons use the ordinary `python-web` worker for finite offline
framework/test-client programs. Multi-process HTTP, WebSockets, SSE and durable
job/session behavior belong to the owned web-lab project. A successful in-process
test client is not browser/network or container-resume acceptance. Preserve both
surfaces when adding framework lessons, and keep dependencies in that profile's
native architecture locks rather than the root Python environment.

Additional statistics tutorials use the validated tutorials/index.json contract;
the original outline and chapter identities remain stable. Offline DAX uses
editable drafts and source/model-bound hand-derived references, with Run rejected
in both service and job layers. A new offline subject needs an explicit supported
contract, not a pretend executable profile.

For a new language, update source-suffix admission and readable labels as well as
profile/language admission, renderer, formatter, fixed execution, image catalog
and CI cases. Use the paired data-visualization route for language variants that
share an analytical question. Captured plots need bounded validated data,
accessible descriptions/tables and persistence tests. Never render arbitrary
saved HTML into the classroom origin.

## Verify the result and hand it off

Use the subject's authoring checks and relevant reference programs. Format code
with `./scripts/format-repo`, then run read-only format/lint checks. Preserve
Markdown literals, vendor files, historical receipts and learner state. Run
reviewed prose normalization and shared generation; never edit generated HTML
or weaken a failure to make the gate green.

Test the changed behavior in the real declared execution surface: browser
interaction, compiler diagnostics, invalid inputs, cancellation, bounded output,
source isolation and saved-result readback after container replacement as
applicable. Use explicitly disposable state. Read-only MCP discovery should
expose the same IDs and prerequisites. Follow [validation](../../../docs/validation.md)
for the relevant gates, including grouped parallel pytest for implementation
changes. The classroom admits one active module job across all profiles; use
separate disposable projects for parallel runtime qualification. Keep launcher
profile/service pairs aligned with the image catalog, including the optional GPU
profiles. A pure prose correction does not require unrelated GPU or cluster runs.

Report maintained sources, registered IDs, actual checks and remaining hardware
or platform limits. Separate parsed source, CPU models, compiled artifacts,
executed results, browser observations and hosted CI. Do not turn a historical
receipt into a claim about changed source, or a chapter count into expertise.
Git commits, registry publication and destructive cleanup remain within the
user's separately authorized scope.

A new ordinary runtime changes `docker/classroom-images.tsv` and the grouped
native AMD64/ARM64 publication coverage. Keep service names, local repositories,
catalog suffixes, staging identities and qualification receipts aligned.
Full CI publication requires a push to `main` with `[publish-docker]` in HEAD.
`[build-test-ALIAS]` selects native App/Core plus one complete ordinary CI
group without Hub writes; `[publish-ALIAS]` on `main` publishes that
qualified partial set. A profile alias expands to its entire group; `js`
selects both JavaScript and TypeScript. Use one exact Docker marker in HEAD.
Publication uses repository secrets
`DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN`; ordinary commits do not opt in.
Only add a publication marker with authorization.

Staging uploads precede complete selected qualification; combined version/latest
promotion must wait for every required selected check. A partial release carries
App, Core and one complete group, while `[publish-docker]` requires all ordinary
profiles. The full publication set currently has 26 images, App plus 25 ordinary
workers, and additionally requires the native scientific-project gate after the
ordinary worker jobs. That gate consumes this run's immutable qualified bases,
checks the installed standalone wheel, numerical/Spark/ML/training behavior,
and preserves the optional R-reference, Scala, standalone TMB API and C++ checks.
Its per-architecture builds run sequentially. Complete source-bound receipts are
required for both first promotion and recovery; local passes are not hosted success.
Existing version conflicts require a checked-in patch bump, not an
overwritten tag. Combined tags use app `VERSION` and workers
`VERSION-<suffix>`. New Hub projects resolve App latest to a concrete saved
version; saved resumes never follow it. `--image-tag PROFILE=VERSION|latest|default`
can pin or clear an ordinary image selection, with cross-revision mixes rejected.
Current CI binds one version to each source revision; do not advertise
arbitrary mixed-release stacks. Learner progress stays outside images.

The manual `./classroom publish` route still previews local images and needs
`--push` for an upload. It publishes one actual architecture, with no fabricated
second platform or combined index; learners use `--architecture-tags` for that
layout. See [distribution](../../../docs/dockerhub.md) before changing either
contract. Local passes and staged images do not prove completed publication.

When a new full version follows a partial release, update the checked-in Python
package and editable lock stanza, App OCI label, launcher, Compose image
defaults, Core base, owned service-workshop defaults and current full-install
examples as one source change. Keep independent third-party and project image
versions and saved `.workshop` selections. An immutable partial version tag is
never reused for a different source revision. Run the exact source, starter,
native worker and Hub pull gates before describing the new version as released.
The dispatch-only `verify-published-images.yml` is a read-only historical
recovery path for the accepted partial 1.0.0 image set, not a shortcut for
publishing a new version. It compares the old promotion receipt and allowed
verifier-only source delta, then tests native pulls without changing tags.
The separate `audit-published-release.yml` handles a completed full publication:
it validates the exact promotion attempt, exports the original published tree,
then audits each native ordinary group with canonical pulls, selected setup,
saved profile/version choices and stop/resume. Its current verifier must pass
source CI, and its result stays separate from image/runtime qualification.
Read the actual receipts before claiming all-module coverage. A `ci-*` candidate
is never the final learner image. Derive subject/profile/image mappings from the
loaders and catalog, and retain the original release SHA when later package
checkpoints share its app version. See the
[full-release audit guide](../../../docs/dockerhub.md#audit-every-published-module-without-republishing).

## Reuse the data and scientific execution contracts

Arrow, DataFusion and PyIceberg library lessons use the separately locked
`data-platforms-python` profile. Ballista and distributed services use their
explicit owned project environments; do not merge incompatible versions into
that worker. The Apache/open-data route demonstrates complete tutorial
registration alongside editable command notebooks and real service workshops.
Read its current qualification ledger before copying a supported-runtime claim.
Prepared Atlas/Delta Sharing clients do not establish server acceptance.

Polars and full dbt/ML engineering programs use `data-engineering`. Beginner dbt
SQL-model variants use `dbt-duckdb` and a fixed fixture; configuration, incremental
state and multi-file projects use the complete Python/CLI route. Do not promise
an arbitrary project editor in the browser.

Native Stan uses `stan-cpu` and `main.stan` with tiny transformed-data fixtures,
fixed compilation and two short seeded chains. Separate JSON input belongs to
the complete CmdStanPy project, not an invented second pad. Julia uses `main.jl`,
a read-only prepared project/depot, two threads and a fresh process. Keep real
sampler, optimizer and numerical diagnostics visible. A tiny chain or successful
fit is not a convergence or scientific-validity guarantee.

A persistent local ML service needs an explicit owned Docker lifecycle and
separate state. Follow the existing service fixture's read-only predictor and
CLI-controlled model activation; do not start an unbounded server inside a pad.
Keep synthetic local evidence distinct from cloud or production qualification.
The engineering book's data-product project separates immutable raw acceptance,
publication pointers and recovery decisions. Its inference project separates
model loading, queued execution, SSE transport and durable request readback.
Reuse their bounded contracts only when the new subject needs them, preserve
private `.workshop/` state and require source-bound failure/lifecycle checks.

When extending required project gates, update the exact required-check sets in
`scripts/ci_classroom.py` and publication evidence validation together. Native CI
currently requires data-product/ML-service checks for data engineering,
inference/browser checks for PyTorch, Flight/Rust IPC for data platforms and
Kafka semantics/lifecycle for Java and owned HTTP/streaming/browser/persistence
checks for Python web. A new lesson reusing an existing profile
does not by itself need another persistent service.

Use `publish_table`/`publish_report` or the prepared plotting helpers for results.
PNG, Plotly, table and JSON share two total outputs, 180,000 bytes per payload and
384,000 bytes combined; tables allow 12 columns and 100 rows. Unsafe large JSON
integers must be strings. Declare required outputs in `figure-contracts.json`,
test actual publication and failure behavior, and verify history without replay.
New `.jl`, `.stan`, dbt SQL/Jinja and complete project fixtures require style,
static checks and portable packaging, excluding generated state and credentials.
