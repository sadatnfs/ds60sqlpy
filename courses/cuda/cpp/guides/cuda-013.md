# cuda-013: Explicit device allocation and transfer

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-010`, `cuda-012`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain explicit device allocation and transfer using the concrete cases below. Produce unchanged guard values, correct output, checked statuses and cleanup after an injected host-side failure.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

cudaMalloc requests a number of bytes and returns a device allocation handle through a pointer argument. For n float elements, calculate n*sizeof(float), checking multiplication bounds for externally supplied sizes. cudaMemcpy also takes bytes and an explicit direction in the simple runtime API. The input owner must remain alive until the transfer finishes, and the device output must remain allocated until its final consumer completes. Host-to-device transfer supplies input; device-to-host transfer produces an observable result. A pointer is not a container with a length field, so the surrounding program must preserve size and lifetime metadata.

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
The separate [CPU reference](../references/cuda-013_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-013_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

Copy \([2,4,6,8]\) as float32. Four elements require 16 bytes. A request for four bytes copies only one float. Zero-initialized test data can hide that error, so use distinct nonzero entries and validate the entire result after the round trip.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
storage = [-99, 1, 2, 3, -99]
for i in range(1, 4):
    storage[i] *= 2
assert storage == [-99, 2, 4, 6, -99]
assert 4 * 4 == 16 and 33 * 8 == 264
print({"guarded_output": storage, "four_float32_bytes": 16})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'guarded_output': [-99, 2, 4, 6, -99], 'four_float32_bytes': 16}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Place sentinel values around a three-element target: \([-99,1,2,3,-99]\). Transform only positions 1 through 3 by doubling, expecting \([-99,2,4,6,-99]\). Guards reveal writes beyond the intended subrange, but they do not prove absence of every possible invalid read; sanitizers add a different check.

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

How many bytes hold 33 double values?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

A copy uses count where the API expects bytes. Which fixture catches it?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

Define an empty-vector transfer policy.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Design cleanup after a failed output allocation.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **equal numerical addresses imply interchangeable host and device pointers.**

For the concrete failure exercise, a copy uses count where the API expects bytes. Which fixture catches it?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-013_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-013: Explicit device allocation and transfer.
Read courses/cuda/cpp/guides/cuda-013.md and courses/cuda/cpp/lessons/cuda-013.md.
Direct prerequisites: `cuda-010`, `cuda-012`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-013_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-013_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
