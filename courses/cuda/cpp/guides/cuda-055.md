# cuda-055: Cooperative Groups and global coordination

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-027`, `cuda-028`, `cuda-036`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Justify cooperative group participation with a written argument and a runtime capability report.

Work through *Cooperative Groups and global coordination* with the concrete cases below. Finish with this evidence:
a correct participation argument and runtime capability report. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Cooperative Groups makes participating thread groups explicit. A group collective is valid only when its membership and participation requirements are met. A block group can express block cooperation; a grid-wide group requires a supported cooperative launch and launch-size constraints. Ordinary launches cannot safely turn a hand-written spin loop into a global barrier. Device support, resource usage and residency determine whether a cooperative grid fits. Start with block-level algorithms and keep a multi-kernel fallback whose dependencies are established by normal launch ordering.

### Key terms

- **Cooperative Groups:** A CUDA API that names sets of threads explicitly and synchronizes them as groups.
- **Thread block tile:** A fixed-size partition of a block, such as 32 threads, created with `tiled_partition`.
- **Grid group:** A group representing every thread in the grid, which can synchronize only under a cooperative launch.
- **Cooperative launch:** A launch through `cudaLaunchCooperativeKernel` that guarantees all blocks are resident at once.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-055_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-055_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

An eight-thread conceptual block splits into two groups of four. Each group sums its values: \([1,2,3,4]\) gives ten and \([5,6,7,8]\) gives 26. The block-level final result is 36 after a separate valid combination step. Group-local synchronization does not synchronize the other group automatically.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = list(range(1, 9))
partials = [sum(values[start : start + 4]) for start in range(0, len(values), 4)]
assert partials == [10, 26] and sum(partials) == 36
assert 12 > 4 * 2
print({"group_sums": partials, "simplified_cooperative_capacity": 8})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'group_sums': [10, 26], 'simplified_cooperative_capacity': 8}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A simplified cooperative capacity is four SMs times two resident blocks per SM, or eight blocks. Requesting twelve cooperative blocks violates that assumed capacity. The actual supported limit must be obtained for the real kernel/device; source-level arithmetic is only an explanatory model.

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

Explain group size versus input count.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why can a grid barrier fail in an ordinary launch?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if cooperative launch is unavailable?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Refactor a reduction into explicit groups.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **calling a grid barrier makes an ordinary launch globally synchronized. .**

For the concrete failure exercise, why can a grid barrier fail in an ordinary launch?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-055_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [Cooperative Groups](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cooperative-groups.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-055: Cooperative Groups and global coordination.
Read courses/cuda/cpp/guides/cuda-055.md and courses/cuda/cpp/lessons/cuda-055.md.
Direct prerequisites: `cuda-027`, `cuda-028`, `cuda-036`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-055_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-055_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
