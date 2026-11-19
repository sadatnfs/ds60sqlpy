# rust-019: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-019_solution.rs](rust-019_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Return one input view:** The annotation prevents a caller from using the view after a required owner is gone. The output is a borrowed view of the longer input.

**Own a result when lifetime must separate:** A deliberate owned copy changes the lifetime contract rather than pretending the borrow is static. The independent owned result survives the temporary scope.

## Task answers

### Task 1: Predict and explain

Draw the valid-use regions of both inputs and the output.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The annotation prevents a caller from using the view after a required owner is gone. The output is a borrowed view of the longer input.

### Task 2: Guided modification

Test the tie policy of longer.

No separate reference answer has been written for this task. Start from Example B: A deliberate owned copy changes the lifetime contract rather than pretending the borrow is static. The independent owned result survives the temporary scope.

### Task 3: Independent construction

Write a borrowed prefix parser with the narrowest lifetime relationship.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn split_prefix<'a>(text: &'a str, prefix: &str) -> Option<&'a str> {
        text.strip_prefix(prefix)
    }
    let line = String::from("qty:42");
    let rest = {
        let prefix = String::from("qty:");
        split_prefix(&line, &prefix)
    };
    assert_eq!(rest, Some("42"));
    Ok(())
}
```

**Observe:** The rest of qty:42 is Some("42"), still usable after the prefix String is dropped.

Only text shares the result's lifetime 'a; prefix gets its own shorter lifetime, so the caller can drop it while keeping the result.

### Task 4: Diagnose a defect

Try returning a local reference and explain why annotations cannot make it valid.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Lifetime names describe relationships, not durations in seconds. Static is not a universal fix. A lifetime annotation cannot rescue a reference to destroyed local storage.

### Task 5: Boundary evidence

Test empty inputs and use after one candidate owner leaves scope.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Return one input view) and Example B (Own a result when lifetime must separate).

### Task 6: Transfer and justify

Choose a borrowed or owned result for a cache boundary and justify cost and lifetime.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Lifetime parameter**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A lifetime parameter expresses a relationship between references. It does not allocate storage or extend an owner's life. A function returning one of two borrowed inputs must describe that the output is valid only where both candidate input borrows are valid. The caller and compiler then check actual uses against that relationship.

Prefer simple ownership first. Lifetime annotations become useful when an API deliberately returns views or stores borrowed data. Returning an owned value can simplify a boundary when independent lifetime is required, at an explicit copying cost. Do not force static lifetime onto data merely to suppress a diagnostic.

`fn choose<'a>(left: &'a str, right: &'a str) -> &'a str` relates the output borrow to both inputs. Elision handles common simple cases automatically. A struct field containing a reference also needs its lifetime relationship.

Lifetime names describe relationships, not durations in seconds. Static is not a universal fix. A lifetime annotation cannot rescue a reference to destroyed local storage.

## Review before continuing

Run the reference and confirm that it prints `rust-019: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
