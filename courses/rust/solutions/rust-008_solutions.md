# rust-008: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-008_solution.rs](rust-008_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Move ownership to a new binding:** The reference intentionally does not compile an invalid old-binding access; the practice task asks the learner to inspect that diagnostic separately. The new binding owns the text.

**Clone only when two owners are needed:** The explicit clone makes the allocation and independent ownership decision visible. The cloned String can change independently.

## Task answers

### Task 1: Predict and explain

Draw ownership before and after the move.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The reference intentionally does not compile an invalid old-binding access; the practice task asks the learner to inspect that diagnostic separately. The new binding owns the text.

### Task 2: Guided modification

Temporarily read first after its move and preserve the compiler diagnostic.

No separate reference answer has been written for this task. Start from Example B: The explicit clone makes the allocation and independent ownership decision visible. The cloned String can change independently.

### Task 3: Independent construction

Write a function taking and returning an owned String.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Clone does not universally mean deep copy. A move can be optimized without changing its ownership semantics. Compiler rejection of a use-after-move is useful evidence, not an obstacle to suppress.

### Task 5: Boundary evidence

Compare String movement with copying an i32.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Move ownership to a new binding) and Example B (Clone only when two owners are needed).

### Task 6: Transfer and justify

Explain whether a function should borrow, clone or take ownership when retaining data for later use.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Owner**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Every owned value has a responsibility for releasing its resources. Moving a non-Copy value transfers that responsibility to another binding or operation. The old binding can no longer be used as though it still owns the value. This prevents accidental double release and many use-after-free errors before execution.

Clone explicitly asks for a value-level duplication defined by the type. Cloning a String duplicates its text storage; cloning an Arc later duplicates shared ownership rather than deep-copying its contents. Copy is a stricter implicit duplication capability used by suitable simple types. Learn the semantic distinction instead of assuming every assignment copies everything.

Assignment of String moves ownership. `.clone()` requests the type's duplication behavior. A function taking String owns its argument and may retain or release it. Returning the String transfers ownership back.

Clone does not universally mean deep copy. A move can be optimized without changing its ownership semantics. Compiler rejection of a use-after-move is useful evidence, not an obstacle to suppress.

## Review before continuing

Run the reference and confirm that it prints `rust-008: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
