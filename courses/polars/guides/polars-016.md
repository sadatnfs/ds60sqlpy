# polars-016: Native expressions and the boundary of Python UDFs

## Level and prerequisites

Advanced. Direct prerequisites: `polars-002`, `polars-010`, `polars-015`

**Outcome:** Use a Python UDF only with an explicit value, type and batching contract.

## Question and mechanism

A Python user-defined function can express logic that is not available as a native expression. Crossing that boundary can add interpreter overhead, reduce optimization opportunities and introduce hidden state. The right question is whether the extra flexibility is required by the problem and whether its semantics remain valid under the execution strategy.

A return dtype is part of the function contract. It helps the engine reason about downstream operations and avoids relying on accidental inference from an early value. A pure function returns a result from its inputs without depending on mutable external state, time, random global draws or side effects. This is especially important when an engine can evaluate a function in more than one batch or order.

Batch equivalence is stronger than purity alone. Subtracting the mean of each batch is deterministic and pure, but does not equal subtracting the mean of the complete dataset. A streamable declaration must be justified by the operation, not used as a performance switch. The worked counterexample shows two different answers from the same values.

## Syntax and data contract

map_elements calls a Python function for values and should declare return_dtype. Compare it with the corresponding native expression before choosing the more expensive interface. The batched counterexample uses ordinary Python arithmetic to expose a semantic issue independently of any query optimizer. A real map_batches adapter additionally needs its output schema and optimization assumptions to be correct.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Compare equivalent native and Python functions

Squaring values has a direct native expression. The Python UDF is included to compare the result and inspect the library warning, not to recommend a slower spelling for ordinary arithmetic. Equality is established on the fixture before discussing cost.

**Expected evidence:** Both implementations return [1,4,9].

```python
import polars as pl


def example_one():
    frame = pl.DataFrame({"x": [1, 2, 3]})
    native = frame.select((pl.col("x") * pl.col("x")).alias("square"))
    udf = frame.select(
        pl.col("x").map_elements(lambda value: value * value, return_dtype=pl.Int64).alias("square")
    )
    assert native.equals(udf)
    assert native["square"].to_list() == [1, 4, 9]
    return {"values": native.to_dicts(), "native_and_udf_equal_on_fixture": True}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Show a non-streamable transformation

The second case centers four values once globally and once within two batches. Both outputs sum to zero, so that aggregate check alone would miss the error. The individual values demonstrate the different transformation.

**Expected evidence:** Global values are [-3,-2,-1,6]; batch-centered values are [-0.5,0.5,-3.5,3.5].

```python
def example_two():
    values = [1.0, 2.0, 3.0, 10.0]
    global_centered = [x - sum(values) / len(values) for x in values]
    batches = [values[:2], values[2:]]
    incorrectly_batched = [x - sum(batch) / len(batch) for batch in batches for x in batch]
    assert global_centered == [-3.0, -2.0, -1.0, 6.0]
    assert incorrectly_batched == [-0.5, 0.5, -3.5, 3.5]
    assert global_centered != incorrectly_batched
    return {
        "whole_dataset_centering": global_centered,
        "invalid_batchwise_centering": incorrectly_batched,
    }


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Replace the UDF

Write the square operation using column expressions only.

**Check:** The values remain [1,4,9].

**Hint:** Use multiplication on the selected column.


### 2. State a return type

Explain what a UDF returning integers should declare.

**Check:** It declares the intended integer dtype.

**Hint:** Schema inference is not a domain specification.


### 3. Change batch boundaries

Center [1,2,3,10] in a different partition.

**Check:** The batchwise answer changes while the global answer does not.

**Hint:** Try three values in the first batch.


### 4. Find a weak check

Explain why a zero-sum check misses the centering defect.

**Check:** Both incorrect and correct outputs can sum to zero.

**Hint:** Check identified intermediate values.


### 5. Introduce hidden state

Describe the risk of incrementing a global counter inside a UDF.

**Check:** Output can depend on evaluation order or batching.

**Hint:** The engine controls evaluation strategy.


### 6. Design a valid two-pass method

Explain how to perform global centering in bounded stages.

**Check:** First obtain the global mean, then subtract that fixed value.

**Hint:** Separate estimation from application.


## Diagnose errors and misleading results

An inefficient-map warning is useful evidence that a native operation may exist. It is not proof that every UDF is wrong. A changed answer under batching is more serious: inspect hidden state, global reductions and schema promises. Do not disable validation flags solely to make a query execute.

## Transfer to independent work

Use a Python UDF only with an explicit value, type and batching contract. Demonstrate equivalence to a trusted result on contrasting fixtures and identify which optimization claims are justified. Preserve a native implementation whenever it is clearer and semantically equivalent.

## Primary references

- [Polars documentation: Native expressions and the boundary of Python UDFs](https://docs.pola.rs/user-guide/expressions/user-defined-python-functions/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-016`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
