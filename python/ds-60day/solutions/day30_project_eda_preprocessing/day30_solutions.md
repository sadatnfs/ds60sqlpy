# Day 30 Solutions: Project: Reproducible EDA and Preprocessing

**Offline teaching data:** The [original synthetic fixtures](../../../fixtures/README.md) replace first-run sample-data downloads. Their values are not historical or observational evidence. Keep numerical conclusions scoped to the declared teaching input.


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

## Exercises 1-5: Worked answers

### Exercise 1: worked answer

**Learner contract:** **Load and scope:** choose a local, constructed, or already-cached dataset and record source/provenance, license if applicable, row grain, keys, shape, time range, analytical question, and measurable acceptance criteria. **Expected behavior:** a fresh-kernel run can recreate the same raw profile without hidden state or network access. **Verify:** assert expected columns and key/time bounds before continuing.

**Reasoning:** Recording scope before analysis (provenance, license, grain, keys, time range, question, and acceptance criteria) turns the project's assumptions into values that later steps can check. Constructing the data inside the cell means a fresh kernel without network access rebuilds exactly the same four rows, so the profile is reproducible. The assertions check the expected columns, that the declared keys exist, and that every event falls inside the stated UTC time range, all before any cleaning happens.

```python
import pandas as pd

raw = pd.DataFrame(
    {
        "entity_id": [1, 2, 2, 3],
        "event_time": pd.to_datetime(
            ["2025-01-01", "2025-01-02", "2025-01-02", "2025-01-03"], utc=True
        ),
        "amount": [10.0, 20.0, 20.0, None],
    }
)
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

### Exercise 2: worked answer

**Learner contract:** **Explore:** analyze quality, distributions, missingness, duplicates, relationships, correlations, and relevant segments. **Constraints:** pair every table/plot with evidence, sample size/denominator, and a caveat; do not treat correlation as causation. **Verify:** every stated finding points to a reproducible calculation or plot and leakage-prone fields are excluded.

**Reasoning:** Every finding is stored with its evidence, denominator, and caveat, so a reader can see how much data supports it: one missing amount out of four rows, one repeated key out of four rows. The amount statistics use only the three known values and say so through `known_amount_denominator`, and the correlation is recorded as a description of three points, not as a causal claim. The empty `leakage_prone_fields_excluded` list documents that the leakage review happened: this project has no prediction target, so there was nothing to exclude.

```python
analysis_rows = raw["amount"].notna()
known_amounts = raw.loc[analysis_rows, "amount"]
exploration = {
    "row_count": len(raw),
    "missing_amount": int(raw["amount"].isna().sum()),
    "duplicate_key_rows": int(raw.duplicated(["entity_id", "event_time"]).sum()),
    "known_total": float(raw["amount"].sum()),
    "known_amount_denominator": int(analysis_rows.sum()),
    "amount_median": float(known_amounts.median()),
    "amount_range": (
        float(known_amounts.min()),
        float(known_amounts.max()),
    ),
    "entity_amount_correlation": float(
        raw.loc[analysis_rows, ["entity_id", "amount"]].corr().loc["entity_id", "amount"]
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
assert all({"claim", "evidence", "denominator", "caveat"} <= finding.keys() for finding in findings)
assert leakage_prone_fields_excluded == []
```

The correlation is a reproducible description over only three known
amounts, not a causal finding. This project has no predictive target, so
no leakage-prone feature is present; the explicit empty list records
that review instead of silently skipping it.

### Exercise 3: worked answer

**Learner contract:** **Clean and transform:** implement `clean(raw)` that returns a new DataFrame and records each decision's evidence, action, rationale, validation, and impact. **Constraints:** preserve raw data, avoid broad silent row dropping, and split before fitting learned transforms if a target exists. **Verify:** test idempotence where promised and reconcile row/entity counts plus key totals.

**Reasoning:** `clean` returns a new frame and never changes `raw`, which the snapshot comparison proves, so the original evidence is always available for a rerun. Each decision is recorded as data with its evidence, action, rationale, validation, and impact, and the impact numbers are checked against the frames: one row and 20.0 of known amount removed, three entities before and after, and the missing amount preserved rather than imputed. Calling `clean` on its own output returns the same frame, which proves the promised idempotence.

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

### Exercise 4: worked answer

**Learner contract:** **Validate:** apply the Day 29 schema to the actual final cleaned DataFrame before output. **Expected behavior:** one valid fixture passes and a deliberately invalid fixture proves an important rule blocks progress. **Constraint:** do not catch and discard the validation failure. **Verify:** assert the invalid fixture raises the named validation error and no output file exists; then assert the valid frame passes, the save runs, and the expected nonempty file exists.

**Reasoning:** The schema is applied to the actual cleaned frame, and only the object returned by a successful `validate` call continues to the save step. A deliberately invalid fixture with a negative amount proves that the most important rule really blocks progress, and its failure table is kept as evidence instead of being swallowed. `lazy=True` collects every failure in one report, so a reviewer sees all the problems at once.

```python
import pandera.pandas as pa

project_schema = pa.DataFrameSchema(
    {
        "entity_id": pa.Column(int, checks=pa.Check.ge(1)),
        "event_time": pa.Column(
            pd.DatetimeTZDtype(unit="ns", tz="UTC"),
            nullable=False,
        ),
        "amount": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
    }
)
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

### Exercise 5: worked answer

**Learner contract:** **Save and report:** write cleaned data and figures under an ignored `artifacts/day30/` path plus a manifest containing source, timestamp/version policy, row count, schema result, and file list. **Constraints:** handle an empty clean dataset as a blocked project, reopen outputs, and summarize findings, limitations, and lessons learned. **Verify:** saved/reloaded shape, schema, and key totals match the validated in-memory frame.

**Reasoning:** The outputs go to the ignored `artifacts/day30/` directory, and an empty result stops the project with a `ValueError` instead of producing empty files that look like success. The manifest records the source, generation time, version policy, row count, schema result, key totals, and file list, so a later reader can check the artifacts without rerunning the notebook. Reopening the saved CSV, restoring the UTC timestamps, and validating again proves that what was written still satisfies the contract and matches the manifest.

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
daily_amount = validated.set_index("event_time")["amount"].resample("D").sum(min_count=1)
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
assert set(manifest["files"]) == {"clean.csv", "daily-amount.png", "report.md"}
```

## Exercises 6-10: Expanded mastery answers

### Exercise 6: answer contract

**Learner contract:** **Prediction:** Before loading data, write the analytical question, row grain, entity keys, expected time range, and acceptance criteria. Predict one failure. **Progressive hint:** A declared expectation turns a surprise into a testable discrepancy. **Verify:** Save the written contract before loading, then assert the raw profile against keys/time/schema and record whether the predicted failure actually occurred.

**Reasoning:** Writing the question, grain, keys, expected time range, and acceptance criteria before looking at the data turns every later surprise into a measurable discrepancy instead of a vague impression. The shared implementation for Exercises 6-7 saves the contract to a file first, then checks the loaded data against it and records whether the predicted failure, a non-unique business key, actually occurred. It did, which justifies the deduplication decision before any cleaning code exists.

### Exercise 7: answer contract

**Learner contract:** **Tracing:** Trace row count, unique entity count, missing target count, and an additive total across raw, cleaned, validated, and saved boundaries. **Progressive hint:** Every material change needs a reason and reconciliation. **Verify:** Build a four-boundary reconciliation table and assert every row/entity/missing/total change has an explicit reason; reopen saved data for the final row.

**Reasoning:** Measuring the same four quantities (rows, unique entities, missing amounts, and the amount total) at the raw, cleaned, validated, and saved boundaries shows exactly where the data changes. In the shared implementation for Exercises 6-7, only the cleaning step changes anything, one row and 20.0 of amount for the removed duplicate, and its reason says so, while the other boundaries are explicitly labelled as unchanged. The saved row is measured from the reopened file rather than from the in-memory frame, so the last step is real evidence.

### Exercise 8: answer contract

**Learner contract:** **Implementation:** Implement a structured decision log entry containing evidence, action, rationale, validation, and impact. **Progressive hint:** Make decisions data, not scattered comments. **Verify:** Validate that each decision entry contains evidence, action, rationale, validation, and impact and links to a reproducible count/test.

**Reasoning:** A decision recorded as a frozen dataclass has a fixed set of fields, so an entry without a rationale or a validation cannot be created, and `asdict` turns it into data that can be saved or tested. Linking the evidence text to a count computed from the data, 2 of 3 invalid amounts, means the log can be re-checked whenever the input changes. The shared implementation for Exercises 8-10 asserts that every required field is present and nonempty and that the stated count matches the data.

### Exercise 9: answer contract

**Learner contract:** **Debugging:** Repair a notebook that depends on out-of-order state and overwrites its raw frame during cleaning. **Progressive hint:** Put parameters/imports first and make `clean(raw)` return a copy. **Verify:** Restart and run top to bottom; assert `raw` remains unchanged, `clean(raw)` returns a copy, and no cell requires a later-created name.

**Reasoning:** A notebook that depends on cells run out of order works only in its author's current session; after a restart, a cell that uses a name created further down fails with `NameError`. The shared implementation for Exercises 8-10 imitates restart-and-run-all by executing the cells in order in a fresh namespace, which succeeds, and in the broken order, which raises `NameError`. `clean_orders` returns a copy, so `raw` is identical before and after cleaning, and rerunning any cell gives the same result.

### Exercise 10: answer contract

**Learner contract:** **Edge case and explanation:** Prevent target/time leakage, handle an empty cleaned dataset, and write an artifact manifest with source, row count, schema result, and version. **Progressive hint:** Block artifact creation when acceptance criteria fail. **Verify:** Use leakage and empty-data fixtures to prove artifact creation is blocked; for a valid run, assert manifest source/count/schema/version match reopened files.

**Reasoning:** Artifact creation is the last gate, so it refuses to run when acceptance fails: an empty cleaned frame or a failed schema raises `ValueError` instead of writing a manifest. Leakage is blocked by checking the feature list against the target and against fields known only after the outcome, and by checking that every training row comes before every evaluation row in time. For the valid run, the shared implementation for Exercises 8-10 asserts the manifest's source, row count, schema result, and version exactly.

## Expanded mastery lab solutions

Build a restartable evidence chain: question and provenance → raw checks → decisions → clean data → validation → artifacts → limitations.

### Shared implementation for Exercises 6-7: Define and reconcile the analytical unit

Record the question and grain before inspection. At each boundary, compare row
count, unique IDs, missing critical values, and additive totals. A difference
is acceptable only when a decision record explains and validates it.

```python
import json
from pathlib import Path

import pandas as pd

contract = {
    "question": "How much known amount is recorded by day?",
    "grain": "one entity event per row",
    "keys": ["entity_id", "event_time"],
    "time_range_utc": ["2025-01-01", "2025-01-03"],
    "required_columns": ["entity_id", "event_time", "amount"],
    "predicted_failure": "the business key is not unique in the raw data",
}
contract_path = Path("artifacts/day30/contract.json")
contract_path.parent.mkdir(parents=True, exist_ok=True)
contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")  # before loading

raw_events = pd.DataFrame(
    {
        "entity_id": [1, 2, 2, 3],
        "event_time": pd.to_datetime(
            ["2025-01-01", "2025-01-02", "2025-01-02", "2025-01-03"], utc=True
        ),
        "amount": [10.0, 20.0, 20.0, None],
    }
)
saved_contract = json.loads(contract_path.read_text(encoding="utf-8"))
assert set(saved_contract["required_columns"]) <= set(raw_events.columns)
start, end = (pd.Timestamp(value, tz="UTC") for value in saved_contract["time_range_utc"])
assert raw_events["event_time"].between(start, end).all()
observed = bool(raw_events.duplicated(saved_contract["keys"]).any())
print({"predicted_failure": saved_contract["predicted_failure"], "observed": observed})
assert observed


def boundary_profile(frame: pd.DataFrame) -> dict[str, float]:
    return {
        "rows": len(frame),
        "entities": int(frame["entity_id"].nunique()),
        "missing_amount": int(frame["amount"].isna().sum()),
        "amount_total": float(frame["amount"].sum()),
    }


deduplicated = raw_events.drop_duplicates(contract["keys"]).reset_index(drop=True)
validated_events = deduplicated[deduplicated["amount"].isna() | deduplicated["amount"].ge(0)]
saved_path = Path("artifacts/day30/reconciled.csv")
validated_events.to_csv(saved_path, index=False)
saved_events = pd.read_csv(saved_path)  # measure the reopened file
reconciliation = pd.DataFrame(
    [
        {"boundary": "raw", **boundary_profile(raw_events), "reason": "source as loaded"},
        {
            "boundary": "cleaned",
            **boundary_profile(deduplicated),
            "reason": "removed 1 exact duplicate key worth 20.0",
        },
        {"boundary": "validated", **boundary_profile(validated_events), "reason": "no change"},
        {"boundary": "saved", **boundary_profile(saved_events), "reason": "no change"},
    ]
)
print(reconciliation.to_string(index=False))
changes = reconciliation[["rows", "entities", "missing_amount", "amount_total"]].diff().iloc[1:]
assert changes.iloc[0].tolist() == [-1, 0, 0, -20.0]
changed = changes.ne(0).any(axis=1).tolist()
reasons = reconciliation["reason"].iloc[1:].tolist()
assert all((reason == "no change") != was_changed for reason, was_changed in zip(reasons, changed))
```

### Shared implementation for Exercises 8-10: Structured decisions and artifact acceptance

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

# Every decision entry is complete and tied to a reproducible count.
entry = asdict(decision)
assert set(entry) == {"evidence", "action", "rationale", "validation", "impact"}
assert all(entry.values())
invalid_amounts = int((~pd.to_numeric(raw["amount"], errors="coerce").ge(0)).sum())
assert entry["evidence"].startswith(f"{invalid_amounts} of {len(raw)}")

# Raw evidence stays unchanged, and restart-and-run-all exposes out-of-order state.
raw_before = raw.copy(deep=True)
assert clean_orders(raw) is not raw
pd.testing.assert_frame_equal(raw, raw_before)

ordered_cells = [
    "import pandas as pd\nMIN_AMOUNT = 0",
    "source = pd.DataFrame({'amount': ['10', 'bad', '-2']})",
    "kept = int(pd.to_numeric(source['amount'], errors='coerce').ge(MIN_AMOUNT).sum())",
]
fresh: dict[str, Any] = {}
for cell in ordered_cells:
    exec(cell, fresh)  # a new namespace imitates restart-and-run-all
assert fresh["kept"] == 1
out_of_order = ["import pandas as pd", *ordered_cells[1:], "MIN_AMOUNT = 0"]
try:
    restarted: dict[str, Any] = {}
    for cell in out_of_order:
        exec(cell, restarted)
except NameError as error:
    print("out-of-order notebook:", error)
else:
    raise AssertionError("a cell that uses a later-created name should fail after restart")

# Blocked artifacts: empty data, failed schema, and leakage.
for problem, frame, passed in [
    ("empty", cleaned.iloc[0:0], True),
    ("schema failed", cleaned, False),
]:
    try:
        artifact_manifest(frame, source="fixture", schema_passed=passed, version="1")
    except ValueError as error:
        print(f"{problem}: blocked ({error})")
    else:
        raise AssertionError(f"{problem} should block artifact creation")


def check_no_leakage(features: list[str], *, target: str, post_outcome: set[str]) -> None:
    leaked = sorted(({target} | post_outcome) & set(features))
    if leaked:
        raise ValueError(f"leakage-prone fields in features: {leaked}")


try:
    check_no_leakage(["amount", "refund_issued"], target="churned", post_outcome={"refund_issued"})
except ValueError as error:
    print("blocked:", error)
else:
    raise AssertionError("a post-outcome field must block the artifact")

timeline = pd.DataFrame({"event_time": pd.date_range("2025-01-01", periods=6, freq="D", tz="UTC")})
cutoff = pd.Timestamp("2025-01-05", tz="UTC")
train_part = timeline[timeline["event_time"] < cutoff]
test_part = timeline[timeline["event_time"] >= cutoff]
assert train_part["event_time"].max() < test_part["event_time"].min()  # no future rows in training

assert manifest == {
    "source": "constructed offline fixture",
    "rows": 1,
    "columns": ["order_id", "amount"],
    "schema_passed": True,
    "version": "1",
}
```

Split time-ordered or target-bearing data before learning any transform. Restart
and run all cells before acceptance, and keep raw data immutable so evidence can
always be reconstructed.
