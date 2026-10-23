# torch-029: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Numerical stability concerns how an equivalent mathematical expression behaves in a finite representation. Logits 1000, 999 define a valid two-class distribution, but directly exponentiating them overflows common floating-point types. Subtracting a shared maximum before softmax preserves the distribution. CrossEntropyLoss and log sum exp implement stable combined operations that avoid unnecessary probability round trips.

Precision and range differ across float16, bfloat 16, float32 and float64. Automatic mixed precision selects operation dtypes under a backend policy; gradient scaling addresses underflow in certain training paths. Those mechanisms require hardware-specific validation. This default CPU lesson checks stable objectives and dtype limits without claiming GPU speed or a qualified mixed-precision training configuration. A stable loss can still optimize the wrong labels or denominator, so numerical and semantic checks remain separate.

**Overflow:** A result exceeding the numeric type's representable range.

**Log-sum-exp:** A stable logarithm of summed exponentials.

**Mixed precision:** A policy using different numeric types for different operations.

**Gradient scaling:** A technique changing gradient magnitude during certain low-precision training workflows.

## Reading the implementation

Use F.cross_entropy on raw logits and torch.logsumexp for a stable log normalizer. Inspect torch.isfinite on forward values and gradients. torch.finfo reports representable ranges and epsilon, but is not a performance benchmark. Keep dtype explicit in independent arithmetic comparisons. Do not cast arbitrary nonfinite inputs into a lower-precision type and expect a stable objective to repair them.

## Separate the mathematical distribution from its representation

For logits z=[1000, 999], the first-class probability is \(\frac{\exp(1000)}{\exp(1000)+\exp(999)}\). Dividing numerator and denominator by \(\exp(1000)\) gives \(\frac{1}{1+\exp(-1)}\), approximately 0.731059. The other probability is approximately 0.268941. The mathematical ratio is well defined even though directly materializing \(\exp(1000)\) overflows the types used in the counterexample.

More generally, subtracting the same finite m from every logit preserves softmax in exact arithmetic. Choosing \(m=\max(z)\) makes every shifted exponent at most one and at least one exactly one. For the target 0 loss, the shifted form is \(\log(1+\exp(-1))\), approximately 0.313262. The gradient is p-one_hot(target), or approximately[-0.268941, 0.268941]. Its entries sum to zero because a common logit shift does not change the objective. This gives an independent forward and backward contract.

Stability is more specific than a function name. logsumexp avoids raw exponential overflow, but computing a large logsumexp value and then subtracting a nearly equal large target logit can still lose precision. A fused logits loss or log_softmax formulation can preserve the small relative difference more directly. Similarly, computing a tiny probability and then taking its log can underflow where a direct log-probability calculation remains finite. Inspect intermediate representation rather than assuming algebraic equivalence implies equal floating-point error.

Range and precision are different properties:

| Type | Approximate maximum finite magnitude | Relative spacing near one |
| --- | --- | --- |
| float16 | 65, 504 | \({2}^{-10}\) |
| bfloat 16 | \(3.39\cdot {10}^{38}\) | \({2}^{-7}\) |
| float32 | \(3.4\cdot {10}^{38}\) | \({2}^{-23}\) |
| float64 | \(1.8\cdot {10}^{308}\) | \({2}^{-52}\) |

bfloat 16 has a much wider exponent range than float16 but fewer fraction bits. A value can avoid overflow while still be represented coarsely. Epsilon near one is not a universal absolute tolerance for all magnitudes or all algorithms. Summation length, conditioning, cancellation and the operations actually performed matter. [PyTorch 2.9 numerical accuracy](https://docs.pytorch.org/docs/2.9/notes/numerical_accuracy.html).

Shift invariance also has a finite-representation limit. If a huge common offset has already rounded two distinct logits to the same stored value, subtracting their maximum cannot recover the lost difference. The lesson's1000 and 999 remain distinct and are therefore an appropriate stability fixture. A NaN input is a different case: maximum subtraction does not repair it, and the explicit validator rejects it before evaluating the objective.

Autocast selects operation dtypes according to a backend policy. It is not equivalent to converting every model tensor and intermediate to float16. Some operations may run or accumulate in higher precision, while others use a lower-precision path. Eligibility and kernel behavior are device/version specific. A CPU bfloat 16 path and a CUDA float16 path therefore need separate acceptance rather than one generic mixed-precision label. [PyTorch 2.9 AMP](https://docs.pytorch.org/docs/2.9/amp.html).

Gradient scaling addresses another boundary. Multiplying a scalar loss by s multiplies its derivatives by s. An update workflow can compute those scaled derivatives, unscale them back to ordinary units, and detect nonfinite values before an optimizer step. This can protect some small backward values from underflow. It cannot recover information already lost in the forward pass or make an invalid loss meaningful.

Clipping thresholds must be applied to unscaled gradients if they are defined in ordinary gradient units. Otherwise changing the scale factor silently changes the effective clipping policy. A scaler may skip an optimizer update after detecting overflow; step counters, scheduler progression and logs should distinguish an attempted iteration from an actual parameter update. The scaler's own state belongs in a training checkpoint when it affects subsequent behavior.

A stable finite loss can still optimize the wrong example pairing, class index or reduction. Conversely, a finite forward value can have a problematic derivative at a singular or extreme point. Check forward inputs, loss, gradients and resulting parameter state as separate stages. The default examples retain small deterministic CPU work and make no throughput or accelerator-memory claim.

## Exercise 1: Expose naive overflow

The question is: Exponentiate float32 logits 1000, 999 directly.

The underlying probabilities are well defined. The failure comes from an unstable intermediate representation, not an impossible classification task.

```python
logits=torch.tensor([1000.,999.],dtype=torch.float32); naive=torch.exp(logits)
assert torch.isinf(naive).all()
```

**Expected:** both exponentials infinite.

**Verify:** Compare the computed values or written argument with both exponentials infinite.

## Exercise 2: Compute a stable class loss

The question is: Use target 0 with the same logits.

The meaningful score difference is one. The stable combined objective avoids constructing enormous raw exponential values.

```python
stable=F.cross_entropy(logits[None,:],torch.tensor([0]))
np.testing.assert_allclose(stable.item(),np.log1p(np.exp(-1)),atol=1e-6,rtol=0)
```

**Expected:** loss \(\log(1+\exp(-1))\) within 1e-6.

**Verify:** Compare the computed values or written argument with loss \(\log(1+\exp(-1))\) within 1e-6.

## Exercise 3: Check shift invariance

The question is: Compare softmax 1000, 999 with softmax 0, -1.

A common logit shift cancels from the normalizer. This property is useful for detecting wrong-axis or inconsistent-clipping implementations.

```python
torch.testing.assert_close(torch.softmax(logits,0),torch.softmax(torch.tensor([0.,-1.]),0),atol=1e-6,rtol=0)
```

**Expected:** probabilities match within 1e-6.

**Verify:** Compare the computed values or written argument with probabilities match within 1e-6.

## Exercise 4: Inspect stable gradients

The question is: Differentiate the target 0 loss with respect to both logits.

The derivative is probability minus the target indicator. Its components sum to zero because both distributions have total mass one.

```python
values=logits.clone().requires_grad_(); F.cross_entropy(values[None,:],torch.tensor([0])).backward()
assert torch.isfinite(values.grad).all(); np.testing.assert_allclose(values.grad.sum().item(),0,atol=1e-6,rtol=0)
```

**Expected:** finite gradients summing approximately 0.

**Verify:** Compare the computed values or written argument with finite gradients summing approximately 0.

## Exercise 5: Compare dtype ranges explicitly

The question is: Inspect float16 and bfloat 16 maximum values and float32 epsilon.

bfloat 16 has a wider exponent range but fewer fraction bits than float16. Range alone does not determine accuracy or backend support.

```python
assert torch.finfo(torch.bfloat16).max>torch.finfo(torch.float16).max
assert torch.finfo(torch.float32).eps>0
```

**Expected:** bfloat 16 range exceeds float16; float32 epsilon positive.

**Verify:** Compare the computed values or written argument with bfloat 16 range exceeds float16; float32 epsilon positive.

## Exercise 6: Reject a nonfinite input contract

The question is: Pass aN aN logit through an explicit finite-input validator.

Stable algebra protects particular finite inputs from avoidable overflow. It does not turn aN aN source into a meaningful probability model.

```python
def checked_loss(value,target):
    if not bool(torch.isfinite(value).all()): raise ValueError('finite logits required')
    return F.cross_entropy(value,target)
try: checked_loss(torch.tensor([[0.,float('nan')]]),torch.tensor([0]))
except ValueError: pass
else: raise AssertionError('NaN logits accepted')
```

**Expected:** ValueError before loss evaluation.

**Verify:** Compare the computed values or written argument with ValueError before loss evaluation.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
