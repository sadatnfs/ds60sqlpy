# cuda-041: Stream-ordered allocation and memory pools

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-010`, `cuda-028`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Stream-ordered allocation and memory pools* with the concrete cases below. Finish with this evidence:
no use-after-free, correct event ordering and an explained retained-versus-live memory report. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A stream-ordered allocator treats allocation and free as operations with ordering relationships. It can reuse pooled storage efficiently, but the program must still ensure that every access occurs after allocation and before the relevant free/reuse. Cross-stream consumers require explicit dependencies. Memory returned to a pool can remain reserved for reuse, so reported device memory need not immediately drop to zero. Distinguish live application allocations from reserved pool storage. Pool behavior and support are runtime capabilities, not assumptions justified by a function name in documentation.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-041_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-041_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Stream A allocates X, writes X and records ready. Stream B waits, reads X and records done. Before A frees X, A waits for done. This closes both the producer-to-consumer edge and the consumer-to-reuse edge. The first event alone is insufficient for lifetime safety.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
events = [
    "allocate_A",
    "write_A",
    "ready",
    "wait_ready_B",
    "read_B",
    "done",
    "wait_done_A",
    "free_A",
]
assert events.index("read_B") < events.index("free_A")
reserved_mib, live_mib = 64, 0
assert reserved_mib >= live_mib
print({"lifetime_order": events, "reserved_MiB": reserved_mib, "live_MiB": live_mib})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'lifetime_order': ['allocate_A', 'write_A', 'ready', 'wait_ready_B', 'read_B', 'done', 'wait_done_A', 'free_A'], 'reserved_MiB': 64, 'live_MiB': 0}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A pool reserves 64 MiB and the application currently uses 16 MiB. After freeing that allocation back to the pool, live usage may be zero while reservation remains 64 MiB. Calling this a leak without examining ownership and retention policy confuses two different measurements.

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

Name both event dependencies in the cross-stream example.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A buffer is freed immediately after enqueuing work in another stream. Diagnose it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should allocation failure preserve?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a repeated temporary-buffer workload.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **returning memory to a pool means the GPU's visible memory usage must immediately fall to zero. .**

For the concrete failure exercise, a buffer is freed immediately after enqueuing work in another stream. Diagnose it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-041_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [Allocator chapter](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/stream-ordered-memory-allocation.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-041: Stream-ordered allocation and memory pools.
Read courses/cuda/cpp/guides/cuda-041.md and courses/cuda/cpp/lessons/cuda-041.md.
Direct prerequisites: `cuda-010`, `cuda-028`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-041_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-041_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
