# Repository tour and upgrade rationale

## What we built before this upgrade

The Git history starts with the Python and SQL course in January 2026. The major July 24 to July 31 work expanded the teaching material, added the engineering bridge and named professional modules, introduced catalog-based validation and separate solutions, and built the portable HTML learning portal. The final July commits concentrated on PowerShell 5.1 compatibility, Windows interpreter discovery, diagnostics, and rendering authoring markers correctly.

The starting snapshot for this review was `3ed0a31`. It contained 154 cataloged lessons: 70 Python, 72 SQL, and 12 bridge. It was already a large curriculum, with complete numbered cores, more than brief answer files, 122 notebooks, a safe guided SQL notebook generator, an authenticated local launcher, and substantial tests. The canonical Python 3.12 environment passed 455 tests, with two PowerShell checks skipped because that parser was unavailable on the review host.

This upgrade preserves that work. It adds a gentler beginner sequence and advanced correctness practice, then turns the materials into a usable coding application with an optional Codex tutor. It does not renumber the historical days or treat a browser checkbox as proof of mastery.

## Sources of truth and data flow

```text
lesson guides + learner artifacts + separate solutions
                       |
              catalog_builder.py
                       |
            curriculum/catalog.json
             /         |         \
       static readers  |     prerequisite planner
                       |
              CoachingService
              /             \
     browser learning lab   optional stdio MCP tutor
       |             |             |
   PadRunner   evidence/progress    read-only by default
       |
  native Python or local disposable PostgreSQL
```

The catalog records stable identity, prerequisites, level, time estimate, dependency group, network behavior, and artifact paths. Named route definitions specify terminal goals and derive the route from that graph. The course guide and lesson readers are generated views. They are rebuilt from source rather than edited by hand.

## Main components

| Location | Responsibility |
| --- | --- |
| `python/ds-60day/` | Historical Python/data-science notebooks, companion guides, and two solution formats |
| `sql/postgres-60day/` | Historical SQL scripts, seed/verification scripts, companion guides, and separate SQL/Markdown solutions |
| `bridge/` | Python/PostgreSQL engineering exercises and fake-backed behavior tests |
| Each track's `professional/` directory | Stable named foundation, professional, advanced, and specialization modules |
| `src/ds60sqlpy/catalog*.py` | Deterministic catalog generation, loading, and learner-facing ordering |
| `study_plan.py` | Topological goal planning, shared prerequisite removal, ready lessons, and time arithmetic |
| `coaching.py`, `progress.py` | Learner evidence and progress operations shared by the application and MCP |
| `lab.py`, `execution.py` | Explicit coding app, authenticated actions, bounded Python/SQL backend runs |
| `portal.py`, `lesson_reader.py` | Existing safe reading/navigation portal, fixed editor launches, and generated HTML |
| `desktop.py`, `scripts/build_app.py` | Frozen/native entry point, persistent workspace initialization, and allowlisted course packaging |
| `mcp_server.py` | Optional SDK-backed local tutoring tools, resources, prompts, and explicit write/reveal boundaries |
| `scripts/audit_*.py` | Practice-count and teaching-depth gates; these supplement semantic review |
| `docs/setup/` | Windows/macOS/Linux, PostgreSQL, notebook, and offline setup |
| `.github/workflows/` | Core/platform/notebook/SQL checks and native/Docker application build definitions |

## Learning gaps addressed

The early SQL sequence previously moved straight into the larger training schema. The new three-lesson on-ramp lets learners read tiny tables, state row grain, predict `NULL` and ordering behavior, and build or debug a query before that jump. Four inserted Python labs build confidence in tracing, debugging, cleaning records, and producing an auditable first investigation.

Advanced additions focus on mechanisms that broad topic surveys often leave under-practised: exact values and calendar boundaries; deployment-shaped group/time evaluation; restarting a file pipeline without false atomicity claims; duplicate-aware reconciliation and join fanout; compound cursors and bounded batches; concurrent visibility and optimistic version checks; and an integrated data-product incident review with independent fixtures.

Every addition has a learner artifact, deep guide, executable reference, and explanatory solution. Practice moves from prediction through implementation and diagnosis to transfer. New lessons use a separate practice registry; the historical baseline remains unchanged. Structural headings, link checks, topic-specific verification contracts, and runnable behavior are all checked separately.

## Application design decisions

The course now has three complementary delivery modes. Static HTML provides a complete offline reading library. The local coding application adds a guided route, code pads, transcripts, figures, saved evidence, and explicit solution comparison. The optional MCP server lets Codex use those same lesson and prerequisite operations while retaining a read-only default and no arbitrary code execution.

The native executable bundles the application runtime and course assets; its backend uses the learner's installed Python/PostgreSQL. Docker packages the backend environment and database for a consistent browser experience. Native build evidence is specific to the actual build platform. A Dockerfile or hosted workflow definition is not evidence that another operating system has been executed successfully.

The coding application is a personal trusted-code programming environment. It has authenticated local requests, bounded runs, exact course-database routing, and separate saved-work storage. It is not presented as a general security sandbox. The original reading portal keeps its smaller fixed launch allowlist. Live database examples remain distinct from fake-backed tests, and a saved completion remains distinct from automatically graded mastery.

## Review scope and limits

Parallel agents inventoried and inspected all historical lesson artifacts, with notebook-aware extraction and targeted semantic reads of guides, exercises, references, and solutions. Shared runtime, bootstrap, catalog, security boundaries, tests, history, generated views, and packaging were reviewed by their responsible agents. Generated HTML was checked against its source rather than treated as an independent authored curriculum. Large repeated artifact families also received structural and behavioral gates.

This is a whole-repository onboarding and targeted upgrade, not a claim that every word was independently pedagogically validated or every heavy model ran on every platform. The checks distinguish parsed structure, local unit behavior, actual PostgreSQL execution, browser interaction, native bundle execution, and unavailable platform/container evidence. Current concrete results belong in [validation](validation.md).

For a learner, start with [learning paths](learning-paths.md). For a contributor, follow [content authoring](content-authoring.md) and [CONTRIBUTING](../CONTRIBUTING.md). For the new delivery system, see [application builds](offline-app.md) and [MCP tutoring](mcp-tutor.md).
