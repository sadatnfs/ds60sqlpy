# cuda-088: Input pipelines and a hungry GPU

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-071`, `cuda-087`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute serial time.
- Compute an ideal bottleneck bound.
- Budget the queue.
- Explain pinned versus ordinary host storage.
- Compare resident-data diagnostic.
- Choose bounded worker experiments.

## Mechanism and vocabulary

Training is a producer-consumer pipeline: obtain examples, decode, transform, batch, transfer and compute. GPU idleness can arise because the next batch is not ready, not because the model kernel is poor. Increasing workers helps only while the bottleneck can parallelize and memory/I/O remain within budget. Prefetch queues hide latency by retaining future batches, so queue depth also consumes resources.

PyTorch's DataLoader and pinned-memory options express one host pipeline; TensorFlow's tf.data map, batch and prefetch express another. Use synthetic resident tensors as a diagnostic comparison, not as a replacement for measuring real preprocessing. Time complete steps and inspect overlap. Bound worker counts and terminate workers cleanly so a tiny lesson cannot leave a large background process tree.



### Key terms

- **Producer-consumer pipeline:** An arrangement where loader workers prepare batches while the device trains on earlier ones.
- **DataLoader worker:** A separate process that reads and transforms samples in parallel with training.
- **Prefetch queue:** A bounded buffer of ready batches that hides loading latency while it stays nonempty.
- **Pipeline bottleneck:** The slowest stage, which bounds overall throughput regardless of how fast the other stages are.

## Worked examples

### Worked example 1

A serial pipeline spends 6 ms preparing and 4 ms computing each batch, totaling 10 ms. Ideal steady-state overlap approaches 6 ms per batch after startup, not 4 ms.

### Worked example 2

Prefetching three batches of 8 MiB requires at least 24 MiB for queued payloads, excluding decoder state, copies and framework overhead.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-088_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-088_cpu.py
```

```python
prepare, compute = 6, 4
serial = prepare + compute
ideal = max(prepare, compute)
queued = 3 * 8 * 1024 * 1024
assert serial == 10 and ideal == 6 and queued == 25165824
print("CPU pipeline model:", serial, ideal, queued)
```

**Expected observation:** Serial 10 ms, ideal steady-state 6 ms, queued payload 25165824 bytes.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `prepare` | `6` |
| `compute` | `4` |
| `serial` | `10` |
| `ideal` | `6` |
| `queued` | `25165824` |

## Equal framework lanes

### PyTorch

Use a bounded DataLoader with num_workers=0 for the tiny baseline. Compare deliberately prepared pinned batches and non_blocking transfers only on the CUDA lane.

### TensorFlow

Build a finite tf.data pipeline with explicit batch and bounded prefetch. Limit the private thread pool in the teaching program and inspect preprocessing versus device work.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-088.md) before opening hints.

### Exercise 1: Compute serial time

**Trap to avoid:** Reporting the 4 ms GPU compute time as the step time ignores the 6 ms the GPU spends idle waiting for input.

### Exercise 2: Compute an ideal bottleneck bound

**Trap to avoid:** Claiming overlap reduces the step to 4 ms assumes the input stage becomes free. Only a faster or more parallel preparation stage can move the bound below 6 ms.

### Exercise 3: Budget the queue

**Trap to avoid:** Budgeting one batch because only one is used at a time ignores that all queued batches are resident at once.

### Exercise 4: Explain pinned versus ordinary host storage

**Trap to avoid:** Pinning every buffer by default can starve the host and slow the whole machine.

### Exercise 5: Compare resident-data diagnostic

**Trap to avoid:** Reporting the resident-data speed as production throughput ignores that real training must load new data every step.

### Exercise 6: Choose bounded worker experiments

**Trap to avoid:** Raising all settings to their maximum at once may exhaust host memory or CPU cores and still hide which change helped.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Add the preparation time and the compute time for one batch.
2. Once stages overlap, find the slowest stage, because it sets the steady-state interval.
3. Multiply the payload of one batch by the number of batches waiting in the queue.
4. Ask what page-locked host memory changes for transfers and what it costs the host.
5. Ask what a resident-tensor run removes from the pipeline and what it therefore cannot measure.
6. Change one worker or queue setting per run and keep an upper bound on each.

## Common mistakes and self-check

A common mistake is blaming the model kernel when the GPU is idle because the next batch is not ready. Another is assuming more workers or a deeper prefetch queue always helps; once the bottleneck stops parallelizing, they only add memory and I/O pressure. Fix both by timing complete steps, checking whether preparation or computation is the slowest stage, and varying one bounded worker or queue setting at a time, shutting workers down cleanly afterward.

**Misconception:** Feeding the model synthetic tensors that already live on the device shows the speed the real pipeline will reach. **Correction:** Resident synthetic data removes decoding, transforms and transfers, so it measures only the compute side. Use it to bound what the model could do, then time the real pipeline and compare the two.

**Evidence limit:** The reference computes a 10 ms serial step, a 6 ms ideal steady state and 25165824 queued bytes from given stage times. Real overlap, decoder cost and framework overhead must be measured with the actual pipeline.

1. Why is ideal overlap 6 ms per batch rather than 4 ms?
2. What does a prefetch queue cost?
3. Why bound and clean up workers in a small lesson?

Answers: [self-check answers](../solutions/cuda-088_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-088: Input pipelines and a hungry GPU.
Read courses/cuda/python/guides/cuda-088.md and courses/cuda/python/lessons/cuda-088.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
