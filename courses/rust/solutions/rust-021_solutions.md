# rust-021: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-021_solution.rs](rust-021_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe mutable capture:** The scope makes the exclusive captured access visible. The closure updates its borrowed accumulator before the borrow ends.

**Move owned data into a closure:** Returning the owned capture makes this closure consuming rather than indefinitely repeatable. The closure transfers its captured String to the caller once.

## Task answers

### Task 1: Predict and explain

Identify capture mode and calling capability in each example.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The scope makes the exclusive captured access visible. The closure updates its borrowed accumulator before the borrow ends.

### Task 2: Guided modification

Write a pure repeatable closure capturing an immutable factor.

No separate reference answer has been written for this task. Start from Example B: Returning the owned capture makes this closure consuming rather than indefinitely repeatable. The closure transfers its captured String to the caller once.

### Task 3: Independent construction

Implement a helper accepting FnMut for repeated transformations.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn apply_times(times: usize, mut step: impl FnMut()) {
        for _ in 0..times {
            step();
        }
    }
    let mut value = 1;
    apply_times(3, || value *= 2);
    assert_eq!(value, 8);
    Ok(())
}
```

**Observe:** Doubling three times turns 1 into 8.

FnMut allows the closure to mutate its captured value on each call, which Fn would forbid.

### Task 4: Diagnose a defect

Diagnose attempting to call a consuming closure twice.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Move does not imply deep copy. A moved reference still has a borrowed lifetime. Avoid adding static bounds when the real solution is scoped execution or owned data.

### Task 5: Boundary evidence

Test a closure with no captures and one capturing a borrowed reference.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Observe mutable capture) and Example B (Move owned data into a closure).

### Task 6: Transfer and justify

Choose capture ownership for work that will run on another thread.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Capture**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A closure captures surrounding values according to what its body needs. It may borrow, mutate captured state or take ownership. Fn, FnMut and FnOnce describe calling capabilities: shared repeatable calls, mutable repeatable calls and at least one consuming call respectively. These traits form a relationship, not three arbitrary spellings to try until compilation succeeds.

A move closure takes ownership of captured values, useful when work outlives the creating scope. Moving a reference still moves only that reference and does not make its borrowed target live forever. Choose capture and call contracts from the intended lifetime and mutation behavior.

`|value| value * factor` declares a closure. `move || ...` transfers captures into it. A closure mutating a captured accumulator needs mutable calling access. A function accepting FnOnce can invoke consuming behavior once.

Move does not imply deep copy. A moved reference still has a borrowed lifetime. Avoid adding static bounds when the real solution is scoped execution or owned data.

## Review before continuing

Run the reference and confirm that it prints `rust-021: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
