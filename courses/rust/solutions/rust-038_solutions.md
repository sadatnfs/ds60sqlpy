# rust-038: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-038_solution.rs](rust-038_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve null versus zero:** Optional iteration respects validity rather than exposing meaningless physical contents at null positions. A valid zero and a null remain distinct positions.

**Keep NaN separate from null:** A finite-value policy is an additional analytical rule, not a synonym for Arrow validity. The column contains one null, one present NaN and one finite value.

## Reason through the six tasks

1. **Predict and explain.** Classify zero, null and NaN separately.

2. **Guided modification.** Add a present infinity and update finite-value accounting.

3. **Independent construction.** Write a summary returning valid, null and finite counts.

4. **Diagnose a defect.** Diagnose summing physical values without applying validity.

5. **Boundary evidence.** Test all-null, empty and no-null columns.

6. **Transfer and justify.** Define missingness and non-finite policies for a sensor dataset before calculating a mean.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A null means the logical value is absent under the dataset's policy. The physical value buffer can still contain bytes at that position, but those bytes are not a valid observation. Always consult validity or use an iterator returning Option. Reading value at a null position and treating its physical contents as data can silently corrupt an analysis.

NaN is a floating-point value category, not an Arrow null. It can represent an undefined numerical result while remaining logically present. A pipeline must decide separately how to handle missing and non-finite measurements. Conflating them changes counts, means and validation outcomes.

Array::is_null and is_valid inspect validity. Int32Array::iter yields Option<i32>. Float64Array can contain both Some(NaN) and None. null_count counts absence, not non-finite values.

Null positions can contain arbitrary physical values. NaN is not equal to itself under ordinary floating equality. Do not replace every null with zero without a domain justification.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
