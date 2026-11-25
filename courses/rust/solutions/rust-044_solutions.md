# rust-044: explanation and comparison

Executable reference: [rust-044_solution.rs](rust-044_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Preserve decimal interpretation:** The raw coefficient alone does not state the decimal amount. Coefficient 125 with scale two represents 1.25 under the declared contract.

**Keep timestamp units explicit:** The logical type prevents a consumer from legitimately treating the same coefficient as seconds without conversion. The second value is one thousand milliseconds after the epoch.

## Task answers

### Task 1: Predict and explain

Explain coefficient, scale and represented amount separately.

**Written answer.** In Example A the stored coefficient is the integer 125. The scale 2, from the type `Decimal128(10, 2)`, says the decimal point sits two digits from the right. The represented amount is therefore 125 times 10 to the power of minus 2, which is 1.25. Precision 10 limits the coefficient to at most 10 digits.

**Why it is correct.** Decimal types store exact integers and carry the scale in the type, so the same coefficient means a different amount under a different scale. Only the coefficient and scale together state the amount.

**Plausible wrong approach.** Reading `prices.value(0)` as the price gives 125, a hundred times too large, because it returns the coefficient.

**How to verify.** Assert `prices.value_as_string(0) == "1.25"` next to `prices.value(0) == 125`.

### Task 2: Guided modification

Add a negative decimal coefficient and retain its scale.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Decimal128Array};
    use arrow::datatypes::DataType;
    let prices =
        Decimal128Array::from(vec![125_i128, 250, -375]).with_precision_and_scale(10, 2)?;
    assert_eq!(prices.value(2), -375);
    assert_eq!(prices.value_as_string(2), "-3.75");
    assert_eq!(prices.data_type(), &DataType::Decimal128(10, 2));
    assert_eq!(prices.iter().flatten().sum::<i128>(), 0);
    Ok(())
}
```

**Observe:** The new coefficient -375 reads as -3.75 under the same scale, the type is still Decimal128(10, 2), and the three coefficients sum to 0.

The sign belongs to the coefficient and the scale applies to every value in the column, so a negative amount needs no special handling. Because all three values share scale 2, their coefficients can be added directly: 1.25 + 2.50 - 3.75 = 0.

**Plausible wrong approach.** Storing -3.75 as `-375` in a column with scale 3 means -0.375; a value's coefficient is only correct under its column's scale.

**How to verify.** Run the block. Change the scale to 3 and `value_as_string(2)` reports -0.375.

### Task 3: Independent construction

Create a schema documenting measurement units and timestamp precision.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::datatypes::{DataType, Field, Schema, TimeUnit};
    use std::collections::HashMap;
    let unit = HashMap::from([("unit".to_string(), "kg".to_string())]);
    let mass = Field::new("mass", DataType::Float64, false);
    let mass = mass.with_metadata(unit);
    let precision = DataType::Timestamp(TimeUnit::Millisecond, Some("UTC".into()));
    let time = Field::new("measured_at", precision.clone(), false);
    let schema = Schema::new(vec![mass, time]);
    let recorded = schema.field(0).metadata().get("unit");
    assert_eq!(recorded.map(String::as_str), Some("kg"));
    assert_eq!(schema.field(1).data_type(), &precision);
    Ok(())
}
```

**Observe:** The mass field records unit kg and the timestamp field records millisecond UTC precision.

Units live in field metadata and time precision in the data type, so both travel with the schema to every consumer.

### Task 4: Diagnose a defect

Diagnose reading milliseconds as seconds or losing decimal scale.

**Written answer.** Reading milliseconds as seconds means taking the raw value of a `Timestamp(Millisecond)` column, such as 1000 from Example B, and treating it as seconds, which places the event 1000 seconds after the epoch instead of 1 second. Casting with `arrow::compute::cast` to `Timestamp(Second, None)` converts correctly and gives 1, while a cast to `Int64` returns the raw 1000. Losing decimal scale is the same mistake for decimals: casting `Decimal128(10, 2)` 1.25 to `Int64` gives 1, and reading the coefficient with `value` gives 125. Convert through the logical type and keep the unit or scale in the schema.

**Why it is correct.** The unit and the scale live in the data type, not in the stored integer. Any step that keeps the integer but drops the type also drops that meaning.

**Plausible wrong approach.** Dividing by 1000 by hand after reading the raw value works for one column but repeats the unit rule in every consumer, and the next one to forget it is wrong again.

**How to verify.** Cast the Example B column to `Timestamp(Second, None)` and to `Int64` and compare the results for row 1: 1 and 1000.

### Task 5: Boundary evidence

Test null decimal/timestamp values and a schema mismatch.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, ArrayRef, Decimal128Array, TimestampMillisecondArray};
    use arrow::datatypes::{DataType, Field, Schema, TimeUnit};
    use arrow::record_batch::RecordBatch;
    use std::sync::Arc;
    let prices =
        Decimal128Array::from(vec![Some(125_i128), None]).with_precision_and_scale(10, 2)?;
    let times = TimestampMillisecondArray::from(vec![None, Some(1000_i64)]).with_timezone("UTC");
    assert_eq!((prices.null_count(), times.null_count()), (1, 1));
    assert!(prices.is_null(1) && times.is_null(0));
    let schema = Arc::new(Schema::new(vec![
        Field::new("price", DataType::Decimal128(10, 2), true),
        Field::new(
            "measured_at",
            DataType::Timestamp(TimeUnit::Millisecond, Some("UTC".into())),
            true,
        ),
    ]));
    let good: Vec<ArrayRef> = vec![Arc::new(prices.clone()), Arc::new(times.clone())];
    assert_eq!(RecordBatch::try_new(schema.clone(), good)?.num_rows(), 2);
    let wrong_scale: Vec<ArrayRef> = vec![
        Arc::new(prices.with_precision_and_scale(10, 3)?),
        Arc::new(times),
    ];
    assert!(RecordBatch::try_new(schema, wrong_scale).is_err());
    Ok(())
}
```

**Observe:** Each column holds one null, the matching batch builds with two rows, and the same coefficients relabeled with scale 3 are rejected by the schema.

Nulls in decimal and timestamp columns are validity, exactly as in integer columns; they are not zero amounts or the epoch. The schema check compares full data types, so a different scale is a type mismatch even though the stored integers are identical.

**Plausible wrong approach.** Filling the null price with 0 and the null time with 0 invents a free item measured at 1970-01-01.

**How to verify.** Run the block. Print the mismatch error; it names Decimal128(10, 2) as expected and Decimal128(10, 3) as found.

### Task 6: Transfer and justify

Plan a separately prepared Rust-to-PyArrow IPC round trip that checks schema, nulls, decimal scale and timestamp units in both languages.

**Judging criteria.** A strong plan prepares a separate Cargo project and a Python environment with a pinned `pyarrow`, writes an IPC stream from Rust with a nullable column, a `Decimal128(10, 2)` column and a millisecond UTC timestamp column, and reads it in Python. Both sides assert the same schema, the same null positions, the decimal value 1.25 rather than 125, and the timestamp unit and zone; Python then writes the batch back for Rust to check again. State one limitation: converting to pandas applies its own rules, so checks must run on Arrow objects.

## Mechanism and diagnostic reasoning

Cross-language interoperability succeeds when logical meaning agrees, not merely when bytes can be transferred. Decimal scale identifies how an integer coefficient maps to a decimal quantity. Timestamp units identify the precision of an epoch-based value, and time-zone metadata affects interpretation. A millisecond value read as seconds can be wildly wrong while remaining a valid integer.

Arrow metadata can record application meaning such as units, but consumers must agree to interpret it. IPC provides a portable transport; the C Data Interface provides an in-process ownership boundary and requires separate FFI preparation. The default pad does not enable every FFI feature or install PyArrow, Parquet or DataFusion. Keep these ecosystem boundaries explicit.

Decimal128Array::with_precision_and_scale sets decimal interpretation. TimestampMillisecondArray carries a specific unit and can attach timezone metadata. data_type exposes the logical contract independently of physical integer access.

An integer cast is not a timestamp-unit conversion. Time-zone metadata is not a complete application scheduling policy. C Data Interface release callbacks and lifetime ownership require a reviewed FFI implementation.

## Review before continuing

Rebuild Example B (Keep timestamp units explicit) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
