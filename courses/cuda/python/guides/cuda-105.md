# cuda-105: Distributed training beyond one host

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-103`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute barrier time.
- Compare parallelism types.
- Diagnose a missing rank.
- Define checkpoint consistency.
- Budget communication.
- Design owned-host cleanup.

## Mechanism and vocabulary

Across hosts, the network joins GPU compute and storage as a first-class resource. A rendezvous establishes participants; collectives require compatible ordering and membership. Data parallelism replicates parameters, tensor parallelism partitions operations, pipeline parallelism partitions layers, and state sharding distributes selected model or optimizer state. Their communication patterns differ.

Stragglers delay synchronized steps. Worker failure requires a coordinated stop or a deliberately implemented recovery protocol; independently retrying one rank can hang the rest. Checkpoints need a consistent global boundary and data-position contract. This lesson uses diagrams and synthetic timelines by default. Actual multi-host work requires explicitly owned hosts, bounded access, suitable networking and separate PyTorch/TensorFlow qualification. Nothing in the browser creates a cluster.



### Key terms

- **Rendezvous:** The startup step in which processes discover each other and agree on ranks and world size.
- **Tensor parallelism:** Splitting individual layer weights across devices, which requires communication inside each layer.
- **Pipeline parallelism:** Placing consecutive layer groups on different devices and streaming microbatches through them.
- **State sharding:** Partitioning parameters, gradients or optimizer state across ranks to reduce per-device memory.
- **Communication budget:** The time and bandwidth available for collectives relative to compute in each step.

## Worked examples

### Worked example 1

Three ranks taking 10, 12 and 30 ms before a barrier yield at least 30 ms compute-phase latency, even though their average is 17.3 ms.

### Worked example 2

A checkpoint assembled from rank 0 at step 10 and rank 1 at step 11 is not a coherent global state unless a protocol explicitly reconciles that difference.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-105_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-105_cpu.py
```

```python
rank_ms = [10, 12, 30]
assert max(rank_ms) == 30
steps = {"rank0": 10, "rank1": 11}
consistent = len(set(steps.values())) == 1
assert not consistent
print("CPU distributed trace: barrier", max(rank_ms), "ms; checkpoint consistent", consistent)
```

**Expected observation:** Barrier 30 ms; mixed-step checkpoint rejected.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rank_ms` | `[10, 12, 30]` |
| `steps` | `{'rank0': 10, 'rank1': 11}` |
| `consistent` | `False` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-105.md) before opening hints.

### Exercise 1: Compute barrier time

**Trap to avoid:** Reporting the average rank time predicts 17.3 ms and hides 13 ms of idle time per step, which makes adding ranks look more efficient than it is.

### Exercise 2: Compare parallelism types

**Trap to avoid:** Using data parallelism for a model that does not fit on one device fails immediately, because each replica needs all parameters, gradients and optimizer state.

### Exercise 3: Diagnose a missing rank

**Trap to avoid:** Restarting only the missing rank while the others wait in a collective fails, because the new process does not join the existing communicator state.

### Exercise 4: Define checkpoint consistency

**Trap to avoid:** Accepting each rank's latest file independently produces mixed-step checkpoints whenever a failure occurs during saving.

### Exercise 5: Budget communication

**Trap to avoid:** Estimating communication from the parameter count without element size or frequency misses that float32 gradients are four bytes and some collectives run several times per step.

### Exercise 6: Design owned-host cleanup

**Trap to avoid:** Killing every GPU process on a host stops other users' jobs, while deleting the output directory loses valid checkpoints.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Find the latest rank to reach the barrier; every rank waits until it arrives.
2. For each strategy, ask what is copied to every rank and what is split, whether parameters, operations, layers or optimizer state.
3. Ask what the remaining ranks do in a collective if one never arrives, and who stops the job.
4. Ask which update step every rank's saved state must share before the files form one checkpoint.
5. For each collective, write the bytes exchanged and how often it runs per training step.
6. List the resources your job created and release only those, leaving checkpoints in place.

## Common mistakes and self-check

A common mistake is restarting one failed rank on its own. The surviving ranks are already waiting inside a collective, so the restarted rank joins a different step and the job hangs or silently diverges. Another mistake is building a checkpoint from rank files saved at different steps. Fix both by using bounded waits, stopping the whole owned job when a rank fails and recovering from a checkpoint taken at one documented global update boundary, with the data position recorded for every rank. Report the slowest rank, not the average, when reasoning about synchronized steps.

**Misconception:** Data, tensor and pipeline parallelism are interchangeable ways to add GPUs, so any of them will scale a model across hosts. **Correction:** Each partitions something different and communicates differently. Data parallelism replicates parameters and reduces gradients every step; tensor parallelism splits operations and exchanges activations inside layers, which needs fast links; pipeline parallelism splits layers and passes activations between stages, leaving idle bubbles unless microbatches fill them. Choose by model size, memory and the network between hosts, and model the communication before scaling out.

**Evidence limit:** The reference computes a 30 ms barrier time and rejects a mixed-step checkpoint from synthetic numbers. It contacts no hosts, so rendezvous, network bandwidth, straggler causes and recovery behavior need explicitly owned machines and separate qualification for each framework.

1. Why does the slowest rank set a synchronized step's time?
2. How do tensor and pipeline parallelism differ?
3. Why can a browser lesson not create a cluster?

Answers: [self-check answers](../solutions/cuda-105_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-105: Distributed training beyond one host.
Read courses/cuda/python/guides/cuda-105.md and courses/cuda/python/lessons/cuda-105.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
