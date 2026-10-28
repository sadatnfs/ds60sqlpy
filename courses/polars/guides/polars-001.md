# polars-001: Rows, columns, schemas and expressions

## Level and prerequisites

Beginner. Direct prerequisites: `python-03`

**Outcome:** Construct and verify a typed table with a stated row grain.

## Question and mechanism

A table is useful only when its rows have a defined meaning. Here a row represents one order, and order_id is its identifier. A column contains values of one logical type; a Series is a single named column, while a DataFrame combines columns of equal length. A schema maps column names to types. Shape tells you how many rows and columns exist, but cannot establish uniqueness, valid units or correct totals.

Polars expressions describe a computation over columns. pl.col("units") is a request to use the units column, not the Python value of one row. Multiplying it by the price expression defines a result for each order. with_columns evaluates those expressions in the context of the input frame and returns a frame with the requested columns. The original Python variable still refers to the original frame. This makes intermediate states inspectable and helps separate raw records from derived quantities.

Start by writing the row grain and unit for every numeric column. Units are counts and price is whole currency units per item in this fixture, so their product is revenue per order. Summing that product answers an aggregate question without changing the meaning of the underlying rows. In a real dataset, discounts, returns and taxes would require a more explicit revenue definition.

## Syntax and data contract

The constructor pl.DataFrame receives a mapping from column names to equally sized Python sequences. The expression (pl.col("units") * pl.col("price")).alias("revenue") has three parts: two column selections, multiplication and a name for the result. select chooses the columns or reductions returned; with_columns retains existing columns. item() is appropriate only when a result contains exactly one cell. Inspect schema, shape and to_dicts() before making a claim about the analysis.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Derive order revenue

The first case keeps all three order identifiers and derives a fourth column. It asserts both the individual products and their sum, because a correct total can conceal offsetting row errors. The input-frame assertion also checks that the transformation did not silently redefine the raw table.

**Expected evidence:** Revenue is [10, 8, 12], total 30; input shape remains 3 by 3 and output shape is 3 by 4.

```python
import polars as pl


def example_one():
    frame = pl.DataFrame({"order_id": [1, 2, 3], "units": [2, 1, 4], "price": [5, 8, 3]})
    result = frame.with_columns((pl.col("units") * pl.col("price")).alias("revenue"))
    assert frame.shape == (3, 3) and result.shape == (3, 4)
    assert result["revenue"].to_list() == [10, 8, 12]
    assert result.select(pl.col("revenue").sum()).item() == 30
    assert "revenue" not in frame.columns
    return {"rows": result.to_dicts(), "total_revenue": 30}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: An empty result still has a schema

The second case defines column types explicitly, then filters every row out. An empty table remains a typed result. Its existence is different from a missing variable or a failed query. Reordering columns changes the presentation contract while preserving values.

**Expected evidence:** The empty frame has 0 rows and the original Int64/String schema; selecting label,id produces that order.

```python
import polars as pl


def example_two():
    frame = pl.DataFrame(
        {"id": [1, 2], "label": ["new", "done"]}, schema={"id": pl.Int64, "label": pl.String}
    )
    assert frame.schema == {"id": pl.Int64, "label": pl.String}
    empty = frame.filter(pl.col("id") > 10)
    assert empty.height == 0 and empty.schema == frame.schema
    selected = frame.select("label", "id")
    assert selected.columns == ["label", "id"]
    return {"empty_shape": empty.shape, "schema": str(empty.schema)}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Predict a new order

Append an order with units 3 and price 4, then predict the total before running.

**Check:** The total is 42 and there are 4 order rows.

**Hint:** Compute the new row contribution first.


### 2. Choose a projection

Return order_id and revenue only.

**Check:** The output has 3 rows and 2 columns.

**Hint:** Use select after defining revenue.


### 3. Explain an aggregate

Replace the final sum with a mean and describe its denominator.

**Check:** Mean order revenue is 10.

**Hint:** There are 3 orders, not 7 items.


### 4. Keep raw state

Check that calling with_columns did not add revenue to frame.

**Check:** The assertion remains true.

**Hint:** Compare frame.columns and result.columns.


### 5. State an empty policy

Filter to orders above 100 and explain whether a zero-row output is an error.

**Check:** The schema remains defined and height is 0.

**Hint:** Distinguish absence of qualifying rows from failed execution.


### 6. Validate identifiers

Add a duplicate order_id and test the proposed key.

**Check:** n_unique is smaller than height.

**Hint:** Column type does not prove uniqueness.


## Diagnose errors and misleading results

A ShapeError usually means constructor columns have different lengths. A missing-column error means the expression names a field unavailable in that context. Neither is fixed by converting all values to strings. If the total differs, inspect the row products and row count before modifying aggregation code. A successful sum also does not establish a valid revenue definition: negative quantities, repeated identifiers and mixed currencies are semantic cases that require explicit policy.

## Transfer to independent work

Construct and verify a typed table with a stated row grain. For an independent case, use a small inventory table with units and cost, calculate stock value, and verify it with Python arithmetic. Preserve both raw and transformed frames so a reviewer can explain every changed field. This establishes a small data contract, not a guarantee that an arbitrary input file is clean.

## Primary references

- [Polars documentation: Rows, columns, schemas and expressions](https://docs.pola.rs/user-guide/concepts/data-structures/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-001`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
