# rust-040: Compute kernels, filtering and row selection

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-039`

## Learning objectives

Filter and take Arrow rows with compute kernels so every column stays aligned. The central exercise is task 3: Filter every column of a batch consistently under one row mask.

## Purpose and mental model

Arrow compute kernels operate on arrays while respecting their logical representation. A Boolean mask selects rows; take selects positions by an index array. These are different operations with different output ordering. Filtering normally preserves the order of admitted rows, while take can repeat or reorder positions.

Type erasure means a kernel can return ArrayRef. Inspect or validate the logical type before downcasting to a concrete array. An unwrap can be justified only by a nearby known kernel/type contract in a controlled fixture. Production generic code should return a useful error for an unexpected type. Preserve null and index bounds policies explicitly.

## Vocabulary and concepts

**Kernel:** A reusable array computation.

**Filter mask:** A Boolean decision per input row.

**Take indices:** Positions selecting and potentially reordering rows.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array` and `arrow::compute`. A passing run prints `rust-040: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

compute::filter accepts an array and BooleanArray mask. compute::take selects by integer indices. as_any().downcast_ref recovers a known concrete array after the type contract has been established.

**Reading Example A (Filter with an explicit mask, code below).** `BooleanArray::from(vec![true, false, true])` builds the selection mask, one entry per row of `values`. `arrow::compute::filter(&values, &mask)` is a kernel: it takes any array and a mask and returns a new array containing only the rows whose mask entry is true, in their original order. Because it accepts any array type, its return type is `ArrayRef`, the type-erased `Arc<dyn Array>`. The `?` propagates an `ArrowError` if the kernel rejects its inputs. To read the result as integers, `as_any().downcast_ref::<Int32Array>()` recovers the concrete type; `unwrap` is safe here because filtering an `Int32Array` always yields one. `iter()` then yields `Option<i32>`, which is why the expected values are wrapped in `Some`.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Filter with an explicit mask

The mask expresses one admission decision for every original position.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{BooleanArray, Int32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        let mask = BooleanArray::from(vec![true, false, true]);
        let result = arrow::compute::filter(&values, &mask)?;
        let typed = result.as_any().downcast_ref::<Int32Array>().unwrap();
        assert_eq!(typed.iter().collect::<Vec<_>>(), vec![Some(2), Some(6)]);
    }
    println!("rust-040: passed");
    Ok(())
}
```

**Observe:** Filtering retains two and six in input order.

### Example B: Reorder and repeat with take

A selected row can appear more than once, so cardinality and aggregation assumptions need review.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Int32Array, UInt32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        let indices = UInt32Array::from(vec![2, 0, 2]);
        let result = arrow::compute::take(&values, &indices, None)?;
        let typed = result.as_any().downcast_ref::<Int32Array>().unwrap();
        assert_eq!(typed.iter().collect::<Vec<_>>(), vec![Some(6), Some(2), Some(6)]);
    }
    println!("rust-040: passed");
    Ok(())
}
```

**Observe:** Take repeats and reorders values according to the index sequence.

## Exercises

1. **Predict and explain.** Predict row count and order for both operations.

2. **Guided modification.** Change one mask value and independently derive the result.

3. **Independent construction.** Filter every column of a batch consistently under one row mask.

4. **Diagnose a defect.** Diagnose filtering one column while leaving others unfiltered.

5. **Boundary evidence.** Test empty selection, all-selected rows and checked invalid indices.

6. **Transfer and justify.** Choose filter or take for a sampling procedure and explain duplicate-row consequences.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Downcast failure is possible in generic code. A mask and array must have compatible lengths. A kernel result does not establish a domain-level ordering guarantee unless the operation contract does.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Filter with an explicit mask) before changing anything, and confirm its observation: Filtering retains two and six in input order.
2. Compare Example B (Reorder and repeat with take) with Example A and name the first line whose behavior differs. Its observation is: Take repeats and reorders values according to the index sequence.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Downcast failure is possible in generic code.

Tempting approaches to rule out before you compare:

- **Task 1.** Expecting `take` to deduplicate indices or to keep input order predicts [2, 6] for Example B and misses the repeated row that can double-count an aggregate.
- **Task 2.** Changing only the expected vector and not the mask makes the test check your edit, not the kernel.
- **Task 5.** Calling `take` with `None` options on indices from an untrusted source assumes they were already validated, so an out-of-range index is no longer reported as a handled error.

## Self-check and next step

Why does `filter` in Example A return [2, 6] in input order? In Example B, why does `take` return [6, 2, 6], and what would that repetition do to a sum? How should a sampling contract state each kernel's treatment of a null in the mask or the index array?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `arrow::compute` documentation](https://docs.rs/arrow/60.0.0/arrow/compute/) for `filter`, `take` and their length rules.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-040: Compute kernels, filtering and row selection.
Read courses/rust/guides/rust-040.md and courses/rust/lessons/rust-040.rs. Prerequisites: rust-039.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-040_solution.rs and
courses/rust/solutions/rust-040_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
