# rust-035: Memory layout, allocation and performance evidence

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-034`

## Learning objectives

Measure memory and performance with evidence instead of assumptions about allocation. The central exercise is task 3: Write a benchmark plan comparing repeated clone with borrowed processing.

## Purpose and mental model

Rust exposes enough control to optimize data layout and allocation, but correctness and a workload model come first. Contiguous arrays can improve locality for column scans, while pointer-heavy structures may incur indirection. Copying a small value can be cheaper than managing shared ownership; cloning a large buffer can dominate a pipeline.

Measure allocations and throughput under a realistic workload, and retain identical semantics across implementations. A single elapsed-time sample is weak evidence. The classroom uses deterministic size and operation observations, then prepares the learner to design an external benchmark. Representation details should not leak into a stable API unless the contract requires them.

## Vocabulary and concepts

**Inline size:** The bytes occupied directly by a value representation.

**Locality:** Access patterns that reuse nearby memory effectively.

**Allocation profile:** Evidence about the number and size of allocated resources.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::mem`. A passing run prints `rust-035: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

size_of measures a type's inline representation, not every allocation reachable from it. Vec capacity is separate allocated storage. reserve can reduce reallocations without changing the algorithmic cost of shifting or sorting.

**Reading Example A (Distinguish handle size from owned data, code below).** `String::from("a")` and `"x".repeat(1000)` both produce a `String`, so both values have the same type and therefore the same inline representation: a pointer to a heap buffer, a capacity and a length. `std::mem::size_of_val(&small)` takes a reference and reports the size in bytes of the value it points to. For a `String` that is the size of those three fields, which depends on the target's pointer width and not on the text. The heap buffers are separate allocations that the strings own, so they do not appear in this number. `len()` reads the length field, which counts bytes of text. `repeat` computes the final length first and allocates one buffer large enough for every copy, so the long string costs one allocation, not a thousand. `size_of_val` is also useful for unsized values such as slices, where `size_of::<T>()` cannot be written; for a `String`, both give the same answer.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Distinguish handle size from owned data

Inline size is not a total retained-memory measurement.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let small = String::from("a");
        let large = "x".repeat(1000);
        assert_eq!(std::mem::size_of_val(&small), std::mem::size_of_val(&large));
        assert_ne!(small.len(), large.len());
    }
    println!("rust-035: passed");
    Ok(())
}
```

**Observe:** String handle size is equal while the owned text lengths differ.

### Example B: Prepare capacity without inventing elements

Reserved capacity is a resource decision, not part of the logical dataset.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut values = Vec::with_capacity(100);
        values.extend(0..10);
        assert_eq!(values.len(), 10);
        assert!(values.capacity() >= 100);
        assert_eq!(values.iter().sum::<i32>(), 45);
    }
    println!("rust-035: passed");
    Ok(())
}
```

**Observe:** Only ten initialized elements participate in the sum.

## Exercises

1. **Predict and explain.** Separate inline handles from their owned allocations.

2. **Guided modification.** Compare vector lengths after different reserve calls.

3. **Independent construction.** Write a benchmark plan comparing repeated clone with borrowed processing.

4. **Diagnose a defect.** Diagnose measuring size_of as total memory retained by nested objects.

5. **Boundary evidence.** Test empty and large inputs with the same correctness oracle.

6. **Transfer and justify.** Choose a layout for repeated column scans and explain locality, ownership and update tradeoffs.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Benchmarking different validation or ordering semantics is invalid. Size and alignment can vary by target. Do not use unsafe layout assumptions to replace an actual profiling result.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Distinguish handle size from owned data) before changing anything, and confirm its observation: String handle size is equal while the owned text lengths differ.
2. Compare Example B (Prepare capacity without inventing elements) with Example A and name the first line whose behavior differs. Its observation is: Only ten initialized elements participate in the sum.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Benchmarking different validation or ordering semantics is invalid.

Tempting approaches to rule out before you compare:

- **Task 1.** Concluding that the two strings use the same memory because the sizes match ignores the heap buffers entirely.
- **Task 2.** Asserting `exact.capacity() == 10` relies on an allocator detail that the documentation does not promise; only `>= 10` is guaranteed.
- **Task 5.** Testing only the large input for speed and the small input for correctness lets a version that overflows on large data pass both checks.

## Self-check and next step

Why does `size_of_val` report the same size for a one-byte and a thousand-byte `String`? After `Vec::with_capacity(100)` and `extend(0..10)`, what are `len()` and the sum, and why are the other reserved slots not elements? What would an allocation count show about reserving capacity that a single wall-clock timing might hide?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `std::mem::size_of` documentation](https://doc.rust-lang.org/std/mem/fn.size_of.html) for how layout and niche optimization set inline size.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-035: Memory layout, allocation and performance evidence.
Read courses/rust/guides/rust-035.md and courses/rust/lessons/rust-035.rs. Prerequisites: rust-034.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-035_solution.rs and
courses/rust/solutions/rust-035_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
