# rust-024: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-024_solution.rs](rust-024_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use independent expected cases:** Literal expectations make the test independent of the implementation expression. Negative, zero and positive cases satisfy the stated clamp rule.

**Reject a plausible wrong boundary:** The property alone would not necessarily distinguish every wrong constant implementation. Zero rejects the incorrect default while idempotence adds a second property.

## Task answers

### Task 1: Predict and explain

Name a wrong implementation each case catches.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Literal expectations make the test independent of the implementation expression. Negative, zero and positive cases satisfy the stated clamp rule.

### Task 2: Guided modification

Add an extreme integer input without negating its minimum value.

No separate reference answer has been written for this task. Start from Example B: The property alone would not necessarily distinguish every wrong constant implementation. Zero rejects the incorrect default while idempotence adds a second property.

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

### Task 4: Diagnose a defect

Diagnose an assertion comparing a function call with itself.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A disabled debug_assert is not a release invariant. Random cases require reproducibility and an oracle. A test that catches and ignores its own failure is misleading.

### Task 5: Boundary evidence

Test idempotence alongside independent boundary expectations.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Use independent expected cases) and Example B (Reject a plausible wrong boundary).

### Task 6: Transfer and justify

Separate unit, integration, compile-fail and runtime evidence for a library change.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Test oracle**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A test is strong when a plausible wrong implementation fails it. Derive expected results from the contract rather than copying the same formula into the assertion. Normal, boundary and invalid cases expose different assumptions. Properties such as idempotence can cover a wider relationship but do not replace concrete expected values.

Rust's built-in test harness runs functions marked test when compiling a test target. The classroom ordinary reference instead invokes always-active assertions through main. This keeps code execution distinct from a Cargo test workflow. A clean unit test does not prove filesystem configuration, network availability or deployment correctness.

assert and assert_eq remain active in ordinary builds, unlike debug_assert. A cfg(test) module belongs to a test compilation. Cargo test discovers unit, integration and documentation tests under their own contracts.

A disabled debug_assert is not a release invariant. Random cases require reproducibility and an oracle. A test that catches and ignores its own failure is misleading.

## Review before continuing

Run the reference and confirm that it prints `rust-024: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
