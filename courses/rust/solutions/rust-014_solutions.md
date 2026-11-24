# rust-014: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-014_solution.rs](rust-014_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep zero distinct from missing:** Absence is a separate case, not a special numeric value. A measured zero remains present and transforms to one.

**Propagate absence until a boundary:** The fallback is not inserted into the collection and should not be mistaken for a valid measurement. An absent lookup stays absent until the explicit display fallback.

## Task answers

### Task 1: Predict and explain

Predict mapping Some(0) and None.

**Written answer.** `measured.map(|value| value + 1)` on `Some(0)` returns `Some(1)`. `missing.map(|value| value + 1)` on `None` returns `None` and never calls the closure.

**Why it is correct.** `map` transforms only the value inside `Some` and passes `None` through unchanged, so absence survives the transformation and zero is treated as an ordinary present value.

**Plausible wrong approach.** Treating `None` like 0 predicts `Some(1)` for both, and treating `Some(0)` as empty predicts `None` for both. Each erases the distinction Example A's `assert_ne!(measured, missing)` establishes.

**How to verify.** Add `assert_eq!(missing.map(|value| value + 1), None);` and count closure calls: `let mut calls = 0; let _ = missing.map(|value| { calls += 1; value }); assert_eq!(calls, 0);`.

### Task 2: Guided modification

Render missing data as an unknown label instead of a numeric sentinel.

**Written answer.** Render at the display boundary: `fn render(value: Option<i32>) -> String { match value { Some(number) => number.to_string(), None => String::from("unknown") } }`. Then `render(values.get(9).copied())` gives `unknown` and `render(Some(0))` gives `0`.

**Why it is correct.** The fallback is a label of a different kind from any measurement, so it cannot be mistaken for data, and the match forces both cases to be handled explicitly.

**Plausible wrong approach.** Keeping Example B's `unwrap_or(-1)` and printing the number is ambiguous wherever -1 is a valid reading, such as a temperature. `unwrap_or(0)` is worse here: a missing reading prints the same as the measured zero in Example A.

**How to verify.** Assert `render(Some(0)) == "0"`, `render(Some(-1)) == "-1"` and `render(None) == "unknown"`. All three strings differ, so every case is distinguishable.

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

**Plausible wrong approach.** Using `find(|value| *value > 0)` treats zero as invalid, so `first_valid(&[-2, 0, 5])` returns `Some(5)` and the first assertion panics. The reference uses `>= 0` because a valid zero must be found.

**How to verify.** Add `assert_eq!(first_valid(&[]), None);` and `assert_eq!(first_valid(&[0]), Some(0));`. Run the block and `rust-014: passed` prints.

### Task 4: Diagnose a defect

Diagnose unwrap on an ordinary not-found path.

**Written answer.** The defect is `let value = values.get(9).unwrap();` on `[2, 4]`. Index 9 is an ordinary not-found case, yet `unwrap` panics with `called Option::unwrap() on a None value`. Return the absence instead: `fn doubled(values: &[i32], index: usize) -> Option<i32> { let value = values.get(index)?; Some(value * 2) }`.

**Why it is correct.** `unwrap` asserts an invariant that does not hold here. The `?` operator on an `Option` returns `None` from the function early, so the caller decides what absence means.

**Plausible wrong approach.** Replacing `unwrap()` with `expect("value exists")` only changes the panic message. Replacing it with `unwrap_or_default()` removes the panic but returns 0, which hides the missing value as a fake measurement.

**How to verify.** Run the defect and read the `None` panic with no marker after it. Then assert `doubled(&[2, 4], 9) == None` and `doubled(&[2, 4], 1) == Some(8)`.

### Task 5: Boundary evidence

Test empty collections, present zero and out-of-range lookup.

**Written answer.** With `let empty: [i32; 0] = [];`, assert `empty.first() == None` and `first_valid(&empty) == None`. With `let zeros = [0];`, assert `zeros.get(0) == Some(&0)` and `zeros.get(1) == None`.

**Why it is correct.** `first` and `get` return `Option<&i32>`, so an empty array and an out-of-range index both produce `None`, while a stored zero produces `Some(&0)`.

**Plausible wrong approach.** Testing presence with `values.get(i).copied().unwrap_or(0) != 0` reports the stored zero as missing, collapsing the present-zero and absent cases this task separates.

**How to verify.** Run the four checks; the run prints `rust-014: passed` only if the present zero and the absent index were kept distinct.

### Task 6: Transfer and justify

Choose when absence should remain optional and when it should become a domain error.

**Written answer.** Keep `Option` when absence is a normal answer, such as a cache miss. Convert to a domain error when the caller needs a reason: `#[derive(Debug, PartialEq)] enum PortError { Missing, NotNumber }` with `fn port(raw: Option<&str>) -> Result<u16, PortError> { let text = raw.ok_or(PortError::Missing)?; text.parse().map_err(|_| PortError::NotNumber) }`.

**Why it is correct.** `ok_or` turns `None` into a named error at the boundary, and `map_err` keeps a parse failure separate from a missing field. A limitation is the extra error type every caller must match.

**Plausible wrong approach.** Returning `Option<u16>` for the port with `raw?.parse().ok()` collapses a missing field and `port=abc` into the same `None`, so the caller cannot tell the user which problem to fix.

**How to verify.** Assert `port(None) == Err(PortError::Missing)`, `port(Some("abc")) == Err(PortError::NotNumber)` and `port(Some("8080")) == Ok(8080)`.

## Mechanism and diagnostic reasoning

Option represents either Some(value) or None. It is appropriate when absence is an expected outcome, such as a lookup finding no record. A real zero remains Some(0), keeping it distinct from missing information. This type-level distinction prevents sentinel values from leaking into valid calculations.

Unwrap asserts that absence is impossible and panics otherwise. Use it only when a nearby invariant or authored fixture makes that claim clear. Pattern matching, map and and_then let code retain absence through transformations until a boundary deliberately chooses a fallback. Choosing a default too early can erase information the caller needs.

`Option<T>` carries a present T or absence. `if let Some(value)` handles the present case. map transforms a present value; and_then chains an operation already returning Option. unwrap_or supplies a deliberate fallback.

None does not explain a failure reason; use Result when a reason matters. A default can hide missing data. Avoid converting every optional to a panic merely to shorten control flow.

## Review before continuing

Run the reference and confirm that it prints `rust-014: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
