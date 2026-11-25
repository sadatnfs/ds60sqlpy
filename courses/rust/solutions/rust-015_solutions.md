# rust-015: explanation and comparison

Executable reference: [rust-015_solution.rs](rust-015_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Parse and validate separately:** Parsing establishes a representation; the second check enforces the domain. Malformed text and negative quantity preserve different reasons.

**Collect only explicitly accepted values:** Converting to Option is deliberate here because the separate count retains rejection evidence; a real importer may need the full reasons. Two accepted values and one rejection are accounted for.

## Task answers

### Task 1: Predict and explain

Trace the success, parse-error and domain-error paths.

**Written answer.** For `"3"`, `text.parse()` yields `Ok(3)`, `?` unwraps it to `3`, the sign check passes and the function returns `Ok(3)`. For `"bad"`, `parse` fails, `map_err` replaces the `ParseIntError` with `"not an integer"`, and `?` returns that error at once, so the sign check never runs. For `"-1"`, parsing succeeds with `-1`, and only the domain check `value < 0` rejects it with `"negative quantity"`.

**Why it is correct.** Syntax is settled before meaning: `?` is the exit for the first stage and the explicit `return Err` is the exit for the second. Each path leaves through exactly one of them, which is why the two reasons never mix.

**Plausible wrong approach.** Reading `"-1"` as a parse failure confuses representation with domain. `-1` is a perfectly valid `i32`; it is the application rule that refuses it.

**How to verify.** Add `assert_eq!("-1".parse::<i32>(), Ok(-1));` next to Example A: it passes, which shows that the rejection came from the second check.

### Task 2: Guided modification

Add an application maximum quantity with a separate error category.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block. Helpers used: `parse_quantity`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    const MAX_QUANTITY: i32 = 1_000;
    fn bounded_quantity(text: &str) -> Result<i32, &'static str> {
        let value = parse_quantity(text)?;
        if value > MAX_QUANTITY {
            return Err("quantity above maximum");
        }
        Ok(value)
    }
    assert_eq!(bounded_quantity("1000"), Ok(1_000));
    assert_eq!(bounded_quantity("1001"), Err("quantity above maximum"));
    assert_eq!(bounded_quantity("bad"), Err("not an integer"));
    assert_eq!(bounded_quantity("-1"), Err("negative quantity"));
    Ok(())
}
```

**Observe:** 1000 is accepted, 1001 is rejected as above maximum, and malformed and negative input keep their original reasons.

The maximum is an application policy layered on top of `parse_quantity`, so it gets its own function and its own error text. `?` forwards the two existing categories unchanged, and the new check runs only on a value that already passed both.

**Plausible wrong approach.** Folding the limit into the parse step with `text.parse::<i32>().ok().filter(|v| *v <= MAX_QUANTITY)` returns `None` for 1001, for `bad` and for `-1` alike, so the caller can no longer tell a typo from an oversized order.

**How to verify.** Run the block, then change `1001` to `1000` in the second assertion and watch it fail with `left: Ok(1000)`, which proves the boundary is inclusive.

### Task 3: Independent construction

Write a function using ? to compose two fallible steps.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block. Helpers used: `parse_quantity`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn doubled_quantity(text: &str) -> Result<i32, &'static str> {
        let value = parse_quantity(text)?;
        value.checked_mul(2).ok_or("quantity too large")
    }
    assert_eq!(doubled_quantity("4"), Ok(8));
    assert_eq!(doubled_quantity("bad"), Err("not an integer"));
    assert_eq!(doubled_quantity("-3"), Err("negative quantity"));
    Ok(())
}
```

**Observe:** 4 doubles to Ok(8); bad text and -3 return their original errors.

The ? operator returns the parse error unchanged, so each failure keeps the message of the step that produced it.

### Task 4: Diagnose a defect

Diagnose replacing every Err with zero.

**Written answer.** The defect is `let quantity = parse_quantity(text).unwrap_or(0);`. Both `"bad"` and `"-1"` become `0`, which is also the result for the legitimate input `"0"`. A total built from such values silently undercounts, and nothing records that any line was rejected.

**Why it is correct.** Zero is a valid quantity in this domain, so it cannot double as a failure marker. Keeping the `Result` until a boundary that can count or report the error is what preserves the evidence.

**Plausible wrong approach.** Replacing `0` with `-1` as the fallback looks safer but reintroduces the same problem with a magic value that later arithmetic will happily add.

**How to verify.** Sum `["2", "bad", "3"]` with `unwrap_or(0)` and get `5`; Example B gets the same `5` but also reports one rejection through `inputs.len() - accepted.len()`.

### Task 5: Boundary evidence

Test empty, zero, negative and overflowing textual input.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block. Helpers used: `parse_quantity`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    assert_eq!(parse_quantity(""), Err("not an integer"));
    assert_eq!(parse_quantity("0"), Ok(0));
    assert_eq!(parse_quantity("-5"), Err("negative quantity"));
    assert_eq!(parse_quantity("2147483647"), Ok(i32::MAX));
    assert_eq!(parse_quantity("2147483648"), Err("not an integer"));
    assert_eq!(parse_quantity(" 3"), Err("not an integer"));
    Ok(())
}
```

**Observe:** Empty text and a leading space are malformed, zero is accepted, -5 is negative, i32::MAX parses, and one past it is reported as not an integer.

`str::parse::<i32>` rejects empty input and surrounding whitespace, so callers must trim deliberately. Overflow is the interesting row: `ParseIntError` knows it is `PosOverflow`, but `map_err(|_| ...)` discards that kind, so a huge number is reported with the same text as a typo.

**Plausible wrong approach.** Assuming `"2147483648"` would wrap to a negative number and be rejected as negative ignores that `parse` checks the range and never wraps.

**How to verify.** Run the block. Then print `"2147483648".parse::<i32>().unwrap_err().kind()` and see `PosOverflow`, the detail a dedicated error category could keep.

### Task 6: Transfer and justify

Choose a public error enum and explain which internal details should remain private.

**Judging criteria.** A strong public enum names recovery categories, for example `Malformed`, `OutOfRange { max }` and `Io`, and keeps internal detail such as raw input, file paths with user names or library error types behind `source()` or out of the type entirely. Each variant should help a caller decide what to do next. State one limitation: adding a variant to a public enum is a breaking change unless it is marked `#[non_exhaustive]`.

## Mechanism and diagnostic reasoning

Result distinguishes Ok(value) from Err(error). It is appropriate when failure has a reason that a caller should inspect or propagate. Parsing text naturally returns a Result because malformed input is different from an ordinary missing lookup. A robust boundary should preserve the distinction between syntax failure and domain rejection.

The question-mark operator returns early with an error while continuing with the successful value. It is a control-flow shortcut with a clear type contract, not an instruction to ignore failure. The main wrapper used in this course can propagate errors to an unsuccessful process outcome. Production APIs should choose error types that expose useful categories without leaking sensitive raw input.

`Result<T,E>` carries a success type and an error type. `?` unwraps success or converts and returns an error. map_err translates an error deliberately. match handles both paths explicitly.

Calling .ok discards the error reason. A catch-all fallback can turn data loss into success. Panic is generally the wrong interface for expected invalid external input.

## Review before continuing

Rebuild Example B (Collect only explicitly accepted values) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
