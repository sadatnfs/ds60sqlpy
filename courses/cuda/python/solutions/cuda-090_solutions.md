# cuda-090: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate scaled and unscaled values

Apply inverse scale exactly once.

**Approach.** Trace the scaled value: a gradient of 0.5 multiplied by scale 1024 becomes 512 during backpropagation, and dividing by 1024 once before the optimizer step restores 0.5.

**Why it is correct here.** Loss scaling multiplies the loss so small gradients stay representable in float16, and every gradient is scaled by the same factor. Unscaling exactly once gives the true gradient.

**A plausible wrong approach.** Unscaling twice, once manually and once by the scaler, produces `0.5/1024`, an update so small that training appears to stall without any error.

**How to verify.** Compute `512/1024 == 0.5` by hand. In PyTorch, call `scaler.unscale_(optimizer)` and inspect `p.grad` for a known small model, comparing with a float32 run.

## Exercise 2: Explain overflow detection

Skip or adjust updates according to the supported scaler when nonfinite.

**Approach.** Explain overflow handling: when scaled gradients contain infinity or NaN, the supported scaler skips the optimizer step and lowers the scale, then raises it again after a run of finite steps.

**Why it is correct here.** A scale large enough to prevent underflow can overflow float16, whose largest finite value is 65504. Skipping the update avoids writing nonfinite values into parameters.

**A plausible wrong approach.** Replacing infinities with zero, or clipping them, so the step can proceed corrupts the update with values unrelated to the true gradient.

**How to verify.** Force an overflow with a very large scale on a tiny model and confirm the parameters are unchanged after the step and the scale decreased.

## Exercise 3: Place clipping correctly

Unscale before clipping.

**Approach.** Unscale before clipping: with gradient 0.5, unscaling 512 gives 0.5, and clipping to threshold 1 leaves 0.5, which is the intended clipped gradient.

**Why it is correct here.** Clipping thresholds are defined in units of the true gradient. The reference computes `min(scaled/scale, 1.0) == 0.5` for the correct order.

**A plausible wrong approach.** Clipping the scaled 512 to 1 and then unscaling gives `1/1024 = 0.0009765625`, the wrong value the reference asserts for the reversed order. Training then barely moves.

**How to verify.** Run the reference and confirm both assertions. In code, check that `unscale_` appears before `clip_grad_norm_`.

## Exercise 4: Compare fp16 and bf16 concepts

Their exponent and mantissa allocations differ.

**Approach.** Compare float16 and bfloat16: float16 has 5 exponent bits and 10 mantissa bits, while bfloat16 has 8 exponent bits, the same as float32, and 7 mantissa bits.

**Why it is correct here.** bfloat16 covers the float32 range, so gradients rarely underflow and loss scaling is usually unnecessary, but it has less precision. float16 is more precise but has a narrow range.

**A plausible wrong approach.** Assuming both 16-bit formats behave the same leads to dropping loss scaling for float16, where small gradients flush to zero.

**How to verify.** Cast `1e-8` to both types: float16 gives 0, bfloat16 keeps a nonzero value. Cast `1 + 2**-9`: float16 keeps it, bfloat16 rounds to 1.

## Exercise 5: Design a full-precision baseline

Use same initialization batch and loss.

**Approach.** Run a float32 baseline with the same initialization, batches, loss and number of steps, and compare loss curves and final metrics with the mixed-precision run.

**Why it is correct here.** Only a matched baseline can show whether reduced precision changed the training outcome. Differences in seeds or data order would otherwise be confused with precision effects.

**A plausible wrong approach.** Comparing the mixed-precision run with an older float32 run using a different seed attributes noise to precision.

**How to verify.** Record seed, data order and step count for both runs and require the final loss to fall within an agreed tolerance.

## Exercise 6: Record quality and throughput separately

A speed improvement cannot excuse numerical failure.

**Approach.** Record quality metrics, such as final loss and validation accuracy, separately from throughput, such as samples per second, for both precision settings.

**Why it is correct here.** Mixed precision can raise throughput while degrading quality. A combined score hides which side changed.

**A plausible wrong approach.** Reporting the speedup without the quality comparison can justify a configuration that fails to train properly.

**How to verify.** Present a table with both metrics per configuration, and accept mixed precision only if quality meets the baseline tolerance.

## Reference observation

Correct gradient 0.5; incorrect clipping order yields 0.0009765625.

The reference file is `courses/cuda/python/references/cuda-090_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
