# torch-023: explanatory solutions

Open these answers only after attempting Debugging custom loops, accumulation and clipping yourself. They reuse the guide's literal inputs, starting from Example A, Expose detachment, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Disconnected loss, Gradient clipping, Update trace. After a pass, choose a new input for exercise 6, Recompute post-update loss, without looking.

After comparing, follow the [review steps](../STUDY-GUIDE.md#after-the-solutions).

## Mechanism review

A custom training loop can fail by disconnecting the graph, forgetting an update, reusing old gradients or applying an incorrect reduction. Debug the first small state transition before adding epochs and logging infrastructure. A gradient of None means no stored derivative was produced for that parameter; a zero tensor may be a valid derivative. Clearing with set_to_none preserves that diagnostic distinction.

Gradient clipping limits a norm after backward and before the optimizer step. It does not repair invalid labels, nonfinite forward values or a data leak. The clip function returns the pre-clipping norm, which is useful for diagnostics. Repeatedly clipping large gradients may indicate an underlying objective or scale problem rather than a complete fix. This lesson uses exact scalar updates and a [3, 4] gradient vector so all observations have independent oracles.

**Disconnected loss:** A value with no gradient path to the intended parameters.

**Gradient clipping:** Bounding gradient magnitude before an update.

**Update trace:** A sequence of parameter, loss and gradient observations.

## Reading the implementation

Check `loss.requires_grad` and parameter.grad before calling step. Use `optimizer.zero_grad(set_to_none=True)` for independent updates. nn.utils.clip_grad_norm_ mutates gradients in place and returns the norm before clipping. Record weight before, gradient before clipping, gradient after clipping and weight after step as distinct states. A detached numeric loss cannot backpropagate to its origin.

## Trace the optimizer state transition and objective denominator

Example A computes a numeric loss from \(w=0\) and detaches it. Its value is still four, but its dependency on w is no longer in the recorded graph. Setting `requires_grad` on that detached scalar would create a new leaf; it would not reconstruct the missing operation. The failed backward leaves the original parameter unchanged, so the sequential Example B still begins at \(w=0\).

For x=[1, 2, 3], y=2x and mean squared error, the objective is \(L(w)=\frac{14}{3}(w-2)^2\). Its derivative is \(\frac{28}{3}(w-2)\). With learning rate \(\frac{1}{10}\), the update is \(w_{\mathrm{next}}=\frac{w}{15}+\frac{28}{15}\). The exact trace is:

| Step | Weight before | Loss before | Gradient | Weight after |
| --- | --- | --- | --- | --- |
| first | 0 | \(\frac{56}{3}\) | \(\frac{-56}{3}\) | \(\frac{28}{15}\) |
| second | \(\frac{28}{15}\) | \(\frac{56}{675}\) | \(\frac{-56}{45}\) | \(\frac{448}{225}\) |

The loss at the final weight is \(\frac{56}{151875}\). A logged loss tensor calculated before step still represents the earlier state after the parameter changes. Recompute the forward objective to report post-update loss; printing the new weight beside the old loss without labeling them mixes two different states.

backward adds to stored gradient buffers. If the second step does not clear the first gradient, the stored value becomes \(\frac{-56}{3}-\frac{56}{45}=\frac{-896}{45}\), and the next weight becomes \(\frac{868}{225}\) rather than \(\frac{448}{225}\). That precise wrong trace distinguishes accidental accumulation from a wrong derivative formula. `set_to_none=True` also makes absence visible: None means no stored gradient was produced for that parameter in the relevant pass, whereas a connected derivative can be an actual zero. An optimizer may treat those cases differently, especially with state or decay.

Intentional microbatch accumulation needs a global denominator. Split the same three rows into one row and two rows at \(w=0\). The local mean gradients are -4 and -26. Averaging those means equally gives -15, but the full-data gradient is (1×(-4)+2×(-26))/3=\(\frac{-56}{3}\). One correct implementation weights each local mean by its valid-example count divided by the total, or accumulates local summed losses and divides by the total valid count. For padded tokens or sample weights, the denominator is the valid weight mass, not necessarily the number of stored rows.

This algebra assumes an additive loss evaluated at the same parameter state with equivalent forward behavior. Updating parameters between microbatches is a different trajectory. BatchNorm statistics, dropout draws, contrastive in-batch negatives and other batch-dependent computations can make a large batch differ even when gradient normalization is correct. State the scope of an equivalence claim rather than using accumulation as a universal replacement.

Norm clipping is another nonlinear boundary. Concatenate the participating parameter gradients into g. L2 clipping uses approximately g'=g×min(1, c/||g||), with a small numerical stabilizer in the implementation. For [3, 4], the norm is five and \(c=1\) gives approximately [0.6, 0.8]. The function returns the original five while mutating gradients in place. Starting from zero, plain SGD at 0.1 then moves to approximately [-0.06, -0.08]. [PyTorch 2.9 clip_grad_norm_](https://docs.pytorch.org/docs/2.9/generated/torch.nn.utils.clip_grad_norm_.html).

Clipping each contribution before accumulation can change the result. Scalar contributions 100 and -99 sum to one; clipping their sum to magnitude one leaves one. Clipping each separately to±1 and then adding gives zero. Therefore clip at the declared update boundary after the intended weighting and accumulation. With scaled gradients, unscale before applying a threshold expressed in ordinary gradient units.

Clipping limits the supplied gradient norm. It does not universally bound optimizer displacement when momentum, adaptive preconditioning, weight decay or retained state also affect the update. It also cannot repair invalid labels, nonfinite forward values or leakage. `error_if_nonfinite=True` makes an infinite/NaN norm a refusal rather than a meaningful update. The unchanged CPU fixture checks these local distinctions; it does not qualify mixed-precision or distributed execution.

## Exercise 1: Detect a detached intermediate

The question is: With Parameter w=1, compute h=(3w).detach() and loss=(h-1)**2, then inspect tracking and attempt backward.

Detaching any intermediate cuts every path from the loss to the parameter, not only the final step.

```python
wd = nn.Parameter(torch.tensor(1.0, dtype=torch.float64))
hidden_value = (wd * 3).detach()
cut = (hidden_value - 1) ** 2
assert not cut.requires_grad
try:
    cut.backward()
except RuntimeError:
    pass
else:
    raise AssertionError("detached intermediate backpropagated")
```

**Expected:** `loss.requires_grad` is False and backward raises RuntimeError.

**Verify:** In a fresh process, the exercise checks confirm `not cut.requires_grad` and `cut.backward()` raises `RuntimeError`.

## Exercise 2: Trace two updates on a new target

The question is: Train w from 0 on x = 1, 2, 3 with y = 3x, two SGD steps with learning rate 0.1, clearing gradients before each.

The error w-3 shrinks by the factor 1-0.1*28/3=1/15 per step: -3, -0.2, then -1/75.

```python
wt = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
xt = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
yt = 3 * xt
opt_t = torch.optim.SGD([wt], lr=0.1)
seen = []
for _ in range(2):
    opt_t.zero_grad(set_to_none=True)
    ((wt * xt - yt) ** 2).mean().backward()
    opt_t.step()
    seen.append(wt.item())
np.testing.assert_allclose(seen, [2.8, 224 / 75], atol=1e-12, rtol=0)
```

**Expected:** weights 2.8 then 224/75.

**Verify:** In a fresh process, the exercise checks confirm `seen` matches `[2.8, 224 / 75]` within 1e-12.

## Exercise 3: Clip a new gradient

The question is: Assign gradient [6, 8] to a parameter vector and clip it to norm 5.

clip_grad_norm_ returns the norm before clipping and rescales by about 5/10, keeping the direction.

```python
vector = nn.Parameter(torch.zeros(2))
vector.grad = torch.tensor([6.0, 8.0])
norm = torch.nn.utils.clip_grad_norm_([vector], 5.0)
assert norm.item() == 10
torch.testing.assert_close(vector.grad, torch.tensor([3.0, 4.0]), atol=1e-5, rtol=0)
```

**Expected:** returned norm 10; clipped gradient approximately [3, 4].

**Verify:** In a fresh process, the exercise checks confirm `norm.item() == 10` and `vector.grad` matches `torch.tensor([3.0, 4.0])` within 1e-05.

## Exercise 4: Apply the clipped update

The question is: Use SGD with rate 0.1 after clipping and inspect the parameter.

Clipping after step would not undo an oversized update. The order backward, inspect, clip, step is part of the training contract.

```python
torch.optim.SGD([parameter], lr=0.1).step()
torch.testing.assert_close(parameter.detach(), torch.tensor([-0.06, -0.08]), atol=1e-6, rtol=0)
```

**Expected:** approximately -0.06, -0.08.

**Verify:** In a fresh process, the exercise checks confirm `parameter.detach()` matches `torch.tensor([-0.06, -0.08])` within 1e-06.

## Exercise 5: Reject nonfinite gradient norms

The question is: Assign an infinite gradient and request error_if_nonfinite True.

A finite clipping threshold cannot make diverge n t state trustworthy. Stop and diagnose the first nonfinite operation rather than continue with contaminated weights.

```python
bad = nn.Parameter(torch.zeros(1))
bad.grad = torch.tensor([float("inf")])
try:
    torch.nn.utils.clip_grad_norm_([bad], 1.0, error_if_nonfinite=True)
except RuntimeError:
    pass
else:
    raise AssertionError("nonfinite gradient accepted")
```

**Expected:** RuntimeError before a valid update.

**Verify:** In a fresh process, the exercise checks confirm `torch.nn.utils.clip_grad_norm_([bad], 1.0, error_if_nonfinite=True)` raises `RuntimeError`.

## Exercise 6: Recompute post-update loss

The question is: Calculate current loss after the two scalar updates and compare with the one-step oracle.

An old loss object does not retroactively change when the parameter changes. Recompute at the new state before labelling a value post-update.

```python
after = ((w * x - y) ** 2).mean().item()
assert 0 <= after < 56 / 675
```

**Expected:** nonnegative and below \(\frac{56}{675}\).

**Verify:** In a fresh process, the exercise checks confirm `0 <= after < 56 / 675`.

