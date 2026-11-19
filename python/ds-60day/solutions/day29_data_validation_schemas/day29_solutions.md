# Day 29 Solutions: Data Validation with Schemas

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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Extend a Pandera schema with documented inclusive/exclusive ranges, allowed categories, nullability, and key uniqueness. **Constraints:** derive each rule from written business meaning and include exact boundary values. **Verify:** one valid fixture passes and a separate invalid fixture for each rule fails with the expected column/check evidence.

**Reasoning:** Each rule comes from a written business meaning, so the schema documents why a value is acceptable, not just which values happened to appear. The boundaries are part of the contract: quantity 0 and price 0.0 pass because the lower bounds are inclusive, 9,999.99 passes and 10,000 fails because the upper bound is exclusive, and `inf` fails the named `finite_price` check. One invalid fixture per rule, validated with `lazy=True`, shows that each rule fails for the expected reason with its own check name in `failure_cases`, so a rule that never fires would be noticed.

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
valid = pd.DataFrame(
    {
        "order_id": [100, 101],
        "quantity": [0, 1],
        "price": [0.0, 9_999.99],
        "status": ["closed", "open"],
        "note": [None, "priority"],
    }
)
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
        raise AssertionError(f"{expected_evidence} fixture should fail validation")
```

The valid fixture includes the exact inclusive lower boundaries and a
value immediately below the exclusive upper boundary. Every rule gets
its own invalid fixture so a learner can identify which check failed.

### Exercise 2: worked answer

**Learner contract:** Validate the cleaned Day 18 DataFrame immediately before saving. **Sequence:** clean → validate returned frame → write only validated output → re-read/reconcile. **Expected behavior:** a deliberately invalid fixture blocks the write and preserves a useful failure report. **Constraint:** do not catch and discard `SchemaError`/`SchemaErrors`. **Verify:** Use a temporary output path to prove valid data writes/reloads, while an invalid fixture raises before the file exists.

**Reasoning:** Validation belongs immediately before the write, on the exact frame that will be saved, so nothing unchecked can reach the file. `validate_then_save` raises before calling `to_csv`, so an invalid frame never creates a file, which the test proves with `invalid_output.exists()`. The `SchemaErrors` object is kept rather than discarded, because its `failure_cases` table names the column, check, and row that failed, and the valid path re-reads the file and reconciles the columns and the quantity total.

```python
from pathlib import Path
import tempfile


def clean_day18(raw_frame: pd.DataFrame) -> pd.DataFrame:
    result = raw_frame.copy()
    result.columns = [column.strip().lower() for column in result]
    result["name"] = result["name"].astype("string").str.strip()
    result["quantity"] = pd.to_numeric(result["quantity"], errors="coerce").astype("Int64")
    result["event_time"] = pd.to_datetime(result["event_time"], errors="coerce", utc=True)
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

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict the difference between coercing a value to the schema dtype and validating it without coercion. **Progressive hint:** Coercion transforms compatible representations; validation checks a state. **Verify:** Validate numeric text with/without coercion and assert the coerced dtype/value versus the strict failure; record what changed rather than calling it mere validation.

**Reasoning:** Coercion and validation do different jobs: coercion converts a compatible representation, such as the text `"2"`, into the schema dtype, while validation only checks the state it is given. Without `coerce=True`, the text column fails the `int64` dtype check; with it, the returned frame holds the integers 2 and 7 while the input frame is unchanged. Text that cannot be converted, such as `"many"`, still fails, so coercion never invents a value; the shared implementation for Exercises 3-4 shows all three cases.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace a row through cleaning, schema validation, and saving. At which boundary must failure stop the write? **Progressive hint:** Validate the actual final frame immediately before persistence. **Verify:** Use a temporary path and event log; assert valid rows reach save only after validation and invalid rows raise before any file/write event.

**Reasoning:** The write must happen only after validation succeeds, so the save function validates first and writes second, and an event log records each step. For the valid frame, the log shows `validated` before `wrote good.csv`; for the invalid frame, validation raises `SchemaErrors` before either event is recorded, and no file exists. The shared implementation for Exercises 3-4 asserts both sequences, which proves that the boundary is the validation call itself.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Create a Pandera schema with non-negative quantity, finite price, and an allowed status set, then validate one good fixture. **Progressive hint:** Derive constraints from stated business rules, not observed values alone. **Verify:** Assert one good fixture returns unchanged meaning, then independently fail negative quantity, nonfinite price, and unknown status with named checks.

**Reasoning:** Each check encodes a stated business rule: quantities cannot be negative, prices must be finite, and statuses come from a fixed list, whatever values happen to appear in a sample. `nullable=False` already rejects missing prices, so the custom check now uses `np.isfinite` to reject infinity, which the earlier `notna()` check did not catch, and naming it `finite_price` makes it identifiable in failure reports. The shared implementation for Exercises 5-7 validates a good row, confirming that coercion kept its meaning, and then fails each of the three rules separately by its check name.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair a pipeline that writes output before validating it or catches and discards every schema error. **Progressive hint:** Validation failure is a blocked output, not a warning-only event. **Verify:** Reorder the pipeline and assert invalid data leaves no output file; retain and inspect the schema failure instead of converting it to a warning.

**Reasoning:** Writing first and validating afterwards means invalid data is already on disk when the check runs, and catching the error with `pass` hides the only evidence that anything went wrong. The repair validates first and lets `SchemaErrors` propagate, so the write never happens, and the caller keeps `failure_cases` for diagnosis. The shared implementation for Exercises 5-7 shows that the buggy version leaves a file of invalid rows behind, and that the repaired version leaves none while keeping the failure report.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Create invalid fixtures for null, range, category, duplicate-key, and dtype rules; use lazy validation to inspect multiple failures. **Progressive hint:** One failure fixture per rule makes contract coverage auditable. **Verify:** Run lazy validation on fixtures violating all five rule families and assert the failure cases include each expected column/check category.

**Reasoning:** A combined fixture with one violation from each rule family (duplicate key, uncoercible dtype, negative quantity, missing price, and unknown status) validated with `lazy=True` collects every failure in one report instead of stopping at the first. Checking that all five check names appear in `failure_cases` proves that every rule family is active. The dtype failure is placed in `order_id` rather than `quantity` because a column that cannot be coerced keeps its text dtype, and a numeric range check on it would then fail with a type error instead of reporting the negative value.

## Expanded mastery lab solutions

Translate business rules into executable boundary contracts and prove both acceptance and informative failure before persisting data.

### Shared implementation for Exercises 3-4: Transform versus assert

Coercion can turn compatible text such as `"2"` into integer `2`; it should not
silently invent a value for incompatible text. The final cleaned frame must
validate before any destination is replaced.

```python
import tempfile
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

text_quantities = pd.DataFrame({"quantity": ["2", "7"]})  # numeric text, dtype object
strict = pa.DataFrameSchema({"quantity": pa.Column(int)})
coercing = pa.DataFrameSchema({"quantity": pa.Column(int, coerce=True)})
try:
    strict.validate(text_quantities)
except pa.errors.SchemaError as error:
    print("without coercion:", error)
else:
    raise AssertionError("text should not pass an int column without coercion")
converted = coercing.validate(text_quantities)
assert str(text_quantities["quantity"].dtype) == "object"  # the input is unchanged
assert str(converted["quantity"].dtype) == "int64"
assert converted["quantity"].tolist() == [2, 7]
try:
    coercing.validate(pd.DataFrame({"quantity": ["2", "many"]}))
except (pa.errors.SchemaError, pa.errors.SchemaErrors) as error:
    print("incompatible text is still rejected:", type(error).__name__)
else:
    raise AssertionError("coercion must not invent a value for 'many'")

events: list[str] = []
quantity_schema = pa.DataFrameSchema({"quantity": pa.Column(int, pa.Check.ge(0))}, strict=True)


def save_validated(frame: pd.DataFrame, path: Path) -> None:
    checked = quantity_schema.validate(frame, lazy=True)
    events.append("validated")
    checked.to_csv(path, index=False)
    events.append(f"wrote {path.name}")


with tempfile.TemporaryDirectory() as folder:
    good_path = Path(folder) / "good.csv"
    bad_path = Path(folder) / "bad.csv"
    save_validated(pd.DataFrame({"quantity": [1, 0]}), good_path)
    assert events == ["validated", "wrote good.csv"] and good_path.exists()
    try:
        save_validated(pd.DataFrame({"quantity": [-1]}), bad_path)
    except pa.errors.SchemaErrors as error:
        print(error.failure_cases[["column", "check", "failure_case"]])
    else:
        raise AssertionError("a negative quantity must stop the write")
    assert events == ["validated", "wrote good.csv"]  # nothing recorded for the bad frame
    assert not bad_path.exists()
```

### Shared implementation for Exercises 5-7: Executable business rules

```python
import numpy as np
import pandas as pd
import pandera.pandas as pa

ORDER_SCHEMA = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, nullable=False, unique=True),
        "quantity": pa.Column(int, pa.Check.ge(0), nullable=False),
        "price": pa.Column(
            float,
            checks=[
                pa.Check.ge(0),
                pa.Check(lambda values: np.isfinite(values), name="finite_price"),
            ],
            nullable=False,
        ),
        "status": pa.Column(str, pa.Check.isin(["new", "paid", "shipped"])),
    },
    strict=True,
    coerce=True,
)

valid = pd.DataFrame({"order_id": [1], "quantity": ["2"], "price": [4.5], "status": ["paid"]})
checked = ORDER_SCHEMA.validate(valid, lazy=True)
assert checked.loc[0, "quantity"] == 2
assert (checked.loc[0, "price"], checked.loc[0, "status"]) == (4.5, "paid")

single_rule_fixtures = {
    "greater_than_or_equal_to(0)": valid.assign(quantity=[-1]),
    "finite_price": valid.assign(price=[float("inf")]),
    "isin(['new', 'paid', 'shipped'])": valid.assign(status=["lost"]),
}
for check_name, broken in single_rule_fixtures.items():
    try:
        ORDER_SCHEMA.validate(broken, lazy=True)
    except pa.errors.SchemaErrors as error:
        assert check_name in error.failure_cases["check"].astype(str).tolist()
    else:
        raise AssertionError(f"{check_name} should fail")

invalid = pd.DataFrame(
    {
        "order_id": [1, 1, "x"],  # Duplicate key and an uncoercible dtype.
        "quantity": [-1, 2, 3],  # Range violation.
        "price": [1.0, None, 2.0],  # Null violation.
        "status": ["unknown", "paid", "new"],  # Category violation.
    }
)
try:
    ORDER_SCHEMA.validate(invalid, lazy=True)
except pa.errors.SchemaErrors as error:
    # Preserve bounded failure cases for diagnosis; do not write invalid data.
    failed_checks = set(error.failure_cases["check"].astype(str))
    print(sorted(failed_checks))
else:
    raise AssertionError("invalid rows should fail the schema")
assert {
    "field_uniqueness",
    "coerce_dtype('int64')",
    "greater_than_or_equal_to(0)",
    "not_nullable",
    "isin(['new', 'paid', 'shipped'])",
} <= failed_checks

import tempfile
from pathlib import Path


def write_then_validate(frame: pd.DataFrame, path: Path) -> None:
    """Bug: the file exists before the check runs, and the failure is discarded."""
    frame.to_csv(path, index=False)
    try:
        ORDER_SCHEMA.validate(frame, lazy=True)
    except pa.errors.SchemaErrors:
        pass


def validate_then_write(frame: pd.DataFrame, path: Path) -> pd.DataFrame:
    checked = ORDER_SCHEMA.validate(frame, lazy=True)  # raises before any write
    checked.to_csv(path, index=False)
    return checked


with tempfile.TemporaryDirectory() as folder:
    buggy_path = Path(folder) / "buggy.csv"
    write_then_validate(invalid, buggy_path)
    assert buggy_path.exists()  # invalid rows were persisted silently
    repaired_path = Path(folder) / "repaired.csv"
    try:
        validate_then_write(invalid, repaired_path)
    except pa.errors.SchemaErrors as error:
        kept_report = error.failure_cases  # retained for diagnosis
    else:
        raise AssertionError("invalid rows must block the write")
    assert not repaired_path.exists() and not kept_report.empty
```

A production save function should write only `checked`. If validation fails,
surface the report and leave any previous valid destination untouched.
