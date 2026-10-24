# rust-004: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-004_solution.rs](rust-004_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow without consuming ownership:** Borrowing reads the existing storage without transferring its lifetime responsibility. Both views observe pear while the owner remains usable.

**Respect byte boundaries:** The optional slicing API makes invalid boundaries observable without panicking. The scalar uses two bytes, and its first byte alone is not a valid string slice.

## Reason through the six tasks

1. **Predict and explain.** Predict byte and scalar counts for the accented character.

2. **Guided modification.** Compare an emoji and a combining-mark sequence.

3. **Independent construction.** Write a function accepting &str and returning its byte length.

4. **Diagnose a defect.** Diagnose indexing a string as if every character were one byte.

5. **Boundary evidence.** Test empty text and an invalid byte boundary through get.

6. **Transfer and justify.** Design a text limit and state whether it counts bytes, scalars or graphemes requiring an external library.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

String owns a growable UTF-8 buffer; str is a string slice, commonly borrowed as &str. A text literal has static storage and can be borrowed without allocating an owned String. This distinction lets APIs accept text without unnecessarily copying it.

UTF-8 byte length differs from Unicode scalar count and user-perceived grapheme count. Rust's standard chars iterator visits Unicode scalar values, not full grapheme clusters. Byte slicing must use valid UTF-8 boundaries or it panics. Choose the unit required by a task before counting, slicing or limiting input.

`String::from("text")` creates owned text. `&text` can borrow it as &str. `len()` counts UTF-8 bytes, `chars().count()` counts scalars, and `get(range)` returns an optional slice if boundaries are valid.

Chars are not always user-visible characters. A borrowed slice cannot outlive its owner. Use a Unicode segmentation crate only in a separately prepared project, not an undeclared pad dependency.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
