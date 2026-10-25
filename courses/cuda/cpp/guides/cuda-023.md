# cuda-023: Stencils and boundary conditions

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-015`, `cuda-017`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain stencils and boundary conditions using the concrete cases below. Produce correct interior and boundary values plus a conserved or monotonic quantity appropriate to the chosen model.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

A stencil computes each output from a neighborhood of input values. The boundary policy is part of the mathematics: clamped, periodic and fixed-zero boundaries describe different problems. Use separate input and output buffers for a time step so one update cannot change a neighbor's inputs halfway through the step. A tiled implementation loads a halo around its interior region because edge outputs need values from neighboring tiles. A barrier only protects data loaded by the same cooperating group; it does not legalize global in-place updates across independently scheduled blocks.

## Mathematical contract

\[
y_i=\frac{x_{i-1}+x_i+x_{i+1}}{3}
\]

The formula requires a separately stated boundary policy for indices outside the input. Input and output are distinct during one time step.

## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/cuda-023_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-023_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

For \([2,4,8]\) with a three-point mean and fixed-zero outside values, one step gives \([2,\frac{14}{3},4]\). With clamped boundaries it gives \([\frac{8}{3},\frac{14}{3},\frac{20}{3}]\). Both are valid calculations, but they answer different questions. A reference must match the chosen policy.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [2.0, 4.0, 8.0]


def at(i):
    return values[i] if 0 <= i < len(values) else 0.0


out = [(at(i - 1) + at(i) + at(i + 1)) / 3 for i in range(len(values))]
assert out == [2.0, 14 / 3, 4.0]
assert values == [2.0, 4.0, 8.0]
print({"fixed_zero_mean": out, "original_preserved": values})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'fixed_zero_mean': [2.0, 4.666666666666667, 4.0], 'original_preserved': [2.0, 4.0, 8.0]}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

An in-place left-to-right update reads newly computed values for later neighbors, creating a directional bias. Two-buffer updates read only the original row and swap roles after completion. For multiple GPU steps, preserve the dependency between launches or streams before swapping logical roles.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-023_gpu.cu) and separate
[GPU learner source](../lessons/cuda-023_gpu.cu) accompany this chapter.
They are standalone files with bounded fixtures, checked runtime calls and host
validation. The learner source intentionally reports incomplete implementation
until you add the chapter's algorithm and assertions. It must never return a
fake GPU success on a CPU machine. Follow the [manual GPU workflow](../README.md)
for exact compilation and execution paths. If the classroom offers the optional
CUDA C++ variant, its capability notice must confirm actual runtime readiness.

The reference contains an explicit no-device failure, launch and completion
checks, and returned-value validation. Source review and CPU reference checks do
not qualify this .cu file on your hardware. Preserve compilation, actual device
execution and sanitizer evidence separately. Exercise 4 is a reasoning diagnosis;
do not deliberately launch a hanging kernel or reset a shared GPU to reproduce it.

## Six progressive exercises

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Start with the literal input and intermediate quantities in worked example 1.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Identify exactly which condition changes in worked example 2.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 3

Compute the periodic neighbor mean for \([2,4,8]\).

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

An image looks smooth but differs near the edge. Investigate what first?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What is a radius-one fixed-zero stencil of singleton \([6]\)?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Transfer the method to diffusion time stepping.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a visually plausible image proves the indexing and update ordering are correct.**

For the concrete failure exercise, an image looks smooth but differs near the edge. Investigate what first?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-023_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-023: Stencils and boundary conditions.
Read courses/cuda/cpp/guides/cuda-023.md and courses/cuda/cpp/lessons/cuda-023.md.
Direct prerequisites: `cuda-015`, `cuda-017`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-023_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-023_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
