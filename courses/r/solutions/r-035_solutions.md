# r-035: reference reasoning

Use the [complete reference](r-035_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The negative and missing amounts remain distinct original inputs, even though both violate the same finite-nonnegative amount rule.

The validator does not silently rename an unexpected field or guess that value must mean amount. Structural drift gets an explicit failure.

## Explained practice

### Exercise 1

Count admitted records in the first example.

Only A is admitted.

**Expected evidence:** Only A is admitted.

### Exercise 2

Make the empty-ID row also have a negative amount.

The row has both missing_id and invalid_amount flags.

**Expected evidence:** The row has both missing_id and invalid_amount flags.

### Exercise 3

Return admitted and quarantined tables with stable IDs.

Their counts reconcile to the input count.

**Expected evidence:** Their counts reconcile to the input count.

### Exercise 4

Diagnose replacing every invalid numeric parse with zero.

Preserve a parse-failure signal and apply an explicit admission policy.

**Expected evidence:** Preserve a parse-failure signal and apply an explicit admission policy.

### Exercise 5

Validate a zero-row table with the correct schema.

An empty but correctly typed batch can be admitted under a stated empty-batch policy.

**Expected evidence:** An empty but correctly typed batch can be admitted under a stated empty-batch policy.

### Exercise 6

Explain what local validation cannot prove.

Range and schema checks do not establish representativeness, causality, freshness or measurement accuracy.

**Expected evidence:** Range and schema checks do not establish representativeness, causality, freshness or measurement accuracy.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
