# polars-009: Ordered windows and row-preserving statistics

## Level and prerequisites

Intermediate. Direct prerequisites: `polars-002`, `polars-005`, `polars-007`

**Outcome:** Create row-preserving historical features with explicit ordering.

## Question and mechanism

A grouped aggregation reduces a group to fewer rows. A window expression computes using a group and maps a result back to the original row grain. This distinction lets a feature pipeline attach group means, previous values or running totals without losing the identity of each event. It also creates opportunities for leakage if the group includes information unavailable at the row's decision time.

Order-sensitive windows need a total ordering rule. Sorting by customer and time is insufficient when two events share a timestamp and their relative order matters. A stable event identifier can serve as a tie-breaker, but only if that order has a meaningful interpretation. The worked fixture uses customer, time and id explicitly. The resulting previous value refers to that sorted sequence, not to an arbitrary input order.

Group centering illustrates a different kind of window. Subtracting a group mean keeps one output per row while using all measurements in that group. It is useful for descriptive analysis, but computing the mean from future or held-out rows would contaminate a deployed feature. Training-time fitting and online application therefore need an additional temporal or split boundary.

## Syntax and data contract

over("customer") assigns the expression to customer groups. cum_sum and shift(1) depend on the order established before the window operation. A reduction such as mean().over("group") broadcasts a group statistic back to each group row. Give the derived column a distinct alias and verify both its values and the unchanged row count.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Sort before computing event history

The first case begins in a deliberately shuffled order. It sorts by the full key before calculating running totals and prior values, including a missing predecessor for each customer's first event. This makes the historical interpretation explicit.

**Expected evidence:** Customer A running totals are [2, 7, 11], customer B has 7, and first predecessors are null.

```python
import polars as pl


def example_one():
    frame = pl.DataFrame(
        {
            "id": [3, 1, 2, 4],
            "customer": ["A", "A", "B", "A"],
            "time": [2, 1, 1, 3],
            "value": [5, 2, 7, 4],
        }
    )
    output = frame.sort("customer", "time", "id").with_columns(
        pl.col("value").cum_sum().over("customer").alias("running"),
        pl.col("value").shift(1).over("customer").alias("previous"),
    )
    assert output["running"].to_list() == [2, 7, 11, 7]
    assert output["previous"].to_list() == [None, 2, 5, None]
    assert output.height == frame.height
    return {"ordered_windows": output.to_dicts()}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Broadcast a statistic without collapsing rows

The second case compares a centered window result with a grouped aggregation. The values [-2, 2, 0] remain attached to three original observations, while grouping produces only two records.

**Expected evidence:** Window output has three rows; grouped means have two rows.

```python
import polars as pl


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [2.0, 6.0, 9.0]})
    centered = frame.with_columns(
        (pl.col("value") - pl.col("value").mean().over("group")).alias("centered")
    )
    assert centered["centered"].to_list() == [-2.0, 2.0, 0.0]
    assert frame.group_by("group").agg(pl.col("value").mean()).height == 2
    assert centered.height == 3
    return {"row_preserving_values": centered["centered"].to_list(), "grouped_rows": 2}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Shuffle the fixture

Change the input ordering and retain the explicit sort.

**Check:** The identified window results remain unchanged.

**Hint:** The sort is part of the computation.


### 2. Add a timestamp tie

Add a same-customer event sharing a timestamp and define its order.

**Check:** A documented tie-breaker produces a deterministic sequence.

**Hint:** A stable order is not automatically a causal order.


### 3. Exclude the current event

Compute the running value available before each event.

**Check:** For A it is [null, 2, 7] before an explicit first-value policy.

**Hint:** Shift the cumulative total within the same group.


### 4. Check group reset

Verify that B does not inherit A history.

**Check:** B has a missing predecessor.

**Hint:** The grouping key defines independent histories.


### 5. Review training leakage

Explain why full-dataset group centering can leak validation information.

**Check:** The explanation identifies which observations estimated the mean.

**Hint:** A window is not a fitted preprocessing boundary.


### 6. Compare grains

Replace the mean window with group_by and inspect row counts.

**Check:** The count changes from 3 to 2.

**Hint:** A reduction returns one result per key.


## Diagnose errors and misleading results

A plausible lag can still belong to a different customer. A cumulative sum can be deterministic but temporally invalid. Inspect grouping keys, timestamp ties and whether the current row should contribute. Keep first-event nulls visible until the missing-history policy is decided.

## Transfer to independent work

Create row-preserving historical features with explicit ordering. Test shuffled inputs, entity boundaries and timestamp ties, then document whether each feature includes the current event. Extend the rule to an availability-time boundary before using the feature in model training.

## Primary references

- [Polars documentation: Ordered windows and row-preserving statistics](https://docs.pola.rs/user-guide/expressions/window-functions/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-009`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
