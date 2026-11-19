# rust-004: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-004_solution.rs](rust-004_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow without consuming ownership:** Borrowing reads the existing storage without transferring its lifetime responsibility. Both views observe pear while the owner remains usable.

**Respect byte boundaries:** The optional slicing API makes invalid boundaries observable without panicking. The scalar uses two bytes, and its first byte alone is not a valid string slice.

## Task answers

### Task 1: Predict and explain

Predict byte and scalar counts for the accented character.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Borrowing reads the existing storage without transferring its lifetime responsibility. Both views observe pear while the owner remains usable.

### Task 2: Guided modification

Compare an emoji and a combining-mark sequence.

No separate reference answer has been written for this task. Start from Example B: The optional slicing API makes invalid boundaries observable without panicking. The scalar uses two bytes, and its first byte alone is not a valid string slice.

### Task 3: Independent construction

Write a function accepting &str and returning its byte length.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn byte_length(text: &str) -> usize {
        text.len()
    }
    assert_eq!(byte_length("pear"), 4);
    assert_eq!(byte_length("é"), 2);
    assert_eq!(byte_length(&String::from("café")), 5);
    Ok(())
}
```

**Observe:** pear has 4 bytes, é has 2 and café has 5.

&str accepts both literals and borrowed Strings, and len counts UTF-8 bytes rather than characters.

### Task 4: Diagnose a defect

Diagnose indexing a string as if every character were one byte.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Chars are not always user-visible characters. A borrowed slice cannot outlive its owner. Use a Unicode segmentation crate only in a separately prepared project, not an undeclared pad dependency.

### Task 5: Boundary evidence

Test empty text and an invalid byte boundary through get.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Borrow without consuming ownership) and Example B (Respect byte boundaries).

### Task 6: Transfer and justify

Design a text limit and state whether it counts bytes, scalars or graphemes requiring an external library.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **String**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

String owns a growable UTF-8 buffer; str is a string slice, commonly borrowed as &str. A text literal has static storage and can be borrowed without allocating an owned String. This distinction lets APIs accept text without unnecessarily copying it.

UTF-8 byte length differs from Unicode scalar count and user-perceived grapheme count. Rust's standard chars iterator visits Unicode scalar values, not full grapheme clusters. Byte slicing must use valid UTF-8 boundaries or it panics. Choose the unit required by a task before counting, slicing or limiting input.

`String::from("text")` creates owned text. `&text` can borrow it as &str. `len()` counts UTF-8 bytes, `chars().count()` counts scalars, and `get(range)` returns an optional slice if boundaries are valid.

Chars are not always user-visible characters. A borrowed slice cannot outlive its owner. Use a Unicode segmentation crate only in a separately prepared project, not an undeclared pad dependency.

## Review before continuing

Run the reference and confirm that it prints `rust-004: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
