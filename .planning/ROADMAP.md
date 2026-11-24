# Roadmap: DS60 Classroom Overhaul

## Overview

Qualify the unfinished release 1.4.4 classroom-guide and Python/SQL walkthrough checkpoint first, then use a catalog-wide evidence matrix to improve every existing language and subject track. The work proceeds from consistent lesson foundations through worked examples, practice, and course-appropriate walkthroughs; then it improves the desktop workspace and verifies local Docker runtimes, image security, code quality, and browser behavior. Publication and test-resource cleanup remain separate, explicitly gated outcomes. This is a brownfield local desktop classroom overhaul, not a new product or a scope limited to Python and SQL.

## Phases

- [ ] **Phase 1: Qualify 1.4.4 Guide & Python/SQL Walkthroughs** - Complete checkpoint qualification for the guide, tour, and reference walkthrough flows.
- [x] **Phase 2: Catalog-wide Coverage Matrix** - Establish source-backed coverage and acceptance evidence for every existing course and lesson.
- [x] **Phase 3: Lesson Foundations & Source Integrity** - Bring authored lessons across all tracks to clear outcomes, prerequisites, and consistent source identity.
- [x] **Phase 4: Worked Examples & Practice** - Improve course-specific examples, scaffolded practice, and explanatory solutions across the catalog.
- [ ] **Phase 5: Walkthroughs & Track Qualification** - Verify course-appropriate walkthroughs, runnable examples, and each track's quality threshold.
- [ ] **Phase 6: Desktop Workspace & Learner State** - Make classroom capabilities clear and preserve learner work through normal operation.
- [ ] **Phase 7: Docker Runtime & Persistence Qualification** - Verify release image profiles and disposable lifecycle behavior without losing saved work.
- [ ] **Phase 8: Release Image Security** - Require clean applicable vulnerability scans for every image intended for publication.
- [ ] **Phase 9: Code & Desktop Acceptance Gates** - Pass repository quality checks and bounded desktop browser acceptance for the overhaul.
- [ ] **Phase 10: Verified Publication & Safe Closeout** - Publish only qualified artifacts, smoke-test the pull, and separately verify safe cleanup.

## Phase Details

### Phase 1: Qualify 1.4.4 Guide & Python/SQL Walkthroughs
**Goal:** As a new learner, I want to use safe lesson guidance, so that I can learn without losing work.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: GUIDE-01, GUIDE-02, WALK-01, WALK-02, WALK-04
**Success Criteria** (what must be TRUE):
  1. A learner can open the manual from the home screen and lesson workspace, understand the major screens and controls, and follow initialization and lesson-switching guidance.
  2. A learner can start, dismiss, and restart the optional tour without changing the selected lesson, overwriting a draft, or executing code.
  3. Python traces expose bounded source-linked events and state, while SQL highlights correspond to supported syntax and verified PostgreSQL behavior; unsupported SQL is clearly rejected or safely handled without learner-data changes.
  4. Learners can tell walkthroughs from ordinary runs and inspect the Python/SQL solution walkthroughs without replacing their drafts; checkpoint acceptance evidence covers automated, disposable PostgreSQL integration, and desktop-browser checks.
**Plans**: 5/5 plans executed
Plans:
**Wave 1**
- [x] 01-01-PLAN.md: Prove the walkthrough tracer and qualify guide/tour safety

**Wave 2** *(after Wave 1)*
- [x] 01-02-PLAN.md: Qualify bounded source-linked Python traces

**Wave 3** *(after Wave 2)*
- [x] 01-03-PLAN.md: Reject unsupported SQL and verify offsets/results

**Wave 4** *(after Wave 3)*
- [x] 01-04-PLAN.md: Validate SQL before database preparation

**Wave 5** *(after Wave 4)*
- [x] 01-05-PLAN.md: Align SQL guidance and complete browser acceptance
**UI hint**: yes

### Phase 2: Catalog-wide Coverage Matrix
**Goal:** The owner and learner-facing work can be planned against a maintained, honest inventory of the entire existing catalog rather than a showcase sample.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: CURR-01
**Success Criteria** (what must be TRUE):
  1. Every current subject, track, lesson, and sequence is accounted for in a maintained catalog-driven matrix.
  2. Each entry distinguishes authored from planned and reading-only from runnable content, and records its source, profile, dependencies, artifacts, and known gaps.
**Plans**: 1 plan

**Wave 1**
- [x] 02-01-PLAN.md: Generate and gate the catalog coverage matrix

### Phase 3: Lesson Foundations & Source Integrity
**Goal:** Learners entering any existing authored track can understand what a lesson teaches and what it expects, while maintainers can trace the displayed lesson back to its stable source identity.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: CURR-02, CURR-07
**Success Criteria** (what must be TRUE):
  1. Every authored lesson states an observable outcome, direct prerequisites, essential terms, and enough context to orient a new learner.
  2. Lesson identity remains stable, and generated readers, prerequisites, maintained sources, and authored-versus-planned status agree across all tracks.
**Plans**: 4 plans

**Wave 1**
- [x] 03-01-PLAN.md: Measure observable outcomes and essential terms

**Wave 2**
- [x] 03-02-PLAN.md: Core lesson outcomes
- [x] 03-03-PLAN.md: Module outcomes and key terms, track by track

**Wave 3**
- [x] 03-04-PLAN.md: Close the gate

### Phase 4: Worked Examples & Practice
**Goal:** Learners across the existing catalog can study accurate examples, practice with appropriate support, and understand the reasoning behind feedback or solutions.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: CURR-03, CURR-04
**Success Criteria** (what must be TRUE):
  1. Every authored lesson has a substantive, accurate worked example with explanation and interpretation appropriate to its subject, including a suitable non-code artifact where execution is not the learning objective.
  2. Every practice lesson progresses from supported reasoning or modification toward independent application and includes a solution or feedback that explains its reasoning.
**Plans**: 3 plans

**Wave 1**
- [x] 04-01-PLAN.md: Measure templated prose and ratchet practice gaps

**Wave 2**
- [x] 04-02-PLAN.md: Worked examples, guides and solutions, track by track

**Wave 3**
- [x] 04-03-PLAN.md: Close the gate

### Phase 5: Walkthroughs & Track Qualification
**Goal:** Every existing track meets the agreed instructional quality floor, with honest execution claims and a suitable guided explanation wherever a walkthrough benefits learners.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: WALK-03, CURR-05, CURR-06
**Success Criteria** (what must be TRUE):
  1. Each existing track that benefits from a guided worked-example or solution walkthrough provides tested adapter behavior or authored steps without claiming universal automatic tracing.
  2. Each runnable example's observed behavior matches its explanation in the registered runtime with its required data or fixture; unavailable or unsupported capabilities are plainly identified.
  3. Every existing language and subject track has a recorded rubric result at its acceptance threshold, with non-applicable criteria and remaining gaps explicitly justified.
**Plans**: 5 plans

**Wave 1**
- [x] 05-01-PLAN.md: Track qualification contract and rubric checker
- [x] 05-02-PLAN.md: Authored walkthrough format, adapter and reference binding

**Wave 2**
- [x] 05-03-PLAN.md: Walkthroughs for the language tracks
- [x] 05-04-PLAN.md: Walkthroughs for the subject tracks

**Wave 3**
- [ ] 05-05-PLAN.md: Recompute the rubric and close Phase 5

### Phase 6: Desktop Workspace & Learner State
**Goal:** Learners can operate the desktop classroom confidently across its real lesson modes and continue their work without accidental execution or loss of saved evidence.
**Mode:** mvp
**Depends on**: Phase 1 and Phase 5
**Requirements**: UX-01, UX-02, STATE-01
**Success Criteria** (what must be TRUE):
  1. In every supported desktop lesson mode, the workspace identifies the current lesson, available actions, reading/runtime capability, readiness, and result location.
  2. Learners can operate the classroom with a keyboard and see clear focus and status cues; applicable contrast and accessibility checks pass.
  3. Navigation, lesson switching, test setup, viewing old results, and runtime restart preserve drafts, progress, and receipts; viewing history never re-executes code.
**Plans**: 4 plans

**Wave 1**
- [x] 06-01-PLAN.md: One workspace mode helper and honest mode wording

**Wave 2**
- [x] 06-02-PLAN.md: Fingerprinted draft backups with a restore choice
- [x] 06-03-PLAN.md: Keyboard, focus and contrast fixes

**Wave 3**
- [x] 06-04-PLAN.md: Desktop workspace browser gate
**UI hint**: yes

### Phase 7: Docker Runtime & Persistence Qualification
**Goal:** The local Docker classroom can be reproduced from the intended source revision, and supported runtime operations and lifecycle transitions work without losing learner data.
**Mode:** mvp
**Depends on**: Phase 5 and Phase 6
**Requirements**: RUN-01, RUN-02
**Success Criteria** (what must be TRUE):
  1. Every Docker image profile included in a release builds from the intended repository revision for its supported architectures and passes its documented startup and operation checks.
  2. Fresh setup, resume, stop, and restart pass in disposable Compose projects, and saved learner data remains intact across the tested lifecycle.
**Plans**: 4 plans

**Wave 1**
- [x] 07-01-PLAN.md: Bind every image to its source revision
- [x] 07-02-PLAN.md: Disposable lifecycle harness

**Wave 2**
- [ ] 07-03-PLAN.md: Two-architecture runtime qualification workflow

**Wave 3**
- [ ] 07-04-PLAN.md: Phase 7 evidence ledger

### Phase 8: Release Image Security
**Goal:** No image advances toward publication with an unresolved CVE reported by the applicable configured scan.
**Mode:** mvp
**Depends on**: Phase 7
**Requirements**: SEC-01
**Success Criteria** (what must be TRUE):
  1. Every image intended for publication has current configured scan results with no unresolved detected CVEs.
  2. An image with a detected CVE is remediated or rebuilt and rescanned; the resulting clean evidence identifies the image and release candidate it qualifies.
**Plans**: 4 plans

**Wave 1**
- [x] 08-01-PLAN.md: Digest-pinned image scan gate

**Wave 2**
- [x] 08-02-PLAN.md: Scan gate in the publish workflows
- [ ] 08-03-PLAN.md: Remediate the Python image family and postgres

**Wave 3**
- [ ] 08-04-PLAN.md: Remediate the native and SDK workers

### Phase 9: Code & Desktop Acceptance Gates
**Goal:** The overhaul has recorded repository and desktop-browser evidence for the relevant changed flows before any publication decision.
**Mode:** mvp
**Depends on**: Phase 6, Phase 7, and Phase 8
**Requirements**: QUAL-01, QUAL-02
**Success Criteria** (what must be TRUE):
  1. Focused automated tests, repository lint and type checks, and generated-content checks relevant to the changes pass.
  2. Desktop browser acceptance covers affected lesson and operation flows, including errors and recovery, at the supported desktop viewport without relying on mobile layouts.
**Plans**: 2 plans

Plans:
- [ ] 09-01-PLAN.md: Repository acceptance gate
- [ ] 09-02-PLAN.md: Desktop browser acceptance
**UI hint**: yes

### Phase 10: Verified Publication & Safe Closeout
**Goal:** A release is available only as a verified registry artifact, and finishing the work leaves learner data and unrelated services untouched.
**Mode:** mvp
**Depends on**: Phase 9
**Requirements**: REL-01, REL-02
**Success Criteria** (what must be TRUE):
  1. Source, tests, Docker images, image scans, registry target, and version tags are verified before publication; the published artifact is then pulled and smoke-tested.
  2. Test cleanup stops only DS60-owned services and containers, preserves learner volumes, and leaves unrelated containers running.
**Plans**: 2 plans

Plans:
- [ ] 10-01-PLAN.md: Publish and verify release 1.4.4
- [ ] 10-02-PLAN.md: Safe closeout

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Qualify 1.4.4 Guide & Python/SQL Walkthroughs | 5/5 | Verified, human UAT pending | - |
| 2. Catalog-wide Coverage Matrix | 1/1 | Complete | 2026-11-23 |
| 3. Lesson Foundations & Source Integrity | 4/4 | Complete | 2026-11-23 |
| 4. Worked Examples & Practice | 3/3 | Complete | 2026-11-23 |
| 5. Walkthroughs & Track Qualification | 4/5 | In Progress | - |
| 6. Desktop Workspace & Learner State | 4/4 | Verified, human UAT pending | - |
| 7. Docker Runtime & Persistence Qualification | 2/4 | In Progress | - |
| 8. Release Image Security | 2/4 | In Progress | - |
| 9. Code & Desktop Acceptance Gates | 0/2 | Planned | - |
| 10. Verified Publication & Safe Closeout | 0/2 | Planned | - |
