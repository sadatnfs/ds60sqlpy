# rust-004: String ownership, UTF-8 and text boundaries

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-003`

## Learning objectives

Work with owned String and borrowed &str and index UTF-8 text only at valid boundaries. The central exercise is task 3: Write a function accepting &str and returning its byte length.

## Purpose and mental model

String owns a growable UTF-8 buffer; str is a string slice, commonly borrowed as &str. A text literal has static storage and can be borrowed without allocating an owned String. This distinction lets APIs accept text without unnecessarily copying it.

UTF-8 byte length differs from Unicode scalar count and user-perceived grapheme count. Rust's standard chars iterator visits Unicode scalar values, not full grapheme clusters. Byte slicing must use valid UTF-8 boundaries or it panics. Choose the unit required by a task before counting, slicing or limiting input.

## Vocabulary and concepts

**String:** An owned growable UTF-8 string.

**str slice:** A borrowed view of valid UTF-8 text.

**Unicode scalar:** A code point excluding surrogate values, distinct from a grapheme cluster.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-004: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`String::from("text")` creates owned text. `&text` can borrow it as &str. `len()` counts UTF-8 bytes, `chars().count()` counts scalars, and `get(range)` returns an optional slice if boundaries are valid.

**Reading Example A (Borrow without consuming ownership, code below).** `String::from("pear")` copies the literal's four bytes into a new heap buffer that `owned` is responsible for freeing. On line 2, `&owned` has type `&String`; the annotation `&str` asks for a string slice instead, and the compiler inserts a deref coercion that produces a pointer and a length into the same buffer, with no copy. `borrowed` is therefore a view, and `assert_eq!(borrowed, "pear")` compares text, not addresses. `owned.len()` on the last line reads through the owner: `len` counts bytes of UTF-8, which matches the character count here only because every letter of pear is ASCII. Both names stay usable because nothing was moved.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Borrow without consuming ownership

Borrowing reads the existing storage without transferring its lifetime responsibility.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let owned = String::from("pear");
        let borrowed: &str = &owned;
        assert_eq!(borrowed, "pear");
        assert_eq!(owned.len(), 4);
    }
    println!("rust-004: passed");
    Ok(())
}
```

**Observe:** Both views observe pear while the owner remains usable.

### Example B: Respect byte boundaries

The optional slicing API makes invalid boundaries observable without panicking.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = "é";
        assert_eq!(text.len(), 2);
        assert_eq!(text.chars().count(), 1);
        assert_eq!(text.get(0..1), None);
        assert_eq!(text.get(0..2), Some("é"));
    }
    println!("rust-004: passed");
    Ok(())
}
```

**Observe:** The scalar uses two bytes, and its first byte alone is not a valid string slice.

## Exercises

1. **Predict and explain.** Predict byte and scalar counts for the accented character.

2. **Guided modification.** Compare an emoji and a combining-mark sequence.

3. **Independent construction.** Write a function accepting &str and returning its byte length.

4. **Diagnose a defect.** Diagnose indexing a string as if every character were one byte.

5. **Boundary evidence.** Test empty text and an invalid byte boundary through get.

6. **Transfer and justify.** Design a text limit and state whether it counts bytes, scalars or graphemes requiring an external library.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Chars are not always user-visible characters. A borrowed slice cannot outlive its owner. Use a Unicode segmentation crate only in a separately prepared project, not an undeclared pad dependency.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Borrow without consuming ownership) before changing anything, and confirm its observation: Both views observe pear while the owner remains usable.
2. Compare Example B (Respect byte boundaries) with Example A and name the first line whose behavior differs. Its observation is: The scalar uses two bytes, and its first byte alone is not a valid string slice.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Chars are not always user-visible characters.

Tempting approaches to rule out before you compare:

- **Task 1.** Predicting `len() == 1` because the glyph looks like one character confuses bytes with scalars. Predicting two scalars is only right if the source holds the decomposed form `e` plus U+0301, which an editor might produce silently.
- **Task 2.** Treating `chars().count()` as the visible length makes `accented.chars().take(1)` return just `"e"`, silently dropping the accent. A one-character limit would cut between the letter and its mark.
- **Task 3.** Declaring the parameter as `text: String` breaks the first call: `byte_length("pear")` is E0308, expected `String`, found `&str`. Passing an owned `String` would also move it into the function, so the caller could not use it afterwards. Returning `text.chars().count()` instead gives 4 for `café`, not 5.
- **Task 5.** Probing with `&text[0..1]` aborts the test instead of observing the boundary: on `""` it panics with an out-of-bounds byte index, and on `"é"` with the char-boundary message, so the later checks never run.
- **Task 6.** `text.chars().take(16).collect::<String>()` limits scalars, not bytes: sixteen crab emoji produce 64 bytes, four times the field size. Writing `&text[..max]` instead panics whenever `max` lands inside a multibyte scalar.

## Self-check and next step

How many bytes and how many `chars` does the precomposed `"é"` contain, and how does `"e\u{301}"` differ even though it looks the same? What does `"é".get(0..1)` return, and why does `&"é"[0..1]` panic instead? Why can one function taking `&str` accept both a `String` and a literal?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 8.2 Strings](https://doc.rust-lang.org/book/ch08-02-strings.html) for why Rust refuses to index a `String` by integer.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-004: String ownership, UTF-8 and text boundaries.
Read courses/rust/guides/rust-004.md and courses/rust/lessons/rust-004.rs. Prerequisites: rust-003.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-004_solution.rs and
courses/rust/solutions/rust-004_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
