# cuda-078: Atomics and contention

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-076`, `cuda-077`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Trace a lost update.
- Compute a skewed histogram.
- Merge partials.
- Count private storage.
- Explain floating atomic order.
- Specify completion before reading.

## Mechanism and vocabulary

An atomic operation updates one supported location indivisibly with respect to competing atomic operations. It does not make an entire multi-location algorithm transactional. A histogram demonstrates the need: two threads reading count 0 and both writing count 1 lose an increment. Atomic addition prevents that lost update for the counter, but every thread targeting the same bin can serialize.

Privatization reduces contention by building per-block or per-warp partial histograms and merging them later. The memory footprint grows with bin count and number of partials. Floating-point atomic addition can still vary with arrival order. Explain what is protected, what ordering is required, and whether non-atomic readers can observe partially completed results.



### Key terms

- **Atomic operation:** A read-modify-write that the hardware completes as one indivisible step, so concurrent updates are not lost.
- **Lost update:** A race in which two threads read the same old value and one thread's write overwrites the other.
- **Privatization:** Giving each block its own partial result, usually in shared memory, then merging the partials with fewer global atomics.
- **Contention:** Many threads updating the same address at once, which serializes atomics and reduces throughput.

## Worked examples

### Worked example 1

Values [0,0,1,2,2,2] produce bins [2,1,3]. Six updates aimed at one bin would be a deliberately skewed contention case.

### Worked example 2

Two local histograms [2,1,0] and [0,0,3] merge elementwise to [2,1,3]. Local updates reduce shared contention at the expense of extra storage and a merge.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-078_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-078_cpu.py
```

```python
values = [0, 0, 1, 2, 2, 2]
bins = [0] * 3
for value in values:
    bins[value] += 1
left, right = [2, 1, 0], [0, 0, 3]
merged = [a + b for a, b in zip(left, right, strict=True)]
assert bins == merged == [2, 1, 3]
print("CPU histogram oracle:", bins)
```

**Expected observation:** Histogram bins [2,1,3].

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `values` | `[0, 0, 1, 2, 2, 2]` |
| `bins` | `[2, 1, 3]` |
| `value` | `2` |
| `left` | `[2, 1, 0]` |
| `right` | `[0, 0, 3]` |
| `merged` | `[2, 1, 3]` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-078.md) before opening hints.

### Exercise 1: Trace a lost update

**Trap to avoid:** Assuming the two writes collide in a visible way, raising an error or producing a garbled value, is incorrect. The lost update produces a plausible number, which is why it escapes notice.

### Exercise 2: Compute a skewed histogram

**Trap to avoid:** Using the uniform data `[0, 1, 2, 0, 1, 2]` as the contention test spreads updates evenly and measures the friendliest case instead.

### Exercise 3: Merge partials

**Trap to avoid:** Concatenating the partials or taking the bin-wise maximum produces wrong totals. The maximum here gives `[2, 1, 3]` by coincidence, so test with overlapping partials such as `[1, 1, 0]` and `[1, 0, 3]`.

### Exercise 4: Count private storage

**Trap to avoid:** Counting only bins times width, 1 KiB here, ignores that each partial owns its own copy and underestimates memory by a factor of the partial count.

### Exercise 5: Explain floating atomic order

**Trap to avoid:** Expecting atomics to give the same bits as a sequential CPU sum confuses race-freedom with order. No update is lost, but the order is still free.

### Exercise 6: Specify completion before reading

**Trap to avoid:** Reading after only the histogram kernel ignores the merge step, so the host sees one block's partial instead of the total.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Interleave two threads' read, add and write steps on one counter that starts at 0 and record the final value.
2. Route all six inputs to the same bin and ask how many updates that bin's counter must absorb.
3. Line up the two local histograms bin by bin and add the matching counters.
4. Multiply the number of partial histograms, the bin count and the bytes per counter.
5. Ask whether atomic float additions arriving in a different order must give the same rounded total.
6. Decide what must finish, including the merge, before the host may read the counts.

## Common mistakes and self-check

A common mistake is assuming an atomic makes a whole algorithm safe. Atomic addition protects one counter from lost updates, but it does not order other memory, and a non-atomic reader can still see a half-merged histogram. Another mistake is sending every thread to one shared bin, which serializes the updates. Fix contention with per-block private histograms merged later, and read the result only after every update and merge has completed.

**Misconception:** Floating-point atomic addition always produces the same total because no update is lost. **Correction:** Atomics prevent lost updates, but they do not fix the order in which updates arrive. Floating-point addition is not associative, so a float sum accumulated with atomics can differ in its last bits between runs. Integer counts such as histogram bins are exact; for float totals, state a tolerance or use a deterministic reduction order when bitwise repeatability is required.

**Evidence limit:** The reference computes bins `[2, 1, 3]` and merges two partial histograms sequentially. It cannot exhibit a lost update, contention or arrival-order rounding, which only occur when real threads race on a device.

1. What exactly does an atomic addition protect?
2. What does privatization trade away to reduce contention?
3. Why can floating-point atomic sums vary between runs?

Answers: [self-check answers](../solutions/cuda-078_solutions.md#self-check-answers).

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-078: Atomics and contention.
Read courses/cuda/python/guides/cuda-078.md and courses/cuda/python/lessons/cuda-078.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
