# torch-018: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Normalization can introduce both state and cross-observation dependencies. BatchNorm uses batch statistics during training and updates running statistics for later inference. LayerNorm normalizes feature values within each record and does not mix unrelated batch rows. PyTorch BatchNorm momentum specifies the weight of the new batch statistic, whereas Keras momentum specifies the retention weight of the old statistic. Equal numeric momentum arguments therefore usually mean different updates.

PyTorch BatchNorm also distinguishes the variance estimate used for training normalization from the unbiased estimate used in the running-variance update. A comparison must name both. The fixture uses a batch with mean 2, 4 and momentum.5 to check running mean 1, 2 from zero. Evaluation must leave running state unchanged. Tokenwise LayerNorm is checked with a future-row perturbation to expose wrong-axis leakage.

**Running statistic:** Persistent state updated from training batches.

**Momentum convention:** Which coefficient weights the old versus new statistic.

**Batch coupling:** One observation influencing another through shared statistics.

**LayerNorm axis:** The feature dimensions normalized within one observation.

## Reading the implementation

nn.BatchNorm1d(2, momentum=.5) treats columns as features for an(N, C)input. train mode updates running_mean and running_var; eval mode uses stored state. nn.LayerNorm(2) reduces the last two-feature dimension independently for each row. Its default epsilon and affine parameters are part of the comparison. Track num_batches_tracked as a buffer, separate from trainable weight and bias.

## Trace normalization axes, state and derivatives

For each normalization group, define mean mu, population variance v and centered values c=x-mu. The internal normalized values are z=c/sqrt(v+epsilon); a learned scale gamma and offset beta then give y=gamma*z+beta. The grouping determines which other values can affect an output. The final tensor shape alone does not reveal that dependency.

| Layer and input | Statistics reduce over | Retained group identity | Affine parameter shape |
| --- | --- | --- | --- |
| BatchNorm1d on [N, C] | N | Channel C | [C] |
| BatchNorm1d on [N, C, L] | N and L | Channel C | [C] |
| BatchNorm2d on [N, C, H, W] | N, H, W | Channel C | [C] |
| LayerNorm(D) on [N, T, D] | D | Each [N, T] token | [D] |
| LayerNorm((T, D)) on [N, T, D] | T, D | Each N record | [T, D] |

The last two rows are different models. The first LayerNorm preserves token independence in its normalization statistics; the second lets future tokens affect earlier ones. On a channels-first image, LayerNorm(C) would act on the final axis only if that axis happens to have size C; it does not automatically interpret the second axis as channels. Reorder axes or choose the intended normalized_shape explicitly.

In the supplied BatchNorm fixture, columns[1, 3] and[3, 5] have means[2, 4]. Each centered column is[-1, 1]. Dividing the squared-deviation sum two by sample count two gives population variance one. Dividing by count minus one gives the unbiased estimate two. PyTorch uses the first estimate for training normalization and the second for updating running variance. Its momentum weights the new statistic. With default tracked statistics, eval uses stored state; setting track_running_stats=False changes that contract. [PyTorch 2.9 BatchNorm1d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BatchNorm1d.html).

With momentum 0.5, initial running mean zero and initial running variance one, the first update gives mean[1, 2] and variance[1.5, 1.5]. During that training call, however, the outputs use the current batch mean[2, 4] and population variance[1, 1], not those newly stored values. With initial gamma=1, beta=0, they are[[-1, -1], [1, 1]] divided by sqrt(1+epsilon). Calling eval afterward on the original batch instead gives[[0, 1], [2, 3]] divided by sqrt(1.5+epsilon). A changed output therefore does not require a changed trainable weight.

For a scalar fixed batch mean b, PyTorch momentum a gives r_t=(1-a)r_(t-1)+a*b. Starting from zero, the solution is r_t=(1-(1-a)^t)*b. With a=0.2 and b=[2, 4], the first two means are[0.4, 0.8] and[0.72, 1.44]. Keras expresses the same mean recurrence using retention momentum m=0.8. If both APIs instead receive 0.2, their first means differ: PyTorch gives[0.4, 0.8] while Keras gives[1.6, 3.2]. The original 0.5 fixture hides this difference because a and 1-a coincide.

Mean-recursion matching still leaves variance state unmatched. The paired TensorFlow chapter's explicit two-row probe[0, 4] has population variance four and checks Keras moving variance 0.5*1+0.5*4=2.5. Its unbiased sample variance is eight, so the corresponding PyTorch running update would be 0.5*1+0.5*8=4.5. These are predictions from the named rules, not evidence that one should transplant a variance buffer between frameworks. The paired chapter contains the Keras execution contract, and this chapter's executable checks independently establish PyTorch's1.5 update on its own fixture. Epsilon and affine defaults must also be aligned before comparing outputs.

A useful geometric view is that centering removes the constant direction inside each group. For one LayerNorm group with d features, write g_i=dL/dz_i after incorporating any affine scale into the upstream gradient. Let s=sqrt(v+epsilon). Differentiating both the mean and variance gives

`dL/dx_i = (g_i - mean(g) - z_i*mean(g*z)) / s`.

This expression explains the dependency: an upstream derivative at one feature contributes to the means that influence other features in the same group. Summing the input derivatives gives zero, up to arithmetic error, because shifting all features by a common constant leaves the normalized values unchanged. The familiar exact removal of the radial direction is softened when epsilon is nonzero. Do not drop epsilon from a derivative calculation while retaining it in the forward pass.

For row[1, 3], mu=2, v=1 and z=[-1, 1]/sqrt(1+epsilon). Appending a separate row[100, 200] does not change this row under LayerNorm(2), since it belongs to a different group. Changing one of the first row's own features does affect both normalized outputs. LayerNorm computes its current input statistics in both train and eval modes and uses a biased variance estimate; its learned affine values can change the final output mean and variance. [PyTorch 2.9 LayerNorm](https://docs.pytorch.org/docs/2.9/generated/torch.nn.LayerNorm.html).

State freezing requires three independent questions. Are affine parameters receiving gradients? Can an optimizer update them? Can the layer mutate running buffers? Setting PyTorch BatchNorm weight and bias requires_grad=False addresses the first question, not the third. A train-mode call can still change running_mean, running_var and num_batches_tracked. Conversely eval can use fixed buffers while gradients still flow through affine parameters or inputs. These controls matter during transfer learning and sensitivity analysis.

Keras BatchNorm has a specific documented behavior: trainable=False selects inference behavior even for a direct call with training=True. The paired TensorFlow guide tests that rule. It is not a general equivalence between Keras trainable and PyTorch requires_grad, and it is not a claim about every Keras layer. Compiled Keras workflows also have their own recompilation rule after trainability changes. [Keras BatchNormalization](https://keras.io/api/layers/normalization_layers/batch_normalization/).

Small-batch and sequential applications need an additional assumption check. A single [1, C] training batch has no second observation per channel for the ordinary BatchNorm training contract; the lesson's singleton call deliberately occurs in eval after state exists. For [N, C, L], statistics include L, so using a whole sequence can couple future and past positions. A causal attention mask cannot undo that normalization dependency. State initialization, batch composition, last-batch policy and sequence layout therefore belong in the model contract, not only in a loader implementation detail.

## Exercise 1: Update a running mean

The question is: Apply BatchNorm momentum.5 to rows 1, 3 and 3, 5.

The batch mean is 2, 4 and the new-statistic weight is.5. The result is not yet the full batch mean.

```python
bn=nn.BatchNorm1d(2,momentum=.5); x=torch.tensor([[1.,3.],[3.,5.]])
bn.train(); bn(x)
torch.testing.assert_close(bn.running_mean,torch.tensor([1.,2.]),atol=1e-6,rtol=0); assert bn.num_batches_tracked.item()==1
```

**Expected:** running mean 1, 2; batch counter 1.

**Verify:** Compare the computed values or written argument with running mean 1, 2; batch counter 1.

## Exercise 2: Freeze state during evaluation

The question is: Call the trained layer in eval mode on 100, 200.

Evaluation must not adapt to assessment batch composition. A forgotten eval call can mutate state and change predictions based on neighboring records.

```python
before=bn.running_mean.clone(); count=bn.num_batches_tracked.clone(); bn.eval(); bn(torch.tensor([[100.,200.]]))
assert torch.equal(before,bn.running_mean) and torch.equal(count,bn.num_batches_tracked)
```

**Expected:** running mean and batch counter unchanged.

**Verify:** Compare the computed values or written argument with running mean and batch counter unchanged.

## Exercise 3: Check LayerNorm row independence

The question is: Normalize 1, 3alone and beside 100, 200.

LayerNorm uses only the current row's features in this configuration. A sequence-wide or batch-wide reduction would fail the perturbation test.

```python
ln=nn.LayerNorm(2); alone=ln(torch.tensor([[1.,3.]])); together=ln(torch.tensor([[1.,3.],[100.,200.]]))
torch.testing.assert_close(alone[0],together[0],atol=1e-6,rtol=0)
```

**Expected:** first row matches within 1e-6.

**Verify:** Compare the computed values or written argument with first row matches within 1e-6.

## Exercise 4: Inspect running variance convention

The question is: From initial running variance 1, use batch values 1, 3whose unbiased variance is 2 and momentum.5.

Forward training normalization uses a biased variance estimate, but the running variance update uses an unbiased one. Comparing only the layer title would miss this detail.

```python
torch.testing.assert_close(bn.running_var,torch.tensor([1.5,1.5]),atol=1e-6,rtol=0)
assert x.var(0,correction=0).tolist()==[1.,1.] and x.var(0,correction=1).tolist()==[2.,2.]
```

**Expected:** running variance 1.5 for each feature.

**Verify:** Compare the computed values or written argument with running variance 1.5 for each feature.

## Exercise 5: Translate momentum explicitly

The question is: Compute updates with old mean 0, batch mean 10 and PyTorch momentum.1versus Keras momentum.1.

To match a PyTorch new-statistic coefficient.1, the Keras old-statistic retention coefficient would be.9. Equal argument names are not enough evidence of equivalence.

```python
old,batch=0.,10.; torch_update=(1-.1)*old+.1*batch; keras_update=.1*old+(1-.1)*batch
assert torch_update==1 and keras_update==9
```

**Expected:** PyTorch 1; Keras 9 under their respective conventions.

**Verify:** Compare the computed values or written argument with PyTorch 1; Keras 9 under their respective conventions.

## Exercise 6: Handle a constant feature row

The question is: Apply LayerNorm to 5, 5 and inspect finiteness.

Epsilon avoids division by zero and the centered numerator is zero. Learned affine offsets would need to be included in a general expected value.

```python
constant=ln(torch.tensor([[5.,5.]])); assert torch.isfinite(constant).all()
torch.testing.assert_close(constant,torch.zeros((1,2)),atol=1e-6,rtol=0)
```

**Expected:** finite zeros with default affine initialization.

**Verify:** Compare the computed values or written argument with finite zeros with default affine initialization.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
