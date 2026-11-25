# rust-007: explanation and comparison

Executable reference: [rust-007_solution.rs](rust-007_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Return a derived integer:** The Copy semantics of this small value permit reuse without transferring an owned allocation. The integer remains available after the call.

**Accept different text owners:** The function needs only a read-only text view, so taking String would impose unnecessary ownership transfer. One borrowed interface accepts owned text and a literal.

## Task answers

### Task 1: Predict and explain

Identify which arguments are copied and which are borrowed.

**Written answer.** `double(original)` receives a copy of the `i32` 7, which is why `original` is still 7 afterwards. `starts_with_p(&owned)` borrows the `String` as `&str` through deref coercion, and `starts_with_p("apple")` passes a string literal, which is already a borrowed `&'static str`. Nothing is moved.

**Why it is correct.** `i32` implements `Copy`, so passing it by value duplicates the bits. `String` does not, so the function takes a reference; `owned` keeps ownership and the final `assert_eq!(owned, "pear")` compiles.

**Plausible wrong approach.** Saying `owned` is copied into the function would require a `.clone()` that the code does not contain. Saying `original` is borrowed misses that `double` has a value parameter `value: i32`.

**How to verify.** Change `starts_with_p` to take `text: String` and call it as `starts_with_p(owned)`: the later `assert_eq!(owned, "pear")` is rejected with E0382, borrow of moved value.

### Task 2: Guided modification

Add a function computing a labeled length from &str.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn labeled_length(label: &str, text: &str) -> String {
        format!("{label}: {} bytes", text.len())
    }
    let owned = String::from("pear");
    assert_eq!(labeled_length("fruit", &owned), "fruit: 4 bytes");
    assert_eq!(labeled_length("note", "café"), "note: 5 bytes");
    assert_eq!(owned, "pear");
    Ok(())
}
```

**Observe:** pear is labeled as 4 bytes, café as 5 bytes, and the owned String is still usable afterwards.

Both parameters are `&str`, so the function accepts literals and borrowed Strings alike and needs no ownership. The label says bytes because `len` counts UTF-8 bytes, which is why the accented word reports 5.

**Plausible wrong approach.** Labeling the result as characters while still calling `len` gives `note: 5 characters` for the four-letter café; the café fixture exposes the mismatch.

**How to verify.** Run the block. Change the parameter to `text: String` and the `&owned` call fails with E0308, expected `String`, found `&String`.

### Task 3: Independent construction

Write a pure rectangle-area function with a documented valid range.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    /// Area of a rectangle; both sides must be at most 65_535.
    fn area(width: u32, height: u32) -> u32 {
        assert!(width <= 65_535 && height <= 65_535);
        width * height
    }
    assert_eq!(area(3, 4), 12);
    assert_eq!(area(0, 9), 0);
    assert_eq!(area(65_535, 65_535), 4_294_836_225);
    Ok(())
}
```

**Observe:** 3 by 4 gives 12, a zero side gives 0, and the documented maximum still fits in u32.

The documented range is exactly the one whose product fits in u32, and the function checks it, so callers cannot reach an overflow.

### Task 4: Diagnose a defect

Diagnose an accidental semicolon on the final return expression.

**Written answer.** The defect is `fn double(value: i32) -> i32 { value * 2; }`. rustc reports E0308, mismatched types: expected `i32`, found `()`, and points at the body with the help text `remove this semicolon to return this value`. Delete the semicolon so `value * 2` is the block's tail expression.

**Why it is correct.** A semicolon turns an expression into a statement whose value is discarded, so the block ends with the unit value `()`. The declared return type `i32` makes the compiler reject the mismatch before anything runs.

**Plausible wrong approach.** Adding `return value * 2;` also compiles and is not wrong, but adding `-> ()` or removing the return type to silence the error changes the contract and breaks every caller that uses the result.

**How to verify.** Compile the defective version and read E0308 with the semicolon hint. Remove the semicolon and `assert_eq!(double(original), 14)` passes again.

### Task 5: Boundary evidence

Test empty text and zero dimensions.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn labeled_length(text: &str) -> String {
        format!("length={}", text.len())
    }
    fn area(width: u32, height: u32) -> u32 {
        width * height
    }
    assert_eq!(labeled_length(""), "length=0");
    assert_eq!(labeled_length(&String::new()), "length=0");
    assert_eq!(area(0, 0), 0);
    assert_eq!(area(0, 65_535), 0);
    assert_eq!(area(65_535, 0), 0);
    Ok(())
}
```

**Observe:** Empty text, as a literal or an empty String, has length 0, and any rectangle with a zero side has area 0.

An empty `&str` is a valid input of length 0, not an error. A zero width or height is inside the documented range of the task 3 contract, and the product is 0 on either side, including next to the largest allowed side.

**Plausible wrong approach.** Treating empty input as invalid with `assert!(!text.is_empty())` makes the function panic on a legitimate empty field instead of reporting length 0.

**How to verify.** Run the block; all five checks pass. Change `area` to return `width + height` and the second area check fails with `left: 65535`.

### Task 6: Transfer and justify

Choose owned or borrowed inputs for an API that stores data after the call.

**Judging criteria.** An API that keeps data after the call should take ownership, as in `fn add(&mut self, name: String)`, so each caller decides whether to move or clone. Taking `&str` and calling `to_string` inside hides the allocation from the caller. A strong answer compares `String`, `&str` and `impl Into<String>` and states one limitation: storing a borrowed `&'a str` ties the container to the caller's data for its whole life.

## Mechanism and diagnostic reasoning

A function should expose accepted inputs, result meaning, mutation and failure. A compact signature cannot tell the whole story, so write the domain contract beside it. Begin with pure computations that return a value; their behavior is easy to test because they do not depend on hidden state.

Rust makes ownership transfer part of an argument type. Passing an integer copies it, while passing an owned String normally moves it. Borrowing can let a function inspect text while leaving ownership with the caller. Choose the signature from the needed capability rather than adding clones until the compiler is quiet.

`fn double(value: i32) -> i32` declares input and output types. A final expression returns its value without a semicolon. `&str` accepts borrowed text, including literals and owned String views.

A reference is not permission to retain data beyond its lifetime. Pure-looking names can hide side effects. Do not clone an entire buffer when a borrow expresses the actual requirement.

## Review before continuing

Rebuild Example B (Accept different text owners) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
