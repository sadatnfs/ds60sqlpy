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





<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day30_project_eda_preprocessing.md`, then open `python/ds-60day/notebooks/day30_project_eda_preprocessing.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 30 — project: reproducible eda and preprocessing to practice a restartable EDA and preprocessing project with an auditable evidence chain
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A project notebook is a reproducible report, not a diary of accidental
execution order. Start with the question, provenance, row grain, keys,
scope, and acceptance criteria. Keep raw data immutable, put cleaning in
functions, validate the final data, and write artifacts only after all
gates pass.

Build an evidence chain from raw to clean to validated to saved output.
Reconcile row counts, unique entities, missingness, and additive totals
at each boundary. Record each material decision with evidence, action,
rationale, validation, and impact. Separate findings from limitations
and stop output when data is empty, invalid, or contaminated by target
or time leakage.

### Vocabulary in plain language

- **acceptance criterion:** a measurable condition required before output is trusted.
- **decision log:** structured evidence and rationale for each material treatment.
- **reconciliation:** comparison of key counts/measures across processing boundaries.
- **artifact:** a generated dataset, figure, report, or manifest.
- **manifest:** metadata describing artifact source, version, shape, and validation.
- **restartability:** the ability to run top to bottom from a fresh kernel with the same result.

### Syntax anatomy

A robust notebook flows through named values such as `raw`,
`profile`, `cleaned`, `validated`, and `artifact_path` rather than
overwriting one `df`. A decision-log record can contain `issue`,
`evidence`, `action`, `rationale`, `validation`, and `impact`.
Assertions at each transition turn narrative expectations into
executable gates.

### Worked example 1 — Reconcile a cleaning boundary

Make every row removal visible and explainable. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import pandas as pd

raw = pd.DataFrame({
    "id": [1, 2, 2, 3],
    "amount": [10.0, 20.0, 20.0, None],
})
cleaned = raw.drop_duplicates().dropna(subset=["amount"]).copy()
reconciliation = {
    "raw_rows": len(raw),
    "clean_rows": len(cleaned),
    "rows_removed": len(raw) - len(cleaned),
    "raw_known_total": raw["amount"].sum(),
    "clean_total": cleaned["amount"].sum(),
}
reconciliation
```

**Expected observation**

```text
The reconciliation reports four raw rows, two clean rows, two removed rows, and totals before/after. Those changes still need documented rationale.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Represent a decision as data

A structured entry is easier to audit than a scattered comment. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
decision = {
    "issue": "duplicate id=2 row",
    "evidence": "two identical rows",
    "action": "keep first exact duplicate",
    "rationale": "duplicate adds no new information",
    "validation": "id/amount pair is unique afterward",
    "impact": "one row and amount=20 removed from row-level totals",
}
sorted(decision)
```

**Expected observation**

```text
All six required fields are listed. The impact makes clear that de-duplication changes additive totals.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Restart the kernel and run all before accepting any artifact.
2. Keep `raw` unchanged and make cleaning functions return copies.
3. Reconcile rows, entities, missing values, and additive measures at every boundary.
4. Block writes when the clean frame is empty, schema fails, or leakage/acceptance criteria remain unresolved.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Boundary to remember:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. **Load and scope:** choose a local, constructed, or already-cached dataset and record source/provenance, license if applicable, row grain, keys, shape, time range, analytical question, and measurable acceptance criteria.
   **Expected behavior:** a fresh-kernel run can recreate the same raw profile without hidden state or network access.
   **Verify:** assert expected columns and key/time bounds before continuing.

2. **Explore:** analyze quality, distributions, missingness, duplicates, relationships, correlations, and relevant segments. **Constraints:** pair every table/plot with evidence, sample size/denominator, and a caveat; do not treat correlation as causation.
   **Verify:** every stated finding points to a reproducible calculation or plot and leakage-prone fields are excluded.

3. **Clean and transform:** implement `clean(raw)` that returns a new DataFrame and records each decision's evidence, action, rationale, validation, and impact. **Constraints:** preserve raw data, avoid broad silent row dropping, and split before fitting learned transforms if a target exists.
   **Verify:** test idempotence where promised and reconcile row/entity counts plus key totals.

4. **Validate:** apply the Day 29 schema to the actual final cleaned DataFrame before output.
   **Expected behavior:** one valid fixture passes and a deliberately invalid fixture proves an important rule blocks progress. **Constraint:** do not catch and discard the validation failure.
   **Verify:** save is impossible until validation succeeds.

5. **Save and report:** write cleaned data and figures under an ignored `artifacts/day30/` path plus a manifest containing source, timestamp/version policy, row count, schema result, and file list. **Constraints:** handle an empty clean dataset as a blocked project, reopen outputs, and summarize findings, limitations, and lessons learned.
   **Verify:** saved/reloaded shape, schema, and key totals match the validated in-memory frame.

### Additional mastery practice

Build a restartable evidence chain: question and provenance → raw checks → decisions → clean data → validation → artifacts → limitations.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

6. **Prediction:** Before loading data, write the analytical question, row grain, entity keys, expected time range, and acceptance criteria. Predict one failure.
   **Progressive hint:** A declared expectation turns a surprise into a testable discrepancy.
   **Verify:** Save the written contract before loading, then assert the raw profile against keys/time/schema and record whether the predicted failure actually occurred.
7. **Tracing:** Trace row count, unique entity count, missing target count, and an additive total across raw, cleaned, validated, and saved boundaries.
   **Progressive hint:** Every material change needs a reason and reconciliation.
   **Verify:** Build a four-boundary reconciliation table and assert every row/entity/missing/total change has an explicit reason; reopen saved data for the final row.
8. **Implementation:** Implement a structured decision log entry containing evidence, action, rationale, validation, and impact.
   **Progressive hint:** Make decisions data, not scattered comments.
   **Verify:** Validate that each decision entry contains evidence, action, rationale, validation, and impact and links to a reproducible count/test.
9. **Debugging:** Repair a notebook that depends on out-of-order state and overwrites its raw frame during cleaning.
   **Progressive hint:** Put parameters/imports first and make `clean(raw)` return a copy.
   **Verify:** Restart and run top to bottom; assert `raw` remains unchanged, `clean(raw)` returns a copy, and no cell requires a later-created name.
10. **Edge case and explanation:** Prevent target/time leakage, handle an empty cleaned dataset, and write an artifact manifest with source, row count, schema result, and version.
   **Progressive hint:** Block artifact creation when acceptance criteria fail.
   **Verify:** Use leakage and empty-data fixtures to prove artifact creation is blocked; for a valid run, assert manifest source/count/schema/version match reopened files.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-30`
(Day 30 — Project: Reproducible EDA and Preprocessing). I am a complete beginner. Emphasize a restartable EDA and preprocessing project with an auditable evidence chain.
Read `python/ds-60day/companion-guides/day30_project_eda_preprocessing.md` and use the learner notebook
`python/ds-60day/notebooks/day30_project_eda_preprocessing.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
