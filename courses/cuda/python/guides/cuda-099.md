# cuda-099: Memory-saving training techniques

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-089`, `cuda-090`, `cuda-094`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute weighted accumulation.
- Find unequal-batch normalization error.
- Place optimizer steps.
- Explain checkpoint recomputation.
- Account for frozen weights.
- Design equal-update tests.

## Mechanism and vocabulary

Gradient accumulation splits an effective batch across microbatches and delays the optimizer step. To match a full mean-loss gradient, weight each microbatch by its number of examples divided by the total. Equal division by microbatch count works only when sizes are equal. Batch-dependent layers, random state and optimizer timing can still break equivalence.

Activation checkpointing saves selected intermediates and recomputes others during backward. It exchanges compute for memory rather than eliminating arithmetic. PyTorch checkpoint utilities and TensorFlow recomputation mechanisms have framework-specific state and randomness rules. Frozen parameters still occupy storage, and upstream activations may remain necessary for trainable downstream components. Compare updates first, then measured peak memory and time.



### Key terms

- **Gradient accumulation:** Summing gradients over several microbatches before one optimizer step to emulate a larger batch.
- **Microbatch weighting:** Scaling each microbatch loss so the accumulated gradient equals the average over the full batch.
- **Activation checkpointing:** Discarding selected activations in forward and recomputing them in backward to trade compute for memory.
- **Frozen weights:** Parameters with gradient tracking disabled, which need no gradient or optimizer-state memory.

## Worked examples

### Worked example 1

Microbatch mean gradients 2 and 8 over sizes 3 and 1 combine to \((3\times2+1\times8)/4=3.5\). Averaging the two means gives 5, which is wrong for the effective batch.

### Worked example 2

Checkpointing reduces retained activations by an illustrative 20 MiB but adds another forward computation. Its benefit depends on memory pressure and the recomputation cost.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-099_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-099_cpu.py
```

```python
sizes, means = [3, 1], [2.0, 8.0]
weighted = sum(n * g for n, g in zip(sizes, means, strict=True)) / sum(sizes)
wrong = sum(means) / len(means)
assert weighted == 3.5 and wrong == 5
print("CPU accumulation oracle:", weighted, wrong)
```

**Expected observation:** Correct weighted gradient 3.5 versus incorrect 5.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `sizes` | `[3, 1]` |
| `means` | `[2.0, 8.0]` |
| `weighted` | `3.5` |
| `wrong` | `5.0` |

## Equal framework lanes

### PyTorch

Normalize each microbatch contribution by total effective examples and step once. Evaluate checkpoint recomputation separately, including random-state and nonreentrant/reentrant API choices for the pinned release.

### TensorFlow

Accumulate GradientTape gradients with example-count weighting. Use the prepared recomputation mechanism only after checking variable capture and stateful behavior; evaluate memory and extra forward work separately.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-099.md) before opening hints.

### Exercise 1: Compute weighted accumulation

**Trap to avoid:** Averaging the two means, `(2 + 8)/2 = 5`, gives the single example in the second microbatch the same weight as the three in the first, so it counts three times as much as it should.

### Exercise 2: Find unequal-batch normalization error

**Trap to avoid:** Trusting that the loop is right because it matches the full-batch gradient on evenly divisible data hides the error, which only appears for an uneven final microbatch.

### Exercise 3: Place optimizer steps

**Trap to avoid:** Calling `zero_grad()` inside the microbatch loop discards earlier contributions, so only the last microbatch affects the update.

### Exercise 4: Explain checkpoint recomputation

**Trap to avoid:** Checkpointing every layer when memory is not the constraint adds recomputation with no benefit.

### Exercise 5: Account for frozen weights

**Trap to avoid:** Assuming a frozen model costs nothing in memory leads to under-budgeting by the full parameter size.

### Exercise 6: Design equal-update tests

**Trap to avoid:** Running the comparison with dropout enabled and different seeds produces differences that hide or mimic accumulation bugs.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Weight each microbatch mean by its example count, add the products and divide by the total count.
2. Average the two microbatch means without weights and compare the result with the full-batch mean gradient.
3. Count the microbatches in one effective batch and place exactly one optimizer step after the last.
4. Ask which intermediates backward needs, which were discarded and what must run again to recreate them.
5. Ask whether a parameter with no gradient still has to be stored on the device.
6. List everything that must match between the accumulated and full-batch runs: data order, reduction, state and randomness.

## Common mistakes and self-check

The classic mistake is averaging microbatch mean gradients equally when microbatch sizes differ. Means 2 and 8 over sizes 3 and 1 give 5 that way, but the correct effective-batch gradient is 3.5. Another mistake is stepping the optimizer after every microbatch. Fix both by weighting each microbatch by its share of examples and stepping once per effective batch, then confirming equal updates against a full batch before comparing memory or time.

**Evidence limit:** The reference computes 3.5 against 5 with ordinary arithmetic. It does not run accumulation or activation checkpointing in a framework, so batch-dependent layers, random state and real peak memory must be checked with the pinned PyTorch or TensorFlow lane.

1. When is dividing by the microbatch count correct?
2. What does activation checkpointing trade?
3. Can accumulation still differ from a full batch when weights are right?

Answers: [self-check answers](../solutions/cuda-099_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-099: Memory-saving training techniques.
Read courses/cuda/python/guides/cuda-099.md and courses/cuda/python/lessons/cuda-099.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
