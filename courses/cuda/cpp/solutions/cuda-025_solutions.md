# cuda-025: explanatory solutions

## Mechanism review

Debugging starts by placing a failure in its phase. A source error prevents compilation; a missing symbol prevents linking; incompatible device code can prevent loading; invalid launch parameters can reject submission; an illegal access can fail asynchronous execution; and a completed kernel can still calculate the wrong answer. Later CUDA calls may surface an earlier asynchronous failure, so the line reporting an error is not always the line that caused it. Use checked phase boundaries in a debug configuration and retain the earliest meaningful diagnostic. Avoid reinstalling tools before a small reproducer isolates the responsible layer.

The separate [CPU reference](../references/cuda-025_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A misspelled identifier in main.cu produces a compiler error before any device work. Fixing bounds checks cannot help until the file compiles. Record the diagnostic with source line and build command, and rerun the smallest compilation step.

**Approach:** Classify the misspelled identifier as a compile failure and fix it at the reported source line.

**Why it is correct:** No device code exists until compilation succeeds, so runtime checks are irrelevant.

**A plausible wrong approach:** Adding bounds checks in the kernel cannot help a file that never builds.

**How to verify:** Rerun only the compile command for main.cu and confirm it exits zero.

## Exercise 2

A launch is accepted but a checked synchronization reports an illegal memory access. Now examine ownership and bounds near that launch. If synchronization succeeds and one output is wrong, inspect arithmetic, layout or uninitialized data instead. These outcomes require different next experiments.

**Approach:** Treat an illegal access at a checked synchronization as an execution failure tied to the preceding launch.

**Why it is correct:** Launch acceptance only means the configuration was valid; the fault appears when work completes.

**A plausible wrong approach:** Blaming the synchronize call itself sends you to inspect the wrong line of host code.

**How to verify:** Check indices near that kernel's bounds and rerun with a sanitizer to name the bad address.

## Exercise 3

Host linking failed; provide the helper definition or link the correct object/library before investigating GPU execution.

**Approach:** Classify an undefined reference to a host helper as a link failure.

**Why it is correct:** The compiler accepted a declaration, but the linker found no definition in the inputs.

**A plausible wrong approach:** Recompiling with different GPU architecture flags changes nothing about a missing host symbol.

**How to verify:** Add the defining object or library to the link line and confirm the binary is produced.

## Exercise 4

It narrows which launch caused an asynchronous error, but changes scheduling and performance. Remove unnecessary synchronization after the dependency bug is repaired.

**Approach:** Insert checked synchronization after each stage while localizing, then remove the extras.

**Why it is correct:** Errors from asynchronous launches surface later, and a sync after each stage pins the culprit.

**A plausible wrong approach:** Leaving every synchronization in production serializes stages that could overlap.

**How to verify:** After the fix, rerun with syncs removed and confirm results and error checks still pass.

## Exercise 5

The required runtime is unavailable; the numerical test did not execute and must not pass.

**Approach:** Report the test as not run or skipped with a no-device reason.

**Why it is correct:** No kernel executed, so no numerical claim was tested.

**A plausible wrong approach:** Counting it as passed hides that the GPU path has never been exercised.

**How to verify:** Run the suite on a machine without a GPU and confirm it reports skipped, not passed.

## Exercise 6

Include source revision, exact shape/dtype/data generator, expected and observed values, launch geometry, device/software identity and smallest failing index.

**Approach:** List revision, shape, dtype, data generator, expected and observed values, launch geometry and first failing index.

**Why it is correct:** Shape dependence means another engineer needs the exact shape and geometry to reproduce it.

**A plausible wrong approach:** Writing only 'wrong answer on large inputs' gives no reproducer and no index to inspect.

**How to verify:** Ask a colleague to reproduce from the report alone and confirm they see the same index.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-025_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Include source revision, exact shape/dtype/data generator, expected and observed values, launch geometry, device/software identity and smallest failing index.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
