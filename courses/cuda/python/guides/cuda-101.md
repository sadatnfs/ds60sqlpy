# cuda-101: LLM training, fine-tuning and GPU memory

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-094`, `cuda-099`, `cuda-100`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **count low-rank parameters**, **compare sequence-length budgets**, and **define held-out evaluation** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Full fine-tuning updates all selected model parameters. Adapter methods train additional small structures while retaining the base weights. Low-rank updates factor a matrix update into two thinner matrices, reducing trainable parameter count, but the base model still occupies memory and activations still flow through it. Optimizer membership should match the intended trainable set exactly.

Sequence length, padding, batch size, precision, saved activations and optimizer state can dominate different workloads. Build a tiny transformer locally with synthetic tokens before considering downloads. Compare full and adapter training on a held-out synthetic task with equal data accounting. Parameter efficiency is not a guarantee of lower total runtime memory or better quality. Both PyTorch and TensorFlow lanes should report their actual variable census and optimizer state.

## Fine-tuning choices and what remains resident

For a dense weight matrix \(W\in\mathbb R^{m\times n}\), a low-rank update can be written \(\Delta W=AB\), where \(A\) has shape \((m,r)\) and \(B\) has shape \((r,n)\). The trainable update contains \(r(m+n)\) parameters instead of \(mn\). Rank controls the update's representational capacity as well as its parameter count; a smaller rank is a modeling decision that needs validation.

Freezing \(W\) does not remove the forward multiplication by \(W\). Inputs still traverse the base model, and activations may still be needed to train adapters at earlier or later layers. Optimizer state for the frozen weights can disappear when those weights are genuinely excluded from optimization, but the weights themselves remain resident unless an explicit offload or quantization scheme changes their storage. Count these categories separately.

The paired framework examples intentionally use a tiny low-rank matrix rather than downloading a model. The base is an identity matrix, one adapter factor is small and the other starts at zero. The zero update preserves the base function initially. Gradients for the two factors can differ at that initialization, so verify actual gradients instead of assuming both must change on the first step. Then connect this mechanism to attention projection matrices in the existing transformer curriculum.

A complete adaptation study defines the target task, training examples, held-out evaluation, trainable-variable list, optimizer membership, precision policy, sequence/batch cap, checkpoint and rollback. Subject-matter factual knowledge is not guaranteed by lowering training loss: evaluate whether answers use the intended domain evidence and compare a retrieval baseline where appropriate. Parameter-efficient tuning, RAG and prompt design solve overlapping but distinct problems. The GPU lesson supplies resource and training mechanics, while the applied-LLM route supplies grounded-answer and task evaluation design.


## Worked examples

### Worked example 1

A 1024 by 1024 matrix has 1,048,576 parameters. A rank 8 update uses\(8(1024+1024)=16{,}384\) trainable parameters while the original matrix remains present.

### Worked example 2

Freezing the base matrix removes its gradient and optimizer-update requirement under the chosen implementation, but downstream training can still need intermediate activations.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
rows, cols, rank = 1024, 1024, 8
base = rows * cols
adapter = rank * (rows + cols)
assert base == 1048576 and adapter == 16384
assert base + adapter > base
print("CPU adapter ledger:", base, adapter, "parameters")
```

**Expected observation:** Base 1,048,576 and adapter 16,384 parameters.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Freeze base parameters explicitly and construct the optimizer from intended trainable tensors. The included low-rank matrix example demonstrates storage and trainability separately before any full transformer adaptation.

### TensorFlow

Set base variables nontrainable, track adapter variables and pass the intended gradient-variable pairs to the optimizer. Report all resident variables as well as trainable counts.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: Count low-rank parameters

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **count low-rank parameters** in the examples above.

### Exercise 2: Include base storage

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **include base storage** in the examples above.

### Exercise 3: Inspect optimizer membership

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **inspect optimizer membership** in the examples above.

### Exercise 4: Compare sequence-length budgets

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **compare sequence-length budgets** in the examples above.

### Exercise 5: Design tiny offline training

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design tiny offline training** in the examples above.

### Exercise 6: Define held-out evaluation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **define held-out evaluation** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Count low-rank parameters".
2. Change one assumption in worked example 2 while preserving the declared contract: include base storage.
3. Trace the CPU program's variables before adding hardware behavior: inspect optimizer membership.
4. Draw producers, consumers and the exact operation boundary for the task "Compare sequence-length budgets".
5. Separate what the small fixture establishes from what the real runtime must show: design tiny offline training.
6. Write a counterexample to an overbroad claim before you define held-out evaluation.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Count low-rank parameters`. For the final claim use `Define held-out evaluation`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-101` using `courses/cuda/python/guides/cuda-101.md` and `courses/cuda/python/lessons/cuda-101.md`. Help me reason about LLM training, fine-tuning and GPU memory. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
