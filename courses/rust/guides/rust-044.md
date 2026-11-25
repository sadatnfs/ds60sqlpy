# rust-044: Cross-language data contracts: decimals, timestamps and metadata

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-043`

## Learning objectives

Record units, decimal scale and timestamp precision in Arrow schemas for other languages. The central exercise is task 3: Create a schema documenting measurement units and timestamp precision.

## Purpose and mental model

Cross-language interoperability succeeds when logical meaning agrees, not merely when bytes can be transferred. Decimal scale identifies how an integer coefficient maps to a decimal quantity. Timestamp units identify the precision of an epoch-based value, and time-zone metadata affects interpretation. A millisecond value read as seconds can be wildly wrong while remaining a valid integer.

Arrow metadata can record application meaning such as units, but consumers must agree to interpret it. IPC provides a portable transport; the C Data Interface provides an in-process ownership boundary and requires separate FFI preparation. The default pad does not enable every FFI feature or install PyArrow, Parquet or DataFusion. Keep these ecosystem boundaries explicit.

## Vocabulary and concepts

**Decimal scale:** The number of fractional decimal places represented by an integer coefficient.

**Timestamp unit:** The time increment represented by one stored integer unit.

**Interchange contract:** Agreement about types, nulls, units, ownership and framing across consumers.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array` and `arrow::datatypes`. A passing run prints `rust-044: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Decimal128Array::with_precision_and_scale sets decimal interpretation. TimestampMillisecondArray carries a specific unit and can attach timezone metadata. data_type exposes the logical contract independently of physical integer access.

**Reading Example A (Preserve decimal interpretation, code below).** `Decimal128Array::from(vec![125_i128, 250])` stores raw 128-bit integers, the coefficients. On its own the array has Arrow's default decimal type, so `with_precision_and_scale(10, 2)` attaches the contract: up to 10 significant decimal digits, 2 of them after the decimal point. It returns a `Result` because a precision or scale outside Decimal128's limits is rejected, and `?` propagates that error. `value(0)` returns the stored `i128` coefficient, not a decimal number; interpreting it requires the scale from the data type. `data_type()` returns a `&DataType`, which is why the expected value is borrowed. `DataType::Decimal128(10, 2)` is the enum variant that carries precision and scale together.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Preserve decimal interpretation

The raw coefficient alone does not state the decimal amount.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Decimal128Array};
        use arrow::datatypes::DataType;
        let prices = Decimal128Array::from(vec![125_i128, 250]).with_precision_and_scale(10, 2)?;
        assert_eq!(prices.value(0), 125);
        assert_eq!(prices.data_type(), &DataType::Decimal128(10, 2));
    }
    println!("rust-044: passed");
    Ok(())
}
```

**Observe:** Coefficient 125 with scale two represents 1.25 under the declared contract.

### Example B: Keep timestamp units explicit

The logical type prevents a consumer from legitimately treating the same coefficient as seconds without conversion.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, TimestampMillisecondArray};
        use arrow::datatypes::{DataType, TimeUnit};
        let times = TimestampMillisecondArray::from(vec![0_i64, 1000]).with_timezone("UTC");
        assert_eq!(times.value(1), 1000);
        assert_eq!(times.data_type(), &DataType::Timestamp(TimeUnit::Millisecond, Some("UTC".into())));
    }
    println!("rust-044: passed");
    Ok(())
}
```

**Observe:** The second value is one thousand milliseconds after the epoch.

## Exercises

1. **Predict and explain.** Explain coefficient, scale and represented amount separately.

2. **Guided modification.** Add a negative decimal coefficient and retain its scale.

3. **Independent construction.** Create a schema documenting measurement units and timestamp precision.

4. **Diagnose a defect.** Diagnose reading milliseconds as seconds or losing decimal scale.

5. **Boundary evidence.** Test null decimal/timestamp values and a schema mismatch.

6. **Transfer and justify.** Plan a separately prepared Rust-to-PyArrow IPC round trip that checks schema, nulls, decimal scale and timestamp units in both languages.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

An integer cast is not a timestamp-unit conversion. Time-zone metadata is not a complete application scheduling policy. C Data Interface release callbacks and lifetime ownership require a reviewed FFI implementation.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Preserve decimal interpretation) before changing anything, and confirm its observation: Coefficient 125 with scale two represents 1.25 under the declared contract.
2. Compare Example B (Keep timestamp units explicit) with Example A and name the first line whose behavior differs. Its observation is: The second value is one thousand milliseconds after the epoch.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An integer cast is not a timestamp-unit conversion.

Tempting approaches to rule out before you compare:

- **Task 1.** Reading `prices.value(0)` as the price gives 125, a hundred times too large, because it returns the coefficient.
- **Task 2.** Storing -3.75 as `-375` in a column with scale 3 means -0.375; a value's coefficient is only correct under its column's scale.
- **Task 5.** Filling the null price with 0 and the null time with 0 invents a free item measured at 1970-01-01.

## Self-check and next step

What value does coefficient 125 represent in a `Decimal128(10, 2)` column, and what would a receiver that assumed scale 3 report? Why is Example B's second timestamp 1000 in a millisecond column, and what would the same integer mean in seconds? Which parts of this contract must travel in the schema rather than in prose?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the Arrow C data interface specification](https://arrow.apache.org/docs/format/CDataInterface.html) for how decimal scale and timestamp units cross languages.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-044: Cross-language data contracts: decimals, timestamps and metadata.
Read courses/rust/guides/rust-044.md and courses/rust/lessons/rust-044.rs. Prerequisites: rust-043.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-044_solution.rs and
courses/rust/solutions/rust-044_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
