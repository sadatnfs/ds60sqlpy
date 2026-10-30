# llm-019: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Overfitting one batch is a diagnostic, not a quality assessment. If a sufficiently flexible model cannot reduce loss on a tiny repeated batch, inspect the target shift, gradient path, optimizer update and output dimension before scaling data. A no-update control distinguishes genuine learning from repeated forward passes. The control should retain exactly the same weights. The working loop has the same initial state and budget but applies updates. Memorizing a handful of transitions demonstrates a functioning optimization path under those conditions; it says nothing about unseen documents or factual answers.

**Overfit diagnostic:** Deliberately memorizing a tiny batch to test the training path.

**Control:** An otherwise comparable run without the intervention.

**Memorization:** Fit to exposed examples without evidence of transfer.

## Reading the implementation

Create two independent models from the same state_dict. Use dropout-free evaluation-compatible architecture so repeated control predictions are deterministic. The control calculates loss under no_grad without optimizer.step. The training loop zeros gradients and updates. Compare loss trajectories and weight snapshots, keeping the first failed invariant rather than only the final scalar.

## Exercise 1: Clone the initial state

The question is: Build two identical decoders with seed9 and copy one state into the other.

Independent model objects avoid shared mutation. Copying the state establishes a fair starting point for the update intervention.

```python
torch.manual_seed(9)
trained = TinyDecoder()
control = TinyDecoder()
control.load_state_dict(trained.state_dict())
assert all(torch.equal(a, b) for a, b in zip(trained.parameters(), control.parameters()))
x = torch.tensor([[1, 2, 3]])
y = torch.tensor([[2, 3, 4]])
```

**Expected:** all parameter tensors initially equal.

**Verify:** Compare the computed values or written argument with all parameter tensors initially equal.

## Exercise 2: Run a no-update control

The question is: Compute the same loss5 times without backward or step.

Repeated execution is not training. The control demonstrates the difference without relying on log messages or an optimizer object merely existing.

```python
before = {k: v.clone() for k, v in control.state_dict().items()}
values = []
with torch.no_grad():
    for _ in range(5):
        z, _ = control(x)
        values.append(F.cross_entropy(z.reshape(-1, 16), y.reshape(-1)).item())
assert len(set(values)) == 1 and all(
    torch.equal(v, before[k]) for k, v in control.state_dict().items()
)
```

**Expected:** all losses equal; weights unchanged.

**Verify:** Compare the computed values or written argument with all losses equal; weights unchanged.

## Exercise 3: Train the repeated batch

The question is: Apply30 Adam(.02) updates to the other model, using the same batch each time.

The comparison is local to one known batch. A loss decrease proves that this loop can adjust its prediction of exposed transitions, not that the dataset is appropriate.

```python
opt = torch.optim.Adam(trained.parameters(), lr=0.02)
curve = []
for _ in range(30):
    opt.zero_grad(set_to_none=True)
    z, _ = trained(x)
    loss = F.cross_entropy(z.reshape(-1, 16), y.reshape(-1))
    curve.append(loss.item())
    loss.backward()
    opt.step()
assert np.isfinite(curve).all() and curve[-1] < curve[0]
```

**Expected:** final batch loss below its initial loss.

**Verify:** Compare the computed values or written argument with final batch loss below its initial loss.

## Exercise 4: Check the class axis

The question is: Inspect logits before flattening and verify vocabulary dimension16.

Cross entropy needs one score per class for each active target. Flattening before checking axes can conceal swapped time and vocabulary dimensions.

```python
z, _ = trained(x)
assert tuple(z.shape) == (1, 3, 16)
```

**Expected:** shape(1,3,16).

**Verify:** Compare the computed values or written argument with shape(1,3,16).

## Exercise 5: Verify the control stayed isolated

The question is: Compare control state with its original snapshot after training the other model.

This catches accidental sharing of parameter storage or an optimizer configured with the wrong model parameters.

```python
assert all(torch.equal(v, before[k]) for k, v in control.state_dict().items())
```

**Expected:** every control tensor unchanged.

**Verify:** Compare the computed values or written argument with every control tensor unchanged.

## Exercise 6: Limit the conclusion

The question is: Write a diagnostic record naming one training sequence and zero held-out sequences.

A successful memorization test should trigger the next evaluation stage, not a deployment claim. If the test fails, preserve its smallest failing batch for debugging.

```python
report = {
    "repeated_sequences": 1,
    "updates": 30,
    "heldout_count": 0,
    "generalization_established": False,
}
assert report["heldout_count"] == 0 and not report["generalization_established"]
```

**Expected:** heldout_count0 and generalization_establishedFalse.

**Verify:** Compare the computed values or written argument with heldout_count0 and generalization_establishedFalse.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
