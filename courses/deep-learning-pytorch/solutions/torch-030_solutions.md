# torch-030: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Distributed and accumulated gradients should represent a declared global objective. Equal averaging of sha rd means weights shards equally, not examples. If one sha rd contains one observation with mean gradient2 and another contains three with mean6, the global example mean is5 rather than4. The same issue appears with unequal microbatches on one CPU.

To reproduce a full-batch mean through accumulation, hold parameters fixed while adding gradient sums, divide by the total active count, and apply one optimizer update. Stepping after each microbatch is a different trajectory because later gradients use changed weights. Distributed Data Parallel has its own reduction semantics; this lesson does not launch multiple processes or claim scaling. It derives the weighting rule that a real distributed implementation must preserve and explains which additional runtime evidence would be required.

**Global objective:** The loss definition over all participating examples.

**Microbatch accumulation:** Combining derivatives before one parameter update.

**Sha rd weighting:** The rule assigning contributions from differently sized partitions.

**Distributed acceptance:** Actual multi-process behavior and failure evidence beyond scalar arithmetic.

## Reading the implementation

Use reduction='sum' for each microbatch, call backward without stepping, then divide accumulated gradients by the total count before one step. Clear gradients before starting the accumulation group. Count active masked targets when appropriate, not merely tensor storage size. If a distributed backend averages gradients across ranks, the local loss scaling must account for that reduction and unequal local counts.

## Exercise 1: Weight unequal sha rd means

The question is: Combine means2, 6 with counts1, 3.

Each mean must be multiplied by its denominator to recover a sum. Averaging means directly discards that information.

```python
means=torch.tensor([2.,6.]); counts=torch.tensor([1.,3.])
assert (means*counts).sum().div(counts.sum()).item()==5 and means.mean().item()==4
```

**Expected:** global mean5; unweighted sha rd mean4.

**Verify:** Compare the computed values or written argument with global mean5; unweighted sha rd mean4.

## Exercise 2: Reconstruct an example mean

The question is: Split gradients2, 4, 6, 8 into one and three elements and recombine sums/counts.

The per-example vector is an independent oracle for the sha rd formula. It catches a checker that merely repeats a wrong averaging assumption.

```python
values=torch.tensor([2.,4.,6.,8.]); parts=[values[:1],values[1:]]
assert sum(part.sum() for part in parts).div(sum(part.numel() for part in parts)).item()==values.mean().item()==5
```

**Expected:** global mean5.

**Verify:** Compare the computed values or written argument with global mean5.

## Exercise 3: Accumulate one full-batch gradient

The question is: Atw0, usex1..4, y2 x, accumulate squared-loss sums forshards1 and3, and divide by 4.

The weight remains fixed across both backward calls. Accumulation is intentional here, and its denominator is applied exactly once.

```python
x=torch.arange(1,5,dtype=torch.float64); y=2*x; w=nn.Parameter(torch.tensor(0.,dtype=torch.float64))
for start,end in [(0,1),(1,4)]: ((w*x[start:end]-y[start:end])**2).sum().backward()
w.grad.div_(4)
assert w.grad.item()==-30
oracle=torch.tensor(0.,dtype=torch.float64,requires_grad=True); full=((oracle*x-y)**2).mean(); assert torch.autograd.grad(full,oracle)[0].item()==-30
```

**Expected:** gradient-30, matching full-batch mean.

**Verify:** Compare the computed values or written argument with gradient-30, matching full-batch mean.

## Exercise 4: Apply one accumulated update

The question is: Take SGD.01 after the global gradient is formed.

The effective batch produces one optimizer step. Learning-rate schedules and optimizer counters should follow that declared step unit.

```python
torch.optim.SGD([w],lr=.01).step(); np.testing.assert_allclose(w.item(),.3,atol=1e-12,rtol=0)
```

**Expected:** new weight.3.

**Verify:** Compare the computed values or written argument with new weight.3.

## Exercise 5: Contrast separate microbatch updates

The question is: Reset w0 and step after eachs hard mean instead.

This is ordinary minibatch training. It is not an implementation of one full-batch update because the second derivative is evaluated at a new state.

```python
other=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); optimizer=torch.optim.SGD([other],lr=.01)
for start,end in [(0,1),(1,4)]:
    optimizer.zero_grad(set_to_none=True); ((other*x[start:end]-y[start:end])**2).mean().backward(); optimizer.step()
assert abs(other.item()-.3)>1e-6
```

**Expected:** endpoint differs from.3.

**Verify:** Compare the computed values or written argument with endpoint differs from.3.

## Exercise 6: Represent empty-sha rd contributions

The question is: Combine an emptys hard and the four real gradients using sums and counts.

A local empty sha rd can contribute a zero sum without computing an undefined mean. A globally empty batch must be rejected separately.

```python
empty=torch.empty(0); numerator=empty.sum()+values.sum(); denominator=empty.numel()+values.numel()
assert denominator==4 and numerator.div(denominator).item()==5
```

**Expected:** empty sha rd contributes0; global mean5.

**Verify:** Compare the computed values or written argument with empty sha rd contributes0; global mean5.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
