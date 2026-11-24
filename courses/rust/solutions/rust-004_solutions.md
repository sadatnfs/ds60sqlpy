# rust-004: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-004_solution.rs](rust-004_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow without consuming ownership:** Borrowing reads the existing storage without transferring its lifetime responsibility. Both views observe pear while the owner remains usable.

**Respect byte boundaries:** The optional slicing API makes invalid boundaries observable without panicking. The scalar uses two bytes, and its first byte alone is not a valid string slice.

## Task answers

### Task 1: Predict and explain

Predict byte and scalar counts for the accented character.

**Written answer.** The precomposed `é` is U+00E9, encoded in UTF-8 as the two bytes `0xC3 0xA9`. So `len()` returns 2 and `chars().count()` returns 1, exactly as Example B asserts.

**Why it is correct.** `len` counts bytes of the UTF-8 encoding, and scalars from U+0080 to U+07FF take two bytes. `chars` decodes those bytes back into one `char`.

**Plausible wrong approach.** Predicting `len() == 1` because the glyph looks like one character confuses bytes with scalars. Predicting two scalars is only right if the source holds the decomposed form `e` plus U+0301, which an editor might produce silently.

**How to verify.** Add `assert_eq!("é".as_bytes(), &[0xC3, 0xA9]);` and `assert_eq!('é' as u32, 0xE9);`. If the first check fails with three bytes, the file contains the decomposed form.

### Task 2: Guided modification

Compare an emoji and a combining-mark sequence.

**Written answer.** Write both with escapes so no editor normalizes them: `let crab = "\u{1F980}";` has `len()` 4 and one scalar, while `let accented = "e\u{301}";` has `len()` 3 and two scalars, yet it displays as one accented letter.

**Why it is correct.** Scalars above U+FFFF need four UTF-8 bytes. The combining acute accent U+0301 needs two bytes and follows a one-byte `e`, and `chars` yields it as its own scalar even though a reader sees one grapheme.

**Plausible wrong approach.** Treating `chars().count()` as the visible length makes `accented.chars().take(1)` return just `"e"`, silently dropping the accent. A one-character limit would cut between the letter and its mark.

**How to verify.** Assert `crab.len() == 4`, `crab.chars().count() == 1`, `accented.len() == 3`, `accented.chars().count() == 2` and `accented.chars().take(1).collect::<String>() == "e"`. All pass, showing scalars are not graphemes.

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

**Plausible wrong approach.** Declaring the parameter as `text: String` breaks the first call: `byte_length("pear")` is E0308, expected `String`, found `&str`. Passing an owned `String` would also move it into the function, so the caller could not use it afterwards. Returning `text.chars().count()` instead gives 4 for `café`, not 5.

**How to verify.** Run the block, then add `let owned = String::from("café"); assert_eq!(byte_length(&owned), 5); assert_eq!(owned, "café");`. Deref coercion turns `&String` into `&str`, and the final check proves the owner is still usable.

### Task 4: Diagnose a defect

Diagnose indexing a string as if every character were one byte.

**Written answer.** `text[0]` does not compile: E0277 says `str` cannot be indexed by an integer. The runtime version, `&text[0..1]` on `"é"`, panics with `byte index 1 is not a char boundary`. Fix it with `text.chars().next()` for the first scalar, or `text.get(0..1)` to observe `None` without a panic.

**Why it is correct.** A `str` is UTF-8 bytes and ranges are byte offsets, so a range must start and end on scalar boundaries. Rust refuses integer indexing because one byte is not a character in multibyte text.

**Plausible wrong approach.** Testing the slice only on `"pear"` passes, because every ASCII letter is one byte. The defect appears only with multibyte input such as the last letter of `"café"`, where `&text[3..4]` panics.

**How to verify.** Assert `"é".chars().next() == Some('é')`, `"café".get(3..4) == None` and `"café".get(3..5) == Some("é")`. The `é` in `café` occupies bytes 3 and 4, so only the second range is valid.

### Task 5: Boundary evidence

Test empty text and an invalid byte boundary through get.

**Written answer.** Check `assert_eq!("".len(), 0);`, `assert_eq!("".get(0..0), Some(""));`, `assert_eq!("".get(0..1), None);` and `assert_eq!("é".get(1..2), None);`. Every probe goes through `get`, so invalid ranges return `None`.

**Why it is correct.** An empty range at offset 0 is a valid slice of any string, including the empty one. A range past the end, or one starting inside the two bytes of `é`, is invalid, and `get` reports that as `None` instead of panicking.

**Plausible wrong approach.** Probing with `&text[0..1]` aborts the test instead of observing the boundary: on `""` it panics with an out-of-bounds byte index, and on `"é"` with the char-boundary message, so the later checks never run.

**How to verify.** Run the four checks plus `assert_eq!("".chars().next(), None);`. All pass and `rust-004: passed` prints.

### Task 6: Transfer and justify

Design a text limit and state whether it counts bytes, scalars or graphemes requiring an external library.

**Written answer.** For a storage field limited to 16 bytes, count bytes and cut at the last scalar boundary: `fn truncate_bytes(text: &str, max: usize) -> &str { let mut end = max.min(text.len()); while !text.is_char_boundary(end) { end -= 1; } &text[..end] }`. A display limit in visible characters would need graphemes from a segmentation crate in a separately prepared Cargo project.

**Why it is correct.** `is_char_boundary` is always true at 0 and at `len()`, so the loop stops, and the slice is valid UTF-8 of at most `max` bytes. The elided lifetime ties the returned `&str` to `text`, so no copy is made. A limitation is that it may still cut a combining mark away from its base letter.

**Plausible wrong approach.** `text.chars().take(16).collect::<String>()` limits scalars, not bytes: sixteen crab emoji produce 64 bytes, four times the field size. Writing `&text[..max]` instead panics whenever `max` lands inside a multibyte scalar.

**How to verify.** Assert `truncate_bytes("café", 4) == "caf"`, `truncate_bytes("café", 5) == "café"`, `truncate_bytes("pear", 10) == "pear"` and `truncate_bytes("\u{1F980}", 3) == ""`. Each result is a valid `&str` no longer than the limit.

## Mechanism and diagnostic reasoning

String owns a growable UTF-8 buffer; str is a string slice, commonly borrowed as &str. A text literal has static storage and can be borrowed without allocating an owned String. This distinction lets APIs accept text without unnecessarily copying it.

UTF-8 byte length differs from Unicode scalar count and user-perceived grapheme count. Rust's standard chars iterator visits Unicode scalar values, not full grapheme clusters. Byte slicing must use valid UTF-8 boundaries or it panics. Choose the unit required by a task before counting, slicing or limiting input.

`String::from("text")` creates owned text. `&text` can borrow it as &str. `len()` counts UTF-8 bytes, `chars().count()` counts scalars, and `get(range)` returns an optional slice if boundaries are valid.

Chars are not always user-visible characters. A borrowed slice cannot outlive its owner. Use a Unicode segmentation crate only in a separately prepared project, not an undeclared pad dependency.

## Review before continuing

Run the reference and confirm that it prints `rust-004: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
