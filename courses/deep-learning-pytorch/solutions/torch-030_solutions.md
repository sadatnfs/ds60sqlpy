# torch-030: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Distributed and accumulated gradients should represent a declared global objective. Equal averaging of shard means weights shards equally, not examples. If one shard contains one observation with mean gradient 2 and another contains three with mean 6, the global example mean is 5 rather than 4. The same issue appears with unequal microbatches on one CPU.

To reproduce a full-batch mean through accumulation, hold parameters fixed while adding gradient sums, divide by the total active count, and apply one optimizer update. Stepping after each microbatch is a different trajectory because later gradients use changed weights. Distributed Data Parallel has its own reduction semantics; this lesson does not launch multiple processes or claim scaling. It derives the weighting rule that a real distributed implementation must preserve and explains which additional runtime evidence would be required.

**Global objective:** The loss definition over all participating examples.

**Microbatch accumulation:** Combining derivatives before one parameter update.

**Sha rd weighting:** The rule assigning contributions from differently sized partitions.

**Distributed acceptance:** Actual multi-process behavior and failure evidence beyond scalar arithmetic.

## Reading the implementation

Use reduction='sum' for each microbatch, call backward without stepping, then divide accumulated gradients by the total count before one step. Clear gradients before starting the accumulation group. Count active masked targets when appropriate, not merely tensor storage size. If a distributed backend averages gradients across ranks, the local loss scaling must account for that reduction and unequal local counts.

## Derive the global gradient and the reduction factor

Let rank or shard r contain n_r participating examples, local gradient sum S_r and local mean \(g_{r}=\frac{S_{r}}{n_{r}}\) when \(n_{r}>0\). The global example-mean gradient is \(\frac{\sum_r S_r}{\sum_r n_r}\), equivalently \(\frac{\sum_r n_rg_r}{N}\). For means 2 and 6 with counts 1 and 3, the numerator is \(2+18=20\) and \(N=4\), giving five. Averaging the two means gives four and defines a different objective with equal shard weight.

The vector[2, 4, 6, 8] is an independent four-example oracle. Splitting it 1:3 gives sums 2 and 18, which recombine to \(\frac{20}{4}=5\). An empty shard contributes sum zero and count zero; its local mean need not be evaluated at all. A globally empty collection has \(N=0\) and must not be divided by zero or described as a valid zero-gradient batch without an explicit skip policy.

For the actual squared-loss fixture, x=[1, 2, 3, 4], y=2x and \(w=0\). The per-example derivatives are \(-4x^2\), or[-4, -16, -36, -64]. Their sum is-120 and global mean-30. The two backward calls in Example C accumulate the summed objectives at the same unchanged w, then divide once by four. One SGD update at 0.01 gives \(w=0.3\).

Stepping after each microbatch changes both normalization and evaluation state. The first one-row mean has gradient-4, so w becomes 0.04. The second three-row mean is then evaluated at that new value and has derivative(58/3)(0.04-2), approximately-37.893333. Its second update ends at approximately 0.418933, not 0.3. This discrepancy is expected because it is a different optimization trajectory, not an accumulation bug to hide with a tolerance.

A distributed reducer introduces another factor. Under a fixed R-rank configuration that averages gradients across ranks, backpropagating a local summed loss divided by global N would produce only \(\frac{1}{R}\) of the intended global gradient after averaging. One appropriate local scaling for this stated convention is \(L_r=\frac{R}{N}\sum_i\ell_{ri}\). The reducer then returns \(\frac1R\sum_r\frac{RS_r}{N}=\frac{\sum_rS_r}{N}\). Equivalently, weight each nonempty local mean by R \(\frac{n_{r}}{N}\). When all n_r are equal, the ordinary mean of local means already has the intended weighting.

That derivation assumes the documented reducer behavior and a fixed participation set. Custom communication hooks, uneven-input mechanisms and changed divisors require a fresh derivation. PyTorch DDP documents that its gradient synchronization semantics depend on the loss reduction and participating processes. [PyTorch 2.9 DistributedDataParallel](https://docs.pytorch.org/docs/2.9/generated/torch.nn.parallel.DistributedDataParallel.html). The current lesson launches no process group and therefore verifies none of that communication behavior experimentally.

Padding and sample weights replace the simple n_r with the relevant valid weight mass. Counting tensor storage positions instead of supervised tokens can scale the gradient according to padding. A rank with no valid targets may still need to participate in the distributed protocol; simply skipping its backward while other ranks enter collectives can be an operational error. The CPU arithmetic handles an empty contribution, but a real implementation needs a separately tested participation policy.

Regularization also needs one global meaning. If the objective is mean data loss plus lambda R(theta), adding the full regularizer independently for every accumulated microbatch and then summing multiplies its contribution by the microbatch count. Add it once per intended update or distribute its coefficient deliberately. Optimizer weight decay has its own update semantics and likewise should not be assumed equivalent when the number of optimizer steps changes.

The equivalence requires more than denominators. Parameters and relevant model state must stay fixed while local contributions are formed. BatchNorm statistics, dropout draws, contrastive negative sets and cross-example losses can differ when a large batch is split. Even a mathematically correct reduction cannot make those different forward computations identical. For stateful optimizers, the one-step boundary preserves the intended momentum/adaptive update count; multiple steps change that history.

A future distributed acceptance packet should join the global objective, rank counts, actual reducer convention, parameter synchronization, cancellation and next-step parity. It should also report communication and throughput only after those quantities are measured. The paired TensorFlow chapter derives the same global arithmetic but does not qualify a TensorFlow strategy or a PyTorch backend merely by simulating shards on one CPU.

## Exercise 1: Weight unequal shard means

The question is: Combine means 2, 6 with counts 1, 3.

Each mean must be multiplied by its denominator to recover a sum. Averaging means directly discards that information.

```python
means=torch.tensor([2.,6.]); counts=torch.tensor([1.,3.])
assert (means*counts).sum().div(counts.sum()).item()==5 and means.mean().item()==4
```

**Expected:** global mean 5; unweighted shard mean 4.

**Verify:** Compare the computed values or written argument with global mean 5; unweighted shard mean 4.

## Exercise 2: Reconstruct an example mean

The question is: Split gradients 2, 4, 6, 8 into one and three elements and recombine sums/counts.

The per-example vector is an independent oracle for the shard formula. It catches a checker that merely repeats a wrong averaging assumption.

```python
values=torch.tensor([2.,4.,6.,8.]); parts=[values[:1],values[1:]]
assert sum(part.sum() for part in parts).div(sum(part.numel() for part in parts)).item()==values.mean().item()==5
```

**Expected:** global mean 5.

**Verify:** Compare the computed values or written argument with global mean 5.

## Exercise 3: Accumulate one full-batch gradient

The question is: At \(w=0\), usex 1..4, y2x, accumulate squared-loss sums forshards 1 and 3, and divide by 4.

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

The question is: Reset w0and step after each shard mean instead.

This is ordinary minibatch training. It is not an implementation of one full-batch update because the second derivative is evaluated at a new state.

```python
other=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); optimizer=torch.optim.SGD([other],lr=.01)
for start,end in [(0,1),(1,4)]:
    optimizer.zero_grad(set_to_none=True); ((other*x[start:end]-y[start:end])**2).mean().backward(); optimizer.step()
assert abs(other.item()-.3)>1e-6
```

**Expected:** endpoint differs from.3.

**Verify:** Compare the computed values or written argument with endpoint differs from.3.

## Exercise 6: Represent empty-shard contributions

The question is: Combine an empty shard and the four real gradients using sums and counts.

A local empty shard can contribute a zero sum without computing an undefined mean. A globally empty batch must be rejected separately.

```python
empty=torch.empty(0); numerator=empty.sum()+values.sum(); denominator=empty.numel()+values.numel()
assert denominator==4 and numerator.div(denominator).item()==5
```

**Expected:** empty shard contributes 0; global mean 5.

**Verify:** Compare the computed values or written argument with empty shard contributes 0; global mean 5.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
