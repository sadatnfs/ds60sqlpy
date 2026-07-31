# Day 29 — Solutions: Data Validation & Schemas (Pandera/Pydantic)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**turning data contracts into executable schemas and informative failures**.

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

### Vocabulary used in the worked answers

- **schema:** an executable description of data fields and constraints.
- **constraint:** a rule values or records must satisfy.
- **nullability:** whether absence is allowed.
- **coercion:** conversion toward a declared representation.
- **validation:** checking actual data against a contract.
- **failure report:** structured evidence identifying violated rules and locations.

### Reference pattern 1 — Validate a small table against explicit rules

A good fixture makes the accepted contract easy to see.

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

**Expected observation:** The two records are returned after successful validation; `price` follows the declared floating representation.

### Reference pattern 2 — Show that validation guards persistence

Only data returned from validation should continue to a write boundary.

```python
def validated_for_output(frame: pd.DataFrame) -> pd.DataFrame:
    checked = schema.validate(frame, lazy=True)
    return checked.copy()

output_ready = validated_for_output(valid)
(len(output_ready), output_ready["quantity"].min())
```

**Expected observation:** `(2, 0)`. An invalid frame would raise before any output-writing code is reached.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Extend a Pandera schema with documented inclusive/exclusive ranges, allowed categories, nullability, and key uniqueness. **Constraints:** derive each rule from written business meaning and include exact boundary values. **Verify:** one valid fixture passes and a separate invalid fixture for each rule fails with the expected column/check evidence.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from turning data contracts into executable schemas and informative failures.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Pydantic for individual Python records/configuration and Pandera for DataFrame-wide column/index checks; database constraints protect stored relational data.

**Edge case:** Nulls, infinities, dtype coercion, duplicate composite keys, unexpected categories, empty frames, and cross-column rules need fixtures.

**Solution evidence to inspect:** one valid fixture passes and a separate invalid fixture for each rule fails with the expected column/check evidence.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Validate the cleaned Day 18 DataFrame immediately before saving. **Sequence:** clean → validate returned frame → write only validated output → re-read/reconcile. **Expected behavior:** a deliberately invalid fixture blocks the write and preserves a useful failure report. **Constraint:** do not catch and discard `SchemaError`/`SchemaErrors`. **Verify:** Use a temporary output path to prove valid data writes/reloads, while an invalid fixture raises before the file exists.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies turning data contracts into executable schemas and informative failures.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Pydantic for individual Python records/configuration and Pandera for DataFrame-wide column/index checks; database constraints protect stored relational data.

**Edge case:** Nulls, infinities, dtype coercion, duplicate composite keys, unexpected categories, empty frames, and cross-column rules need fixtures.

**Solution evidence to inspect:** Use a temporary output path to prove valid data writes/reloads, while an invalid fixture raises before the file exists.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the difference between coercing a value to the schema dtype and validating it without coercion. **Progressive hint:** Coercion transforms compatible representations; validation checks a state. **Verify:** Validate numeric text with/without coercion and assert the coerced dtype/value versus the strict failure; record what changed rather than calling it mere validation.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying turning data contracts into executable schemas and informative failures.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Pydantic for individual Python records/configuration and Pandera for DataFrame-wide column/index checks; database constraints protect stored relational data.

**Edge case:** Nulls, infinities, dtype coercion, duplicate composite keys, unexpected categories, empty frames, and cross-column rules need fixtures.

**Solution evidence to inspect:** Validate numeric text with/without coercion and assert the coerced dtype/value versus the strict failure; record what changed rather than calling it mere validation.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace a row through cleaning, schema validation, and saving. At which boundary must failure stop the write? **Progressive hint:** Validate the actual final frame immediately before persistence. **Verify:** Use a temporary path and event log; assert valid rows reach save only after validation and invalid rows raise before any file/write event.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the turning data contracts into executable schemas and informative failures model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Pydantic for individual Python records/configuration and Pandera for DataFrame-wide column/index checks; database constraints protect stored relational data.

**Edge case:** Nulls, infinities, dtype coercion, duplicate composite keys, unexpected categories, empty frames, and cross-column rules need fixtures.

**Solution evidence to inspect:** Use a temporary path and event log; assert valid rows reach save only after validation and invalid rows raise before any file/write event.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Create a Pandera schema with non-negative quantity, finite price, and an allowed status set, then validate one good fixture. **Progressive hint:** Derive constraints from stated business rules, not observed values alone. **Verify:** Assert one good fixture returns unchanged meaning, then independently fail negative quantity, nonfinite price, and unknown status with named checks.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies turning data contracts into executable schemas and informative failures.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Pydantic for individual Python records/configuration and Pandera for DataFrame-wide column/index checks; database constraints protect stored relational data.

**Edge case:** Nulls, infinities, dtype coercion, duplicate composite keys, unexpected categories, empty frames, and cross-column rules need fixtures.

**Solution evidence to inspect:** Assert one good fixture returns unchanged meaning, then independently fail negative quantity, nonfinite price, and unknown status with named checks.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a pipeline that writes output before validating it or catches and discards every schema error. **Progressive hint:** Validation failure is a blocked output, not a warning-only event. **Verify:** Reorder the pipeline and assert invalid data leaves no output file; retain and inspect the schema failure instead of converting it to a warning.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in turning data contracts into executable schemas and informative failures.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Pydantic for individual Python records/configuration and Pandera for DataFrame-wide column/index checks; database constraints protect stored relational data.

**Edge case:** Nulls, infinities, dtype coercion, duplicate composite keys, unexpected categories, empty frames, and cross-column rules need fixtures.

**Solution evidence to inspect:** Reorder the pipeline and assert invalid data leaves no output file; retain and inspect the schema failure instead of converting it to a warning.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Create invalid fixtures for null, range, category, duplicate-key, and dtype rules; use lazy validation to inspect multiple failures. **Progressive hint:** One failure fixture per rule makes contract coverage auditable. **Verify:** Run lazy validation on fixtures violating all five rule families and assert the failure cases include each expected column/check category.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from turning data contracts into executable schemas and informative failures.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Pydantic for individual Python records/configuration and Pandera for DataFrame-wide column/index checks; database constraints protect stored relational data.

**Edge case:** Nulls, infinities, dtype coercion, duplicate composite keys, unexpected categories, empty frames, and cross-column rules need fixtures.

**Solution evidence to inspect:** Run lazy validation on fixtures violating all five rule families and assert the failure cases include each expected column/check category.
<!-- END BEGINNER SOLUTION REVIEW -->

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
