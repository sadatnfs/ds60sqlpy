# cuda-087: Device placement and one auditable training step

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-067`, `cuda-072`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **derive the scalar gradient**, **inspect every tensor device**, and **distinguish correctness and performance** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A training step includes forward computation, scalar loss, gradients and an optimizer update. Moving only inputs to a GPU while leaving parameters on CPU violates the intended placement contract. Frameworks differ in idiom: PyTorch explicitly moves tensors and modules to a device; TensorFlow uses device scopes, placement rules and tracked variables. Inspect actual placement and fail clearly if an explicitly requested GPU is unavailable.

For a one-parameter regressor \(y=wx\) with mean squared error, derive the derivative before trusting autograd. Both framework lanes should reproduce this tiny update and compare to the same CPU arithmetic. Keep initialization, examples, loss reduction and learning rate identical. A correct one-step update establishes a bounded behavior, not model quality or GPU performance.

## Derive the update before invoking autograd

For observations \(x_i\), targets \(y_i\), scalar parameter \(w\) and batch size \(N\), use mean squared error:

\[
L(w)=\frac{1}{N}\sum_{i=1}^{N}(wx_i-y_i)^2,
\qquad
\frac{dL}{dw}=\frac{2}{N}\sum_{i=1}^{N}x_i(wx_i-y_i).
\]

The residual is prediction minus target. The chain rule multiplies its factor of two by the derivative of the prediction, which is the input. At the supplied initial weight, residuals are -2 and -4. Multiplying by inputs gives -2 and -8; doubling and averaging gives -10. SGD subtracts learning rate times gradient, so subtracting a negative gradient increases the weight. This sign check is a useful debugging habit.

In PyTorch, `requires_grad=True` requests gradient tracking on the parameter. `loss.backward()` accumulates into its `.grad`, so an ordinary repeated training loop must zero old gradients at the chosen update boundary. The optimizer owns references to the trainable parameter objects; replacing a parameter object carelessly can leave the optimizer updating the old one. Inspect both parameter identity and device when debugging.

In TensorFlow, `GradientTape` records operations involving watched trainable variables in its scope. `tape.gradient(loss, w)` returns the derivative, which is then paired with the variable for `apply_gradients`. A missing derivative is different from a zero derivative. Check that the intended variable was watched and that the forward computation stayed connected to it. Both frameworks need parameters, inputs and relevant optimizer state on compatible devices; neither makes a cross-device mismatch mathematically meaningful.


## Worked examples

### Worked example 1

With x=[1,2], target=[2,4], \(w=0\), mean loss is 10 and derivative is-10. SGD with learning rate 0.1 updates w to 1.

### Worked example 2

Using sum loss instead of mean doubles the derivative for this batch and changes the update to 2. A faster run with a different loss normalization is not an equivalent training comparison.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
x, y = [1.0, 2.0], [2.0, 4.0]
w = 0.0
loss = sum((w * a - b) ** 2 for a, b in zip(x, y, strict=True)) / len(x)
grad = sum(2 * a * (w * a - b) for a, b in zip(x, y, strict=True)) / len(x)
w -= 0.1 * grad
assert loss == 10 and grad == -10 and w == 1
print("CPU training oracle:", loss, grad, w)
```

**Expected observation:** Loss 10, gradient-10, new weight 1.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Create tensors and parameters on the chosen torch.device, zero gradients, compute mean loss, call backward and step. Inspect w.device and compare the derived gradient before changing the model.

### TensorFlow

Create variables and operations in an explicit tf.device scope, use GradientTape, and apply the resulting gradients. Inspect variable placement and compare the same mean-loss derivative.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: Derive the scalar gradient

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **derive the scalar gradient** in the examples above.

### Exercise 2: Calculate the update

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **calculate the update** in the examples above.

### Exercise 3: Compare sum and mean

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **compare sum and mean** in the examples above.

### Exercise 4: Inspect every tensor device

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **inspect every tensor device** in the examples above.

### Exercise 5: Write equal PyTorch and TensorFlow contracts

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **write equal PyTorch and TensorFlow contracts** in the examples above.

### Exercise 6: Distinguish correctness and performance

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **distinguish correctness and performance** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Derive the scalar gradient".
2. Change one assumption in worked example 2 while preserving the declared contract: calculate the update.
3. Trace the CPU program's variables before adding hardware behavior: compare sum and mean.
4. Draw producers, consumers and the exact operation boundary for the task "Inspect every tensor device".
5. Separate what the small fixture establishes from what the real runtime must show: write equal PyTorch and TensorFlow contracts.
6. Write a counterexample to an overbroad claim before you distinguish correctness and performance.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Derive the scalar gradient`. For the final claim use `Distinguish correctness and performance`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-087` using `courses/cuda/python/guides/cuda-087.md` and `courses/cuda/python/lessons/cuda-087.md`. Help me reason about Device placement and one auditable training step. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
