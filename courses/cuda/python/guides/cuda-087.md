# cuda-087: Device placement and one auditable training step

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-067`, `cuda-072`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Derive the scalar gradient.
- Calculate the update.
- Compare sum and mean.
- Inspect every tensor device.
- Write equal PyTorch and TensorFlow contracts.
- Distinguish correctness and performance.

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


### Key terms

- **Device placement:** Assigning tensors and model parameters to a device; all operands of one operation must be on the same device.
- **Loss gradient:** The derivative of the loss with respect to each parameter, computed by backpropagation.
- **Optimizer step:** The update that changes parameters using their gradients and any optimizer state.
- **Device scope:** A TensorFlow context such as `tf.device` that controls where new operations are placed.

## Worked examples

### Worked example 1

With x=[1,2], target=[2,4], \(w=0\), mean loss is 10 and derivative is -10. SGD with learning rate 0.1 updates w to 1.

### Worked example 2

Using sum loss instead of mean doubles the derivative for this batch and changes the update to 2. A faster run with a different loss normalization is not an equivalent training comparison.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-087_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-087_cpu.py
```

```python
x, y = [1.0, 2.0], [2.0, 4.0]
w = 0.0
loss = sum((w * a - b) ** 2 for a, b in zip(x, y, strict=True)) / len(x)
grad = sum(2 * a * (w * a - b) for a, b in zip(x, y, strict=True)) / len(x)
w -= 0.1 * grad
assert loss == 10 and grad == -10 and w == 1
print("CPU training oracle:", loss, grad, w)
```

**Expected observation:** Loss 10, gradient -10, new weight 1.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `x` | `[1.0, 2.0]` |
| `y` | `[2.0, 4.0]` |
| `w` | `1.0` |
| `loss` | `10.0` |
| `grad` | `-10.0` |

## Equal framework lanes

### PyTorch

Create tensors and parameters on the chosen torch.device, zero gradients, compute mean loss, call backward and step. Inspect w.device and compare the derived gradient before changing the model.

### TensorFlow

Create variables and operations in an explicit tf.device scope, use GradientTape, and apply the resulting gradients. Inspect variable placement and compare the same mean-loss derivative.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-087.md) before opening hints.

### Exercise 1: Derive the scalar gradient

**Trap to avoid:** Dropping the factor 2 from the derivative, a common slip when writing it by hand, gives -5 and a half-size update. Autograd would then disagree with the hand derivation.

### Exercise 2: Calculate the update

**Trap to avoid:** Adding the gradient instead of subtracting it gives `w = -1`, which raises the loss to `((-1-2)**2 + (-2-4)**2)/2 = 22.5`. The sign error is easy to miss when only the update size is checked.

### Exercise 3: Compare sum and mean

**Trap to avoid:** Comparing a sum-loss run with a mean-loss run and attributing the speed or convergence difference to the GPU confounds hardware with loss normalization.

### Exercise 4: Inspect every tensor device

**Trap to avoid:** Checking only the model parameters misses inputs and targets, and moving the model after creating the optimizer can leave the optimizer holding stale references in some setups.

### Exercise 5: Write equal PyTorch and TensorFlow contracts

**Trap to avoid:** Letting each framework use its default initializer or loss reduction makes the numbers differ for reasons unrelated to correctness.

### Exercise 6: Distinguish correctness and performance

**Trap to avoid:** Reporting a speedup from a run that silently used a sum loss, or ran partly on the CPU, compares different computations.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Differentiate the mean of `(w*x - y)**2` with respect to `w` and evaluate it at `w = 0` for the batch.
2. Subtract the learning rate times the gradient from the current weight.
3. Replace the mean with a sum and ask how the gradient changes with batch size.
4. Check parameters, inputs, targets and optimizer state, not just the batch you moved.
5. List each value both frameworks must share: data, initial weight, loss reduction and learning rate.
6. Ask what must already agree before any timing number means anything.

## Common mistakes and self-check

A common mistake is moving only the inputs to the GPU while parameters, targets or optimizer state stay on the CPU, which raises a device mismatch error or forces hidden copies. Another is comparing frameworks whose loss reductions differ: a sum loss doubles this batch's gradient and changes the update. Fix both by inspecting every tensor's device, failing clearly when an explicitly requested GPU is missing, and keeping data, initialization, reduction and learning rate identical.

**Evidence limit:** The reference reproduces loss 10, gradient -10 and new weight 1 with CPU arithmetic. It does not run PyTorch or TensorFlow, so actual device placement and autograd results need the framework lanes.

1. Why derive the gradient by hand before trusting autograd?
2. How do PyTorch and TensorFlow differ in placement idiom?
3. What does a correct one-step update establish?

Answers: [self-check answers](../solutions/cuda-087_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-087: Device placement and one auditable training step.
Read courses/cuda/python/guides/cuda-087.md and courses/cuda/python/lessons/cuda-087.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
