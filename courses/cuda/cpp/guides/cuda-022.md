# cuda-022: Histograms, atomics and contention

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-020`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain histograms, atomics and contention using the concrete cases below. Produce exact counts and a contention-based explanation of two timing regimes.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

A histogram counts values into bins. Several threads can increment the same bin, so ordinary read-modify-write operations can lose updates. An atomic addition makes that individual update indivisible at its supported scope. It does not make an entire multi-step algorithm atomic or publish unrelated data automatically. A block-private histogram can reduce global contention by combining local counts before a global merge. It also costs shared memory and initialization work. Distribution matters: uniformly spread samples and one hot bin exercise very different contention patterns even with identical input size.

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
The separate [CPU reference](../references/cuda-022_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-022_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

Values \([0,2,2,1,2,0]\) with three bins produce \([2,1,3]\). The sum of bins is six. Two workers both reading an old count of zero and then each writing one lose a count; correct atomic accumulation produces two.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [0, 2, 2, 1, 2, 0]


def histogram(items):
    bins = [0, 0, 0]
    for value in items:
        assert 0 <= value < len(bins)
        bins[value] += 1
    return bins


parts = [histogram(values[:3]), histogram(values[3:])]
merged = [sum(pair) for pair in zip(*parts)]
assert merged == [2, 1, 3] and sum(merged) == len(values)
print({"partials": parts, "merged": merged})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'partials': [[1, 0, 2], [1, 1, 1]], 'merged': [2, 1, 3]}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Split the values into two groups of three. Their private histograms are \([1,0,2]\) and \([1,1,1]\); merging gives \([2,1,3]\). This explains the algorithm without promising the private version is faster. For small inputs, initialization and merging may cost more than direct atomic updates.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-022_gpu.cu) and separate
[GPU learner source](../lessons/cuda-022_gpu.cu) accompany this chapter.
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

Build a four-bin histogram of \([3,3,0,1,3]\).

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

The input contains category -1. Define a safe contract.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What fixture maximizes simple same-bin contention?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Transfer histograms to quantized floating measurements.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **an atomic operation is either always fast or always slow, independent of access pattern.**

For the concrete failure exercise, the input contains category -1. Define a safe contract.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-022_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-022: Histograms, atomics and contention.
Read courses/cuda/cpp/guides/cuda-022.md and courses/cuda/cpp/lessons/cuda-022.md.
Direct prerequisites: `cuda-017`, `cuda-020`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-022_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-022_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
