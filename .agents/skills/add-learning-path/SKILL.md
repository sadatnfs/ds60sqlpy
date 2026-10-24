---
name: add-learning-path
description: Add or extend a DS60 subject, language or tutorial sequence with prerequisite-aware lessons, reviewed runtime integration, reproducible authoring and browser delivery. Use for curriculum implementation or expansion, not ordinary tutoring or an unrelated application feature.
---

# Add a learning path

Build a coherent path from the learner's actual starting point to independently
solving a bounded problem. Keep explanations, practice or tutorial mode, runtime
capabilities and saved-work behavior consistent. Preserve the user's requested
scope; a new lesson does not automatically require a new runtime or a whole
beginner-to-advanced subject.

## Choose the existing contract

Read [root guidance](../../../AGENTS.md), the closest subject `AGENTS.md`,
[content authoring](../../../docs/content-authoring.md) and the relevant subject
plan. Inspect the working tree and keep unrelated changes. Use parallel work
for independent content and verification with clear file ownership.

Use [integration boundaries](references/integration.md) when deciding between:

- an existing legacy Python, SQL or bridge lesson;
- a modern module subject, lesson or language variant;
- a reading-only practice lesson;
- the statistics tutorial, or a deliberately implemented new tutorial loader;
- a genuinely new execution backend.

A subject and a language profile are different things. A math topic can reuse
Python; a conceptual lesson may need no runtime. New module subjects normally
use `courses/<subject>/track.json` and `lessons.json`. Do not insert them into
the generated legacy catalog merely to make them visible.

## Design the learning sequence

Use [the progression reference](references/progression.md) for language-specific
mechanisms and a practical zero-to-independent progression. First inspect
existing lessons so the change closes a gap instead of duplicating content.
Write an observable finish condition, direct prerequisites and the evidence a
learner can produce. Keep stable IDs and preserve existing completion records.

For a full subject, cover beginner, intermediate and advanced stages with
meaningful milestones. Plan around skills and projects, not a fixed day count.
For a small addition, place it at the right prerequisite milestone. Do not
publish filler to satisfy a stage or exercise counter.

## Author a complete teaching unit

Find the durable source generator, if one exists, before editing its output.
Each practice unit needs a self-contained guide, learner artifact, separate
reference and explanation, bounded local fixtures, progressive hints and
inspectable expected observations. Explain new terms, syntax anatomy, at least
two worked examples, common errors, tradeoffs and retrieval/transfer. Use the
subject's real exercise contract; keep solutions out of answer-free starters.

Reading practice uses reasoning and a separate explanation, with no invented
execution step. Tutorial mode provides worked theory, code, use cases and
answered discussion directly. The statistics book explicitly has no exams,
problem sets, prediction gate or hidden solutions. A different tutorial book
needs a supported loader before registration.

Author mathematics with explicit LaTeX and tag code fences with the real
language. Literal program syntax remains code. Keep offline default fixtures
small and deterministic. Identify optional downloads, datasets, hardware and
external services without triggering them during normal reading or generation.
Use original prose and public or synthetic examples, with appropriate sources
and licenses. Avoid private organization data and developer machine paths.

## Register and integrate

Follow [the module contract](../../../docs/implementation/ADDING_A_MODULE.md)
for exact schemas. Register authored content only after its real artifacts
exist. Do not invent a scaffold CLI, verifier ID, runtime, command field or
arbitrary endpoint. Inspect current allowlists and reuse a reviewed profile.

Runtime admission targets Linux-container workers. Windows learners use WSL 2
and its Docker integration; retain the thin Windows Docker launchers as host
setup tools. Native Windows backends, ACL implementation and executable builds
are not supported targets or release gates. Use the current Linux core,
contributor, Docker/browser, owned-Kubernetes and portable-ZIP CI contracts.
A Linux container pass does not establish WSL installation or another host's
engine setup; report those boundaries separately.

New subjects join the same `/classroom` directory. Add an accessible distinct
theme and text label, then verify search and prerequisites. Preserve separate
pads and result history for lesson, variant, language and SQL mode. Navigating
must save or retain a recoverable draft; viewing history must not overwrite
source or execute code. Capability notices must reflect actual readiness.

Before promising a CLI or project, inspect supported arguments, standard input,
files, multi-file builds and dependency installation. Use an implemented bounded
channel or clearly label the separate prepared external workflow.

A new backend is a separate implementation: fixed argv, bounded execution and
output, cancellation, cleanup, immutable fixtures, explicit external ownership,
prepared dependencies and actual worker evidence. A lexer, manifest entry,
passing compile or reference output alone cannot establish all these properties.

## Verify and hand off

Run the subject's documented authoring command where applicable, then use the
verified shared commands in [integration boundaries](references/integration.md).
Run `./scripts/format-repo` after the relevant subject generator, then the full
`./scripts/format-repo --check` and `./scripts/lint-repo` before submission.
Inspect `--list` when adding
file types; a new language needs a reviewed formatter adapter and pinned tools,
not an unreported exclusion. Preserve third-party code, learner state, locks
and generated-reader ownership. Embedded teaching snippets keep their authored
layout. Check generation drift, content rendering and module/legacy contracts.
Run meaningful reference and misconception cases. Do not reduce a check to accept
a wrong example or rewrite a historical execution receipt as if it were new.

Exercise the browser path in disposable test state: guide, starter, run or
reading behavior, explicit solution reveal, errors, switching, save/reload and
restoration after container replacement. Test read-only tutor discovery when
identity changes. Run grouped parallel tests for integration without altering
unrelated learner state or publishing images.

Report changed durable sources, registered IDs, commands and actual results,
including skipped or unverified platforms. Keep generated readers aligned and
update contributor/learner documentation where behavior changes. A successful
check is evidence for its tested contract, not a promise of expert competence
or a bug-free product.

## Current reference implementations

Use the C, Go, C#, Rust and Swift subjects for single-source compiled-language
contracts and staged filenames. Use JavaScript js-043 through js-066 for an
offline browser-library specialization with actual D3 interaction and saved
client observations. Use the Docker subject and Kubernetes networking extension
for complete reading/manual paths whose advanced host capabilities remain
explicit. These are examples to inspect, not generators to run over a different
subject. The progression and integration references document their boundaries.

Browser acceptance must cover the live state after representative interactions,
resizing and navigation, not merely an initial success marker. Inspect settled
painted output and handled sandbox errors, retain original observations, and
qualify saved-result readback after actual container replacement without replay.
