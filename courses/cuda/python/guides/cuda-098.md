# cuda-098: Backward is part of the operator

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-097`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Derive the input VJP.
- Derive bias gradient.
- Run finite differences away from a kink.
- Explain a failed kink gradcheck.
- Specify higher-order support.
- Compare each framework reference.

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


### Key terms

- **Vector-Jacobian product:** The quantity backward computes: the upstream gradient multiplied by the operator's Jacobian.
- **Subgradient:** A valid slope choice at a kink such as ReLU at zero, where the ordinary derivative is undefined.
- **Finite difference:** A numerical derivative estimate from evaluating a function at nearby points, used to check analytic gradients.
- **Gradient check (gradcheck):** A PyTorch utility that compares analytic and finite-difference gradients, usually in double precision.

## Worked examples

### Worked example 1

At x=2 with \(a=2,b=1\), y=5 and derivative \(dy/dx=2\). A central finite difference around 2 agrees within numerical tolerance.

### Worked example 2

At \(x=-0.5\), the preactivation is zero. A central difference straddles the kink and need not equal the framework-selected subgradient, so test the documented boundary separately.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-098_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-098_cpu.py
```

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `x` | `2.0` |
| `eps` | `1e-05` |
| `numeric` | `2.0000000000131024` |
| `upstream` | `[1, 3]` |
| `mask` | `[0, 1]` |
| `bias_grad` | `3` |

## Equal framework lanes

### PyTorch

Register a mathematically correct backward and test vector-Jacobian products with double-precision gradcheck away from kinks. An op registration check is not a substitute for derivative verification.

### TensorFlow

Use the supported registered-gradient or custom_gradient mechanism. Compare GradientTape results with a native reference and finite differences, including documented nondifferentiable boundaries.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-098.md) before opening hints.

### Exercise 1: Derive the input VJP

**Trap to avoid:** Using the output `y` instead of a mask, `upstream * a * y`, scales gradients by activation values and is wrong for every positive input not equal to 1.

### Exercise 2: Derive bias gradient

**Trap to avoid:** Returning the upstream sum without masking gives 4, including a contribution from a position where the ReLU blocked gradient.

### Exercise 3: Run finite differences away from a kink

**Trap to avoid:** Running the check in float32 with a tiny epsilon loses precision to cancellation and fails even when the analytic gradient is right.

### Exercise 4: Explain a failed kink gradcheck

**Trap to avoid:** Changing the backward to return 1 at the kink so the check passes chooses a convention for the test's sake.

### Exercise 5: Specify higher-order support

**Trap to avoid:** Assuming double backward works because first-order gradcheck passed leads to silent zero second derivatives.

### Exercise 6: Compare each framework reference

**Trap to avoid:** Comparing PyTorch's custom op with TensorFlow's custom op only checks they agree with each other.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Multiply the upstream gradient by `a` wherever the preactivation is positive, and use the boundary rule elsewhere.
2. The bias is shared by every element, so collect each element's masked upstream contribution into one number.
3. Perturb `x` by the same small step in both directions and divide the difference by twice the step.
4. Evaluate the preactivation at the failing point and ask whether the derivative is unique there.
5. Ask what a first-order check says about differentiating the gradient itself.
6. Compare forward results first, then compare backward results separately against each framework's native expression.

## Common mistakes and self-check

A common mistake is returning the gradient of a shared parameter with the shape of the input. The bias gradient is a sum of masked upstream values, a scalar here, not an elementwise array. Another mistake is running finite differences at the ReLU kink and treating the mismatch as a bug. Fix both by deriving each vector-Jacobian product by hand, reducing over elements for shared parameters and testing points away from the kink separately from the documented boundary behavior.

**Evidence limit:** The reference checks a finite-difference derivative near 2 and a bias VJP of 3 in double precision. It does not register a gradient in PyTorch or TensorFlow, so integration, higher-order gradients and unusual layouts remain untested.

1. What does a backward function compute?
2. Why can a central difference disagree at the kink?
3. What do framework registration checks validate?

Answers: [self-check answers](../solutions/cuda-098_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-098: Backward is part of the operator.
Read courses/cuda/python/guides/cuda-098.md and courses/cuda/python/lessons/cuda-098.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
