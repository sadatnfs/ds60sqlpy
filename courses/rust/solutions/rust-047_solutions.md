# rust-047: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-047_solution.rs](rust-047_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Check a bounded algebraic property:** The range avoids overflow, making the mathematical property appropriate to this representation. All one hundred bounded pairs were checked and satisfy the addition relation.

**Check order and multiplicity separately:** Order alone would not reject a broken implementation that drops duplicates. Sorting establishes order without losing the repeated three.

## Task answers

### Task 1: Predict and explain

State the assumptions making the bounded arithmetic property valid.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The range avoids overflow, making the mathematical property appropriate to this representation. All one hundred bounded pairs were checked and satisfy the addition relation.

### Task 2: Guided modification

Add a small exhaustive test for checked quantity addition.

No separate reference answer has been written for this task. Start from Example B: Order alone would not reject a broken implementation that drops duplicates. Sorting establishes order without losing the repeated three.

### Task 3: Independent construction

Write a property checking an Arrow filter's output count against its Boolean mask.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, BooleanArray, Int32Array};
    for pattern in 0_u32..16 {
        let mask: Vec<bool> = (0..4).map(|bit| pattern & (1 << bit) != 0).collect();
        let values = Int32Array::from(vec![1, 2, 3, 4]);
        let kept = arrow::compute::filter(&values, &BooleanArray::from(mask.clone()))?;
        let expected = mask.iter().filter(|keep| **keep).count();
        assert_eq!(kept.len(), expected);
    }
    Ok(())
}
```

**Observe:** For all 16 masks over four rows, the filtered length equals the number of true entries.

Enumerating every mask of a small size checks the property exhaustively, including the all-false and all-true edge cases.

### Task 4: Diagnose a defect

Diagnose a sortedness test that never checks retained values.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A property can be too weak to distinguish incorrect implementations. Integer overflow can invalidate a mathematical law's assumed domain. Compiler message wording may change even when the underlying rule remains correct.

### Task 5: Boundary evidence

Preserve empty, duplicate and all-null regression fixtures.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Check a bounded algebraic property) and Example B (Check order and multiplicity separately).

### Task 6: Transfer and justify

Design an external fuzzing and compile-fail plan with reproducible seeds, minimized failures and clear acceptance scope.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Property test**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Advanced verification combines examples, properties and boundary-specific evidence. A property such as sorting preserving element multiplicity can expose mistakes that one expected list misses. Compile-fail tests can preserve an API's ownership or visibility restrictions, but they belong to a deliberately prepared test harness rather than an ordinary successful runtime reference.

Fuzzing and property-testing crates are valuable external tools, not hidden dependencies in this pad. Start with deterministic exhaustive enumeration over a small bounded domain and an independent oracle. Keep minimized counterexamples when a failure appears. Never weaken an invariant to accommodate a wrong implementation merely because a large suite is expensive.

Nested loops can enumerate a small input space reproducibly. A sorted clone can be compared with the original through a frequency map. Compile diagnostics should be categorized by the violated rule rather than fragile full-message text.

A property can be too weak to distinguish incorrect implementations. Integer overflow can invalidate a mathematical law's assumed domain. Compiler message wording may change even when the underlying rule remains correct.

## Review before continuing

Run the reference and confirm that it prints `rust-047: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
