# cuda-042: Unified memory, residency and migration

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`, `cuda-032`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Report unified memory behavior tied to queried device capabilities and observed page migration.

Work through *Unified memory, residency and migration* with the concrete cases below. Finish with this evidence:
correctness and a report tied to actual memory capabilities and observed movement. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Unified virtual addressing concerns address-space organization; managed memory provides an allocation model whose residency and migration are managed under supported platform rules. Neither term promises uniform access cost. First touch can trigger movement, alternating host/device access can cause repeated migration, and prefetch is a placement hint with its own ordering requirements. Coherent systems, discrete GPUs and WSL can have different capabilities. Query support and use the selected platform's documented contract. A single pointer does not erase the need to reason about which processor owns useful work at each phase.

### Key terms

- **Managed memory:** An allocation from `cudaMallocManaged` that both host and device can address through one pointer.
- **Page migration:** Moving memory pages between host and device on demand, which costs time the first time each page is touched.
- **Prefetch:** A `cudaMemPrefetchAsync` hint that moves pages to a processor before they are needed.
- **Unified virtual addressing:** One virtual address space shared by host and devices so a pointer value identifies its memory.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-042_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-042_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A 64 MiB managed array is initialized by the CPU and then processed repeatedly on a GPU. The first GPU pass may include migration costs that later resident passes do not. Report the first pass separately rather than using a warm result to promise cold-start latency.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
mib, transitions = 64, 20
modeled_moved_mib = mib * transitions
assert modeled_moved_mib == 1280
print({"simplified_transition_volume_MiB": modeled_moved_mib, "actual_migration_measured": False})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'simplified_transition_volume_MiB': 1280, 'actual_migration_measured': False}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Alternating a full CPU pass and full GPU pass for ten rounds can move the working set repeatedly. A simplified model counts twenty ownership transitions, unlike a batched design with one transfer to each side. Actual migration can occur at finer granularity and depends on platform support.

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

Distinguish a pointer value from physical residency.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can managed memory still run out of usable resources?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an unsupported prefetch capability do?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Redesign an alternating pipeline to reduce movement.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **one pointer means one physically uniform memory pool or that managed allocation eliminates data-movement cost. .**

For the concrete failure exercise, why can managed memory still run out of usable resources?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-042_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [Unified memory](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/unified-memory.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-042: Unified memory, residency and migration.
Read courses/cuda/cpp/guides/cuda-042.md and courses/cuda/cpp/lessons/cuda-042.md.
Direct prerequisites: `cuda-005`, `cuda-032`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-042_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-042_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
