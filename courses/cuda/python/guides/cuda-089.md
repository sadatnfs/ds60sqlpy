# cuda-089: Allocations and out-of-memory reasoning

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-070`, `cuda-087`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Build a parameter ledger.
- Add activation bytes.
- Separate reserve and live usage.
- Diagnose a retained graph.
- Explain memory growth.
- Design a safe batch-size experiment.

## Mechanism and vocabulary

Training memory contains parameters, gradients, optimizer state, saved activations, temporary workspaces and allocator reserve. These terms respond differently to batch size and precision. Adam commonly maintains two moment tensors, while mixed-precision implementations may retain additional master state. Count the actual implementation instead of applying one universal bytes-per-parameter rule.

PyTorch distinguishes allocated and reserved memory and can retain autograd graphs when losses or outputs remain attached. TensorFlow memory growth changes reservation behavior but does not make an oversized live workload fit. Both require bounded experiments with the same model and controlled batch changes. Host container limits do not generally impose a per-process GPU-memory quota. Avoid intentional OOM on shared devices and use supplied failure traces instead.



### Key terms

- **Memory ledger:** An accounting of parameters, gradients, optimizer state, activations and allocator reserve that predicts peak device memory.
- **Optimizer state:** Extra per-parameter tensors such as Adam's first and second moments, often twice the size of the parameters.
- **Activation memory:** Intermediate outputs saved during the forward pass for use in backward, growing with batch size and depth.
- **Retained graph:** An autograd graph kept alive by a stored loss or output tensor, which holds its activations in memory.

## Worked examples

### Worked example 1

For 1000 float32 parameters, parameters, gradients and two moment arrays total 16000 bytes before activations and workspaces. This is an illustrative ledger, not a full framework prediction.

### Worked example 2

Doubling batch size can approximately double saved activation payload while leaving parameter count unchanged. Retaining every step loss tensor can grow a graph independently of batch size.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-089_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-089_cpu.py
```

```python
params = 1000
state_bytes = params * 4 * 4
activations = 8 * 128 * 4
assert state_bytes == 16000 and activations == 4096
assert state_bytes + 2 * activations == 24192
print("CPU memory ledger:", state_bytes, activations)
```

**Expected observation:** State 16000 bytes and activation 4096 bytes for the example.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `params` | `1000` |
| `state_bytes` | `16000` |
| `activations` | `4096` |

## Equal framework lanes

### PyTorch

Distinguish memory_allocated from memory_reserved. Retained tensors and attached loss histories keep graph storage live; scalar summaries should be detached deliberately.

### TensorFlow

Configure memory growth before device initialization when using it. Inspect current/peak allocator observations where supported and separate reservation policy from the required live tensors.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-089.md) before opening hints.

### Exercise 1: Build a parameter ledger

**Trap to avoid:** Counting parameters only, 4000 bytes, underestimates training memory by four times for this optimizer.

### Exercise 2: Add activation bytes

**Trap to avoid:** Ignoring activations because they are temporary misses that they live from forward until backward, which is when memory peaks.

### Exercise 3: Separate reserve and live usage

**Trap to avoid:** Reading the reserved number in a monitoring tool and concluding tensors are leaking confuses cache with live usage. Tools such as `nvidia-smi` report the reserved total, so they show this inflated number.

### Exercise 4: Diagnose a retained graph

**Trap to avoid:** Blaming a fixed-size growth per step on fragmentation or the allocator leads to tuning allocator settings that do not fix the reference leak.

### Exercise 5: Explain memory growth

**Trap to avoid:** Turning growth on to fix an out-of-memory error treats a policy as a capacity increase.

### Exercise 6: Design a safe batch-size experiment

**Trap to avoid:** Doubling until the program crashes uses an out-of-memory error as the measurement and can disrupt other users.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Count every array the optimizer keeps per parameter and multiply by the dtype's bytes.
2. Multiply batch size, saved elements per example and itemsize.
3. Ask which number includes storage the allocator holds for reuse but no live tensor uses.
4. Look for a loss or output kept in a list across steps that still carries its graph.
5. Ask whether changing how memory is reserved changes how many bytes the step needs live.
6. Fix small upper bounds before running and decide when you will stop without exhausting the device.

## Common mistakes and self-check

A common mistake is applying a universal bytes-per-parameter rule and ignoring activations, workspaces and allocator reserve. Another is keeping every step's loss tensor in a list, which retains autograd graphs and grows memory regardless of batch size. A third is reading reserved memory as live usage. Fix these by building a ledger from the actual arrays and dtypes, storing detached scalar summaries and comparing allocated with reserved memory in small, bounded batch experiments.

**Misconception:** Turning on TensorFlow memory growth or clearing an allocator cache will make an oversized workload fit. **Correction:** Memory growth only changes when TensorFlow reserves device memory, and clearing a cache releases memory that is reserved but unused. Neither shrinks the live set of parameters, gradients, optimizer state and activations. If the live set exceeds the device, reduce the batch size or precision, or change the model.

**Evidence limit:** The reference totals 16000 bytes of optimizer state and 4096 activation bytes for an illustrative ledger. Real usage also includes workspaces, allocator reserve and framework internals, so it does not predict an out-of-memory threshold on a device.

1. Why does Adam need more memory than plain SGD?
2. What does TensorFlow memory growth change?
3. Does a container memory limit cap GPU memory?

Answers: [self-check answers](../solutions/cuda-089_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-089: Allocations and out-of-memory reasoning.
Read courses/cuda/python/guides/cuda-089.md and courses/cuda/python/lessons/cuda-089.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
