# rust-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-009_solution.rs](rust-009_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow more than once:** Both references inspect the same allocation without taking release responsibility. Two readers coexist and the owner remains intact.

**Return a borrowed view:** The function returns a slice whose validity depends on the input owner. The result is a view into caller-owned text, with an explicit empty policy.

## Task answers

### Task 1: Predict and explain

Identify the owner and both readers.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Both references inspect the same allocation without taking release responsibility. Two readers coexist and the owner remains intact.

### Task 2: Guided modification

Add another read-only inspection without cloning.

No separate reference answer has been written for this task. Start from Example B: The function returns a slice whose validity depends on the input owner. The result is a view into caller-owned text, with an explicit empty policy.

### Task 3: Independent construction

Write a last-word function returning a borrowed slice.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn last_word(text: &str) -> &str {
        text.split_whitespace().last().unwrap_or("")
    }
    let sentence = String::from("pear apple");
    assert_eq!(last_word(&sentence), "apple");
    assert_eq!(last_word(""), "");
    Ok(())
}
```

**Observe:** The last word of pear apple is apple; empty text gives an empty slice.

The returned slice borrows from the input, so the elided lifetime ties the result to text and no new String is allocated.

### Task 4: Diagnose a defect

Try returning a reference to a local String and explain the compiler rejection.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A reference cannot make its owner live longer by declaration alone. Borrow duration follows actual use constraints. Avoid converting every slice to String unless independent ownership is needed.

### Task 5: Boundary evidence

Test empty text and a single word.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Borrow more than once) and Example B (Return a borrowed view).

### Task 6: Transfer and justify

Choose a borrowed view or owned result for a parser whose caller may discard the input immediately.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Shared borrow**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A shared reference grants temporary read access without taking ownership. Several shared borrows can coexist when no conflicting mutation occurs. The owner must remain alive while borrowed data can still be used. Rust's borrow checker tracks these relationships through control flow, often ending a borrow after its last use rather than the end of the entire lexical block.

A borrowed API is useful for inspection, searching and parsing views. It avoids unnecessary allocation while preserving caller ownership. The lifetime constraint is not a runtime timer: it is a compile-time relationship between valid uses. Returning a reference to a local value is invalid because the owner disappears when the function returns.

`&value` creates a shared reference. Dereferencing with `*reference` accesses a referenced scalar when needed. Auto-dereferencing makes many method calls convenient. A return type `&str` must refer to storage owned elsewhere for a sufficient lifetime.

A reference cannot make its owner live longer by declaration alone. Borrow duration follows actual use constraints. Avoid converting every slice to String unless independent ownership is needed.

## Review before continuing

Run the reference and confirm that it prints `rust-009: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
