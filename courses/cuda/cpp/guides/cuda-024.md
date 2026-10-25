# cuda-024: First capstone: a reliable GPU data pipeline

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-014`, `cuda-020`, `cuda-021`, `cuda-022`, `cuda-008`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain first capstone: a reliable GPU data pipeline using the concrete cases below. Produce a specification, CPU oracle, adversarial fixtures, checked error paths, actual GPU output and honest end-to-end report.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

A pipeline is more than a list of correct kernels. Each stage has a shape, ownership and validity contract that must match its consumer. Filtering changes count; normalization changes numeric range; histogramming assumes valid bins. Keep the count with the output buffer, and do not pass allocation capacity as the number of valid elements. First build a tiny CPU oracle, then introduce one GPU stage at a time. A useful capstone report includes cases where a CPU is preferable, because proving that a GPU exists is different from proving it helps the application.

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
The separate [CPU reference](../references/cuda-024_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-024_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

A synthetic event pipeline keeps nonnegative values from \([-2,1,3,-1,2]\), producing \([1,3,2]\). It computes count three, sum six and mean two. A histogram over bins 0 through 3 gives \([0,1,1,1]\). This ties compaction output count to every downstream stage.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [-2, 1, 3, -1, 2]
selected = [v for v in values if v >= 0]
bins = [selected.count(i) for i in range(4)]
assert selected == [1, 3, 2] and bins == [0, 1, 1, 1]
result = {"count": len(selected), "sum": sum(selected), "mean": sum(selected) / len(selected)}
assert result == {"count": 3, "sum": 6, "mean": 2.0}
print(result, bins)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'count': 3, 'sum': 6, 'mean': 2.0} [0, 1, 1, 1]
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

An empty selection from \([-4,-1]\) has count zero and sum zero, but no defined ordinary arithmetic mean. Return a named empty-result status or optional mean rather than dividing by zero. The histogram remains four zeros under this contract.

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

Specify the pipeline output for \([0,0,3]\).

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

A downstream kernel consumes capacity ten after only three items were selected. Diagnose it.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

Add a value 7 when only bins 0 through 3 are supported.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Define a fair end-to-end comparison.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **individual correct kernels necessarily compose correctly when buffers, shapes or ownership differ.**

For the concrete failure exercise, a downstream kernel consumes capacity ten after only three items were selected. Diagnose it.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-024_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-024: First capstone: a reliable GPU data pipeline.
Read courses/cuda/cpp/guides/cuda-024.md and courses/cuda/cpp/lessons/cuda-024.md.
Direct prerequisites: `cuda-014`, `cuda-020`, `cuda-021`, `cuda-022`, `cuda-008`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-024_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-024_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
