# rust-048: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-048_solution.rs](rust-048_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Summarize a nullable measurement column:** The calculation preserves a complete accounting of its five input positions. Three valid nonnegative values total five, alongside one null and one rejected negative.

**Keep empty and all-null data distinct:** A total of zero alone cannot express this distinction. No submitted rows and two missing observations remain different reports.

## Task answers

### Task 1: Predict and explain

Trace each value to accepted, null or rejected accounting.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The calculation preserves a complete accounting of its five input positions. Three valid nonnegative values total five, alongside one null and one rejected negative.

### Task 2: Guided modification

Add another valid value and independently derive the new report.

No separate reference answer has been written for this task. Start from Example B: A total of zero alone cannot express this distinction. No submitted rows and two missing observations remain different reports.

### Task 3: Independent construction

Build a multi-column RecordBatch report and round-trip it through IPC.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{ArrayRef, Int32Array, StringArray};
    use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
    use arrow::record_batch::RecordBatch;
    use std::sync::Arc;
    let names: ArrayRef = Arc::new(StringArray::from(vec!["apple", "pear"]));
    let totals: ArrayRef = Arc::new(Int32Array::from(vec![5, 2]));
    let report = RecordBatch::try_from_iter(vec![("name", names), ("total", totals)])?;
    let mut bytes = Vec::new();
    {
        let mut writer = StreamWriter::try_new(&mut bytes, &report.schema())?;
        writer.write(&report)?;
        writer.finish()?;
    }
    let mut reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
    assert_eq!(reader.next().unwrap()?, report);
    assert!(reader.next().is_none());
    Ok(())
}
```

**Observe:** The two-column report round-trips unchanged and the stream ends after one batch.

Comparing whole batches checks the schema and every column together, and the second next() proves the stream was finished explicitly.

### Task 4: Diagnose a defect

Introduce and diagnose a null-as-zero, schema-order or duplicate-row defect.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A passing kernel does not prove external storage, authentication or every architecture. Do not label Parquet, DataFusion or a distributed service supported without explicit dependency and runtime qualification. Retain source-bound evidence for the program actually executed.

### Task 5: Boundary evidence

Test empty, all-null, all-rejected, overflow and malformed-input boundaries.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Summarize a nullable measurement column) and Example B (Keep empty and all-null data distinct).

### Task 6: Transfer and justify

Deliver a project README with schema, ownership, bounds, failure policies, actual runtime evidence and one independent Arrow extension.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Analytical contract**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

The final project combines a schema, nullable columns, domain admission and a deterministic report. Arrow provides the representation and kernels; the application owns what counts as a valid measurement and how rejection is reported. A correct total must state its population and handling of missing values.

Build the portable kernel first, then extend the external InventoryLab or a separately prepared Arrow Cargo project. Keep package resolution, source compilation, runtime assertions, browser delivery and cross-language interchange evidence separate. Expert practice includes explaining limits and diagnosing unfamiliar failures, not assuming a finite tutorial covers every library or production architecture.

A typed nullable array exposes valid values through Option iteration. The application can count nulls, reject negative present values and sum the admitted population. A stable report record makes those decisions inspectable.

A passing kernel does not prove external storage, authentication or every architecture. Do not label Parquet, DataFusion or a distributed service supported without explicit dependency and runtime qualification. Retain source-bound evidence for the program actually executed.

## Review before continuing

Run the reference and confirm that it prints `rust-048: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
