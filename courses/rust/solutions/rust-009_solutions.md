# rust-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-009_solution.rs](rust-009_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow more than once:** Both references inspect the same allocation without taking release responsibility. Two readers coexist and the owner remains intact.

**Return a borrowed view:** The function returns a slice whose validity depends on the input owner. The result is a view into caller-owned text, with an explicit empty policy.

## Task answers

### Task 1: Predict and explain

Identify the owner and both readers.

**Written answer.** In Example A, `text` owns the `String` holding `pear`, and `first` and `second` are two `&String` readers of the same allocation. In Example B, `sentence` owns the text, `first_word` receives it as a `&str` parameter, and the returned `&str` is a third view into the same bytes.

**Why it is correct.** `&text` creates a shared reference without moving anything, and any number of shared references may coexist while no mutable borrow exists. The owner alone frees the allocation when its scope ends, which is why `text` can still be compared with `pear` afterwards.

**Plausible wrong approach.** Calling `first` an owner implies `let first = &text;` moved the string. If it had been written `let first = text;`, the next line `let second = &text;` would be rejected with E0382, borrow of moved value.

**How to verify.** Add `assert!(std::ptr::eq(first, second));` and `assert_eq!(first.as_ptr(), text.as_ptr());`. Both pass, showing the two readers and the owner point at one allocation.

### Task 2: Guided modification

Add another read-only inspection without cloning.

**Written answer.** After the existing checks, add `let third = &text; assert!(third.starts_with("pe"));`. `starts_with` takes `&self`, so a third shared borrow is enough and nothing is copied.

**Why it is correct.** Shared borrows can be added freely as long as no code mutates `text` while they are live. The inspection reads the same four bytes the other readers see.

**Plausible wrong approach.** `let third = text.clone();` also passes the check but allocates a second `pear` and inspects the copy, the habit the pitfall warns against. Reaching for `&mut text` instead fails with E0596, because `text` is not declared mutable.

**How to verify.** Add `assert!(std::ptr::eq(third, &text));`; it passes for the borrow and would fail for the clone, whose bytes live elsewhere. The run then ends with `rust-009: passed`.

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

**Plausible wrong approach.** Splitting on a single space, `text.split(' ').last()`, looks equivalent but returns the empty piece after a trailing space: for `"pear apple "` it yields `""` instead of `apple`. `split_whitespace` skips runs of whitespace, so it returns the real last word.

**How to verify.** Add `assert_eq!(last_word("pear apple "), "apple");`, `assert_eq!(last_word("   "), "");` and `assert!(std::ptr::eq(last_word(&sentence), &sentence[5..]));`. The last check proves the result is bytes 5 to 10 of `sentence`, not a new allocation.

### Task 4: Diagnose a defect

Try returning a reference to a local String and explain the compiler rejection.

**Written answer.** Write `fn make_word() -> &str { let word = String::from("pear"); &word }`. rustc first reports E0106, missing lifetime specifier, because there is no input reference to borrow from. Annotating `-> &'static str` then produces E0515: the function returns a reference to data owned by the current function.

**Why it is correct.** `word` is dropped when `make_word` returns, so any reference to it would point at freed memory. A lifetime annotation only describes how long a borrow may be used; it cannot extend the life of the owner.

**Plausible wrong approach.** Accepting the `'static` suggestion as the fix trades E0106 for E0515, since `'static` promises the data lives for the whole program, which a local `String` cannot. The correct change returns ownership: `fn make_word() -> String`.

**How to verify.** Compile each broken version and read E0106, then E0515. Change the signature to `-> String`, return `String::from("pear")`, and `assert_eq!(make_word(), "pear");` passes.

### Task 5: Boundary evidence

Test empty text and a single word.

**Written answer.** Check `first_word("") == ""`, `first_word("   ") == ""` and, for one word, `let single = String::from("pear");` with `first_word(&single) == "pear"` and `last_word(&single) == "pear"`.

**Why it is correct.** `split_whitespace` yields no items for empty or all-space text, so `unwrap_or("")` supplies the documented empty policy. A single word is both the first and the last, so the two functions must agree on it.

**Plausible wrong approach.** Replacing `unwrap_or("")` with `unwrap()` passes every one-word and two-word case but panics on `""` with `called Option::unwrap() on a None value`, so the empty-text check never completes.

**How to verify.** Run the checks and add `assert!(std::ptr::eq(first_word(&single), single.as_str()));`: for a single word the borrowed result covers the whole input. All pass before the marker.

### Task 6: Transfer and justify

Choose a borrowed view or owned result for a parser whose caller may discard the input immediately.

**Written answer.** If the caller may drop the input right after parsing, return owned data: `fn parse_name(line: &str) -> String { line.split_whitespace().next().unwrap_or("").to_string() }`. Keep a borrowed `&str` result for callers that hold the whole input in memory, such as a file read once and scanned many times.

**Why it is correct.** An owned `String` has no lifetime tie to `line`, so the result stays valid after the input buffer is dropped or reused. The cost is one allocation per parsed field, which is the limitation of this choice.

**Plausible wrong approach.** Returning `&str` and then dropping the input fails: `let name = { let line = String::from("pear 3"); first_word(&line) };` is rejected with E0597, `line` does not live long enough, because the view would outlive its owner.

**How to verify.** Write the same block with `parse_name` instead: it compiles and `assert_eq!(name, "pear");` passes. Switching back to `first_word` reproduces E0597.

## Mechanism and diagnostic reasoning

A shared reference grants temporary read access without taking ownership. Several shared borrows can coexist when no conflicting mutation occurs. The owner must remain alive while borrowed data can still be used. Rust's borrow checker tracks these relationships through control flow, often ending a borrow after its last use rather than the end of the entire lexical block.

A borrowed API is useful for inspection, searching and parsing views. It avoids unnecessary allocation while preserving caller ownership. The lifetime constraint is not a runtime timer: it is a compile-time relationship between valid uses. Returning a reference to a local value is invalid because the owner disappears when the function returns.

`&value` creates a shared reference. Dereferencing with `*reference` accesses a referenced scalar when needed. Auto-dereferencing makes many method calls convenient. A return type `&str` must refer to storage owned elsewhere for a sufficient lifetime.

A reference cannot make its owner live longer by declaration alone. Borrow duration follows actual use constraints. Avoid converting every slice to String unless independent ownership is needed.

## Review before continuing

Run the reference and confirm that it prints `rust-009: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
