# rust-043: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-043_solution.rs](rust-043_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Read CSV through its real parser:** Header handling and column types are deliberate rather than guessed from a hand-written split. The parser produces two rows under the explicit schema.

**Read newline-delimited JSON:** Structural decoding retains missingness rather than converting it to zero. JSON null becomes Arrow null under the declared nullable field.

## Reason through the six tasks

1. **Predict and explain.** State the schema and framing expected by each reader.

2. **Guided modification.** Add a CSV quoted field containing a comma and inspect its single parsed value.

3. **Independent construction.** Read a small nullable dataset and validate its domain ranges afterward.

4. **Diagnose a defect.** Diagnose using the foundation split_once parser for general quoted CSV.

5. **Boundary evidence.** Test malformed numeric text, explicit null and records spanning more than one batch.

6. **Transfer and justify.** Design an inference-to-reviewed-schema workflow with checks for later type and nullability drift.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

CSV and JSON are external representations with their own syntax and ambiguity. CSV supports quoted delimiters and escaped quotes, so a naive split is not a general parser. JSON can contain fields with inconsistent types across records. An explicit Arrow schema gives the reader a target contract and makes incompatible values visible.

Automatic inference is useful exploration but should not silently become a production schema policy. A sample may miss later nulls or wider numeric ranges. Bound input size and batch size, inspect errors and validate domain constraints after decoding. The prepared crate includes actual CSV and newline-delimited JSON reader features; no separate package is fetched during a run.

CSV ReaderBuilder takes a schema and with_header policy. JSON ReaderBuilder consumes newline-delimited object records. Both readers yield fallible RecordBatch values, and batch size bounds one produced chunk.

NDJSON is not a single enclosing JSON array. Reader success does not establish domain validity. Always handle each yielded batch error rather than counting only successful batches.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
