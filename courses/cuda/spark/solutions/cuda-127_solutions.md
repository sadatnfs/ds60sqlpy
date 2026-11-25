# cuda-127: explained solutions

Compare with your [worksheet](../lessons/cuda-127.md) attempt.

## Exercise 1: Derive expected revenue

A revenue is \((2+4)\times10=60\), and B revenue is \(3\times20=60\).

**Approach.** Derive expected revenue by joining sales to prices and summing quantity times price per product: A is `(2 + 4)*10 = 60` and B is `3*20 = 60`.

**Why it is correct here.** Each sale row matches exactly one price row, so revenue per product is the sum of quantities times that price. The integer fixture gives exact output with no tolerance needed.

**A plausible wrong approach.** Summing prices per product before multiplying, or multiplying the total quantity by the sum of all prices, mixes products and gives wrong totals such as 180 for A.

**How to verify.** The reference asserts `[('A', 60), ('B', 60)]`. Both the Scala and PySpark pipelines must produce exactly these rows after sorting by product.

## Exercise 2: Write Scala expressions

Use explicit schema join and groupBy.

**Approach.** Write the Scala pipeline with an explicit schema for both tables, `sales.join(prices, "product")`, a column `quantity * price`, and `groupBy("product").agg(sum(...))`.

**Why it is correct here.** An explicit schema fixes column types, so integer arithmetic stays exact and the join key types match. Each step maps directly to the reference loop.

**A plausible wrong approach.** Relying on schema inference from text files can type numbers as strings or doubles, changing join behavior or output types between runs.

**How to verify.** Print the schema and the sorted result, and compare the result with the reference revenue.

## Exercise 3: Write PySpark expressions

Match those operations and sort output.

**Approach.** Write the PySpark pipeline with the same schema, join, product column and aggregation, then `orderBy("product")` so output order is defined.

**Why it is correct here.** Both languages build the same logical plan through Catalyst, so the outputs must be equal. Sorting removes order differences that are not semantic.

**A plausible wrong approach.** Collecting rows into Python and summing in a loop changes where the work runs and stops being a Spark pipeline comparison.

**How to verify.** Compare the PySpark output rows with the Scala output rows and with the reference, and compare the physical plans for the same operators.

## Exercise 4: Test duplicate dimension keys

Reject or explicitly accept multiplicity.

**Approach.** Test duplicate dimension keys: adding a second price row for A doubles A's matches, so the contract must either reject non-unique prices or explicitly accept the multiplicity.

**Why it is correct here.** A join multiplies rows for duplicate keys. If the business rule says one price per product, a uniqueness check protects revenue from silent doubling.

**A plausible wrong approach.** Running the join without checking lets a duplicate price row double A to 120 with no error, which looks like a real sales increase.

**How to verify.** Add the duplicate row, assert the uniqueness check fails with a clear message, and confirm revenue is unchanged when the check passes.

## Exercise 5: Capture executed GPU evidence

Require plans metrics and equality on actual hardware.

**Approach.** Capture executed GPU evidence on actual hardware: the final physical plan showing GPU operators for the join and aggregate, operator metrics, and output equal to the CPU result.

**Why it is correct here.** Each piece rules out a different gap, such as configuration without execution or execution with different results.

**A plausible wrong approach.** Claiming GPU execution from a CPU-only environment, or from a configuration file alone, reports evidence that does not exist.

**How to verify.** Store the plan, metrics and comparison from one run, and mark the item pending if no GPU host was available.

## Exercise 6: Prepare a balanced capstone report

Include CPU functionality and pending GPU limitations separately.

**Approach.** Prepare a balanced capstone report separating verified CPU functionality, such as matching Scala and PySpark outputs, from pending GPU validation and its limitations.

**Why it is correct here.** A reader needs to know what was proven and what remains open. Mixing them overstates the result.

**A plausible wrong approach.** Writing the report as if GPU acceleration was demonstrated when only CPU runs happened misleads anyone deciding on deployment.

**How to verify.** Check each claim in the report against a recorded run, and list every item that still requires hardware.

## Self-check answers

1. **Why run both ordinary Spark implementations before any GPU comparison?** Semantic agreement must be established first, so later differences point to the backend rather than the query.

2. **What does a GPU report need besides timing?** The compatibility matrix, initial and executed plans, unsupported reasons, resource assignment, concurrency and memory observations.

3. **When may the query text change across backends?** Only as a separately named rewrite that is revalidated against the oracle.

## Reference observation

Sorted revenue [(A,60),(B,60)].

Asserted by `courses/cuda/spark/references/cuda-127_cpu.py`.
