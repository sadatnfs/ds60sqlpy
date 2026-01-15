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
import pandera as pa, pandera.typing as pat

dtypes = {'city':'string', 'price':'float64', 'qty':'Int64', 'date':'string'}
df = pd.read_csv('raw.csv', dtype=dtypes, parse_dates=['date'])

class Schema(pa.SchemaModel):
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
train.to_parquet('data/train.parquet', index=False)
metadata = {'columns': df.dtypes.astype(str).to_dict()}
```

Tips
- Keep code in functions for reuse
- Capture decisions and rationale in markdown cells
