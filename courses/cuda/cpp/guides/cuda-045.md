# cuda-045: CCCL, Thrust and CUB before writing everything by hand

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-020`, `cuda-021`, `cuda-022`, `cuda-039`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Compare a Thrust or CUB primitive against a handwritten kernel and justify the library or custom choice.

**Scope:** Standard parallel algorithms, execution policies, temporary storage, iterators, ownership and custom operators.

**Evidence to produce:** Equivalent semantics, stated temporary-memory needs and a justified library/custom decision.

## Purpose, vocabulary and mental model

CUDA Core Compute Libraries bring maintained building blocks such as Thrust algorithms, CUB primitives and CUDA-oriented standard-library facilities. Their abstractions do not remove ownership, stream or temporary-storage obligations. Prefer a tested library primitive when it matches semantics, and keep a handwritten version as a learning baseline or for a demonstrated special requirement. Some primitive interfaces separate workspace-size queries from execution; read the pinned interface rather than guessing. Iterator adapters can avoid materializing intermediate arrays, but they must preserve valid lifetimes and access patterns.

### Key terms

- **Thrust:** A C++ template library of parallel algorithms, such as sort and reduce, over host and device containers.
- **CUB:** A CUDA library of block-level, warp-level and device-wide primitives with explicit temporary storage.
- **Temporary storage query:** A first CUB call with a null workspace pointer that returns the number of bytes the algorithm needs.
- **Execution policy:** An argument such as `thrust::cuda::par.on(stream)` that selects where and on which stream a Thrust algorithm runs.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-045_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-045_cpu.py
```

## Worked example 1: trace the mechanism

Transform \([1,2,3,4]\) by squaring and sum, obtaining 30. A fused transform-reduce can avoid a separate \([1,4,9,16]\) allocation when its interface supports the desired operation. The mathematical result is the same; the memory and scheduling behavior differ.

**Why:** 1 + 4 + 9 + 16 = 30, and fusion avoids storing [1, 4, 9, 16].

```python
values = [1, 2, 3, 4]
assert sum(x * x for x in values) == 30
selected = [x for x in [5, 2, 5, 1] if x >= 5]
assert selected == [5, 5]
print({"transform_reduce_reference": 30, "stable_selection": selected})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'transform_reduce_reference': 30, 'stable_selection': [5, 5]}
```

**Check:** The reference asserts the sum of squares is 30.

## Worked example 2: change a meaningful condition

Stable filtering \([5,2,5,1]\) for values at least five returns \([5,5]\). Sorting before filtering also retains the two fives here, but generally changes order. Choose the algorithm according to semantic requirements, not merely the nearest familiar function name.

**Why:** Stable filtering of [5, 2, 5, 1] returns [5, 5] with original order preserved.

**Check:** Test a fixture with distinct survivors such as [7, 2, 5] and confirm order [7, 5].

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Express squaring and summing of [1, 2, 3, 4] as one transform-reduce call.

**Trap to avoid:** Materializing the squares then reducing is correct but allocates and reads an extra array.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Use a stable selection keeping values at least 5 in input order.

**Trap to avoid:** Sorting first passes this fixture but reorders survivors in general.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compare reduce and transform-reduce for sum of squares.

**Trap to avoid:** Claiming the results differ because the algorithms differ confuses implementation with value.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why must a library stream argument be deliberate?

**Trap to avoid:** Leaving the default stream can add hidden synchronization with other streams.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What is the empty sum-of-squares identity?

**Trap to avoid:** Passing the first element as initial value fails when no element exists.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

State when a custom reduction is justified.

**Trap to avoid:** Writing one to avoid reading documentation duplicates tested code with new bugs.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Library calls remove the need to understand allocation, synchronization or data layout.** Libraries implement the algorithm, but the caller still owns inputs, outputs, temporary storage, stream choice and layout. CUB primitives ask you to query and allocate temporary storage, Thrust policies decide where work runs, and a call on the wrong stream races with other work. Worked example 2 shows semantics matter too: sorting before filtering changes order, so pick the primitive that matches the contract. Worked example 1 makes the memory point concrete: a fused transform-reduce sums the squares of [1,2,3,4] to 30 without storing the intermediate array [1,4,9,16] in device memory.

## Self-check, retrieval and transfer

1. Why can transform-reduce use less memory than transform followed by reduce?
2. What is the sum of squares of an empty input?
3. Why is a library stream argument a correctness choice?

Short answers are in the [separate explanations](../solutions/cuda-045_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Core Compute Libraries](https://nvidia.github.io/cccl/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-045: CCCL, Thrust and CUB before writing everything by hand.
Read courses/cuda/cpp/guides/cuda-045.md and courses/cuda/cpp/lessons/cuda-045.md.
Direct prerequisites: `cuda-020`, `cuda-021`, `cuda-022`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-045_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-045_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
