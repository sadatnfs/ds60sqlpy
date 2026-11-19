# Day 20 Solutions: Merging and Joining DataFrames

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

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Join product, order-item, and customer tables to compute revenue per customer. **Before code:** write each table's row grain and key uniqueness. **Sequence:** many order items to one product, calculate line revenue, aggregate to customer grain, then attach one customer record. **Expected behavior:** one output row per customer with orders. **Verify:** assert both merges pass their declared `validate` relationship, customer IDs are unique in the result, and summed customer revenue equals summed line revenue exactly.

**Reasoning:** Writing each table's grain first (one product per `sku`, one customer per `cid`, one row per order item) tells you which side of each merge must be unique, and the `is_unique` assertions check those claims against the data. The order of operations matters: line revenue is computed at item grain, where `qty` and `price` meet, then summed to customer grain, and only then joined to the customer table, so each customer appears once and nothing is multiplied. `validate="many_to_one"` and `validate="one_to_one"` make pandas raise `MergeError` if a key turns out to be duplicated, and the final reconciliation proves that no revenue was lost or counted twice. Customer 30 has no orders, so it correctly does not appear in an output defined as customers with orders.

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
customers = pd.DataFrame({"cid": [10, 20, 30], "name": ["Ada", "Lin", "No Orders"]})

# Grains: one product per sku, one customer per cid, and one order item
# per order_item_id.
assert products["sku"].is_unique
assert customers["cid"].is_unique
assert order_items["order_item_id"].is_unique

items = order_items.merge(products, on="sku", how="left", validate="many_to_one").assign(
    revenue=lambda frame: frame["qty"] * frame["price"]
)
revenue = (
    items.groupby("cid", as_index=False)
    .agg(revenue=("revenue", "sum"))
    .merge(customers, on="cid", how="left", validate="one_to_one")
    .loc[:, ["cid", "name", "revenue"]]
)
assert revenue["cid"].is_unique
assert revenue["revenue"].sum() == items["revenue"].sum()
```

### Exercise 2: worked answer

**Learner contract:** Demonstrate a right join that preserves every row of a chosen right-side customer table, including a customer with no matching order. **Expected behavior:** the unmatched right row survives with missing order fields. **Then:** swap table order and reproduce the result with a left join. **Verify:** compare sorted keys and explain why left joins are often easier to read from a chosen primary table.

**Reasoning:** A right join keeps every row of the right table, so customer 30, who has no orders, survives with missing order fields, and `indicator=True` labels that row `right_only`. Swapping the tables and using a left join keeps the same rows, which the sorted-key comparison proves; only the column order differs. Left joins are usually easier to read because the table whose rows you want to keep is written first, and the rest of the expression reads as attaching information to it.

```python
right_joined = order_items.merge(customers, on="cid", how="right", indicator=True)
equivalent_left = customers.merge(order_items, on="cid", how="left", indicator=True)
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

### Exercise 3: worked answer

**Learner contract:** Create data where a supposedly unique dimension key is duplicated, then use the correct `validate` relationship to raise `MergeError`. **Constraints:** state which side should be one and which may be many; do not de-duplicate merely to silence the error. **Verify:** repair the fixture or data contract and show the validated merge succeeds without row multiplication.

**Reasoning:** `validate="many_to_one"` states that each `sku` on the right side must be unique; the duplicated product A violates that claim, so pandas raises `MergeError` before returning a frame with doubled order lines. The repair is to fix the data or the contract, here by using the product table whose keys are unique, not to call `drop_duplicates` until the error disappears, which could silently discard a real price change. The final row-count check proves that the validated merge did not multiply rows.

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
repaired = order_items.merge(products, on="sku", how="left", validate="many_to_one")
assert len(repaired) == len(order_items)
```

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** One key appears twice on the left and three times on the right. Predict the number of joined rows for that key. **Progressive hint:** A many-to-many match forms every pair: left count × right count. **Verify:** Build the 2-by-3 fixture and assert exactly six rows for that key; compare with `validate` rejecting the unintended many-to-many relationship.

**Reasoning:** When a key appears twice on the left and three times on the right, the merge pairs every left row with every right row, so that key produces `2 * 3 = 6` rows. That is correct for a genuine many-to-many relationship, but it usually signals an unexpected duplicate. The shared implementation for Exercises 4-5 asserts the six rows and shows that `validate="one_to_many"` rejects the duplicated left key with `MergeError` instead of multiplying rows silently.

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace an outer merge with `indicator=True` and classify `left_only`, `right_only`, and `both` rows. **Progressive hint:** The indicator is a compact reconciliation tool. **Verify:** Assert one known key lands in each indicator category and reconcile category counts to the full outer-join row count.

**Reasoning:** An outer merge keeps keys from both sides, and `indicator=True` adds a `_merge` column with `left_only`, `right_only`, or `both`, so one column reconciles the two tables. In the shared implementation for Exercises 4-5, customer 1 has only an order, customer 3 has only a customer record, and customer 2 has both. The category counts add up to the outer-join row count because every row belongs to exactly one category.

### Exercise 6: answer contract

**Learner contract:** **Implementation:** Implement an anti-join returning left rows whose key has no right match. **Progressive hint:** Use a left merge with indicator, then filter `left_only`. **Verify:** Assert the anti-join returns exactly the unmatched left keys, preserves left columns/order, and does not duplicate rows when right keys repeat.

**Reasoning:** An anti-join keeps the left rows that have no match on the right: a left merge with `indicator=True`, filtered to `left_only`. Reducing the right side to its distinct keys first means a repeated right key cannot duplicate left rows, and selecting `left.columns` at the end drops the helper column and keeps the left column order. The shared implementation for Exercises 6-8 checks the result against the expected unmatched key, `"C"`, and against a right table with a repeated key.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** Repair a merge whose `validate='one_to_many'` is reversed relative to the actual product-to-order-item relationship. **Progressive hint:** Say which side must have unique keys before choosing `1:m` or `m:1`. **Verify:** Assert key uniqueness on each side, choose `many_to_one` for item-to-product data, and show the reversed validation fails on the duplicate item key.

**Reasoning:** Validation names follow the merge order: `one_to_many` claims that the left table's keys are unique. Order items repeat `sku` (two rows for A) while products do not, so with items on the left the correct claim is `many_to_one`, and the reversed claim fails with `MergeError`. Checking `is_unique` on each side before choosing the argument turns the relationship into evidence rather than a guess, as the shared implementation for Exercises 6-8 shows.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Investigate how missing keys match in pandas and decide whether to reject, sentinel-fill, or separate them before a business-key join. **Progressive hint:** Do not assume pandas null-key behavior matches SQL. **Verify:** Test two missing keys under pandas behavior, then assert the chosen reject/separate/sentinel policy prevents them from being mistaken for a business match.

**Reasoning:** Unlike SQL, where `NULL = NULL` is never true, pandas matches missing keys to each other, so two unrelated rows without a `sku` join and look like a real relationship. The reference rejects missing business keys before merging with a `ValueError`, because a record without a key cannot be matched reliably; moving those rows to a separate review table is a reasonable alternative. The shared implementation for Exercises 6-8 first shows the `None`-to-`None` match, then the rejection.

## Expanded mastery lab solutions

Declare each table's grain and key cardinality before merging. Use validation and reconciliation to make row loss or multiplication visible.

### Shared implementation for Exercises 4-5: Cardinality and reconciliation

Two matching left rows times three matching right rows produce six output rows.
An outer merge indicator shows orphans from each side as well as matches.

```python
import pandas as pd
from pandas.errors import MergeError

left = pd.DataFrame({"key": ["k", "k"], "left_value": [1, 2]})
right = pd.DataFrame({"key": ["k", "k", "k"], "right_value": ["x", "y", "z"]})
pairs = left.merge(right, on="key", how="inner")
assert len(pairs) == 2 * 3  # every left row pairs with every right row
try:
    left.merge(right, on="key", validate="one_to_many")
except MergeError as error:
    print("rejected:", error)
else:
    raise AssertionError("duplicate left keys must violate one_to_many")

orders = pd.DataFrame({"cid": [1, 2], "order_total": [10.0, 20.0]})
customer_names = pd.DataFrame({"cid": [2, 3], "name": ["Lin", "Mo"]})
outer = orders.merge(customer_names, on="cid", how="outer", indicator=True)
categories = dict(zip(outer["cid"], outer["_merge"].astype(str)))
assert categories == {1: "left_only", 2: "both", 3: "right_only"}
assert int(outer["_merge"].value_counts().sum()) == len(outer) == 3
```

### Shared implementation for Exercises 6-8: Anti-join and an explicit null-key policy

```python
import pandas as pd


def anti_join(left: pd.DataFrame, right: pd.DataFrame, *, key: str) -> pd.DataFrame:
    """Return left rows with no matching non-null key on the right."""

    if left[key].isna().any() or right[key].isna().any():
        raise ValueError(f"{key} must be non-null before this business-key join")
    right_keys = right[[key]].drop_duplicates()
    marked = left.merge(right_keys, on=key, how="left", validate="many_to_one", indicator=True)
    return marked.loc[marked["_merge"].eq("left_only"), left.columns].reset_index(drop=True)


products = pd.DataFrame({"sku": ["A", "B"], "price": [10.0, 5.0]})
items = pd.DataFrame({"sku": ["A", "A", "C"], "qty": [1, 2, 1]})

# Many item rows refer to one unique product row: many_to_one.
priced = items.merge(products, on="sku", how="left", validate="many_to_one", indicator=True)
assert priced["_merge"].tolist() == ["both", "both", "left_only"]
assert anti_join(items, products, key="sku")["sku"].tolist() == ["C"]

# Repeated right keys do not duplicate left rows; left columns stay in order.
repeated_right = pd.concat([products, products.iloc[[0]]], ignore_index=True)
assert anti_join(items, repeated_right, key="sku").equals(anti_join(items, products, key="sku"))
assert anti_join(items, products, key="sku").columns.tolist() == items.columns.tolist()

# Reversed validation: items repeat sku, so they cannot be the "one" side.
assert not items["sku"].is_unique and products["sku"].is_unique
try:
    items.merge(products, on="sku", how="left", validate="one_to_many")
except MergeError:
    pass
else:
    raise AssertionError("one_to_many must fail when the left keys repeat")

# pandas matches missing keys to each other, unlike SQL.
left_nulls = pd.DataFrame({"sku": [None, "A"], "qty": [1, 2]})
right_nulls = pd.DataFrame({"sku": [None, "A"], "price": [99.0, 10.0]})
assert len(left_nulls.merge(right_nulls, on="sku", how="inner")) == 2
try:
    anti_join(left_nulls, right_nulls, key="sku")
except ValueError as error:
    print("rejected:", error)
else:
    raise AssertionError("missing business keys must be rejected")
```

Unlike SQL equality joins, pandas can match missing keys to one another. This
solution rejects missing business keys before merging so the policy cannot be
mistaken for a real relationship.
