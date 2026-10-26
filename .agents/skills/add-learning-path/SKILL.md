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
answers and no exams, exercise quota or hidden-solution gate. A new tutorial
book requires a supported loader, not merely a file named `manifest.json`.

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
