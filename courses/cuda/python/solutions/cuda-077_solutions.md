# cuda-077: explained solutions

Compare with your [worksheet](../lessons/cuda-077.md) attempt.

## Exercise 1: Compute a tree by hand

Combine pairs and carry the leftover value.

**Approach.** Compute the pair tree for `[1, 2, 3, 4, 5]` by hand: level one gives `[3, 7, 5]` with 5 carried, level two gives `[10, 5]`, level three gives `[15]`.

**Why it is correct here.** The reference loop sums slices `items[i:i+2]`, so an odd element forms a one-item slice and passes to the next level. Each level halves the count, rounding up, until one value remains.

**A plausible wrong approach.** Pairing only `range(0, len(items) - 1, 2)` drops the odd element at each odd level. For this input the result becomes 10 and the error looks small enough to mistake for rounding.

**How to verify.** Write each level and confirm the sum is preserved at every step: 15, 15, 15. The reference asserts `items == [15]`.

## Exercise 2: Test the odd tail

The fifth value must survive.

**Approach.** Add a test whose last element is distinctive, such as `[1, 2, 3, 4, 5]`, and assert the result is 15, not 10.

**Why it is correct here.** Ignoring the tail removes exactly the fifth value, so the faulty total differs by 5. A large, exact gap with integer inputs is an indexing bug; rounding errors cannot produce it.

**A plausible wrong approach.** Using a tolerance like `abs(result - 15) < 10` would accept 10. Picking tolerances that wide hides structural bugs inside numerical noise.

**How to verify.** Compare with exact equality, since integer sums are exact in floating point at this size. Repeat with seven elements to check that two carry steps also work.

## Exercise 3: Construct cancellation

Use large opposite signs plus a small residual.

**Approach.** Use `[1e16, 1.0, -1e16]`: a left-to-right float64 sum computes `1e16 + 1.0`, which rounds back to `1e16`, then subtracts to 0, while `math.fsum` returns 1.0.

**Why it is correct here.** Doubles have 53 bits of mantissa, so near `1e16` the spacing between representable numbers is 2. Adding 1 is lost in rounding. The true sum is 1, which fsum tracks exactly with extra partials.

**A plausible wrong approach.** Using `[1.0, 2.0, 3.0]` as the cancellation test shows nothing, since every order gives 6 exactly. A test needs magnitudes far enough apart to exceed the mantissa.

**How to verify.** Assert `sum(values) == 0.0` and `math.fsum(values) == 1.0` on standard IEEE doubles. The reference asserts the fsum result.

## Exercise 4: Choose absolute and relative tolerance

Near zero needs meaningful absolute tolerance.

**Approach.** Compare GPU and CPU sums with `abs(a - b) <= atol + rtol * abs(b)`, choosing `rtol` from the dtype and the number of terms and an `atol` that reflects the scale of the inputs when the expected value is near zero.

**Why it is correct here.** Relative tolerance scales with the expected value. When cancellation makes the expected result 1 or 0 while the terms are about 1e16, rounding error is proportional to the terms, so only an absolute term sized to them is meaningful.

**A plausible wrong approach.** Using relative tolerance alone with an expected value of 0 requires exact equality. Any reordering then fails, even though both answers are within normal rounding of the large terms.

**How to verify.** Compute the bound for the cancellation input and confirm 0 and 1 both fit when `atol` reflects the term magnitude. Confirm an indexing error like 10 versus 15 still falls outside.

## Exercise 5: Compare atomics with staged reduction

Atomics trade simplicity for contention and order.

**Approach.** Contrast `cuda.atomic.add` on one global accumulator with a staged reduction: per-block shared-memory trees followed by a final pass over block partials.

**Why it is correct here.** Atomics are short to write, but every thread serializes on one address, and the order of floating additions depends on scheduling. A staged tree has fixed pairing within each block and far fewer global updates.

**A plausible wrong approach.** Claiming the atomic version is deterministic because each update is indivisible confuses atomicity with order. Each addition is safe, but the sequence of additions still varies.

**How to verify.** For integer inputs both must give the identical total. For float32 inputs, run the atomic version several times and look for differences in the last bits, while the staged version with a fixed launch stays stable.

## Exercise 6: Explain deterministic settings limits

Repeatability does not imply cross-hardware identical arithmetic.

**Approach.** Explain that deterministic library settings fix the order of operations for one configuration, but changing GPU model, library version or launch configuration may still change the floating-point result.

**Why it is correct here.** Determinism guarantees repeatable results on the same software, hardware and inputs. Different hardware can choose different kernels, block counts or fused multiply-add usage, which changes rounding.

**A plausible wrong approach.** Treating a deterministic flag as a promise of identical results across machines leads to bit-exact comparisons between environments that fail for legitimate reasons.

**How to verify.** Record the environment with each result. Expect bit-identical answers only within one environment, and use a tolerance when comparing across environments.

## Self-check answers

1. **Why can a tree reduction differ from a left-to-right loop?** Floating-point addition is not associative, and the tree groups additions differently. Both can be valid implementations with different rounding.

2. **How do you tell rounding noise from a missing element?** Rounding noise is small relative to the data's scale. A missing element changes the sum by that element's value, like 10 instead of 15.

3. **Why does a sum near zero need an absolute tolerance?** A relative tolerance scales with the expected value, so it shrinks to almost nothing near zero and rejects acceptable rounding.

## Reference observation

Accurate cancellation sum 1 and tail-preserving sum 15.

Asserted by `courses/cuda/python/references/cuda-077_cpu.py`.
