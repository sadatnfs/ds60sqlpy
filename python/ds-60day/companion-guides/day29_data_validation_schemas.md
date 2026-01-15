# Day 29 — Data Validation with Schemas (Companion Guide)

## Learning objectives
- Define and enforce data schemas with Pandera or Pydantic
- Validate types, ranges, categories, and unique constraints
- Integrate validation in pipelines and CI

## Why this matters
Data contracts catch issues early and keep pipelines robust as data evolves.

## Core concepts and examples
### Pandera schemas
```python
import pandera as pa
import pandera.typing as pat

class Sales(pa.SchemaModel):
    order_id: pat.Series[int] = pa.Field(unique=True)
    store: pat.Series[str]
    amount: pat.Series[float] = pa.Field(ge=0)

validated = Sales.validate(df)
```

### Pydantic models (row-wise)
```python
from pydantic import BaseModel, Field
class Row(BaseModel):
    order_id: int
    amount: float = Field(ge=0)
rows = [Row(**rec) for rec in df.to_dict(orient='records')]
```

### Great Expectations (concept)
- Create expectations suites; run in CI; produce data docs

## Common pitfalls
- Validating after transformation instead of before ingestion
- Overly strict schemas that block real-world changes
- Silent coercions; prefer fail-fast unless justified

## Practice exercises
1) Write a Pandera schema for a dataset with categories and ranges
2) Add schema validation to the start of an ETL job
3) Configure CI to run validations on sample data

## Further reading
- Pandera: https://pandera.readthedocs.io
- Great Expectations: https://greatexpectations.io
