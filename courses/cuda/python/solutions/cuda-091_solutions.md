# cuda-091: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: State cross-correlation convention

Write the exact index formula.

**Approach.** Write the cross-correlation formula used by deep learning libraries: `out[i] = sum(x[i+j]*k[j] for j in range(len(k)))`, with no kernel flip.

**Why it is correct here.** For `x = [1, 2, 3, 4]` and `k = [1, -1]`, each output is `x[i] - x[i+1] = -1`, giving `[-1, -1, -1]`. Mathematical convolution flips the kernel and gives `[1, 1, 1]`.

**A plausible wrong approach.** Writing a reference with `k[len(k)-1-j]`, textbook convolution, flips every sign compared with the library, which looks like a broken GPU kernel.

**How to verify.** The reference asserts `out == [-1, -1, -1]`. Compare against `torch.nn.functional.conv1d` on the same values.

## Exercise 2: Calculate output length

Valid length is input minus kernel plus one.

**Approach.** Compute the valid output length as input length minus kernel length plus one: `4 - 2 + 1 = 3`.

**Why it is correct here.** With no padding, the kernel slides only over positions where it fits entirely. There are three such starting positions, 0, 1 and 2.

**A plausible wrong approach.** Using input length as output length assumes same padding, adding an output whose computation needs a value beyond the input.

**How to verify.** Check the reference's `range(len(x)-len(k)+1)` produces three outputs, and confirm the library's output shape matches.

## Exercise 3: Count layout conversion cost

Include conversions in complete latency.

**Approach.** Include layout conversion in total latency: with conversion cost 2 ms and saving 1 ms per call against 2 ms unconverted, one call costs `2 + 1 = 3` ms against 2, while four calls cost `2 + 4 = 6` against 8.

**Why it is correct here.** The conversion is paid once and the saving accrues per reuse, so it pays off only when the converted data is reused enough. The reference asserts both inequalities.

**A plausible wrong approach.** Counting only the faster convolution, 1 ms against 2, declares conversion a win even for a single call.

**How to verify.** Evaluate both expressions and note the break-even at two calls, where both total 4 ms.

## Exercise 4: Compare forward and backward

Both computations matter for training.

**Approach.** Compare forward and backward costs: training runs the forward convolution plus two backward convolutions, for input gradients and weight gradients, and each may choose a different algorithm.

**Why it is correct here.** An algorithm or layout that speeds the forward pass can slow the backward ones. Training time depends on all three. Inference, by contrast, only runs the forward pass, so the best choice can differ between the two uses.

**A plausible wrong approach.** Benchmarking only the forward pass and applying the result to training ignores roughly two thirds of the convolution work.

**How to verify.** Time forward and backward separately in a profiler for each candidate layout, and confirm gradients match a reference.

## Exercise 5: Explain algorithm warmup

Algorithm choice may need startup work.

**Approach.** Explain algorithm warm-up: with benchmark mode enabled, cuDNN tries several algorithms for each new shape on the first call and caches the fastest.

**Why it is correct here.** The first iteration for each shape includes that search, so it is much slower than steady state. New shapes trigger a new search.

**A plausible wrong approach.** Timing the first iteration and concluding the configuration is slow measures the search.

**How to verify.** Discard warm-up iterations for every shape and record their count. Steady-state times should be stable. Without a GPU, record the plan and mark the timings as not measured.

## Exercise 6: Design two shape cases

Use a narrow and wider batch with unchanged semantics.

**Approach.** Design two shape cases with unchanged semantics: a narrow batch such as 1 and a wider batch such as 32, same channels, kernel size and padding.

**Why it is correct here.** The best algorithm and layout can differ by shape, so one size may not represent the workload. A batch of 1 may favor a different algorithm than a batch of 32, and conversion overhead weighs more when each call does little work.

**A plausible wrong approach.** Testing a single shape and generalizing the chosen layout risks regressions at other batch sizes. Production traffic that mixes sizes then sees the slow path.

**How to verify.** Verify outputs for both shapes against a reference, then report time per sample for each.

## Reference observation

Valid cross-correlation [-1,-1,-1]; conversion amortization depends on reuse.

The reference file is `courses/cuda/python/references/cuda-091_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
