# Day 20 — Merging and Joins

**Level:** Intermediate

A join combines tables according to keys and cardinality. Predict which rows
should survive and how many rows can be produced before calling `merge`.

## Learning objectives

By the end of this lesson, you can:

- choose inner, left, right, or outer join semantics;
- distinguish row concatenation from key-based merging;
- state and enforce one-to-one, one-to-many, or many-to-many cardinality;
- diagnose orphan keys, duplicate keys, dtype mismatches, and suffixes;
- reconcile row counts and totals after a merge.

## Prerequisites

Complete Day 19 (`python-19`): table grain, grouping keys, and aggregation.





<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day20_pandas_merging_joins.md`, then open `python/ds-60day/notebooks/day20_pandas_merging_joins.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 20 — merging and joins to practice relational keys, join types, cardinality, and reconciliation
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **key:** one or more columns used to identify or match records.
- **cardinality:** the one/many relationship of matching keys on each side.
- **join:** an operation combining records according to key matches.
- **orphan:** a row whose key has no match on the other side.
- **anti-join:** rows from one side that have no match.
- **reconciliation:** checks proving expected rows and measures were preserved.

### Syntax anatomy

`left.merge(right, on="sku", how="left", validate="many_to_one",
indicator=True)` preserves all left rows, matches equal `sku` values,
asserts that the right key is unique, and adds `_merge` evidence. The
validation wording is from left to right.

### Worked example 1 — Enrich many line items from one product row

Make many-to-one cardinality executable. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

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

**Expected observation**

```text
`(3, {'both': 3, ...})`; category counts may include zero-valued labels. No item row was lost or multiplied.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Make an orphan visible

A left merge indicator supports reconciliation and anti-joins. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
more_items = pd.DataFrame({"sku": ["A", "C"], "qty": [1, 1]})
checked = more_items.merge(
    products, on="sku", how="left",
    validate="many_to_one", indicator=True
)
checked[["sku", "_merge"]].to_dict("records")
```

**Expected observation**

```text
`[{'sku': 'A', '_merge': 'both'}, {'sku': 'C', '_merge': 'left_only'}]`. Product `C` is an orphan.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Check key dtypes, missingness, and uniqueness on both tables before merging.
2. Use the cardinality language from left to right when choosing `validate`.
3. Add `indicator=True` and inspect every category before dropping `_merge`.
4. Reconcile row counts and additive totals; a successful call is not proof of a correct relationship.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** An index join can be concise when indexes are deliberate keys; explicit column merges are often easier for beginners to audit.

**Boundary to remember:** Null keys, whitespace/case differences, composite keys, duplicate dimensions, and many-to-many multiplication need policy.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Join key:** column(s) used to match rows.
- **Cardinality:** number of rows per key on each side (`1:1`, `1:m`, `m:1`,
  or `m:m`).
- **Inner join:** matched keys only; **left join:** every left row; **right
  join:** every right row; **outer join:** every key from either side.
- **Orphan:** row whose key has no match in the other table.
- **Row explosion:** unintended multiplication caused by duplicate keys.

## Worked example

```python
import pandas as pd

products = pd.DataFrame({"sku": ["A", "B"], "price": [4.0, 7.5]})
items = pd.DataFrame({"order_id": [1, 1, 2], "sku": ["A", "B", "A"]})

priced = items.merge(
    products,
    on="sku",
    how="left",
    validate="many_to_one",
    indicator=True,
)
assert priced["_merge"].eq("both").all()
```

The contract says many item rows may refer to one product row. `indicator=True`
makes missing matches visible during validation.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Join product, order-item, and customer tables to compute revenue per customer. **Before code:** write each table's row grain and key uniqueness. **Sequence:** many order items to one product, calculate line revenue, aggregate to customer grain, then attach one customer record.
   **Expected behavior:** one output row per customer with orders.
   **Verify:** use `validate` on both merges and reconcile total line revenue to customer revenue.

2. Demonstrate a right join that preserves every row of a chosen right-side customer table, including a customer with no matching order.
   **Expected behavior:** the unmatched right row survives with missing order fields. **Then:** swap table order and reproduce the result with a left join.
   **Verify:** compare sorted keys and explain why left joins are often easier to read from a chosen primary table.

3. Create data where a supposedly unique dimension key is duplicated, then use the correct `validate` relationship to raise `MergeError`. **Constraints:** state which side should be one and which may be many; do not de-duplicate merely to silence the error.
   **Verify:** repair the fixture or data contract and show the validated merge succeeds without row multiplication.

### Additional mastery practice

Declare each table's grain and key cardinality before merging. Use validation and reconciliation to make row loss or multiplication visible.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** One key appears twice on the left and three times on the right. Predict the number of joined rows for that key.
   **Progressive hint:** A many-to-many match forms every pair: left count × right count.
   **Verify:** Build the 2-by-3 fixture and assert exactly six rows for that key; compare with `validate` rejecting the unintended many-to-many relationship.
5. **Tracing:** Trace an outer merge with `indicator=True` and classify `left_only`, `right_only`, and `both` rows.
   **Progressive hint:** The indicator is a compact reconciliation tool.
   **Verify:** Assert one known key lands in each indicator category and reconcile category counts to the full outer-join row count.
6. **Implementation:** Implement an anti-join returning left rows whose key has no right match.
   **Progressive hint:** Use a left merge with indicator, then filter `left_only`.
   **Verify:** Assert the anti-join returns exactly the unmatched left keys, preserves left columns/order, and does not duplicate rows when right keys repeat.
7. **Debugging:** Repair a merge whose `validate='one_to_many'` is reversed relative to the actual product-to-order-item relationship.
   **Progressive hint:** Say which side must have unique keys before choosing `1:m` or `m:1`.
   **Verify:** Assert key uniqueness on each side, choose `many_to_one` for item-to-product data, and show the reversed validation fails on the duplicate item key.
8. **Edge case and explanation:** Investigate how missing keys match in pandas and decide whether to reject, sentinel-fill, or separate them before a business-key join.
   **Progressive hint:** Do not assume pandas null-key behavior matches SQL.
   **Verify:** Test two missing keys under pandas behavior, then assert the chosen reject/separate/sentinel policy prevents them from being mistaken for a business match.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- How many output rows can an `m:m` match create for one key?
- Why might a left join produce more rows than the left input?
- What does an outer join reveal about data quality?
- Why should join-key dtypes be normalized before merging?

Expected behavior: revenue reconciles with line items, orphan rows are
identified rather than silently lost, and incorrect cardinality raises
`MergeError`.

## Common pitfalls and diagnosis

- **Row count unexpectedly multiplies:** measure duplicate counts on both key
  sets and add `validate`.
- **Matches are missing:** compare key dtypes, whitespace, case, and nulls.
- **`_x`/`_y` columns are confusing:** select needed columns or supply meaningful
  suffixes before downstream work.
- **Totals change after a join:** reconcile at the pre-join grain and inspect
  duplicated matches.
- **`concat` was used for a relational join:** use `merge`; `concat` stacks or
  aligns along an axis rather than matching business keys.

## Continue

- [Open the learner notebook](../notebooks/day20_pandas_merging_joins.ipynb)
- [Check the separate solution](../solutions/day20_pandas_merging_joins/day20_solutions.md)
- [Next: Day 21 — Time series with pandas](day21_time_series_pandas.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-20`
(Day 20 — Merging and Joins). I am a complete beginner. Emphasize relational keys, join types, cardinality, and reconciliation.
Read `python/ds-60day/companion-guides/day20_pandas_merging_joins.md` and use the learner notebook
`python/ds-60day/notebooks/day20_pandas_merging_joins.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
