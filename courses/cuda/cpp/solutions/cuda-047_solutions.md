# cuda-047: explanatory solutions

## Mechanism review

The discrete Fourier transform rewrites samples as frequency components with an explicit sign and normalization convention. An inverse transform must use the matching convention. cuFFT uses plans to prepare a transform shape/layout and may need workspace; plan creation is separate from execution. Multiplication in frequency space corresponds to circular convolution unless padding supplies enough length for the desired linear convolution. Real-to-complex storage has a special output shape and, for some in-place workflows, padding requirements. Define those layouts before moving data rather than treating all transforms as same-size arrays.

The separate [CPU reference](../references/cuda-047_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

The four-sample signal \([0,1,0,-1]\) has energy at the positive and negative one-cycle frequency components. A direct CPU DFT gives approximately [0,-2i,0,2i]. Small real roundoff terms are expected. This is a tiny semantic reference, not a fast FFT implementation.

**Approach:** Evaluate the DFT of [0, 1, 0, -1] directly on the CPU for k from 0 to 3.

**Why it is correct:** The signal is a one-cycle sine, so energy sits at k = 1 and k = 3 as -2i and 2i.

**A plausible wrong approach:** Requiring exact zeros in the real parts rejects roundoff near 2.4e-16 that is expected.

**How to verify:** The reference asserts each coefficient is within 1e-12 of [0, -2j, 0, 2j].

## Exercise 2

Linear convolution of \([1,2]\) and \([3,4]\) is \([3,10,8]\), requiring length three. A length-two circular convolution wraps the final eight into the first position, giving \([11,10]\). Zero-pad to at least the required linear-convolution length before comparing an FFT workflow.

**Approach:** Zero-pad [1, 2] and [3, 4] to length three before multiplying spectra.

**Why it is correct:** Linear convolution needs 2 + 2 - 1 = 3 outputs, giving [3, 10, 8].

**A plausible wrong approach:** Using length two wraps the 8 onto the 3, producing circular [11, 10].

**How to verify:** The reference asserts [3, 10, 8]; compare the FFT-based result after padding.

## Exercise 3

Five plus three minus one equals seven.

**Approach:** Add the lengths and subtract one.

**Why it is correct:** Five plus three minus one is seven output samples.

**A plausible wrong approach:** Padding to only five truncates the last two linear outputs by wrapping.

**How to verify:** Convolve two arrays of lengths five and three directly and count outputs.

## Exercise 4

The normalization convention was omitted or applied on the wrong side; apply the required scaling for the selected transform API.

**Approach:** Divide by N once in the round trip on the side the API leaves unnormalized.

**Why it is correct:** Unnormalized forward and inverse transforms multiply the input by N.

**A plausible wrong approach:** Dividing in both directions shrinks the result by N instead.

**How to verify:** Run forward then inverse on a known signal and compare to the input.

## Exercise 5

All frequency coefficients are zero within exact or justified numerical behavior; this alone is too weak to validate layout and sign.

**Approach:** Expect zero coefficients for a zero signal within roundoff.

**Why it is correct:** A linear transform maps zero to zero.

**A plausible wrong approach:** Treating a zero signal as a full test misses sign and layout errors.

**How to verify:** Add the sine fixture alongside to catch sign and index mistakes.

## Exercise 6

Separate plan creation from repeated execution, state batch/layout/precision, validate spectrum or convolution semantics and include required transfers.

**Approach:** Time plan creation separately from repeated executions, stating batch, layout and precision.

**Why it is correct:** Plans are reused, so their cost amortizes differently from execution.

**A plausible wrong approach:** Including plan creation in each iteration inflates per-transform cost.

**How to verify:** Validate spectra first, then record timing samples with transfers included as required.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-047_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Separate plan creation from repeated execution, state batch/layout/precision, validate spectrum or convolution semantics and include required transfers.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
