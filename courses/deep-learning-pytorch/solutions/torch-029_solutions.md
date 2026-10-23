# torch-029: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Numerical stability concerns how an equivalent mathematical expression behaves in a finite representation. Logits1000, 999 define a valid two-class distribution, but directly exponentiating them overflows common floating-point types. Subtracting a shared maximum before softmax preserves the distribution. CrossEntropyLoss and log sum exp implement stable combined operations that avoid unnecessary probability round trips.

Precision and range differ across float16, bfloat16, float32 and float64. Automatic mixed precision selects operation dtypes under a backend policy; gradient scaling addresses underflow in certain training paths. Those mechanisms require hardware-specific validation. This default CPU lesson checks stable objectives and dtype limits without claiming GPU speed or a qualified mixed-precision training configuration. A stable loss can still optimize the wrong labels or denominator, so numerical and semantic checks remain separate.

**Overflow:** A result exceeding the numeric type's represent able range.

**Log-sum-exp:** A stable logarithm of summed exponentials.

**Mixed precision:** A policy using different numeric types for different operations.

**Gradient scaling:** A technique changing gradient magnitude during certain low-precision training workflows.

## Reading the implementation

UseF.cross_entropy on raw logits and torch.log sum exp for a stable log normalizer. Inspect torch.isfinite on forward values and gradients. torch.finfo reports represent able ranges and epsilon, but is not a performance benchmark. Keep dtype explicit in independent arithmetic comparisons. Do not cast arbitrary nonfinite inputs into a lower-precision type and expect a stable objective to repair them.

## Exercise 1: Expose naive overflow

The question is: Exponentiate float32 logits1000, 999 directly.

The underlying probabilities are well defined. The failure comes from an unstable intermediate representation, not an impossible classification task.

```python
logits=torch.tensor([1000.,999.],dtype=torch.float32); naive=torch.exp(logits)
assert torch.isinf(naive).all()
```

**Expected:** both exponentials infinite.

**Verify:** Compare the computed values or written argument with both exponentials infinite.

## Exercise 2: Compute a stable class loss

The question is: Use target0 with the same logits.

The meaningful score difference is one. The stable combined objective avoids constructing enormous raw exponential values.

```python
stable=F.cross_entropy(logits[None,:],torch.tensor([0]))
np.testing.assert_allclose(stable.item(),np.log1p(np.exp(-1)),atol=1e-6,rtol=0)
```

**Expected:** loss log(1+exp(-1)) within1e-6.

**Verify:** Compare the computed values or written argument with loss log(1+exp(-1)) within1e-6.

## Exercise 3: Check shift invariance

The question is: Compare softmax1000, 999 with softmax0, -1.

A common logit shift cancels from the normalizer. This property is useful for detecting wrong-axis or inconsistent-clipping implementations.

```python
torch.testing.assert_close(torch.softmax(logits,0),torch.softmax(torch.tensor([0.,-1.]),0),atol=1e-6,rtol=0)
```

**Expected:** probabilities match within1e-6.

**Verify:** Compare the computed values or written argument with probabilities match within1e-6.

## Exercise 4: Inspect stable gradients

The question is: Differentiate the target0 loss with respect to both logits.

The derivative is probability minus the target indicator. Its components sum to zero because both distributions have total mass one.

```python
values=logits.clone().requires_grad_(); F.cross_entropy(values[None,:],torch.tensor([0])).backward()
assert torch.isfinite(values.grad).all(); np.testing.assert_allclose(values.grad.sum().item(),0,atol=1e-6,rtol=0)
```

**Expected:** finite gradients summing approximately0.

**Verify:** Compare the computed values or written argument with finite gradients summing approximately0.

## Exercise 5: Compare dtype ranges explicitly

The question is: Inspect float16 andbfloat16 maximum values and float32 epsilon.

bfloat16 has a wider exponent range but fewer fraction bits than float16. Range alone does not determine accuracy or backend support.

```python
assert torch.finfo(torch.bfloat16).max>torch.finfo(torch.float16).max
assert torch.finfo(torch.float32).eps>0
```

**Expected:** bfloat16 range exceeds float16; float32 epsilon positive.

**Verify:** Compare the computed values or written argument with bfloat16 range exceeds float16; float32 epsilon positive.

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
