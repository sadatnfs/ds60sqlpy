# cuda-047: cuFFT and a complete signal-processing example

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain cuFFT and a complete signal-processing example using the concrete cases below. Produce correct frequencies and round-trip error, explicit normalization and measured plan-versus-execution cost.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

The discrete Fourier transform rewrites samples as frequency components with an explicit sign and normalization convention. An inverse transform must use the matching convention. cuFFT uses plans to prepare a transform shape/layout and may need workspace; plan creation is separate from execution. Multiplication in frequency space corresponds to circular convolution unless padding supplies enough length for the desired linear convolution. Real-to-complex storage has a special output shape and, for some in-place workflows, padding requirements. Define those layouts before moving data rather than treating all transforms as same-size arrays.

## Mathematical contract

\[
X_k=\sum_{n=0}^{N-1}x_n e^{-2\pi\mathrm{i}kn/N}
\]

This forward DFT convention uses a negative exponent and no forward normalization. The matching inverse needs its corresponding scaling.

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
The separate [CPU reference](../references/cuda-047_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-047_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

The four-sample signal \([0,1,0,-1]\) has energy at the positive and negative one-cycle frequency components. A direct CPU DFT gives approximately [0,-2i,0,2i]. Small real roundoff terms are expected. This is a tiny semantic reference, not a fast FFT implementation.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
import cmath

signal = [0, 1, 0, -1]
spectrum = [
    sum(x * cmath.exp(-2j * cmath.pi * k * n / 4) for n, x in enumerate(signal)) for k in range(4)
]
expected = [0, -2j, 0, 2j]
assert all(abs(a - b) < 1e-12 for a, b in zip(spectrum, expected))
assert [1 * 3, 1 * 4 + 2 * 3, 2 * 4] == [3, 10, 8]
print({"DFT": spectrum, "linear_convolution": [3, 10, 8]})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'DFT': [0j, (2.4492935982947064e-16-2j), 2.449293598294706e-16j, (-7.347880794884119e-16+2j)], 'linear_convolution': [3, 10, 8]}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Linear convolution of \([1,2]\) and \([3,4]\) is \([3,10,8]\), requiring length three. A length-two circular convolution wraps the final eight into the first position, giving \([11,10]\). Zero-pad to at least the required linear-convolution length before comparing an FFT workflow.

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

Find the minimum linear-convolution length for arrays of lengths five and three.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

A forward/inverse round trip returns N times the input. Diagnose it.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What happens with a zero-valued signal?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Define a signal-processing benchmark.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a visually plausible spectrum proves correct scaling or an FFT automatically computes linear convolution. .**

For the concrete failure exercise, a forward/inverse round trip returns N times the input. Diagnose it.
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-047_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [cuFFT documentation](https://docs.nvidia.com/cuda/cufft/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-047: cuFFT and a complete signal-processing example.
Read courses/cuda/cpp/guides/cuda-047.md and courses/cuda/cpp/lessons/cuda-047.md.
Direct prerequisites: `cuda-006`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-047_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-047_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
