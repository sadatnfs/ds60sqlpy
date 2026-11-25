# cuda-099: explained solutions

Compare with your [worksheet](../lessons/cuda-099.md) attempt.

## Exercise 1: Compute weighted accumulation

Use sample-count weights.

**Approach.** Weight each microbatch mean gradient by its sample count: `(3*2 + 1*8) / (3 + 1) = 14/4 = 3.5`.

**Why it is correct here.** The effective-batch gradient is the mean over all four examples. Microbatch means already divide by their own sizes, so multiplying back by the sizes recovers the sums before dividing by the total.

**A plausible wrong approach.** Averaging the two means, `(2 + 8)/2 = 5`, gives the single example in the second microbatch the same weight as the three in the first, so it counts three times as much as it should.

**How to verify.** The reference asserts `weighted == 3.5` and `wrong == 5`. Compare with the mean gradient of one batch containing all four examples.

## Exercise 2: Find unequal-batch normalization error

Do not average unequal means blindly.

**Approach.** Find the normalization error in an accumulation loop that divides each microbatch loss by the number of microbatches regardless of their sizes, which equals averaging unequal means.

**Why it is correct here.** Dividing by the microbatch count is correct only when all microbatches have the same size. A short final microbatch then gets too much weight in every epoch.

**A plausible wrong approach.** Trusting that the loop is right because it matches the full-batch gradient on evenly divisible data hides the error, which only appears for an uneven final microbatch.

**How to verify.** Test with sizes 3 and 1 and compare the accumulated gradient with 3.5. Scaling each loss by `size/total` fixes it, and the test should then pass.

## Exercise 3: Place optimizer steps

Step once per effective batch.

**Approach.** Place `optimizer.step()` and `optimizer.zero_grad()` once per effective batch, after the last microbatch's `backward()`, not after each microbatch.

**Why it is correct here.** Gradients accumulate in `.grad` across backward calls. Stepping after each microbatch applies several smaller updates with different parameters, which is a different algorithm from one large-batch update.

**A plausible wrong approach.** Calling `zero_grad()` inside the microbatch loop discards earlier contributions, so only the last microbatch affects the update.

**How to verify.** Count optimizer steps per epoch and confirm it equals the number of effective batches. Compare the updated weights with a single full-batch step.

## Exercise 4: Explain checkpoint recomputation

Recompute discarded intermediates during backward.

**Approach.** Explain activation checkpointing: selected layers discard their intermediate activations after the forward pass and recompute them during backward from saved inputs.

**Why it is correct here.** Memory falls because only the segment inputs stay alive, an illustrative 20 MiB saved in the lesson's example, but each checkpointed segment runs its forward computation twice.

**A plausible wrong approach.** Checkpointing every layer when memory is not the constraint adds recomputation with no benefit.

**How to verify.** Measure peak allocated memory and step time with checkpointing on and off. Gradients must match within tolerance, since recomputation changes time but not the math.

## Exercise 5: Account for frozen weights

Freezing gradients does not remove parameters.

**Approach.** Account for frozen weights: setting `requires_grad=False` removes gradient and optimizer state for those parameters, but the parameters themselves stay in memory.

**Why it is correct here.** Freezing saves gradient storage and optimizer moments, three times the parameter bytes for Adam, but the forward pass still reads every frozen weight.

**A plausible wrong approach.** Assuming a frozen model costs nothing in memory leads to under-budgeting by the full parameter size.

**How to verify.** Compare allocated memory before and after freezing and confirm the reduction matches gradient plus optimizer bytes while parameter bytes remain.

## Exercise 6: Design equal-update tests

Match data order loss reduction state and random behavior.

**Approach.** Design tests for equal updates: compare accumulated microbatch training with full-batch training using the same data order, loss reduction, initial state and disabled randomness such as dropout.

**Why it is correct here.** Accumulation is meant to reproduce the large-batch update. Holding every other factor fixed isolates the accumulation logic.

**A plausible wrong approach.** Running the comparison with dropout enabled and different seeds produces differences that hide or mimic accumulation bugs.

**How to verify.** Assert weights after one effective step agree within float tolerance, and repeat with an uneven final microbatch.

## Self-check answers

1. **When is dividing by the microbatch count correct?** Only when every microbatch has the same number of examples; otherwise weights must follow example counts.

2. **What does activation checkpointing trade?** Memory for compute: discarded intermediates are recomputed during backward, so arithmetic increases.

3. **Can accumulation still differ from a full batch when weights are right?** Yes. Batch-dependent layers such as batch normalization, random state and optimizer timing can break the equivalence.

## Reference observation

Correct weighted gradient 3.5 versus incorrect 5.

Asserted by `courses/cuda/python/references/cuda-099_cpu.py`.
