# cuda-060: Multiple GPUs, topology and collective communication

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-028`, `cuda-039`, `cuda-040`, `cuda-044`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain multiple GPUs, topology and collective communication using the concrete cases below. Produce correct combined result, observed topology, collective completion and strong/weak scaling interpretation where meaningful.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

Multiple GPUs have distinct allocations, execution contexts and communication paths. Peer access may be available for a pair, but it must be supported and explicitly configured under the platform's rules. Topology affects whether traffic uses PCIe, NVLink or other paths. A collective such as all-reduce combines values and makes the result available to every participant. Participants must agree on communicator, datatype, count and collective order; mismatches can hang or fail. Multi-GPU within one machine does not prove multi-node operation, which adds network, process-launch and failure concerns.

## Mathematical contract

\[
E_p=\frac{S_p}{p}
\]

Strong-scaling efficiency E uses speedup S for fixed total work on p devices with the same result and timing scope.

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
The separate [CPU reference](../references/cuda-060_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-060_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

Split \([1,2,3,4,5]\) across two devices as \([1,2,3]\) and \([4,5]\). Local sums are six and nine; a combined sum is fifteen. A gather gives the final result to one destination, whereas all-reduce gives fifteen to both participants. A CPU partition model demonstrates semantics only.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [1, 2, 3, 4, 5]
partials = [sum(values[:3]), sum(values[3:])]
all_reduce_model = [sum(partials)] * 2
assert partials == [6, 9] and all_reduce_model == [15, 15]
assert 1.6 / 2 == 0.8
print({"CPU_collective_model": all_reduce_model, "multi_GPU_executed": False})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'CPU_collective_model': [15, 15], 'multi_GPU_executed': False}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For a radius-one stencil split into left and right partitions, each side needs its neighbor's boundary value before updating edge cells. Exchange halos and establish completion before reading them. Copying only the interior or assuming all device pointers share one pool breaks the contract.

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

Compute strong-scaling efficiency for speedup 1.6 on two GPUs.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

Rank zero calls all-reduce while rank one calls broadcast first. Diagnose it.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What can one GPU prove about two-device peer access?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Define weak versus strong scaling.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **two GPUs share memory automatically or multi-GPU execution proves multi-node readiness. , .**

For the concrete failure exercise, rank zero calls all-reduce while rank one calls broadcast first. Diagnose it.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-060_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [Multi-GPU programming](https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/multi-gpu-systems.html)
- [NCCL](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-060: Multiple GPUs, topology and collective communication.
Read courses/cuda/cpp/guides/cuda-060.md and courses/cuda/cpp/lessons/cuda-060.md.
Direct prerequisites: `cuda-028`, `cuda-039`, `cuda-040`, `cuda-044`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-060_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-060_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
