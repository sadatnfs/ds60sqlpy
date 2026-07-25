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
