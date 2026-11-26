# DS60 Classroom Overhaul

## What This Is

DS60 Classroom is a local, desktop-first browser classroom for learning programming, data science, statistics, machine learning, and systems through written lessons, examples, exercises, and prepared Docker runtimes. This project will make the existing classroom and its learning content clear, reliable, and well-furnished for beginners and experienced learners across every current language and subject track. Python and SQL provide a quality reference, not a limit on the work.

## Core Value

Learners can understand, practice, run, and keep their work in any DS60 course without installing toolchains or losing learning state.

## Requirements

### Validated

- ✓ A single local browser classroom serves the existing course catalog; published baseline, 1.4.3.
- ✓ Learners can use prepared Linux Docker runtimes and preserve local drafts, progress, and run records; published baseline, 1.4.3.
- ✓ Python and SQL are the instructional quality reference for this overhaul; confirmed by the project owner.

### Active

- [ ] Complete and qualify the checkpointed classroom manual, optional tour, and Python/SQL code and solution walkthroughs.
- [ ] Improve the desktop classroom's navigation, lesson operation, exercises, and run experience without losing drafts or saved results.
- [ ] Review and improve the content and learning experience for every existing language and subject track, using clear, accurate, practical instruction at least as strong as the Python and SQL reference.
- [ ] Verify supported Docker images, runtime behavior, startup, saved work, and release distribution through reproducible tests.
- [x] Make CVE scanning and CVE-only remediation opt-in, without weakening classroom functionality or image-integrity checks (owner closeout, 2026-11-25).
- [ ] Gate changes with focused automated tests, repository quality checks, and bounded desktop browser review.
- [ ] Publish a release only after its code, image, and registry checks pass; stop DS60-owned test containers when the work is finished.

### Out of Scope

- Mobile-specific interface design; the owner specified desktop as the target.
- Turning the local classroom into a shared hosted service or weakening the trusted-local-code boundary; this overhaul preserves the local Docker product model.
- Deleting learner data or volumes as part of testing or cleanup; saved learner work must remain intact.
- Adding new subject families as a substitute for improving the courses already in the catalog; existing language and subject tracks are the current scope.

## Context

- Current handoff: release v2.1.1 is published; all 44 implementation plans are
  complete. The owner closed this overhaul on 2026-11-25. Start new-machine
  work from `main`, `AGENTS.md` and `docs/fresh-machine.md`; no previous chat or
  machine-local runtime state is needed. Historical context below records the
  initial checkpoint, not an instruction to resume it.
- The project is a brownfield Python application with a static HTML, CSS, and JavaScript classroom, a broad multi-subject curriculum, and profile-specific Docker worker images.
- The repository's GSD codebase map is in `.planning/codebase/`. Product and architecture references include `PRODUCT.md`, `AGENTS.md`, `docs/repository-tour.md`, and `docs/implementation/CHECKPOINT.md`.
- The current checkout is `checkpoint/classroom-guide-step-through-2026-11-20` at the checkpoint commit `a7b9bee8`. It contains the manual, tour, UI refinements, and an initial Python/SQL step-through implementation.
- The checkpoint is unfinished qualification work, not release 1.4.4. The step-through backend needs automated coverage, PostgreSQL behavior needs disposable integration verification, and the desktop browser acceptance and release gates remain incomplete.
- The user has authorized Git pushes and Docker build/test work. Docker Hub was recreated as a public empty repository before the pause; verify its current state again before any release publication.
- At resume, the four running containers were identified as unrelated Awesome Copilot MCP services. The DS60 Compose project was exited. Do not stop unrelated containers; clean up only DS60-owned test services and containers.

## Constraints

- **Platform**: Design and verify for desktop browsers; do not spend scope on mobile-specific layouts.
- **Runtime**: Preserve local Docker delivery, the existing course/profile boundaries, and offline classroom assets.
- **Learner state**: Keep drafts, progress, receipts, and volumes intact across UI and runtime changes.
- **Content quality**: Preserve accurate source material and stable lesson identities; make improvements evidence-based and testable.
- **Image security**: CVE scans and CVE-only fixes are opt-in, not publication gates. Preserve runtime qualification, secret checks, digest/checksum validation and local isolation. Do not claim vulnerability-free images.
- **Release safety**: Separate ordinary code changes from pushing to `main` and publishing images. Verify all release gates and the Docker Hub target before publishing.
- **Cleanup**: Stop DS60-owned test containers at completion, but do not stop unrelated services or remove learner volumes.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Track the whole DS60 overhaul, with checkpoint qualification first | The owner asked to continue the pending beginner-experience work and improve the full product | Accepted |
| Improve all existing language and subject tracks now | The owner clarified that improvements should not stop at Python and SQL | Accepted |
| Use Python and SQL as a quality reference, not as exclusive scope | The original near-term work targets these tracks, while the owner expanded the overhaul to all languages | Accepted |
| Keep the target desktop-only | Mobile-specific work is not wanted for this classroom | Accepted |
| Preserve the local Docker model and all learner state | This is the established product and its saved work is essential | Accepted |
| Require clean image vulnerability scans before publication | Original overhaul requirement | Superseded 2026-11-25 |
| Prioritize a working classroom; make CVE scans and CVE-only fixes opt-in | Owner explicitly retired the automatic CVE maintenance workload | Accepted 2026-11-25 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Move verified requirements to Validated and record the phase.
2. Move invalidated requirements to Out of Scope with the reason.
3. Add newly approved requirements and record decisions.
4. Confirm the project description and current focus remain accurate.

**After each milestone** (via `/gsd-complete-milestone`):
1. Review the project description, core value, requirements, context, constraints, and decisions.
2. Update the context with the verified product and release state.

---
*Last updated: 2026-11-25 at owner-requested closeout*
