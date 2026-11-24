# rust-024: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-024_solution.rs](rust-024_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use independent expected cases:** Literal expectations make the test independent of the implementation expression. Negative, zero and positive cases satisfy the stated clamp rule.

**Reject a plausible wrong boundary:** The property alone would not necessarily distinguish every wrong constant implementation. Zero rejects the incorrect default while idempotence adds a second property.

## Task answers

### Task 1: Predict and explain

Name a wrong implementation each case catches.

**Written answer.** The row `(-2, 0)` catches the identity `|value| value` (it returns -2) and `abs` (it returns 2). The row `(0, 0)` catches Example B's `if value <= 0 { 1 }` default. The row `(3, 3)` catches a constant `|_| 0`.

**Why it is correct.** Each row is a literal written from the clamp rule, not from the expression under test, so a wrong implementation fails the first row where its rule differs.

**Plausible wrong approach.** Claiming `(3, 3)` catches `abs` is wrong: `3_i32.abs()` is 3. Only the negative row separates `abs` from the clamp, so removing it would let that bug through.

**How to verify.** Replace `input.max(0)` with `input.abs()`; the loop panics on the first row with `left: 2` and `right: 0`. Restore `max(0)` and all rows pass.

### Task 2: Guided modification

Add an extreme integer input without negating its minimum value.

**Written answer.** Extend the table to `[(-2, 0), (0, 0), (3, 3), (i32::MIN, 0), (i32::MAX, i32::MAX)]`. `i32::MIN.max(0)` is 0 and `i32::MAX.max(0)` is `i32::MAX`.

**Why it is correct.** `max` only compares, so the extreme inputs are safe for the implementation, and the expected values are written as constants, so the test performs no arithmetic either.

**Plausible wrong approach.** Writing an expectation such as `-i32::MIN`, or calling `i32::MIN.abs()`, overflows because 2147483648 does not fit in an `i32`. The constant form is rejected at compile time by the deny-by-default arithmetic overflow lint, and `abs` panics with attempt to negate with overflow when checks are on.

**How to verify.** Run the five-row loop; it passes. Add `assert_eq!(i32::MIN.checked_abs(), None);` to show why the test avoids negation.

### Task 3: Independent construction

Write table-driven checks for a quantity validator.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn valid_quantity(value: i32) -> bool {
        (0..=1000).contains(&value)
    }
    let cases = [(-1, false), (0, true), (1000, true), (1001, false)];
    for (input, expected) in cases {
        assert_eq!(valid_quantity(input), expected, "input {input}");
    }
    Ok(())
}
```

**Observe:** All four rows pass, including both edges of the 0 to 1000 range.

Each row pairs an input with an independently written expectation, and the message names the failing input.

**Plausible wrong approach.** Writing the range as `(0..1000).contains(&value)` excludes 1000, because `..` is half-open. The `(1000, true)` row then panics with `left: false`, `right: true` and the message `input 1000`.

**How to verify.** Add `(500, true)` and `(i32::MIN, false)` rows. Temporarily switch to `0..1000` to watch the `input 1000` failure, then restore `0..=1000`.

### Task 4: Diagnose a defect

Diagnose an assertion comparing a function call with itself.

**Written answer.** The defect is `assert_eq!(valid_quantity(1001), valid_quantity(1001));`. Both sides run the same code, so it passes for any implementation that returns the same answer twice. The fix is a literal expectation: `assert_eq!(valid_quantity(1001), false, "input 1001");`.

**Why it is correct.** An oracle must come from outside the code under test. Comparing a call with itself only checks determinism, never whether 1001 is accepted or refused.

**Plausible wrong approach.** Computing the expectation as `(0..=1000).contains(&1001)` looks independent, but it copies the implementation's expression, so a shared off-by-one bug would pass on both sides.

**How to verify.** Break the function to `fn valid_quantity(_: i32) -> bool { true }`. The self-comparison still passes, while the literal assertion panics with `left: true`, `right: false` and `input 1001`.

### Task 5: Boundary evidence

Test idempotence alongside independent boundary expectations.

**Written answer.** Keep Example A's literal table and add a property loop: `for value in [-4, 0, 7, i32::MIN, i32::MAX] { let once = value.max(0); assert_eq!(once.max(0), once); }`.

**Why it is correct.** Idempotence says clamping twice changes nothing, which every correct clamp satisfies. The literal rows pin where the boundary is, which the property cannot do on its own.

**Plausible wrong approach.** Relying on idempotence alone passes for the identity `|value| value` and for the constant `|_| 0`, since both return the same result when applied twice. Neither is a clamp.

**How to verify.** Swap in the identity for `max(0)`: the property loop still passes, but the table fails on `(-2, 0)` with `left: -2`, `right: 0`.

### Task 6: Transfer and justify

Separate unit, integration, compile-fail and runtime evidence for a library change.

**Written answer.** For a change that makes `valid_quantity` return `Result<Quantity, QuantityError>`: unit tests in `#[cfg(test)] mod tests` cover -1, 0, 1000 and 1001. An integration test in `tests/` drives the import through the `pub` API. A `compile_fail` doctest shows code outside the module cannot build `Quantity` directly. A runtime check runs the binary on a fixture file and compares its output.

**Why it is correct.** Each layer proves something the others cannot: unit tests pin the rule, integration tests pin the public surface, the doctest pins a compile-time guarantee, and the runtime check exercises real file paths. None proves deployment configuration.

**Plausible wrong approach.** Treating a green `cargo test` as proof the binary reads the right file is wrong here: the unit and integration tests pass slices of strings and never open the configured path.

**How to verify.** Run `cargo test --lib`, `cargo test --test import` and `cargo test --doc` separately in the Cargo project, then `cargo run` on the fixture. In the pad only the assertion run applies, ending with `rust-024: passed`.

## Mechanism and diagnostic reasoning

A test is strong when a plausible wrong implementation fails it. Derive expected results from the contract rather than copying the same formula into the assertion. Normal, boundary and invalid cases expose different assumptions. Properties such as idempotence can cover a wider relationship but do not replace concrete expected values.

Rust's built-in test harness runs functions marked test when compiling a test target. The classroom ordinary reference instead invokes always-active assertions through main. This keeps code execution distinct from a Cargo test workflow. A clean unit test does not prove filesystem configuration, network availability or deployment correctness.

assert and assert_eq remain active in ordinary builds, unlike debug_assert. A cfg(test) module belongs to a test compilation. Cargo test discovers unit, integration and documentation tests under their own contracts.

A disabled debug_assert is not a release invariant. Random cases require reproducibility and an oracle. A test that catches and ignores its own failure is misleading.

## Review before continuing

Run the reference and confirm that it prints `rust-024: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
