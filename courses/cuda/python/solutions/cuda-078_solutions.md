# cuda-078: explained solutions

Compare with your [worksheet](../lessons/cuda-078.md) attempt.

## Exercise 1: Trace a lost update

Two readers can overwrite one another.

**Approach.** Trace two threads incrementing bin 0, which holds 2: both read 2, both compute 3, both store 3. The final count is 3, although two updates happened.

**Why it is correct here.** A non-atomic increment is a read, an add and a write. If both reads happen before either write, the second write overwrites the first with the same value, and one increment disappears.

**A plausible wrong approach.** Assuming the two writes collide in a visible way, raising an error or producing a garbled value, is incorrect. The lost update produces a plausible number, which is why it escapes notice.

**How to verify.** Write the interleaving as a table of read, add and write steps per thread. The final value must be 3, while an atomic or serial version gives 4.

## Exercise 2: Compute a skewed histogram

Six zeros yield count 6 in bin 0.

**Approach.** Compute the histogram of `[0, 0, 0, 0, 0, 0]` with three bins: bin 0 holds 6 and the others hold 0.

**Why it is correct here.** Every update targets bin 0, so this input is the worst case for contention. Correctness is easy to state, while performance depends on serialization at one counter.

**A plausible wrong approach.** Using the uniform data `[0, 1, 2, 0, 1, 2]` as the contention test spreads updates evenly and measures the friendliest case instead.

**How to verify.** Run the reference loop on the six zeros and assert `bins == [6, 0, 0]`. The total of the bins must equal the input length, 6.

## Exercise 3: Merge partials

Add corresponding bins.

**Approach.** Merge per-block histograms by adding matching bins: `[2, 1, 0] + [0, 0, 3]` gives `[2, 1, 3]`.

**Why it is correct here.** Each partial counts a disjoint subset of the input, so the full count for a bin is the sum of the partial counts. The reference asserts the merged list equals the direct histogram.

**A plausible wrong approach.** Concatenating the partials or taking the bin-wise maximum produces wrong totals. The maximum here gives `[2, 1, 3]` by coincidence, so test with overlapping partials such as `[1, 1, 0]` and `[1, 0, 3]`.

**How to verify.** Use `zip(left, right, strict=True)` so different bin counts raise an error. Check that the sum of the merged bins equals the input length.

## Exercise 4: Count private storage

Partials times bins times counter width.

**Approach.** Compute private storage as partials times bins times counter width. For 1024 block partials, 256 bins and 4-byte counters, that is `1024*256*4 = 1048576` bytes.

**Why it is correct here.** Privatization trades memory for reduced contention, since every partial needs a full copy of the bins. The cost grows linearly with each factor.

**A plausible wrong approach.** Counting only bins times width, 1 KiB here, ignores that each partial owns its own copy and underestimates memory by a factor of the partial count.

**How to verify.** Recompute the product and confirm 1 MiB. Then halve the number of partials and confirm the bytes halve.

## Exercise 5: Explain floating atomic order

Atomicity does not fix addition order.

**Approach.** Explain that `atomic.add` on a float accumulator makes each addition indivisible but leaves the order of additions to the scheduler, so rounding may differ between runs.

**Why it is correct here.** Floating addition is not associative. Different arrival orders round at different points, so atomic sums are correct within rounding but not bitwise reproducible.

**A plausible wrong approach.** Expecting atomics to give the same bits as a sequential CPU sum confuses race-freedom with order. No update is lost, but the order is still free.

**How to verify.** Sum values of very different magnitudes atomically several times and compare the last bits. Integer counters give identical results every time.

## Exercise 6: Specify completion before reading

Wait for all updates and merges before host retrieval.

**Approach.** Before reading bins on the host, wait for the histogram kernel and the merge to finish, for example with `cuda.synchronize()` or an implicit synchronization in a device-to-host copy on the same stream.

**Why it is correct here.** Launches are asynchronous. Reading the bins before the merge completes can return partial counts.

**A plausible wrong approach.** Reading after only the histogram kernel ignores the merge step, so the host sees one block's partial instead of the total.

**How to verify.** Assert that the copied bins sum to the input length. A smaller total signals that the read happened before all updates completed.

## Self-check answers

1. **What exactly does an atomic addition protect?** One supported memory location against lost updates from competing atomic operations. It does not make a multi-location update transactional.

2. **What does privatization trade away to reduce contention?** Extra storage for per-block or per-warp histograms and an additional merge step.

3. **Why can floating-point atomic sums vary between runs?** Atomicity prevents lost updates, but the order of additions follows thread arrival, and floating-point rounding depends on that order.

## Reference observation

Histogram bins [2,1,3].

Asserted by `courses/cuda/python/references/cuda-078_cpu.py`.
