# rust-043: CSV and JSON readers with explicit schemas

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-042`

## Learning objectives

Read CSV and JSON into Arrow with an explicit schema and validate domain rules afterward. The central exercise is task 3: Read a small nullable dataset and validate its domain ranges afterward.

## Purpose and mental model

CSV and JSON are external representations with their own syntax and ambiguity. CSV supports quoted delimiters and escaped quotes, so a naive split is not a general parser. JSON can contain fields with inconsistent types across records. An explicit Arrow schema gives the reader a target contract and makes incompatible values visible.

Automatic inference is useful exploration but should not silently become a production schema policy. A sample may miss later nulls or wider numeric ranges. Bound input size and batch size, inspect errors and validate domain constraints after decoding. The prepared crate includes actual CSV and newline-delimited JSON reader features; no separate package is fetched during a run.

## Vocabulary and concepts

**Schema inference:** Estimating a schema from observed data.

**NDJSON:** JSON objects separated by newlines for record-oriented streaming.

**Batch size:** The maximum records targeted in one reader output batch.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array`, `arrow::csv`, `arrow::datatypes`, `arrow::json`, `std::io` and `std::sync`. A passing run prints `rust-043: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

CSV ReaderBuilder takes a schema and with_header policy. JSON ReaderBuilder consumes newline-delimited object records. Both readers yield fallible RecordBatch values, and batch size bounds one produced chunk.

**Reading Example A (Read CSV through its real parser, code below).** The schema is built before any data is read: two non-nullable fields, `name` as `Utf8` and `quantity` as `Int32`. `ReaderBuilder::new(schema)` starts a reader configuration from that schema, so the parser does not infer types from the text. `with_header(true)` says the first line holds column names rather than data, and `with_batch_size(8)` caps each batch at eight rows. `build(Cursor::new(input))` accepts any `Read` source; the byte string literal `b"..."` has type `&[u8; N]`, and the `Cursor` makes it readable. Each call to `next` returns an `Option` wrapping a parse result, so `unwrap()` takes the first batch and `?` surfaces a parse failure.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Read CSV through its real parser

Header handling and column types are deliberate rather than guessed from a hand-written split.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use std::io::Cursor;
        use arrow::datatypes::{DataType, Field, Schema};
        let schema = Arc::new(Schema::new(vec![Field::new("name", DataType::Utf8, false), Field::new("quantity", DataType::Int32, false)]));
        let input = b"name,quantity\npear,2\napple,3\n";
        let mut reader = arrow::csv::ReaderBuilder::new(schema)
            .with_header(true)
            .with_batch_size(8)
            .build(Cursor::new(input))?;
        let batch = reader.next().unwrap()?;
        assert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));
        assert_eq!(batch.column(0).as_any().downcast_ref::<arrow::array::StringArray>().unwrap().value(0), "pear");
    }
    println!("rust-043: passed");
    Ok(())
}
```

**Observe:** The parser produces two rows under the explicit schema.

### Example B: Read newline-delimited JSON

Structural decoding retains missingness rather than converting it to zero.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use std::io::Cursor;
        use arrow::array::Int32Array;
        use arrow::datatypes::{DataType, Field, Schema};
        let schema = Arc::new(Schema::new(vec![Field::new("quantity", DataType::Int32, true)]));
        let input = b"{\"quantity\":2}\n{\"quantity\":null}\n";
        let mut reader = arrow::json::ReaderBuilder::new(schema)
            .with_batch_size(8)
            .build(Cursor::new(input))?;
        let batch = reader.next().unwrap()?;
        let values = batch
            .column(0)
            .as_any()
            .downcast_ref::<Int32Array>()
            .unwrap();
        assert_eq!(values.iter().collect::<Vec<_>>(), vec![Some(2), None]);
    }
    println!("rust-043: passed");
    Ok(())
}
```

**Observe:** JSON null becomes Arrow null under the declared nullable field.

## Exercises

1. **Predict and explain.** State the schema and framing expected by each reader.

2. **Guided modification.** Add a CSV quoted field containing a comma and inspect its single parsed value.

3. **Independent construction.** Read a small nullable dataset and validate its domain ranges afterward.

4. **Diagnose a defect.** Diagnose using the foundation split_once parser for general quoted CSV.

5. **Boundary evidence.** Test malformed numeric text, explicit null and records spanning more than one batch.

6. **Transfer and justify.** Design an inference-to-reviewed-schema workflow with checks for later type and nullability drift.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

NDJSON is not a single enclosing JSON array. Reader success does not establish domain validity. Always handle each yielded batch error rather than counting only successful batches.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Read CSV through its real parser) before changing anything, and confirm its observation: The parser produces two rows under the explicit schema.
2. Compare Example B (Read newline-delimited JSON) with Example A and name the first line whose behavior differs. Its observation is: JSON null becomes Arrow null under the declared nullable field.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: NDJSON is not a single enclosing JSON array.

Tempting approaches to rule out before you compare:

- **Task 1.** Passing a JSON array such as `[{"quantity":2}]` to the newline-delimited reader assumes the two JSON formats are interchangeable; it expects separate objects, not one enclosing array.
- **Task 2.** Expecting three fields from the first record counts every comma, as a plain split would; the parser would instead report an error if a row truly had an extra field.
- **Task 5.** Reading only the first batch and reporting 2 rows treats the first chunk as the whole file.

## Self-check and next step

Why does Example A pass an explicit schema to the CSV reader rather than inferring one from two rows? In Example B, how does a JSON `null` become an Arrow null, and what would you expect if the field were declared non-nullable? How does newline-delimited JSON differ from a single JSON array?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the Arrow 60 crate documentation](https://docs.rs/arrow/60.0.0/arrow/) for the CSV and JSON reader builders and `with_batch_size`.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-043: CSV and JSON readers with explicit schemas.
Read courses/rust/guides/rust-043.md and courses/rust/lessons/rust-043.rs. Prerequisites: rust-042.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-043_solution.rs and
courses/rust/solutions/rust-043_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
