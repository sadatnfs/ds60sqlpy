# cuda-044: Second capstone: a streaming numerical service core

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-038`, `cuda-039`, `cuda-040`, `cuda-041`, `cuda-042`, `cuda-043`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Second capstone: a streaming numerical service core* with the concrete cases below. Finish with this evidence:
all outputs match, no chunk is dropped or reused early, memory stays within the budget, and the report separates request latency from throughput. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A streaming compute service needs bounded ownership and backpressure before it needs more streams. Backpressure means producers stop or reject work when the system cannot safely accept another item. A slot moves through states such as free, filling, computing, copying and consumed. Reuse is allowed only after the final consumer completes. Cancellation stops admission and cleans up according to actual completion state; it does not magically cancel every submitted device instruction. This capstone is a bounded local pipeline, not a new network server inside the classroom worker.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-044_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-044_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

With capacity two, submit chunks A and B. Chunk C waits until a slot becomes free. If A finishes compute but its output is still downloading, A's slot is not yet free. A correct queue can process arbitrary many chunks with constant bounded storage by reusing only completed slots.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
states = ["free", "filling", "computing", "copying", "consumed", "free"]
assert states.index("computing") < states.index("consumed")
chunks = [[1, 2], [3], [], [4, 5]]
results = [[2 * x for x in chunk] for chunk in chunks]
assert results == [[2, 4], [6], [], [8, 10]]
print({"reference_results": results, "slot_lifecycle": states})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'reference_results': [[2, 4], [6], [], [8, 10]], 'slot_lifecycle': ['free', 'filling', 'computing', 'copying', 'consumed', 'free']}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A synchronous pipeline has 7 ms latency per chunk. A pipelined version can deliver later chunks every 3 ms while the first still takes roughly 7 ms in the ideal model. Throughput and first-result latency are distinct objectives; reporting only the inter-result interval hides the user's wait.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

Exercises 1 and 2 are guided reconstructions of the worked examples; exercises
3-6 change an input, diagnose a defect, test a boundary and transfer the idea.
For each one, keep the calculation, output, diagram or failure policy you
produce so another reader can compare it with the worked cases. If the hint is
not enough, reread the mechanism paragraph and the bounded CPU assertion.

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Write legal transitions for a two-slot pipeline.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A cancellation handler immediately frees all device buffers. What is missing?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should happen to a zero-length chunk?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Define capstone acceptance beyond timing.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **maximizing batch size automatically gives the best user experience.**

For the concrete failure exercise, a cancellation handler immediately frees all device buffers. What is missing?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-044_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-044: Second capstone: a streaming numerical service core.
Read courses/cuda/cpp/guides/cuda-044.md and courses/cuda/cpp/lessons/cuda-044.md.
Direct prerequisites: `cuda-038`, `cuda-039`, `cuda-040`, `cuda-041`, `cuda-042`, `cuda-043`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-044_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-044_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
