# cuda-047: cuFFT and a complete signal-processing example

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-039`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Verify cuFFT frequencies and round-trip error with explicit normalization and measure plan versus execution cost.

**Scope:** Transform conventions, inverse normalization, real/complex storage, plan creation, batch layout and workspace.

**Evidence to produce:** Correct frequencies and round-trip error, explicit normalization and measured plan-versus-execution cost.

## Purpose, vocabulary and mental model

The discrete Fourier transform rewrites samples as frequency components with an explicit sign and normalization convention. An inverse transform must use the matching convention. cuFFT uses plans to prepare a transform shape/layout and may need workspace; plan creation is separate from execution. Multiplication in frequency space corresponds to circular convolution unless padding supplies enough length for the desired linear convolution. Real-to-complex storage has a special output shape and, for some in-place workflows, padding requirements. Define those layouts before moving data rather than treating all transforms as same-size arrays.

### Key terms

- **FFT plan:** A cuFFT object created for one size, type and batch that stores precomputed setup for repeated transforms.
- **Normalization convention:** The rule for scaling; cuFFT transforms are unnormalized, so a forward and inverse round trip scales values by N.
- **Circular convolution:** Convolution in which indices wrap around, which is what pointwise multiplication of DFTs computes.
- **Real-to-complex transform:** A transform of N real inputs that stores only N/2+1 complex outputs because of conjugate symmetry.

## Mathematical contract

\[
X_k=\sum_{n=0}^{N-1}x_n e^{-2\pi\mathrm{i}kn/N}
\]

This forward DFT convention uses a negative exponent and no forward normalization. The matching inverse needs its corresponding scaling.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-047_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-047_cpu.py
```

## Worked example 1: trace the mechanism

The four-sample signal \([0,1,0,-1]\) has energy at the positive and negative one-cycle frequency components. A direct CPU DFT gives approximately [0,-2i,0,2i]. Small real roundoff terms are expected. This is a tiny semantic reference, not a fast FFT implementation.

**Why:** The signal is a one-cycle sine, so energy sits at k = 1 and k = 3 as -2i and 2i.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'DFT': [0j, (2.4492935982947064e-16-2j), 2.449293598294706e-16j, (-7.347880794884119e-16+2j)], 'linear_convolution': [3, 10, 8]}
```

**Check:** The reference asserts each coefficient is within 1e-12 of [0, -2j, 0, 2j].

## Worked example 2: change a meaningful condition

Linear convolution of \([1,2]\) and \([3,4]\) is \([3,10,8]\), requiring length three. A length-two circular convolution wraps the final eight into the first position, giving \([11,10]\). Zero-pad to at least the required linear-convolution length before comparing an FFT workflow.

**Why:** Linear convolution needs 2 + 2 - 1 = 3 outputs, giving [3, 10, 8].

**Check:** The reference asserts [3, 10, 8]; compare the FFT-based result after padding.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Evaluate the DFT of [0, 1, 0, -1] directly on the CPU for k from 0 to 3.

**Trap to avoid:** Requiring exact zeros in the real parts rejects roundoff near 2.4e-16 that is expected.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Zero-pad [1, 2] and [3, 4] to length three before multiplying spectra.

**Trap to avoid:** Using length two wraps the 8 onto the 3, producing circular [11, 10].

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Find the minimum linear-convolution length for arrays of lengths five and three.

**Trap to avoid:** Padding to only five truncates the last two linear outputs by wrapping.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A forward/inverse round trip returns N times the input. Diagnose it.

**Trap to avoid:** Dividing in both directions shrinks the result by N instead.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What happens with a zero-valued signal?

**Trap to avoid:** Treating a zero signal as a full test misses sign and layout errors.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Define a signal-processing benchmark.

**Trap to avoid:** Including plan creation in each iteration inflates per-transform cost.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A visually plausible spectrum proves correct scaling or an FFT automatically computes linear convolution.** A spectrum can have the right shape and the wrong scale, because conventions differ on where the 1/N factor goes. Frequency-space multiplication gives circular convolution, which wraps results, as worked example 2 shows with [11,10]. Check a round trip and zero-pad to the linear length before trusting it.

## Self-check, retrieval and transfer

1. What length avoids wraparound when convolving lengths 4 and 3?
2. A round trip returns N times the input. What is missing?
3. Why is plan creation kept outside timing loops?

Short answers are in the [separate explanations](../solutions/cuda-047_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
