# Expansion implementation checkpoint

Last updated: 22 October 2026. Starting commit: `19b2396`.

## Scope and current result

Work happens directly in `~/workspace/ds60sqlpy`. There are no additional
clones, worktrees, agent commits, pushes or published container images. The
human owns Git staging and commits. Read `git status --short` before resuming.

The five-course design contains 204 planned lessons. The first implementation
batch has **29 authored lesson sets**, with guides, learner sources or
worksheets, separate explained solutions, fixtures and track authoring rules:

| Track | Authored IDs | Still planned |
| --- | --- | --- |
| TensorFlow | `tf-001` through `tf-008` | 28 |
| LLM theory in Python | `llm-001` through `llm-009` | 33 |
| C++ | `cpp-001`, `cpp-002`, `cpp-003`, `cpp-009` | 38 |
| Kubernetes | `k8s-001`, `k8s-002`, `k8s-003`, `k8s-008` | 38 |
| Scala and Spark | `spark-001`, `spark-002`, `spark-003`, `spark-013` | 38 |

The PySpark variant of `spark-013` has its own source, solution and saved pad;
it is not an extra lesson in the count. There are **175 planned lesson bodies
remaining**. Some systems pilots therefore have planned prerequisites. They
are clearly marked pilots, not a complete beginner-to-advanced publication.
The existing 168 published Python/SQL/engineering lessons remain available.

## Implemented application

- `/journeys` renders the authored course guides beside editable pads, prediction
  and explanation notes, explicit solution reveal, structured verification,
  compiler diagnostics, bounded logs and attempt history.
- `/journey-preview` retains the complete planned route. Planned lessons have
  no fake execution or completion action.
- Module state is separate from existing progress: `.learning/modules/` holds
  source, notes, sessions and persisted job receipts on the host. Empty source
  is a valid saved draft. Scala and PySpark drafts remain separate.
- Authenticated same-origin `/api/modules` requests have a separate bounded
  body allowance. Legacy API limits stay unchanged. Runtime endpoints and
  operations are fixed by the host preparation and lesson manifest.
- Jobs are asynchronous and idempotent. Reconnection polls an accepted job;
  it does not replay source. Uncertain cleanup holds admission. A proved new
  CPU worker instance can close an unavailable old receipt as failed; external
  Kubernetes cleanup requires explicit owned recovery.
- The optional local launcher selects profiles, builds sequentially with
  foreground logs, checks local engine/disk prerequisites and reuses host
  learner state. Windows has `START_MODULE_LAB.cmd`; base engine setup remains
  in `START_DOCKER_LAB.cmd` with its WSL 2 walkthrough.

## Runtime boundaries and evidence

See [runtime instructions](../modules-runtime.md), [worker status](worker-status.md),
[ML content status](ml-content-status.md), and
[systems content status](systems-content-status.md).

Fixed private workers implement Python/NumPy, C++20, TensorFlow CPU, standalone
Scala, Spark Scala and PySpark. CPU PyTorch has a separate locked image recipe;
its image/runtime has not been qualified in this batch. The current LLM pilot
uses NumPy and does not require PyTorch. Single-file C++ compilation is
implemented; a browser multi-file CMake project workflow is still future work.

Kubernetes uses an explicitly prepared owned kind cluster, scoped expiring
credentials, pinned fixture image and exact namespace identity. The browser
and workers have no Docker socket or ambient kubeconfig. The one-shot operation
accepts only the fixed bounded hello Deployment and optional Service. It
checks real controller/Pod readiness, matching EndpointSlice Pod UIDs, a fresh
in-cluster version client, and UID-precondition cleanup. Stateful rolling
changes, arbitrary commands and the entire six-task pilot are not automatically
graded. Host preparation/release are separate visible operations.

Actual Linux arm64 Docker proofs and image IDs are recorded in ignored
`work/modules-acceptance/*.json`. Positive and misconception cases have passed
for Python, TensorFlow, C++, Scala and both Spark variants. Kubernetes positive
routing and Deployment-only checks passed; a 15-second negative test exposed
an insufficient cleanup reserve. Final independent cleanup-grace and shutdown
fix qualification is in progress. Do not call Kubernetes final until the
final receipt records timeout/cancellation cleanup and graceful worker stop.

This machine's Docker Hub download certificate validation failed. Trusted
cached/GCR inputs were selected with TLS verification retained. Standard
upstream defaults remain portable build inputs; optional base overrides are
supported. No engine trust, VM configuration, unrelated cache or service was
changed. Builds and acceptance are Linux arm64 on this engine, not proof of
Windows, Linux amd64 or native Windows ACL behavior.

## Acceptance resources and stop policy

The user's temporary native preview and personal Docker HTTP app were stopped
at their request. Preserve their `.learning`, personal PostgreSQL volume,
native PostgreSQL 5432 and unrelated containers.

Current test resources belong only to Compose project
`ds60-modules-validation`: browser port 58769, PostgreSQL port 58433 and ignored
host learner folder `work/modules-acceptance/learning`. Private runtime tokens
and Kubernetes receipts are outside `.learning` in a private temporary session.
Never print or package credentials. Read the last non-secret record in
`work/kubernetes-owned-preparation.log` to find the owned session; do not adopt
an ambient cluster or create another session without checking that record.

Stop test HTTP and workers after verification, then explicitly release only
the recorded owned kind session using `scripts/prepare_kubernetes.py release`.
Keep the user's personal HTTP app stopped. Never restart the engine, prune
unrelated resources, delete learner state or stop the user's personal database.

## Resume and next authoring batch

1. Read this checkpoint, owner status files, `git status` and the final receipts.
2. Inspect actual owned test services before starting more. Source/configuration
   alone is not runtime evidence. Check host and engine free disk before builds.
3. Finish any recorded acceptance gap, then run the grouped four-worker suite
   with isolated caches and the disposable PostgreSQL on port 58432. The
   host-only TensorFlow opt-in test is expected to skip when TensorFlow is not
   installed; actual TensorFlow execution must still pass in its worker.
4. Regenerate/check readers and the journey preview after authoring changes.
   Never hand-edit generated HTML or the original published catalog.
5. Fill the missing systems foundations before expanding their intermediate
   stages. Follow `courses/<track>/AGENTS.md`, the per-track `lessons.json`,
   `docs/expansion/architecture.md`, [the module authoring contract](ADDING_A_MODULE.md)
   and publication gates. Each new lesson needs
   a full explanation, vocabulary, worked examples, graded practice, separate
   solutions, meaningful fixtures and appropriate execution checks.
6. Promote a module into the published catalog only after its prerequisite
   chain, runtime and supported platform rows pass their publication gates.
   Do not mark all 204 lessons complete because five pilots execute.

Useful checks: `scripts/check_modules.py`, `scripts/check_module_ui.mjs`,
`build_journey_preview.py --check`, `build_course_guide.py --check`,
`build_lesson_readers.py --check`, Ruff, strict MyPy and `pytest -n 4 --dist
loadgroup`. Build logs use `work/build-*.log`; narrow runtime helpers and
non-secret evidence use `work/modules-acceptance/`.
