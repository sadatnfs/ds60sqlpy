# rust-001: explanation and comparison

Executable reference: [rust-001_solution.rs](rust-001_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Check a greeting:** The explicit check connects a value to its expected observation. Hello, Rust appears before the lesson marker.

**Calculate instead of copying output:** A second check rejects a plausible wrong operator rather than merely confirming that printing works. The calculated capacity is 24, while addition would give 10.

## Task answers

### Task 1: Predict and explain

Predict the greeting and final marker order.

**Written answer.** Only two statements print. Example A's `println!("{greeting}")` writes `Hello, Rust`; Example B and the `Task 3` block only assert; the last statement prints `rust-001: passed`. So stdout is exactly `Hello, Rust` followed by the marker line.

**Why it is correct.** `main` runs its statements top to bottom, and a passing `assert_eq!` or `assert_ne!` produces no output. The seat count 24 and the shelf capacity are compared, never printed, so neither number can appear.

**Plausible wrong approach.** Predicting a confirmation line after each assertion, or the value 24 in the output, treats a check as a print. Predicting the marker first ignores that its `println!` is the final statement before `Ok(())`.

**How to verify.** Run the reference and compare stdout with the two-line prediction. Then change the expected literal in Example A to `"Hello, rust"`: the run panics with an `assert_eq!` failure showing both strings and prints nothing, because the assertion sits before the greeting's `println!`.

### Task 2: Guided modification

Change the greeting and keep its expected value independent.

**Written answer.** Edit the binding to `let greeting = "Hi, Ferris";` and type the expected literal into the check by hand: `assert_eq!(greeting, "Hi, Ferris");`. The two sides come from two separate sources, the code and the requirement.

**Why it is correct.** Because the expected value is written from the requirement rather than read back from `greeting`, a typo in the binding makes the two strings differ and the program panics before printing a wrong greeting.

**Plausible wrong approach.** Writing `let expected = greeting; assert_eq!(greeting, expected);` compares the binding with itself. It passes for `"Hi, Feris"` or any other text, so the check can never reject a mistake.

**How to verify.** Misspell only the binding as `"Hi, Feris"` and run: the panic shows `left: "Hi, Feris"` and `right: "Hi, Ferris"`, and no greeting or marker is printed. Fix the spelling and both lines appear.

### Task 3: Independent construction

Compute the capacity of three shelves with eight books each.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Plausible wrong approach.** Writing `let capacity = 24;` and asserting 24 copies the answer instead of computing it, so the check would still pass if the operator were wrong. Writing `shelves + books_per_shelf` instead gives 11, which this assertion does reject.

**How to verify.** Add Example B's style of second check, `assert_ne!(capacity, shelves + books_per_shelf);`, comparing 24 with 11. Then swap `*` for `+` temporarily: the run panics with `left: 11` and `right: 24` before `rust-001: passed`.

### Task 4: Diagnose a defect

Remove a closing brace temporarily and classify the compiler diagnostic.

**Written answer.** Delete the `}` that closes the `Task 3` block. rustc stops with `error: this file contains an unclosed delimiter` and labels the unmatched `{`. This is a compile-time syntax diagnostic: no executable is built, so not even `Hello, Rust` appears.

**Why it is correct.** The parser must pair every delimiter before type checking or code generation can start. A panic, by contrast, happens while the program runs and would follow any earlier output such as the greeting.

**Plausible wrong approach.** Classifying it as a runtime crash because the run failed confuses the two kinds of evidence. A panic prints `thread 'main' panicked` after `Hello, Rust`; here nothing ran. Restoring a brace in a different place can also compile while moving the marker `println!` into the wrong block.

**How to verify.** Run with the brace missing: the output is a compiler error mentioning an unclosed delimiter and contains no program output. Restore the brace in its original position and the greeting and marker print again.

### Task 5: Boundary evidence

Check zero shelves and one shelf.

**Written answer.** Wrap the formula as `fn capacity(shelves: u32, books_per_shelf: u32) -> u32 { shelves * books_per_shelf }` and check `assert_eq!(capacity(0, 8), 0);` and `assert_eq!(capacity(1, 8), 8);`.

**Why it is correct.** Zero shelves hold zero books whatever the per-shelf number, and one shelf holds exactly one shelf's worth. Multiplication gives both results, so these two fixtures pin the formula at its smallest inputs.

**Plausible wrong approach.** Using addition, `shelves + books_per_shelf`, claims an empty bookcase holds 8 books and a single shelf holds 9. Testing only the three-shelf case would catch that too, but would not show that an empty bookcase is handled.

**How to verify.** Both assertions pass silently and `rust-001: passed` prints. Swap `*` for `+` and the zero-shelf check panics with `left: 8` and `right: 0`.

### Task 6: Transfer and justify

Model a three-level capacity calculation and explain every intermediate value.

**Written answer.** Model a library: `let floors = 2; let rooms_per_floor = 3; let shelves_per_room = 4; let books_per_shelf = 8;` then `let rooms = floors * rooms_per_floor;` (6), `let shelves = rooms * shelves_per_room;` (24) and `let books = shelves * books_per_shelf;` (192).

**Why it is correct.** Each binding names one unit, so each intermediate value has its own hand-worked expectation: 2 times 3 rooms, 6 times 4 shelves, 24 times 8 books. A limitation is that every floor and room must be identical; irregular rooms need a sum over a list instead.

**Plausible wrong approach.** Skipping a level, for example `floors * shelves_per_room * books_per_shelf`, multiplies floors by a per-room figure and yields 64. Writing the whole product as one literal expression hides which level was dropped.

**How to verify.** Assert every level: `assert_eq!(rooms, 6); assert_eq!(shelves, 24); assert_eq!(books, 192);`. Change `rooms_per_floor` to 5 and the first failing check reports `left: 10`, naming the level that changed.

## Mechanism and diagnostic reasoning

Rust checks source before producing a native executable. A compiler diagnostic means the program has not reached its entrypoint. A panic during execution means an operation violated a checked assumption. Successful output means only the path that actually ran completed. Keep these forms of evidence separate when learning to diagnose a program.

The classroom supplies a pinned compiler and Arrow library inside Linux Docker. The browser sends a single source file, not a Cargo project or arbitrary shell command. Start by tracing a tiny calculation and independently checking its result. This builds the habit of distinguishing observed behavior from a printed success claim.

`fn main` declares the entry function. `let` introduces a binding. `println!` is a macro, indicated by the exclamation mark. `assert_eq!` compares actual and expected values and panics on disagreement. A semicolon turns an expression into a statement whose value is discarded.

A compiler success does not establish business correctness. Do not replace a failing assertion with a success print. The Result-returning main wrapper is scaffolding for later error propagation; its full meaning is taught in the error chapters.

## Review before continuing

Rebuild Example B (Calculate instead of copying output) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
