# rust-003: Integer range, checked arithmetic and numerical intent

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-002`

## Learning objectives

Choose checked, wrapping or saturating integer arithmetic on purpose and handle overflow explicitly. The central exercise is task 3: Write a checked quantity-total calculation returning an explicit failure.

## Purpose and mental model

Fixed-width integers have finite ranges. Rust provides explicit checked, wrapping, saturating and overflowing arithmetic so an API can state what happens at a boundary. Do not rely on differences between debug and optimized overflow settings for business correctness. Choose the intended policy directly.

Floating-point arithmetic approximates many decimal fractions. A tolerance should reflect scale and numerical error, not hide a unit mismatch. Money often needs an integer smallest-unit representation or a separately prepared decimal library with a documented rounding policy. The standard library does not make every numerical domain exact automatically.

## Vocabulary and concepts

**Overflow:** A mathematical result outside the representation range.

**Checked arithmetic:** Arithmetic reporting an unrepresentable result explicitly.

**Saturation:** Clamping an overflowing result to a type boundary.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-003: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`checked_add` returns Option and reports overflow as None. `wrapping_add` performs modular arithmetic. `saturating_add` stays at the limit. An explicit integer type makes the tested range unambiguous.

**Reading Example A (Choose a visible overflow policy, code below).** `255_u8` is an integer literal with a type suffix: the underscore is only a visual separator, and `u8` fixes the type as an unsigned 8-bit integer whose range is 0 to 255. Each of the first three lines therefore asks what 255 plus 1 should mean when the true sum, 256, needs a ninth bit. The three methods are inherent methods on every integer type, and each name states a policy: `checked_` reports failure through `Option`, `wrapping_` keeps the low eight bits, and `saturating_` clamps at the nearest limit. `assert_eq!` compares each result with an expected value of the same type, so `None` on line 1 is an `Option<u8>` and the bare `0` and `255` are `u8` values. Line 4 is an in-range control: `2_u8.checked_add(3)` cannot overflow, so it shows what a successful checked result looks like, wrapped in `Some`. Without that control, the checks could not tell a working `checked_add` from one that always returned `None`.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Choose a visible overflow policy

The choice is semantic and should not depend on a compiler optimization setting.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(255_u8.checked_add(1), None);
        assert_eq!(255_u8.wrapping_add(1), 0);
        assert_eq!(255_u8.saturating_add(1), 255);
        assert_eq!(2_u8.checked_add(3), Some(5));
    }
    println!("rust-003: passed");
    Ok(())
}
```

**Observe:** The same boundary produces absence, zero or 255 under three distinct policies.

### Example B: Keep numeric units explicit

Integer smallest units avoid accidental decimal approximation in this bounded pricing example.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let cents_per_item: u64 = 125;
        let quantity: u64 = 3;
        assert_eq!(cents_per_item.checked_mul(quantity), Some(375));
        let approximate = 0.1_f64 + 0.2;
        assert!((approximate - 0.3).abs() < 1e-12);
    }
    println!("rust-003: passed");
    Ok(())
}
```

**Observe:** Three items cost 375 cents, while the floating fixture uses an explicit tolerance.

## Exercises

1. **Predict and explain.** Predict the three overflow policies.

2. **Guided modification.** Repeat the investigation with subtraction at zero.

3. **Independent construction.** Write a checked quantity-total calculation returning an explicit failure.

4. **Diagnose a defect.** Diagnose relying on debug-mode overflow behavior in production logic.

5. **Boundary evidence.** Test zero, maximum and one beyond an accepted application range.

6. **Transfer and justify.** Choose numeric representation, units and rounding rules for a pricing contract.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Wrapping is usually wrong for counts even when it avoids a panic. A tolerance does not repair unit conversion errors. Converting with as can truncate or reinterpret values; use checked conversion when range matters.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Choose a visible overflow policy) before changing anything, and confirm its observation: The same boundary produces absence, zero or 255 under three distinct policies.
2. Compare Example B (Keep numeric units explicit) with Example A and name the first line whose behavior differs. Its observation is: Three items cost 375 cents, while the floating fixture uses an explicit tolerance.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Wrapping is usually wrong for counts even when it avoids a panic.

Tempting approaches to rule out before you compare:

- **Task 1.** Predicting that `wrapping_add` gives 256 or panics forgets that its whole purpose is to keep the result inside `u8`. Predicting `Some(255)` for `checked_add` confuses it with saturation.
- **Task 2.** Using `saturating_sub` for the stock calculation reports 0 remaining after an order of 3 against a stock of 2, quietly hiding the one unit that could not be supplied.
- **Task 5.** Writing the guard as `quantity < 1_000` rejects the documented maximum 1000; only the boundary fixture catches it, since every middle value behaves the same under both guards.

## Self-check and next step

What do `255u8.checked_add(1)`, `255u8.wrapping_add(1)` and `255u8.saturating_add(1)` return? Why can the plain `255u8 + 1` panic in one build profile and wrap in another? Why is 375 stored as integer cents a safer total than 3.75 dollars in an `f64`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `u8` primitive documentation](https://doc.rust-lang.org/std/primitive.u8.html) for the `checked_`, `wrapping_` and `saturating_` method families.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-003: Integer range, checked arithmetic and numerical intent.
Read courses/rust/guides/rust-003.md and courses/rust/lessons/rust-003.rs. Prerequisites: rust-002.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-003_solution.rs and
courses/rust/solutions/rust-003_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
