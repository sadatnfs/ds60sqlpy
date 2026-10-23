# torch-023: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A custom training loop can fail by disconnecting the graph, forgetting an update, reusing old gradients or applying an incorrect reduction. Debug the first small state transition before adding epochs and logging infrastructure. A gradient of None means no stored derivative was produced for that parameter; a zero tensor may be a valid derivative. Clearing with set_to_none preserves that diagnostic distinction.

Gradient clipping limits a norm after backward and before the optimizer step. It does not repair invalid labels, nonfinite forward values or a data leak. The clip function returns the pre-clipping norm, which is useful for diagnostics. Repeatedly clipping large gradients may indicate an underlying objective or scale problem rather than a complete fix. This lesson uses exact scalar updates and a3, 4gradient vector so all observations have independent oracles.

**Disconnected loss:** A value with no gradient path to the intended parameters.

**Gradient clipping:** Bounding gradient magnitude before an update.

**Update trace:** A sequence of parameter, loss and gradient observations.

## Reading the implementation

Check loss.requires_grad and parameter.grad before calling step. Use optimizer.zero_grad(set_to_none=True) for independent updates. nn.utils.clip_grad_norm_ mutates gradients inplace and returns the norm before clipping. Record weight before, gradient before clipping, gradient after clipping and weight after step as distinct states. A detached numeric loss cannot backpropagate to its origin.

## Trace the optimizer state transition and objective denominator

Example A computes a numeric loss from w=0 and detaches it. Its value is still four, but its dependency on w is no longer in the recorded graph. Setting requires_grad on that detached scalar would create a new leaf; it would not reconstruct the missing operation. The failed backward leaves the original parameter unchanged, so the sequential Example B still begins at w=0.

For x=[1, 2, 3], y=2x and mean squared error, the objective is L(w)=(14/3)(w-2)^2. Its derivative is(28/3)(w-2). With learning rate 1/10, the update is w_next=w/15+28/15. The exact trace is:

| Step | Weight before | Loss before | Gradient | Weight after |
| --- | --- | --- | --- | --- |
| first | 0 | 56/3 | -56/3 | 28/15 |
| second | 28/15 | 56/675 | -56/45 | 448/225 |

The loss at the final weight is 56/151875. A logged loss tensor calculated before step still represents the earlier state after the parameter changes. Recompute the forward objective to report post-update loss; printing the new weight beside the old loss without labeling them mixes two different states.

backward adds to stored gradient buffers. If the second step does not clear the first gradient, the stored value becomes -56/3-56/45=-896/45, and the next weight becomes 868/225 rather than 448/225. That precise wrong trace distinguishes accidental accumulation from a wrong derivative formula. set_to_none=True also makes absence visible: None means no stored gradient was produced for that parameter in the relevant pass, whereas a connected derivative can be an actual zero. An optimizer may treat those cases differently, especially with state or decay.

Intentional microbatch accumulation needs a global denominator. Split the same three rows into one row and two rows at w=0. The local mean gradients are -4 and -26. Averaging those means equally gives -15, but the full-data gradient is(1×(-4)+2×(-26))/3=-56/3. One correct implementation weights each local mean by its valid-example count divided by the total, or accumulates local summed losses and divides by the total valid count. For padded tokens or sample weights, the denominator is the valid weight mass, not necessarily the number of stored rows.

This algebra assumes an additive loss evaluated at the same parameter state with equivalent forward behavior. Updating parameters between microbatches is a different trajectory. BatchNorm statistics, dropout draws, contrastive in-batch negatives and other batch-dependent computations can make a large batch differ even when gradient normalization is correct. State the scope of an equivalence claim rather than using accumulation as a universal replacement.

Norm clipping is another nonlinear boundary. Concatenate the participating parameter gradients into g. L2 clipping uses approximately g'=g×min(1, c/||g||), with a small numerical stabilizer in the implementation. For[3, 4], the norm is five and c=1 gives approximately[0.6, 0.8]. The function returns the original five while mutating gradients in place. Starting from zero, plain SGD at 0.1 then moves to approximately[-0.06, -0.08]. [PyTorch 2.9 clip_grad_norm_](https://docs.pytorch.org/docs/2.9/generated/torch.nn.utils.clip_grad_norm_.html).

Clipping each contribution before accumulation can change the result. Scalar contributions 100 and-99 sum to one; clipping their sum to magnitude one leaves one. Clipping each separately to±1 and then adding gives zero. Therefore clip at the declared update boundary after the intended weighting and accumulation. With scaled gradients, unscale before applying a threshold expressed in ordinary gradient units.

Clipping limits the supplied gradient norm. It does not universally bound optimizer displacement when momentum, adaptive preconditioning, weight decay or retained state also affect the update. It also cannot repair invalid labels, nonfinite forward values or leakage. error_if_nonfinite=True makes an infinite/NaN norm a refusal rather than a meaningful update. The unchanged CPU fixture checks these local distinctions; it does not qualify mixed-precision or distributed execution.

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

The question is: Usex 1, 2, 3, y2x, w0 and two SGD.1 steps with gradient clearing.

Comparing each state finds the first divergence. A final-value-only check can hide wrong intermediate logging or compensating errors.

```python
x=torch.tensor([1.,2.,3.],dtype=torch.float64); y=2*x; optimizer=torch.optim.SGD([w],lr=.1); history=[]
for _ in range(2):
    optimizer.zero_grad(set_to_none=True); loss=((w*x-y)**2).mean(); loss.backward(); assert w.grad is not None; optimizer.step(); history.append(w.item())
np.testing.assert_allclose(history,[28/15,448/225],atol=1e-12,rtol=0)
```

**Expected:** weights 28/15 then 448/225.

**Verify:** Compare the computed values or written argument with weights 28/15 then 448/225.

## Exercise 3: Inspect norm clipping

The question is: Assign gradient 3, 4 to a parameter vector and clip to norm 1.

The function returns the original norm, not the new one. The small numerical difference comes from the stabilizing epsilon in the clip coefficient.

```python
parameter=nn.Parameter(torch.zeros(2)); parameter.grad=torch.tensor([3.,4.])
before=torch.nn.utils.clip_grad_norm_([parameter],1.)
assert before.item()==5; torch.testing.assert_close(parameter.grad,torch.tensor([.6,.8]),atol=1e-6,rtol=0)
```

**Expected:** returned norm 5; new gradient approximately.6, .8.

**Verify:** Compare the computed values or written argument with returned norm 5; new gradient approximately.6, .8.

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

**Expected:** nonnegative and below 56/675.

**Verify:** Compare the computed values or written argument with nonnegative and below 56/675.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
