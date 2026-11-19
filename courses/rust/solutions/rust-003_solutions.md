# rust-003: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-003_solution.rs](rust-003_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Choose a visible overflow policy:** The choice is semantic and should not depend on a compiler optimization setting. The same boundary produces absence, zero or 255 under three distinct policies.

**Keep numeric units explicit:** Integer smallest units avoid accidental decimal approximation in this bounded pricing example. Three items cost 375 cents, while the floating fixture uses an explicit tolerance.

## Task answers

### Task 1: Predict and explain

Predict the three overflow policies.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The choice is semantic and should not depend on a compiler optimization setting. The same boundary produces absence, zero or 255 under three distinct policies.

### Task 2: Guided modification

Repeat the investigation with subtraction at zero.

No separate reference answer has been written for this task. Start from Example B: Integer smallest units avoid accidental decimal approximation in this bounded pricing example. Three items cost 375 cents, while the floating fixture uses an explicit tolerance.

### Task 3: Independent construction

Write a checked quantity-total calculation returning an explicit failure.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn total_cents(price: u64, quantity: u64) -> Result<u64, String> {
        price
            .checked_mul(quantity)
            .ok_or_else(|| String::from("total overflows u64"))
    }
    assert_eq!(total_cents(125, 3), Ok(375));
    assert!(total_cents(u64::MAX, 2).is_err());
    Ok(())
}
```

**Observe:** 125 cents times 3 is Ok(375); u64::MAX times 2 is an explicit Err.

checked_mul returns None on overflow, and ok_or_else turns that into a named failure instead of a wrapped or saturated total.

### Task 4: Diagnose a defect

Diagnose relying on debug-mode overflow behavior in production logic.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Wrapping is usually wrong for counts even when it avoids a panic. A tolerance does not repair unit conversion errors. Converting with as can truncate or reinterpret values; use checked conversion when range matters.

### Task 5: Boundary evidence

Test zero, maximum and one beyond an accepted application range.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Choose a visible overflow policy) and Example B (Keep numeric units explicit).

### Task 6: Transfer and justify

Choose numeric representation, units and rounding rules for a pricing contract.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Overflow**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Fixed-width integers have finite ranges. Rust provides explicit checked, wrapping, saturating and overflowing arithmetic so an API can state what happens at a boundary. Do not rely on differences between debug and optimized overflow settings for business correctness. Choose the intended policy directly.

Floating-point arithmetic approximates many decimal fractions. A tolerance should reflect scale and numerical error, not hide a unit mismatch. Money often needs an integer smallest-unit representation or a separately prepared decimal library with a documented rounding policy. The standard library does not make every numerical domain exact automatically.

`checked_add` returns Option and reports overflow as None. `wrapping_add` performs modular arithmetic. `saturating_add` stays at the limit. An explicit integer type makes the tested range unambiguous.

Wrapping is usually wrong for counts even when it avoids a panic. A tolerance does not repair unit conversion errors. Converting with as can truncate or reinterpret values; use checked conversion when range matters.

## Review before continuing

Run the reference and confirm that it prints `rust-003: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
