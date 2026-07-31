# Day 20 — Solutions: Pandas Merging and Joins

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**relational keys, join types, cardinality, and reconciliation**.

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

### Reference pattern 1 — Enrich many line items from one product row

Make many-to-one cardinality executable.

```python
import pandas as pd

items = pd.DataFrame({"sku": ["A", "A", "B"], "qty": [1, 2, 1]})
products = pd.DataFrame({"sku": ["A", "B"], "price": [10.0, 5.0]})
priced = items.merge(
    products, on="sku", how="left",
    validate="many_to_one", indicator=True
)
(len(priced), priced["_merge"].value_counts().to_dict())
```

**Expected observation:** `(3, {'both': 3, ...})`; category counts may include zero-valued labels. No item row was lost or multiplied.

### Reference pattern 2 — Make an orphan visible

A left merge indicator supports reconciliation and anti-joins.

```python
more_items = pd.DataFrame({"sku": ["A", "C"], "qty": [1, 1]})
checked = more_items.merge(
    products, on="sku", how="left",
    validate="many_to_one", indicator=True
)
checked[["sku", "_merge"]].to_dict("records")
```

**Expected observation:** `[{'sku': 'A', '_merge': 'both'}, {'sku': 'C', '_merge': 'left_only'}]`. Product `C` is an orphan.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Join product, order-item, and customer tables to compute revenue per customer. **Before code:** write each table's row grain and key uniqueness. **Sequence:** many order items to one product, calculate line revenue, aggregate to customer grain, then attach one customer record. **Expected behavior:** one output row per customer with orders. **Verify:** use `validate` on both merges and reconcile total line revenue to customer revenue.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies relational keys, join types, cardinality, and reconciliation.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Edge case:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.

**Solution evidence to inspect:** use `validate` on both merges and reconcile total line revenue to customer revenue.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Demonstrate a right join that preserves every row of a chosen right-side customer table, including a customer with no matching order. **Expected behavior:** the unmatched right row survives with missing order fields. **Then:** swap table order and reproduce the result with a left join. **Verify:** compare sorted keys and explain why left joins are often easier to read from a chosen primary table.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies relational keys, join types, cardinality, and reconciliation.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Edge case:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.

**Solution evidence to inspect:** compare sorted keys and explain why left joins are often easier to read from a chosen primary table.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Create data where a supposedly unique dimension key is duplicated, then use the correct `validate` relationship to raise `MergeError`. **Constraints:** state which side should be one and which may be many; do not de-duplicate merely to silence the error. **Verify:** repair the fixture or data contract and show the validated merge succeeds without row multiplication.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in relational keys, join types, cardinality, and reconciliation.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Edge case:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.

**Solution evidence to inspect:** repair the fixture or data contract and show the validated merge succeeds without row multiplication.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** One key appears twice on the left and three times on the right. Predict the number of joined rows for that key. **Progressive hint:** A many-to-many match forms every pair: left count × right count. **Verify:** Build the 2-by-3 fixture and assert exactly six rows for that key; compare with `validate` rejecting the unintended many-to-many relationship.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying relational keys, join types, cardinality, and reconciliation.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Edge case:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.

**Solution evidence to inspect:** Build the 2-by-3 fixture and assert exactly six rows for that key; compare with `validate` rejecting the unintended many-to-many relationship.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace an outer merge with `indicator=True` and classify `left_only`, `right_only`, and `both` rows. **Progressive hint:** The indicator is a compact reconciliation tool. **Verify:** Assert one known key lands in each indicator category and reconcile category counts to the full outer-join row count.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the relational keys, join types, cardinality, and reconciliation model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Edge case:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.

**Solution evidence to inspect:** Assert one known key lands in each indicator category and reconcile category counts to the full outer-join row count.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement an anti-join returning left rows whose key has no right match. **Progressive hint:** Use a left merge with indicator, then filter `left_only`. **Verify:** Assert the anti-join returns exactly the unmatched left keys, preserves left columns/order, and does not duplicate rows when right keys repeat.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies relational keys, join types, cardinality, and reconciliation.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Edge case:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.

**Solution evidence to inspect:** Assert the anti-join returns exactly the unmatched left keys, preserves left columns/order, and does not duplicate rows when right keys repeat.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a merge whose `validate='one_to_many'` is reversed relative to the actual product-to-order-item relationship. **Progressive hint:** Say which side must have unique keys before choosing `1:m` or `m:1`. **Verify:** Assert key uniqueness on each side, choose `many_to_one` for item-to-product data, and show the reversed validation fails on the duplicate item key.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in relational keys, join types, cardinality, and reconciliation.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Edge case:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.

**Solution evidence to inspect:** Assert key uniqueness on each side, choose `many_to_one` for item-to-product data, and show the reversed validation fails on the duplicate item key.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Investigate how missing keys match in pandas and decide whether to reject, sentinel-fill, or separate them before a business-key join. **Progressive hint:** Do not assume pandas null-key behavior matches SQL. **Verify:** Test two missing keys under pandas behavior, then assert the chosen reject/separate/sentinel policy prevents them from being mistaken for a business match.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from relational keys, join types, cardinality, and reconciliation.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Edge case:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.

**Solution evidence to inspect:** Test two missing keys under pandas behavior, then assert the chosen reject/separate/sentinel policy prevents them from being mistaken for a business match.
<!-- END BEGINNER SOLUTION REVIEW -->

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
