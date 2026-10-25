# cuda-050: explanatory solutions

## Mechanism review

Parallel random-number generation needs a reproducible mapping from logical samples to independent streams or subsequences. Giving every thread identical initial state can repeat the same draws and destroy effective sample size. A seed identifies an experiment, but the generator, stream partition and sample-count mapping are also part of it. Monte Carlo error is sampling uncertainty, distinct from floating-point error or a bug. Increasing independent sample count usually reduces standard error at a square-root rate. RNG initialization can be expensive, so report setup separately from sustained generation when evaluating performance.

The separate [CPU reference](../references/cuda-050_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Estimate the integral of x squared on \([0,1]\) by averaging squared uniform samples. The exact answer is one third. A fixed CPU seed produces a reproducible educational estimate; its closeness is not evidence about cuRAND or independent GPU streams. Keep a broad deterministic sanity check separate from statistical claims.

## Exercise 2

Four workers initialized with exactly the same stream each draw \([0.1,0.7]\). Concatenating gives eight entries but only two distinct draws repeated four times. Treating them as eight independent observations understates uncertainty. A correct design gives workers nonoverlapping documented subsequences.

## Exercise 3

It is approximately halved under the usual finite-variance assumptions, not divided by four.

## Exercise 4

No. Different generators or stream mappings need not produce identical draws. Compare stated reproducibility and statistical contracts.

## Exercise 5

An undefined-estimate status rather than division by zero or a false estimate of zero.

## Exercise 6

Record generator/version, seed, subsequence assignment, sample count, estimator, uncertainty calculation and numeric precision.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-050_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Record generator/version, seed, subsequence assignment, sample count, estimator, uncertainty calculation and numeric precision.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
