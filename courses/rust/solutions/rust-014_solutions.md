# rust-014: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-014_solution.rs](rust-014_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep zero distinct from missing:** Absence is a separate case, not a special numeric value. A measured zero remains present and transforms to one.

**Propagate absence until a boundary:** The fallback is not inserted into the collection and should not be mistaken for a valid measurement. An absent lookup stays absent until the explicit display fallback.

## Task answers

### Task 1: Predict and explain

Predict mapping Some(0) and None.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Absence is a separate case, not a special numeric value. A measured zero remains present and transforms to one.

### Task 2: Guided modification

Render missing data as an unknown label instead of a numeric sentinel.

No separate reference answer has been written for this task. Start from Example B: The fallback is not inserted into the collection and should not be mistaken for a valid measurement. An absent lookup stays absent until the explicit display fallback.

### Task 3: Independent construction

Write a first-valid-item lookup returning Option.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn first_valid(values: &[i32]) -> Option<i32> {
        values.iter().copied().find(|value| *value >= 0)
    }
    assert_eq!(first_valid(&[-2, 0, 5]), Some(0));
    assert_eq!(first_valid(&[-1, -3]), None);
    Ok(())
}
```

**Observe:** The first valid item in -2, 0, 5 is Some(0); no valid item gives None.

find returns Option, so a valid zero stays distinguishable from having no valid item at all.

### Task 4: Diagnose a defect

Diagnose unwrap on an ordinary not-found path.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: None does not explain a failure reason; use Result when a reason matters. A default can hide missing data. Avoid converting every optional to a panic merely to shorten control flow.

### Task 5: Boundary evidence

Test empty collections, present zero and out-of-range lookup.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Keep zero distinct from missing) and Example B (Propagate absence until a boundary).

### Task 6: Transfer and justify

Choose when absence should remain optional and when it should become a domain error.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Option**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Option represents either Some(value) or None. It is appropriate when absence is an expected outcome, such as a lookup finding no record. A real zero remains Some(0), keeping it distinct from missing information. This type-level distinction prevents sentinel values from leaking into valid calculations.

Unwrap asserts that absence is impossible and panics otherwise. Use it only when a nearby invariant or authored fixture makes that claim clear. Pattern matching, map and and_then let code retain absence through transformations until a boundary deliberately chooses a fallback. Choosing a default too early can erase information the caller needs.

`Option<T>` carries a present T or absence. `if let Some(value)` handles the present case. map transforms a present value; and_then chains an operation already returning Option. unwrap_or supplies a deliberate fallback.

None does not explain a failure reason; use Result when a reason matters. A default can hide missing data. Avoid converting every optional to a panic merely to shorten control flow.

## Review before continuing

Run the reference and confirm that it prints `rust-014: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
