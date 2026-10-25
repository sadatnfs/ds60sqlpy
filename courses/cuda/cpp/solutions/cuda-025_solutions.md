# cuda-025: explanatory solutions

## Mechanism review

Debugging starts by placing a failure in its phase. A source error prevents compilation; a missing symbol prevents linking; incompatible device code can prevent loading; invalid launch parameters can reject submission; an illegal access can fail asynchronous execution; and a completed kernel can still calculate the wrong answer. Later CUDA calls may surface an earlier asynchronous failure, so the line reporting an error is not always the line that caused it. Use checked phase boundaries in a debug configuration and retain the earliest meaningful diagnostic. Avoid reinstalling tools before a small reproducer isolates the responsible layer.

The separate [CPU reference](../references/cuda-025_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A misspelled identifier in main.cu produces a compiler error before any device work. Fixing bounds checks cannot help until the file compiles. Record the diagnostic with source line and build command, and rerun the smallest compilation step.

## Exercise 2

A launch is accepted but a checked synchronization reports an illegal memory access. Now examine ownership and bounds near that launch. If synchronization succeeds and one output is wrong, inspect arithmetic, layout or uninitialized data instead. These outcomes require different next experiments.

## Exercise 3

Host linking failed; provide the helper definition or link the correct object/library before investigating GPU execution.

## Exercise 4

It narrows which launch caused an asynchronous error, but changes scheduling and performance. Remove unnecessary synchronization after the dependency bug is repaired.

## Exercise 5

The required runtime is unavailable; the numerical test did not execute and must not pass.

## Exercise 6

Include source revision, exact shape/dtype/data generator, expected and observed values, launch geometry, device/software identity and smallest failing index.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-025_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Include source revision, exact shape/dtype/data generator, expected and observed values, launch geometry, device/software identity and smallest failing index.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
