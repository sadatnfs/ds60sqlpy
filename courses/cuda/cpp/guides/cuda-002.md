# cuda-002: Meet the hardware without memorizing a product catalog

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-001`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Label a hardware and software map that separates SMs, warps, memory levels and compute capability.

Work through *Meet the hardware without memorizing a product catalog* with the concrete cases below. Finish with this evidence:
labeled hardware/software map and a capability report if hardware exists. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

An SM, or streaming multiprocessor, schedules groups of GPU threads and owns finite execution and storage resources. A block is a cooperating group in your program; it is not a physical processor. Blocks can wait for resources and need not run in index order. Within a block, threads are organized into warps, normally 32 threads in CUDA. A warp issues instructions with a set of participating lanes. Registers hold per-thread working values, shared memory supports block cooperation, and device DRAM holds larger arrays. Copy engines may transfer data while computation proceeds, but concurrency depends on hardware and dependencies. Compute capability identifies a hardware feature family; toolkit version identifies software.

### Key terms

- **Streaming multiprocessor (SM):** A GPU processing unit that schedules warps and owns finite registers, shared memory and execution pipelines.
- **Warp:** A group of 32 threads that an SM schedules together when it issues instructions.
- **Thread block:** A programmer-defined group of threads that runs on one SM and can cooperate through shared memory and barriers.
- **Compute capability:** A version number that identifies a GPU architecture's hardware feature set, separate from the toolkit version.
- **Copy engine:** A hardware unit that moves data between host and device memory and may overlap transfers with computation.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-002_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-002_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Draw four SM boxes and a grid of ten blocks. Under the deliberately simplified assumption of one resident block per SM, the grid needs at least three waves: four, four and two blocks. This is an occupancy illustration, not a runtime prediction. Real residency depends on registers, shared memory, threads and architectural limits.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
from math import ceil

assert ceil(10 / 4) == 3
assert [ceil(n / 32) for n in (31, 32, 33, 100)] == [1, 1, 2, 4]
print({"simplified_waves": ceil(10 / 4), "warps_for_100_threads": ceil(100 / 32)})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'simplified_waves': 3, 'warps_for_100_threads': 4}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A block with 100 threads occupies four warps. The last warp contains four valid program threads and 28 unused lane positions. A kernel with 100 blocks does not require 10,000 physical arithmetic units. Scheduling reuses execution resources over time. Do not build a dependency that assumes block 0 finishes first.

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

Calculate the warp count for blocks with 31, 32 and 33 threads.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A program labels its toolkit version as the GPU compute capability. Repair the inventory.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Can ten blocks require more than three waves in the four-SM drawing?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Map a 2 MiB array through host memory, transfer engine, device DRAM and an SM.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **every launched thread occupies its own permanent physical core.**

For the concrete failure exercise, a program labels its toolkit version as the GPU compute capability. Repair the inventory.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-002_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-002: Meet the hardware without memorizing a product catalog.
Read courses/cuda/cpp/guides/cuda-002.md and courses/cuda/cpp/lessons/cuda-002.md.
Direct prerequisites: `cuda-001`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-002_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-002_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
