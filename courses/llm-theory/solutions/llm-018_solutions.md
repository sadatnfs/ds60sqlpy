# llm-018: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A training loop changes model state through a controlled sequence: clear gradients, calculate logits, reduce loss over active targets, backpropagate, inspect gradients and apply one update. Without zeroing, gradients accumulate. Without optimizer.step, losses may be repeatedly computed while weights never change. A bounded loop records an exact update count and stops even if the model has not converged. This lesson trains a small literal transition task for twelve steps, well below the two-hundred-step ceiling. Finite losses and a changed parameter demonstrate a functioning update path; they do not demonstrate held-out language quality.

**Training step:** One gradient calculation followed by one optimizer update.

**Gradient norm:** A magnitude summary used to diagnose update scale.

**Step budget:** A hard upper bound on optimization work.

## Reading the implementation

model.train() declares training behavior. Adam operates on model.parameters(). zero_grad(set_to_none=True) removes previous leaf gradients. Flatten logits and shifted labels for cross entropy. Compute a gradient norm after backward and before step. Snapshot parameters with detach().clone(), because a reference to the same tensor would change with the model and hide updates.

## Exercise 1: Prepare a tiny training batch

The question is: Use two four-token sequences and shifted labels with vocabulary16.

The fixture is small enough to enumerate every target. The context length and vocabulary remain below the decoder limits.

```python
torch.manual_seed(7)
model = TinyDecoder()
ids = torch.tensor([[1, 2, 3, 4], [2, 3, 4, 5]])
inputs = ids[:, :-1]
targets = ids[:, 1:]
assert tuple(inputs.shape) == (2, 3) and targets.numel() == 6
```

**Expected:** inputs shape(2,3);6 active targets.

**Verify:** Compare the computed values or written argument with inputs shape(2,3);6 active targets.

## Exercise 2: Measure the initial objective

The question is: Calculate initial cross entropy before any optimizer step.

The initial value is an observation for the fixed seed and implementation. It is not a promised constant across every library version.

```python
logits, _ = model(inputs)
initial = F.cross_entropy(logits.reshape(-1, 16), targets.reshape(-1)).item()
assert np.isfinite(initial) and initial > 0
```

**Expected:** finite positive loss.

**Verify:** Compare the computed values or written argument with finite positive loss.

## Exercise 3: Perform twelve bounded updates

The question is: Use Adam(.01), zero gradients each step, log losses and norms, and update exactly12 times.

The norm is captured before the optimizer mutates weights. Saving the entire short trace makes the first nonfinite or missing update visible.

```python
opt = torch.optim.Adam(model.parameters(), lr=0.01)
before = model.output.weight.detach().clone()
losses = []
norms = []
for _ in range(12):
    opt.zero_grad(set_to_none=True)
    logits, _ = model(inputs)
    loss = F.cross_entropy(logits.reshape(-1, 16), targets.reshape(-1))
    loss.backward()
    norm = (
        sum(float(p.grad.square().sum()) for p in model.parameters() if p.grad is not None) ** 0.5
    )
    losses.append(loss.item())
    norms.append(norm)
    opt.step()
assert len(losses) == 12 and np.isfinite(losses + norms).all() and max(norms) > 0
```

**Expected:** 12 finite losses and norms; at least one positive norm.

**Verify:** Compare the computed values or written argument with 12 finite losses and norms; at least one positive norm.

## Exercise 4: Verify actual parameter change

The question is: Compare the output projection with its detached snapshot.

A printed training message or decreasing cached value cannot prove an update. The snapshot must own its data so it does not alias the live parameter.

```python
assert not torch.equal(before, model.output.weight.detach())
```

**Expected:** weights differ.

**Verify:** Compare the computed values or written argument with weights differ.

## Exercise 5: Clear accumulated gradients

The question is: Call zero_grad(set_to_none=True) after the run and inspect every parameter gradient.

This confirms the intended reset policy. Accumulating gradients deliberately is possible, but requires an explicit denominator and update schedule.

```python
opt.zero_grad(set_to_none=True)
assert all(p.grad is None for p in model.parameters())
```

**Expected:** all gradientsNone.

**Verify:** Compare the computed values or written argument with all gradientsNone.

## Exercise 6: Report budget honestly

The question is: Create a run record with12 completed updates and the declared200 maximum.

Stopping a bounded diagnostic is not evidence of convergence. The report states what was executed and leaves held-out quality to a separate experiment.

```python
report = {
    "steps": 12,
    "maximum_steps": 200,
    "initial_loss": initial,
    "last_training_loss": losses[-1],
    "convergence_established": False,
}
assert report["steps"] <= report["maximum_steps"] and report["convergence_established"] is False
```

**Expected:** stopped_at12; no convergence claim.

**Verify:** Compare the computed values or written argument with stopped_at12; no convergence claim.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
