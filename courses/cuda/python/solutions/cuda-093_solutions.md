# cuda-093: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count specializations

Two distinct shape signatures.

**Approach.** Count specializations by collecting distinct shape signatures: the calls `(4, 8)`, `(4, 8)` and `(8, 8)` form the set `{(4, 8), (8, 8)}`, so the simplified cache compiles twice.

**Why it is correct here.** A shape-specialized compiler such as `torch.compile` with static shapes keys its cache on input shapes and dtypes. A repeated signature reuses the cached code, while a new leading dimension triggers another compilation.

**A plausible wrong approach.** Counting one compilation per call, three here, ignores the cache and overestimates startup cost. Counting one compilation total assumes the compiler generalizes across shapes, which static specialization does not.

**How to verify.** The reference asserts `len(set(shapes)) == 2`. With a real compiler, enable recompilation logging and confirm exactly two compile events for this call sequence.

## Exercise 2: Calculate break-even calls

At 500 calls costs tie and 501 starts benefiting.

**Approach.** Divide the compile cost by the per-call saving: `500 / 1 = 500` calls repay the 500 ms compilation, so at 500 calls the two paths tie and from call 501 the compiled path is ahead.

**Why it is correct here.** Total compiled cost is `500 + c*(t-1)` against `c*t` uncompiled for `c` calls with per-call time `t`. The difference is `500 - c`, which is zero at 500 and negative afterward.

**A plausible wrong approach.** Assuming compilation pays off immediately because each call is faster ignores the startup cost. A short-lived job of 100 calls loses 400 ms overall.

**How to verify.** The reference asserts the ratio is 500. Recompute with a 2 ms saving and confirm the break-even halves to 250 calls.

## Exercise 3: Describe a graph break

Unsupported dynamic behavior can leave compiled regions.

**Approach.** Describe a graph break: when the compiler meets something it cannot trace, such as a data-dependent Python branch on a tensor value or a call to an unsupported library, it ends the compiled region, runs that code eagerly and starts a new region.

**Why it is correct here.** Each break splits the graph, reducing fusion opportunities and adding transitions between compiled and eager execution. Correctness is preserved, but expected speedups can disappear.

**A plausible wrong approach.** Assuming a program that ran without errors under the compiler was compiled as one graph overlooks silent breaks, which are reported only when logging is enabled.

**How to verify.** Enable graph-break reporting, for example `torch._dynamo.explain`, and record the number of graphs and the reason for each break.

## Exercise 4: Specify an accepted shape set

List bounded dimensions and dtypes.

**Approach.** Specify the accepted shape set explicitly, such as batch sizes 4 and 8 with a fixed feature width 8 and float32 dtype, and reject or pad other inputs.

**Why it is correct here.** A bounded set keeps compilation count bounded and predictable. Padding inputs to the nearest accepted size trades some wasted work for avoiding new compilations.

**A plausible wrong approach.** Accepting arbitrary shapes in production lets each new batch size trigger a recompilation, causing latency spikes.

**How to verify.** Send an input outside the set and confirm it is rejected or padded, and that the compile count stays at the expected value.

## Exercise 5: Compare gradients

Forward agreement does not imply backward agreement.

**Approach.** Compare gradients between compiled and eager execution, not only forward outputs, by computing `backward()` in both and comparing parameter gradients with a tolerance.

**Why it is correct here.** Compilers transform the backward graph separately and may fuse or reorder its operations. A forward match says nothing about backward correctness.

**A plausible wrong approach.** Checking only that forward outputs match and assuming gradients follow can miss a backward bug that shows up only as slower training.

**How to verify.** Use the same inputs and initial parameters for both modes and compare every gradient tensor within float32 tolerance.

## Exercise 6: Separate compilation and replay

Compilation creates code while replay reuses an execution schedule.

**Approach.** Separate compilation, which generates and optimizes kernels for a shape, from CUDA graph replay, which records a fixed sequence of launches and reissues it with low launch overhead.

**Why it is correct here.** Replay requires static shapes and fixed memory addresses. It reduces CPU launch cost but does not by itself change the kernels.

**A plausible wrong approach.** Expecting graph replay to speed up compute-bound kernels confuses launch overhead with kernel time.

**How to verify.** Profile a step before and after enabling graph capture and compare host launch time and kernel time separately.

## Reference observation

Two modeled specializations;500-call break-even.

The reference file is `courses/cuda/python/references/cuda-093_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
