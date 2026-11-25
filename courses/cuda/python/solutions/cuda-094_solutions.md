# cuda-094: explained solutions

Compare with your [worksheet](../lessons/cuda-094.md) attempt.

## Exercise 1: List checkpoint fields

Include all state affecting the next update.

**Approach.** List every field that affects the next update: model weights, optimizer state such as the momentum buffer `v`, the learning-rate scheduler state, the gradient scaler state, the step counter, random generator states and the position of the data sampler.

**Why it is correct here.** Exact continuation means the resumed run computes the same next update as the uninterrupted run. Any omitted field that influences that update makes the two runs diverge.

**A plausible wrong approach.** Saving only `model.state_dict()` because that is what inference needs leaves out optimizer and sampler state, which training needs.

**How to verify.** Save, reload, take one step, and compare with one step of the uninterrupted run. Every saved field should be justified by a change it causes when omitted.

## Exercise 2: Compute momentum continuation

Carry the previous velocity.

**Approach.** Carry the velocity through the restart: with `w = 1.0`, `v = 0.5` and gradient 0.2, the next velocity is `0.9*0.5 + 0.2 = 0.65` and the new weight is `1.0 - 0.1*0.65 = 0.935`.

**Why it is correct here.** Momentum SGD updates `v = 0.9*v + g` and then `w = w - lr*v`, so the previous velocity contributes `0.45` of the step. The reference asserts the continued weight is 0.935.

**A plausible wrong approach.** Recomputing velocity from the current gradient alone, `v = g`, gives `1.0 - 0.1*0.2 = 0.98`, the weights-only value, which ignores accumulated history.

**How to verify.** Check `abs(continued - 0.935) < 1e-12` from the reference and that it differs from `weights_only`.

## Exercise 3: Diagnose weights-only restart

The optimizer trajectory changes.

**Approach.** Diagnose a weights-only restart: velocity restarts at zero, so the first resumed step moves `w` to 0.98 instead of 0.935, and the trajectory differs from then on.

**Why it is correct here.** The momentum state is part of the optimizer trajectory. Resetting it produces a different, slower update after each restart, so training curves show a visible discontinuity.

**A plausible wrong approach.** Treating the difference as random noise from reloading misses that it is deterministic: the same restart always produces the same wrong value.

**How to verify.** Compare the first resumed step with the uninterrupted step. A difference equal to `lr*0.9*v`, 0.045 here, identifies the missing velocity.

## Exercise 4: Record sampler position

Persist the next unconsumed example or reproducible sampler state.

**Approach.** Persist the sampler position, such as the next unconsumed batch index 3 or the sampler's random state plus epoch, so the resumed run starts at batch 3.

**Why it is correct here.** A checkpoint taken after batch 2 represents a model that has seen batches 1 and 2. Resuming at batch 3 preserves exact data exposure.

**A plausible wrong approach.** Restarting the epoch from the beginning replays batches 1 and 2, which double counts them, while skipping to a new shuffle may omit batch 3 entirely.

**How to verify.** Record the batch indices consumed before and after resume and assert their union is one complete pass with no repeats.

## Exercise 5: Choose a safe save boundary

Save after a completed consistent optimizer step.

**Approach.** Save only at a boundary after a completed optimizer step, when weights, optimizer state and step counter are all consistent, not between `backward()` and `optimizer.step()`.

**Why it is correct here.** Between backward and step, gradients exist but weights do not yet reflect them. A checkpoint there pairs updated statistics with old weights or loses gradients entirely.

**A plausible wrong approach.** Saving from a signal handler at an arbitrary moment can capture a half-updated state.

**How to verify.** Add a check that the saved step counter equals the number of completed optimizer steps, and resume from a checkpoint to confirm the next step matches.

## Exercise 6: Define cross-hardware tolerance

Document numerical agreement rather than universal byte equality.

**Approach.** Define tolerance for resuming on different hardware: document an expected agreement, such as relative difference below a stated threshold on loss after N steps, instead of byte equality.

**Why it is correct here.** Different GPUs and libraries may choose different kernels and summation orders, so floating results differ slightly even with identical state.

**A plausible wrong approach.** Requiring byte-identical weights across hardware leads to false failures that obscure real restart bugs.

**How to verify.** Resume the same checkpoint on two machines and compare loss curves within the documented tolerance, recording both environments.

## Self-check answers

1. **Why save at an update boundary?** Partially accumulated gradients are ambiguous to restore unless the format explicitly handles them, while a completed step is consistent.

2. **Does a checkpoint restore a running GPU context?** No. It restores numerical training state, not a live context, an in-flight stream or allocator contents.

3. **Why must checkpoint storage outlive the training process?** The process is disposable; a restart can only continue if the saved state survives the process that wrote it.

## Reference observation

Correct restored update 0.935 differs from weights-only 0.98.

Asserted by `courses/cuda/python/references/cuda-094_cpu.py`.
