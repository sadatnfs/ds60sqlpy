# cuda-069: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Predict repeated seeding

Repeated initialization repeats the sequence.

**Approach.** Predict that two fresh generators seeded with 7, or one generator reseeded with 7, produce the same first draws. Reseeding resets the stream to its start.

**Why it is correct here.** A seeded pseudo-random generator is deterministic: the seed fixes the internal state, and the state fixes every subsequent draw. Worked example 1 shows two `Random(7)` objects agreeing on four draws.

**A plausible wrong approach.** Reseeding inside a training loop each step to get reproducibility makes every step see the same random numbers, so dropout masks or shuffles repeat and the experiment loses its randomness.

**How to verify.** Create `random.Random(7)` twice and compare the first four `random()` values; they must be equal. Then reseed one mid-stream and confirm it returns to the first value.

## Exercise 2: Continue a stream

Retain the generator between batches.

**Approach.** Keep one generator object alive across batches and draw from it; the second batch continues the stream instead of repeating the first.

**Why it is correct here.** The reference draws `first`, then `second` from the same object and asserts `first != second`. The state after batch one is the starting point for batch two.

**A plausible wrong approach.** Creating a new generator per batch with the same seed makes each batch identical. Creating one per batch with `seed + batch` gives distinct but correlated-by-construction streams that are harder to reason about.

**How to verify.** Run the cuda-069 reference and check that `first != second` holds. Record the first value of each batch to show the continuation.

## Exercise 3: Restore generator state

Save state before drawing.

**Approach.** Call `rng.getstate()` before drawing a batch, and later call `rng.setstate(saved)` to replay exactly that batch.

**Why it is correct here.** The state captures the whole generator, not just the seed. The reference saves state, draws `first`, draws `second`, restores, and asserts the replay equals `first`.

**A plausible wrong approach.** Saving state after drawing the batch captures the position for the next batch. Restoring it replays `second`, not `first`, which is an off-by-one in time.

**How to verify.** In the reference, the assertion `first == [rng.random() for _ in range(4)]` after `setstate` is the check. It passes only if state was saved before the first draw.

## Exercise 4: Design a distribution check

Check sample mean and variance with tolerances.

**Approach.** For a large sample, compare the sample mean and variance with the distribution's known values within a tolerance. For uniform on [0, 1), the mean is 0.5 and variance 1/12.

**Why it is correct here.** Different backends implement different generators, so draw-by-draw equality is not a fair test across CPU and GPU. Statistical moments are a property every correct uniform generator shares.

**A plausible wrong approach.** Requiring exact equality between CuPy and Python random draws fails even when both are correct, because their algorithms differ. Using a tolerance tighter than sampling error also fails randomly.

**How to verify.** Draw 100000 values, compute mean and variance, and accept if each is within a tolerance chosen from sampling error, for example about `0.0037` for the mean (four times `0.2887 / sqrt(100000)`) at four standard errors. Record seed and sample size.

## Exercise 5: Separate backend equality from exact bytes

Use numeric or statistical contracts.

**Approach.** Write the contract as numeric or statistical agreement across backends, and reserve exact-byte equality for replays within the same backend, version and seed.

**Why it is correct here.** Worked example 2 notes that restoring Python state does not make CuPy or TensorFlow produce the same values. Their generators and parallel streams are different algorithms.

**A plausible wrong approach.** Hashing the output bytes of a CPU run and a GPU run and calling the mismatch a bug wastes debugging time on something that is not a defect.

**How to verify.** Verify within-backend replay by comparing bytes for the same seed twice. Verify cross-backend agreement with the moment test or with a downstream metric tolerance.

## Exercise 6: List checkpoint randomness

Include Python, NumPy, framework, device and sampler state.

**Approach.** List every source of randomness a resumed run needs: Python `random` state, NumPy generator state, the framework CPU and per-device generator states, and the data sampler or shuffler state.

**Why it is correct here.** Training uses several generators at once. Restoring only the Python state, as in this chapter's reference, replays Python draws but not GPU dropout or the order the sampler yields batches.

**A plausible wrong approach.** Saving only the initial seed and reseeding on resume restarts the streams at the beginning, so the resumed run repeats the first epoch's shuffles instead of continuing.

**How to verify.** Checkpoint, resume, and compare the next batch indices and a dropout mask with an uninterrupted run under the same backend. Both must match for the checkpoint to be complete.

## Reference observation

Restored batch matches and continued batch differs.

The reference file is `courses/cuda/python/references/cuda-069_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
