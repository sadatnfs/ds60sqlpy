# Requirements: DS60 Classroom Overhaul

**Defined:** 2026-11-23
**Approved by project owner:** 2026-11-23
**Core Value:** Learners can understand, practice, run, and keep their work in any DS60 course without installing toolchains or losing learning state.

## v1 Requirements

### Guided Classroom

- [x] **GUIDE-01**: A learner can open the classroom guide from the home screen and lesson workspace, find what each major screen and control does, and follow initialization and lesson-switching instructions.
- [x] **GUIDE-02**: A learner can start, dismiss, and restart the optional classroom tour without changing the selected lesson, overwriting work, or starting code execution.
- [ ] **UX-01**: In each supported desktop lesson mode, the workspace clearly identifies the current lesson, available actions, runtime or reading capability, readiness, and where results appear.
- [ ] **UX-02**: A learner can operate the desktop classroom with the keyboard and see clear focus and status cues; applicable project contrast and accessibility checks pass.
- [ ] **STATE-01**: Navigation, lesson switching, viewing old results, test setup, and runtime restart preserve learner drafts, progress, and receipts; viewing old evidence never re-executes code.

### Walkthroughs

- [x] **WALK-01**: A Python walkthrough presents a bounded, testable execution trace with relevant source location, event, stack or local state, output, and clear limit or error behavior.
- [x] **WALK-02**: A SQL walkthrough explains only its documented, verified query subset, ties clause highlights to source offsets and PostgreSQL results, and clearly handles unsupported input without modifying learner data.
- [ ] **WALK-03**: Each existing track that benefits from a guided worked-example or solution walkthrough provides a course-appropriate explanation through a tested adapter or authored steps, without claiming universal automatic tracing.
- [x] **WALK-04**: Learners can distinguish a code walkthrough from an ordinary run and inspect a solution walkthrough without replacing their own draft.

### Curriculum Quality

- [ ] **CURR-01**: A maintained catalog-driven matrix accounts for every current subject and lesson, distinguishing authored, planned, reading-only, and runnable content and recording source, profile, dependencies, and known gaps.
- [ ] **CURR-02**: Every authored lesson states observable learning outcomes, direct prerequisites, essential terms, and enough context to orient a new learner while preserving stable lesson identity.
- [ ] **CURR-03**: Every authored lesson includes an accurate, substantive worked example with explanation and interpretation appropriate to its subject; non-code lessons use an appropriate non-code artifact.
- [ ] **CURR-04**: Every practice lesson progresses from supported reasoning or modification toward appropriate independent application and includes a solution or feedback that explains the reasoning.
- [ ] **CURR-05**: Each runnable example is checked against its registered runtime and required data or fixture, with actual behavior matching the explanation; unsupported or unavailable capabilities are identified honestly.
- [ ] **CURR-06**: Every existing language and subject track is reviewed against the shared quality rubric and reaches its acceptance threshold, with each non-applicable criterion or remaining gap explicitly justified.
- [ ] **CURR-07**: Content improvements are source-led and course-specific; generated readers, stable IDs, prerequisites, and authored-versus-planned distinctions remain consistent.

### Runtime and Release

- [ ] **RUN-01**: Every Docker image profile included in a release builds from the intended repository revision for its supported architectures and passes its documented startup and operation checks.
- [ ] **RUN-02**: Fresh setup, resume, stop, and restart behavior are verified with disposable Compose projects, and saved learner data remains intact.
- [ ] **SEC-01**: Every image intended for publication is scanned with the current configured vulnerability checks and has no unresolved detected CVEs; affected images are remediated and rescanned before publication.
- [ ] **QUAL-01**: Each phase passes the focused automated tests, repository lint and type checks, and generated-content checks relevant to its changes.
- [ ] **QUAL-02**: Desktop browser acceptance verifies the affected lesson and operation flows, including errors and recovery, at the supported desktop viewport without relying on mobile layouts.
- [ ] **REL-01**: A release is published only after its source, tests, Docker images, image scans, registry target, and version tags are verified; the published artifact is pulled and smoke-tested.
- [ ] **REL-02**: Completion stops only DS60-owned test services and containers, preserves learner volumes, and leaves unrelated containers untouched.

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
| UX-01 | Phase 6 | Pending |
| UX-02 | Phase 6 | Pending |
| STATE-01 | Phase 6 | Pending |
| WALK-01 | Phase 1 | Complete |
| WALK-02 | Phase 1 | Complete |
| WALK-03 | Phase 5 | Pending |
| WALK-04 | Phase 1 | Complete |
| CURR-01 | Phase 2 | Pending |
| CURR-02 | Phase 3 | Pending |
| CURR-03 | Phase 4 | Pending |
| CURR-04 | Phase 4 | Pending |
| CURR-05 | Phase 5 | Pending |
| CURR-06 | Phase 5 | Pending |
| CURR-07 | Phase 3 | Pending |
| RUN-01 | Phase 7 | Pending |
| RUN-02 | Phase 7 | Pending |
| SEC-01 | Phase 8 | Pending |
| QUAL-01 | Phase 9 | Pending |
| QUAL-02 | Phase 9 | Pending |
| REL-01 | Phase 10 | Pending |
| REL-02 | Phase 10 | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0

---
*Requirements defined: 2026-11-23*
*Last updated: 2026-11-23 after research synthesis*
