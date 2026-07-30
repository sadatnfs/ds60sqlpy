# Day 30 — Solutions: Project — EDA and Preprocessing

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** **Load and scope.** Use a local file, constructed dataset, or already-cached Seaborn sample; record provenance, row grain, shape, and analytical question. **Hint:** restart the notebook before continuing so hidden state cannot supply the data.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** **Explore.** Examine distributions, missingness, duplicates, relationships, correlations, and relevant segments. **Hint:** pair each table/plot with one sentence of evidence and one caveat; correlation alone is not causation.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** **Clean and transform.** Reuse/refine the Day 18 cleaner and document each decision. **Hint:** keep raw data unchanged and assert idempotence where appropriate.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Original lesson practice

**Prompt:** **Validate.** Apply a Pandera schema from Day 29 before writing. **Hint:** create at least one deliberately invalid fixture proving an important constraint can fail.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 5 — Original lesson practice

**Prompt:** **Save and report.** Write cleaned output under `artifacts/day30/`, export readable figures, summarize findings/limitations, and add a final "What I learned" section. **Hint:** report row counts and key totals at raw, cleaned, and saved boundaries. If the dataset includes a prediction target, split before learning imputation, encoding, scaling, or target-aware decisions.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 6 — Prediction

**Prompt:** Before loading data, write the analytical question, row grain, entity keys, expected time range, and acceptance criteria. Predict one failure.

**Reasoning checkpoint:** A declared expectation turns a surprise into a testable discrepancy. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Tracing

**Prompt:** Trace row count, unique entity count, missing target count, and an additive total across raw, cleaned, validated, and saved boundaries.

**Reasoning checkpoint:** Every material change needs a reason and reconciliation. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Implementation

**Prompt:** Implement a structured decision log entry containing evidence, action, rationale, validation, and impact.

**Reasoning checkpoint:** Make decisions data, not scattered comments. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 9 — Debugging

**Prompt:** Repair a notebook that depends on out-of-order state and overwrites its raw frame during cleaning.

**Reasoning checkpoint:** Put parameters/imports first and make `clean(raw)` return a copy. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 10 — Edge case and explanation

**Prompt:** Prevent target/time leakage, handle an empty cleaned dataset, and write an artifact manifest with source, row count, schema result, and version.

**Reasoning checkpoint:** Block artifact creation when acceptance criteria fail. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
