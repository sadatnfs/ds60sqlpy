# cuda-067: Transfers have cost and lifetime

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-066`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Count bytes for ten iterations.
- Model a batched transfer.
- Find premature source reuse.
- Explain pinned-memory lifetime.
- Design an end-to-end timer.
- Identify an intentionally CPU-friendly workload.

## Mechanism and vocabulary

A transfer pays fixed submission latency plus a size-dependent term. With payload B bytes and effective bandwidth W bytes per second, a useful first model is \(T=\ell+B/W\), where \(\ell\) is submission latency. This is a hypothesis for planning, not a benchmark. Small transfers often pay the fixed term repeatedly. Keeping intermediate arrays on device can save round trips even when the arithmetic expression does not change.

Asynchronous copying also creates an ownership obligation. The source must remain valid and unchanged until the copy finishes; the destination cannot be consumed before its dependency is satisfied. Pinned host memory can enable useful transfer overlap under supported conditions, but pinning every object consumes host resources. Count transfers before optimizing them and include serialization, packing and final output retrieval in end-to-end latency.



### Key terms

- **Transfer latency:** The fixed startup cost of a copy that is paid regardless of how many bytes move.
- **Effective bandwidth:** Bytes moved divided by measured elapsed time; it approaches peak bandwidth only for large transfers because latency is included.
- **Pinned memory:** Page-locked host memory that the GPU can reach by direct memory access, enabling faster and asynchronous copies.
- **End-to-end timer:** A measurement that brackets the copy in, the kernel and the copy back, so transfer cost is not hidden.

## Worked examples

### Worked example 1

Copying 100 rows separately at 10 microseconds submission cost spends at least 1 millisecond on submissions. One contiguous batch pays the submission term once.

### Worked example 2

Over K iterations, a transformation that copies input and output every iteration moves \(2KB\) bytes. Uploading once and downloading once moves \(2B\) bytes if all intermediates stay device-resident.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-067_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-067_cpu.py
```

```python
size = 4096
iterations = 10
round_trip = 2 * size * iterations
resident = 2 * size
assert round_trip == 81920
assert resident == 8192
latency = 10e-6
bandwidth = 1e9
many = 100 * (latency + 40 / bandwidth)
one = latency + 4000 / bandwidth
assert many > one
print("CPU cost model:", round_trip, resident, "bytes")
```

**Expected observation:** 81920 versus 8192 modeled bytes; these are not measured timings.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `size` | `4096` |
| `iterations` | `10` |
| `round_trip` | `81920` |
| `resident` | `8192` |
| `latency` | `1e-05` |
| `bandwidth` | `1000000000.0` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-067.md) before opening hints.

### Exercise 1: Count bytes for ten iterations

**Trap to avoid:** Counting only uploads (`10B`) treats the output copy as free. Many real pipelines download a result every step for logging, so omitting it halves the modeled traffic.

### Exercise 2: Model a batched transfer

**Trap to avoid:** Expecting batching to reduce the payload is the mistake. The bytes are the same; if your model shows the bandwidth term shrinking, you have double-counted or dropped rows.

### Exercise 3: Find premature source reuse

**Trap to avoid:** Adding a sleep after the copy call seems to fix it in testing because the copy usually finishes. It is timing luck: a larger batch or a busy bus makes the race reappear.

### Exercise 4: Explain pinned-memory lifetime

**Trap to avoid:** Pinning every array in the program to be safe consumes host memory the OS cannot page out, which can starve other processes. Pinning is a bounded resource, not a free speedup.

### Exercise 5: Design an end-to-end timer

**Trap to avoid:** Stopping the timer right after the kernel call returns measures submission only, because the call is asynchronous; it reports a tiny number regardless of the 81920 versus 8192 byte difference.

### Exercise 6: Identify an intentionally CPU-friendly workload

**Trap to avoid:** Assuming the GPU always wins because it has more cores ignores the fixed costs. A benchmark on one tiny array would show the CPU ahead, and the conclusion that the GPU is slow would also be wrong.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Count bytes per iteration in the round-trip version and multiply by ten; then count the upload-once, download-once version.
2. Hold the 4000-byte payload fixed and ask which part of the transfer model, latency or bandwidth, changes with batching.
3. Mark when Python regains control after the asynchronous upload and when the copy engine finishes reading the host buffer.
4. Ask who owns the page-locked buffer while a copy is pending, and what happens if that owner is garbage collected.
5. Write where the caller's clock starts and stops, then check whether both transfers fall inside that interval.
6. Compare about 10 microseconds of submission latency with the time a CPU needs for ten float additions.

## Common mistakes and self-check

The mistake this chapter targets is tuning the arithmetic while ignoring how many times data crosses the bus. Copying input and output on every one of K iterations moves 2KB bytes; keeping intermediates resident moves 2B. A second mistake is overwriting or freeing a host buffer while an asynchronous copy still reads it. Fix both by counting transfers before tuning kernels, and by waiting on the copy's event before reusing or releasing the source.

**Evidence limit:** The 81920 and 8192 byte counts come from the transfer model, not from a timer. Real effective bandwidth, pinned versus pageable behavior and copy and compute overlap must be measured on the target system before you claim a latency saving.

1. In the model latency plus B divided by W, which term does batching reduce?
2. Why is pinning every host array a poor default?
3. What must an end-to-end timer include in this chapter?

Answers: [self-check answers](../solutions/cuda-067_solutions.md#self-check-answers).

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-067: Transfers have cost and lifetime.
Read courses/cuda/python/guides/cuda-067.md and courses/cuda/python/lessons/cuda-067.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
