# cuda-056: Asynchronous copies, barriers and software pipelines

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-019`, `cuda-028`, `cuda-036`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement a two-stage asynchronous copy pipeline with correct tails and explain whether the overlap helped.

Work through *Asynchronous copies, barriers and software pipelines* with the concrete cases below. Finish with this evidence:
correct tails, synchronization checks and a measured explanation of whether overlap helped. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Within-GPU asynchronous copy mechanisms can move tiles from global to shared storage while other work proceeds, subject to architecture, alignment and API requirements. These are different from host-to-device asynchronous transfers. A producer commits a stage, a consumer waits for its completion, and the stage cannot be overwritten until consumption finishes. Double buffering alternates two storage slots but does not remove these dependencies. Hardware-accelerated paths and fallback behavior must be checked for the exact toolchain and device. Correct tail loading and barrier participation remain essential even when the happy path overlaps efficiently.

### Key terms

- **memcpy_async:** A cooperative copy from global to shared memory that can proceed while threads do other work.
- **cuda::pipeline:** A libcu++ object that tracks stages of asynchronous copies through acquire, commit, wait and release.
- **Asynchronous barrier:** A `cuda::barrier` that separates arriving from waiting so threads can work between the two.
- **Software pipelining:** Overlapping the load of the next tile with computation on the current tile using several buffers.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-056_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-056_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

For three tiles using two slots, tile 0 loads slot A and tile 1 loads slot B. Tile 2 may reuse A only after computation using tile 0 finishes. Copy completion permits reading; consumer completion permits reuse. Those are two different milestones.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
states = ["free", "copying", "ready", "consuming", "done", "free"]
assert states.index("ready") < states.index("consuming") < states.index("done")
assert 16 % 16 == 0 and (16 + 4) % 16 != 0
print({"slot_lifetime": states, "offset_address_aligned_to_16": False})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'slot_lifetime': ['free', 'copying', 'ready', 'consuming', 'done', 'free'], 'offset_address_aligned_to_16': False}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A 16-byte transfer requirement does not mean an arbitrary pointer cast creates 16-byte alignment. An address offset by four bytes from an aligned base is still misaligned for that contract. Use valid alignment/layout or a supported fallback, and test the final partial tile separately.

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

List the lifetime states of one tile slot.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A consumer reads immediately after initiating a copy. Diagnose it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What happens to a partial final tile?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose whether to add asynchronous staging.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **initiating a copy makes its destination immediately readable. .**

For the concrete failure exercise, a consumer reads immediately after initiating a copy. Diagnose it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-056_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [Asynchronous copies](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/async-copies.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-056: Asynchronous copies, barriers and software pipelines.
Read courses/cuda/cpp/guides/cuda-056.md and courses/cuda/cpp/lessons/cuda-056.md.
Direct prerequisites: `cuda-019`, `cuda-028`, `cuda-036`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-056_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-056_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
