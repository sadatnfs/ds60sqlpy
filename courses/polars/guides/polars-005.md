# polars-005: Aggregation grain and weighted quantities

## Level and prerequisites

Beginner. Direct prerequisites: `polars-002`, `polars-004`

**Outcome:** Build an aggregate whose numerator, denominator and weighting unit are explicit.

## Question and mechanism

Aggregation changes the grain of a table. An order-level frame becomes a customer-level frame when rows are grouped by customer and reduced to one result per customer. Every non-key output must describe how values inside the group are combined. A sum, a mean and a row count encode different questions; a plausible number does not establish that the question matches the decision.

Rates require particular care. If source rows contain successes and trials, the pooled rate is total successes divided by total trials. Averaging row-level rates gives equal weight to each row, even when one row contains one trial and another contains ninety-nine. The first example makes that difference large enough to inspect by hand. The two calculations are both mathematically defined, but they estimate different weighted quantities.

Missing values also affect denominators. pl.len counts group rows, while count on a column counts non-null values. A group with one row and no observed measurement should not be described as an observed zero. Preserve counts beside estimates so a later reader can distinguish a small group, an empty measurement set and a genuine zero outcome.

## Syntax and data contract

group_by defines the grouping keys and agg names the reductions. Sort the final result when row order is part of a comparison or published artifact. Compute a ratio after aggregating its numerator and denominator; this keeps their relationship visible. Give counts explicit names such as rows and observed rather than using one ambiguous n for all purposes.

## Mathematical interpretation

The pooled rate is \(\widehat p=\frac{\sum_i s_i}{\sum_i n_i}\). The equal-row rate is \(m^{-1}\sum_i s_i/n_i\). Here \(s_i\) is a success count, \(n_i\) its trial count and \(m\) the number of source rows. They agree only under additional weighting conditions.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Pool trials rather than average row rates

Group A has 1 success in 1 trial and 9 successes in 99 trials. Its pooled rate is 10/100. The equal-row mean overweights the one-trial row. The program reports that counterexample alongside the correct pooled quantities.

**Expected evidence:** The pooled rates are \(A=0.1\) and \(B=0.5\); the equal-row average for \(A\) is approximately \(0.545\).

```python
import polars as pl


def example_one():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "successes": [1, 9, 1], "trials": [1, 99, 2]})
    output = (
        frame.group_by("group")
        .agg(
            pl.col("successes").sum().alias("successes"),
            pl.col("trials").sum().alias("trials"),
            pl.len().alias("rows"),
        )
        .with_columns((pl.col("successes") / pl.col("trials")).alias("rate"))
        .sort("group")
    )
    assert output["rate"].to_list() == [0.1, 0.5]
    naive = (
        frame.filter(pl.col("group") == "A")
        .select((pl.col("successes") / pl.col("trials")).mean())
        .item()
    )
    assert abs(naive - 0.1) > 0.4
    return {"weighted_rates": output.to_dicts(), "wrong_equal_row_mean": naive}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Preserve missingness in group summaries

The second case emits row count, observed count and mean together. The all-null group remains present, and its mean remains absent. That is evidence about measurement availability, not evidence that the underlying quantity equals zero.

**Expected evidence:** Group A has 2 rows,1 observed value and mean 2; group B has 1 row,0 observed values and null mean.

```python
import polars as pl


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [2, None, None]})
    result = (
        frame.group_by("group")
        .agg(
            pl.len().alias("rows"),
            pl.col("value").count().alias("observed"),
            pl.col("value").mean().alias("mean"),
        )
        .sort("group")
    )
    assert result["rows"].to_list() == [2, 1]
    assert result["observed"].to_list() == [1, 0]
    assert result["mean"].to_list() == [2.0, None]
    return {"grain": "one row per group", "summary": result.to_dicts()}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Compute a global rate

Pool all three rate rows without grouping.

**Check:** The global rate is 11/102.

**Hint:** Sum both counts before division.


### 2. Find a zero denominator

Add a group with 0 successes and 0 trials.

**Check:** The output follows an explicit undefined-rate policy.

**Hint:** A zero-trial group contains no rate evidence.


### 3. Change the estimand

Describe when an equal-group average would be appropriate.

**Check:** The answer defines equal weighting of groups.

**Hint:** Weighting is part of the scientific question.


### 4. Audit row grain

Compare input row count with the number of group keys.

**Check:** Three input rows reduce to 2 groups.

**Hint:** A grouping operation changes output identity.


### 5. Report precision inputs

Keep success and trial counts beside each estimated rate.

**Check:** Both components are recoverable.

**Hint:** A displayed percentage alone loses information.


### 6. Handle an all-null group

Decide whether to retain group B in the measurement summary.

**Check:** Its observed count remains 0.

**Hint:** Do not impute without a model.


## Diagnose errors and misleading results

A rate above 1 can indicate numerator/denominator mismatch or join fanout. A mean that changes after a harmless-looking reshape may have changed its weighting unit. Inspect group keys, original grain and counts before adjusting formulas. Never compare unsorted group outputs positionally unless row order is explicitly part of the contract.

## Transfer to independent work

Build an aggregate whose numerator, denominator and weighting unit are explicit. Reconcile the totals independently with Python arithmetic, retain coverage counts, and then decide whether the result supports the intended comparison. Apply the same discipline to conversion rates, average losses and model-quality dashboards.

## Primary references

- [Polars documentation: Aggregation grain and weighted quantities](https://docs.pola.rs/user-guide/expressions/aggregation/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-005`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
