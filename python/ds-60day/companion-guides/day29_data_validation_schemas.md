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

1. Add range and allowed-category constraints to a schema. **Hint:** start from
   written business rules, include boundary values, and create one invalid
   fixture per rule.
2. Validate the cleaned Day 18 DataFrame before saving. **Hint:** perform
   cleaning, validate the returned frame, then write only the validated result;
   preserve the failure report when validation stops the write.

### Additional mastery practice

Translate business rules into executable boundary contracts and prove both acceptance and informative failure before persisting data.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict the difference between coercing a value to the schema dtype and validating it without coercion.
   **Progressive hint:** Coercion transforms compatible representations; validation checks a state.
4. **Tracing:** Trace a row through cleaning, schema validation, and saving. At which boundary must failure stop the write?
   **Progressive hint:** Validate the actual final frame immediately before persistence.
5. **Implementation:** Create a Pandera schema with non-negative quantity, finite price, and an allowed status set, then validate one good fixture.
   **Progressive hint:** Derive constraints from stated business rules, not observed values alone.
6. **Debugging:** Repair a pipeline that writes output before validating it or catches and discards every schema error.
   **Progressive hint:** Validation failure is a blocked output, not a warning-only event.
7. **Edge case and explanation:** Create invalid fixtures for null, range, category, duplicate-key, and dtype rules; use lazy validation to inspect multiple failures.
   **Progressive hint:** One failure fixture per rule makes contract coverage auditable.

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
