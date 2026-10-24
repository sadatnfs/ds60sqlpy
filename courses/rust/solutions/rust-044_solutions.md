# rust-044: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-044_solution.rs](rust-044_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve decimal interpretation:** The raw coefficient alone does not state the decimal amount. Coefficient 125 with scale two represents 1.25 under the declared contract.

**Keep timestamp units explicit:** The logical type prevents a consumer from legitimately treating the same coefficient as seconds without conversion. The second value is one thousand milliseconds after the epoch.

## Reason through the six tasks

1. **Predict and explain.** Explain coefficient, scale and represented amount separately.

2. **Guided modification.** Add a negative decimal coefficient and retain its scale.

3. **Independent construction.** Create a schema documenting measurement units and timestamp precision.

4. **Diagnose a defect.** Diagnose reading milliseconds as seconds or losing decimal scale.

5. **Boundary evidence.** Test null decimal/timestamp values and a schema mismatch.

6. **Transfer and justify.** Plan a separately prepared Rust-to-PyArrow IPC round trip that checks schema, nulls, decimal scale and timestamp units in both languages.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Cross-language interoperability succeeds when logical meaning agrees, not merely when bytes can be transferred. Decimal scale identifies how an integer coefficient maps to a decimal quantity. Timestamp units identify the precision of an epoch-based value, and time-zone metadata affects interpretation. A millisecond value read as seconds can be wildly wrong while remaining a valid integer.

Arrow metadata can record application meaning such as units, but consumers must agree to interpret it. IPC provides a portable transport; the C Data Interface provides an in-process ownership boundary and requires separate FFI preparation. The default pad does not enable every FFI feature or install PyArrow, Parquet or DataFusion. Keep these ecosystem boundaries explicit.

Decimal128Array::with_precision_and_scale sets decimal interpretation. TimestampMillisecondArray carries a specific unit and can attach timezone metadata. data_type exposes the logical contract independently of physical integer access.

An integer cast is not a timestamp-unit conversion. Time-zone metadata is not a complete application scheduling policy. C Data Interface release callbacks and lifetime ownership require a reviewed FFI implementation.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
