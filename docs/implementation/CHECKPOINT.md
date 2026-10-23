# Implementation checkpoint

Updated 23 October 2026. Human-managed HEAD: `6299005`. All implementation is in
the main checkout. Human Git staging, commits and pushes remain untouched.
No image was published. Preserve unrelated containers and every learner volume.

## Current phase

Unified-classroom implementation is in progress. The user requested one
entrypoint for Python, SQL, bridge and all eleven module/book subjects, distinct
subject themes, properly typeset math, syntax-highlighted code, and updated
navigation/documentation. Root owns backend integration, routing, launchers,
validation and packaging. Parallel owners: rich_rendering owns the shared
renderer/dependencies; unified_ui owns classroom HTML/CSS/JS and UI tests;
math_content_docs owns authored math conversion and user-facing documentation.

Canonical URL: /classroom. The former /learn and /journeys URLs will serve the
same shell as compatibility aliases. Existing legacy pads, coaching phases,
module sessions and job histories retain their storage and stable IDs. The
combined subject index is derived from both catalogs, never hand-counted.
Native MathML and server syntax highlighting must work offline and preserve
code bytes. Math authoring conversion is separate from executable code changes.

This phase is not complete. Final acceptance must cover all fourteen subjects,
legacy Python/SQL save and execution modes, module jobs/variants, explicit
solutions, math/code rendering, mobile/keyboard/themes, persistence, strict
Host/Origin/token checks, full parallel tests, Docker delivery and a new clean
archive. Earlier acceptance numbers below describe the prior distribution.

The user requests comprehensive teaching rather than larger counts alone.
The statistics book is a learning tutorial with theory, worked examples and
answered interviews, with no exams, problem sets or solution gate. Read markers
are manual reading records and never proof of mastery. User instructions:
parallel agents where useful, no em dashes, main checkout only, local images.

## Authored inventory

| Subject | Lessons or chapters |
| --- | ---: |
| cpp | 42 |
| deep-learning-pytorch | 36 |
| deep-learning-tensorflow | 36 |
| java | 36 |
| javascript-typescript | 42 |
| kubernetes | 42 |
| llm-applied | 24 |
| llm-theory | 48 |
| nlp | 24 |
| scala-spark | 42 |
| statistics-ml | 40 |

There are 412 canonical module/book lessons, plus 30 separately saved PySpark
variants. The legacy Python/SQL/bridge catalog contains 186 lessons, including
12 new Python and 6 new SQL deepening lessons. All 186 pass practice and depth
structural audits. The statistics source map preserves all 1,005 labels in the
user-supplied 40-section outline and its source hash.

## Ownership at this checkpoint

All authoring agents are frozen. Root owns final integration and cleanup.
TensorFlow 36, PyTorch 36, theory 48 and applied 24 have completed substantive
mechanism review. The final attention guards 043/046 and applied fixes 010/015/022
have matching Docker receipts, including each changed worked sequence.
The independent starter verifier checks archive integrity, complete content,
exact source parity and exclusion of private/runtime files.
The actual read-only stdio MCP smoke passed all 11 subjects and 412 canonical
lessons with no write, network, execution or official-solution access.

Consult the checked-in authoring sources before future edits. Further executable
changes require new source-matching receipts. Never replace a failed example
with its expected output or weaken a contract to hide a defect.

## Platform and learner experience

The `/journeys` UI serves guides, editable pads, notes, compiler output, source
line diagnostics, job history, per-track resume, stage/topic filters and section
navigation. The book uses a wide reading view, method search, section picker and
explicit read marker. All stages and empty-result filters preserve the selected
lesson and unsaved draft. The actual inline script passes 36 behavior checks.

Ten ordinary Docker profiles support Python Core, TensorFlow CPU, PyTorch CPU,
C++20, Java 21, Node JavaScript, strict TypeScript, standalone Scala, Scala Spark
and PySpark. The app-to-worker route has now executed one current reference
successfully through each profile. C++ ownership lesson009 explicitly explains
its fixed verifier entry point; reading lessons no longer receive run guidance.

Windows and Mac thin launchers obtain the actual published port from the
healthy container, including `.env` port overrides. Windows needs a local Linux
Docker engine with WSL2, but no host Python/compiler/PostgreSQL for ordinary
classroom use. The clean starter archive includes all course/build sources and
excludes learner state, credentials, host node_modules and checker caches.

Classroom learning, database and private runtime storage use separate named
volumes. Ordinary worker ports stay private; neither the browser nor a learner
worker mounts the engine socket. This is a personal trusted-code classroom,
not a hostile multi-user security sandbox. Kubernetes requires explicit owned
host preparation and has its own restricted broker and bounded lease.

## Actual validation evidence so far

- `work/current-reference-evidence.json`: 385 source-hash-matching successful
  Docker reference records, including all 40 book examples and 69 Scala/Spark
  language variants. The final expert and applied fixes are included.
- [Runtime reference evidence](runtime-reference-evidence.json): portable public index
  of the same reference/source/image identities, without learner output or tokens.
- 115 standalone and 43 sequential ML worked programs passed fresh Docker
  processes, followed by focused attention, decoder, normalization, tracing,
  LoRA and PyTorch repair batches. Review ledgers identify prose-only parity.
- All 76 C++ worked programs and both complete CMake projects passed the newly
  rebuilt GCC image, including configure/build/CTest/install and an installed
  consumer. `work/cpp-project-current-acceptance.json` and
  `work/cpp-worked-programs-docker-acceptance.json` are current.
- All 6 SQL learner/reference pairs passed native PostgreSQL 16 and actual
  Docker PostgreSQL 17 as the restricted course user, using temporary objects
  and rollback. See `work/sql-deepening-docker-acceptance.json`.
- All 12 new Python references passed actual Core Docker; a later pandas mixed-ID
  rejection fix has its own matching acceptance receipt.
- JS029-031 passed actual Docker-served Chromium keyboard, focus, storage,
  URL, literal-text and CSP checks. The temporary servers were removed.
- The current Docker delivery audit checked 2,186 HTML pages, 1,269 module
  documents, 442 lesson variants and 50,507 internal links with zero failures.
  See work/one-command-delivery-acceptance.json. All ten ordinary app-to-worker
  routes passed fresh references. Desktop/mobile LLM reading, preference
  persistence, source/notes retention and the 72-link chapter map also passed.
- Real browser C++ compilation prints 42; previous Java and Node browser runs
  passed. Saved code/output survived container replacement. Mobile book search
  found random forests, hid practice gates, retained section navigation and
  showed no horizontal page overflow at 390px.
- Final source acceptance: Ruff/format passed 339 checked files; strict MyPy
  passed 195 source files; all 122 notebooks and 26 course validation checks
  passed. All 412 authored module contracts and 36 UI behaviors passed.
  The grouped four-worker suite passed 2,011 tests with 244 explicit
  optional host-runtime skips in 127.16 seconds. Separately qualified Docker
  references and browser/cluster checks remain distinct evidence tiers.
  Repository and Git-history secret scans passed in the earlier completed phase.
- Real C++, Java, JavaScript and TypeScript error submissions failed with the
  expected compiler/parser diagnostics before program output. Failed source
  remained saved as designed; prior validation pads were restored afterward.
  See `work/compiler-failure-acceptance.json`.
- Actual stdio MCP initialization, discovery and content reads passed for all
  11 subjects and 412 canonical lessons. Default mutation/solution boundaries
  held, with no writes, network or child execution by the server. The task
  receipt is `work/mcp-final-smoke/receipt.json`.


## Kubernetes and optional pretrained evidence

Kubernetes contract 2 passed its 12 actual positive/negative/cleanup cases and a
configured classroom workload. SIGTERM removed 5 owned objects to 0 in 5.078s.
The exact cluster was released. The new teacher-only 019 observer additionally
proved environment snapshot, asynchronous projected-file update, explicit cache
reload and replacement-Pod state. Projection was observed at 62.898s; the complete
operation took 75.701s. UID-aware cleanup and exact-session release succeeded.
The initial patch-file stdin error was repaired and its failure provenance kept.
See `work/kubernetes-secret-observer-acceptance.json` and the subject status.
Advanced controller/storage/network host capabilities remain separately scoped.

The optional pinned SmolLM2 recipe executed actual full and LoRA ten-step
training offline in its own CPU image. Seeding before adapter construction
repaired nondeterministic initialization; two fresh runs produced identical
adapter bytes. The generated conversion-rate answer was factually wrong and
truncated, so answer acceptance remains rejected despite successful mechanics.
The tiny four-train/one-evaluation shared-template fixture is not domain-quality
proof. Weights remain outside the repository. Seeded training/inference receipts
are `work/pretrained-seeded-training-acceptance.json` and
`work/pretrained-seeded-inference-acceptance.json`.

## Build and environment

All observed container execution is Linux arm64 on this machine's local engine.
Native Windows/WSL 2 and Linux amd64 execution remain unqualified. Both platform
locks and multi-architecture base manifests are available; configuration is not
runtime evidence. No GPU or internet model API is required by default examples.

The shared launcher prepares all ten ordinary workers and the lab from the
frozen generated source. Per-service build calls bound image-build concurrency.
Use the final distribution report for its exact image identities and archive hash.
This engine cannot verify Docker Hub's CDN certificate chain, so successful
builds used the documented TLS-enabled mirrors and pinned Astral Python image.
The checked-in `docker/registry-mirrors.env.txt` is a public build-only override.
The final user command must show foreground build logs and never publish images.

## Preserved validation state

The follow-up uses only ds60-onestep-validation, on app port 8766 and PostgreSQL
port 55433 after its explicit port-change test. The earlier
ds60-classroom-validation project is stopped. Its volumes and the new project's
volumes retain test learning state. Personal ds60-learning-postgres-1 and
chs-datatier-valkey-1 stay untouched. Personal port 8765 remains occupied.

Stop only the follow-up project and the isolated native PostgreSQL 16 instance
on port 58432 when finishing acceptance; the final output report records cleanup
readback. No kind nodes remain. Do not broadly prune images or volumes. No
continuation automation remains active. Human Git staging, commits and pushes
remain separate.

The new One-Command-Classroom archive supersedes the prior Complete-Classroom
and beta/native archives. The source entrypoint is ./classroom; from the user's
Mac, ~/workspace/ds60sqlpy/classroom works from any directory. Build output stays
visible and no image is published.
