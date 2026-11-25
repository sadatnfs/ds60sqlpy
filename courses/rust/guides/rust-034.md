# rust-034: Unsafe code, FFI and a documented safety argument

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-033`

## Learning objectives

Write a safety argument before any unsafe code and keep unsafe behind a safe API. The central exercise is task 3: Write a safe wrapper specification before considering an unsafe implementation.

## Purpose and mental model

Unsafe permits a small set of operations whose correctness the compiler cannot fully establish. It does not disable every safety rule or turn wrong memory access into valid behavior. Each unsafe block needs an argument covering pointer validity, alignment, initialized length, aliasing and lifetime. Keep the block small and wrap it in a safe interface that enforces those conditions.

Foreign-function interfaces add an ABI contract: layout, calling convention, string encoding, ownership and failure signaling must agree across languages. A successful link does not prove those agreements. The ordinary fixture uses a pointer obtained from a live array and immediately reconstructs a read-only slice under a documented invariant, without calling undeclared native libraries.

## Vocabulary and concepts

**Unsafe operation:** An operation requiring caller-provided safety evidence.

**ABI:** The binary-level calling and layout agreement between compiled components.

**Safety invariant:** The conditions a safe wrapper must preserve around unsafe code.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::slice`. A passing run prints `rust-034: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`as_ptr` borrows an address from live storage. `slice::from_raw_parts` is unsafe because the caller supplies validity and length. A SAFETY comment explains why this exact operation satisfies its preconditions.

**Reading Example A (Reconstruct a bounded borrowed view, code below).** `values.as_ptr()` returns a `*const i32` to the first element. Creating a raw pointer is safe; only dereferencing it, or calling a function that does, requires `unsafe`. `std::slice::from_raw_parts` is an `unsafe fn` because its correctness depends on facts the compiler cannot check about the pointer, the length and what else may touch that memory; the function's documentation lists them under Safety. The `// SAFETY:` comment is the conventional place to argue that each one holds, and Clippy's `undocumented_unsafe_blocks` lint can require it. The `unsafe` block wraps only the one call that needs it. Its result is an ordinary `&[i32]`, so the assertion compares it with a slice literal like any safe borrow.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Reconstruct a bounded borrowed view

The safety proof is tied to the pointer origin and exact length, not merely to the pointer being non-null.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2_i32, 3, 4];
        let pointer = values.as_ptr();
        // SAFETY: pointer comes from this live initialized array; length is exact; no mutation overlaps.
        let view = unsafe { std::slice::from_raw_parts(pointer, values.len()) };
        assert_eq!(view, &[2, 3, 4]);
    }
    println!("rust-034: passed");
    Ok(())
}
```

**Observe:** The reconstructed view matches the live initialized array.

### Example B: Prefer the safe operation when available

Unsafe should be justified by a real boundary, not used because pointer syntax appears advanced.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2, 3, 4];
        let view = &values[..];
        assert_eq!(view.iter().sum::<i32>(), 9);
    }
    println!("rust-034: passed");
    Ok(())
}
```

**Observe:** A normal slice provides the same read contract without a manual safety burden.

## Exercises

1. **Predict and explain.** State every precondition needed by from_raw_parts.

2. **Guided modification.** Reduce the borrowed length while retaining valid initialized storage.

3. **Independent construction.** Write a safe wrapper specification before considering an unsafe implementation.

4. **Diagnose a defect.** Diagnose returning a pointer after its owner is dropped.

5. **Boundary evidence.** Review zero-length and alignment rules without executing undefined behavior.

6. **Transfer and justify.** Design an FFI ownership document stating allocation, release, encoding and error conventions.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Never test undefined behavior by hoping it crashes predictably. A null check is insufficient to prove pointer validity. Panics crossing an incompatible FFI boundary need a deliberate policy.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Reconstruct a bounded borrowed view) before changing anything, and confirm its observation: The reconstructed view matches the live initialized array.
2. Compare Example B (Prefer the safe operation when available) with Example A and name the first line whose behavior differs. Its observation is: A normal slice provides the same read contract without a manual safety burden.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Never test undefined behavior by hoping it crashes predictably.

Tempting approaches to rule out before you compare:

- **Task 1.** Treating a null check as sufficient misses alignment, length, initialization, aliasing and lifetime. A non-null pointer into freed memory satisfies it and is still undefined behavior.
- **Task 2.** Increasing the length beyond `values.len()` to read neighboring memory is undefined behavior even if a run happens to print plausible numbers.
- **Task 5.** Passing `std::ptr::null()` as the pointer of an empty slice, on the reasoning that nothing is read, is undefined behavior, and dereferencing a misaligned `*const u64` to see what happens is undefined behavior too.

## Self-check and next step

What must be true of the pointer and length passed to `from_raw_parts` in Example A, and which of those facts does the compiler check? Why does Example B prefer an ordinary slice for the same read? Rewrite Example A's `SAFETY` comment for a pointer that came from a foreign function instead of a live local array.

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `std::slice::from_raw_parts` documentation](https://doc.rust-lang.org/std/slice/fn.from_raw_parts.html) for the exact safety preconditions the `SAFETY` comment must establish. The broader reference is [https://doc.rust-lang.org/nomicon/](https://doc.rust-lang.org/nomicon/).

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-034: Unsafe code, FFI and a documented safety argument.
Read courses/rust/guides/rust-034.md and courses/rust/lessons/rust-034.rs. Prerequisites: rust-033.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-034_solution.rs and
courses/rust/solutions/rust-034_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
