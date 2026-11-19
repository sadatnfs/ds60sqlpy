# rust-044: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-044_solution.rs](rust-044_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve decimal interpretation:** The raw coefficient alone does not state the decimal amount. Coefficient 125 with scale two represents 1.25 under the declared contract.

**Keep timestamp units explicit:** The logical type prevents a consumer from legitimately treating the same coefficient as seconds without conversion. The second value is one thousand milliseconds after the epoch.

## Task answers

### Task 1: Predict and explain

Explain coefficient, scale and represented amount separately.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The raw coefficient alone does not state the decimal amount. Coefficient 125 with scale two represents 1.25 under the declared contract.

### Task 2: Guided modification

Add a negative decimal coefficient and retain its scale.

No separate reference answer has been written for this task. Start from Example B: The logical type prevents a consumer from legitimately treating the same coefficient as seconds without conversion. The second value is one thousand milliseconds after the epoch.

### Task 3: Independent construction

Create a schema documenting measurement units and timestamp precision.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An integer cast is not a timestamp-unit conversion. Time-zone metadata is not a complete application scheduling policy. C Data Interface release callbacks and lifetime ownership require a reviewed FFI implementation.

### Task 5: Boundary evidence

Test null decimal/timestamp values and a schema mismatch.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Preserve decimal interpretation) and Example B (Keep timestamp units explicit).

### Task 6: Transfer and justify

Plan a separately prepared Rust-to-PyArrow IPC round trip that checks schema, nulls, decimal scale and timestamp units in both languages.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Decimal scale**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Cross-language interoperability succeeds when logical meaning agrees, not merely when bytes can be transferred. Decimal scale identifies how an integer coefficient maps to a decimal quantity. Timestamp units identify the precision of an epoch-based value, and time-zone metadata affects interpretation. A millisecond value read as seconds can be wildly wrong while remaining a valid integer.

Arrow metadata can record application meaning such as units, but consumers must agree to interpret it. IPC provides a portable transport; the C Data Interface provides an in-process ownership boundary and requires separate FFI preparation. The default pad does not enable every FFI feature or install PyArrow, Parquet or DataFusion. Keep these ecosystem boundaries explicit.

Decimal128Array::with_precision_and_scale sets decimal interpretation. TimestampMillisecondArray carries a specific unit and can attach timezone metadata. data_type exposes the logical contract independently of physical integer access.

An integer cast is not a timestamp-unit conversion. Time-zone metadata is not a complete application scheduling policy. C Data Interface release callbacks and lifetime ownership require a reviewed FFI implementation.

## Review before continuing

Run the reference and confirm that it prints `rust-044: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
