# rust-043: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-043_solution.rs](rust-043_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Read CSV through its real parser:** Header handling and column types are deliberate rather than guessed from a hand-written split. The parser produces two rows under the explicit schema.

**Read newline-delimited JSON:** Structural decoding retains missingness rather than converting it to zero. JSON null becomes Arrow null under the declared nullable field.

## Task answers

### Task 1: Predict and explain

State the schema and framing expected by each reader.

**Written answer.** The CSV reader in Example A expects comma-separated text with one header line, enabled by `with_header(true)`, and then one record per line with exactly the declared fields, `name` as `Utf8` and `quantity` as `Int32`. The JSON reader in Example B expects newline-delimited JSON: one complete object per line, with keys matched to field names, here a nullable `quantity`. Both take the schema from you instead of guessing it, and both return batches of at most 8 rows.

**Why it is correct.** Framing decides how bytes split into records and fields, and the schema decides how each field is decoded. Stating both makes a type or format surprise an error, not a silent change.

**Plausible wrong approach.** Passing a JSON array such as `[{"quantity":2}]` to the newline-delimited reader assumes the two JSON formats are interchangeable; it expects separate objects, not one enclosing array.

**How to verify.** Remove `with_header(true)` from Example A and the header line is parsed as data, failing to decode `quantity` as an `Int32`.

### Task 2: Guided modification

Add a CSV quoted field containing a comma and inspect its single parsed value.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, AsArray};
    use arrow::datatypes::{DataType, Field, Schema};
    use std::sync::Arc;
    let schema = Arc::new(Schema::new(vec![
        Field::new("name", DataType::Utf8, false),
        Field::new("quantity", DataType::Int32, false),
    ]));
    let input = b"name,quantity\n\"pear, ripe\",2\napple,3\n";
    let mut reader = arrow::csv::ReaderBuilder::new(schema)
        .with_header(true)
        .build(std::io::Cursor::new(&input[..]))?;
    let batch = reader.next().unwrap()?;
    let names = batch.column(0).as_string::<i32>();
    assert_eq!(batch.num_rows(), 2);
    assert_eq!(names.value(0), "pear, ripe");
    assert_eq!(names.len(), 2);
    Ok(())
}
```

**Observe:** The quoted field becomes the single value pear, ripe, and the batch still has two rows of two columns.

The CSV parser treats a comma inside double quotes as part of the value and removes the quotes, so the row keeps exactly two fields. That rule is part of the CSV format, which is why a real parser is needed here.

**Plausible wrong approach.** Expecting three fields from the first record counts every comma, as a plain split would; the parser would instead report an error if a row truly had an extra field.

**How to verify.** Run the block. Remove the quotes around `pear, ripe` and the reader returns an error for the extra field.

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

**Written answer.** The defect is reusing InventoryLab's `line.split_once(',')` on general CSV. For the record `"pear, ripe",2` it returns the name `"pear` and the quantity ` ripe",2`, which fails to parse, so a valid row is counted as rejected. It also keeps quotes in names, cannot handle a newline inside a quoted value and ignores the header. Use `arrow::csv::ReaderBuilder` with an explicit schema, as in Example A and task 2.

**Why it is correct.** InventoryLab documents its format as a deliberately simple two-field fixture, not quoted CSV. Moving that parser to a different input format changes its contract without changing its code.

**Plausible wrong approach.** Switching to `rsplit_once(',')` happens to fix this one row but still mishandles quotes in the last field and escaped quotes.

**How to verify.** Evaluate `"\"pear, ripe\",2".split_once(',')` and compare it with the task 2 result: the split gives two broken pieces, the parser gives `pear, ripe` and 2.

### Task 5: Boundary evidence

Test malformed numeric text, explicit null and records spanning more than one batch.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::Array;
    use arrow::datatypes::{DataType, Field, Schema};
    use std::io::Cursor;
    use std::sync::Arc;
    let schema = Arc::new(Schema::new(vec![
        Field::new("name", DataType::Utf8, false),
        Field::new("quantity", DataType::Int32, true),
    ]));
    let bad = b"name,quantity\npear,2\nfig,x\n";
    let mut reader = arrow::csv::ReaderBuilder::new(schema.clone())
        .with_header(true)
        .build(Cursor::new(&bad[..]))?;
    assert!(reader.next().unwrap().is_err());
    let input = b"name,quantity\npear,2\nfig,\nkiwi,4\n";
    let reader = arrow::csv::ReaderBuilder::new(schema)
        .with_header(true)
        .with_batch_size(2)
        .build(Cursor::new(&input[..]))?;
    let mut sizes = Vec::new();
    let mut nulls = 0;
    for batch in reader {
        let batch = batch?;
        sizes.push(batch.num_rows());
        nulls += batch.column(1).null_count();
    }
    assert_eq!(sizes, vec![2, 1]);
    assert_eq!(nulls, 1);
    Ok(())
}
```

**Observe:** The text x in an Int32 column makes the reader return an error. The three valid rows arrive as batches of 2 and 1, with the empty quantity for fig read as one null.

A parse error is reported for the batch containing it, so the caller must decide what happens to the whole input. An empty field in a nullable column is an explicit null, not 0, and a batch size of 2 makes the third record start a second batch.

**Plausible wrong approach.** Reading only the first batch and reporting 2 rows treats the first chunk as the whole file.

**How to verify.** Run the block. Print the error with `{:?}`; it names the value x, the type Int32 and line 2.

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
