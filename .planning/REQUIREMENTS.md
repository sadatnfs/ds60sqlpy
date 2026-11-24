# Requirements: DS60 Classroom Overhaul

**Defined:** 2026-11-23
**Approved by project owner:** 2026-11-23
**Core Value:** Learners can understand, practice, run, and keep their work in any DS60 course without installing toolchains or losing learning state.

## v1 Requirements

### Guided Classroom

- [x] **GUIDE-01**: A learner can open the classroom guide from the home screen and lesson workspace, find what each major screen and control does, and follow initialization and lesson-switching instructions.
- [x] **GUIDE-02**: A learner can start, dismiss, and restart the optional classroom tour without changing the selected lesson, overwriting work, or starting code execution.
- [x] **UX-01**: In each supported desktop lesson mode, the workspace clearly identifies the current lesson, available actions, runtime or reading capability, readiness, and where results appear.
- [x] **UX-02**: A learner can operate the desktop classroom with the keyboard and see clear focus and status cues; applicable project contrast and accessibility checks pass.
- [x] **UX-03**: The classroom chrome passes an unslop audit (heydamir/unslop): no decorative gradients, glows, emoji icons, uppercase tracked labels, looping motion or off-scale spacing, one accent on a quiet neutral ramp, while lesson plans and lesson content stay unchanged.
- [x] **STATE-01**: Navigation, lesson switching, viewing old results, test setup, and runtime restart preserve learner drafts, progress, and receipts; viewing old evidence never re-executes code.

### Walkthroughs

- [x] **WALK-01**: A Python walkthrough presents a bounded, testable execution trace with relevant source location, event, stack or local state, output, and clear limit or error behavior.
- [x] **WALK-02**: A SQL walkthrough explains only its documented, verified query subset, ties clause highlights to source offsets and PostgreSQL results, and clearly handles unsupported input without modifying learner data.
- [x] **WALK-03**: Each existing track that benefits from a guided worked-example or solution walkthrough provides a course-appropriate explanation through a tested adapter or authored steps, without claiming universal automatic tracing.
- [x] **WALK-04**: Learners can distinguish a code walkthrough from an ordinary run and inspect a solution walkthrough without replacing their own draft.

### Curriculum Quality

- [x] **CURR-01**: A maintained catalog-driven matrix accounts for every current subject and lesson, distinguishing authored, planned, reading-only, and runnable content and recording source, profile, dependencies, and known gaps.
- [x] **CURR-02**: Every authored lesson states observable learning outcomes, direct prerequisites, essential terms, and enough context to orient a new learner while preserving stable lesson identity.
- [x] **CURR-03**: Every authored lesson includes an accurate, substantive worked example with explanation and interpretation appropriate to its subject; non-code lessons use an appropriate non-code artifact.
- [x] **CURR-04**: Every practice lesson progresses from supported reasoning or modification toward appropriate independent application and includes a solution or feedback that explains the reasoning.
- [x] **CURR-05**: Each runnable example is checked against its registered runtime and required data or fixture, with actual behavior matching the explanation; unsupported or unavailable capabilities are identified honestly.
- [x] **CURR-06**: Every existing language and subject track is reviewed against the shared quality rubric and reaches its acceptance threshold, with each non-applicable criterion or remaining gap explicitly justified.
- [x] **CURR-07**: Content improvements are source-led and course-specific; generated readers, stable IDs, prerequisites, and authored-versus-planned distinctions remain consistent.

### Runtime and Release

- [x] **RUN-01**: Every Docker image profile included in a release builds from the intended repository revision for its supported architectures and passes its documented startup and operation checks.
- [x] **RUN-02**: Fresh setup, resume, stop, and restart behavior are verified with disposable Compose projects, and saved learner data remains intact.
- [x] **SEC-01**: Every image intended for publication is scanned with the current configured vulnerability checks and has no unresolved detected CVEs; affected images are remediated and rescanned before publication.
- [x] **QUAL-01**: Each phase passes the focused automated tests, repository lint and type checks, and generated-content checks relevant to its changes.
- [x] **QUAL-02**: Desktop browser acceptance verifies the affected lesson and operation flows, including errors and recovery, at the supported desktop viewport without relying on mobile layouts.
- [x] **REL-01**: A release is published only after its source, tests, Docker images, image scans, registry target, and version tags are verified; the published artifact is pulled and smoke-tested.
- [x] **REL-02**: Completion stops only DS60-owned test services and containers, preserves learner volumes, and leaves unrelated containers untouched.
- [x] **REL-03**: Release 2.0.0 is published as a verified GitHub release with its registry images, after which every local DS60 Docker container and image is removed, learner volumes are preserved, and unrelated resources are untouched.

### Post-release Hardening

- [ ] **HARD-01**: Repository and image security findings with an available fix are remediated; shipped Dockerfile misconfigurations are removed from the app image, base-image and kernel-header findings are reduced, CodeQL scans every push, and each remaining exception has a current justification.
- [ ] **HARD-02**: Lessons teach lesson-specific material rather than shared template text; the catalog templated-prose total falls by at least half and no lesson exceeds 50% templated words.
- [ ] **HARD-03**: Runnable code samples in the companion guides are executed by an automated harness in their own runtimes, and failures are fixed or explicitly marked as fragments.
- [ ] **HARD-04**: The R worker image can build source packages with C, C++ and Fortran code, and a test proves it.
- [ ] **HARD-05**: Qualified scientific-project images are scanned and pushed to the registry from GitHub Actions only, with multi-architecture manifests.
- [ ] **HARD-06**: The full test suite passes repeatedly under parallel execution with no known flaky tests.
- [ ] **HARD-07**: No tracked first-party file contains an em dash or en dash, and a repository-wide gate enforces it.

## v2 Requirements

Deferred until the existing course quality floor and core classroom workflows are established.

### Optional Learning Features

- **LEARN-01**: Learners can use prediction checks, code-ordering activities, or seeded debugging exercises where a course can provide unambiguous and useful feedback.
- **LEARN-02**: Learners can receive track-aware next-step suggestions grounded in the authored prerequisite graph.
- **LEARN-03**: Optional AI tutoring or adaptive sequencing is introduced only after a separate evidence, evaluation, and safety design.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Mobile-specific interface design | The owner specified desktop as the target. |
| New subject families | Improve and qualify the existing catalog before expanding it. |
| A universal automatic step-through parser for every language and subject | Runtime semantics and teaching needs differ; use tested adapters or authored steps. |
| Hosted multi-user classroom, social features, or remote execution of untrusted code | These change the local product and trusted-local-code boundary. |
| Gamified completion, inferred mastery, or mandatory solution gates | These do not establish learning and conflict with self-paced use of worked solutions. |
| Test cleanup that deletes learner volumes or unrelated containers | Preserve user data and services; use isolated disposable test state. |

## Definition of Done

- Every v1 requirement is mapped to exactly one roadmap phase and verified with recorded evidence.
- Every existing subject track has a complete coverage status; no track is considered finished from lesson counts or a showcase sample alone.
- Runnable examples and runtime-dependent walkthroughs are tested against the correct supported environment; non-applicable cases have a reason.
- Automated checks, desktop browser review, saved-state checks, and required Docker profile and vulnerability checks pass.
- Any published release is verified from its resulting registry artifact, and cleanup preserves learner data and unrelated services.

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GUIDE-01 | Phase 1 | Complete |
| GUIDE-02 | Phase 1 | Complete |
| UX-01 | Phase 6 | Complete |
| UX-02 | Phase 6 | Complete |
| STATE-01 | Phase 6 | Complete |
| WALK-01 | Phase 1 | Complete |
| WALK-02 | Phase 1 | Complete |
| WALK-03 | Phase 5 | Complete |
| WALK-04 | Phase 1 | Complete |
| CURR-01 | Phase 2 | Complete |
| CURR-02 | Phase 3 | Complete |
| CURR-03 | Phase 4 | Complete |
| CURR-04 | Phase 4 | Complete |
| CURR-05 | Phase 5 | Complete |
| CURR-06 | Phase 5 | Complete |
| CURR-07 | Phase 3 | Complete |
| RUN-01 | Phase 7 | Complete |
| RUN-02 | Phase 7 | Complete |
| SEC-01 | Phase 8 | Complete |
| QUAL-01 | Phase 9 | Complete |
| QUAL-02 | Phase 9 | Complete |
| REL-01 | Phase 10 | Complete |
| REL-02 | Phase 10 | Complete |
| UX-03 | Phase 08.1 | Complete |
| REL-03 | Phase 10 | Complete |
| HARD-01 | Phase 11 | Pending |
| HARD-02 | Phase 11 | Pending |
| HARD-03 | Phase 11 | Pending |
| HARD-04 | Phase 11 | Pending |
| HARD-05 | Phase 11 | Pending |
| HARD-06 | Phase 11 | Pending |
| HARD-07 | Phase 11 | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0

---
*Requirements defined: 2026-11-23*
*Last updated: 2026-11-24 after adding Phase 11 post-release hardening requirements*
