# cuda-036: Occupancy, registers and latency hiding

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-002`, `cuda-019`, `cuda-033`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Choose a launch configuration for a stated workload and justify it even when the highest-occupancy setting loses.

Work through *Occupancy, registers and latency hiding* with the concrete cases below. Finish with this evidence:
a justified configuration choice for a stated workload and device, including an explanation when the highest-occupancy setting loses. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Occupancy compares resident warps with a hardware limit. Residency is constrained by threads, blocks, register allocation and shared memory, including allocation granularity. Resident does not mean ready to issue: a warp may wait for data or dependencies. More work per thread can improve reuse while increasing registers and reducing occupancy. Forcing fewer registers can increase spills to device memory. The goal is a correct faster workload, not maximizing one percentage. Use reviewed launch candidates, compiler resource reports and timings together, and avoid pretending a simplified resource arithmetic model reproduces every scheduling rule.

### Key terms

- **Occupancy:** The ratio of resident warps on an SM to the maximum it supports, limited by registers, shared memory and block size.
- **Register pressure:** High register use per thread that reduces how many warps can be resident at once.
- **Register spill:** Values the compiler moves to local memory when a thread needs more registers than are available.
- **Latency hiding:** Keeping the SM busy by switching to eligible warps while other warps wait for memory.
- **Launch bounds:** The `__launch_bounds__` qualifier that tells the compiler the maximum block size so it can limit registers.

## Mathematical contract

\[
N_{\mathrm{blocks}}\leq\left\lfloor\frac{R_{\mathrm{SM}}}{R_{\mathrm{thread}}T_{\mathrm{block}}}\right\rfloor
\]

This simplified register-only bound ignores allocation granularity and all other hardware limits. Do not report it as actual achieved occupancy.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-036_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-036_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

In a simplified SM with 65,536 registers, a 256-thread block using 64 registers per thread needs 16,384 registers. Registers alone permit four blocks. At 128 registers per thread, registers alone permit two. Other limits can reduce both figures; this calculation is not an actual occupancy API result.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
register_file, threads = 65536, 256
blocks = [register_file // (threads * registers) for registers in (64, 128)]
assert blocks == [4, 2]
print({"register_only_block_limits": blocks, "other_hardware_limits_included": False})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'register_only_block_limits': [4, 2], 'other_hardware_limits_included': False}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Configuration A takes 2 ms with 50% occupancy. Configuration B takes 2.4 ms with 75%. If both pass correctness, A wins that stated timing objective. Investigate reuse, instruction-level parallelism and spills rather than choosing B merely because its percentage is larger.

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

Estimate register-limited blocks for 128 threads at 64 registers using 65,536 registers.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why might reducing a register limit make a kernel slower?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What limits an extremely small grid?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a launch sweep.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **100 percent occupancy is always the best target.**

For the concrete failure exercise, why might reducing a register limit make a kernel slower?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-036_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-036: Occupancy, registers and latency hiding.
Read courses/cuda/cpp/guides/cuda-036.md and courses/cuda/cpp/lessons/cuda-036.md.
Direct prerequisites: `cuda-002`, `cuda-019`, `cuda-033`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-036_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-036_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
