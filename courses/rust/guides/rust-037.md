# rust-037: Arrow columnar memory and typed arrays

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-036`

## Learning objectives

Build typed Arrow arrays and read values through the Array trait. The central exercise is task 3: Construct paired integer and text columns with equal row counts.

## Purpose and mental model

Apache Arrow defines a columnar in-memory representation for analytical data. A typed array stores values of one logical type along with validity information and, for variable-width types, offsets and data buffers. This differs from a collection of row objects with independent allocations for every field.

Columnar layout can make scans and vectorized operations efficient, but Arrow is not a database, query optimizer or automatic distributed engine. Its arrays provide a representation and compute building blocks. The prepared Arrow 60 crate is real library code linked into the worker. Begin with typed arrays and the Array trait before using type-erased columns in a RecordBatch.

## Vocabulary and concepts

**Columnar layout:** Grouping values by column rather than storing independent row objects.

**Typed array:** An Arrow array with a known concrete element representation.

**Validity:** Information identifying which logical positions are null.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array`. A passing run prints `rust-037: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Int32Array stores signed 32-bit integer values. Importing the Array trait exposes common methods such as len and null_count. StringArray stores variable-width UTF-8 values. ArrayRef later erases concrete type behind Arc<dyn Array>.

**Reading Example A (Create a concrete integer column, code below).** `use arrow::array::{Array, Int32Array};` imports a concrete array type and the `Array` trait. The trait supplies methods shared by every array type, such as `null_count`, `is_null` and `is_valid`, and trait methods are callable only when the trait is in scope. `Int32Array::from(vec![2, 4, 6])` turns the vector into an Arrow values buffer: a contiguous, immutable block of 32-bit integers laid out by the Arrow columnar format, so other Arrow-aware code can read it without conversion. Because the input had no `Option` values, no validity bitmap is allocated, and every slot counts as valid. `value(1)` reads the slot at index 1 directly from the buffer; it does not consult validity, and it panics if the index is out of bounds. The column's data type, `Int32`, comes from the Rust type, so no schema is needed for a single array.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Create a concrete integer column

The trait supplies common array behavior while the concrete type supplies typed value access.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        assert_eq!(values.len(), 3);
        assert_eq!(values.value(1), 4);
        assert_eq!(values.null_count(), 0);
    }
    println!("rust-037: passed");
    Ok(())
}
```

**Observe:** The concrete column contains three non-null integers.

### Example B: Use a variable-width text column

Offsets and UTF-8 data support variable-width values without pretending every row has a fixed-size string slot.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, StringArray};
        let labels = StringArray::from(vec!["a", "longer", "é"]);
        assert_eq!(labels.len(), 3);
        assert_eq!(labels.value(1), "longer");
        assert_eq!(labels.value(2), "é");
    }
    println!("rust-037: passed");
    Ok(())
}
```

**Observe:** Different text lengths share one logical column.

## Exercises

1. **Predict and explain.** Identify logical length, type and null count.

2. **Guided modification.** Add a fourth value and inspect its typed access.

3. **Independent construction.** Construct paired integer and text columns with equal row counts.

4. **Diagnose a defect.** Diagnose treating Arrow as an automatically installed SQL engine.

5. **Boundary evidence.** Test an empty typed array and a non-ASCII string.

6. **Transfer and justify.** Compare row-object and columnar representations for a repeated analytical scan.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Value access at an invalid index still violates bounds. A library being linked does not mean every optional Arrow feature is enabled. Parquet and DataFusion are separate crates and workflows.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Create a concrete integer column) before changing anything, and confirm its observation: The concrete column contains three non-null integers.
2. Compare Example B (Use a variable-width text column) with Example A and name the first line whose behavior differs. Its observation is: Different text lengths share one logical column.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Value access at an invalid index still violates bounds.

Tempting approaches to rule out before you compare:

- **Task 1.** Reading `null_count() == 0` as proof that all values are meaningful mixes validity with domain rules: a non-null 0 or an empty string is still present.
- **Task 2.** Calling `values.value(4)` to reach the fourth value uses a one-based index and panics, because index 4 is past the end of a four-row array.
- **Task 5.** Using `value_length` as a character count reports 6 for 日本, which breaks a length limit stated in characters.

## Self-check and next step

What do `len()`, `value(1)` and `null_count()` return for Example A's `Int32Array`, and which buffers hold those facts? How does Example B's `StringArray` store "longer" and "é" in one column, and how many bytes does "é" occupy? Why must `is_null(i)` be checked before trusting `value(i)`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the Arrow 60 crate documentation](https://docs.rs/arrow/60.0.0/arrow/) for typed arrays such as `Int32Array`.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-037: Arrow columnar memory and typed arrays.
Read courses/rust/guides/rust-037.md and courses/rust/lessons/rust-037.rs. Prerequisites: rust-036.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-037_solution.rs and
courses/rust/solutions/rust-037_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
