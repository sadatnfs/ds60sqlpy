# Add or extend a learning module

Read the [checkpoint](CHECKPOINT.md) and
[expansion architecture](../expansion/architecture.md) first. Reuse one existing
runtime when it fits. A new subject, a new lesson and a new execution backend
are separate changes, with separate acceptance evidence.

## Add a lesson to an existing subject

1. Read `courses/<track>/AGENTS.md`. Add the complete prerequisite-aware plan
   entry under `docs/expansion/plans/`, retaining a stable lesson ID.
2. Author a substantial guide, learner source or worksheet, separate executable
   solution and explanation, and deterministic small fixtures. Define vocabulary,
   explain the mechanism, show worked examples, and progress from observation
   to repair and transfer. Do not use an empty heading or a task list as a lesson.
3. Register only completed content in `courses/<track>/lessons.json`. Copy an
   existing record's schema: ID, authored status, language, fixed runtime profile,
   guide/source/solution paths and optional registered verification ID. Keep
   paths inside that course and exclude credentials, downloads and shell text.
4. Use `reading` plus `markdown` for a theory worksheet that needs no execution.
   Use a curated language variant only when the same learning objective has a
   separately authored implementation. `spark-013@pyspark` demonstrates separate
   saved pads while retaining one canonical lesson count.
5. Add meaningful correctness and misconception tests. Run `check_modules.py`,
   the teaching depth/practice checks used by the subject, its reference code,
   the affected verifier and the actual prepared worker. Printed success text
   is not a verifier. Execution success does not certify learner understanding.
6. Regenerate the preview and HTML readers, then test the real browser guide,
   source, explicit solution reveal, save/reload and result rendering. Planned
   prerequisites must remain visibly planned until their complete content exists.

The module manifest cannot contain a run command, endpoint, compiler flag or
arbitrary file path. `ModuleCatalog` validates curated file ownership, suffixes,
source limits and profile/language compatibility. Reads revalidate paths.
`ModuleState` preserves drafts in the host learning directory and never rewrites
the original progress file or the learner source in `courses/`.

## Add a subject or execution backend

Subject admission currently uses explicit registries. Do not assume adding a
JSON file enables arbitrary languages. Update and test these deliberate gates:

| Layer | Implementation |
| --- | --- |
| Planned route and prerequisite graph | `journey_design.py`: `TRACK_IDS`, profiles and plan validation |
| Authored file admission | `modules.py`: languages, profile pairs, verifiers and manifests |
| App-to-worker routing | `module_jobs.py`: fixed `SERVICES` and endpoint validation |
| Worker operation | `worker_operations.py`: fixed `PROFILES`, argv, preparation and typed verifier |
| External resource ownership | A dedicated adapter, as in `kubernetes_module.py` |
| Image and resource budget | `docker/workers/`, an explicit Compose profile and private network |
| Host preparation | Both module launchers, local engine checks and private session handling |
| Reader and tutor delivery | `lesson_reader.py`, module UI and read-only MCP module tools |
| Portable payload | `desktop.py` allowlist and starter archive validation |

A backend needs an actual bounded readiness smoke, process isolation, compile
failure behavior, shared work deadline, cancellation, descendant cleanup,
output/file limits and unknown-outcome recovery. External resources additionally
need explicit scope, namespace/cluster identity, ownership receipts, UID-aware
cleanup and fresh bounded cleanup time. No browser or learner worker receives
an engine socket, ambient kubeconfig, arbitrary host command or cloud credential.

Prepare dependencies explicitly, pin the relevant toolchain and platform locks,
and keep small default fixtures offline. Document which additional tasks need
network access, GPUs, larger data or optional downloads. Never start those tasks
as a side effect of opening a lesson. Keep container image publication separate
from local build and test.

## Publication and honest status

A lesson can be authored while a profile is unavailable. A working arm64 Docker
image does not establish Linux amd64 or Windows host acceptance. Record exact
image IDs, architecture, reference results, rejected misconceptions, timeout,
cancellation, saved-work recovery and the platform actually tested.

Keep beta modules separate from the 168-lesson published catalog until their
prerequisite chains and publication gates pass. Update the checkpoint and owner
status after each coherent batch. Future agents should resume from those files
and actual receipts, rather than infer completion from the number of plan entries.

Run the grouped four-worker suite after integration. Add platform-specific CI
or execution rows deliberately; leave untested rows unqualified. Preserve the
historical baseline, ignored learner work and unrelated services throughout.
