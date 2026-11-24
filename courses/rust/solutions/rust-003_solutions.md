# rust-003: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-003_solution.rs](rust-003_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Choose a visible overflow policy:** The choice is semantic and should not depend on a compiler optimization setting. The same boundary produces absence, zero or 255 under three distinct policies.

**Keep numeric units explicit:** Integer smallest units avoid accidental decimal approximation in this bounded pricing example. Three items cost 375 cents, while the floating fixture uses an explicit tolerance.

## Task answers

### Task 1: Predict and explain

Predict the three overflow policies.

**Written answer.** For `255_u8` plus 1: `checked_add` returns `None`, `wrapping_add` returns 0 and `saturating_add` returns 255. The in-range control `2_u8.checked_add(3)` returns `Some(5)`, so `checked_add` is not simply refusing everything.

**Why it is correct.** 255 is `u8::MAX`, so the true sum 256 needs a ninth bit. Checked arithmetic reports that the result does not fit, wrapping keeps the low eight bits of 256 (which are all zero), and saturating clamps to the largest representable value.

**Plausible wrong approach.** Predicting that `wrapping_add` gives 256 or panics forgets that its whole purpose is to keep the result inside `u8`. Predicting `Some(255)` for `checked_add` confuses it with saturation.

**How to verify.** The first three assertions of Example A encode exactly these predictions. Change the expected wrapping result to 255 and the run panics with `left: 0` and `right: 255` before any marker prints.

### Task 2: Guided modification

Repeat the investigation with subtraction at zero.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    assert_eq!(0_u8.checked_sub(1), None);
    assert_eq!(0_u8.wrapping_sub(1), 255);
    assert_eq!(0_u8.saturating_sub(1), 0);
    assert_eq!(5_u8.checked_sub(3), Some(2));
    let stock: u32 = 2;
    let ordered: u32 = 3;
    assert_eq!(stock.checked_sub(ordered), None);
    Ok(())
}
```

**Observe:** At zero, checked subtraction gives None, wrapping gives 255 and saturating stays at 0; 5 minus 3 is Some(2), and 2 units of stock minus an order of 3 is None.

Below zero mirrors the overflow case at the top: wrapping jumps to `u8::MAX`, saturation clamps at the lower bound 0, and only `checked_sub` makes the impossible stock level visible as `None` instead of a plausible count.

**Plausible wrong approach.** Using `saturating_sub` for the stock calculation reports 0 remaining after an order of 3 against a stock of 2, quietly hiding the one unit that could not be supplied.

**How to verify.** Every assertion passes and `rust-003: passed` prints. Replace the stock check's call with `Some(stock.wrapping_sub(ordered))` and it fails with `left: Some(4294967295)`, a huge u32 instead of a refusal.

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

**Written answer.** The defect is `let total = price * quantity;` for `u64` money values. A debug build panics with `attempt to multiply with overflow`, but a release build compiles with overflow checks off and silently wraps, so production gets a small wrong total. Replace it with `price.checked_mul(quantity)` and handle `None` explicitly, as task 3 does.

**Why it is correct.** Overflow checks are a build-profile setting, not part of the program's meaning. Only the explicit `checked_*`, `wrapping_*` or `saturating_*` methods state a policy that holds in every profile.

**Plausible wrong approach.** Adding `#[cfg(debug_assertions)]` tests that expect the panic proves only debug behavior; the release binary still wraps. Switching to `u128` delays the overflow without stating what should happen when it occurs.

**How to verify.** Compare `std::hint::black_box(u64::MAX).wrapping_mul(2)`, which is `u64::MAX - 1`, with `checked_mul` returning `None`. The pad compiles in debug mode, so the plain `*` version would panic there instead of producing the release value.

### Task 5: Boundary evidence

Test zero, maximum and one beyond an accepted application range.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn accept_quantity(quantity: u32) -> Result<u32, String> {
        if quantity <= 1_000 {
            Ok(quantity)
        } else {
            Err(format!("quantity {quantity} exceeds 1000"))
        }
    }
    assert_eq!(accept_quantity(0), Ok(0));
    assert_eq!(accept_quantity(1_000), Ok(1_000));
    assert_eq!(
        accept_quantity(1_001),
        Err(String::from("quantity 1001 exceeds 1000"))
    );
    assert_eq!(u8::try_from(255_u32), Ok(255));
    assert!(u8::try_from(256_u32).is_err());
    assert_eq!(300_i32 as u8, 44);
    Ok(())
}
```

**Observe:** Quantities 0 and 1000 are accepted, 1001 is rejected with a message naming it; converting 255 to u8 succeeds, 256 fails, and an `as` cast turns 300 into 44.

The application range 0 to 1000 is narrower than `u32`, so it needs its own check with an inclusive upper bound. The last three lines show the same boundary for type conversion: `try_from` refuses the first value past `u8::MAX`, while `as` keeps the low byte of 300 (300 - 256 = 44).

**Plausible wrong approach.** Writing the guard as `quantity < 1_000` rejects the documented maximum 1000; only the boundary fixture catches it, since every middle value behaves the same under both guards.

**How to verify.** Run the block. Change the guard to `<` and the second assertion panics with an `Err` naming 1000, showing the off-by-one at the edge.

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
