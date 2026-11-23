# Architecture Patterns

**Domain:** Local, desktop-first multi-subject programming and data-science classroom  
**Researched:** 2026-11-23  
**Research scope:** Integrating and improving current tracks without replacing DS60's architecture

## Recommended Architecture

Keep the existing local Python modular monolith, shared `/classroom` browser shell, independent curriculum loaders, fixed runtime-profile workers, and local learner-state stores. Improve the experience through the contracts between these layers - not by collapsing subject catalogs, turning profiles into curriculum categories, or introducing a new application per language.

```text
Maintained subject sources
  ├─ legacy lessons/catalog inputs
  ├─ authored module plans, track + lesson manifests
  └─ tutorial-specific manifest and coverage
          │ validate identities, prerequisites, artifacts, mode and profile
          ▼
Catalog loaders ── normalized learner-facing views ── Shared /classroom UI
          │                                              │
          │ resolve lesson + actual capabilities         ├─ guide / source / notes
          ▼                                              ├─ progress and drafts
Application services ── fixed runtime adapter             └─ saved observations
          │                        │
          │                        ▼
          │             Prepared Docker worker profile
          │
          └──────────── Local .learning state
                        + named Docker volumes

Maintained sources → subject generators/normalizers → static guide/readers
```

The legacy `Catalog` and authored `ModuleCatalog` are intentionally separate registration and persistence contracts. `ClassroomService.index()` composes their learner-facing views, while the shared browser interface presents common navigation, saved-work conventions, and lesson workspaces. The statistics tutorial has its own manifest contract. Preserve these distinctions while standardizing the experience that learners encounter.

The core design rule is **subject says what is learned; lesson mode and runtime profile say how it is learned and whether/how it runs**. Every route should report real lesson capabilities. Reading-only chapters, opaque browser previews, legacy pads, and worker-backed code runs are different modes; do not make a run button, a profile, or an evidence type appear universal when it is not.

### Component Boundaries

| Component | Responsibility | Integration contract |
|-----------|----------------|----------------------|
| Authored curriculum | Teaching source, stable lesson IDs, prerequisites, mode, artifacts, and references | Keep current source-of-truth per track; identify its loader and generator before editing |
| Catalog loaders | Validate routes and expose authored lessons, variants, prerequisites, and admitted profiles | Planned work is not authored/runtime-ready; only complete validated artifacts enter learner routes |
| Shared classroom and application services | Present all registered subjects and coordinate lesson views, drafts, runs, progress, and receipts | Keep subject-specific content metadata while reusing common navigation and workspace behaviors |
| Rendering/build pipeline | Render safe classroom lessons and checked-in static readers from maintained sources | Regenerate in documented order; generated HTML is output, not the place to author |
| Runtime adapters and workers | Execute only fixed, reviewed profile operations with bounded input/output and cleanup | Bind lesson metadata to registered profiles; manifests do not define shell commands |
| Learner-state stores | Persist progress, drafts, notes, run/observation receipts, and module job state | Preserve stable identity and store boundaries; reading a receipt never replays execution |
| Local delivery | Start the classroom and selected prepared services through Docker Compose and launcher scripts | Keep learner data in the established named volumes/state paths, not disposable container layers |

### Data Flow

1. **Find the maintained route.** Inspect the current catalog and the subject's authoring instructions. Python/SQL/bridge legacy lessons, modern module tracks, founding module plans, and the Statistics/ML book do not share one authoring manifest. A route's planned metadata is not evidence that lesson artifacts exist.
2. **Preserve identity and choose the existing contract.** Prefer improving the current lesson and stable ID. Register prerequisites and variants against existing IDs. Choose the subject's current loader contract rather than migrating it to a new generic format for consistency's sake.
3. **Complete teaching artifacts before admission.** Keep guide, learner source, solution/explanation, fixtures and verification evidence distinct. The practice and tutorial contracts differ: practice requires exercises and separate explanations; tutorial tracks expose complete worked sources without an artificial hidden-answer gate.
4. **Expose honest capabilities.** The catalog binds each authored lesson to a registered runtime profile or `reading`; application code routes that profile to a fixed adapter. Browser preview, local legacy execution, worker verification, and self-reported completion must remain distinguishable in UI and stored history.
5. **Regenerate shared outputs.** Run the subject's documented generator where applicable; then run the reviewed prose normalization and TeX compilation stages as needed, and regenerate both course guide and lesson readers. Run the corresponding `--check` commands. Never patch generated classroom/static HTML as the source of a fix.
6. **Verify the complete learner path.** Check catalog and prerequisite validation, rendered lesson and navigation, source/variant behavior, realistic run or reading flow, draft save/reload, and prior-result viewing. Test actual prepared runtime behavior separately from metadata admission. Use disposable project state for Docker/browser integration checks and retain learner volumes.
7. **Qualify delivery and persistence.** Verify the local launcher resumes the intended project and profile selection, that browser mutations target the correct local service, and that data survives container recreation. Do not infer persistence from an application unit test alone.

## Patterns to Follow

### 1. Stable identity with per-track authoring adapters
**What:** Keep authored sources and native contracts intact; loaders translate validated lesson identity, prerequisites, artifacts, mode, and profile into a common learner-facing view.  
**When:** Improving existing lessons or extending any current subject.  
**Why:** This standardizes navigation and behavior while preserving legacy IDs, existing plans, tutorial-specific structures, and author workflows. Track identity should never be inferred from language or worker profile alone.

### 2. Shared shell, capability-driven lesson workspace
**What:** The single `/classroom` interface uses catalog-derived capabilities to show the appropriate reading, practice, preview, or run workflow. Subject labels and theme keys identify the subject, but color is not the only signal. Repeated controls keep consistent labels, behavior, focus handling, and keyboard operation.
**When:** Refining the directory, lesson workspace, themes, navigation, and result presentation.
**Why:** A shared shell gives learners predictable interaction across tracks without pretending every lesson can execute the same way. WCAG 2.2 recommends the current standard for web content and defines testable accessibility criteria; DS60's authoring guide already requires plain language, non-color identification, and accessible content.

### 3. Profile-to-fixed-operation runtime boundary
**What:** Lesson metadata names an allowlisted profile and a constrained artifact contract; trusted application adapters choose fixed worker operations, limits, and cleanup. Read-only and browser-only modes remain explicit.  
**When:** Qualifying or extending any language/runtime path.  
**Why:** A profile indicates prepared tooling, not full lesson readiness. It preserves the established execution boundary and avoids arbitrary commands in content metadata.

### 4. Source-bound, non-replaying evidence
**What:** Keep drafts, progress markers, run results, worker verification, browser observations, and learner-confirmed completion as separately typed state, each tied to stable lesson/source identity. Displaying old results reads stored evidence; it does not rerun code or replace the current draft.  
**When:** Changing workspace transitions, history, completion indicators, or persistence.  
**Why:** This lets learners resume safely and prevents the UI from overstating what a result proves. Preserve current separate stores and atomic/locked update mechanisms rather than inventing a unified status flag.

### 5. Persist learner state outside replaceable containers
**What:** Retain the `.learning` state boundary and named Docker volumes for learner data; make the launcher and tests explicit about project identity and non-destructive lifecycle operations.  
**When:** Modifying Compose services, startup/resume, image rebuilds, backup, or browser persistence tests.  
**Why:** Docker documents volumes as persisting outside an individual container's lifecycle. DS60's local product model depends on keeping state through app/worker recreation, not baking it into image layers.

## Integration Order for a Cross-Track Quality Pass

1. **Inventory routes and capabilities from current loaders.** Generate the live catalog and module reports; group by subject, learning mode, and profile. Do not rely on an old lesson count or treat each profile as a subject.
2. **Set shared learner-experience criteria.** Apply the current guide contract to clarity, prerequisites, observable outcomes, examples, errors, exercises/solutions or complete tutorial examples, accessibility, and actual run instructions. Use Python/SQL as a reference, not as the only target.
3. **Improve content at its maintained source.** Follow the subject's `AGENTS.md` and authoring generator. Preserve canonical IDs, source integrity, variants, route structure, and separate teaching artifacts.
4. **Register and validate at the owning boundary.** Validate prerequisites, artifact paths, learning mode and profile admission. Add a reviewed backend adapter only if the existing runtime cannot satisfy the lesson contract; do not create a new worker/image merely to gain a common UI.
5. **Regenerate shared and static presentations.** Run the subject generator, scoped prose normalization, TeX build when applicable, course guide and reader builders, then their drift checks and rendering gates.
6. **Test by layer, then end-to-end.** Start with contract/content tests and relevant unit tests; test changed runtime profiles against prepared, disposable targets; exercise browser navigation, variant switching, drafts, reload, history, and saved results; then run grouped repository and release gates required by the change.
7. **Verify local Docker lifecycle and state preservation.** Exercise startup, resume, readiness, selected profile behavior, and the relevant worker/browser route using an explicitly disposable project. Check saved work after restart/recreation. Clean only DS60-owned test resources; never remove learner volumes as incidental test cleanup.

This order isolates authoring and catalog mistakes before expensive runtime/browser checks, while still requiring real integration evidence for every changed execution path.

## Anti-Patterns to Avoid

### Collapsing catalogs or replacing all lesson sources with one schema
**What:** Move legacy curriculum, founding plans, additive tracks, and tutorial books into a newly unified content registry to make presentation consistent.  
**Why bad:** Their validation, generation, lesson lifecycle, and learning-mode contracts differ; a migration risks stable identities and creates broad unrelated churn.  
**Instead:** Normalize only the learner-facing view and shared workspace behaviors. Keep track-specific authoring and registration boundaries.

### Treating plan entries or profile availability as a runnable lesson
**What:** Show a lesson as ready because a plan row exists, its language is highlighted, or a worker image is installed.  
**Why bad:** The catalog deliberately distinguishes planned from authored; runtime availability alone does not establish complete artifacts, correct operation, or successful qualification.  
**Instead:** Require the complete authored bundle, validated profile binding, and appropriate lesson-specific/runtime evidence before exposing that capability.

### Making every subject follow practice or every lesson have Run
**What:** Require exercises/solution gating for tutorial books, or add pretend execution to reading-only and external-system lessons.  
**Why bad:** It changes instructional intent and can falsely claim verification.  
**Instead:** Preserve validated practice/tutorial modes and use explicit reading, preview, worker, or externally prepared workflow capabilities.

### Merging all learner state into a generic completion record
**What:** Treat visited, read, self-reported complete, browser-observed, and worker-verified lessons as equivalent; replay history automatically.  
**Why bad:** It loses source context, overwrites current work, and represents weak evidence as verified learning or execution.  
**Instead:** Retain separate state stores and typed evidence; always bind result details to their source/lesson identity.

### Testing persistence by deleting or replacing learner data
**What:** Use a normal classroom project or remove volumes to make Docker tests repeatable.  
**Why bad:** It risks irreversible loss and violates the local classroom's resume contract.  
**Instead:** Use an explicitly disposable Compose project and test fixtures; retain its test data only until bounded cleanup of DS60-owned resources, without pruning volumes globally.

## Scalability Considerations

DS60 is a local single-classroom product, not a hosted multi-tenant service. The table describes the supported design and the boundary where scope would change.

| Concern | One local learner (supported) | 100 concurrent learners | 1M concurrent learners |
|---------|------------------------------|-------------------------|------------------------|
| Execution | Current controller and per-worker single-active-job limits; keep bounded profiles | Current rejection-on-active-run is not a fairness/queue policy; would need an explicit queue and per-user/resource isolation before expansion | Outside current product architecture; requires separately designed service isolation and fleet scheduling |
| State | Local `.learning` stores and Docker volumes, with locks/atomic replacement and explicit project identity | Shared filesystem semantics and user ownership would need requalification; do not assume local locks imply distributed coordination | Requires a separately designed multi-tenant persistence architecture and operational recovery model |
| Catalog/UI | One local catalog view and shared browser session | Could retain the view model, but would need authenticated user/session and tenant boundaries not present in the local product | Hosted identity, availability, and delivery are out of scope and cannot be reached by simply scaling the current server |
| Delivery | Prepared local Docker Compose profiles and resume workflow | Local launcher and named-volume behavior do not provide hosted deployment orchestration | New product and threat model required; do not widen the trusted-local-code boundary incrementally |

Do not optimize for these larger scales in the current overhaul. If shared hosting becomes an approved requirement, treat it as a new architecture and security decision rather than removing the current single-active-job guard.

## Sources

### Repository evidence

- [Project scope and constraints](../PROJECT.md); local desktop classroom, all existing tracks, Docker, saved-work requirements.
- [Codebase architecture map](../codebase/ARCHITECTURE.md) and [stack map](../codebase/STACK.md); current layers, APIs, catalogs, profiles, stores, and delivery.
- [`docs/repository-tour.md`](../../docs/repository-tour.md); lesson flow, maintained/generated/private artifacts, and source map.
- [`docs/content-authoring.md`](../../docs/content-authoring.md); shared lesson contract, authoring order, modes, accessibility, generators, and validation.
- [`docs/implementation/ADDING_A_MODULE.md`](../../docs/implementation/ADDING_A_MODULE.md); route metadata, artifact admission, profile boundaries, and end-to-end qualification.
- [`docs/implementation/CHECKPOINT.md`](../../docs/implementation/CHECKPOINT.md); current shared UI, route types, prepared runtimes, and volume/resume constraints.
- [Codebase concerns](../codebase/CONCERNS.md); step-through test gap, trusted-local-code boundary, and single-active-job limit.

### Authoritative external references

- [Docker Compose application model](https://docs.docker.com/compose/intro/compose-application-model/); services, networks, volumes, and project isolation.
- [Docker volumes](https://docs.docker.com/engine/storage/volumes/); volume lifecycle is independent of an individual container; supports the recommendation to preserve named learner-state volumes.
- [Python 3.12 `os.replace`](https://docs.python.org/3.12/library/os.html#os.replace); documents replacement behavior and atomicity on POSIX when successful; this supports, but does not replace, DS60's locking, validation, and whole-record update logic.
- [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/); current W3C accessibility recommendation for consistent, operable web content; use it alongside DS60's existing classroom-specific accessibility checklist.

**Confidence:** High for the repository-specific architecture and integration order (direct source documentation reviewed). External-source findings are linked to official documentation; the research provider's confidence classifier rated web-fetched sources LOW, so they support rather than determine the recommendations.
