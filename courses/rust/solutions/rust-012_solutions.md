# rust-012: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-012_solution.rs](rust-012_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reserve within an invariant:** The method owns both the affordability check and the subtraction. A successful reservation leaves three units.

**Reject without partial mutation:** Validation occurs before changing state, preserving the prior valid value. Excess demand is rejected and zero is an allowed no-op.

## Task answers

### Task 1: Predict and explain

Explain the capability expressed by each method receiver.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The method owns both the affordability check and the subtraction. A successful reservation leaves three units.

### Task 2: Guided modification

Add a checked restock method.

No separate reference answer has been written for this task. Start from Example B: Validation occurs before changing state, preserving the prior valid value. Excess demand is rejected and zero is an allowed no-op.

### Task 3: Independent construction

Create a bounded counter with private state and validated operations.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    struct Counter {
        value: u32,
        limit: u32,
    }
    impl Counter {
        fn new(limit: u32) -> Self {
            Self { value: 0, limit }
        }
        fn increment(&mut self) -> bool {
            if self.value == self.limit {
                return false;
            }
            self.value += 1;
            true
        }
    }
    let mut counter = Counter::new(2);
    assert!(counter.increment() && counter.increment());
    assert!(!counter.increment());
    assert_eq!(counter.value, 2);
    Ok(())
}
```

**Observe:** Two increments succeed, the third is refused, and the value stays at the limit 2.

The fields are private to the defining module, so callers can change the counter only through increment, which checks the limit first.

### Task 4: Diagnose a defect

Diagnose subtracting before checking available stock.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Public writable fields can bypass invariants. Unsigned types prevent negative representation but do not prevent overflow. A method taking &mut self is not automatically safe for unsynchronized sharing across threads.

### Task 5: Boundary evidence

Test zero, exact-stock and excess reservations.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Reserve within an invariant) and Example B (Reject without partial mutation).

### Task 6: Transfer and justify

Choose a consuming method when an operation should make the prior state unavailable.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Struct**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A struct groups named fields into a domain value. Methods express operations on that value, and their receiver states whether they borrow, mutate or consume it. A constructor function can validate inputs before creating a valid instance. Private fields prevent callers from bypassing that constructor or later invariants.

Failure atomicity means a rejected operation leaves the prior valid state unchanged. Check all rejection conditions before mutation or build a candidate value and commit it only after validation. Encapsulation is useful because it keeps this reasoning in one place rather than requiring every caller to remember the rule.

`impl Inventory` contains associated functions and methods. `&self` reads, `&mut self` mutates, and `self` consumes. An associated constructor such as new can return Option or Result.

Public writable fields can bypass invariants. Unsigned types prevent negative representation but do not prevent overflow. A method taking &mut self is not automatically safe for unsynchronized sharing across threads.

## Review before continuing

Run the reference and confirm that it prints `rust-012: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
