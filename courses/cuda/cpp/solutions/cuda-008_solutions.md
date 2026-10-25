# cuda-008: explanatory solutions

## Mechanism review

A reproducible experiment records enough context to explain why a result happened. An input seed is useful only alongside the generator, dtype, shape and distribution. A benchmark needs timing scope, warm-up policy and retained samples, while a correctness result needs an independent expected answer. Hardware access, successful compilation, successful execution and acceptable numerical output are four distinct observations. A resource budget limits input size and repeated work before running. On a shared GPU, reserve only the memory and compute time that the owner has authorized; do not use unbounded spin loops as teaching fixtures.

The separate [CPU reference](../references/cuda-008_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Report A says 'GPU: 0.2 ms'. Report B records a synthetic float32 vector of 1,024 elements, seed 7, upload excluded, five warm-ups, twenty event-timed samples, device/toolkit identities and an absolute error bound. B is interpretable, but it still needs raw samples and CPU comparison before supporting a speedup claim.

## Exercise 2

A vector-add oracle uses \([0,-2,5]\) and \([3,2,-1]\), expecting \([3,0,4]\). Add length-zero and a 33-element fixture to expose assumptions about block boundaries. This reference can run on any CPU. Label it CPU correctness evidence rather than evidence that a GPU kernel has run.

## Exercise 3

Source identity, exact bounded input, reference method, observed result or error, and execution environment/capability are a useful minimum.

## Exercise 4

Compilation passed; execution was cancelled or incomplete. A separate completed numerical comparison is required for runtime acceptance.

## Exercise 5

Unavailable or skipped with the actual reason, never a successful CUDA result and never a fabricated timing.

## Exercise 6

Their raw payload is 12 MB total. Add library workspace and runtime overhead separately and reject larger input before allocation.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-008_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Their raw payload is 12 MB total. Add library workspace and runtime overhead separately and reject larger input before allocation.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
