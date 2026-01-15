# Day 20 — Merging and Joins (Companion Guide)

## Learning objectives
- Combine tables with concat, merge, and join
- Choose appropriate join type (inner/left/right/outer) and keys
- Validate merges and diagnose mismatches

## Why this matters
Most datasets are not in one table. Correct joins prevent data loss and duplication.

## Core concepts and examples
### concat vs merge
```python
pd.concat([df1, df2], axis=0, ignore_index=True)   # stack rows
pd.concat([s1, s2], axis=1)                        # align on index, add columns
```

### merge basics
```python
orders = pd.read_csv('orders.csv')
customers = pd.read_csv('customers.csv')
merged = orders.merge(customers, how='left', on='customer_id', validate='m:1')
```

### multiple keys and suffixes
```python
m = a.merge(b, how='inner', on=['store_id','sku'], suffixes=('_a','_b'))
```

### diagnosing issues
```python
m = a.merge(b, how='outer', on='id', indicator=True)
m['_merge'].value_counts()
```

## Common pitfalls
- Joining on non-unique keys unintentionally; use `validate` to enforce cardinality
- Different dtypes for join keys; align with `astype`
- Duplicate column names; set suffixes or select needed columns before merge

## Practice exercises
1) Perform left vs inner join and compare row counts
2) Use `indicator=True` to find records unmatched in either table
3) Merge on multiple keys and verify cardinality

## Further reading
- Merge/join: https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
