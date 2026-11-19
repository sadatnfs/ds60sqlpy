# rust-001: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-001_solution.rs](rust-001_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Check a greeting:** The explicit check connects a value to its expected observation. Hello, Rust appears before the lesson marker.

**Calculate instead of copying output:** A second check rejects a plausible wrong operator rather than merely confirming that printing works. The calculated capacity is 24, while addition would give 10.

## Task answers

### Task 1: Predict and explain

Predict the greeting and final marker order.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The explicit check connects a value to its expected observation. Hello, Rust appears before the lesson marker.

### Task 2: Guided modification

Change the greeting and keep its expected value independent.

No separate reference answer has been written for this task. Start from Example B: A second check rejects a plausible wrong operator rather than merely confirming that printing works. The calculated capacity is 24, while addition would give 10.

### Task 3: Independent construction

Compute the capacity of three shelves with eight books each.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let shelves = 3;
    let books_per_shelf = 8;
    let capacity = shelves * books_per_shelf;
    assert_eq!(capacity, 24);
    Ok(())
}
```

**Observe:** Three shelves of eight books hold 24 books.

The product is written as a calculation, and assert_eq! compares it with 24, a value worked out independently.

### Task 4: Diagnose a defect

Remove a closing brace temporarily and classify the compiler diagnostic.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A compiler success does not establish business correctness. Do not replace a failing assertion with a success print. The Result-returning main wrapper is scaffolding for later error propagation; its full meaning is taught in the error chapters.

### Task 5: Boundary evidence

Check zero shelves and one shelf.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Check a greeting) and Example B (Calculate instead of copying output).

### Task 6: Transfer and justify

Model a three-level capacity calculation and explain every intermediate value.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Compiler**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Rust checks source before producing a native executable. A compiler diagnostic means the program has not reached its entrypoint. A panic during execution means an operation violated a checked assumption. Successful output means only the path that actually ran completed. Keep these forms of evidence separate when learning to diagnose a program.

The classroom supplies a pinned compiler and Arrow library inside Linux Docker. The browser sends a single source file, not a Cargo project or arbitrary shell command. Start by tracing a tiny calculation and independently checking its result. This builds the habit of distinguishing observed behavior from a printed success claim.

`fn main` declares the entry function. `let` introduces a binding. `println!` is a macro, indicated by the exclamation mark. `assert_eq!` compares actual and expected values and panics on disagreement. A semicolon turns an expression into a statement whose value is discarded.

A compiler success does not establish business correctness. Do not replace a failing assertion with a success print. The Result-returning main wrapper is scaffolding for later error propagation; its full meaning is taught in the error chapters.

## Review before continuing

Run the reference and confirm that it prints `rust-001: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
