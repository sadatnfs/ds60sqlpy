# rust-008: explanation and comparison

Executable reference: [rust-008_solution.rs](rust-008_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Move ownership to a new binding:** The reference intentionally does not compile an invalid old-binding access; the practice task asks the learner to inspect that diagnostic separately. The new binding owns the text.

**Clone only when two owners are needed:** The explicit clone makes the allocation and independent ownership decision visible. The cloned String can change independently.

## Task answers

### Task 1: Predict and explain

Draw ownership before and after the move.

**Written answer.** Before the move, `first` owns a heap buffer holding `pear`. After `let second = first;`, `second` owns that same buffer and `first` is moved-from: it may not be read, and it will not be dropped. At the end of the block only `second` frees the buffer.

**Why it is correct.** A `String` is a pointer, length and capacity triple that owns its allocation. Assignment copies the triple and transfers ownership, so exactly one owner remains and the buffer is freed exactly once.

**Plausible wrong approach.** Drawing two arrows to the buffer, one from each name, describes a double free waiting to happen. Drawing two buffers describes `clone`, which Example B does explicitly.

**How to verify.** Record `let address = first.as_ptr();` before the move and assert `second.as_ptr() == address` after it: the bytes did not move, only ownership did.

### Task 2: Guided modification

Temporarily read first after its move and preserve the compiler diagnostic.

**Written answer.** Add `assert_eq!(first, "pear");` after `let second = first;`. rustc rejects it with E0382, borrow of moved value: `first`. The diagnostic marks `let second = first;` as `value moved here` and the new line as `value borrowed here after move`, notes that `String` does not implement the `Copy` trait, and suggests `first.clone()`.

**Why it is correct.** After a move the compiler treats `first` as uninitialized, so any read, even a borrow inside `assert_eq!`, is refused at compile time. No program is built, so no runtime check is reached.

**Plausible wrong approach.** Accepting the suggested `.clone()` reflexively makes the error disappear but changes the design to two buffers; if only reading was needed, borrowing with `let second = &first;` is the honest fix.

**How to verify.** Save the full E0382 text in your notes, then delete the temporary line; the reference compiles and `rust-008: passed` prints.

### Task 3: Independent construction

Write a function taking and returning an owned String.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn shout(mut text: String) -> String {
        text.push('!');
        text
    }
    let original = String::from("ready");
    let louder = shout(original);
    assert_eq!(louder, "ready!");
    Ok(())
}
```

**Observe:** The returned String is ready! and ownership has moved into louder.

Taking String by value transfers ownership into the function, which may mutate it and hand ownership back; original can no longer be used.

### Task 4: Diagnose a defect

Diagnose adding clones everywhere instead of choosing a borrowed interface.

**Written answer.** The defect is a reader written as `fn count_p(text: String) -> usize` and called as `count_p(name.clone())` at every site because the caller still needs `name`. Each call allocates and copies the whole buffer just to read it. Change the signature to `fn count_p(text: &str) -> usize` and call `count_p(&name)`.

**Why it is correct.** The function only reads, so a shared borrow states its real requirement. The caller keeps ownership, nothing is copied, and literals can be passed without allocating.

**Plausible wrong approach.** Removing the clones but keeping `text: String` makes the second call E0382, because the first call moved `name`; the clones were hiding a wrong interface, not a missing copy.

**How to verify.** After the change, assert `count_p(&name) == count_p(&name)` twice in a row and that `name` is still the original text, with no `.clone()` anywhere in the file.

### Task 5: Boundary evidence

Compare String movement with copying an i32.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let count = 5_i32;
    let copied = count;
    assert_eq!(count + copied, 10);
    let name = String::from("pear");
    let address = name.as_ptr();
    let moved = name;
    assert_eq!(moved.as_ptr(), address);
    let cloned = moved.clone();
    assert_ne!(cloned.as_ptr(), address);
    assert_eq!(moved, cloned);
    Ok(())
}
```

**Observe:** After copying, both i32 bindings are usable and sum to 10; the moved String keeps its original buffer address, while the clone has a new address with equal contents.

`i32` is `Copy`, so `count` stays valid after assignment. Moving the `String` copies only its pointer, length and capacity, so the heap address is unchanged, whereas `clone` allocates a separate buffer holding the same bytes.

**Plausible wrong approach.** Assuming `let moved = name;` copies the text predicts a new address after the move; the address equality check shows it does not.

**How to verify.** Run the block. Add `assert_eq!(name, "pear");` after the move and compilation fails with E0382, while the equivalent read of `count` compiles.

### Task 6: Transfer and justify

Explain whether a function should borrow, clone or take ownership when retaining data for later use.

**Judging criteria.** Retaining data means the function needs an owner. Taking `String` by value lets a caller move a value it no longer needs at no copying cost, or write `.clone()` when it still needs one, which keeps the cost visible at the call site. Borrowing suits functions that only inspect. A strong answer names who pays for each clone and states one limitation, such as a large buffer cloned on every call by callers that keep their own copy.

## Mechanism and diagnostic reasoning

Every owned value has a responsibility for releasing its resources. Moving a non-Copy value transfers that responsibility to another binding or operation. The old binding can no longer be used as though it still owns the value. This prevents accidental double release and many use-after-free errors before execution.

Clone explicitly asks for a value-level duplication defined by the type. Cloning a String duplicates its text storage; cloning an Arc later duplicates shared ownership rather than deep-copying its contents. Copy is a stricter implicit duplication capability used by suitable simple types. Learn the semantic distinction instead of assuming every assignment copies everything.

Assignment of String moves ownership. `.clone()` requests the type's duplication behavior. A function taking String owns its argument and may retain or release it. Returning the String transfers ownership back.

Clone does not universally mean deep copy. A move can be optimized without changing its ownership semantics. Compiler rejection of a use-after-move is useful evidence, not an obstacle to suppress.

## Review before continuing

Rebuild Example B (Clone only when two owners are needed) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
