# rust-008: Ownership, moves and explicit cloning

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-007`

## Learning objectives

Predict moves and clones and transfer ownership into and out of functions. The central exercise is task 3: Write a function taking and returning an owned String.

## Purpose and mental model

Every owned value has a responsibility for releasing its resources. Moving a non-Copy value transfers that responsibility to another binding or operation. The old binding can no longer be used as though it still owns the value. This prevents accidental double release and many use-after-free errors before execution.

Clone explicitly asks for a value-level duplication defined by the type. Cloning a String duplicates its text storage; cloning an Arc later duplicates shared ownership rather than deep-copying its contents. Copy is a stricter implicit duplication capability used by suitable simple types. Learn the semantic distinction instead of assuming every assignment copies everything.

## Vocabulary and concepts

**Owner:** The value responsible for a resource lifetime.

**Move:** Transfer of ownership that invalidates the prior use path.

**Clone:** An explicit type-defined duplication operation.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-008: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Assignment of String moves ownership. `.clone()` requests the type's duplication behavior. A function taking String owns its argument and may retain or release it. Returning the String transfers ownership back.

**Reading Example A (Move ownership to a new binding, code below).** `String::from("pear")` creates a value with three parts on the stack, a pointer, a length and a capacity, plus a heap buffer holding the four bytes. `first` owns that value, which means `first` is responsible for freeing the buffer when it goes out of scope. `let second = first;` moves the three stack fields into `second` and marks `first` as moved. The heap buffer is not copied, and there is still exactly one owner, so the buffer is freed exactly once, when `second` goes out of scope at the end of the block. The comment marks the line to try: a use such as `println!("{first}")` after the move is rejected at compile time with E0382, borrow of moved value, and the diagnostic points back at the move. Nothing runs at run time to enforce this. The compiler tracks ownership statically, so a moved-from binding costs nothing and simply cannot be read.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Move ownership to a new binding

The reference intentionally does not compile an invalid old-binding access; the practice task asks the learner to inspect that diagnostic separately.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let first = String::from("pear");
        let second = first;
        assert_eq!(second, "pear");
        // Using first here would be a compile error: ownership moved.
    }
    println!("rust-008: passed");
    Ok(())
}
```

**Observe:** The new binding owns the text.

### Example B: Clone only when two owners are needed

The explicit clone makes the allocation and independent ownership decision visible.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let first = String::from("pear");
        let mut second = first.clone();
        second.push('s');
        assert_eq!(first, "pear");
        assert_eq!(second, "pears");
    }
    println!("rust-008: passed");
    Ok(())
}
```

**Observe:** The cloned String can change independently.

## Exercises

1. **Predict and explain.** Draw ownership before and after the move.

2. **Guided modification.** Temporarily read first after its move and preserve the compiler diagnostic.

3. **Independent construction.** Write a function taking and returning an owned String.

4. **Diagnose a defect.** Diagnose adding clones everywhere instead of choosing a borrowed interface.

5. **Boundary evidence.** Compare String movement with copying an i32.

6. **Transfer and justify.** Explain whether a function should borrow, clone or take ownership when retaining data for later use.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Clone does not universally mean deep copy. A move can be optimized without changing its ownership semantics. Compiler rejection of a use-after-move is useful evidence, not an obstacle to suppress.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Move ownership to a new binding) before changing anything, and confirm its observation: The new binding owns the text.
2. Compare Example B (Clone only when two owners are needed) with Example A and name the first line whose behavior differs. Its observation is: The cloned String can change independently.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Clone does not universally mean deep copy.

Tempting approaches to rule out before you compare:

- **Task 1.** Drawing two arrows to the buffer, one from each name, describes a double free waiting to happen. Drawing two buffers describes `clone`, which Example B does explicitly.
- **Task 2.** Accepting the suggested `.clone()` reflexively makes the error disappear but changes the design to two buffers; if only reading was needed, borrowing with `let second = &first;` is the honest fix.
- **Task 5.** Assuming `let moved = name;` copies the text predicts a new address after the move; the address equality check shows it does not.

## Self-check and next step

After `let second = first;` with `first: String`, which binding owns the heap buffer, and what does the compiler report if you read `first` afterwards? Why does the same assignment between two `i32` bindings leave both usable? When is `clone` the right repair, and when does a borrow state the requirement better?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 4.1 What is Ownership?](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) for moves, `Clone` and `Copy`.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-008: Ownership, moves and explicit cloning.
Read courses/rust/guides/rust-008.md and courses/rust/lessons/rust-008.rs. Prerequisites: rust-007.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-008_solution.rs and
courses/rust/solutions/rust-008_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
