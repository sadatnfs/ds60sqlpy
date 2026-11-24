---
gsd_state_version: "1.0"
current_phase: 11
current_phase_name: Post-release Hardening & Content Completion
current_plan: 0
status: executing
stopped_at: Phase-11-executing-wave-1
last_updated: "2026-11-24T21:30:06.000Z"
last_activity: 2026-11-24; Phase 11 planned (8 plans); executing wave 1.
state_head: 2c3c3f8ecefde5a26325f6f49f22238c8b5b147a
progress:
  total_phases: 12
  completed_phases: 9
  total_plans: 43
  completed_plans: 35
  percent: 81
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-23)

**Core value:** Learners can understand, practice, run, and keep their work in any DS60 course without installing toolchains or losing learning state.
**Current focus:** Phase 11 post-release hardening: security, templated lessons, guide code execution, R compilers, scientific image publishing, flaky tests and dashes

## Current Position

Phase: 11 (Post-release Hardening & Content Completion): EXECUTING
Current Plan: 0
Total Plans in Phase: 8
Status: All 35 plans have summaries. Phases 2, 3, 4, 5, 7, 8, 08.1, 9 and 10 verified (passed). Phases 1 and 6 verified human_needed (first-time learner walkthrough). Release v2.0.0 is a published, non-draft GitHub release tagged at a4354ff8; every local DS60 image, container and network was removed, and learner volumes were kept.
Last activity: 2026-11-24; Phase 11 added at the owner's request (security fixes, lesson template text, guide code execution, R compilers, scientific image publishing from Actions, flaky tests, em/en dashes).

Progress: [████████░░] 81% of plans (9 of 12 phases closed; 2 await human UAT; Phase 11 planning)

## Performance Metrics

**Velocity:**
- Total plans completed: 1
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: Not established

**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | multi-session | 3 tasks | 5 files |
| Phase 01 P02 | 30min | 2 tasks | 1 files |
| Phase 01 P03 | 2h | 3 tasks | 5 files |
| Phase 01 P04 | 40m | 2 tasks | 4 files |
| Phase 01 P05 | 3sessions | 3 tasks | 12 files |
| Phase 02 P01 | 1 session | 6 tasks | 10 files |

## Accumulated Context

### Decisions

- Phase 1 qualifies the unfinished 1.4.4 checkpoint; it does not claim that the broader overhaul is complete or published.
- All existing language and subject tracks are in scope. Python and SQL are a quality reference and checkpoint, not a scope boundary.
- Preserve desktop-only delivery, local Docker and trusted-local-code boundaries, stable lesson IDs, learner state, and capability distinctions.
- Keep runtime builds, image scans, registry publication, and cleanup as separately verified gates.
- The coverage matrix (`curriculum/coverage-matrix.json`) is the work queue for Phases 3 to 5. Gaps never fail CI; only drift or missing cataloged files do.

### Pending Todos

- Human UAT: a first-time learner walkthrough for Phases 1 and 6.
- Owner review of the 276 pending-owner CVE exceptions before their earliest expiry (2026-12-23).

### Blockers/Concerns

- The project owner approved the v1 requirements on 2026-11-23.
- Verify the Docker Hub target immediately before any publication; do not stop unrelated containers or remove learner volumes.
- Browser gates run in a disposable classroom project with the containerized Playwright runner; never use the learner project `ds60-classroom` or its volumes.

### Roadmap Evolution

- Phase 08.1 inserted after Phase 8: Unslop classroom UI chrome per heydamir/unslop (user request); lesson content untouched (URGENT)
- Phase 11 added after release 2.0.0: Post-release Hardening & Content Completion (owner request; absorbs the deferred security, scientific image, R runtime, templated content, flaky test and dash items)

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| UAT | Phases 1 and 6 first-time learner walkthrough | human_needed | 2026-11-24 | v2.0.0 |
| Security | 276 pending-owner CVE exceptions (earliest expiry 2026-12-23) | owner review | 2026-11-24 | v2.0.0 |
| Images | Scientific profile images are not published to Docker Hub | deferred | 2026-11-24 | v2.0.0 |
| Runtime | R worker ships without compilers; spark-tmb on OpenSSL 3.5; standalone packages on Spark 4.0.1 | deferred | 2026-11-24 | v2.0.0 |
| Content | Templated stub lessons and guide code that is not executed in CI | deferred | 2026-11-24 | v2.0.0 |
| Quality | 6 flaky tests (including ballista); 879 repo-wide em/en dash hits outside the changed files | deferred | 2026-11-24 | v2.0.0 |
| Caches | About 60.63 GB of BuildKit cache and 10 GB in ~/.cache/ds60sqlpy kept locally | owner decision | 2026-11-24 | v2.0.0 |

## Session Continuity

Last session: 2026-11-24T21:30:06.000Z
Stopped at: Phase-10-complete
Resume file: None
