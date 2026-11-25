# cuda-085: explained solutions

Compare with your [worksheet](../lessons/cuda-085.md) attempt.

## Exercise 1: Compute complete latency

Include packing and transfer.

**Approach.** Add every component of latency: the library path is 8 ms of kernels plus 2 ms of transfer, 10 ms; the custom path is 6 + 2 + 3 ms of packing, 11 ms.

**Why it is correct here.** The custom kernel itself is 2 ms faster, but packing adds 3 ms. End-to-end latency is what callers experience, so the custom path is worse by 1 ms in this model.

**A plausible wrong approach.** Comparing kernel times alone, 6 against 8 ms, declares the custom version a win while ignoring the new packing step.

**How to verify.** The reference asserts totals of 10 and 11. Recompute after removing packing to check the comparison flips only when packing is eliminated.

## Exercise 2: List a numerical contract

Specify shape dtype tolerance and edge behavior.

**Approach.** Write the numerical contract for the operation: input shape and dtype, output dtype, tolerance against a reference, and behavior on empty inputs, NaN and overflow.

**Why it is correct here.** A replacement kernel must meet the same contract as the library. Without a written contract, a faster kernel that rounds differently or mishandles NaN looks like an improvement.

**A plausible wrong approach.** Testing only that the shapes match accepts any numbers of the right size, so a kernel that returns zeros, or that silently turns NaN inputs into finite outputs, would pass every check.

**How to verify.** Turn each clause into a test and run it against both implementations: a random input compared with tolerance, an empty input, an input containing NaN, and an input near the dtype maximum. Both must pass the same suite.

## Exercise 3: Add temporary memory

Count peak simultaneously live buffers.

**Approach.** Count temporary memory as the peak sum of buffers alive at the same time. For example, input, a packed copy and the output of `N` float32 values each give `3*4*N` bytes at peak, not `2*4*N`.

**Why it is correct here.** Peak memory decides whether a workload fits. The packed buffer coexists with the input during packing and with the output during the kernel.

**A plausible wrong approach.** Summing only the input and output ignores intermediates, so the custom path can run out of memory at a size where the library path fit, even though both outputs are the same size.

**How to verify.** Measure peak allocation with the library's memory pool statistics, such as CuPy's `get_default_memory_pool().used_bytes()`, for a known size and compare with the arithmetic. Free the pool between runs so caching does not hide the peak.

## Exercise 4: Identify a maintenance cost

Architecture and compiler changes need requalification.

**Approach.** Name a maintenance cost: a custom kernel must be recompiled and requalified for new GPU architectures, toolkit versions and compiler changes, while the library vendor handles that work.

**Why it is correct here.** Hand-tuned kernels encode assumptions about one generation's resources. A new architecture can change the best tile size or break inline assembly.

**A plausible wrong approach.** Counting only the development time ignores ongoing cost, which repeats every time the team adopts a new GPU or toolkit release and often exceeds the original effort.

**How to verify.** List the owner of each requalification step and the test that must pass on each supported architecture. If no one owns the step, the kernel has no maintenance plan.

## Exercise 5: Choose two workload sizes

Use tiny and representative bounded inputs.

**Approach.** Choose two workload sizes: a tiny input, where launch and first-call overheads dominate, and a representative bounded input sized like production work.

**Why it is correct here.** The fused kernel can win at the representative size by removing intermediates while losing at the tiny size because of compilation and launch cost.

**A plausible wrong approach.** Benchmarking only at the largest size that fits hides the small-input behavior, which matters when production calls are mostly small batches.

**How to verify.** Report both sizes with the same correctness checks, warm-up policy and synchronized timing method, and state the device used. Without a GPU, mark both timings as not measured.

## Exercise 6: Write a keep-or-replace decision

Keep the library unless measured benefits justify added obligations.

**Approach.** Write the decision: keep the library unless measured end-to-end gains on representative inputs exceed the added maintenance, testing and portability obligations. Here keep it, since the custom path is slower.

**Why it is correct here.** The modeled custom path loses 1 ms end to end and adds obligations, so nothing justifies the switch.

**A plausible wrong approach.** Choosing the custom kernel because its compute portion, 6 ms against 8 ms, is faster ignores the stated total and the packing step that the custom path requires.

**How to verify.** Include the totals, sizes, contract and the owner list in the decision record, so a later reviewer can repeat the decision if packing is removed or the library changes.

## Self-check answers

1. **When can a custom kernel be justified over a library call?** When it delivers a measured end-to-end benefit, such as fusing launches or handling an unusual layout, that survives correctness checks and outweighs its maintenance cost.

2. **Why include tiny inputs in the comparison?** At tiny sizes launch overhead and first-call compilation dominate, so a fused or custom kernel that wins on large inputs can lose there.

3. **What is an educational kernel's honest success claim?** It is learning evidence that the student understands the mechanism. It is not evidence of a production improvement unless measurements show one.

## Reference observation

Library 10 and custom 11 modeled milliseconds.

Asserted by `courses/cuda/python/references/cuda-085_cpu.py`.
