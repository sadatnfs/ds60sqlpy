# torch-014: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Multiclass classification chooses exactly one outcome among mutually exclusive classes. Multi label classification makes several independent binary decisions, so multiple labels can be present. A final layer with three outputs can serve either task; the target meaning determines the loss. PyTorch CrossEntropyLoss expects raw class logits and class-index targets by default. It includes log-softmax internally, so applying softmax first changes the intended calculation.

The class axis convention matters. For ordinary batches, logits have shape(N, C) and targets(N). For spatial tasks, the class axis remains dimension1, unlike many channels-last examples in other frameworks. Multi label BCEWithLogitsLoss instead expects a target matrix matching the logits. Report which axes are averaged before comparing losses with different output widths.

**Multiclass target:** One class identity among mutually exclusive alternatives.

**Multi label target:** A binary presence value for each independently meaningful label.

**Class axis:** The dimension indexing alternative categories in a logit tensor.

## Reading the implementation

UseF.cross_entropy with long integer class indices and floating logits. Sparse target indices must satisfy0<=target<C. For independent labels, use floating0/1 targets with F.binary_cross_entropy_with_logits. softmax(dim=1) creates a class distribution for reporting. A uniform three-class logit vector gives loss log3, while three independent binary logits at zero each give probability.5.

## Exercise 1: Calculate uniform multiclass loss

The question is: Use one row of three zero logits and target class1.

Every class has probability one-third. The target index identifies a category, not a numeric magnitude to regress.

```python
logits=torch.zeros((1,3),dtype=torch.float64); target=torch.tensor([1],dtype=torch.long)
np.testing.assert_allclose(F.cross_entropy(logits,target).item(),np.log(3),atol=1e-12,rtol=0)
```

**Expected:** cross entropy log3.

**Verify:** Compare the computed values or written argument with cross entropy log3.

## Exercise 2: Contrast independent binary outputs

The question is: Apply sigmoid to the same three zero logits for a multi label task.

Independent probabilities need not sum to one. A softmax would force labels to compete and change the task.

```python
independent=torch.sigmoid(logits)
assert independent.tolist()==[[.5,.5,.5]] and independent.sum().item()==1.5
```

**Expected:** probabilities.5, .5, .5 with sum1.5.

**Verify:** Compare the computed values or written argument with probabilities.5, .5, .5 with sum1.5.

## Exercise 3: Inspect target shapes and types

The question is: Create class indices2, 0 and binary rows[1, 0, 1], [0, 1, 0].

The target contracts differ because the prediction events differ. Reshaping or casting without understanding those events can make a wrong task appear accepted.

```python
classes=torch.tensor([2,0],dtype=torch.long); labels=torch.tensor([[1.,0.,1.],[0.,1.,0.]])
assert tuple(classes.shape)==(2,) and tuple(labels.shape)==(2,3) and classes.dtype==torch.long and labels.is_floating_point()
```

**Expected:** shapes(2, ) and(2, 3); long versus floating.

**Verify:** Compare the computed values or written argument with shapes(2, ) and(2, 3); long versus floating.

## Exercise 4: Check class-axis normalization

The question is: Apply softmax(dim1) to a2 x3 matrix.

Normalizing over the batch axis would couple unrelated observations. Row mass isa direct axis check.

```python
scores=torch.tensor([[2.,0.,-2.],[0.,1.,3.]])
probs=torch.softmax(scores,dim=1); torch.testing.assert_close(probs.sum(1),torch.ones(2),atol=1e-6,rtol=0)
```

**Expected:** each row sums1.

**Verify:** Compare the computed values or written argument with each row sums1.

## Exercise 5: Name the multi label denominator

The question is: Compute B C E over two rows and three labels of zero logits.

There are six binary events but two records. A mean per record of summed label loss would differ by a factor of three.

```python
per_entry=F.binary_cross_entropy_with_logits(torch.zeros_like(labels),labels,reduction='none')
np.testing.assert_allclose([per_entry.sum().item(),per_entry.mean().item()],[6*np.log(2),np.log(2)],atol=1e-6,rtol=0)
```

**Expected:** sum6 log2; mean log2.

**Verify:** Compare the computed values or written argument with sum6 log2; mean log2.

## Exercise 6: Reject an out-of-vocabulary class

The question is: Use class index3 for a three-class row.

Class indices are bounded by the output vocabulary. Validation at the data boundary gives a clearer diagnostic before loss calculation.

```python
try: F.cross_entropy(torch.zeros((1,3)),torch.tensor([3]))
except (IndexError,RuntimeError): pass
else: raise AssertionError('unknown class accepted')
```

**Expected:** IndexError or RuntimeError identifying an invalid target.

**Verify:** Compare the computed values or written argument with IndexError or RuntimeError identifying an invalid target.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
