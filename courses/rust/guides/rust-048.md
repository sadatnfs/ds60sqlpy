# rust-048: Capstone: a validated Arrow analytical report

## Level and prerequisites

Advanced, approximately 180 minutes. Prerequisites: `rust-047`

## Learning objectives

Build a validated Arrow report with honest accounting and round-trip it through IPC. The central exercise is task 3: Build a multi-column RecordBatch report and round-trip it through IPC.

## Purpose and mental model

The final project combines a schema, nullable columns, domain admission and a deterministic report. Arrow provides the representation and kernels; the application owns what counts as a valid measurement and how rejection is reported. A correct total must state its population and handling of missing values.

Build the portable kernel first, then extend the external InventoryLab or a separately prepared Arrow Cargo project. Keep package resolution, source compilation, runtime assertions, browser delivery and cross-language interchange evidence separate. Expert practice includes explaining limits and diagnosing unfamiliar failures, not assuming a finite tutorial covers every library or production architecture.

## Vocabulary and concepts

**Analytical contract:** The population, units and missingness rules defining a calculation.

**Acceptance evidence:** Observed results establishing a declared requirement.

**Extension boundary:** A deliberate interface for adding a new capability.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array`. A passing run prints `rust-048: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).

Use [InventoryLab](../fixtures/InventoryLab/README.md) for the real library/project structure. The Arrow classroom dependency is already prepared; any independent Cargo project must deliberately prepare and lock Arrow60 before claiming offline builds.

## Syntax anatomy and execution trace

A typed nullable array exposes valid values through Option iteration. The application can count nulls, reject negative present values and sum the admitted population. A stable report record makes those decisions inspectable.

**Reading Example A (Summarize a nullable measurement column, code below).** `Int32Array::from` with `Option` items builds a nullable column. `values.iter()` yields an `Option<i32>` for each row by reading the validity bitmap, and `flatten()` drops the `None` rows, so nulls never reach the filter. `filter(|value| *value >= 0)` receives a reference to each remaining value, hence the `*`, and keeps the nonnegative ones. `collect` into `Vec<_>` materializes the accepted values. The last assertion is the accounting identity: total rows minus nulls minus accepted rows must equal the number rejected, so every row is counted exactly once in one of the three groups. `null_count` reads a stored count rather than rescanning the rows.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Summarize a nullable measurement column

The calculation preserves a complete accounting of its five input positions.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![Some(2), None, Some(3), Some(-1), Some(0)]);
        let accepted: Vec<_> = values
            .iter()
            .flatten()
            .filter(|value| *value >= 0)
            .collect();
        assert_eq!(accepted.iter().sum::<i32>(), 5);
        assert_eq!(accepted.len(), 3);
        assert_eq!(values.null_count(), 1);
        assert_eq!(values.len() - values.null_count() - accepted.len(), 1);
    }
    println!("rust-048: passed");
    Ok(())
}
```

**Observe:** Three valid nonnegative values total five, alongside one null and one rejected negative.

### Example B: Keep empty and all-null data distinct

A total of zero alone cannot express this distinction.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let empty = Int32Array::from(Vec::<Option<i32>>::new());
        let missing = Int32Array::from(vec![None::<i32>, None]);
        assert_eq!((empty.len(), empty.null_count()), (0, 0));
        assert_eq!((missing.len(), missing.null_count()), (2, 2));
    }
    println!("rust-048: passed");
    Ok(())
}
```

**Observe:** No submitted rows and two missing observations remain different reports.

## Exercises

1. **Predict and explain.** Trace each value to accepted, null or rejected accounting.

2. **Guided modification.** Add another valid value and independently derive the new report.

3. **Independent construction.** Build a multi-column RecordBatch report and round-trip it through IPC.

4. **Diagnose a defect.** Introduce and diagnose a null-as-zero, schema-order or duplicate-row defect.

5. **Boundary evidence.** Test empty, all-null, all-rejected, overflow and malformed-input boundaries.

6. **Transfer and justify.** Deliver a project README with schema, ownership, bounds, failure policies, actual runtime evidence and one independent Arrow extension.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A passing kernel does not prove external storage, authentication or every architecture. Do not label Parquet, DataFusion or a distributed service supported without explicit dependency and runtime qualification. Retain source-bound evidence for the program actually executed.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Summarize a nullable measurement column) before changing anything, and confirm its observation: Three valid nonnegative values total five, alongside one null and one rejected negative.
2. Compare Example B (Keep empty and all-null data distinct) with Example A and name the first line whose behavior differs. Its observation is: No submitted rows and two missing observations remain different reports.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A passing kernel does not prove external storage, authentication or every architecture.

Tempting approaches to rule out before you compare:

- **Task 1.** Rejecting 0 together with the negatives treats a valid zero as bad data and reports 2 accepted, 2 rejected.
- **Task 2.** Updating the expected numbers by hand from the old report, 5 + 4 and 3 + 1, checks arithmetic, not the program.
- **Task 5.** Using `sum += value` makes the overflow case panic in debug builds and wrap silently in release builds, so the report would depend on the build profile.

## Self-check and next step

In Example A, which values make up the total of 5, and why do the null and the rejected negative appear as counts rather than vanishing? In Example B, why must an empty input and two missing observations produce different reports? Which acceptance check would fail if nulls were silently treated as zero?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the Arrow 60 crate documentation](https://docs.rs/arrow/60.0.0/arrow/) for the array and compute APIs the capstone combines.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-048: Capstone: a validated Arrow analytical report.
Read courses/rust/guides/rust-048.md and courses/rust/lessons/rust-048.rs. Prerequisites: rust-047.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-048_solution.rs and
courses/rust/solutions/rust-048_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
