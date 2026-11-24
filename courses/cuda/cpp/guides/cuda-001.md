# cuda-001: What a GPU accelerates, and what it cannot make fast

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: None within this subject. Basic loops and arrays help; revisit Python or C++ foundations when needed.

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Decide whether to accelerate or keep each of two tasks on the CPU using an end-to-end Amdahl model.

Work through *What a GPU accelerates, and what it cannot make fast* with the concrete cases below. Finish with this evidence:
a decomposition diagram and a justified decision to accelerate or keep two tasks on CPU. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A CPU is optimized to make progress on a comparatively small number of complicated instruction streams. A GPU spends more of its resources on throughput across many pieces of work. This is a design distinction, not a rule that the GPU wins. A dependency means that one result must exist before another calculation can start. Pixel brightness updates have independent destinations; a running account balance has a dependency between successive balances. There can still be a parallel prefix algorithm for that balance, but changing the algorithm is real work. Include loading data, launching kernels and returning results when deciding whether acceleration helps a person waiting for an answer.

### Key terms

- **Throughput:** The amount of completed work per unit of time across many independent pieces of work, which GPU designs favor.
- **Latency:** The time from submitting one piece of work until its result is available, including transfer and launch costs.
- **Data dependency:** A relationship in which one calculation needs another calculation's result before it can start.
- **Amdahl's law:** A bound on whole-application speedup set by the fraction of time that stays serial or unaccelerated.

## Mathematical contract

\[
T_{\mathrm{new}}=T_{\mathrm{serial}}+\frac{T_{\mathrm{parallel}}}{s}+T_{\mathrm{transfer}}
\]

Times use the same units; s is the speedup of only the parallel portion. Launch and other overhead must also be included when present.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-001_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-001_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Suppose an application spends 20 seconds parsing and 80 seconds transforming pixels. An imagined GPU makes the transform ten times faster and adds 4 seconds of transfers. The new time is \(20 + 8 + 4 = 32\) seconds, so the application speedup is 3.125. The tenfold kernel improvement is not the application improvement. Even an infinitely fast transform leaves 24 seconds under these assumptions.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
cpu = 20 + 80
gpu = 20 + 80 / 10 + 4
assert gpu == 32
assert cpu / gpu == 3.125
print({"CPU_seconds": cpu, "modeled_GPU_seconds": gpu, "speedup": cpu / gpu})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'CPU_seconds': 100, 'modeled_GPU_seconds': 32.0, 'speedup': 3.125}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For one tiny request, suppose CPU arithmetic costs 2 microseconds, while GPU submission and transfers cost 30 microseconds before arithmetic. A 0.2 microsecond kernel gives 30.2 microseconds end to end. Batching 1,000 independent requests may amortize overhead, but it changes waiting time and memory usage. Neither result follows from a core count.

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

Construct a 100-second workload with 60 seconds parallelizable and no transfer cost; compute the best possible speedup.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A report compares a 2 ms CPU request against a 0.1 ms kernel and claims 20 times faster. Identify the missing observations.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What changes if the input contains zero pixels?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Would you accelerate a chain of 1,000 dependent HTTP requests using a CUDA kernel?

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **more GPU cores imply every program becomes faster.**

For the concrete failure exercise, a report compares a 2 ms CPU request against a 0.1 ms kernel and claims 20 times faster. Identify the missing observations.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-001_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-001: What a GPU accelerates, and what it cannot make fast.
Read courses/cuda/cpp/guides/cuda-001.md and courses/cuda/cpp/lessons/cuda-001.md.
Direct prerequisites: None within this subject. Basic loops and arrays help; revisit Python or C++ foundations when needed.
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-001_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-001_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
