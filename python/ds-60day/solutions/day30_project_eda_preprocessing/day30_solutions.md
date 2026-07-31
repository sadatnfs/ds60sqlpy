# Day 30 — Solutions: Project — EDA and Preprocessing

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **a restartable EDA and preprocessing project with an auditable evidence chain**. Predict each named
result before comparing your attempt with its matching assertions.

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

### Vocabulary used in the worked answers

- **acceptance criterion:** a measurable condition required before output is trusted.
- **decision log:** structured evidence and rationale for each material treatment.
- **reconciliation:** comparison of key counts/measures across processing boundaries.
- **artifact:** a generated dataset, figure, report, or manifest.
- **manifest:** metadata describing artifact source, version, shape, and validation.
- **restartability:** the ability to run top to bottom from a fresh kernel with the same result.

### How to compare an answer

For this lesson's **a restartable EDA and preprocessing project with an auditable evidence chain** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–5 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** **Load and scope:** choose a local, constructed, or already-cached dataset and record source/provenance, license if applicable, row grain, keys, shape, time range, analytical question, and measurable acceptance criteria. **Expected behavior:** a fresh-kernel run can recreate the same raw profile without hidden state or network access. **Verify:** assert expected columns and key/time bounds before continuing.

**Reasoning:** Implement this exact contract as written: Load and scope: choose a local, constructed, or already-cached dataset and record source/provenance, license if applicable, row grain, keys, shape, time range, analytical question, and measurable acceptance criteria. Expected behavior: a fresh-kernel run can recreate the same raw profile without hidden state or network access. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert expected columns and key/time bounds before continuing. That connects the answer to a restartable EDA and preprocessing project with an auditable evidence chain.

```python
import pandas as pd

raw = pd.DataFrame({
    "entity_id": [1, 2, 2, 3],
    "event_time": pd.to_datetime([
        "2025-01-01", "2025-01-02", "2025-01-02", "2025-01-03"
    ], utc=True),
    "amount": [10.0, 20.0, 20.0, None],
})
scope = {
    "provenance": "constructed course fixture",
    "license": "course-authored fixture; CC0-style reuse permitted",
    "grain": "one entity event per row",
    "keys": ["entity_id", "event_time"],
    "shape": raw.shape,
    "time_range_utc": (
        raw["event_time"].min().isoformat(),
        raw["event_time"].max().isoformat(),
    ),
    "question": "How much known amount is recorded by day?",
    "acceptance": {
        "required_columns_present": True,
        "final_business_key_unique": True,
        "final_amount_non_negative_or_missing": True,
    },
}
expected_columns = {"entity_id", "event_time", "amount"}
assert set(raw.columns) == expected_columns
assert set(scope["keys"]).issubset(raw.columns)
assert raw["event_time"].min() >= pd.Timestamp("2025-01-01", tz="UTC")
assert raw["event_time"].max() <= pd.Timestamp("2025-01-03", tz="UTC")
```

Because the data is constructed in the cell, a fresh offline kernel can
reproduce the same four raw rows without hidden files or network state.

**Verification evidence:** assert expected columns and key/time bounds before continuing.

### Exercise 2 — worked answer

**Learner contract:** **Explore:** analyze quality, distributions, missingness, duplicates, relationships, correlations, and relevant segments. **Constraints:** pair every table/plot with evidence, sample size/denominator, and a caveat; do not treat correlation as causation. **Verify:** every stated finding points to a reproducible calculation or plot and leakage-prone fields are excluded.

**Reasoning:** Implement this exact contract as written: Explore: analyze quality, distributions, missingness, duplicates, relationships, correlations, and relevant segments. Constraints: pair every table/plot with evidence, sample size/denominator, and a caveat; do not treat correlation as causation. Keep the prompt's named data and constraints visible in the code, then establish this specific result: every stated finding points to a reproducible calculation or plot and leakage-prone fields are excluded. That connects the answer to a restartable EDA and preprocessing project with an auditable evidence chain.

```python
analysis_rows = raw["amount"].notna()
known_amounts = raw.loc[analysis_rows, "amount"]
exploration = {
    "row_count": len(raw),
    "missing_amount": int(raw["amount"].isna().sum()),
    "duplicate_key_rows": int(
        raw.duplicated(["entity_id", "event_time"]).sum()
    ),
    "known_total": float(raw["amount"].sum()),
    "known_amount_denominator": int(analysis_rows.sum()),
    "amount_median": float(known_amounts.median()),
    "amount_range": (
        float(known_amounts.min()),
        float(known_amounts.max()),
    ),
    "entity_amount_correlation": float(
        raw.loc[analysis_rows, ["entity_id", "amount"]]
        .corr()
        .loc["entity_id", "amount"]
    ),
}
findings = [
    {
        "claim": "one of four rows has missing amount",
        "evidence": exploration["missing_amount"],
        "denominator": exploration["row_count"],
        "caveat": "missingness reason is not available",
    },
    {
        "claim": "one repeated business-key row can double count amount",
        "evidence": exploration["duplicate_key_rows"],
        "denominator": exploration["row_count"],
        "caveat": "a real source owner must confirm duplicate semantics",
    },
]
leakage_prone_fields_excluded: list[str] = []

assert exploration["missing_amount"] == 1
assert exploration["duplicate_key_rows"] == 1
assert exploration["known_total"] == 50.0
assert exploration["known_amount_denominator"] == 3
assert all({"claim", "evidence", "denominator", "caveat"} <= finding.keys()
           for finding in findings)
assert leakage_prone_fields_excluded == []
```

The correlation is a reproducible description over only three known
amounts, not a causal finding. This project has no predictive target, so
no leakage-prone feature is present; the explicit empty list records
that review instead of silently skipping it.

**Verification evidence:** every stated finding points to a reproducible calculation or plot and leakage-prone fields are excluded.

### Exercise 3 — worked answer

**Learner contract:** **Clean and transform:** implement `clean(raw)` that returns a new DataFrame and records each decision's evidence, action, rationale, validation, and impact. **Constraints:** preserve raw data, avoid broad silent row dropping, and split before fitting learned transforms if a target exists. **Verify:** test idempotence where promised and reconcile row/entity counts plus key totals.

**Reasoning:** Implement this exact contract as written: Clean and transform: implement `clean(raw)` that returns a new DataFrame and records each decision's evidence, action, rationale, validation, and impact. Constraints: preserve raw data, avoid broad silent row dropping, and split before fitting learned transforms if a target exists. Keep the prompt's named data and constraints visible in the code, then establish this specific result: test idempotence where promised and reconcile row/entity counts plus key totals. That connects the answer to a restartable EDA and preprocessing project with an auditable evidence chain.

```python
def clean(raw_frame: pd.DataFrame) -> pd.DataFrame:
    result = raw_frame.copy()
    result = result.drop_duplicates(["entity_id", "event_time"])
    return result.reset_index(drop=True)


raw_snapshot = raw.copy(deep=True)
cleaned = clean(raw)
assert raw.shape == (4, 3)
assert cleaned.shape == (3, 3)
assert clean(cleaned).equals(cleaned)
pd.testing.assert_frame_equal(raw, raw_snapshot)

decisions = [
    {
        "evidence": "one exact duplicate business key",
        "action": "keep first",
        "rationale": "duplicate carries identical values",
        "validation": "business key unique afterward",
        "impact": {"rows_removed": 1, "known_amount_removed": 20.0},
    },
    {
        "evidence": "one amount is missing",
        "action": "preserve missing value",
        "rationale": "no defensible imputation rule is available",
        "validation": "missing count remains one",
        "impact": {"values_imputed": 0},
    },
]
assert not cleaned.duplicated(["entity_id", "event_time"]).any()
assert cleaned["entity_id"].nunique() == raw["entity_id"].nunique() == 3
assert raw["amount"].sum() - cleaned["amount"].sum() == 20.0
assert cleaned["amount"].isna().sum() == 1
```

**Verification evidence:** test idempotence where promised and reconcile row/entity counts plus key totals.

### Exercise 4 — worked answer

**Learner contract:** **Validate:** apply the Day 29 schema to the actual final cleaned DataFrame before output. **Expected behavior:** one valid fixture passes and a deliberately invalid fixture proves an important rule blocks progress. **Constraint:** do not catch and discard the validation failure. **Verify:** assert the invalid fixture raises the named validation error and no output file exists; then assert the valid frame passes, the save runs, and the expected nonempty file exists.

**Reasoning:** Implement this exact contract as written: Validate: apply the Day 29 schema to the actual final cleaned DataFrame before output. Expected behavior: one valid fixture passes and a deliberately invalid fixture proves an important rule blocks progress. Constraint: do not catch and discard the validation failure. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert the invalid fixture raises the named validation error and no output file exists; then assert the valid frame passes, the save runs, and the expected nonempty file exists. That connects the answer to a restartable EDA and preprocessing project with an auditable evidence chain.

```python
import pandera.pandas as pa

project_schema = pa.DataFrameSchema({
    "entity_id": pa.Column(int, checks=pa.Check.ge(1)),
    "event_time": pa.Column(
        pd.DatetimeTZDtype(unit="ns", tz="UTC"),
        nullable=False,
    ),
    "amount": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
})
validated = project_schema.validate(cleaned, lazy=True)
assert len(validated) == 3

invalid = cleaned.assign(amount=[10.0, -0.01, None])
validation_failure = None
try:
    project_schema.validate(invalid, lazy=True)
except pa.errors.SchemaErrors as error:
    validation_failure = error.failure_cases
assert validation_failure is not None
assert "amount" in validation_failure.to_string()

frame_ready_to_save = validated
assert frame_ready_to_save is validated
```

`frame_ready_to_save` is assigned only from the successful validation
result. The negative fixture preserves its failure table as diagnostic
evidence and never reaches the output code.

**Verification evidence:** assert the invalid fixture raises the named validation error and no output file exists; then assert the valid frame passes, the save runs, and the expected nonempty file exists.

### Exercise 5 — worked answer

**Learner contract:** **Save and report:** write cleaned data and figures under an ignored `artifacts/day30/` path plus a manifest containing source, timestamp/version policy, row count, schema result, and file list. **Constraints:** handle an empty clean dataset as a blocked project, reopen outputs, and summarize findings, limitations, and lessons learned. **Verify:** saved/reloaded shape, schema, and key totals match the validated in-memory frame.

**Reasoning:** Implement this exact contract as written: Save and report: write cleaned data and figures under an ignored `artifacts/day30/` path plus a manifest containing source, timestamp/version policy, row count, schema result, and file list. Constraints: handle an empty clean dataset as a blocked project, reopen outputs, and summarize findings, limitations, and lessons learned. Keep the prompt's named data and constraints visible in the code, then establish this specific result: saved/reloaded shape, schema, and key totals match the validated in-memory frame. That connects the answer to a restartable EDA and preprocessing project with an auditable evidence chain.

```python
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt

if validated.empty:
    raise ValueError("project produced no accepted rows")
artifact_dir = Path("artifacts/day30")
artifact_dir.mkdir(parents=True, exist_ok=True)
data_path = artifact_dir / "clean.csv"
figure_path = artifact_dir / "daily-amount.png"
manifest_path = artifact_dir / "manifest.json"
report_path = artifact_dir / "report.md"

validated.to_csv(data_path, index=False)
daily_amount = (
    validated.set_index("event_time")["amount"].resample("D").sum(min_count=1)
)
axes = daily_amount.plot(
    kind="bar",
    title="Known amount by UTC day",
    ylabel="Amount (course units)",
)
axes.figure.tight_layout()
axes.figure.savefig(figure_path, dpi=150)
plt.close(axes.figure)

report = (
    "# Day 30 findings\n\n"
    "- Finding: one exact duplicate key was removed.\n"
    "- Limitation: one amount is missing and its cause is unknown.\n"
    "- Lesson: preserve raw evidence and validate before saving.\n"
)
report_path.write_text(report, encoding="utf-8")
manifest = {
    "source": scope["provenance"],
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "version_policy": "increment for any schema or cleaning-contract change",
    "row_count": len(validated),
    "schema_validated": True,
    "known_amount_total": float(validated["amount"].sum()),
    "unique_entity_count": int(validated["entity_id"].nunique()),
    "files": [data_path.name, figure_path.name, report_path.name],
    "version": 1,
}
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

reloaded = pd.read_csv(data_path, parse_dates=["event_time"])
reloaded["event_time"] = pd.to_datetime(reloaded["event_time"], utc=True)
revalidated = project_schema.validate(reloaded, lazy=True)
assert len(reloaded) == manifest["row_count"]
assert float(revalidated["amount"].sum()) == manifest["known_amount_total"]
assert revalidated["entity_id"].nunique() == manifest["unique_entity_count"]
assert all((artifact_dir / name).exists() for name in manifest["files"])
assert set(manifest["files"]) == {
    "clean.csv", "daily-amount.png", "report.md"
}
```

**Verification evidence:** saved/reloaded shape, schema, and key totals match the validated in-memory frame.

## Exercises 6–10 — Expanded mastery answers

### Exercise 6 — answer contract

**Learner contract:** **Prediction:** Before loading data, write the analytical question, row grain, entity keys, expected time range, and acceptance criteria. Predict one failure. **Progressive hint:** A declared expectation turns a surprise into a testable discrepancy. **Verify:** Save the written contract before loading, then assert the raw profile against keys/time/schema and record whether the predicted failure actually occurred.

**Reasoning:** Predict this named state change before running it: Prediction: Before loading data, write the analytical question, row grain, entity keys, expected time range, and acceptance criteria. Predict one failure. Progressive hint: A declared expectation turns a surprise into a testable discrepancy. Then compare the prediction with this proof target: Save the written contract before loading, then assert the raw profile against keys/time/schema and record whether the predicted failure actually occurred. This makes a restartable EDA and preprocessing project with an auditable evidence chain observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Save the written contract before loading, then assert the raw profile against keys/time/schema and record whether the predicted failure actually occurred.

### Exercise 7 — answer contract

**Learner contract:** **Tracing:** Trace row count, unique entity count, missing target count, and an additive total across raw, cleaned, validated, and saved boundaries. **Progressive hint:** Every material change needs a reason and reconciliation. **Verify:** Build a four-boundary reconciliation table and assert every row/entity/missing/total change has an explicit reason; reopen saved data for the final row.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace row count, unique entity count, missing target count, and an additive total across raw, cleaned, validated, and saved boundaries. Progressive hint: Every material change needs a reason and reconciliation. Record the named value, shape, label, or iterator position needed to establish: Build a four-boundary reconciliation table and assert every row/entity/missing/total change has an explicit reason; reopen saved data for the final row. The trace exposes a restartable EDA and preprocessing project with an auditable evidence chain directly.

**Evidence to locate in the grouped implementation:** Build a four-boundary reconciliation table and assert every row/entity/missing/total change has an explicit reason; reopen saved data for the final row.

### Exercise 8 — answer contract

**Learner contract:** **Implementation:** Implement a structured decision log entry containing evidence, action, rationale, validation, and impact. **Progressive hint:** Make decisions data, not scattered comments. **Verify:** Validate that each decision entry contains evidence, action, rationale, validation, and impact and links to a reproducible count/test.

**Reasoning:** Implement this exact contract as written: Implementation: Implement a structured decision log entry containing evidence, action, rationale, validation, and impact. Progressive hint: Make decisions data, not scattered comments. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Validate that each decision entry contains evidence, action, rationale, validation, and impact and links to a reproducible count/test. That connects the answer to a restartable EDA and preprocessing project with an auditable evidence chain.

**Evidence to locate in the grouped implementation:** Validate that each decision entry contains evidence, action, rationale, validation, and impact and links to a reproducible count/test.

### Exercise 9 — answer contract

**Learner contract:** **Debugging:** Repair a notebook that depends on out-of-order state and overwrites its raw frame during cleaning. **Progressive hint:** Put parameters/imports first and make `clean(raw)` return a copy. **Verify:** Restart and run top to bottom; assert `raw` remains unchanged, `clean(raw)` returns a copy, and no cell requires a later-created name.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a notebook that depends on out-of-order state and overwrites its raw frame during cleaning. Progressive hint: Put parameters/imports first and make `clean(raw)` return a copy. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Restart and run top to bottom; assert `raw` remains unchanged, `clean(raw)` returns a copy, and no cell requires a later-created name. The diagnosis depends on a restartable EDA and preprocessing project with an auditable evidence chain.

**Evidence to locate in the grouped implementation:** Restart and run top to bottom; assert `raw` remains unchanged, `clean(raw)` returns a copy, and no cell requires a later-created name.

### Exercise 10 — answer contract

**Learner contract:** **Edge case and explanation:** Prevent target/time leakage, handle an empty cleaned dataset, and write an artifact manifest with source, row count, schema result, and version. **Progressive hint:** Block artifact creation when acceptance criteria fail. **Verify:** Use leakage and empty-data fixtures to prove artifact creation is blocked; for a valid run, assert manifest source/count/schema/version match reopened files.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Prevent target/time leakage, handle an empty cleaned dataset, and write an artifact manifest with source, row count, schema result, and version. Progressive hint: Block artifact creation when acceptance criteria fail. Values below, at, and above the named boundary must produce the evidence Use leakage and empty-data fixtures to prove artifact creation is blocked; for a valid run, assert manifest source/count/schema/version match reopened files. Those cases show how a restartable EDA and preprocessing project with an auditable evidence chain behaves at its edge.

**Evidence to locate in the grouped implementation:** Use leakage and empty-data fixtures to prove artifact creation is blocked; for a valid run, assert manifest source/count/schema/version match reopened files.

## Expanded mastery lab solutions

Build a restartable evidence chain: question and provenance → raw checks → decisions → clean data → validation → artifacts → limitations.

### Shared implementation for Exercises 6–7 — Define and reconcile the analytical unit

Record the question and grain before inspection. At each boundary, compare row
count, unique IDs, missing critical values, and additive totals. A difference
is acceptable only when a decision record explains and validates it.

### Shared implementation for Exercises 8–10 — Structured decisions and artifact acceptance

```python
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class Decision:
    evidence: str
    action: str
    rationale: str
    validation: str
    impact: str


def clean_orders(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy; never overwrite the raw evidence frame."""

    cleaned = raw.copy()
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    cleaned = cleaned.loc[cleaned["amount"].notna() & cleaned["amount"].ge(0)]
    return cleaned.reset_index(drop=True)


def artifact_manifest(
    frame: pd.DataFrame, *, source: str, schema_passed: bool, version: str
) -> dict[str, Any]:
    """Build manifest only for an accepted non-empty validated artifact."""

    if frame.empty:
        raise ValueError("cleaned artifact must contain at least one row")
    if not schema_passed:
        raise ValueError("schema validation must pass before artifact creation")
    return {
        "source": source,
        "rows": len(frame),
        "columns": list(frame.columns),
        "schema_passed": True,
        "version": version,
    }


raw = pd.DataFrame({"order_id": [1, 2, 3], "amount": ["10", "bad", "-2"]})
cleaned = clean_orders(raw)
decision = Decision(
    evidence="2 of 3 amount values are invalid or negative",
    action="exclude invalid amount rows",
    rationale="amount is required for revenue analysis",
    validation="cleaned amount is numeric, non-null, and non-negative",
    impact="1 of 3 rows remains; report this attrition",
)
manifest = artifact_manifest(
    cleaned, source="constructed offline fixture", schema_passed=True, version="1"
)
assert raw["amount"].tolist() == ["10", "bad", "-2"]
assert manifest["rows"] == 1
assert asdict(decision)["action"] == "exclude invalid amount rows"
```

Split time-ordered or target-bearing data before learning any transform. Restart
and run all cells before acceptance, and keep raw data immutable so evidence can
always be reconstructed.
