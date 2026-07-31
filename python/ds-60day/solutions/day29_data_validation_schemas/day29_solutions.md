# Day 29 — Solutions: Data Validation & Schemas (Pandera/Pydantic)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **turning data contracts into executable schemas and informative failures**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **turning data contracts into executable schemas and informative failures** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Extend a Pandera schema with documented inclusive/exclusive ranges, allowed categories, nullability, and key uniqueness. **Constraints:** derive each rule from written business meaning and include exact boundary values. **Verify:** one valid fixture passes and a separate invalid fixture for each rule fails with the expected column/check evidence.

**Reasoning:** Make this boundary unambiguous in code: Extend a Pandera schema with documented inclusive/exclusive ranges, allowed categories, nullability, and key uniqueness. Constraints: derive each rule from written business meaning and include exact boundary values. Values below, at, and above the named boundary must produce the evidence one valid fixture passes and a separate invalid fixture for each rule fails with the expected column/check evidence. Those cases show how turning data contracts into executable schemas and informative failures behaves at its edge.

```python
import numpy as np
import pandas as pd
import pandera.pandas as pa

# Business meaning:
# - order_id is the unique non-null business key.
# - quantity may be zero: inclusive range [0, infinity).
# - price uses inclusive lower and exclusive upper bounds: [0, 10_000).
# - status is a required controlled category; note is optional.
schema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, unique=True, nullable=False),
        "quantity": pa.Column(int, checks=pa.Check.ge(0), nullable=False),
        "price": pa.Column(
            float,
            checks=[
                pa.Check.ge(0),
                pa.Check.lt(10_000),
                pa.Check(
                    lambda values: np.isfinite(values),
                    name="finite_price",
                ),
            ],
            nullable=False,
            coerce=True,
        ),
        "status": pa.Column(
            str,
            checks=pa.Check.isin(["open", "closed"]),
            nullable=False,
        ),
        "note": pa.Column("string", nullable=True, coerce=True),
    },
    strict=True,
)
valid = pd.DataFrame({
    "order_id": [100, 101],
    "quantity": [0, 1],
    "price": [0.0, 9_999.99],
    "status": ["closed", "open"],
    "note": [None, "priority"],
})
assert schema.validate(valid).shape == (2, 5)

invalid_fixtures = {
    "quantity": valid.assign(quantity=[-1, 1]),
    "price_lower_bound": valid.assign(price=[-0.01, 4.5]),
    "price_upper_bound": valid.assign(price=[10_000.0, 4.5]),
    "price_finite": valid.assign(price=[np.inf, 4.5]),
    "status": valid.assign(status=["unknown", "open"]),
    "required_key": valid.assign(order_id=[None, 101]),
    "unique_key": valid.assign(order_id=[100, 100]),
}
for expected_evidence, invalid in invalid_fixtures.items():
    try:
        schema.validate(invalid, lazy=True)
    except pa.errors.SchemaErrors as error:
        evidence = error.failure_cases.to_string()
        if expected_evidence == "price_lower_bound":
            assert "greater_than_or_equal_to(0)" in evidence
        elif expected_evidence == "price_upper_bound":
            assert "less_than(10000)" in evidence
        elif expected_evidence == "price_finite":
            assert "finite_price" in evidence
        elif expected_evidence == "unique_key":
            assert "field_uniqueness" in evidence
        elif expected_evidence == "required_key":
            assert "not_nullable" in evidence or "coerce_dtype" in evidence
        else:
            assert expected_evidence in evidence
    else:
        raise AssertionError(
            f"{expected_evidence} fixture should fail validation"
        )
```

The valid fixture includes the exact inclusive lower boundaries and a
value immediately below the exclusive upper boundary. Every rule gets
its own invalid fixture so a learner can identify which check failed.

**Verification evidence:** one valid fixture passes and a separate invalid fixture for each rule fails with the expected column/check evidence.

### Exercise 2 — worked answer

**Learner contract:** Validate the cleaned Day 18 DataFrame immediately before saving. **Sequence:** clean → validate returned frame → write only validated output → re-read/reconcile. **Expected behavior:** a deliberately invalid fixture blocks the write and preserves a useful failure report. **Constraint:** do not catch and discard `SchemaError`/`SchemaErrors`. **Verify:** Use a temporary output path to prove valid data writes/reloads, while an invalid fixture raises before the file exists.

**Reasoning:** Implement this exact contract as written: Validate the cleaned Day 18 DataFrame immediately before saving. Sequence: clean → validate returned frame → write only validated output → re-read/reconcile. Expected behavior: a deliberately invalid fixture blocks the write and preserves a useful failure report. Constraint: do not catch and discard `SchemaError`/`SchemaErrors`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Use a temporary output path to prove valid data writes/reloads, while an invalid fixture raises before the file exists. That connects the answer to turning data contracts into executable schemas and informative failures.

```python
from pathlib import Path
import tempfile


def clean_day18(raw_frame: pd.DataFrame) -> pd.DataFrame:
    result = raw_frame.copy()
    result.columns = [column.strip().lower() for column in result]
    result["name"] = result["name"].astype("string").str.strip()
    result["quantity"] = pd.to_numeric(
        result["quantity"], errors="coerce"
    ).astype("Int64")
    result["event_time"] = pd.to_datetime(
        result["event_time"], errors="coerce", utc=True
    )
    return result.drop_duplicates().reset_index(drop=True)


day18_schema = pa.DataFrameSchema(
    {
        "name": pa.Column("string", nullable=False),
        "quantity": pa.Column("Int64", checks=pa.Check.ge(0), nullable=False),
        "event_time": pa.Column(
            pd.DatetimeTZDtype(unit="ns", tz="UTC"),
            nullable=False,
        ),
    },
    strict=True,
)


def validate_then_save(frame: pd.DataFrame, path: Path) -> pd.DataFrame:
    checked = day18_schema.validate(frame, lazy=True)
    checked.to_csv(path, index=False)
    return checked


raw_day18 = pd.DataFrame(
    {
        "Name": [" Ada ", "Lin"],
        "Quantity": ["2", "0"],
        "Event_Time": [
            "2025-01-01T00:00:00Z",
            "2025-01-02T00:00:00Z",
        ],
    }
)
cleaned_day18 = clean_day18(raw_day18)
with tempfile.TemporaryDirectory() as folder:
    output = Path(folder) / "valid.csv"
    checked = validate_then_save(cleaned_day18, output)
    assert output.exists()
    reloaded = pd.read_csv(output)
    assert reloaded.columns.tolist() == checked.columns.tolist()
    assert reloaded["quantity"].sum() == checked["quantity"].sum()

    invalid_output = Path(folder) / "invalid.csv"
    invalid = cleaned_day18.assign(quantity=[-1, 0])
    try:
        validate_then_save(invalid, invalid_output)
    except pa.errors.SchemaErrors as error:
        failure_report = error.failure_cases
        assert not failure_report.empty
        assert "quantity" in failure_report.to_string()
    else:
        raise AssertionError("invalid data should fail")
    assert not invalid_output.exists()
```

The order is explicit: clean, validate the returned frame, save only
that validated object, reopen, and reconcile. The invalid path keeps
Pandera's failure cases for diagnosis and proves no file was created.

**Verification evidence:** Use a temporary output path to prove valid data writes/reloads, while an invalid fixture raises before the file exists.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict the difference between coercing a value to the schema dtype and validating it without coercion. **Progressive hint:** Coercion transforms compatible representations; validation checks a state. **Verify:** Validate numeric text with/without coercion and assert the coerced dtype/value versus the strict failure; record what changed rather than calling it mere validation.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the difference between coercing a value to the schema dtype and validating it without coercion. Progressive hint: Coercion transforms compatible representations; validation checks a state. Then compare the prediction with this proof target: Validate numeric text with/without coercion and assert the coerced dtype/value versus the strict failure; record what changed rather than calling it mere validation. This makes turning data contracts into executable schemas and informative failures observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Validate numeric text with/without coercion and assert the coerced dtype/value versus the strict failure; record what changed rather than calling it mere validation.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace a row through cleaning, schema validation, and saving. At which boundary must failure stop the write? **Progressive hint:** Validate the actual final frame immediately before persistence. **Verify:** Use a temporary path and event log; assert valid rows reach save only after validation and invalid rows raise before any file/write event.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace a row through cleaning, schema validation, and saving. At which boundary must failure stop the write? Progressive hint: Validate the actual final frame immediately before persistence. Record the named value, shape, label, or iterator position needed to establish: Use a temporary path and event log; assert valid rows reach save only after validation and invalid rows raise before any file/write event. The trace exposes turning data contracts into executable schemas and informative failures directly.

**Evidence to locate in the grouped implementation:** Use a temporary path and event log; assert valid rows reach save only after validation and invalid rows raise before any file/write event.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Create a Pandera schema with non-negative quantity, finite price, and an allowed status set, then validate one good fixture. **Progressive hint:** Derive constraints from stated business rules, not observed values alone. **Verify:** Assert one good fixture returns unchanged meaning, then independently fail negative quantity, nonfinite price, and unknown status with named checks.

**Reasoning:** Implement this exact contract as written: Implementation: Create a Pandera schema with non-negative quantity, finite price, and an allowed status set, then validate one good fixture. Progressive hint: Derive constraints from stated business rules, not observed values alone. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert one good fixture returns unchanged meaning, then independently fail negative quantity, nonfinite price, and unknown status with named checks. That connects the answer to turning data contracts into executable schemas and informative failures.

**Evidence to locate in the grouped implementation:** Assert one good fixture returns unchanged meaning, then independently fail negative quantity, nonfinite price, and unknown status with named checks.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a pipeline that writes output before validating it or catches and discards every schema error. **Progressive hint:** Validation failure is a blocked output, not a warning-only event. **Verify:** Reorder the pipeline and assert invalid data leaves no output file; retain and inspect the schema failure instead of converting it to a warning.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a pipeline that writes output before validating it or catches and discards every schema error. Progressive hint: Validation failure is a blocked output, not a warning-only event. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Reorder the pipeline and assert invalid data leaves no output file; retain and inspect the schema failure instead of converting it to a warning. The diagnosis depends on turning data contracts into executable schemas and informative failures.

**Evidence to locate in the grouped implementation:** Reorder the pipeline and assert invalid data leaves no output file; retain and inspect the schema failure instead of converting it to a warning.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Create invalid fixtures for null, range, category, duplicate-key, and dtype rules; use lazy validation to inspect multiple failures. **Progressive hint:** One failure fixture per rule makes contract coverage auditable. **Verify:** Run lazy validation on fixtures violating all five rule families and assert the failure cases include each expected column/check category.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Create invalid fixtures for null, range, category, duplicate-key, and dtype rules; use lazy validation to inspect multiple failures. Progressive hint: One failure fixture per rule makes contract coverage auditable. Values below, at, and above the named boundary must produce the evidence Run lazy validation on fixtures violating all five rule families and assert the failure cases include each expected column/check category. Those cases show how turning data contracts into executable schemas and informative failures behaves at its edge.

**Evidence to locate in the grouped implementation:** Run lazy validation on fixtures violating all five rule families and assert the failure cases include each expected column/check category.

## Expanded mastery lab solutions

Translate business rules into executable boundary contracts and prove both acceptance and informative failure before persisting data.

### Shared implementation for Exercises 3–4 — Transform versus assert

Coercion can turn compatible text such as `"2"` into integer `2`; it should not
silently invent a value for incompatible text. The final cleaned frame must
validate before any destination is replaced.

### Shared implementation for Exercises 5–7 — Executable business rules

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
