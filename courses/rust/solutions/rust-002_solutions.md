# rust-002: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-002_solution.rs](rust-002_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Expose an accumulator:** Only the value requiring state transitions is declared mutable. The mutable total changes while the fixed input remains 4.

**Shadow after a representation change:** Shadowing can change type, but names must still explain whether a value is text, length or parsed quantity. The new count is the text length, not the number twelve.

## Task answers

### Task 1: Predict and explain

Identify the static type and mutability of each binding.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Only the value requiring state transitions is declared mutable. The mutable total changes while the fixed input remains 4.

### Task 2: Guided modification

Remove unnecessary mut declarations in a small program.

No separate reference answer has been written for this task. Start from Example B: Shadowing can change type, but names must still explain whether a value is text, length or parsed quantity. The new count is the text length, not the number twelve.

### Task 3: Independent construction

Write a running total with fixed input and mutable accumulator.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let deliveries = [3, 5, 2];
    let mut total = 0;
    for amount in deliveries {
        total += amount;
    }
    assert_eq!(total, 10);
    assert_eq!(deliveries, [3, 5, 2]);
    Ok(())
}
```

**Observe:** The running total ends at 10 and the input array is unchanged.

Only the accumulator is declared mut; the fixed input stays immutable, so the compiler rejects any accidental edit to it.

### Task 4: Diagnose a defect

Diagnose assigning a String to a mutable integer binding.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Immutable does not mean every object reachable through a type is deeply frozen. Shadowing can conceal a units change. Type inference is not dynamic typing.

### Task 5: Boundary evidence

Test an empty input string and a zero accumulator.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Expose an accumulator) and Example B (Shadow after a representation change).

### Task 6: Transfer and justify

Choose shadowing or distinct names for parsing stages and justify readability.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Binding**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Rust bindings are immutable by default. `mut` grants permission to change a binding's value. Immutability reduces the number of state transitions a reader must consider, but it is not a substitute for understanding ownership and interior mutability introduced later. Prefer a new derived value when that expresses the operation clearly.

Type inference remains static: the compiler determines a concrete type from context. Shadowing introduces a new binding with the same name and can deliberately change its type. Reassignment instead changes the value of an existing mutable binding and must preserve its type. Use either technique to expose meaning rather than obscure where a value came from.

`let count: i32 = 3` annotates a type. `let mut total = 0` allows reassignment. `let text = text.len()` shadows the earlier name with a new binding. Integer suffixes such as `3_u64` constrain inference.

Immutable does not mean every object reachable through a type is deeply frozen. Shadowing can conceal a units change. Type inference is not dynamic typing.

## Review before continuing

Run the reference and confirm that it prints `rust-002: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
