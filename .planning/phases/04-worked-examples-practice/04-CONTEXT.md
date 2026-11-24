# Phase 4 context: worked examples and practice

## Requirements

- CURR-03: every authored lesson includes an accurate, substantive worked
  example with explanation and interpretation appropriate to its subject;
  non-code lessons use an appropriate non-code artifact.
- CURR-04: every practice lesson progresses from supported reasoning or
  modification toward appropriate independent application and includes a
  solution or feedback that explains the reasoning.

## Findings (Phase 2 matrix, before Phase 3 edits)

- Thresholds come from `scripts/audit_lesson_depth.py`: guide at least 1050
  words, at least 2 fenced examples, practice solution Markdown at least 700
  words, at least 6 exercises.
- Open gaps: thin-solution 698, thin-guide 418, few-examples 352.
  few-exercises and missing-solution are already 0, so every practice lesson
  already has six tasks and a solution file.
- thin-solution is concentrated in cuda (128, median 361 words), dax, r,
  kubernetes and web-development (60 each), docker and swift (42), jax (34),
  julia (32, median 174) and javascript-typescript and llm-evaluation (24).
- thin-guide is led by apache (75), python-web (67), web-development (59),
  tmb (48), r (31), statistics-ml (29) and advanced-spark (26).
- few-examples (0 or 1 fenced block) is led by python-web (72),
  data-ml-engineering (71), apache (41), advanced-spark (38), tmb (30) and
  statistics-ml (29, all with none).
- Templated prose is widespread. Counting paragraphs of at least 20 words whose
  sampled 8-word shingles mostly occur in more than two lessons, about 970k
  guide and solution words are generator boilerplate: go 70%, c 71%, java 64%,
  cuda 54%, javascript-typescript 55%, swift 54%, sql 49%. Word-count gaps can
  be closed by padding with more templated text, which would not help a
  learner.

## Decisions

1. Keep the existing gap definitions (total words, fenced blocks) so the
   Phase 2 baseline stays comparable.
2. Add a `templated_words` metric per lesson and a corpus ratchet:
   the total may not rise above the measured post-Phase-3 baseline. New
   guide and solution prose must therefore be lesson-specific; a generator
   template that stamps the same paragraph into many lessons fails the gate.
   The `--track` helper prints the track's templated-word total so agents can
   show it did not rise.
3. A worked example is a fenced artifact the learner can run or inspect,
   followed by an interpretation: what it shows, which line or value matters,
   and what a changed input would do. Reading and operations lessons use a
   fenced non-code artifact (query plan, manifest, config, table, log,
   derivation) with the same interpretation.
4. A solution explains each task's reasoning: approach, why it is correct,
   at least one plausible wrong approach and why it fails, and how to verify
   the result. Restating the code or the task does not count.
5. `tests/test_coverage_matrix.py` holds thin-guide, few-examples and
   thin-solution to ceilings that only fall; the final plan sets them to 0.
6. Rewriting the existing templated scaffolding across all tracks is out of
   scope for this phase (about 970k words). The ratchet stops it from growing,
   and the metric makes later reduction measurable.
7. Track work uses the Phase 3 pattern: one agent per track or track group,
   editing only that track's authoring sources, rebuilding it and checking with
   the read-only helper. The orchestrator regenerates shared outputs, runs the
   gates and commits.
