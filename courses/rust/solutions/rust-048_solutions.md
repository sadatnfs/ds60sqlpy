# rust-048: explanation and comparison

Executable reference: [rust-048_solution.rs](rust-048_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Summarize a nullable measurement column:** The calculation preserves a complete accounting of its five input positions. Three valid nonnegative values total five, alongside one null and one rejected negative.

**Keep empty and all-null data distinct:** A total of zero alone cannot express this distinction. No submitted rows and two missing observations remain different reports.

## Task answers

### Task 1: Predict and explain

Trace each value to accepted, null or rejected accounting.

**Written answer.** Example A has five positions. 2 is valid and nonnegative, so accepted. Position 1 is null and counted by `null_count`. 3 is accepted. -1 is valid but negative, so rejected. 0 is valid and nonnegative, so accepted. That gives 3 accepted with sum 5, 1 null and 1 rejected, and 3 + 1 + 1 equals the 5 submitted positions.

**Why it is correct.** Each position falls into exactly one category, so the three counts must add up to the input length. That identity is what the last assertion checks.

**Plausible wrong approach.** Rejecting 0 together with the negatives treats a valid zero as bad data and reports 2 accepted, 2 rejected.

**How to verify.** Assert `accepted.len() + values.null_count() + 1 == values.len()` with the rejected count computed from the data, not written as a literal.

### Task 2: Guided modification

Add another valid value and independently derive the new report.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Int32Array};
    let input = [Some(2), None, Some(3), Some(-1), Some(0), Some(4)];
    let values = Int32Array::from(input.to_vec());
    let accepted: Vec<i32> = values
        .iter()
        .flatten()
        .filter(|value| *value >= 0)
        .collect();
    let (mut sum, mut kept, mut nulls, mut rejected) = (0, 0, 0, 0);
    for item in input {
        match item {
            None => nulls += 1,
            Some(value) if value < 0 => rejected += 1,
            Some(value) => {
                sum += value;
                kept += 1;
            }
        }
    }
    assert_eq!((accepted.iter().sum::<i32>(), accepted.len()), (sum, kept));
    assert_eq!((values.null_count(), rejected), (nulls, 1));
    assert_eq!((sum, kept, nulls, rejected), (9, 4, 1, 1));
    Ok(())
}
```

**Observe:** Adding 4 gives a report of sum 9, four accepted, one null and one rejected, and the Arrow calculation matches a plain match-based derivation.

The derivation classifies the original Rust values with one `match`, without Arrow or `filter`, so agreement is evidence about the Arrow path rather than a repeat of it. The new value only changes the accepted sum and count.

**Plausible wrong approach.** Updating the expected numbers by hand from the old report, 5 + 4 and 3 + 1, checks arithmetic, not the program.

**How to verify.** Run the block. Change the new value to `Some(-4)` and the derivation reports sum 5 with two rejected, so the assertion expecting one rejected value fails.

### Task 3: Independent construction

Build a multi-column RecordBatch report and round-trip it through IPC.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** Take the null-as-zero defect: computing the report with `values.values().iter().filter(|value| **value >= 0)` reads the physical buffer, so Example A's null slot, which holds 0, is counted as an accepted 0. The report becomes 4 accepted, sum 5, 0 nulls, and the sum hides the error because the inserted value is zero. Count through `values.iter()`, which yields `None` for the null, and keep the accounting identity accepted + null + rejected = length as an assertion.

**Why it is correct.** The physical buffer has a slot for every row, including nulls, and Arrow does not promise what a null slot contains. Only iteration that applies validity separates missing data from a real zero.

**Plausible wrong approach.** Checking only the sum misses this defect entirely, since adding a zero leaves it at 5. The counts are what expose it.

**How to verify.** Run the buggy count on Example A and compare: 4 accepted against the correct 3, with the same sum.

### Task 5: Boundary evidence

Test empty, all-null, all-rejected, overflow and malformed-input boundaries.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Int32Array};
    fn report(values: &Int32Array) -> Result<(i32, usize, usize, usize), String> {
        let mut sum = 0_i32;
        let (mut accepted, mut rejected) = (0, 0);
        for value in values.iter().flatten() {
            if value < 0 {
                rejected += 1;
                continue;
            }
            sum = sum.checked_add(value).ok_or("total overflows i32")?;
            accepted += 1;
        }
        Ok((sum, accepted, values.null_count(), rejected))
    }
    assert_eq!(report(&Int32Array::from(Vec::<i32>::new()))?, (0, 0, 0, 0));
    assert_eq!(report(&Int32Array::from(vec![None, None]))?, (0, 0, 2, 0));
    assert_eq!(report(&Int32Array::from(vec![-1, -2]))?, (0, 0, 0, 2));
    assert!(report(&Int32Array::from(vec![i32::MAX, 1])).is_err());
    let parsed: Result<Vec<i32>, _> = ["2", "x"].iter().map(|text| text.parse::<i32>()).collect();
    assert!(parsed.is_err());
    Ok(())
}
```

**Observe:** Empty, all-null and all-rejected inputs give three different reports, an overflowing total returns an error, and the malformed text x fails before it can reach the column.

All three non-error cases have a sum of 0, so only the counts tell them apart. Overflow returns an error instead of a wrapped or panicking total, and malformed input is rejected at parsing, where the text is still available to report.

**Plausible wrong approach.** Using `sum += value` makes the overflow case panic in debug builds and wrap silently in release builds, so the report would depend on the build profile.

**How to verify.** Run the block. Replace `checked_add` with `wrapping_add` and the overflow case returns a negative sum instead of an error.

### Task 6: Transfer and justify

Deliver a project README with schema, ownership, bounds, failure policies, actual runtime evidence and one independent Arrow extension.

**Judging criteria.** A strong README states the schema with types and nullability, which function owns each buffer and when it is released, the bounds on memory and input size, and the failure policy for nulls, negatives and malformed rows. It shows actual output from a real run, not expected output, and describes one Arrow extension, such as a grouped total built with `take` or a filtered report, with its own acceptance check. State one limitation of the extension and the evidence that would show it works.

## Mechanism and diagnostic reasoning

The final project combines a schema, nullable columns, domain admission and a deterministic report. Arrow provides the representation and kernels; the application owns what counts as a valid measurement and how rejection is reported. A correct total must state its population and handling of missing values.

Build the portable kernel first, then extend the external InventoryLab or a separately prepared Arrow Cargo project. Keep package resolution, source compilation, runtime assertions, browser delivery and cross-language interchange evidence separate. Expert practice includes explaining limits and diagnosing unfamiliar failures, not assuming a finite tutorial covers every library or production architecture.

A typed nullable array exposes valid values through Option iteration. The application can count nulls, reject negative present values and sum the admitted population. A stable report record makes those decisions inspectable.

A passing kernel does not prove external storage, authentication or every architecture. Do not label Parquet, DataFusion or a distributed service supported without explicit dependency and runtime qualification. Retain source-bound evidence for the program actually executed.

## Review before continuing

Rebuild Example B (Keep empty and all-null data distinct) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
