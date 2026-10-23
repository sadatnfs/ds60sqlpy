# torch-018: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Normalization can introduce both state and cross-observation dependencies. BatchNorm uses batch statistics during training and updates running statistics for later inference. LayerNorm normalizes feature values within each record and does not mix unrelated batch rows. PyTorch BatchNorm momentum specifies the weight of the new batch statistic, whereas Keras momentum specifies the retention weight of the old statistic. Equal numeric momentum arguments therefore usually mean different updates.

PyTorch BatchNorm also distinguishes the variance estimate used for training normalization from the unbiased estimate used in the running-variance update. A comparison must name both. The fixture uses a batch with mean2, 4 and momentum.5 to check running mean1, 2 from zero. Evaluation must leave running state unchanged. Tokenwise LayerNorm is checked with a future-row perturbation to expose wrong-axis leakage.

**Running statistic:** Persistent state updated from training batches.

**Momentum convention:** Which coefficient weights the old versus new statistic.

**Batch coupling:** One observation influencing another through shared statistics.

**LayerNorm axis:** The feature dimensions normalized within one observation.

## Reading the implementation

nn.BatchNorm1 d(2, momentum=.5) treats columns as features for an(N, C)input. train mode updates running_mean and running_var; eval mode uses stored state. nn.LayerNorm(2) reduces the last two-feature dimension independently for each row. Its default epsilon and affine parameters are part of the comparison. Track num_batches_tracked as a buffer, separate from trainable weight and bias.

## Exercise 1: Update a running mean

The question is: Apply BatchNorm momentum.5 to rows1, 3 and3, 5.

The batch mean is2, 4 and the new-statistic weight is.5. The result is not yet the full batch mean.

```python
bn=nn.BatchNorm1d(2,momentum=.5); x=torch.tensor([[1.,3.],[3.,5.]])
bn.train(); bn(x)
torch.testing.assert_close(bn.running_mean,torch.tensor([1.,2.]),atol=1e-6,rtol=0); assert bn.num_batches_tracked.item()==1
```

**Expected:** running mean1, 2; batch counter1.

**Verify:** Compare the computed values or written argument with running mean1, 2; batch counter1.

## Exercise 2: Freeze state during evaluation

The question is: Call the trained layer in eval mode on100, 200.

Evaluation must not adapt to assessment batch composition. A forgotten eval call can mutate state and change predictions based on neighboring records.

```python
before=bn.running_mean.clone(); count=bn.num_batches_tracked.clone(); bn.eval(); bn(torch.tensor([[100.,200.]]))
assert torch.equal(before,bn.running_mean) and torch.equal(count,bn.num_batches_tracked)
```

**Expected:** running mean and batch counter unchanged.

**Verify:** Compare the computed values or written argument with running mean and batch counter unchanged.

## Exercise 3: Check LayerNorm row independence

The question is: Normalize1, 3 alone and beside100, 200.

LayerNorm uses only the current row's features in this configuration. A sequence-wide or batch-wide reduction would fail the perturbation test.

```python
ln=nn.LayerNorm(2); alone=ln(torch.tensor([[1.,3.]])); together=ln(torch.tensor([[1.,3.],[100.,200.]]))
torch.testing.assert_close(alone[0],together[0],atol=1e-6,rtol=0)
```

**Expected:** first row matches within1e-6.

**Verify:** Compare the computed values or written argument with first row matches within1e-6.

## Exercise 4: Inspect running variance convention

The question is: From initial running variance1, use batch values1, 3 whose unbiased variance is2 and momentum.5.

Forward training normalization uses a biased variance estimate, but the running variance update uses an unbiased one. Comparing only the layer title would miss this detail.

```python
torch.testing.assert_close(bn.running_var,torch.tensor([1.5,1.5]),atol=1e-6,rtol=0)
assert x.var(0,correction=0).tolist()==[1.,1.] and x.var(0,correction=1).tolist()==[2.,2.]
```

**Expected:** running variance1.5 for each feature.

**Verify:** Compare the computed values or written argument with running variance1.5 for each feature.

## Exercise 5: Translate momentum explicitly

The question is: Compute updates with old mean0, batch mean10 and PyTorch momentum.1 versus Keras momentum.1.

To match a PyTorch new-statistic coefficient.1, the Keras old-statistic retention coefficient would be.9. Equal argument names are not enough evidence of equivalence.

```python
old,batch=0.,10.; torch_update=(1-.1)*old+.1*batch; keras_update=.1*old+(1-.1)*batch
assert torch_update==1 and keras_update==9
```

**Expected:** PyTorch1; Keras9 under their respective conventions.

**Verify:** Compare the computed values or written argument with PyTorch1; Keras9 under their respective conventions.

## Exercise 6: Handle a constant feature row

The question is: Apply LayerNorm to5, 5 and inspect finiteness.

Epsilon avoid division by zero and the centered numerator is zero. Learned affine offsets would need to be included in a general expected value.

```python
constant=ln(torch.tensor([[5.,5.]])); assert torch.isfinite(constant).all()
torch.testing.assert_close(constant,torch.zeros((1,2)),atol=1e-6,rtol=0)
```

**Expected:** finite zeros with default affine initialization.

**Verify:** Compare the computed values or written argument with finite zeros with default affine initialization.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
