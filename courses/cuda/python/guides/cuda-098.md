# cuda-098: Backward is part of the operator

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-097`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **derive the input VJP**, **explain a failed kink gradcheck**, and **compare each framework reference** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A backward implementation computes a vector-Jacobian product: the upstream gradient weights each output's contribution to each input. For an elementwise affine-ReLU \(y=\max(0,ax+b)\), the derivative with respect to x is a where ax+b is positive and the chosen boundary derivative elsewhere. The derivative with respect to shared a or b is a reduction over elements, not an elementwise output of the same shape.

PyTorch autograd registration and TensorFlow custom-gradient or registered-gradient mechanisms differ, but both need mathematical tests. Finite differences approximate derivatives away from nondifferentiable boundaries; double precision and carefully chosen perturbations reduce numerical noise. Framework registration checks validate integration properties, not every derivative. State whether higher-order gradients and unusual layouts are supported.

## Derive the vector-Jacobian product, including shared parameters

Let \(z_i=ax_i+b\), \(y_i=\max(0,z_i)\), and let \(g_i\) be the upstream derivative of a scalar objective with respect to \(y_i\). Away from the kink, define \(m_i=1\) when \(z_i>0\) and zero otherwise. The backward equations are:

\[
\bar x_i=g_i a m_i,\qquad
\bar a=\sum_i g_i x_i m_i,\qquad
\bar b=\sum_i g_i m_i.
\]

Input gradients are elementwise because each input influences one output. Scale and bias gradients reduce over all outputs because those parameters are shared. Forgetting those reductions is a common error that can remain hidden when testing only one element. Broadcasting adds another version of the same issue: a broadcast dimension's gradient must be reduced back to the original parameter shape.

A central finite difference computes \([f(x+\epsilon)-f(x-\epsilon)]/(2\epsilon)\). Too large an epsilon introduces truncation error; too small can lose the difference to rounding. Use small double-precision inputs away from nondifferentiable boundaries and vary epsilon if a discrepancy is ambiguous. At the ReLU kink, test the documented chosen derivative rather than insisting a symmetric finite difference define it.

Backward also has memory and stream contracts. Saved forward intermediates must remain valid until consumed. Recomputing a mask can save storage only when it reproduces the same forward branch under the supported precision policy. Test non-unit upstream gradients, because differentiating a sum supplies all ones and may hide missing multiplication by the incoming gradient. State whether second derivatives are supported and test them separately; first-order correctness does not imply higher-order graph support.


## Worked examples

### Worked example 1

At x=2 with \(a=2,b=1\), y=5 and derivative \(dy/dx=2\). A central finite difference around 2 agrees within numerical tolerance.

### Worked example 2

At \(x=-0.5\), the preactivation is zero. A central difference straddles the kink and need not equal the framework-selected subgradient, so test the documented boundary separately.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
def f(x):
    return max(0.0, 2 * x + 1)


x, eps = 2.0, 1e-5
numeric = (f(x + eps) - f(x - eps)) / (2 * eps)
assert abs(numeric - 2.0) < 1e-8
upstream = [1, 3]
mask = [0, 1]
bias_grad = sum(g * m for g, m in zip(upstream, mask, strict=True))
assert bias_grad == 3
print("CPU gradient oracle:", numeric, bias_grad)
```

**Expected observation:** Finite-difference derivative approximately 2 and bias VJP 3.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Register a mathematically correct backward and test vector-Jacobian products with double-precision gradcheck away from kinks. An op registration check is not a substitute for derivative verification.

### TensorFlow

Use the supported registered-gradient or custom_gradient mechanism. Compare GradientTape results with a native reference and finite differences, including documented nondifferentiable boundaries.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: Derive the input VJP

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **derive the input VJP** in the examples above.

### Exercise 2: Derive bias gradient

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **derive bias gradient** in the examples above.

### Exercise 3: Run finite differences away from a kink

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **run finite differences away from a kink** in the examples above.

### Exercise 4: Explain a failed kink gradcheck

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **explain a failed kink gradcheck** in the examples above.

### Exercise 5: Specify higher-order support

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **specify higher-order support** in the examples above.

### Exercise 6: Compare each framework reference

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **compare each framework reference** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Derive the input VJP".
2. Change one assumption in worked example 2 while preserving the declared contract: derive bias gradient.
3. Trace the CPU program's variables before adding hardware behavior: run finite differences away from a kink.
4. Draw producers, consumers and the exact operation boundary for the task "Explain a failed kink gradcheck".
5. Separate what the small fixture establishes from what the real runtime must show: specify higher-order support.
6. Write a counterexample to an overbroad claim before you compare each framework reference.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Derive the input VJP`. For the final claim use `Compare each framework reference`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-098` using `courses/cuda/python/guides/cuda-098.md` and `courses/cuda/python/lessons/cuda-098.md`. Help me reason about Backward is part of the operator. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
