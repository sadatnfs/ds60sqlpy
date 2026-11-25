# rust-005: explanation and comparison

Executable reference: [rust-005_solution.rs](rust-005_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Choose a value with if:** Both branches return the same kind of value, so the result has one static type. The branch expression supplies one immutable label.

**Classify explicit boundaries:** A tiny boundary fixture rejects an off-by-one policy error. The transition at sixty and the invalid upper range are distinct.

## Task answers

### Task 1: Predict and explain

Identify the value produced by each branch.

**Written answer.** Example A binds `label` to `"present"` because `3 > 0`; the else branch never runs. In Example B, `classify(59)` takes `0..=59` and returns `"retry"`, `classify(60)` takes `60..=100` and returns `"pass"`, and `classify(101)` reaches the wildcard and returns `"invalid"`.

**Why it is correct.** `if` and `match` are expressions, so the chosen branch's final value becomes the binding. Every branch yields a `&'static str`, which gives `label` and the closure's result one static type.

**Plausible wrong approach.** Reading `0..=59` as exclusive predicts that 59 is not retry. With an exclusive pattern `0..59`, 59 would match neither range and fall to `_`, returning `"invalid"`, not `"pass"`.

**How to verify.** The existing checks confirm 59, 60 and 101. Add `assert_eq!(classify(0), "retry");` and `assert_eq!(classify(100), "pass");` to confirm both inclusive outer ends.

### Task 2: Guided modification

Change the threshold and update neighboring tests.

**Written answer.** Move the threshold to 70 in both ranges: `0..=69 => "retry", 70..=100 => "pass"`. Update the neighbors to `classify(69) == "retry"` and `classify(70) == "pass"`, and keep the 101 check.

**Why it is correct.** The two ranges still partition 0 to 100 with no gap or overlap, and the checks at 69 and 70 pin the new boundary from both sides.

**Plausible wrong approach.** Editing only the second arm to `70..=100` leaves 60 through 69 unmatched by either range. The wildcard keeps the match exhaustive, so it compiles, and `classify(65)` silently returns `"invalid"`.

**How to verify.** Add `assert_eq!(classify(65), "retry");`. On the half-edited version it panics with `left: "invalid"` and `right: "retry"`; with both arms changed, all checks pass.

### Task 3: Independent construction

Write a negative, zero and positive classifier.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn classify(value: i32) -> &'static str {
        match value {
            i32::MIN..=-1 => "negative",
            0 => "zero",
            1..=i32::MAX => "positive",
        }
    }
    assert_eq!(classify(-4), "negative");
    assert_eq!(classify(0), "zero");
    assert_eq!(classify(9), "positive");
    Ok(())
}
```

**Observe:** -4, 0 and 9 are classified as negative, zero and positive.

The three ranges cover every i32 exactly once, so the match is exhaustive without a catch-all arm that could hide a mistake.

**Plausible wrong approach.** Writing the first arm as `i32::MIN..=0` is an off-by-one: 0 matches it first and is classified negative. rustc warns that the later `0` arm is an unreachable pattern, and `assert_eq!(classify(0), "zero")` panics.

**How to verify.** The block checks -4, 0 and 9. Add the extremes and neighbors: `classify(i32::MIN)` and `classify(-1)` give `"negative"`, `classify(1)` and `classify(i32::MAX)` give `"positive"`.

### Task 4: Diagnose a defect

Diagnose a semicolon that changes a branch result into unit.

**Written answer.** The defect is `let label = if count > 0 { "present"; } else { "empty" };`. The semicolon makes the first branch a statement, so that block evaluates to `()`, and rustc reports E0308 because the `if` and `else` branches have incompatible types. Removing the semicolon restores the `&str` value.

**Why it is correct.** A block's value is its final expression only when no semicolon follows it. With the semicolon, the string is evaluated and discarded, and the branch produces unit.

**Plausible wrong approach.** Making the branches agree by adding a semicolon after `"empty"` too compiles, but `label` becomes `()`. The following `assert_eq!(label, "present")` then fails to compile, because `()` cannot be compared with `&str`.

**How to verify.** Compile the defect and read the E0308 message about incompatible branch types. Remove the semicolon and `assert_eq!(label, "present");` passes.

### Task 5: Boundary evidence

Test both valid endpoints and one value beyond each.

**Written answer.** Check both valid endpoints and one value past each: `classify(0) == "retry"`, `classify(100) == "pass"`, `classify(-1) == "invalid"` and `classify(101) == "invalid"`.

**Why it is correct.** 0 and 100 are the inclusive outer ends of `0..=59` and `60..=100`, and -1 and 101 are the nearest values outside them, which only the wildcard catches.

**Plausible wrong approach.** Testing 1 and 99 instead of 0 and 100 passes a classifier written as `1..=59` and `60..=99`, which wrongly sends 0 and 100 to `"invalid"`.

**How to verify.** Run the four checks. Change `60..=100` to `60..100` temporarily: `classify(100)` panics with `left: "invalid"` and `right: "pass"`. Restore it and all four pass.

### Task 6: Transfer and justify

Choose explicit enum matches or a wildcard for a finite application state model.

**Written answer.** For `enum Order { Draft, Paid, Shipped }`, list every variant: `fn can_cancel(order: &Order) -> bool { match order { Order::Draft | Order::Paid => true, Order::Shipped => false } }`. Keep wildcards for open numeric domains such as scores, where `_` represents invalid input.

**Why it is correct.** With explicit arms, adding a variant such as `Refunded` makes every incomplete match fail with E0004, non-exhaustive patterns, so each decision is revisited. A limitation is that an enum from another crate marked `#[non_exhaustive]` still requires a wildcard.

**Plausible wrong approach.** Writing `Order::Shipped => false, _ => true` is correct today, but when `Refunded` is added it silently becomes cancellable. The wildcard removes the compiler feedback the lesson's pitfall warns about.

**How to verify.** Assert `can_cancel(&Order::Paid)` and `!can_cancel(&Order::Shipped)`. Then add `Refunded` temporarily: compilation fails with E0004 naming `Order::Refunded` as not covered. Remove it again.

## Mechanism and diagnostic reasoning

Rust treats many control-flow constructs as expressions producing values. An if expression must return compatible types from its branches. This encourages deriving one result instead of initializing a mutable variable and assigning it inconsistently on several paths.

Match handles patterns and requires coverage of possibilities. A broad wildcard can be useful for invalid numeric ranges but can hide newly added enum cases. Make boundaries explicit and test adjacent inputs. A correct normal example does not prove that an inclusive versus exclusive threshold is right.

`let label = if condition { "yes" } else { "no" };` uses a branch result. The final expression in a block has no semicolon when it supplies the value. `0..=59` is an inclusive pattern range.

A semicolon can change a block value. Match arm order matters when patterns overlap. A wildcard that hides an unhandled domain state weakens maintenance feedback.

## Review before continuing

Rebuild Example B (Classify explicit boundaries) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
