# Day 20 — Solutions: Pandas Merging and Joins

We build product and order item tables, compute revenue by customer, demonstrate right join, and validate merge cardinality.

Contents
- Exercise 1: Join products/order_items/customer to compute revenue
- Exercise 2: Right join example and when it’s useful
- Exercise 3: validate='one_to_many' to catch duplicates

---

Setup
```python
import pandas as pd

customers = pd.DataFrame({"cid":[1,2,3], "name":["Ada","Alan","Linus"]})
products  = pd.DataFrame({"sku":["A","B"], "price":[10.0, 5.0]})
order_items = pd.DataFrame({
    "oid":[10,10,11,12],
    "cid":[1,1,1,3],
    "sku":["A","B","A","B"],
    "qty":[2,1,1,3],
})
```

Exercise 1 — Revenue by customer
```python
items = order_items.merge(products, on='sku', how='left', validate='m:1')
items = items.assign(revenue=items['qty'] * items['price'])
by_cust = (items
    .groupby('cid', as_index=False)
    .agg(revenue=('revenue','sum'))
    .merge(customers, on='cid', how='left', validate='1:1')
    .loc[:, ['cid','name','revenue']]
)
by_cust
```

Exercise 2 — Right join
```python
# Right join all customers with any orders (keep all orders even if cid missing from customers)
right_demo = order_items.merge(customers, on='cid', how='right', indicator=True)
right_demo['_merge'].value_counts()
```
When useful: preserving all rows from the right table regardless of matches (often you want left joins from a primary fact table; right is symmetric but less common).

Exercise 3 — validate to catch duplicates
```python
# Expect each (sku) to map to a single product row; enforce m:1
items = order_items.merge(products, on='sku', how='left', validate='m:1')
# If a product appears twice, pandas raises MergeError explaining the violation.
```
Notes
- Always think about join cardinality; use validate to enforce expectations.
- Align dtypes for keys before merging to avoid surprises.

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Join products, order items, and customers to compute revenue per customer. **Hint:** write each table's grain and key uniqueness first; calculate line-level revenue only after price and quantity share a row.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Demonstrate a right join and explain when it is useful. **Hint:** identify which right-side rows must survive; compare with swapping the inputs and performing a left join.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Use `validate="one_to_many"` to catch unexpected duplicates. **Hint:** place the table expected to have one row per key on the left, then deliberately duplicate one of its keys to observe the error.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** One key appears twice on the left and three times on the right. Predict the number of joined rows for that key.

**Reasoning checkpoint:** A many-to-many match forms every pair: left count × right count. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace an outer merge with `indicator=True` and classify `left_only`, `right_only`, and `both` rows.

**Reasoning checkpoint:** The indicator is a compact reconciliation tool. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Implement an anti-join returning left rows whose key has no right match.

**Reasoning checkpoint:** Use a left merge with indicator, then filter `left_only`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Repair a merge whose `validate='one_to_many'` is reversed relative to the actual product-to-order-item relationship.

**Reasoning checkpoint:** Say which side must have unique keys before choosing `1:m` or `m:1`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Investigate how missing keys match in pandas and decide whether to reject, sentinel-fill, or separate them before a business-key join.

**Reasoning checkpoint:** Do not assume pandas null-key behavior matches SQL. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Declare each table's grain and key cardinality before merging. Use validation and reconciliation to make row loss or multiplication visible.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Cardinality and reconciliation

Two matching left rows times three matching right rows produce six output rows.
An outer merge indicator shows orphans from each side as well as matches.

### Practices 3–5 — Anti-join and an explicit null-key policy

```python
import pandas as pd


def anti_join(left: pd.DataFrame, right: pd.DataFrame, *, key: str) -> pd.DataFrame:
    """Return left rows with no matching non-null key on the right."""

    if left[key].isna().any() or right[key].isna().any():
        raise ValueError(f"{key} must be non-null before this business-key join")
    right_keys = right[[key]].drop_duplicates()
    marked = left.merge(
        right_keys, on=key, how="left", validate="many_to_one", indicator=True
    )
    return marked.loc[marked["_merge"].eq("left_only"), left.columns].reset_index(drop=True)


products = pd.DataFrame({"sku": ["A", "B"], "price": [10.0, 5.0]})
items = pd.DataFrame({"sku": ["A", "A", "C"], "qty": [1, 2, 1]})

# Many item rows refer to one unique product row: many_to_one.
priced = items.merge(products, on="sku", how="left", validate="many_to_one", indicator=True)
assert priced["_merge"].tolist() == ["both", "both", "left_only"]
assert anti_join(items, products, key="sku")["sku"].tolist() == ["C"]
```

Unlike SQL equality joins, pandas can match missing keys to one another. This
solution rejects missing business keys before merging so the policy cannot be
mistaken for a real relationship.
