# cuda-103: Multi-GPU training on one host

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-087`, `cuda-088`, `cuda-092`, `cuda-094`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute equal-replica average.
- Handle unequal counts.
- Assign rank and device.
- Check complete sample coverage.
- Design collective failure handling.
- Compare framework distribution contracts.

## Mechanism and vocabulary

Data parallelism gives replicas different examples, computes gradients and combines those gradients before consistent updates. Rank identifies a participant; a process often owns one GPU. Correctness depends on sample partition, loss normalization, collective order and optimizer state, not merely launching more processes. Different effective batch sizes change the optimization problem.

PyTorch DistributedDataParallel typically uses one process per device and a suitable collective backend. TensorFlow MirroredStrategy coordinates replicas with its own distribution and loss-scaling conventions. Test against a single-device effective-batch reference. Unequal final batches require deliberate handling; repeated examples from padding must be counted. A CPU weighted-average model teaches semantics but cannot validate NCCL, GPU peer access or communication performance.



### Key terms

- **Data parallelism:** Replicating the model on every rank and splitting each batch among them.
- **Rank:** The integer identity of one process in a distributed group.
- **All-reduce:** A collective that combines tensors from every rank and returns the result to all ranks, used to average gradients.
- **Sample partition:** The assignment of distinct samples to each rank so no sample is counted twice per epoch.
- **Effective batch size:** The per-rank batch multiplied by the number of ranks and the accumulation steps.

## Worked examples

### Worked example 1

Two equal-sized replicas with mean gradients 2 and 4 combine to 3. A single-device batch containing their examples should produce the same mathematical gradient.

### Worked example 2

With replica sample counts 3 and 1 and gradients 2 and 4, the global sample mean is 2.5, not 3. Normalization must match the intended data accounting.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-103_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-103_cpu.py
```

```python
counts, gradients = [3, 1], [2.0, 4.0]
weighted = sum(n * g for n, g in zip(counts, gradients, strict=True)) / sum(counts)
assert weighted == 2.5
assert sum(gradients) / 2 == 3.0
print("CPU distributed-gradient oracle:", weighted)
```

**Expected observation:** Global example-weighted gradient 2.5.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `counts` | `[3, 1]` |
| `gradients` | `[2.0, 4.0]` |
| `weighted` | `2.5` |

## Equal framework lanes

### PyTorch

Use an explicitly owned one-process-per-device DDP job with appropriate collective backend and bounded rendezvous. Validate the effective global batch and every rank's sample coverage.

### TensorFlow

Use MirroredStrategy for an explicitly prepared multi-device host. In custom loops apply the distribution-aware loss normalization and compare the resulting update with a single-device reference.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-103.md) before opening hints.

### Exercise 1: Compute equal-replica average

**Trap to avoid:** Summing gradients without dividing by world size gives 6, which effectively doubles the learning rate whenever another GPU is added, so changing the device count silently changes training dynamics.

### Exercise 2: Handle unequal counts

**Trap to avoid:** Relying on the default world-size average when the sampler gives the last rank a short batch introduces a small bias every epoch, which is hard to notice because loss still falls.

### Exercise 3: Assign rank and device

**Trap to avoid:** Creating the model before setting the device places every replica on GPU 0, and the first out-of-memory error appears far from its cause.

### Exercise 4: Check complete sample coverage

**Trap to avoid:** Assuming coverage because each rank processed `len(dataset)/world_size` batches ignores padding and the `drop_last` setting.

### Exercise 5: Design collective failure handling

**Trap to avoid:** Letting surviving ranks wait without a timeout keeps the devices occupied by a job that cannot finish, and nobody receives an error to act on.

### Exercise 6: Compare framework distribution contracts

**Trap to avoid:** Porting a training script between frameworks and assuming identical gradients because both are data-parallel skips the place where the semantics actually differ.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. With equal replica sizes, add the two mean gradients and divide by the replica count.
2. Weight each replica's mean gradient by its example count, or state a documented equal-batch policy instead.
3. Write which process owns which device, and how each process learns its rank.
4. List the examples each rank received and check that every example appears exactly once.
5. Ask what the healthy ranks do while one rank never joins a collective, and how long they should wait.
6. Ask whether passing a PyTorch distributed test says anything about a TensorFlow strategy.

## Common mistakes and self-check

A common mistake is averaging replica gradients equally when replicas processed different numbers of examples. Counts 3 and 1 with gradients 2 and 4 give a global example mean of 2.5, not 3. Another is padding the last batch with repeated examples and counting them twice. Fix both by deciding the normalization from the intended data accounting, checking complete sample coverage and comparing against a single-device reference with the same effective batch.

**Evidence limit:** The reference computes weighted means on the CPU, giving 3 for equal replicas and 2.5 for counts 3 and 1. It launches no processes, so NCCL behavior, GPU peer access and communication cost need a prepared multi-GPU host.

1. What does data parallelism give each replica?
2. Why does adding replicas change the optimization problem?
3. What is the usual PyTorch arrangement for DistributedDataParallel?

Answers: [self-check answers](../solutions/cuda-103_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-103: Multi-GPU training on one host.
Read courses/cuda/python/guides/cuda-103.md and courses/cuda/python/lessons/cuda-103.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
