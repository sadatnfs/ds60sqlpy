# Day 29 — Data Validation with Schemas

**Level:** Intermediate

A schema turns assumptions about columns, types, ranges, and uniqueness into an
executable boundary contract. Validation detects problems; it does not decide
how to clean them.

## Learning objectives

By the end of this lesson, you can:

- define a Pandera DataFrame model with typed columns;
- add nullability, range, category, and uniqueness constraints;
- validate a frame at a pipeline boundary;
- interpret a schema failure without discarding bad rows silently;
- distinguish DataFrame validation from row/object validation.

## Prerequisites

Complete Day 28 (`python-28`) and the typed cleaner from Day 18 (`python-18`).
Pandera is in the `data` dependency group. Pydantic is an optional
object-validation tool in the advanced `production` group.

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

2. Read `python/ds-60day/companion-guides/day29_data_validation_schemas.md`, then open `python/ds-60day/notebooks/day29_data_validation_schemas.ipynb` from the repository
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

**Lesson outcome:** use day 29 — data validation with schemas to practice turning data contracts into executable schemas and informative failures
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A data schema describes more than column names: required presence,
dtypes, nullability, ranges, allowed categories, uniqueness, and
cross-field rules. Derive constraints from domain/business meaning and
declared interfaces, not merely from values observed in one sample.

Validation should sit immediately before a boundary that depends on the
contract, especially saving or handing data to a model. Coercion changes
compatible representations; validation checks the resulting state.
Treat a failure as blocked output with actionable evidence. Test one
valid fixture and one deliberately invalid fixture for every important
rule.

### Vocabulary in plain language

- **schema:** an executable description of data fields and constraints.
- **constraint:** a rule values or records must satisfy.
- **nullability:** whether absence is allowed.
- **coercion:** conversion toward a declared representation.
- **validation:** checking actual data against a contract.
- **failure report:** structured evidence identifying violated rules and locations.

### Syntax anatomy

In Pandera, `pa.Column(float, checks=pa.Check.ge(0), nullable=False)`
states representation, a non-negative constraint, and missing policy.
`schema.validate(frame, lazy=True)` collects multiple failures before
raising a `SchemaErrors` report. Coercion, if enabled, occurs before
checks and must not be mistaken for silently repairing invalid meaning.

### Worked example 1 — Validate a small table against explicit rules

A good fixture makes the accepted contract easy to see. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import pandas as pd
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "quantity": pa.Column(int, checks=pa.Check.ge(0)),
    "price": pa.Column(float, checks=pa.Check.ge(0), coerce=True),
    "status": pa.Column(str, checks=pa.Check.isin(["open", "closed"])),
})
valid = pd.DataFrame({
    "quantity": [1, 0],
    "price": [2.5, 0.0],
    "status": ["open", "closed"],
})
checked = schema.validate(valid)
checked.to_dict("records")
```

**Expected observation**

```text
The two records are returned after successful validation; `price` follows the declared floating representation.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Show that validation guards persistence

Only data returned from validation should continue to a write boundary. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def validated_for_output(frame: pd.DataFrame) -> pd.DataFrame:
    checked = schema.validate(frame, lazy=True)
    return checked.copy()

output_ready = validated_for_output(valid)
(len(output_ready), output_ready["quantity"].min())
```

**Expected observation**

```text
`(2, 0)`. An invalid frame would raise before any output-writing code is reached.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Write the business meaning and exact boundary values before encoding a check.
2. Separate cleaning/coercion from validation and count values changed by coercion.
3. Use lazy validation during diagnosis to see multiple rule failures together.
4. Do not catch and discard schema errors or save before validation.

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

**Useful alternative:** Use Pydantic for individual Python records/configuration and Pandera for DataFrame-wide column/index checks; database constraints protect stored relational data.

**Boundary to remember:** Nulls, infinities, dtype coercion, duplicate composite keys, unexpected categories, empty frames, and cross-column rules need fixtures.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Schema:** executable description of expected data shape and constraints.
- **Constraint:** rule such as non-negative, unique, allowed category, or
  non-null.
- **Coercion:** attempt to convert values to the declared dtype.
- **Fail fast:** reject invalid data near the boundary rather than propagating
  it.
- **Lazy validation:** collect multiple failures before raising.
- **DataFrame model:** class-based Pandera schema for table-shaped data.

## Worked example

```python
import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

class ReadingSchema(pa.DataFrameModel):
    sensor_id: Series[int] = pa.Field(ge=1, unique=True)
    status: Series[str] = pa.Field(isin=["ok", "warning"])
    value: Series[float] = pa.Field(nullable=False)

    class Config:
        coerce = True

readings = pd.DataFrame(
    {"sensor_id": [1, 2], "status": ["ok", "warning"], "value": [2.5, 4.0]}
)
validated = ReadingSchema.validate(readings)
```

Coercion is explicit; inspect source anomalies before relying on coercion as
cleaning.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Extend a Pandera schema with documented inclusive/exclusive ranges, allowed categories, nullability, and key uniqueness. **Constraints:** derive each rule from written business meaning and include exact boundary values.
   **Verify:** one valid fixture passes and a separate invalid fixture for each rule fails with the expected column/check evidence.

2. Validate the cleaned Day 18 DataFrame immediately before saving. **Sequence:** clean → validate returned frame → write only validated output → re-read/reconcile.
   **Expected behavior:** a deliberately invalid fixture blocks the write and preserves a useful failure report. **Constraint:** do not catch and discard `SchemaError`/`SchemaErrors`.
   **Verify:** Use a temporary output path to prove valid data writes/reloads, while an invalid fixture raises before the file exists.

### Additional mastery practice

Translate business rules into executable boundary contracts and prove both acceptance and informative failure before persisting data.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict the difference between coercing a value to the schema dtype and validating it without coercion.
   **Progressive hint:** Coercion transforms compatible representations; validation checks a state.
   **Verify:** Validate numeric text with/without coercion and assert the coerced dtype/value versus the strict failure; record what changed rather than calling it mere validation.
4. **Tracing:** Trace a row through cleaning, schema validation, and saving. At which boundary must failure stop the write?
   **Progressive hint:** Validate the actual final frame immediately before persistence.
   **Verify:** Use a temporary path and event log; assert valid rows reach save only after validation and invalid rows raise before any file/write event.
5. **Implementation:** Create a Pandera schema with non-negative quantity, finite price, and an allowed status set, then validate one good fixture.
   **Progressive hint:** Derive constraints from stated business rules, not observed values alone.
   **Verify:** Assert one good fixture returns unchanged meaning, then independently fail negative quantity, nonfinite price, and unknown status with named checks.
6. **Debugging:** Repair a pipeline that writes output before validating it or catches and discards every schema error.
   **Progressive hint:** Validation failure is a blocked output, not a warning-only event.
   **Verify:** Reorder the pipeline and assert invalid data leaves no output file; retain and inspect the schema failure instead of converting it to a warning.
7. **Edge case and explanation:** Create invalid fixtures for null, range, category, duplicate-key, and dtype rules; use lazy validation to inspect multiple failures.
   **Progressive hint:** One failure fixture per rule makes contract coverage auditable.
   **Verify:** Run lazy validation on fixtures violating all five rule families and assert the failure cases include each expected column/check category.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- Which rules belong in a schema versus a cleaning function?
- What can coercion accidentally hide?
- When is uniqueness expected globally versus within a composite key?
- Why should both valid and invalid fixtures be tested?

Expected behavior: valid input returns a typed frame, each invalid fixture
fails for the intended rule, and invalid output is not written.

## Common pitfalls and diagnosis

- **Schema and DataFrame column names differ:** compare exact labels and whether
  extra/missing columns are allowed.
- **A nullable column still fails:** nullable controls missing values, not
  incompatible non-missing types or other constraints.
- **Coercion turns bad text into a failure far from its source:** validate/raw
  profile first and retain source-row context.
- **A schema is treated as cleaning:** keep repair decisions explicit and test
  validation after cleaning.
- **Pandera imports fail:** verify the notebook uses `.venv` and the standard
  data dependencies were installed.

## Continue

- [Open the learner notebook](../notebooks/day29_data_validation_schemas.ipynb)
- [Check the separate solution](../solutions/day29_data_validation_schemas/day29_solutions.md)
- [Next: Day 30 — EDA and preprocessing project](day30_project_eda_preprocessing.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-29`
(Day 29 — Data Validation with Schemas). Direct catalog prerequisites: `python-28`.
I have completed the direct prerequisites: `python-28`. Emphasize turning data contracts into executable schemas and informative failures.
Read `python/ds-60day/companion-guides/day29_data_validation_schemas.md` and use the learner notebook
`python/ds-60day/notebooks/day29_data_validation_schemas.ipynb`. Do not open or quote anything under `solutions/` unless
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
