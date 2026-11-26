---
gsd_state_version: "1.0"
current_phase: 1
current_phase_name: Qualify 1.4.4 Guide & Python/SQL Walkthroughs
current_plan: 5
status: paused
stopped_at: Owner closeout; resume only for a new explicit task
last_updated: "2026-11-26T00:42:12Z"
last_activity: 2026-11-25
last_activity_desc: Owner closeout, opt-in CVE policy and fresh-machine handoff
state_head: 627a039676027250fd209401aa7bff79856a1ca1
progress:
  total_phases: 12
  completed_phases: 10
  total_plans: 44
  completed_plans: 44
  percent: 83
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-23)

**Core value:** Learners can understand, practice, run, and keep their work in any DS60 course without installing toolchains or losing learning state.
**Current focus:** Owner-requested closeout. All 44 plans are done and release
v2.1.1 is published. Start a new computer or assistant at `AGENTS.md` and
`docs/fresh-machine.md` on `main`. No automatic continuation is pending.
Progress and copy-paste takeover prompts: `docs/TAKEOVER.md`.

## Current Position

Phase: 1 (Qualify 1.4.4 Guide & Python/SQL Walkthroughs), awaiting human UAT
Current Plan: 5 of 5
Status: Closed out by owner; Phases 1 and 6 human walkthroughs remain unperformed, not claimed as passed
Last activity: 2026-11-25: CVE maintenance retired as a required gate; fresh-machine handoff prepared

Progress: [████████░░] 44 of 44 plans done (10 of 12 phases closed; Phases 1 and 6 await human UAT)

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 11 | 9 | - | - |

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
- Keep runtime builds, registry publication, and cleanup as separately verified gates.
- Owner decision 2026-11-25: CVE scanning and CVE-only fixes are opt-in. Historical
  Phase 8 and 11 scan requirements and exception-renewal tasks no longer apply.
  Keep functionality, image integrity, secret checks and trusted-local isolation.
- The coverage matrix (`curriculum/coverage-matrix.json`) is the work queue for Phases 3 to 5. Gaps never fail CI; only drift or missing cataloged files do.

### Pending Todos

- No automatic work is queued. Human walkthroughs for Phases 1 and 6 and the
  R11 clarity review remain optional future work, not completed acceptance.
- The historical 94 CVE exception proposals are retained for audit only;
  expiry does not require owner action or block ordinary releases.

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
| Security | Historical 94 CVE exception proposals | retired as required work by owner | 2026-11-25 | v2.1.1 |
| Images | Scientific profile images published from GitHub Actions (HARD-05) | resolved in Phase 11 | 2026-11-24 | v2.1.0 |
| Runtime | R worker compilers (HARD-04); R rebuilt on Debian 13 and Swift on Amazon Linux 2023 | resolved in Phase 11 | 2026-11-24 | v2.1.1 |
| Content | Templated lessons (HARD-02) and guide code execution in CI (HARD-03) | resolved in Phase 11 | 2026-11-24 | v2.1.0 |
| Quality | Flaky tests (HARD-06) and repository-wide em/en dash gate (HARD-07) | resolved in Phase 11 | 2026-11-24 | v2.1.0 |
| Cleanup | Local DS60 images and containers removed; learner volumes retained | completed | 2026-11-25 | v2.1.1 |

## Session Continuity

Last session: 2026-11-25 owner closeout
Stopped at: Closed out; begin with docs/fresh-machine.md for a new explicit task
Resume file: None
