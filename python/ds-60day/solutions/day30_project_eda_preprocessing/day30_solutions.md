# Day 30 — Solutions: Project — EDA and Preprocessing

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**a restartable EDA and preprocessing project with an auditable evidence chain**.

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

### Reference pattern 1 — Reconcile a cleaning boundary

Make every row removal visible and explainable.

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

**Expected observation:** The reconciliation reports four raw rows, two clean rows, two removed rows, and totals before/after. Those changes still need documented rationale.

### Reference pattern 2 — Represent a decision as data

A structured entry is easier to audit than a scattered comment.

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

**Expected observation:** All six required fields are listed. The impact makes clear that de-duplication changes additive totals.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** **Load and scope:** choose a local, constructed, or already-cached dataset and record source/provenance, license if applicable, row grain, keys, shape, time range, analytical question, and measurable acceptance criteria. **Expected behavior:** a fresh-kernel run can recreate the same raw profile without hidden state or network access. **Verify:** assert expected columns and key/time bounds before continuing.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** assert expected columns and key/time bounds before continuing.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** **Explore:** analyze quality, distributions, missingness, duplicates, relationships, correlations, and relevant segments. **Constraints:** pair every table/plot with evidence, sample size/denominator, and a caveat; do not treat correlation as causation. **Verify:** every stated finding points to a reproducible calculation or plot and leakage-prone fields are excluded.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** every stated finding points to a reproducible calculation or plot and leakage-prone fields are excluded.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Clean and transform:** implement `clean(raw)` that returns a new DataFrame and records each decision's evidence, action, rationale, validation, and impact. **Constraints:** preserve raw data, avoid broad silent row dropping, and split before fitting learned transforms if a target exists. **Verify:** test idempotence where promised and reconcile row/entity counts plus key totals.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** test idempotence where promised and reconcile row/entity counts plus key totals.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Validate:** apply the Day 29 schema to the actual final cleaned DataFrame before output. **Expected behavior:** one valid fixture passes and a deliberately invalid fixture proves an important rule blocks progress. **Constraint:** do not catch and discard the validation failure. **Verify:** save is impossible until validation succeeds.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** save is impossible until validation succeeds.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Save and report:** write cleaned data and figures under an ignored `artifacts/day30/` path plus a manifest containing source, timestamp/version policy, row count, schema result, and file list. **Constraints:** handle an empty clean dataset as a blocked project, reopen outputs, and summarize findings, limitations, and lessons learned. **Verify:** saved/reloaded shape, schema, and key totals match the validated in-memory frame.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** saved/reloaded shape, schema, and key totals match the validated in-memory frame.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Before loading data, write the analytical question, row grain, entity keys, expected time range, and acceptance criteria. Predict one failure. **Progressive hint:** A declared expectation turns a surprise into a testable discrepancy. **Verify:** Save the written contract before loading, then assert the raw profile against keys/time/schema and record whether the predicted failure actually occurred.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** Save the written contract before loading, then assert the raw profile against keys/time/schema and record whether the predicted failure actually occurred.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace row count, unique entity count, missing target count, and an additive total across raw, cleaned, validated, and saved boundaries. **Progressive hint:** Every material change needs a reason and reconciliation. **Verify:** Build a four-boundary reconciliation table and assert every row/entity/missing/total change has an explicit reason; reopen saved data for the final row.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the a restartable EDA and preprocessing project with an auditable evidence chain model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** Build a four-boundary reconciliation table and assert every row/entity/missing/total change has an explicit reason; reopen saved data for the final row.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement a structured decision log entry containing evidence, action, rationale, validation, and impact. **Progressive hint:** Make decisions data, not scattered comments. **Verify:** Validate that each decision entry contains evidence, action, rationale, validation, and impact and links to a reproducible count/test.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** Validate that each decision entry contains evidence, action, rationale, validation, and impact and links to a reproducible count/test.

### Exercise 9 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a notebook that depends on out-of-order state and overwrites its raw frame during cleaning. **Progressive hint:** Put parameters/imports first and make `clean(raw)` return a copy. **Verify:** Restart and run top to bottom; assert `raw` remains unchanged, `clean(raw)` returns a copy, and no cell requires a later-created name.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** Restart and run top to bottom; assert `raw` remains unchanged, `clean(raw)` returns a copy, and no cell requires a later-created name.

### Exercise 10 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Prevent target/time leakage, handle an empty cleaned dataset, and write an artifact manifest with source, row count, schema result, and version. **Progressive hint:** Block artifact creation when acceptance criteria fail. **Verify:** Use leakage and empty-data fixtures to prove artifact creation is blocked; for a valid run, assert manifest source/count/schema/version match reopened files.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from a restartable EDA and preprocessing project with an auditable evidence chain.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A notebook is appropriate for a readable project report; extract stable cleaning/validation functions into modules once behavior is established and tested.

**Edge case:** Empty outputs, duplicate/conflicting keys, schema drift, stale artifacts, hidden state, target/time leakage, and path portability need gates.

**Solution evidence to inspect:** Use leakage and empty-data fixtures to prove artifact creation is blocked; for a valid run, assert manifest source/count/schema/version match reopened files.
<!-- END BEGINNER SOLUTION REVIEW -->

We combine EDA, cleaning, schema validation, and report generation into a reproducible workflow.

Deliverables
- Reproducible notebook with sections
- Cleaned dataset with schema
- Short findings write-up

---

Checklist with code skeletons

1) Define problem/questions
- What are we trying to predict/understand?
- What are the target and key features?

2) Load with dtypes + validate schema
```python
import pandas as pd
import pandera.pandas as pa
import pandera.typing as pat

dtypes = {'city':'string', 'price':'float64', 'qty':'Int64', 'date':'string'}
df = pd.read_csv('raw.csv', dtype=dtypes, parse_dates=['date'])

class Schema(pa.DataFrameModel):
    city: pat.Series[str]
    price: pat.Series[float] = pa.Field(ge=0)
    qty: pat.Series[int] = pa.Field(ge=0)
    date: pat.Series[pd.DatetimeTZDtype] | pat.Series[pd.Timestamp]

Schema.validate(df)
```

3) Profile nulls/dtypes/dupes/outliers
```python
summary = {
    'shape': df.shape,
    'nulls': df.isna().mean().to_dict(),
    'dtypes': df.dtypes.astype(str).to_dict(),
    'dupes': int(df.duplicated().sum()),
}
print(summary)
```

4) Clean and transform
```python
df['city'] = df['city'].str.strip().str.upper()
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(df['price'].median())
```

5) Visuals and segmentation
```python
import seaborn as sns, matplotlib.pyplot as plt
sns.histplot(df, x='price', hue='city'); plt.show()
```

6) Split train/test before target-aware transforms
```python
from sklearn.model_selection import train_test_split
train, test = train_test_split(df, test_size=0.2, random_state=42)
```

7) Save processed data and data dictionary
```python
from pathlib import Path

artifact_dir = Path('artifacts/day30/processed')
artifact_dir.mkdir(parents=True, exist_ok=True)
train.to_parquet(artifact_dir / 'train.parquet', index=False)
test.to_parquet(artifact_dir / 'test.parquet', index=False)
metadata = {'columns': df.dtypes.astype(str).to_dict()}
```

Tips
- Keep code in functions for reuse
- Capture decisions and rationale in markdown cells

---

## Expanded mastery lab solutions

Build a restartable evidence chain: question and provenance → raw checks → decisions → clean data → validation → artifacts → limitations.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Define and reconcile the analytical unit

Record the question and grain before inspection. At each boundary, compare row
count, unique IDs, missing critical values, and additive totals. A difference
is acceptable only when a decision record explains and validates it.

### Practices 3–5 — Structured decisions and artifact acceptance

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
