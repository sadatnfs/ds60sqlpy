# rust-044: Cross-language data contracts: decimals, timestamps and metadata

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-043`

## Learning objectives

Create a schema documenting measurement units and timestamp precision. Then plan a separately prepared Rust-to-PyArrow IPC round trip that checks schema, nulls, decimal scale and timestamp units in both languages.

## Purpose and mental model

Cross-language interoperability succeeds when logical meaning agrees, not merely when bytes can be transferred. Decimal scale identifies how an integer coefficient maps to a decimal quantity. Timestamp units identify the precision of an epoch-based value, and time-zone metadata affects interpretation. A millisecond value read as seconds can be wildly wrong while remaining a valid integer.

Arrow metadata can record application meaning such as units, but consumers must agree to interpret it. IPC provides a portable transport; the C Data Interface provides an in-process ownership boundary and requires separate FFI preparation. The default pad does not enable every FFI feature or install PyArrow, Parquet or DataFusion. Keep these ecosystem boundaries explicit.

## Vocabulary and concepts

**Decimal scale:** The number of fractional decimal places represented by an integer coefficient.

**Timestamp unit:** The time increment represented by one stored integer unit.

**Interchange contract:** Agreement about types, nulls, units, ownership and framing across consumers.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Decimal128Array::with_precision_and_scale sets decimal interpretation. TimestampMillisecondArray carries a specific unit and can attach timezone metadata. data_type exposes the logical contract independently of physical integer access.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An integer cast is not a timestamp-unit conversion. Time-zone metadata is not a complete application scheduling policy. C Data Interface release callbacks and lifetime ownership require a reviewed FFI implementation.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Decimal scale, Timestamp unit, Interchange contract without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://arrow.apache.org/docs/format/CDataInterface.html). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
