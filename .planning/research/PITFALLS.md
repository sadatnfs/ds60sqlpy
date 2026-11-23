# Domain Pitfalls

**Domain:** Multi-language educational programming classroom with local Docker runtimes  
**Researched:** 2026-11-23  
**Confidence:** MEDIUM overall — repository risks are grounded in the supplied planning/codebase maps; external guidance is from current official documentation and established computing-education research. No application tests, browser checks, or Docker builds were run for this research.

## Critical Pitfalls

### Pitfall 1: Lessons teach a plausible story, not a correct and learnable model

**Evidence class:** General researched risk; no content-level defect was established by the repository map.

**What goes wrong:** Lessons can contain technically true fragments but omit prerequisites, silently rely on vocabulary or setup taught later, or teach a simplified rule that fails on the next exercise. Learners then copy patterns without developing a mental model. In an overhaul, editing prose and code examples independently can also make the explanation, output, exercise, and solution disagree.

**Why it happens:** Large curricula often have several authors, formats, and generations of material. Technical review alone does not establish that a novice can follow the sequence. Introductory programming research identifies novice mental models, misconceptions, and cognitive load as recurring instructional concerns; the ACM/IEEE-CS/AAAI CS2023 report provides a current curriculum reference, but it does not certify DS60 lessons.

**Warning signs:**
- A lesson uses terms, syntax, files, tools, or mathematical concepts before defining or linking prerequisites.
- Examples skip intermediate reasoning, or a code/output change is unexplained.
- “Expected output” or solution text differs from what the shipped runtime produces.
- A lesson objective cannot be checked by its exercise or assessment.
- A content-only review reports completeness without a learner-level walkthrough.

**Prevention:** For each lesson, record measurable outcomes, prerequisites, worked examples, misconceptions to surface, exercises, and expected results. Walk a beginner path from the previous lesson; execute examples in the target runtime; have an independent reviewer verify the explanation and solution. Treat simplifications as explicit scope limits and revisit them where they cease to hold. Use CS2023 as a competency reference, not as proof that an individual lesson is effective.

**Likely phase:** Curriculum/content audit and authored lesson revision, after the checkpoint’s Python/SQL step-through qualification.

**Sources:** [ACM/IEEE-CS/AAAI CS2023 curriculum](https://csed.acm.org/) (endorsed 2024); [Cambridge Handbook of Computing Education Research, “Novice Programmers and Introductory Programming”](https://www.cambridge.org/core/books/cambridge-handbook-of-computing-education-research/novice-programmers-and-introductory-programming/0CEDFE1B121198D3FB5F1541EBE3DCAD).

### Pitfall 2: “Parity” means equal file counts, not equivalent learning

**Evidence class:** Scope-derived risk, not a confirmed repository content defect.

**What goes wrong:** Some languages/tracks receive carefully scaffolded explanations and tested exercises while others only gain superficial rewrites, examples, or navigation. A single uniform lesson template can also erase language-specific concepts and prerequisites. Learners experience uneven depth even though the catalog looks complete.

**Why it happens:** DS60’s stated scope includes every existing language and subject track, while its architecture deliberately keeps legacy lessons/catalogs and authored modules/plans distinct. Those boundaries make blanket edits and counts a poor proxy for instructional equivalence. The supplied maps do not establish that current parity has been measured or that any track is currently inferior.

**Warning signs:**
- Acceptance criteria count lessons or files but do not compare outcomes, prerequisite chains, exercise coverage, or runtime behavior.
- A track is declared “done” because its catalog loads, even though its lessons are planned, unauthored, or not executable.
- One language’s examples, exercise difficulty, or solutions are copied without adapting idioms or prerequisites.
- The same concepts recur with inconsistent names or assumptions between tracks.

**Prevention:** Build a track-by-track matrix of learning outcomes, prerequisites, worked examples, exercise types/difficulty, solution quality, and runnable verification. Compare equivalence at the outcome level, not syntax or lesson length. Preserve appropriate language-specific teaching, explicitly identify tracks with no meaningful counterpart, and validate both catalog families and authored/runtime bindings. Make gaps visible rather than filling them with placeholder material.

**Likely phase:** Cross-curriculum inventory and language/subject parity work; repeat the matrix as a completion gate for each track.

**Sources:** [CS2023 knowledge areas and curricular practices](https://csed.acm.org/); repository context and boundaries in `.planning/PROJECT.md` and `.planning/codebase/ARCHITECTURE.md`.

### Pitfall 3: SQL walkthroughs confidently explain a parser’s guess

**Evidence class:** **Observed repository risk.** `.planning/codebase/CONCERNS.md` reports a new, large custom SQL tokenizer/planner and response builder without matching automated tests; the project context says its PostgreSQL behavior still needs disposable integration verification. This is an unverified edge-case risk, not a confirmed incorrect trace.

**What goes wrong:** A walkthrough can reject valid SQL, label a statement incorrectly, attribute a row/result to the wrong clause, or show an execution story that does not match PostgreSQL. Quoted names, string literals, comments, nested expressions, CTEs, set operations, multi-command input, and database-specific behavior are common fault lines. A guessed or partial trace is especially harmful because it teaches a false execution model.

**Why it happens:** SQL is a language with lexical and grammatical structure, not a reliable sequence of keywords. PostgreSQL documents tokens, comments, quoted identifiers/literals and a broad `SELECT` grammar, including CTEs, set operations, ordering/limits and locking clauses. A hand-built recognizer can be valuable for an explicitly bounded subset, but must not silently imply full dialect coverage.

**Warning signs:**
- Tests cover only uncomplicated `SELECT` statements or assert response shape without checking trace semantics.
- Comments, dollar-quoted strings, quoted identifiers, nested queries, CTEs, `UNION`/`INTERSECT`/`EXCEPT`, aliases, or cursor positions are missing from the test matrix.
- Unsupported or ambiguous input produces a plausible explanation instead of a clear limitation.
- A walkthrough output is accepted without comparison to the exact PostgreSQL version/runtime.
- Query display order is treated as guaranteed when the query has no explicit `ORDER BY`.

**Prevention:** First test tokenizer/planner/response functions table-by-table, including malformed and unsupported cases. State the supported SQL subset and fail closed or fall back to ordinary execution when a reliable explanation is unavailable. Verify read-only behavior, ordering assumptions, result rows, cancellation/timeouts, and output bounds against a disposable PostgreSQL instance matching the supported runtime (the mapped CI database is PostgreSQL 17). Test the browser request/response contract separately. Do not equate “database accepted it” with “the teaching trace is accurate.”

**Likely phase:** Immediate checkpoint qualification for step-through; deeper SQL grammar and dialect work only where the audit finds an intentional need.

**Sources:** `.planning/codebase/CONCERNS.md`; [PostgreSQL 17 lexical structure](https://www.postgresql.org/docs/17/sql-syntax-lexical.html); [PostgreSQL 17 SELECT](https://www.postgresql.org/docs/17/sql-select.html); [PostgreSQL 17 transaction modes](https://www.postgresql.org/docs/17/sql-set-transaction.html).

### Pitfall 4: A refactor or test “cleanup” loses learner work

**Evidence class:** General change risk; the architecture map describes existing protections, and no data-loss bug was established.

**What goes wrong:** Drafts, progress, receipts, or job records disappear, are reinitialized, become unreadable, or are mistaken for disposable generated files during UI/runtime refactoring, schema changes, or Docker cleanup. A test may pass while having overwritten a real `.learning` directory or removed a learner volume.

**Why it happens:** State is spread across separate stores and directories, with different meanings and update behavior. A code change that merges these boundaries, changes identity/path rules, or treats a receipt as replayable state can invalidate existing learner data. Atomic replacement protects a write from partial-file exposure, but it is not a migration, backup, compatibility, or restore strategy by itself.

**Warning signs:**
- Tests point at a developer’s normal state path or a named volume instead of isolated temporary/disposable state.
- A state-format change has no old-format fixture, migration test, or rollback/restore check.
- UI controls, startup code, or container scripts clear state as part of routine reset/upgrade.
- Tests check only that new writes work, not that pre-existing drafts/progress/receipts survive.
- Test/cleanup commands use broad volume or container deletion rather than explicit DS60-owned resources.

**Prevention:** Preserve the distinct progress, drafts, pads, receipts, and job-record contracts. Use `tmp_path` or explicitly disposable databases/volumes for tests; snapshot a fixture before and after migration; test upgrade, interruption, recovery, and restore paths; keep backups outside directories that cleanup removes. Before cleanup, identify ownership and verify the target. Retain the current locking/atomic-write protections and test their failure paths rather than replacing them casually.

**Likely phase:** Any persistence/UI/runtime phase that changes saved-work flows; add explicit upgrade/restore acceptance before release.

**Sources:** `.planning/codebase/ARCHITECTURE.md` (separate stores, locks, atomic JSON replacement); `.planning/PROJECT.md` (learner data and volumes must remain intact); [Python `os.replace`](https://docs.python.org/3/library/os.html#os.replace).

### Pitfall 5: Docker or process limits are mistaken for a security sandbox

**Evidence class:** **Observed repository boundary and high-impact risk.** The concerns map says local `PadRunner` executes code with the application environment and repository-root working directory; time/output limits do not block access to available files or networks. It also documents a trusted-local-code boundary and a more constrained, fixed-operation worker path. This is not a finding that the documented local model is currently insecure.

**What goes wrong:** A classroom feature is exposed to untrusted or remote users while retaining direct execution privileges, or a worker is given host paths, Docker control, credentials, or network access it does not need. CPU/memory/time bounds reduce some denial-of-service impact but do not make arbitrary code safe. A container boundary can also be weakened by privileged mode, host mounts, daemon sockets, or overly broad credentials.

**Why it happens:** The word “container” can create false confidence. Docker’s security documentation treats namespaces, cgroups, daemon access, container configuration, and kernel hardening as separate concerns; Docker explicitly warns that daemon control and host-directory sharing can grant powerful host access.

**Warning signs:**
- An API or classroom mode becomes remotely accessible, multi-user, or intended for untrusted submissions without a new threat model.
- Local direct-pad and worker execution are treated as equivalent security boundaries.
- Worker operations or curriculum manifests can choose arbitrary shell commands/arguments.
- Containers run privileged, mount the Docker socket or broad host paths, retain unnecessary capabilities, or lack resource bounds.
- Security verification only proves that a container starts or that a request token is present.

**Prevention:** Preserve the product’s trusted-local-code contract unless the owner explicitly funds a separate isolation design. Keep curriculum manifests declarative and operations allowlisted. Audit every execution path, including step-through; test filesystem/network exposure, identity, mounts, secrets, time/memory/process/output bounds, and cancellation. Apply least privilege, rootless operation where supported, narrow mounts/network, and non-root identities where compatible. Treat any shared/remote/untrusted-code capability as a security-critical architecture phase, not a routine UI enhancement.

**Likely phase:** Runtime/container qualification; any proposal to serve remote or untrusted code requires a dedicated security design and verification phase before implementation.

**Sources:** `.planning/codebase/CONCERNS.md`; `.planning/codebase/ARCHITECTURE.md`; [Docker Engine security](https://docs.docker.com/engine/security/); [Docker rootless mode](https://docs.docker.com/engine/security/rootless/); [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/).

## Moderate Pitfalls

### Pitfall 6: “Reproducible build” is confused with “fresh base image”

**Evidence class:** General researched risk; `.planning/PROJECT.md` says image/runtime verification is not yet complete.

**What goes wrong:** Different developers or CI jobs produce different images from mutable tags, unpinned package repositories, implicit build contexts, or cached layers. Conversely, pinning everything forever creates reproducible but stale and vulnerable images. Tests may pass on a developer’s existing image while the published build is missing files or uses another dependency/runtime combination.

**Why it happens:** Docker’s guidance distinguishes `--pull` (refresh base images) from `--no-cache` (rerun build steps); neither alone makes all dependency inputs repeatable. Docker build context controls which files are available to `COPY`/`ADD`, so an incorrect context or `.dockerignore` can omit required course/runtime files or accidentally send private/unneeded files.

**Warning signs:**
- Base images or package dependencies float without a recorded update policy.
- Build checks reuse a local image rather than rebuilding from the checked-out revision.
- Compose/build scripts use inconsistent context paths, profiles, or tags.
- A clean build cannot reproduce test results, or the image lacks packaged/offline assets.
- Updates are made to pins without rebuilding, running runtime checks, and recording the resulting digest.

**Prevention:** Make build context and `.dockerignore` intentional; pin base images/dependencies for controlled rebuild inputs, and schedule deliberate updates to those pins. Test a clean build for each supported profile/platform from the release commit, then exercise the actual image startup, course assets, storage mounts, and execution behavior. Record image digests and build inputs; keep freshness scans/update cadence separate from reproducibility checks.

**Likely phase:** Docker profile/runtime verification, followed by every release candidate and dependency/base-image update.

**Sources:** `.planning/PROJECT.md`; [Docker build best practices](https://docs.docker.com/build/building/best-practices/); [Docker build context](https://docs.docker.com/build/concepts/context/).

### Pitfall 7: A passing local build is published as the verified release

**Evidence class:** **Observed release readiness risk.** The project map says release gates remain incomplete and the Docker Hub repository was recreated empty and must be checked before publishing. No incorrect publication was observed.

**What goes wrong:** A mutable tag points to the wrong commit/image, a registry target is stale or unexpected, or a push succeeds without the release artifact being independently pulled and tested. Credentials or tokens passed as build arguments may be recorded in build metadata. Users then receive an image that does not match the reviewed source or that cannot be reproduced.

**Why it happens:** Local build success, registry push success, and release correctness are different claims. Docker documents SBOM/provenance attestations as build metadata and warns that build arguments can appear in provenance; tags are not a cryptographic identity for image content.

**Warning signs:**
- Publishing starts before all code, image, startup, and registry checks pass.
- The intended registry/repository/tag is not re-verified immediately before push.
- The pushed image is not pulled by digest and smoke-tested in a clean environment.
- Release notes or tags are treated as evidence of provenance without checking source revision/build materials.
- Secrets are passed through Docker build arguments or appear in logs/attestations.

**Prevention:** Keep publishing behind explicit release gates. Verify registry ownership and target state immediately before push; build from the approved commit; use a unique release tag plus recorded digest; pull that digest into a clean test environment and exercise it. Generate and inspect SBOM/provenance attestations where supported. Pass credentials through supported secret mechanisms, never build arguments. Publish only after all checks pass and record the exact artifact identity.

**Likely phase:** Release qualification and publication, after Docker profile and end-to-end checks; do not combine this with routine code changes.

**Sources:** `.planning/PROJECT.md`; [Docker build attestations](https://docs.docker.com/build/metadata/attestations/); [SLSA provenance attestations](https://docs.docker.com/build/metadata/attestations/slsa-provenance/); [Docker GitHub Actions attestations and secret warning](https://docs.docker.com/build/ci/github-actions/attestations/).

## Minor Pitfalls

### Pitfall 1: Automated checks validate repository shape but not learner-visible truth

**What goes wrong:** Catalog, lint, type, and browser-contract checks all pass, while a lesson is confusing, an exercise is too advanced for its prerequisites, or a result shown in the classroom is stale.

**Prevention:** Retain the existing automated quality gates, but supplement them with content-specific expected-output checks, runnable examples, and bounded desktop learner-path review. Record which checks actually ran and which optional database/browser checks were skipped.

**Sources:** `.planning/codebase/TESTING.md`; CS2023 curricular practices at [csed.acm.org](https://csed.acm.org/).

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Checkpoint / Python-SQL walkthrough qualification | Custom trace logic looks convincing without proving SQL correctness or state behavior | Add parser/response unit tests first; verify PostgreSQL read-only, timeouts, results, and browser contract against disposable state |
| Content inventory and lesson revision | Missing prerequisites, inconsistent outcomes, or syntax-only parity | Audit every current track against outcomes/prerequisites/examples/exercises/solutions; label unverified tracks as gaps |
| Classroom UI and learner-state changes | Drafts or receipts overwritten, reset, or orphaned | Exercise upgrade/recovery on copied state; test real persistence contracts; never clean up learner volumes |
| Docker profile/runtime qualification | Resource limits mistaken for isolation; image differs from local environment | Review each execution path and profile; test privilege/mount/network/resource boundaries and clean-image behavior |
| Release and publication | Wrong registry target, mutable tag drift, or incomplete verification | Verify target immediately before push; gate on all tests; pull/test the published digest and retain provenance |

## Sources

- Repository evidence and project constraints: `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/ARCHITECTURE.md` (analysis date 2026-11-23).
- ACM/IEEE-CS/AAAI, [CS2023 Computer Science Curricula](https://csed.acm.org/) (endorsed Jan–Feb 2024).
- Cambridge University Press, [Novice Programmers and Introductory Programming](https://www.cambridge.org/core/books/cambridge-handbook-of-computing-education-research/novice-programmers-and-introductory-programming/0CEDFE1B121198D3FB5F1541EBE3DCAD).
- PostgreSQL, [17: Lexical Structure](https://www.postgresql.org/docs/17/sql-syntax-lexical.html), [17: SELECT](https://www.postgresql.org/docs/17/sql-select.html), and [17: SET TRANSACTION](https://www.postgresql.org/docs/17/sql-set-transaction.html).
- Python, [`os.replace`](https://docs.python.org/3/library/os.html#os.replace).
- Docker, [Engine security](https://docs.docker.com/engine/security/), [rootless mode](https://docs.docker.com/engine/security/rootless/), [resource constraints](https://docs.docker.com/engine/containers/resource_constraints/), [build best practices](https://docs.docker.com/build/building/best-practices/), and [build context](https://docs.docker.com/build/concepts/context/).
- Docker, [build attestations](https://docs.docker.com/build/metadata/attestations/), [SLSA provenance](https://docs.docker.com/build/metadata/attestations/slsa-provenance/), and [GitHub Actions attestations](https://docs.docker.com/build/ci/github-actions/attestations/).
