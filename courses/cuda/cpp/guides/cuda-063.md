# cuda-063: Capstone: a measured scientific or data application

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-038`, `cuda-039`, `cuda-040`, `cuda-044`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain capstone: a measured scientific or data application using the concrete cases below. Produce cPU baseline, adversarial tests, sanitizer results where applicable, profiling artifacts, reproducible benchmark, failure behavior and a report stating when CPU is preferable.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

An independent numerical project begins with a bounded question, not a performance claim. Specify accepted input, output semantics, precision, resource budget and failure behavior. Build an independent CPU reference and adversarial fixtures before optimizing. Choose algorithms or libraries that fit the contract, then profile the complete pipeline. Retain evidence that another learner can reproduce: source, generation parameters, correctness comparisons, tool diagnostics where available and timing samples. A CPU-only project remains a valid algorithm/design portfolio piece when it clearly leaves GPU performance unmeasured.

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
The separate [CPU reference](../references/cuda-063_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-063_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

Project A filters a synthetic signal with a fixed-zero stencil, computes an energy sum and returns both transformed values and the scalar. For \([2,4,8]\), the stencil reference is \([2,\frac{14}{3},4]\). The energy is the sum of squares, \(\frac{376}{9}\). Explicitly define whether energy is computed before or after filtering.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
from fractions import Fraction

filtered = [Fraction(2), Fraction(14, 3), Fraction(4)]
energy = sum(x * x for x in filtered)
assert energy == Fraction(376, 9)
print({"exact_filtered": [str(x) for x in filtered], "post_filter_energy": str(energy)})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'exact_filtered': ['2', '14/3', '4'], 'post_filter_energy': '376/9'}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Project B aggregates graph neighbors using CSR then normalizes nonempty rows. It includes isolated nodes, duplicate-edge policy and skewed row lengths. The project can choose a library sparse multiply or a custom kernel, but must compare identical semantics and include conversion costs when the graph arrives in another format.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

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

Write a minimal acceptance contract for Project A.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

A project claims a speedup but omits graph conversion. Diagnose it.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

Give three adversarial fixtures.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Decide whether the GPU earns deployment.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a performance demo without documented assumptions is a deliverable someone else can maintain.**

For the concrete failure exercise, a project claims a speedup but omits graph conversion. Diagnose it.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-063_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-063: Capstone: a measured scientific or data application.
Read courses/cuda/cpp/guides/cuda-063.md and courses/cuda/cpp/lessons/cuda-063.md.
Direct prerequisites: `cuda-038`, `cuda-039`, `cuda-040`, `cuda-044`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-063_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-063_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
