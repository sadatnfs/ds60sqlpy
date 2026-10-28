# polars-002: Expression contexts and explicit dependencies

## Level and prerequisites

Beginner. Direct prerequisites: `polars-001`

**Outcome:** Build a transformation whose dependency stages are explicit.

## Question and mechanism

Expressions are evaluated in a context supplied by a table operation. A selection can return a scalar reduction or a row-sized result. A with_columns call describes a set of column computations over the same input context. That distinction matters when one new column appears to depend on another new column in the same call. The expression using x sees the input x, not a partially updated value created by an earlier argument.

This is a data-dependency rule, not a promise about the machine's execution order. An optimizer can parallelize independent expressions precisely because their meaning does not depend on which argument happens to execute first. When a later expression needs an earlier result, create an explicit stage with another with_columns call. Naming intermediate fields is often clearer than trying to pack an entire pipeline into one large expression.

Strings require equal care. In many expression positions a bare string denotes a column name. pl.lit("paid") unambiguously describes a literal value. Conditions should state what happens for every row, including missing conditions, and each output should have a deliberate name. The purpose of an alias is to define a result schema, not merely to improve a printed table.

## Syntax and data contract

In pl.col("x")+1, x is selected from the current input. alias("x") asks the result to use that name, replacing the returned x column. Two calls form two contexts: frame.with_columns(...).with_columns(...). A when/then/otherwise expression constructs conditional values; pl.lit distinguishes a constant from a column reference. Prefer readable intermediate names when a calculation has several stages.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Parallel context versus sequential transformation

The first case updates x and calculates old_x_times_ten in the same call. The deliberately named output makes its dependency visible. A second pipeline creates another with_columns context, so the multiplication uses the updated x values. This is a minimal example of why argument order is not a substitute for a dependency graph.

**Expected evidence:** The same-call multiplication is[10,20,30]; the staged multiplication is[20,30,40].

```python
import polars as pl


def example_one():
    frame = pl.DataFrame({"x": [1, 2, 3]})
    output = frame.with_columns(
        (pl.col("x") + 1).alias("x"), (pl.col("x") * 10).alias("old_x_times_ten")
    )
    assert output.to_dict(as_series=False) == {"x": [2, 3, 4], "old_x_times_ten": [10, 20, 30]}
    sequential = frame.with_columns((pl.col("x") + 1).alias("x")).with_columns(
        (pl.col("x") * 10).alias("new_x_times_ten")
    )
    assert sequential["new_x_times_ten"].to_list() == [20, 30, 40]
    return {"parallel_context": output.to_dicts(), "explicit_dependency": sequential.to_dicts()}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Condition on a value and diagnose a missing field

The second case recognizes revenue only for paid rows. The predicate uses a literal string and the else branch returns a numeric zero. It separately demonstrates that naming an absent column raises a real error rather than producing an implicit all-null column.

**Expected evidence:** Recognized amounts are[5,0,11]; selecting a missing column is rejected.

```python
import polars as pl


def example_two():
    frame = pl.DataFrame({"status": ["paid", "pending", "paid"], "amount": [5, 7, 11]})
    output = frame.select(
        pl.when(pl.col("status") == pl.lit("paid"))
        .then(pl.col("amount"))
        .otherwise(pl.lit(0))
        .alias("recognized")
    )
    assert output["recognized"].to_list() == [5, 0, 11]
    assert frame.select(pl.lit("paid").alias("literal")).item() == "paid"
    try:
        frame.select(pl.col("missing"))
    except pl.exceptions.ColumnNotFoundError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"recognized": output.to_dicts(), "missing_column_rejected": rejected}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Change the increment

Increment x by 2 before the dependent multiplication.

**Check:** The staged values are[30,40,50].

**Hint:** The second context must see the new x.


### 2. Name the old value

Keep x unchanged and create incremented_x.

**Check:** Both x and incremented_x are visible.

**Hint:** Use a new alias.


### 3. Remove ambiguity

Produce a column containing the word paid for every row.

**Check:** Every returned value is the string paid.

**Hint:** A literal is different from pl.col("paid").


### 4. Change a business condition

Recognize pending amounts at half value and paid amounts at full value.

**Check:** The fixture total becomes 19.5.

**Hint:** Use explicit ordered conditions and a numeric else.


### 5. Break a dependency

Attempt to use a newly named alias in the same call before a second context exists.

**Check:** A missing-column error identifies the unavailable alias.

**Hint:** Inspect the input schema of that operation.


### 6. Compare two implementations

Write the same recognized amounts with a filter plus an aggregate.

**Check:** The paid total is 16 in both implementations.

**Hint:** Compare equivalent grains and denominators.


## Diagnose errors and misleading results

If an expression unexpectedly uses old values, inspect its context before suspecting nondeterministic execution. If a string causes a missing-column error, decide whether it represents a name or a literal. A conditional expression may still evaluate branches as expressions, so do not rely on it to protect an otherwise invalid operation. Make casts and denominator policies valid independently, then select the appropriate result.

## Transfer to independent work

Build a transformation whose dependency stages are explicit. Apply the same reasoning to feature pipelines: a normalized value should reference the intended cleaned field, and training and serving must agree on that order. Use intermediate schemas and a small hand-calculated fixture to review the pipeline before optimizing it.

## Primary references

- [Polars documentation: Expression contexts and explicit dependencies](https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-002`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
