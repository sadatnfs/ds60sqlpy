# Day 30 — Project: Reproducible EDA and Preprocessing

**Level:** Intermediate checkpoint

This checkpoint combines loading, profiling, cleaning, visualization, schema
validation, and written reasoning into one restartable analysis.

## Learning objectives

By the end of this project, you can:

- define an analytical question, dataset scope, and row grain;
- build a deterministic raw-to-clean pipeline;
- produce an evidence-led EDA with clearly labeled visuals;
- validate the cleaned table before saving it;
- document decisions, limitations, and what you learned.

## Prerequisites

Complete Days 16–29, especially cleaning (`python-18`), EDA (`python-24`),
visualization (`python-25`), feature engineering (`python-28`), and schemas
(`python-29`).

## Vocabulary and mental model

- **Reproducibility:** another learner can run the same inputs/code and obtain
  equivalent results.
- **Provenance:** where data came from and when/how it was obtained.
- **Lineage:** transformations connecting raw input to an output.
- **Decision log:** evidence, choice, rationale, and consequence for each
  non-obvious cleaning step.
- **Acceptance criteria:** observable conditions required for completion.
- **Artifact:** generated dataset, figure, or report; source code/notebook is
  tracked, while disposable output belongs under ignored `artifacts/`.

## Worked example: a decision record

Before coding a repair, record it:

```text
Evidence: 3.2% of `amount` values are non-numeric, concentrated in source B.
Decision: coerce those values to missing; do not impute until source B is reviewed.
Validation: schema rejects missing `amount` before the final save.
Impact: final output is blocked instead of silently changing those rows.
```

This is more useful than an unexplained `dropna()` because it preserves the
reasoning and a way to verify the consequence.

## Exercises and progressive hints

1. **Load and scope.** Use a local file, constructed dataset, or already-cached
   Seaborn sample; record provenance, row grain, shape, and analytical question.
   **Hint:** restart the notebook before continuing so hidden state cannot supply
   the data.
2. **Explore.** Examine distributions, missingness, duplicates, relationships,
   correlations, and relevant segments. **Hint:** pair each table/plot with one
   sentence of evidence and one caveat; correlation alone is not causation.
3. **Clean and transform.** Reuse/refine the Day 18 cleaner and document each
   decision. **Hint:** keep raw data unchanged and assert idempotence where
   appropriate.
4. **Validate.** Apply a Pandera schema from Day 29 before writing. **Hint:**
   create at least one deliberately invalid fixture proving an important
   constraint can fail.
5. **Save and report.** Write cleaned output under `artifacts/day30/`, export
   readable figures, summarize findings/limitations, and add a final
   "What I learned" section. **Hint:** report row counts and key totals at raw,
   cleaned, and saved boundaries.

If the dataset includes a prediction target, split before learning imputation,
encoding, scaling, or target-aware decisions.

### Additional mastery practice

Build a restartable evidence chain: question and provenance → raw checks → decisions → clean data → validation → artifacts → limitations.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

6. **Prediction:** Before loading data, write the analytical question, row grain, entity keys, expected time range, and acceptance criteria. Predict one failure.
   **Progressive hint:** A declared expectation turns a surprise into a testable discrepancy.
7. **Tracing:** Trace row count, unique entity count, missing target count, and an additive total across raw, cleaned, validated, and saved boundaries.
   **Progressive hint:** Every material change needs a reason and reconciliation.
8. **Implementation:** Implement a structured decision log entry containing evidence, action, rationale, validation, and impact.
   **Progressive hint:** Make decisions data, not scattered comments.
9. **Debugging:** Repair a notebook that depends on out-of-order state and overwrites its raw frame during cleaning.
   **Progressive hint:** Put parameters/imports first and make `clean(raw)` return a copy.
10. **Edge case and explanation:** Prevent target/time leakage, handle an empty cleaned dataset, and write an artifact manifest with source, row count, schema result, and version.
   **Progressive hint:** Block artifact creation when acceptance criteria fail.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check and acceptance criteria

- Can the notebook run top-to-bottom in a fresh kernel with networking off?
- Is every non-obvious cleaning decision supported by evidence?
- Do schema checks run before any final data write?
- Do raw and cleaned row counts/totals reconcile or have documented differences?
- Are generated data, caches, `.venv`, and secrets absent from the Git diff?
- Can a reader distinguish observed findings, hypotheses, and limitations?

Expected deliverables: restartable notebook, validated cleaned dataset, labeled
figures, concise findings, decision log, and explicit limitations.

## Common pitfalls and diagnosis

- **The notebook works only after out-of-order execution:** restart the kernel
  and run all; move definitions before use and remove hidden state.
- **Cleaning choices are unexplained:** add evidence, rationale, and a
  validation/reconciliation for each material change.
- **Schema runs only on a toy fixture:** validate the actual final frame
  immediately before saving.
- **A first-use dataset fails offline:** prime the documented cache online or
  use local/constructed data.
- **Target leakage inflates results:** fit learned preprocessing only on
  training data and keep evaluation data untouched.
- **Machine-specific files appear in Git:** keep `.venv`, caches, `.env`, and
  generated output in ignored locations.

## Continue

- [Open the learner notebook](../notebooks/day30_project_eda_preprocessing.ipynb)
- [Review the separate project solution](../solutions/day30_project_eda_preprocessing/day30_solutions.md)
- [Next: Day 31 — Probability basics](day31_probability_basics.md)
