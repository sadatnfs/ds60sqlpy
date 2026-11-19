# rust-043: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-043_solution.rs](rust-043_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Read CSV through its real parser:** Header handling and column types are deliberate rather than guessed from a hand-written split. The parser produces two rows under the explicit schema.

**Read newline-delimited JSON:** Structural decoding retains missingness rather than converting it to zero. JSON null becomes Arrow null under the declared nullable field.

## Task answers

### Task 1: Predict and explain

State the schema and framing expected by each reader.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Header handling and column types are deliberate rather than guessed from a hand-written split. The parser produces two rows under the explicit schema.

### Task 2: Guided modification

Add a CSV quoted field containing a comma and inspect its single parsed value.

No separate reference answer has been written for this task. Start from Example B: Structural decoding retains missingness rather than converting it to zero. JSON null becomes Arrow null under the declared nullable field.

### Task 3: Independent construction

Read a small nullable dataset and validate its domain ranges afterward.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, AsArray};
    use arrow::datatypes::{DataType, Field, Int32Type, Schema};
    use std::sync::Arc;
    let field = Field::new("quantity", DataType::Int32, true);
    let schema = Arc::new(Schema::new(vec![field]));
    let input = b"{\"quantity\":2}\n{\"quantity\":null}\n{\"quantity\":-1}\n";
    let mut reader = arrow::json::ReaderBuilder::new(schema).build(&input[..])?;
    let batch = reader.next().unwrap()?;
    let values = batch.column(0).as_primitive::<Int32Type>();
    let negative = values.iter().flatten().filter(|v| *v < 0).count();
    assert_eq!((values.len(), values.null_count(), negative), (3, 1, 1));
    Ok(())
}
```

**Observe:** Reading succeeds with 3 rows, 1 null and 1 negative value that the domain check then reports.

The schema decides what parses; the domain rule, nonnegative quantities, is a separate check run on the decoded values.

### Task 4: Diagnose a defect

Diagnose using the foundation split_once parser for general quoted CSV.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: NDJSON is not a single enclosing JSON array. Reader success does not establish domain validity. Always handle each yielded batch error rather than counting only successful batches.

### Task 5: Boundary evidence

Test malformed numeric text, explicit null and records spanning more than one batch.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Read CSV through its real parser) and Example B (Read newline-delimited JSON).

### Task 6: Transfer and justify

Design an inference-to-reviewed-schema workflow with checks for later type and nullability drift.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Schema inference**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

CSV and JSON are external representations with their own syntax and ambiguity. CSV supports quoted delimiters and escaped quotes, so a naive split is not a general parser. JSON can contain fields with inconsistent types across records. An explicit Arrow schema gives the reader a target contract and makes incompatible values visible.

Automatic inference is useful exploration but should not silently become a production schema policy. A sample may miss later nulls or wider numeric ranges. Bound input size and batch size, inspect errors and validate domain constraints after decoding. The prepared crate includes actual CSV and newline-delimited JSON reader features; no separate package is fetched during a run.

CSV ReaderBuilder takes a schema and with_header policy. JSON ReaderBuilder consumes newline-delimited object records. Both readers yield fallible RecordBatch values, and batch size bounds one produced chunk.

NDJSON is not a single enclosing JSON array. Reader success does not establish domain validity. Always handle each yielded batch error rather than counting only successful batches.

## Review before continuing

Run the reference and confirm that it prints `rust-043: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
