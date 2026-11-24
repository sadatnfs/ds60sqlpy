# cuda-008: explanatory solutions

## Mechanism review

A reproducible experiment records enough context to explain why a result happened. An input seed is useful only alongside the generator, dtype, shape and distribution. A benchmark needs timing scope, warm-up policy and retained samples, while a correctness result needs an independent expected answer. Hardware access, successful compilation, successful execution and acceptable numerical output are four distinct observations. A resource budget limits input size and repeated work before running. On a shared GPU, reserve only the memory and compute time that the owner has authorized; do not use unbounded spin loops as teaching fixtures.

The separate [CPU reference](../references/cuda-008_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Report A says 'GPU: 0.2 ms'. Report B records a synthetic float32 vector of 1,024 elements, seed 7, upload excluded, five warm-ups, twenty event-timed samples, device/toolkit identities and an absolute error bound. B is interpretable, but it still needs raw samples and CPU comparison before supporting a speedup claim.

**Approach:** List what Report B records that Report A lacks: data type, size, seed, warm-ups, sample count, identities and an error bound.

**Why it is correct:** Each field lets another person reproduce the run or judge its scope; 0.2 ms alone cannot be interpreted.

**A plausible wrong approach:** Treating B as proof of speedup ignores that it still lacks raw samples and a matched CPU baseline.

**How to verify:** Check each field of B against the receipt template and mark raw samples and CPU comparison as missing.

## Exercise 2

A vector-add oracle uses \([0,-2,5]\) and \([3,2,-1]\), expecting \([3,0,4]\). Add length-zero and a 33-element fixture to expose assumptions about block boundaries. This reference can run on any CPU. Label it CPU correctness evidence rather than evidence that a GPU kernel has run.

**Approach:** Add [0, -2, 5] and [3, 2, -1] elementwise, then extend fixtures to length 0 and 33.

**Why it is correct:** Negative and zero results exercise signs, and 33 elements cross a 32-thread boundary into a second warp.

**A plausible wrong approach:** Testing only with 32 elements would pass a kernel that drops or overruns the tail element.

**How to verify:** The reference asserts the sum is [3, 0, 4] and prints a receipt with gpu_executed False.

## Exercise 3

Source identity, exact bounded input, reference method, observed result or error, and execution environment/capability are a useful minimum.

**Approach:** Pick fields that let a stranger rerun and judge the check: source, input, reference, result, environment.

**Why it is correct:** Without the exact input and reference method, a reported pass cannot be reproduced or questioned.

**A plausible wrong approach:** Recording only pass or fail discards the observed values that would reveal a near-miss or a tolerance problem.

**How to verify:** Fill the five fields for the vector-add fixture and confirm someone else could repeat it from them alone.

## Exercise 4

Compilation passed; execution was cancelled or incomplete. A separate completed numerical comparison is required for runtime acceptance.

**Approach:** Split the record into compile, execute and validate stages and mark execution cancelled.

**Why it is correct:** A compiler exit code covers only translation; it says nothing about whether the kernel ran or matched.

**A plausible wrong approach:** Leaving passed because no error appeared conflates missing evidence with positive evidence.

**How to verify:** Confirm the corrected record shows compile passed, execute cancelled, validate not run.

## Exercise 5

Unavailable or skipped with the actual reason, never a successful CUDA result and never a fabricated timing.

**Approach:** Record the status as skipped or unavailable, with the reason such as zero visible devices.

**Why it is correct:** A skipped result is honest and machine-readable, while a fabricated success misleads downstream summaries.

**A plausible wrong approach:** Substituting the CPU reference output and labeling it CUDA invents execution evidence that never existed.

**How to verify:** Run the CPU model on a no-device machine and verify its receipt says CPU reference.

## Exercise 6

Their raw payload is 12 MB total. Add library workspace and runtime overhead separately and reject larger input before allocation.

**Approach:** Multiply three vectors by one million elements by 4 bytes, then list workspace and runtime overhead separately.

**Why it is correct:** The 12 MB payload is exact; extra allocations depend on libraries and must be budgeted as distinct lines.

**A plausible wrong approach:** Budgeting exactly 12 MB of free memory fails when the runtime context and alignment add their own usage.

**How to verify:** The reference asserts 3 * 1_000_000 * 4 == 12_000_000; test that oversized requests are rejected before allocation.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-008_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It also asserts an exercise answer that the guide's model leaves for you to derive: `assert 3 * 1_000_000 * 4 == 12_000_000`. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Their raw payload is 12 MB total. Add library workspace and runtime overhead separately and reject larger input before allocation.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
