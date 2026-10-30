# torch-012: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

An auditable regressor combines data identity, a baseline, an explicit training loop and separate assessment. The three-feature fixture uses target 2 a-b+c, so every row can be checked by hand. Four rows are used for fitting and two are reserved for assessment. A training-mean baseline provides a comparison that ignores features. The learned linear model updates under a fixed 100-step budget without using the holdout to choose settings.

The capstone must report what it actually establishes. A small synthetic holdout can show that the implementation uses features in the intended way, but it cannot establish robustness or population accuracy. Keep the scalar arithmetic pilot from lesson 008 as an independent mechanism check alongside the larger experiment. Hashing split IDs records identity; it does not prove the split design was appropriate.

**Experiment manifest:** The identities and settings needed to reconstruct a run.

**Training baseline:** A simple rule fitted only on training data.

**Frozen assessment:** Evaluation performed after model-selection choices are fixed.

## Reading the implementation

Create X shaped(6, 3), targets shaped(6, 1), and nn.Linear(3, 1, bias=False) with zero weights. Select rows by frozen index lists. Use MSELoss and SGD with rate 0.1, zeroing gradients every step. Evaluate after the fixed budget under no_grad. Record train and holdout losses with their counts, plus model state and split identities. Do not overwrite the original split after seeing errors.

## Derive a capstone oracle from the training design

The six input rows are zero, the three coordinate basis vectors, then[1, 1, 1] and[2, 1, 1]. The target is 2 a-b+c, so the targets are[0, 2, -1, 1, 2, 4]. The first four rows are training and the last two are assessment. Input shape is(6, 3), target shape(6, 1), and the bias-free Linear stores one row of three weights. This shape contract must remain unchanged throughout fitting and evaluation.

The training-only baseline is(0+2-1+1)/4=0.5. On assessment targets 2 and 4, its squared errors are 2.25 and 12.25, giving MSE 7.25. This baseline ignores features but uses the same assessment records and metric as the learned model. Fitting its constant to the assessment mean would invalidate that comparison.

The basis-vector training design makes the optimizer trajectory independently solvable. Let the stored weight row be w=[w_a, w_b, w_c] and the intended row be w*=[2, -1, 1]. The zero input contributes a zero residual because the model has no bias. The other three rows isolate one coefficient each, so the training objective is:

`L_train(w) = [(w_a-2)²+(w_b+1)²+(w_c-1)²]/4`.

Its gradient is(w-w*)/2. With SGD rate 0.1, one update changes the error to 0.95(w-w*). Starting at zero, after t updates the weight is`w_t=(1-0.95^t)w*`. This oracle does not read PyTorch's gradient buffer or reuse the training-loop implementation. It follows from the declared design matrix and denominator.

After 100 updates, the missing fraction is \(r={0.95}^{100}\), about 0.00592. The weights are approximately[1.98816, -0.99408, 0.99408]. The final training MSE is 1.5r² and the assessment MSE is 10 r², about 0.000351. The assessment formula follows because its predictions are(1-r) times targets 2 and 4, so the two squared residuals are 4 r² and 16 r². These exact symbolic quantities strengthen the capstone beyond merely observing that loss decreased or beat 7.25.

The curve records each loss before that iteration's update. Its first value is 1.5 and its last value corresponds to 99 completed updates, namely \(1.5\cdot {0.95}^{198}\). The separately recomputed final training error follows 100 updates and is \(1.5\cdot {0.95}^{200}\). Calling curve[-1] the final model's loss would create a one-step interpretation error even though every loop operation ran successfully.

The fixture is identifiable within this hypothesis class because the three nonzero training rows span all three feature directions. That mathematical fact helps explain successful recovery on linear combinations of those directions. It does not show that an arbitrary real dataset is linear, noise-free, representative orwell-conditioned. Adding a trainable bias, changing feature scaling or altering the loss denominator changes the derivation and requires a new oracle.

The final report should retain training and assessment IDs, their counts, parameter dtype and layout, initial state, actual update count, baseline score, final fixed-state errors and the visible synthetic limitation. model.eval() and no_grad make evaluation behavior and derivative recording explicit; no optimizer step occurs during assessment. The two assessment rows demonstrate the intended procedure, but are far too few and too deliberately constructed to support a broad reliability claim.

The paired TensorFlow implementation uses the same mathematical fixture in float32, whereas this PyTorch reference uses float64. Compare the function, transposed kernel layout, denominator and update count before tolerances. A small rounding difference is different from a missing update, an unintended bias or a changed split.

## Exercise 1: Create the three-feature fixture

The question is: Use rows zero, e1, e2, e3, [1, 1, 1], [2, 1, 1] and target 2 a-b+c.

The target formula is part of the fixture definition. The learner can inspect it without relying on an opaque downloaded dataset.

```python
x = torch.tensor(
    [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [2.0, 1.0, 1.0],
    ],
    dtype=torch.float64,
)
y = x @ torch.tensor([[2.0], [-1.0], [1.0]], dtype=torch.float64)
train = [0, 1, 2, 3]
test = [4, 5]
torch.testing.assert_close(
    y[:, 0], torch.tensor([0.0, 2.0, -1.0, 1.0, 2.0, 4.0], dtype=torch.float64), atol=0, rtol=0
)
```

**Expected:** targets 0, 2, -1, 1, 2, 4.

**Verify:** Compare the computed values or written argument with targets 0, 2, -1, 1, 2, 4.

## Exercise 2: Measure the training-mean baseline

The question is: Fit the constant from training targets and score the two holdout rows.

The baseline receives the same assessment rows as the model, but its constant is fitted only on training targets.

```python
mean = y[train].mean()
baseline = ((y[test] - mean) ** 2).mean()
assert mean.item() == 0.5 and baseline.item() == 7.25
```

**Expected:** mean.5; holdout MSE 7.25.

**Verify:** Compare the computed values or written argument with mean.5; holdout MSE 7.25.

## Exercise 3: Train a bounded linear model

The question is: Initialize a bias-free 3-to-1Linear layer at zero and run 100 SGD with rate 0.1 updates.

The fixed budget is decided before assessment. A successful decrease demonstrates fitting on exposed data, not generalization by itself.

```python
model = nn.Linear(3, 1, bias=False, dtype=torch.float64)
with torch.no_grad():
    model.weight.zero_()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
initial = ((model(x[train]) - y[train]) ** 2).mean().item()
curve = []
for _ in range(100):
    optimizer.zero_grad(set_to_none=True)
    loss = ((model(x[train]) - y[train]) ** 2).mean()
    curve.append(loss.item())
    loss.backward()
    optimizer.step()
assert len(curve) == 100 and np.isfinite(curve).all() and curve[-1] < initial
expected_weight = torch.tensor([[2.0, -1.0, 1.0]], dtype=torch.float64) * (1 - 0.95**100)
torch.testing.assert_close(model.weight, expected_weight, atol=1e-12, rtol=0)
np.testing.assert_allclose([curve[0], curve[-1]], [1.5, 1.5 * 0.95**198], atol=1e-12, rtol=0)
```

**Expected:** 100 finite updates; training loss decreases.

**Verify:** Compare the computed values or written argument with 100 finite updates; training loss decreases.

## Exercise 4: Open the holdout after fitting

The question is: Calculate final training and holdout MSE without updates.

The score is specific to two authored holdout rows. Do not tune the learning rate after this observation and still call the same data untouched.

```python
model.eval()
with torch.no_grad():
    train_error = ((model(x[train]) - y[train]) ** 2).mean().item()
    test_error = ((model(x[test]) - y[test]) ** 2).mean().item()
assert np.isfinite([train_error, test_error]).all() and test_error < baseline.item()
np.testing.assert_allclose(
    [train_error, test_error], [1.5 * 0.95**200, 10 * 0.95**200], atol=1e-12, rtol=0
)
```

**Expected:** finite errors; holdout error below 7.25on this fixture.

**Verify:** Compare the computed values or written argument with finite errors; holdout error below 7.25on this fixture.

## Exercise 5: Retain an independent pilot oracle

The question is: Calculate the scalar first update directly from NumPy without using the module.

The pilot protects the update mechanism independently of the feature model. A low final error could otherwise conceal a compensating implementation mistake.

```python
pilot = np.array([1.0, 2.0, 3.0])
gradient = 2 * np.mean((-2 * pilot) * pilot)
updated = -0.1 * gradient
np.testing.assert_allclose(
    [updated, np.mean((updated * pilot - 2 * pilot) ** 2)], [28 / 15, 56 / 675], atol=1e-12, rtol=0
)
```

**Expected:** w28/15and loss \(\frac{56}{675}\).

**Verify:** Compare the computed values or written argument with w28/15and loss \(\frac{56}{675}\).

## Exercise 6: Write the bounded evidence report

The question is: Record split IDs, 100 steps, errors and the two-row limitation.

The report should let a reviewer distinguish local software evidence from statistical reliability. A small successful fixture is a beginning, not a deployment certificate.

```python
report = {
    "train_ids": train,
    "test_ids": test,
    "steps": 100,
    "train_mse": train_error,
    "test_mse": test_error,
    "limit": "two synthetic holdout rows",
}
assert not set(train) & set(test) and len(report["test_ids"]) == 2 and report["steps"] == 100
```

**Expected:** disjoint IDs; holdout count 2; explicit limited scope.

**Verify:** Compare the computed values or written argument with disjoint IDs; holdout count 2; explicit limited scope.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
