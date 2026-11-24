# torch-029: explanatory solutions

Open these answers only after attempting Stable objectives, precision and mixed-precision boundaries yourself. They reuse the guide's literal inputs, starting from Example A, Expose naive overflow, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Overflow, Log-sum-exp, Mixed precision. After a pass, choose a new input for exercise 6, Reject a nonfinite input contract, without looking.

## Mechanism review

Numerical stability concerns how an equivalent mathematical expression behaves in a finite representation. Logits 1000, 999 define a valid two-class distribution, but directly exponentiating them overflows common floating-point types. Subtracting a shared maximum before softmax preserves the distribution. CrossEntropyLoss and logsumexp implement stable combined operations that avoid unnecessary probability round trips.

Precision and range differ across float16, bfloat16, float32 and float64. Automatic mixed precision selects operation dtypes under a backend policy; gradient scaling addresses underflow in certain training paths. Those mechanisms require hardware-specific validation. This default CPU lesson checks stable objectives and dtype limits without claiming GPU speed or a qualified mixed-precision training configuration. A stable loss can still optimize the wrong labels or denominator, so numerical and semantic checks remain separate.

**Overflow:** A result exceeding the numeric type's representable range.

**Log-sum-exp:** A stable logarithm of summed exponentials.

**Mixed precision:** A policy using different numeric types for different operations.

**Gradient scaling:** A technique changing gradient magnitude during certain low-precision training workflows.

## Reading the implementation

Use F.cross_entropy on raw logits and torch.logsumexp for a stable log normalizer. Inspect torch.isfinite on forward values and gradients. torch.finfo reports representable ranges and epsilon, but is not a performance benchmark. Keep dtype explicit in independent arithmetic comparisons. Do not cast arbitrary nonfinite inputs into a lower-precision type and expect a stable objective to repair them.

## Separate the mathematical distribution from its representation

For logits z=[1000, 999], the first-class probability is \(\frac{\exp(1000)}{\exp(1000)+\exp(999)}\). Dividing numerator and denominator by \(\exp(1000)\) gives \(\frac{1}{1+\exp(-1)}\), approximately 0.731059. The other probability is approximately 0.268941. The mathematical ratio is well defined even though directly materializing \(\exp(1000)\) overflows the types used in the counterexample.

More generally, subtracting the same finite m from every logit preserves softmax in exact arithmetic. Choosing \(m=\max(z)\) makes every shifted exponent at most zero, so every shifted exponential is at most one and at least one equals one. For the target 0 loss, the shifted form is \(\log(1+\exp(-1))\), approximately 0.313262. The gradient is p-one_hot(target), or approximately [-0.268941, 0.268941]. Its entries sum to zero because a common logit shift does not change the objective. This gives an independent forward and backward contract.

Stability is more specific than a function name. logsumexp avoids raw exponential overflow, but computing a large logsumexp value and then subtracting a nearly equal large target logit can still lose precision. A fused logits loss or log_softmax formulation can preserve the small relative difference more directly. Similarly, computing a tiny probability and then taking its log can underflow where a direct log-probability calculation remains finite. Inspect intermediate representation rather than assuming algebraic equivalence implies equal floating-point error.

Range and precision are different properties:

| Type | Approximate maximum finite magnitude | Relative spacing near one |
| --- | --- | --- |
| float16 | 65504 | \({2}^{-10}\) |
| bfloat16 | \(3.39\cdot {10}^{38}\) | \({2}^{-7}\) |
| float32 | \(3.4\cdot {10}^{38}\) | \({2}^{-23}\) |
| float64 | \(1.8\cdot {10}^{308}\) | \({2}^{-52}\) |

bfloat16 has a much wider exponent range than float16 but fewer fraction bits. A value can avoid overflow while still be represented coarsely. Epsilon near one is not a universal absolute tolerance for all magnitudes or all algorithms. Summation length, conditioning, cancellation and the operations actually performed matter. [PyTorch 2.9 numerical accuracy](https://docs.pytorch.org/docs/2.9/notes/numerical_accuracy.html).

Shift invariance also has a finite-representation limit. If a huge common offset has already rounded two distinct logits to the same stored value, subtracting their maximum cannot recover the lost difference. The lesson's 1000 and 999 remain distinct and are therefore an appropriate stability fixture. A NaN input is a different case: maximum subtraction does not repair it, and the explicit validator rejects it before evaluating the objective.

Autocast selects operation dtypes according to a backend policy. It is not equivalent to converting every model tensor and intermediate to float16. Some operations may run or accumulate in higher precision, while others use a lower-precision path. Eligibility and kernel behavior are device/version specific. A CPU bfloat16 path and a CUDA float16 path therefore need separate acceptance rather than one generic mixed-precision label. [PyTorch 2.9 AMP](https://docs.pytorch.org/docs/2.9/amp.html).

Gradient scaling addresses another boundary. Multiplying a scalar loss by s multiplies its derivatives by s. An update workflow can compute those scaled derivatives, unscale them back to ordinary units, and detect nonfinite values before an optimizer step. This can protect some small backward values from underflow. It cannot recover information already lost in the forward pass or make an invalid loss meaningful.

Clipping thresholds must be applied to unscaled gradients if they are defined in ordinary gradient units. Otherwise changing the scale factor silently changes the effective clipping policy. A scaler may skip an optimizer update after detecting overflow; step counters, scheduler progression and logs should distinguish an attempted iteration from an actual parameter update. The scaler's own state belongs in a training checkpoint when it affects subsequent behavior.

A stable finite loss can still optimize the wrong example pairing, class index or reduction. Conversely, a finite forward value can have a problematic derivative at a singular or extreme point. Check forward inputs, loss, gradients and resulting parameter state as separate stages. The default examples retain small deterministic CPU work and make no throughput or accelerator-memory claim.

## Exercise 1: Find the float64 overflow boundary

The question is: Exponentiate float64 values 709 and 710.

The float64 maximum is about 1.8e308, between \(e^{709}\) and \(e^{710}\); for float32 the boundary lies between 88 and 89.

```python
big = torch.tensor([709.0, 710.0], dtype=torch.float64)
grown = torch.exp(big)
assert torch.isfinite(grown[0]) and torch.isinf(grown[1])
```

**Expected:** \(e^{709}\) is finite (about 8.2e307); \(e^{710}\) overflows to inf.

**Verify:** In a fresh process, the exercise checks confirm `torch.isfinite(grown[0])` and `torch.isinf(grown[1])`.

## Exercise 2: Compute a stable loss for target 1

The question is: Use float32 logits [1000, 998] with target class 1.

cross_entropy subtracts the maximum logit internally, so only the difference of 2 matters.

```python
wide_logits = torch.tensor([[1000.0, 998.0]])
np.testing.assert_allclose(
    F.cross_entropy(wide_logits, torch.tensor([1])).item(), np.log1p(np.exp(2)), atol=1e-5, rtol=0
)
```

**Expected:** loss \(\log(1+e^{2})\), about 2.1269, within 1e-5.

**Verify:** In a fresh process, the exercise checks confirm `F.cross_entropy(wide_logits, torch.tensor([1])).item()` matches `np.log1p(np.exp(2))` within 1e-05.

## Exercise 3: Check a new shift

The question is: Compare the softmax of [1000, 998] with the softmax of [5, 3].

Subtracting 995 from both logits leaves the probabilities unchanged.

```python
torch.testing.assert_close(
    torch.softmax(wide_logits[0], 0), torch.softmax(torch.tensor([5.0, 3.0]), 0), atol=1e-6, rtol=0
)
np.testing.assert_allclose(
    torch.softmax(torch.tensor([5.0, 3.0]), 0)[0].item(), 1 / (1 + np.exp(-2)), atol=1e-6, rtol=0
)
```

**Expected:** both are about [0.8808, 0.1192] and match within 1e-6.

**Verify:** In a fresh process, the exercise checks confirm `torch.softmax(wide_logits[0], 0)` matches `torch.softmax(torch.tensor([5.0, 3.0]), 0)` within 1e-06 and `torch.softmax(torch.tensor([5.0, 3.0]), 0)[0].item()` matches `1 / (1 + np.exp(-2))` within 1e-06.

## Exercise 4: Inspect stable gradients

The question is: Differentiate the target 0 loss with respect to both logits.

The derivative is probability minus the target indicator. Its components sum to zero because both distributions have total mass one.

```python
values = logits.clone().requires_grad_()
F.cross_entropy(values[None, :], torch.tensor([0])).backward()
assert torch.isfinite(values.grad).all()
np.testing.assert_allclose(values.grad.sum().item(), 0, atol=1e-6, rtol=0)
```

**Expected:** finite gradients summing approximately 0.

**Verify:** In a fresh process, the exercise checks confirm `torch.isfinite(values.grad).all()` and `values.grad.sum().item()` matches `0` within 1e-06.

## Exercise 5: Compare dtype ranges explicitly

The question is: Inspect float16 and bfloat16 maximum values and float32 epsilon.

bfloat16 has a wider exponent range but fewer fraction bits than float16. Range alone does not determine accuracy or backend support.

```python
assert torch.finfo(torch.bfloat16).max > torch.finfo(torch.float16).max
assert torch.finfo(torch.float32).eps > 0
```

**Expected:** bfloat16 range exceeds float16; float32 epsilon positive.

**Verify:** In a fresh process, the exercise checks confirm `torch.finfo(torch.bfloat16).max > torch.finfo(torch.float16).max` and `torch.finfo(torch.float32).eps > 0`.

## Exercise 6: Reject a nonfinite input contract

The question is: Pass a NaN logit through an explicit finite-input validator.

Stable algebra protects particular finite inputs from avoidable overflow. It does not turn a NaN source into a meaningful probability model.

```python
def checked_loss(value, target):
    if not bool(torch.isfinite(value).all()):
        raise ValueError("finite logits required")
    return F.cross_entropy(value, target)


try:
    checked_loss(torch.tensor([[0.0, float("nan")]]), torch.tensor([0]))
except ValueError:
    pass
else:
    raise AssertionError("NaN logits accepted")
```

**Expected:** ValueError before loss evaluation.

**Verify:** In a fresh process, the exercise checks confirm `checked_loss(torch.tensor([[0.0, float('nan')]]), torch.tensor([0]))` raises `ValueError`.

## Review after comparison

Repeat exercise 4, Inspect stable gradients, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, Compare dtype ranges explicitly, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.
