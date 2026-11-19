# rust-005: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-005_solution.rs](rust-005_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Choose a value with if:** Both branches return the same kind of value, so the result has one static type. The branch expression supplies one immutable label.

**Classify explicit boundaries:** A tiny boundary fixture rejects an off-by-one policy error. The transition at sixty and the invalid upper range are distinct.

## Task answers

### Task 1: Predict and explain

Identify the value produced by each branch.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Both branches return the same kind of value, so the result has one static type. The branch expression supplies one immutable label.

### Task 2: Guided modification

Change the threshold and update neighboring tests.

No separate reference answer has been written for this task. Start from Example B: A tiny boundary fixture rejects an off-by-one policy error. The transition at sixty and the invalid upper range are distinct.

### Task 3: Independent construction

Write a negative, zero and positive classifier.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

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

### Task 4: Diagnose a defect

Diagnose a semicolon that changes a branch result into unit.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A semicolon can change a block value. Match arm order matters when patterns overlap. A wildcard that hides an unhandled domain state weakens maintenance feedback.

### Task 5: Boundary evidence

Test both valid endpoints and one value beyond each.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Choose a value with if) and Example B (Classify explicit boundaries).

### Task 6: Transfer and justify

Choose explicit enum matches or a wildcard for a finite application state model.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Expression**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Rust treats many control-flow constructs as expressions producing values. An if expression must return compatible types from its branches. This encourages deriving one result instead of initializing a mutable variable and assigning it inconsistently on several paths.

Match handles patterns and requires coverage of possibilities. A broad wildcard can be useful for invalid numeric ranges but can hide newly added enum cases. Make boundaries explicit and test adjacent inputs. A correct normal example does not prove that an inclusive versus exclusive threshold is right.

`let label = if condition { "yes" } else { "no" };` uses a branch result. The final expression in a block has no semicolon when it supplies the value. `0..=59` is an inclusive pattern range.

A semicolon can change a block value. Match arm order matters when patterns overlap. A wildcard that hides an unhandled domain state weakens maintenance feedback.

## Review before continuing

Run the reference and confirm that it prints `rust-005: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
