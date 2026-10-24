# llm-026: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A representation probe asks whether a label can be predicted from a frozen representation. It does not prove that the original model used that information causally when making its own decisions. A probe can exploit accidental correlations, document identity or label leakage. Freeze the representation, split by independent document families and compare with a shuffled-label control. The synthetic fixture here makes the first coordinate equal to a simple label sign so linear separability can be checked exactly. That deliberate construction is a teaching example, not evidence about a pretrained language model. Causal claims would require interventions on the feature and an appropriate behavioral outcome.

**Probe:** A supervised readout trained or evaluated on a representation.

**Frozen representation:** Features held fixed while the readout is investigated.

**Causal use:** A feature influencing a decision under an appropriate intervention.

## Reading the implementation

Create frozen torch tensors and fit or derive a small linear probe separately from the encoder. Never backpropagate the probe objective into the frozen representation. Compare predicted labels on held-out identities, not the same rows used to choose the threshold. Shuffling labels changes the association while retaining the feature distribution. Record counts and split units beside both scores.

## Exercise 1: Construct transparent representations

The question is: Use features[-2,0],[-1,1],[1,0],[2,1] and labels 0,0,1,1.

The label is deliberately encoded in a coordinate. This supplies a clear positive control for the probing procedure.

```python
features=torch.tensor([[-2.,0.],[-1.,1.],[1.,0.],[2.,1.]]); labels=torch.tensor([0,0,1,1]); prediction=(features[:,0]>0).long()
assert torch.equal(prediction,labels)
```

**Expected:** first-coordinate sign predicts all four labels.

**Verify:** Compare the computed values or written argument with first-coordinate sign predicts all four labels.

## Exercise 2: Use a held-out fixture

The question is: Evaluate the same fixed threshold on new representations[-3,1],[3,0].

The threshold is fixed before opening these two rows. The result has only two held-out units and should be reported with that count.

```python
held=torch.tensor([[-3.,1.],[3.,0.]]); truth=torch.tensor([0,1]); got=(held[:,0]>0).long()
assert torch.equal(got,truth)
```

**Expected:** two correct held-out predictions.

**Verify:** Compare the computed values or written argument with two correct held-out predictions.

## Exercise 3: Add shuffled-label control

The question is: Compare predictions against shuffled labels 0,1,0,1.

The control breaks the specific association while preserving label balance. A high control score would suggest the probe or split can exploit another shortcut.

```python
shuffled=torch.tensor([0,1,0,1]); assert int((prediction==shuffled).sum())==2
```

**Expected:** 2 of4 correct.

**Verify:** Compare the computed values or written argument with 2 of4 correct.

## Exercise 4: Protect frozen state

The question is: Clone features, compute a probe loss using a separate trainable weight, and inspect gradients.

A readout investigation should not alter the representation under study. Fine-tuning the encoder answers a different question about learnability.

```python
before=features.clone(); weight=nn.Parameter(torch.tensor([[1.],[0.]])); logits=(features@weight).ravel(); loss=F.binary_cross_entropy_with_logits(logits,labels.float()); loss.backward()
assert weight.grad is not None and features.grad is None and torch.equal(features,before)
```

**Expected:** probe gradient exists; features have no gradient.

**Verify:** Compare the computed values or written argument with probe gradient exists; features have no gradient.

## Exercise 5: Expose family leakage

The question is: Mark rows0 and 1 as versions of familyA and place them on opposite sides of a split.

A probe can memorize family-specific features. Row-level disjointness does not prevent related documents from leaking across evaluation.

```python
families=['A','A','B','C']; assert {families[0]} & {families[1]}=={'A'}
```

**Expected:** familyA crosses partitions.

**Verify:** Compare the computed values or written argument with familyA crosses partitions.

## Exercise 6: Bound the interpretation

The question is: Write a result with heldout_count2,control_accuracy.5 and causal_use_establishedFalse.

Even perfect decoding does not show that the original system consulted that coordinate. The interpretation must match what the probe actually measured.

```python
report={'heldout_count':2,'control_accuracy':.5,'decodable':True,'causal_use_established':False}
assert report['decodable'] and not report['causal_use_established']
```

**Expected:** report distinguishes decodability from causal use.

**Verify:** Compare the computed values or written argument with report distinguishes decodability from causal use.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
