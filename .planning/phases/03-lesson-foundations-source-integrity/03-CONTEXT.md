# Phase 3 context: lesson foundations and source integrity

## Requirements

- CURR-02: every authored lesson states observable outcomes, direct
  prerequisites, essential terms and enough context to orient a new learner,
  while keeping stable lesson identity.
- CURR-07: content improvements are source-led and course-specific; generated
  readers, stable IDs, prerequisites and the authored-versus-planned
  distinction stay consistent.

## Findings

- The classroom lesson header already renders the catalog outcome and the
  direct prerequisites (or "Start here: no earlier lesson is required.") for
  every authored and planned lesson (`classroom.js`, authored and planned
  paths). Copying prerequisites into about 1100 guides would duplicate the
  catalog and drift, so orientation is owned by the catalog.
- Baseline (Phase 2 matrix): 31 core lessons have no outcome; 971 guides
  define fewer than 3 terms; about 133 outcomes are not observable (64 cuda
  lowercase deliverable phrases, 40 templated statistics-ml "Understand ..."
  outcomes, 23 llm-applied definitions, sql-58/59/60 noun phrases, llm-007
  "Learn", apache-074 "Understand").
- `unknown_prerequisites` is already empty for every row.

## Decisions

1. Outcomes: the matrix flags `weak-outcome` when a catalog outcome does not
   start with a curated observable action verb (an "-ly" adverb before one is
   allowed), starts lowercase or has fewer than 4 words. "Understand",
   "Know" and "Learn" are never accepted.
2. Prerequisites: remain catalog-owned; any unknown prerequisite is a
   coverage problem.
3. Essential terms: every authored guide carries a `## Key terms` section
   with at least 3 lesson-specific `- **Term:** definition` bullets, written
   in the track's authoring sources and seeded from the plan lesson's
   `concepts` so catalog search and guide vocabulary agree.
4. Orientation: `guide-no-orientation` is retired. Guide-level
   `states_prerequisites`/`states_objectives` stay as informational metrics.
5. Gate: `tests/test_coverage_matrix.py` holds `missing-outcome`,
   `weak-outcome` and `few-terms` to ceilings that only fall; the final plan
   sets them to zero.
6. Track work is done by per-track agents that edit only their own track's
   authoring sources, rebuild that track, run its tests and check progress
   with the read-only `--track/--gaps` helper. The orchestrator regenerates
   shared outputs and commits.
