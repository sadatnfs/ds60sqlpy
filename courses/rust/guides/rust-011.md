# rust-011: Slices, arrays and vector growth

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `rust-010`

## Learning objectives

Accept slices instead of owned collections and handle empty input explicitly. The central exercise is task 3: Implement a maximum function accepting a slice and returning Option.

## Purpose and mental model

An array has a compile-time length as part of its type. A Vec owns a growable allocation. A slice borrows a contiguous region and carries its length without owning that allocation. Accepting &[T] lets a function read arrays and vectors through one interface.

Vector growth can reallocate storage, which explains why a borrow into a vector cannot remain live while a conflicting push changes its allocation. Capacity reserves room but does not create initialized logical elements. Indexing panics outside the valid range; get returns Option when absence is a normal possibility.

## Vocabulary and concepts

**Array:** A fixed-length value whose type includes its length.

**Vector:** An owned growable contiguous sequence.

**Slice:** A borrowed contiguous view carrying a length.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-011: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`[i32; 3]` is an array of exactly three integers. `Vec<i32>` owns a variable-length sequence. `&[i32]` is a borrowed slice. len and capacity describe different properties.

**Reading Example A (Accept arrays and vectors uniformly, code below).** `fn total(values: &[i32]) -> i32` takes a slice, a borrowed pointer and length over contiguous `i32` values, and never learns what owns them. `values.iter().sum()` walks the slice and adds the elements; the return type `i32` tells `sum` what to produce. The three calls pass three different owners. `&[2, 3, 4]` borrows a fixed-size array of type `[i32; 3]`, and the compiler coerces `&[i32; 3]` to `&[i32]`. `&vec![1, 2]` borrows a temporary `Vec<i32>`, and deref coercion turns `&Vec<i32>` into the same slice type. `&[]` borrows an empty array; the slice it produces has length 0, and summing nothing yields 0, the identity for addition, without a special case.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Accept arrays and vectors uniformly

The function requires read access, not a particular allocation strategy.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn total(values: &[i32]) -> i32 {
            values.iter().sum()
        }
        assert_eq!(total(&[2, 3, 4]), 9);
        assert_eq!(total(&vec![1, 2]), 3);
        assert_eq!(total(&[]), 0);
    }
    println!("rust-011: passed");
    Ok(())
}
```

**Observe:** One slice interface accepts several owning representations.

### Example B: Separate capacity from logical elements

The optional lookup exposes absence instead of indexing uninitialized capacity.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut values: Vec<i32> = Vec::with_capacity(10);
        assert_eq!(values.len(), 0);
        assert!(values.capacity() >= 10);
        values.push(7);
        assert_eq!(values.get(0), Some(&7));
        assert_eq!(values.get(1), None);
    }
    println!("rust-011: passed");
    Ok(())
}
```

**Observe:** Reserved storage still contains zero logical elements until push.

## Exercises

1. **Predict and explain.** Identify owner, length and borrowed view in each call.

2. **Guided modification.** Use a subslice and predict its total.

3. **Independent construction.** Implement a maximum function accepting a slice and returning Option.

4. **Diagnose a defect.** Diagnose keeping an element reference live across a conflicting vector push.

5. **Boundary evidence.** Test empty, singleton and out-of-range get cases.

6. **Transfer and justify.** Choose an array, Vec or slice for stored state, function input and fixed-size coordinates.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Capacity is not a valid index limit. A slice does not extend its owner's lifetime. Avoid accepting &Vec when a slice expresses the actual requirement.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Accept arrays and vectors uniformly) before changing anything, and confirm its observation: One slice interface accepts several owning representations.
2. Compare Example B (Separate capacity from logical elements) with Example A and name the first line whose behavior differs. Its observation is: Reserved storage still contains zero logical elements until push.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Capacity is not a valid index limit.

Tempting approaches to rule out before you compare:

- **Task 1.** Treating `with_capacity(10)` as length 10 predicts that `values[5]` is valid. It panics with `index out of bounds: the len is 1 but the index is 5`, because capacity is reserved space, not elements.
- **Task 2.** Reading `1..3` as inclusive predicts 12, which is what `1..=3` gives. Extending the range to `&data[2..5]` panics, because the end 5 is past the length 4.
- **Task 3.** Dropping `.copied()` returns `values.iter().max()`, an `Option<&i32>`, and the signature promising `Option<i32>` is rejected with E0308. Keeping a plain `i32` return with `unwrap_or(i32::MIN)` compiles but makes an empty slice look like a real minimum value.
- **Task 5.** Probing with `one[1]` instead of `get` panics with `index out of bounds: the len is 1 but the index is 1`, which aborts the test rather than recording the out-of-range case.
- **Task 6.** Declaring `fn total(values: &Vec<i32>)` rejects `total(&[2, 3, 4])` with E0308 and cannot take `&data[1..3]`. Storing a point as `Vec<i32>` lets a three-element point appear at run time.

## Self-check and next step

Why can a vector push invalidate an element reference even when capacity seems large enough? After Example B's `Vec::with_capacity(10)`, what are `len()` and the smallest possible `capacity()`, and is index 0 valid before the push? After one push, what does `get(1)` return compared with indexing `[1]`? Why is `&[i32]` a better parameter than `&Vec<i32>`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 8.1 Vectors](https://doc.rust-lang.org/book/ch08-01-vectors.html) for why a push can invalidate an element reference.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-011: Slices, arrays and vector growth.
Read courses/rust/guides/rust-011.md and courses/rust/lessons/rust-011.rs. Prerequisites: rust-010.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-011_solution.rs and
courses/rust/solutions/rust-011_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
