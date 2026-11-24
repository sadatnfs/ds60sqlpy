# Project Research Summary

**Project:** DS60 Classroom Overhaul  
**Domain:** Local, desktop-first, multi-track programming, data-science, statistics, machine-learning, and applied-science classroom  
**Researched:** 2026-11-23  
**Confidence:** MEDIUM

## Executive Summary

DS60 is an established local browser classroom, not a greenfield course platform. Its value depends on three things working together: clear instruction across the existing catalog, honest lesson/runtime capabilities, and reliable preservation of learners' local work. The research strongly recommends improving the classroom through its current Python modular monolith, static browser UI, independent curriculum sources/loaders, fixed Docker worker profiles, and separate learner-state stores. Do not treat the owner's Python/SQL quality reference as a scope limit: every existing language and subject track is in scope, with course-specific instruction rather than mechanically identical content.

The recommended sequence is to qualify the unfinished Python/SQL checkpoint, inventory all current routes and learning modes against a shared quality contract, then improve content and classroom operation without collapsing the existing authoring boundaries. Follow with track-appropriate runtime, saved-state, browser, image, and release verification. The principal risks are “parity” that counts files instead of equivalent learning, a plausible but unverified SQL walkthrough, and changes or test cleanup that damage saved work. Mitigate these with explicit per-track evidence, tested/fail-closed execution explanations, disposable integration state, and release gates that distinguish repository, image, and registry verification.

## Key Findings

### Recommended Stack

Keep the current stack and add no new application framework or content platform. The product already uses Python 3.11-3.12, its standard-library HTTP server, packaged HTML/CSS/vanilla JavaScript, Docker Compose, profile-specific worker images, `uv`/`uv.lock`, pytest, and the existing content/runtime validators. The stack research is explicit: all-track improvement is a curriculum, renderer, and verification effort, not a rationale to migrate the web stack, database, or runtime boundary. Extend the existing test and validation patterns to represent every registered track; use browser review for browser behavior and do not mistake Python's permissive `html.parser` for a conformance or accessibility validator. See [STACK.md](STACK.md).

**Core technologies:**
- **Python 3.11-3.12 and the standard-library HTTP server:** established application/control plane with a supported runtime range; preserve it unless a concrete compatibility need emerges.
- **Static HTML/CSS/vanilla JavaScript:** packaged, offline-compatible desktop classroom; improve in place rather than adding a framework/build chain.
- **Docker Compose and profile-specific workers:** current local delivery and runtime isolation model; keep fixed, reviewed operations and avoid consolidating toolchains into the app image.
- **pytest and existing validators:** extend current quality gates with catalog-driven, parametrized all-track coverage; avoid new validation dependencies without a specific gap.
- **PostgreSQL and optional `psycopg` bridge:** preserve existing SQL learning and integration boundaries.

### Expected Features

The feature research treats baseline classroom infrastructure as already present; the overhaul's table stakes are the instructional and operational quality layered on top. Build a shared lesson contract around observable outcomes, explicit prerequisites, essential concepts, worked examples, practice, explained solutions/feedback, and clear runtime/data requirements. A repeatable learner loop should move from context and explanation through inspection or prediction, bounded action, observation, interpretation, and next step. Adapt the activity to the subject: not every valid lesson is executable code or needs a Run button.

**Must have (table stakes):**
- A catalog-wide, beginner-readable lesson contract with stable IDs and an honest distinction between planned and authored material.
- A guided but flexible lesson loop, meaningful worked examples, scaffolded-to-independent practice, and reviewed feedback that tells learners what to inspect next.
- A desktop classroom path that makes lesson, work, run/reading mode, results, and resume points understandable while preserving drafts, progress, and receipts.
- A per-track quality/completeness matrix that verifies outcomes and learning evidence, not merely file counts; runnable artifacts where execution is part of the learning outcome.

**Should have (competitive):**
- Qualify Python/SQL interactive walkthroughs as a reference, then extend the shared interaction contract only through tested per-language adapters or authored steps.
- Add low-stakes prediction → observation → explanation and selectively use missing-line, trace-table, code-ordering, or debugging activities.
- Use analysis-story lessons for data/science tracks (question, provenance, assumptions, method, diagnostics, interpretation, limitations) and track-aware next-step guidance.
- Maintain automated content-quality checks paired with human review; automation can find omissions and regressions, not certify pedagogy or scientific validity.

**Defer (v2+):**
- A universal parser/stepper across languages and subjects, adaptive sequencing based on inferred mastery, social/hosted classroom features, and general-purpose AI tutoring.
- New subject families or broad platform changes. First meet the quality floor for existing tracks and establish evidence of a concrete learner need.

See [FEATURES.md](FEATURES.md) for the full feature landscape and research limits. Evidence for instructional patterns is credible but only partly transferable: for example, PRIMM and formative-assessment studies support investigation and feedback patterns, but much of the available evidence is from school or higher-education contexts rather than adult local self-study.

### Architecture Approach

Retain the local modular monolith and standardize the learner-facing contract across current boundaries. Subject sources, legacy catalogs, authored module plans/manifests, and the statistics tutorial have distinct authoring and validation lifecycles; loaders compose normalized learner-facing views for the shared `/classroom` shell. Subject says what is learned; lesson mode and a registered profile say how it is learned and whether/how it runs. The shared UI should be capability-driven, while adapters choose fixed worker operations. Keep saved drafts, progress, notes, receipts, and job state separate and source-bound; viewing old evidence must not rerun code or overwrite current work. See [ARCHITECTURE.md](ARCHITECTURE.md).

**Major components:**
1. **Maintained curriculum sources and generators**; track-specific instructional source, stable identity, prerequisites, artifacts, and references; generated HTML/readers are outputs, not authoring sources.
2. **Catalog loaders and normalized views**; validate identity, prerequisites, artifact completeness, mode, and profile; planned entries do not become runnable lessons by implication.
3. **Shared classroom and application services**; common navigation/workspace behavior, drafts, runs, progress, and results while retaining subject-specific content and capability distinctions.
4. **Fixed runtime adapters and prepared Docker workers**; allowlisted profiles and constrained operations, bounded I/O and cleanup; curriculum metadata must not choose arbitrary shell commands.
5. **Learner-state stores and local delivery**; preserve current store/volume boundaries through app and worker recreation; integration tests use explicitly disposable project state.

### Critical Pitfalls

These are risks, not blanket claims that the current product contains defective lessons or a confirmed data-loss/security incident.

1. **Plausible but incorrect or unlearnable instruction**; align outcomes, prerequisites, explanations, examples, expected results, exercises, and solutions; execute examples in their target runtime and get an independent learner-level review. CS2023 is a competency reference, not lesson validation.
2. **Fake all-track parity**; do not equate lesson counts or catalog registration with equivalent learning. Track outcomes, prerequisites, examples, practice, solutions, and runtime evidence; preserve appropriate course-specific depth and label gaps instead of adding placeholders.
3. **Unverified SQL walkthroughs (observed repository risk)**; the codebase concern map identifies a new custom tokenizer/planner/response path without matching automated coverage, and PostgreSQL verification remains outstanding. Test supported and rejected syntax explicitly, fail closed or fall back when a trustworthy explanation is unavailable, and compare behavior with the supported PostgreSQL runtime using disposable data.
4. **Learner-state loss (high-impact change risk)**; retain separate state contracts and stable identities; test with `tmp_path`/disposable databases or Compose projects, include existing-state fixtures and recovery checks, and never use learner volumes as test cleanup targets.
5. **Execution-boundary and delivery mistakes (observed architecture boundary; release readiness incomplete)**; preserve trusted-local-code assumptions and fixed worker operations; do not treat CPU/time limits or “containerized” as a full sandbox. Rebuild/test images from the approved revision, check the intended registry target just before publication, and pull/smoke-test the pushed digest before declaring release readiness.

Detailed evidence, warning signs, prevention, and phase-specific mitigations are in [PITFALLS.md](PITFALLS.md).

## Implications for Roadmap

The following is a dependency-ordered proposal, not a claim that the project already has a detailed validated phase plan. It respects the active scope in [PROJECT.md](../PROJECT.md): qualify the checkpoint first; improve **all** existing language and subject tracks; retain desktop-first local Docker delivery and learner state. `.planning/STATE.md` and `.planning/REQUIREMENTS.md` were not present at synthesis time, so the project file and the owner's explicit scope clarification are the available scope authority.

### Phase 1: Qualify the Existing Checkpoint and Python/SQL Reference
**Rationale:** Project context calls the checkpoint unfinished, not a release. Its step-through is a useful quality reference only after its behavior is tested. Qualifying it first resolves an existing prerequisite and prevents scaling an unverified interaction pattern.  
**Delivers:** Automated tests for trace/planner/response behavior and edge cases; disposable PostgreSQL integration verification; browser acceptance for the reference flow; completed checkpoint guide/tour/walkthrough qualification as defined by active project requirements.  
**Addresses:** Guided walkthroughs and predictable lesson operation from FEATURES; existing reference implementation and checkpoint state from PROJECT/ARCHITECTURE.  
**Avoids:** Pitfall 3 (a plausible SQL parser guess) and Pitfall 4 (data loss in browser/runtime transitions). This phase must not expand the parser's claimed language coverage without evidence.

### Phase 2: Catalog-Wide Inventory and Acceptance Contract
**Rationale:** All-track scope cannot be planned or verified from a handful of showcase lessons. First enumerate current loader/catalog routes and classify authored versus planned, subject, learning mode, profile/data dependencies, generator, and artifacts. Establish a common outcome-level rubric while respecting track-specific authoring contracts.  
**Delivers:** A source-backed coverage matrix for every current language/subject track and lesson/sequence, explicit gaps and “not applicable” reasons, and acceptance evidence for a track to qualify.  
**Uses:** Existing catalog reports, pytest/validators, and standard library only where narrow structural checks add value.  
**Implements:** Maintained-source → loader → normalized learner-facing view contracts.  
**Avoids:** Pitfalls 1 and 2 (instructional correctness and file-count parity); do not count a plan entry as authored content.

### Phase 3: All-Track Curriculum and Learning-Loop Improvements
**Rationale:** With the inventory and quality floor agreed, content work can proceed across every existing course family without privileging only Python/SQL or flattening subject differences. Batch by compatible content/source/runtime workflows, but report completion by track so a batch cannot hide neglected routes.  
**Delivers:** Improved lessons with observable objectives, prerequisites, concept explanation, worked examples, appropriate scaffolded practice and solution rationale, accurate expected results, and declared reading/run mode. Include analysis-story patterns for relevant science/data courses and retain authored-versus-planned semantics.  
**Addresses:** All-track lesson contract, guided sequence, worked examples, practice, and understandable feedback from FEATURES.  
**Uses:** Existing content generators and source-specific validators; execute examples when execution is part of the outcome.  
**Avoids:** Pitfalls 1 and 2; no copied Python prose as a substitute for language- or subject-aware instruction.

### Phase 4: Capability-Driven Desktop Workspace and Evidence
**Rationale:** Make the shared shell support the improved course loop, without pretending every lesson can run or changing state identity/storage. Keep UI consistency at the interaction level and truthful differences at the capability level.  
**Delivers:** Clear navigation and lesson workspace for reading, practice, preview, and worker-backed modes; understandable result/feedback placement; keyboard/focus and non-color cues; reliable resume; old result inspection that does not replay execution. Extend walkthrough behavior only via proven adapters or authored steps.  
**Addresses:** Predictable desktop operation, feedback, selective prediction/investigation formats, and track-aware next steps from FEATURES.  
**Implements:** Shared shell, capability-driven lesson workspace, and source-bound typed evidence from ARCHITECTURE.  
**Avoids:** Pitfalls 3 and 4; do not unify evidence into a misleading completion flag or sacrifice current drafts/receipts for UI simplicity.

### Phase 5: Runtime, Persistence, and Release Qualification
**Rationale:** Curriculum admission and UI metadata do not prove a worker/image works or that state survives lifecycle events. Validate affected runtime paths in a clean, disposable environment before any publication. Release is a gated outcome, not a side effect of content completion.  
**Delivers:** Reproducible checks for supported profile images, startup/resume, actual bounded operations, selected runtime behavior, saved-work persistence across restart/recreation, repository quality checks, and bounded desktop acceptance. If a release is authorized, re-check Docker Hub ownership/target, publish only after gates, then pull and test the artifact by digest; clean only DS60-owned test resources.  
**Uses:** Docker Compose/profile setup, current CI and quality checks, existing release workflow; preserve PostgreSQL and state volumes.  
**Avoids:** Pitfalls 4 and 5, plus Docker freshness/reproducibility and publication risks in PITFALLS.md. Never prune learner volumes or stop unrelated containers.

### Phase Ordering Rationale

- Qualify the in-progress reference before using it as a pattern; then measure the whole catalog before authoring to an all-track scope.
- Establish outcomes and evidence before bulk lesson edits; content generators and catalog loaders remain the source-specific boundaries.
- Improve the shared workspace against real lesson modes and learner tasks rather than making UI affordances dictate the curriculum.
- Test progressively: content/contract checks first, then changed runtime profiles and state behavior, then browser and clean-image/release checks. A test pass does not by itself establish instructional quality.
- Treat publication as separately gated. Preserve local-only and trusted-local-code boundaries; any hosted/untrusted-code idea would require new approved scope and a security design, not an incremental classroom feature.

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 1:** Targeted research/inspection is warranted for the exact supported SQL subset, PostgreSQL 17 behavior, edge cases, and the existing trace implementation. Its custom behavior is not covered merely by general SQL documentation.
- **Phase 3:** Use targeted subject-expert/repository research for niche scientific, statistical, and specialist tracks (and each track's source/generator/runtime). External pedagogy findings are not enough to validate scientific assumptions or produce accurate course-specific instruction.
- **Phase 5:** Re-check current Docker image/profile configuration and registry state at execution time. Deep research is needed only if verification exposes an unsupported isolation, portability, or provenance requirement.

**Phases with standard patterns (skip broad research-phase):**
- **Phase 2:** Repository catalog/loader inventory and matrix construction are primarily codebase discovery and acceptance-definition work; use the current codebase maps and source generators.
- **Phase 4:** Shared desktop interaction, saved-state regression testing, keyboard access, and capability-driven rendering have established repository patterns. Validate against WCAG 2.2 and actual browser behavior; do not expand into a new UI stack.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Directly grounded in the supplied repository stack and architecture maps and existing dependency/configuration details. Exact all-track coverage assertions remain to be designed. |
| Features | MEDIUM | Broad computing-education literature supports objectives, worked examples, formative checks, and investigation. Evidence is not specifically about adult self-directed study in a local multi-track classroom, and it does not determine subject-specific teaching quality. |
| Architecture | HIGH | Strong repository-specific evidence from the codebase map and authoring/implementation documentation. External official docs corroborate Docker volume and WCAG guidance, not the DS60 contracts themselves. |
| Pitfalls | MEDIUM | The key implementation/state/runtime risks are tied to the repository concern map and project constraints; general instructional risks are evidence-informed, not proof of defects in individual DS60 lessons. No code, tests, browser, or Docker builds were run as part of this research. |

**Overall confidence:** MEDIUM. The architectural direction and scope are clear, but the breadth and quality of current lesson content have not been independently audited, and this synthesis is research - not qualification evidence.

### Gaps to Address

- **STATE/requirements files absent:** `.planning/STATE.md` and `.planning/REQUIREMENTS.md` were unavailable. Before roadmap approval, reconcile this synthesis with any subsequently created active state/requirements and the current project decisions.
- **No complete current lesson-quality inventory in research:** Phase 2 must generate the source-of-truth route/lesson matrix from all loaders and distinguish authored, planned, reading-only, and runnable content.
- **No per-track acceptance threshold:** Define observable per-lesson/track completion and the required sample of runtime/browser evidence; avoid a count-only gate.
- **Walkthrough coverage boundary:** Confirm what Python/SQL currently supports and what the milestone expects for other executable tracks. Do not promise universal automatic tracing; decide between tested adapters and explicit authored walkthroughs case by case.
- **Execution and release evidence outstanding:** Research did not execute tests, builds, Compose lifecycle checks, browser review, registry checks, or release publication. Verify all at implementation/release time and preserve learner volumes and unrelated services.
- **Instructional transfer uncertainty:** Apply PRIMM, formative-assessment, and Parsons findings as candidate patterns and evaluate them in DS60's context; do not claim a proven effect for its adult learner population.

## Sources

### Primary: Repository evidence (HIGH for product context)

- [`.planning/PROJECT.md`](../PROJECT.md); active scope, validated baseline, checkpoint status, constraints, state preservation, and release/cleanup rules.
- [`STACK.md`](STACK.md); existing stack, version support, dependency policy, and test/tool recommendations.
- [`FEATURES.md`](FEATURES.md); table stakes, differentiators, deferrals, and feature dependencies.
- [`ARCHITECTURE.md`](ARCHITECTURE.md); curriculum/catalog boundaries, runtime adapters, learner state, integration order, and local delivery.
- [`PITFALLS.md`](PITFALLS.md); evidence-classified risks, warnings, and mitigations.
- Repository maps/docs cited by the research inputs: `.planning/codebase/STACK.md`, `ARCHITECTURE.md`, `CONCERNS.md`, `TESTING.md`; `docs/repository-tour.md`, `docs/content-authoring.md`, `docs/implementation/ADDING_A_MODULE.md`, and `docs/implementation/CHECKPOINT.md`. These describe the repository and are not external efficacy evidence.

### Primary/official external references

- [Python 3.12 `html.parser`](https://docs.python.org/3.12/library/html.parser.html); limits of lightweight HTML token inspection.
- [pytest parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html) and [Python Packaging User Guide: `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/); established test matrix and optional-dependency practices.
- [PostgreSQL 17 lexical structure](https://www.postgresql.org/docs/17/sql-syntax-lexical.html), [`SELECT`](https://www.postgresql.org/docs/17/sql-select.html), and [transaction modes](https://www.postgresql.org/docs/17/sql-set-transaction.html); SQL grammar/runtime boundaries relevant to the walkthrough risk.
- [Docker Compose application model](https://docs.docker.com/compose/intro/compose-application-model/), [Docker volumes](https://docs.docker.com/engine/storage/volumes/), and [Docker Engine security](https://docs.docker.com/engine/security/); local service/project and persistence/security boundaries.
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/), [build context](https://docs.docker.com/build/concepts/context/), and [build attestations](https://docs.docker.com/build/metadata/attestations/); reproducible inputs and release artifact verification.
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/); web content accessibility criteria.
- [ACM/IEEE-CS/AAAI CS2023](https://csed.acm.org/); curriculum competency reference, not a DS60 lesson certification.

### Secondary: Computing-education research (MEDIUM; transfer limits apply)

- [PRIMM research project](https://computingeducationresearch.org/projects/primm/) and [2019 study](https://doi.org/10.1080/08993408.2019.1608781); investigate/predict/run/modify/make sequencing; evidence context is not adult local self-study.
- Thangaraj, Ward & O’Riordan, [systematic review of formative assessment in programming](https://doi.org/10.4230/OASIcs.ICPEC.2023.7); feedback/check patterns and evidence-base limitations.
- Ericson et al., [Parsons problems systematic review](https://doi.org/10.1145/3571785.3574127); constrained code-ordering as a selective practice option, not a universal replacement for writing.
- Barba et al., [Teaching and Learning with Jupyter](https://jupyter4edu.github.io/jupyter-edu-book/index.html); computational narrative, examples, assignments, and assessment patterns.
- Cambridge Handbook, [Novice Programmers and Introductory Programming](https://www.cambridge.org/core/books/cambridge-handbook-of-computing-education-research/novice-programmers-and-introductory-programming/0CEDFE1B121198D3FB5F1541EBE3DCAD); novice mental models, misconceptions, and cognitive load.

---
*Research completed: 2026-11-23*  
*Ready for roadmap: yes, subject to the gaps and active-scope reconciliation above.*
