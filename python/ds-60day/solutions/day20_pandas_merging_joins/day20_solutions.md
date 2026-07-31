# Day 20 — Solutions: Pandas Merging and Joins

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **relational keys, join types, cardinality, and reconciliation**. Predict each named
result before comparing your attempt with its matching assertions.

A merge combines rows whose key values match. Before code, state each
table's grain, which columns form the key, and whether that key is unique
on each side. Those facts determine expected cardinality: one-to-one,
one-to-many, many-to-one, or many-to-many.

Join type controls preservation: inner keeps matches, left preserves
left rows, right preserves right rows, and outer preserves both sides.
A join can silently drop unmatched rows or multiply repeated matches.
Use `validate` to enforce cardinality, `indicator=True` to classify
matches/orphans, and row-count/total reconciliation to prove the result
has the intended meaning.

### Vocabulary used in the worked answers

- **key:** one or more columns used to identify or match records.
- **cardinality:** the one/many relationship of matching keys on each side.
- **join:** an operation combining records according to key matches.
- **orphan:** a row whose key has no match on the other side.
- **anti-join:** rows from one side that have no match.
- **reconciliation:** checks proving expected rows and measures were preserved.

### How to compare an answer

For this lesson's **relational keys, join types, cardinality, and reconciliation** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Join product, order-item, and customer tables to compute revenue per customer. **Before code:** write each table's row grain and key uniqueness. **Sequence:** many order items to one product, calculate line revenue, aggregate to customer grain, then attach one customer record. **Expected behavior:** one output row per customer with orders. **Verify:** assert both merges pass their declared `validate` relationship, customer IDs are unique in the result, and summed customer revenue equals summed line revenue exactly.

**Reasoning:** Implement this exact contract as written: Join product, order-item, and customer tables to compute revenue per customer. Before code: write each table's row grain and key uniqueness. Sequence: many order items to one product, calculate line revenue, aggregate to customer grain, then attach one customer record. Expected behavior: one output row per customer with orders. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert both merges pass their declared `validate` relationship, customer IDs are unique in the result, and summed customer revenue equals summed line revenue exactly. That connects the answer to relational keys, join types, cardinality, and reconciliation.

```python
import pandas as pd

products = pd.DataFrame({"sku": ["A", "B"], "price": [5.0, 8.0]})
order_items = pd.DataFrame(
    {
        "order_item_id": [1, 2, 3],
        "cid": [10, 10, 20],
        "sku": ["A", "B", "A"],
        "qty": [2, 1, 3],
    }
)
customers = pd.DataFrame(
    {"cid": [10, 20, 30], "name": ["Ada", "Lin", "No Orders"]}
)

# Grains: one product per sku, one customer per cid, and one order item
# per order_item_id.
assert products["sku"].is_unique
assert customers["cid"].is_unique
assert order_items["order_item_id"].is_unique

items = order_items.merge(
    products, on="sku", how="left", validate="many_to_one"
).assign(revenue=lambda frame: frame["qty"] * frame["price"])
revenue = (
    items.groupby("cid", as_index=False)
    .agg(revenue=("revenue", "sum"))
    .merge(customers, on="cid", how="left", validate="one_to_one")
    .loc[:, ["cid", "name", "revenue"]]
)
assert revenue["cid"].is_unique
assert revenue["revenue"].sum() == items["revenue"].sum()
```

**Verification evidence:** assert both merges pass their declared `validate` relationship, customer IDs are unique in the result, and summed customer revenue equals summed line revenue exactly.

### Exercise 2 — worked answer

**Learner contract:** Demonstrate a right join that preserves every row of a chosen right-side customer table, including a customer with no matching order. **Expected behavior:** the unmatched right row survives with missing order fields. **Then:** swap table order and reproduce the result with a left join. **Verify:** compare sorted keys and explain why left joins are often easier to read from a chosen primary table.

**Reasoning:** Implement this exact contract as written: Demonstrate a right join that preserves every row of a chosen right-side customer table, including a customer with no matching order. Expected behavior: the unmatched right row survives with missing order fields. Then: swap table order and reproduce the result with a left join. Keep the prompt's named data and constraints visible in the code, then establish this specific result: compare sorted keys and explain why left joins are often easier to read from a chosen primary table. That connects the answer to relational keys, join types, cardinality, and reconciliation.

```python
right_joined = order_items.merge(
    customers, on="cid", how="right", indicator=True
)
equivalent_left = customers.merge(
    order_items, on="cid", how="left", indicator=True
)
right_keys = right_joined["cid"].sort_values().reset_index(drop=True)
left_keys = equivalent_left["cid"].sort_values().reset_index(drop=True)
pd.testing.assert_series_equal(right_keys, left_keys)
assert (right_joined["_merge"] == "right_only").any()
unmatched = right_joined.loc[right_joined["_merge"].eq("right_only")]
assert unmatched["cid"].tolist() == [30]
assert unmatched["order_item_id"].isna().all()
```

The swapped left join is often easier to read because the preserved
customer table appears first.

**Verification evidence:** compare sorted keys and explain why left joins are often easier to read from a chosen primary table.

### Exercise 3 — worked answer

**Learner contract:** Create data where a supposedly unique dimension key is duplicated, then use the correct `validate` relationship to raise `MergeError`. **Constraints:** state which side should be one and which may be many; do not de-duplicate merely to silence the error. **Verify:** repair the fixture or data contract and show the validated merge succeeds without row multiplication.

**Reasoning:** Reproduce the exact failure described here before changing code: Create data where a supposedly unique dimension key is duplicated, then use the correct `validate` relationship to raise `MergeError`. Constraints: state which side should be one and which may be many; do not de-duplicate merely to silence the error. Preserve that failing case, repair the violated rule, and rerun the evidence named here: repair the fixture or data contract and show the validated merge succeeds without row multiplication. The diagnosis depends on relational keys, join types, cardinality, and reconciliation.

```python
import pandas as pd
from pandas.errors import MergeError

duplicated_products = pd.concat([products, products.iloc[[0]]], ignore_index=True)
try:
    order_items.merge(
        duplicated_products,
        on="sku",
        how="left",
        validate="many_to_one",
    )
except MergeError:
    pass
else:
    raise AssertionError("duplicated product keys must violate many_to_one")

assert products["sku"].is_unique
repaired = order_items.merge(
    products, on="sku", how="left", validate="many_to_one"
)
assert len(repaired) == len(order_items)
```

**Verification evidence:** repair the fixture or data contract and show the validated merge succeeds without row multiplication.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** One key appears twice on the left and three times on the right. Predict the number of joined rows for that key. **Progressive hint:** A many-to-many match forms every pair: left count × right count. **Verify:** Build the 2-by-3 fixture and assert exactly six rows for that key; compare with `validate` rejecting the unintended many-to-many relationship.

**Reasoning:** Predict this named state change before running it: Prediction: One key appears twice on the left and three times on the right. Predict the number of joined rows for that key. Progressive hint: A many-to-many match forms every pair: left count × right count. Then compare the prediction with this proof target: Build the 2-by-3 fixture and assert exactly six rows for that key; compare with `validate` rejecting the unintended many-to-many relationship. This makes relational keys, join types, cardinality, and reconciliation observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Build the 2-by-3 fixture and assert exactly six rows for that key; compare with `validate` rejecting the unintended many-to-many relationship.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace an outer merge with `indicator=True` and classify `left_only`, `right_only`, and `both` rows. **Progressive hint:** The indicator is a compact reconciliation tool. **Verify:** Assert one known key lands in each indicator category and reconcile category counts to the full outer-join row count.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace an outer merge with `indicator=True` and classify `left_only`, `right_only`, and `both` rows. Progressive hint: The indicator is a compact reconciliation tool. Record the named value, shape, label, or iterator position needed to establish: Assert one known key lands in each indicator category and reconcile category counts to the full outer-join row count. The trace exposes relational keys, join types, cardinality, and reconciliation directly.

**Evidence to locate in the grouped implementation:** Assert one known key lands in each indicator category and reconcile category counts to the full outer-join row count.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Implement an anti-join returning left rows whose key has no right match. **Progressive hint:** Use a left merge with indicator, then filter `left_only`. **Verify:** Assert the anti-join returns exactly the unmatched left keys, preserves left columns/order, and does not duplicate rows when right keys repeat.

**Reasoning:** Implement this exact contract as written: Implementation: Implement an anti-join returning left rows whose key has no right match. Progressive hint: Use a left merge with indicator, then filter `left_only`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert the anti-join returns exactly the unmatched left keys, preserves left columns/order, and does not duplicate rows when right keys repeat. That connects the answer to relational keys, join types, cardinality, and reconciliation.

**Evidence to locate in the grouped implementation:** Assert the anti-join returns exactly the unmatched left keys, preserves left columns/order, and does not duplicate rows when right keys repeat.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Repair a merge whose `validate='one_to_many'` is reversed relative to the actual product-to-order-item relationship. **Progressive hint:** Say which side must have unique keys before choosing `1:m` or `m:1`. **Verify:** Assert key uniqueness on each side, choose `many_to_one` for item-to-product data, and show the reversed validation fails on the duplicate item key.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a merge whose `validate='one_to_many'` is reversed relative to the actual product-to-order-item relationship. Progressive hint: Say which side must have unique keys before choosing `1:m` or `m:1`. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Assert key uniqueness on each side, choose `many_to_one` for item-to-product data, and show the reversed validation fails on the duplicate item key. The diagnosis depends on relational keys, join types, cardinality, and reconciliation.

**Evidence to locate in the grouped implementation:** Assert key uniqueness on each side, choose `many_to_one` for item-to-product data, and show the reversed validation fails on the duplicate item key.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Investigate how missing keys match in pandas and decide whether to reject, sentinel-fill, or separate them before a business-key join. **Progressive hint:** Do not assume pandas null-key behavior matches SQL. **Verify:** Test two missing keys under pandas behavior, then assert the chosen reject/separate/sentinel policy prevents them from being mistaken for a business match.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Investigate how missing keys match in pandas and decide whether to reject, sentinel-fill, or separate them before a business-key join. Progressive hint: Do not assume pandas null-key behavior matches SQL. Values below, at, and above the named boundary must produce the evidence Test two missing keys under pandas behavior, then assert the chosen reject/separate/sentinel policy prevents them from being mistaken for a business match. Those cases show how relational keys, join types, cardinality, and reconciliation behaves at its edge.

**Evidence to locate in the grouped implementation:** Test two missing keys under pandas behavior, then assert the chosen reject/separate/sentinel policy prevents them from being mistaken for a business match.

## Expanded mastery lab solutions

Declare each table's grain and key cardinality before merging. Use validation and reconciliation to make row loss or multiplication visible.

### Shared implementation for Exercises 4–5 — Cardinality and reconciliation

Two matching left rows times three matching right rows produce six output rows.
An outer merge indicator shows orphans from each side as well as matches.

### Shared implementation for Exercises 6–8 — Anti-join and an explicit null-key policy

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
