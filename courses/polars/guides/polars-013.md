# polars-013: Nested data, lists and structs

## Level and prerequisites

Advanced. Direct prerequisites: `polars-002`, `polars-004`

**Outcome:** Normalize nested events with an explicit population and identity contract.

## Question and mechanism

Nested data is common in event payloads, transaction items and model outputs. A list holds a variable-length sequence inside one row; a struct combines named fields into one value with a defined internal schema. These representations can preserve relationships that would be awkward to encode as unrelated flat columns. Flattening them is a deliberate change in grain, not merely a display operation.

Exploding an item list turns one order record into multiple item records. Empty lists and absent lists require different interpretations: one can mean that no items were recorded, while the other can mean that the item information is unavailable. The first case makes an explicit eligible-order policy before exploding. This avoids relying on a library default to decide the analytical meaning of empty or missing collections.

Native nested expressions retain the columnar model. list.eval applies an expression to elements of each list; struct.field extracts a named component. These operations make the intended shape visible to the engine. Python object loops may still be useful for unusual logic, but should not replace simple native transformations without a reason and a measured cost.

## Syntax and data contract

list.len returns list lengths while preserving null for an absent list. Filtering positive lengths before explode makes the item-grain population explicit. pl.struct packs named columns, and struct.field selects by name rather than position. Inside list.eval, pl.element refers to one list element, not an outer DataFrame column.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Declare the population before exploding

Three orders contain two items, an empty list and an unknown list. The program keeps only the positive-length list before flattening, and reports the omitted order identities. This is one declared policy, not a universal definition of an order count.

**Expected evidence:** The item table contains two rows for order 1; orders 2 and 3 remain outside that item population.

```python
import polars as pl


def example_one():
    frame = pl.DataFrame({"order": [1, 2, 3], "items": [["a", "b"], [], None]})
    normalized = frame.with_columns(pl.col("items").list.len().alias("count"))
    assert normalized["count"].to_list() == [2, 0, None]
    eligible = normalized.filter(pl.col("count") > 0).explode("items")
    assert eligible.to_dicts() == [
        {"order": 1, "items": "a", "count": 2},
        {"order": 1, "items": "b", "count": 2},
    ]
    return {"order_rows": 3, "item_rows": 2, "excluded_empty_or_unknown_orders": [2, 3]}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Preserve named structure and transform elements

The second case packs x and y into a point struct, reconstructs the columns and then doubles nested list values. It checks both identity preservation and the shape of the nested result.

**Expected evidence:** The struct round trip equals its source; doubled lists are [[2,4],[6]].

```python
import polars as pl


def example_two():
    frame = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
    packed = frame.select(pl.struct("x", "y").alias("point"))
    extracted = packed.select(pl.col("point").struct.field("x"), pl.col("point").struct.field("y"))
    assert extracted.equals(frame)
    evaluated = pl.DataFrame({"values": [[1, 2], [3]]}).select(
        pl.col("values").list.eval(pl.element() * 2).alias("doubled")
    )
    assert evaluated["doubled"].to_list() == [[2, 4], [6]]
    return {"struct_round_trip": True, "nested_values": evaluated.to_dicts()}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Separate empty from unknown

Create separate counts for an empty list and a null list.

**Check:** There is one of each.

**Hint:** A list length of 0 is not a null length.


### 2. Change the grain

Write the key for the exploded item table.

**Check:** An order_id alone is no longer sufficient.

**Hint:** One order may contain repeated item labels.


### 3. Keep order-level metrics

Compute the original number of orders before exploding.

**Check:** The count remains 3.

**Hint:** Do not infer orders from item rows.


### 4. Add a struct field

Add a third named coordinate and round-trip all fields.

**Check:** All values and field names are preserved.

**Hint:** Select fields by name.


### 5. Transform a nested value

Square each numeric element without a Python row loop.

**Check:** The lists become [[1,4],[9]].

**Hint:** Use list.eval with element expressions.


### 6. Test null nested elements

Add a list containing a null element and define the policy.

**Check:** The null remains visible unless explicitly handled.

**Hint:** A missing element differs from a missing list.


## Diagnose errors and misleading results

Unexpected row counts after explode usually indicate an unstated grain or empty-list policy. Missing struct fields indicate schema evolution or a spelling problem, not an invitation to select by position. Check nested dtypes before applying numeric expressions and retain collection-level identifiers for reconciliation.

## Transfer to independent work

Normalize nested events with an explicit population and identity contract. Demonstrate empty, missing and repeated-element cases, then verify that any flattened table can still be related to its original records. This is essential for reliable event analytics and sequence-feature construction.

## Primary references

- [Polars documentation: Nested data, lists and structs](https://docs.pola.rs/user-guide/expressions/lists-and-arrays/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-013`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
