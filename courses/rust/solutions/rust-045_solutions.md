# rust-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-045_solution.rs](rust-045_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate bounded chunks:** The summary retains only counters, not a duplicate copy of every processed batch. Three chunks account for five rows and total fifteen.

**Account for rejected rows:** A rejection policy must preserve the denominator needed to interpret the result. Valid zero is retained and every input row is accounted for.

## Reason through the six tasks

1. **Predict and explain.** Trace chunk sizes and cumulative row counts.

2. **Guided modification.** Change the chunk size without changing the final result.

3. **Independent construction.** Apply the same accounting to an Arrow batch reader.

4. **Diagnose a defect.** Diagnose collecting all batches before claiming bounded-memory processing.

5. **Boundary evidence.** Test empty input, an all-rejected batch and a partial final batch.

6. **Transfer and justify.** Design cancellation and partial-output semantics for a long-running import.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A data pipeline needs bounds on admitted input, buffered batches, memory and output. Processing one batch at a time can reduce peak memory, but retaining every batch in a result vector defeats that design. A batch size is not a total-job limit, and one variable-width value can still be very large.

Preserve accounting at every boundary: submitted rows, valid rows, rejected rows and output rows should have defined relationships. Filtering changes row count while projection changes columns. Cancellation and partial failure need explicit outcome semantics so an incomplete report is not presented as complete. The fixture demonstrates deterministic batch accounting without a remote source.

Chunking a slice gives bounded views of owned input. An accumulator stores only the required summary. Checked arithmetic and explicit row counters prevent silent overflow or dropped-record accounting.

Batch size alone does not bound total memory or individual value size. A partial result needs an explicit incomplete status. Do not infer complete input consumption from a valid first batch.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
