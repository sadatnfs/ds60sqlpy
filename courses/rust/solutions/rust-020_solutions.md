# rust-020: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-020_solution.rs](rust-020_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Consume a transformation recipe:** Copied turns referenced integers into independent small values before filtering and mapping. The recipe selects and transforms while retaining the borrowed source.

**Observe iterator progress:** Calling next again does not restart the source automatically. The iterator advances and eventually exhausts.

## Task answers

### Task 1: Predict and explain

Identify adapters and the final consumer.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Copied turns referenced integers into independent small values before filtering and mapping. The recipe selects and transforms while retaining the borrowed source.

### Task 2: Guided modification

Add a take limit and predict how much work is demanded.

No separate reference answer has been written for this task. Start from Example B: Calling next again does not restart the source automatically. The iterator advances and eventually exhausts.

### Task 3: Independent construction

Write a borrowed transformation returning a collected result.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn upper_names(names: &[&str]) -> Vec<String> {
        names.iter().map(|name| name.to_uppercase()).collect()
    }
    let names = ["pear", "fig"];
    assert_eq!(upper_names(&names), vec!["PEAR", "FIG"]);
    assert_eq!(names, ["pear", "fig"]);
    Ok(())
}
```

**Observe:** The result is PEAR and FIG, and the borrowed input is unchanged.

The function borrows the input slice, the iterator chain is lazy, and collect consumes it into a new owned Vec.

### Task 4: Diagnose a defect

Diagnose constructing a lazy map and expecting it to execute immediately.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Laziness does not mean no allocation if a later consumer collects. Reusing an exhausted iterator does not recreate it. A chain with hidden effects can execute at an unexpected boundary.

### Task 5: Boundary evidence

Test empty input and a partially consumed iterator.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Consume a transformation recipe) and Example B (Observe iterator progress).

### Task 6: Transfer and justify

Choose iter, iter_mut or into_iter for three operations and justify ownership.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Adapter**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Iterator adapters describe transformations that execute when consumed. Map and filter generally build a recipe; collect, sum or a loop drives it. Repeated iteration is possible only if the source can be recreated or borrowed appropriately. An iterator itself holds progress and may be exhausted.

The three common vector forms make ownership visible: iter yields shared references, iter_mut yields exclusive references, and into_iter consumes owned elements. Choose the form matching the work. A lazily executed closure with side effects is harder to reason about, so keep transformations pure unless the side effect is explicitly the lesson.

`iter().filter(...).map(...)` chains borrowed transformations. collect needs an inferred or annotated target. next advances one iterator instance. into_iter consumes the collection when the collection owns non-Copy elements.

Laziness does not mean no allocation if a later consumer collects. Reusing an exhausted iterator does not recreate it. A chain with hidden effects can execute at an unexpected boundary.

## Review before continuing

Run the reference and confirm that it prints `rust-020: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
