# Day 29 — Solutions: Data Validation & Schemas (Pandera/Pydantic)

We add constraints and validate a cleaned DataFrame prior to saving.

Contents
- Exercise 1: Add column constraints (ranges, categories)
- Exercise 2: Validate a cleaned DataFrame before saving

---

Exercise 1 — Column constraints
```python
import pandas as pd
import pandera.pandas as pa
import pandera.typing as pat

class Cleaned(pa.DataFrameModel):
    id: pat.Series[int] = pa.Field(ge=1, unique=True)
    city: pat.Series[str] = pa.Field(isin=['NY','SF','LA','SEA'])
    price: pat.Series[float] = pa.Field(ge=0)
    qty: pat.Series[int] = pa.Field(ge=0)

    class Config:
        coerce = True   # coerce types where possible

# Example data
clean = pd.DataFrame({'id':[1,2,3], 'city':['NY','SF','LA'], 'price':[9.5, 12.0, 0.0], 'qty':[1,2,3]})
validated = Cleaned.validate(clean)
print(validated.dtypes)
```

Exercise 2 — Validate before saving
```python
from pathlib import Path

def save_validated(df: pd.DataFrame, path: Path) -> None:
    Cleaned.validate(df)           # raises detailed errors when invalid
    df.to_parquet(path, index=False)

# save_validated(validated, Path('clean.parquet'))
```
Notes
- Prefer fail-fast; catch data issues early with clear messages
- For row-wise validation, Pydantic models can validate dict records

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Add range and allowed-category constraints to a schema. **Hint:** start from written business rules, include boundary values, and create one invalid fixture per rule.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Validate the cleaned Day 18 DataFrame before saving. **Hint:** perform cleaning, validate the returned frame, then write only the validated result; preserve the failure report when validation stops the write.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict the difference between coercing a value to the schema dtype and validating it without coercion.

**Reasoning checkpoint:** Coercion transforms compatible representations; validation checks a state. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace a row through cleaning, schema validation, and saving. At which boundary must failure stop the write?

**Reasoning checkpoint:** Validate the actual final frame immediately before persistence. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Create a Pandera schema with non-negative quantity, finite price, and an allowed status set, then validate one good fixture.

**Reasoning checkpoint:** Derive constraints from stated business rules, not observed values alone. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a pipeline that writes output before validating it or catches and discards every schema error.

**Reasoning checkpoint:** Validation failure is a blocked output, not a warning-only event. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Create invalid fixtures for null, range, category, duplicate-key, and dtype rules; use lazy validation to inspect multiple failures.

**Reasoning checkpoint:** One failure fixture per rule makes contract coverage auditable. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Translate business rules into executable boundary contracts and prove both acceptance and informative failure before persisting data.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Transform versus assert

Coercion can turn compatible text such as `"2"` into integer `2`; it should not
silently invent a value for incompatible text. The final cleaned frame must
validate before any destination is replaced.

### Practices 3–5 — Executable business rules

```python
import pandas as pd
import pandera.pandas as pa

ORDER_SCHEMA = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, nullable=False, unique=True),
        "quantity": pa.Column(int, pa.Check.ge(0), nullable=False),
        "price": pa.Column(
            float,
            checks=[pa.Check.ge(0), pa.Check(lambda values: values.notna())],
            nullable=False,
        ),
        "status": pa.Column(str, pa.Check.isin(["new", "paid", "shipped"])),
    },
    strict=True,
    coerce=True,
)

valid = pd.DataFrame(
    {"order_id": [1], "quantity": ["2"], "price": [4.5], "status": ["paid"]}
)
checked = ORDER_SCHEMA.validate(valid, lazy=True)
assert checked.loc[0, "quantity"] == 2

invalid = pd.DataFrame(
    {
        "order_id": [1, 1],       # Duplicate key.
        "quantity": [-1, 2],      # Range violation.
        "price": [1.0, None],     # Null violation.
        "status": ["unknown", "paid"],  # Category violation.
    }
)
try:
    ORDER_SCHEMA.validate(invalid, lazy=True)
except pa.errors.SchemaErrors as error:
    # Preserve bounded failure cases for diagnosis; do not write invalid data.
    assert not error.failure_cases.empty
else:
    raise AssertionError("invalid rows should fail the schema")
```

A production save function should write only `checked`. If validation fails,
surface the report and leave any previous valid destination untouched.
