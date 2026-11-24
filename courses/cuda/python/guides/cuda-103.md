# cuda-103: Multi-GPU training on one host

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-087`, `cuda-088`, `cuda-092`, `cuda-094`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute equal-replica average**, **check complete sample coverage**, and **compare framework distribution contracts** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

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

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

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

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Use an explicitly owned one-process-per-device DDP job with appropriate collective backend and bounded rendezvous. Validate the effective global batch and every rank's sample coverage.

### TensorFlow

Use MirroredStrategy for an explicitly prepared multi-device host. In custom loops apply the distribution-aware loss normalization and compare the resulting update with a single-device reference.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Compute equal-replica average

**Trap to avoid:** Summing gradients without dividing by world size gives 6, which effectively doubles the learning rate whenever another GPU is added, so changing the device count silently changes training dynamics.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Handle unequal counts

**Trap to avoid:** Relying on the default world-size average when the sampler gives the last rank a short batch introduces a small bias every epoch, which is hard to notice because loss still falls.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Assign rank and device

**Trap to avoid:** Creating the model before setting the device places every replica on GPU 0, and the first out-of-memory error appears far from its cause.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Check complete sample coverage

**Trap to avoid:** Assuming coverage because each rank processed `len(dataset)/world_size` batches ignores padding and the `drop_last` setting.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Design collective failure handling

**Trap to avoid:** Letting surviving ranks wait without a timeout keeps the devices occupied by a job that cannot finish, and nobody receives an error to act on.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Compare framework distribution contracts

**Trap to avoid:** Porting a training script between frameworks and assuming identical gradients because both are data-parallel skips the place where the semantics actually differ.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute equal-replica average".
2. Change one assumption in worked example 2 while preserving the declared contract: handle unequal counts.
3. Trace the CPU program's variables before adding hardware behavior: assign rank and device.
4. Draw producers, consumers and the exact operation boundary for the task "Check complete sample coverage".
5. Separate what the small fixture establishes from what the real runtime must show: design collective failure handling.
6. Write a counterexample to an overbroad claim before you compare framework distribution contracts.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute equal-replica average`. For the final claim use `Compare framework distribution contracts`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-103: Multi-GPU training on one host.
Read courses/cuda/python/guides/cuda-103.md and courses/cuda/python/lessons/cuda-103.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
