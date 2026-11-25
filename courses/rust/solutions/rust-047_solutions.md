# rust-047: explanation and comparison

Executable reference: [rust-047_solution.rs](rust-047_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Check a bounded algebraic property:** The range avoids overflow, making the mathematical property appropriate to this representation. All one hundred bounded pairs were checked and satisfy the addition relation.

**Check order and multiplicity separately:** Order alone would not reject a broken implementation that drops duplicates. Sorting establishes order without losing the repeated three.

## Task answers

### Task 1: Predict and explain

State the assumptions making the bounded arithmetic property valid.

**Written answer.** The property `a + b == b + a` holds for mathematical integers, and Example A only checks it under assumptions that keep `i32` addition equal to that. Both values lie in 0 to 9, so every sum is at most 18 and cannot overflow `i32`. The loops enumerate all 100 pairs, so the test is exhaustive for that domain, and equality on `i32` is exact.

**Why it is correct.** Outside its stated domain the property no longer describes this code: near `i32::MAX`, `a + b` panics in debug builds, so the law depends on the range limit.

**Plausible wrong approach.** Concluding that addition is commutative for every `i32` from this test generalizes past the domain it enumerated.

**How to verify.** Change the ranges to include `i32::MAX` and run in a debug build: the first overflowing pair panics with attempt to add with overflow.

### Task 2: Guided modification

Add a small exhaustive test for checked quantity addition.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut checked = 0;
    for a in 0_u8..=u8::MAX {
        for b in 0_u8..=u8::MAX {
            let wide = u16::from(a) + u16::from(b);
            let expected = u8::try_from(wide).ok();
            assert_eq!(a.checked_add(b), expected);
            checked += 1;
        }
    }
    assert_eq!(checked, 65_536);
    Ok(())
}
```

**Observe:** All 65,536 pairs of u8 quantities agree with a wider oracle: checked_add returns the sum when it fits and None when it does not.

The `u8` domain is small enough to enumerate completely, and the oracle adds in `u16`, which cannot overflow for two `u8` values, then checks whether the result fits back into `u8`. The oracle never calls `checked_add`, so the test does not reuse the implementation it judges.

**Plausible wrong approach.** Testing only small values such as 1 + 2 never reaches the overflow boundary, so an implementation that wraps would pass.

**How to verify.** Run the block. Replace `a.checked_add(b)` with `Some(a.wrapping_add(b))` and the assertion fails at 1 + 255.

### Task 3: Independent construction

Write a property checking an Arrow filter's output count against its Boolean mask.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** The defect is a sort test that only asserts `output.windows(2).all(|pair| pair[0] <= pair[1])`. An implementation that returns an empty vector, a vector of one repeated value, or the input with a duplicate removed passes it, because all of those are sorted. Add the multiplicity check from Example B, or compare the result with a trusted oracle such as a clone sorted by `sort_unstable`.

**Why it is correct.** Sorting has two obligations: the output is ordered, and it is a permutation of the input. A property that checks only the first is too weak to reject an implementation that loses data.

**Plausible wrong approach.** Adding `output.len() == input.len()` alone still accepts `[1, 1, 1, 1]` for the input `[3, 1, 3, 2]`.

**How to verify.** Feed the order-only test a fake sort that returns `Vec::new()`: it passes. Run Example B's multiplicity loop on the same output and it fails.

### Task 5: Boundary evidence

Preserve empty, duplicate and all-null regression fixtures.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Int32Array};
    fn report(values: &Int32Array) -> (usize, usize, i64) {
        let total = values.iter().flatten().map(i64::from).sum();
        (values.len(), values.null_count(), total)
    }
    let fixtures = [
        ("empty", Int32Array::from(Vec::<i32>::new()), (0, 0, 0)),
        ("duplicate", Int32Array::from(vec![4, 4, 1]), (3, 0, 9)),
        ("all null", Int32Array::from(vec![None, None]), (2, 2, 0)),
    ];
    for (name, values, expected) in &fixtures {
        assert_eq!(report(values), *expected, "fixture {name}");
    }
    Ok(())
}
```

**Observe:** The empty, duplicate and all-null fixtures each produce their recorded report, and a failure would name the fixture.

Each fixture is stored with its name and expected result, so it keeps guarding against the defect it represents: duplicates must both count, and an all-null column must report two rows and two nulls rather than looking like the empty input.

**Plausible wrong approach.** Deleting a fixture after its bug is fixed lets the same defect return unnoticed.

**How to verify.** Run the block. Change `report` to deduplicate values before summing and the duplicate fixture fails with its name in the message.

### Task 6: Transfer and justify

Design an external fuzzing and compile-fail plan with reproducible seeds, minimized failures and clear acceptance scope.

**Judging criteria.** A strong plan prepares a separate project with `cargo fuzz` for the parser or kernel under test and a compile-fail harness such as `trybuild` for guarantees enforced by types. Every fuzz run records its seed and corpus, each crash is minimized and saved as a permanent regression input, and each compile-fail case pins its expected error. The acceptance scope states what is covered, such as one function within a time budget, and what is not. State one limitation: fuzzing finds crashes and failed assertions, not wrong answers that no check rejects.

## Mechanism and diagnostic reasoning

Advanced verification combines examples, properties and boundary-specific evidence. A property such as sorting preserving element multiplicity can expose mistakes that one expected list misses. Compile-fail tests can preserve an API's ownership or visibility restrictions, but they belong to a deliberately prepared test harness rather than an ordinary successful runtime reference.

Fuzzing and property-testing crates are valuable external tools, not hidden dependencies in this pad. Start with deterministic exhaustive enumeration over a small bounded domain and an independent oracle. Keep minimized counterexamples when a failure appears. Never weaken an invariant to accommodate a wrong implementation merely because a large suite is expensive.

Nested loops can enumerate a small input space reproducibly. A sorted clone can be compared with the original through a frequency map. Compile diagnostics should be categorized by the violated rule rather than fragile full-message text.

A property can be too weak to distinguish incorrect implementations. Integer overflow can invalidate a mathematical law's assumed domain. Compiler message wording may change even when the underlying rule remains correct.

## Review before continuing

Rebuild Example B (Check order and multiplicity separately) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
