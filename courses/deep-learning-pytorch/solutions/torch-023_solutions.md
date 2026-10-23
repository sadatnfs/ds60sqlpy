# torch-023: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A custom training loop can fail by disconnecting the graph, forgetting an update, reusing old gradients or applying an incorrect reduction. Debug the first small state transition before adding epochs and logging infrastructure. A gradient of None means no stored derivative was produced for that parameter; a zero tensor may be a valid derivative. Clearing with set_to_none preserves that diagnostic distinction.

Gradient clipping limits a norm after backward and before the optimizer step. It does not repair invalid labels, nonfinite forward values or a data leak. The clip function returns the pre-clipping norm, which is useful for diagnostics. Repeatedly clipping large gradients may indicate an underlying objective or scale problem rather than a complete fix. This lesson uses exact scalar updates and a3, 4 gradient vector so all observations have independent oracles.

**Disconnected loss:** A value with no gradient path to the intended parameters.

**Gradient clipping:** Bounding gradient magnitude before an update.

**Update trace:** A sequence of parameter, loss and gradient observations.

## Reading the implementation

Check loss.requires_grad and parameter.grad before calling step. Use optimizer.zero_grad(set_to_none=True) for independent updates. nn.utils.clip_grad_norm_ mutates gradients inplace and returns the norm before clipping. Record weight before, gradient before clipping, gradient after clipping and weight after step as distinct states. A detached numeric loss cannot backpropagate to its origin.

## Exercise 1: Expose detachment

The question is: Detach (w-2)**2 before backward and inspect tracking.

The loss may have the correct numeric value while the training path is broken. Re-enabling requires_grad on the detached scalar would create a new leaf, not reconnect w.

```python
w=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); disconnected=((w-2)**2).detach()
assert not disconnected.requires_grad
try: disconnected.backward()
except RuntimeError: pass
else: raise AssertionError('detached loss backpropagated')
```

**Expected:** detached loss requires_grad False; backward raises RuntimeError.

**Verify:** Compare the computed values or written argument with detached loss requires_grad False; backward raises RuntimeError.

## Exercise 2: Repair two exact updates

The question is: Usex1, 2, 3, y2 x, w0 and two SGD.1 steps with gradient clearing.

Comparing each state finds the first divergence. A final-value-only check can hide wrong intermediate logging or compensating errors.

```python
x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x; optimizer=torch.optim.SGD([w],lr=.1); history=[]
for _ in range(2):
    optimizer.zero_grad(set_to_none=True); loss=((w*x-y)**2).mean(); loss.backward(); assert w.grad is not None; optimizer.step(); history.append(w.item())
np.testing.assert_allclose(history,[28/15,448/225],atol=1e-12,rtol=0)
```

**Expected:** weights28/15 then448/225.

**Verify:** Compare the computed values or written argument with weights28/15 then448/225.

## Exercise 3: Inspect norm clipping

The question is: Assign gradient3, 4 to a parameter vector and clip to norm1.

The function returns the original norm, not the new one. The small numerical difference comes from the stabilizing epsilon in the clip coefficient.

```python
parameter=nn.Parameter(torch.zeros(2)); parameter.grad=torch.tensor([3.,4.])
before=torch.nn.utils.clip_grad_norm_([parameter],1.)
assert before.item()==5; torch.testing.assert_close(parameter.grad,torch.tensor([.6,.8]),atol=1e-6,rtol=0)
```

**Expected:** returned norm5; new gradient approximately.6, .8.

**Verify:** Compare the computed values or written argument with returned norm5; new gradient approximately.6, .8.

## Exercise 4: Apply the clipped update

The question is: Use SGD.1 after clipping and inspect the parameter.

Clipping after step would not undo an oversized update. The order backward, inspect, clip, step is part of the training contract.

```python
torch.optim.SGD([parameter],lr=.1).step()
torch.testing.assert_close(parameter.detach(),torch.tensor([-.06,-.08]),atol=1e-6,rtol=0)
```

**Expected:** approximately-.06, -.08.

**Verify:** Compare the computed values or written argument with approximately-.06, -.08.

## Exercise 5: Reject nonfinite gradient norms

The question is: Assign an infinite gradient and request error_if_nonfinite True.

A finite clipping threshold cannot make diverge n t state trustworthy. Stop and diagnose the first nonfinite operation rather than continue with contaminated weights.

```python
bad=nn.Parameter(torch.zeros(1)); bad.grad=torch.tensor([float('inf')])
try: torch.nn.utils.clip_grad_norm_([bad],1.,error_if_nonfinite=True)
except RuntimeError: pass
else: raise AssertionError('nonfinite gradient accepted')
```

**Expected:** RuntimeError before a valid update.

**Verify:** Compare the computed values or written argument with RuntimeError before a valid update.

## Exercise 6: Recompute post-update loss

The question is: Calculate current loss after the two scalar updates and compare with the one-step oracle.

An old loss object does not retroactively change when the parameter changes. Recompute at the new state before labelling a value post-update.

```python
after=((w*x-y)**2).mean().item(); assert 0<=after<56/675
```

**Expected:** nonnegative and below56/675.

**Verify:** Compare the computed values or written argument with nonnegative and below56/675.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
