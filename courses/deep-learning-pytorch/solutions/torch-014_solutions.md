# torch-014: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Multiclass classification chooses exactly one outcome among mutually exclusive classes. Multilabel classification makes several independent binary decisions, so multiple labels can be present. A final layer with three outputs can serve either task; the target meaning determines the loss. PyTorch CrossEntropyLoss expects raw class logits and class-index targets by default. It includes log-softmax internally, so applying softmax first changes the intended calculation.

The class axis convention matters. For ordinary batches, logits have shape(N, C) and targets(N). For spatial tasks, the class axis remains dimension 1, unlike many channels-last examples in other frameworks. Multilabel BCEWithLogitsLoss instead expects a target matrix matching the logits. Report which axes are averaged before comparing losses with different output widths.

**Multiclass target:** One class identity among mutually exclusive alternatives.

**Multilabel target:** A binary presence value for each independently meaningful label.

**Class axis:** The dimension indexing alternative categories in a logit tensor.

## Reading the implementation

Use F.cross_entropy with long integer class indices and floating logits. Sparse target indices must satisfy \(0\le \mathrm{target}<C\). For independent labels, use floating 0/1 targets with F.binary_cross_entropy_with_logits. `softmax(dim=1)` creates a class distribution for reporting. A uniform three-class logit vector gives loss log 3, while three independent binary logits at zero each give probability 0.5.

## Derive the class competition and its tensor contract

For a single multiclass record with logits z_0..z_(C-1), softmax assigns \(p_c=\frac{e^{z_c}}{\sum_j e^{z_j}}\). The indexed-target loss is`logsumexp(z)-z_y`. It compares the observed class with all alternatives through one shared normalization. Adding the same constant to every logit leaves the probabilities and loss unchanged, which is why a numerically stable implementation can subtract a row maximum.

At three zero logits and target class 1, p=[\(\frac{1}{3}\), \(\frac{1}{3}\), \(\frac{1}{3}\)] and loss=log 3. The gradient with respect to the three logits is[\(\frac{1}{3}\), \(\frac{-2}{3}\), \(\frac{1}{3}\)] before a batch reduction. The components sum to zero because raising every score equally cannot change class competition. This provides a derivative interpretation beyond the forward scalar.

PyTorch's indexed-target shapes are:

| Task | Logits | Integer target | Class axis |
| --- | --- | --- | --- |
| One record | (C, ) | scalar | The only logit axis |
| Ordinary batch | (N, C) | (N, ) | Dimension 1 |
| Spatial labels | (N, C, H, W) | (N, H, W) | Dimension 1 |
| Independent multilabel batch | (N, C) | Floating(N, C) | Each label is a binary event |

A sparse target index is a category identity, not a numeric value to regress. It must be a valid class index under the declared vocabulary. Probability-target forms instead match the logit shape and require a meaningful distribution across the class axis. The application should validate nonnegativity and normalization rather than assuming a floating tensor automatically supplies valid soft labels. The official API distinguishes these forms and their reductions. [PyTorch 2.9 CrossEntropyLoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.CrossEntropyLoss.html).

Applying softmax before CrossEntropyLoss feeds probabilities into an API that interprets them as logits and normalizes again. Uniform scores are a poor detector of this bug because any equal-valued score vector still produces a uniform distribution and losslog 3. A nonuniform fixture such as[2, 0, -2] exposes the changed confidence and objective. This is another reason to retain asymmetric, nonuniform examples alongside exact symmetric reference points.

Multilabel prediction has a different denominator and probability meaning. For two records and three binary labels, there are six binary events. Zero logits give each marginal probability 0.5, so the three probabilities in a row sum to 1.5 rather than one. That sum can represent an expected count of positive labels; it is not itself a probability of one mutually exclusive outcome. Shared features can still relate the labels, and independent binary losses do not automatically describe their full joint distribution.

Each zero-logit binary entry contributeslog 2. Summing all six gives 6 log2; the element mean giveslog 2; the mean across records of a sum across three labels gives 3 log2. All three are possible reductions, but they imply different objective and gradient scales. State whether the denominator counts records, labels, valid pixels or another participation unit.

Weights and ignored entries require another check. For class-index targets with class weights, PyTorch's weighted mean uses the participating target-class weights in its denominator, and ignore_index excludes designated targets from that participation. Do not transfer that exact formula automatically to soft-target cross entropy orpositive-weighted binary loss. A padded spatial or sequence target can otherwise change training scale while the displayed output tensor shape remains plausible.

For Keras comparisons, the default class-axis convention is often the last axis, whereas the PyTorch spatial categorical interface expects classes at dimension 1. Reorder axes and align target indexing explicitly; merely matching total element count can normalize across the wrong population or couple unrelated observations.

## Exercise 1: Calculate uniform multiclass loss

The question is: Use one row of three zero logits and target class 1.

Every class has probability one-third. The target index identifies a category, not a numeric magnitude to regress.

```python
logits = torch.zeros((1, 3), dtype=torch.float64)
target = torch.tensor([1], dtype=torch.long)
np.testing.assert_allclose(F.cross_entropy(logits, target).item(), np.log(3), atol=1e-12, rtol=0)
```

**Expected:** cross entropy log 3.

**Verify:** Compare the computed values or written argument with cross entropy log 3.

## Exercise 2: Contrast independent binary outputs

The question is: Apply sigmoid to the same three zero logits for a multilabel task.

Independent probabilities need not sum to one. A softmax would force labels to compete and change the task.

```python
independent = torch.sigmoid(logits)
assert independent.tolist() == [[0.5, 0.5, 0.5]] and independent.sum().item() == 1.5
```

**Expected:** probabilities.5, .5, .5 with sum 1.5.

**Verify:** Compare the computed values or written argument with probabilities.5, .5, .5 with sum 1.5.

## Exercise 3: Inspect target shapes and types

The question is: Create class indices 2, 0 and binary rows[1, 0, 1], [0, 1, 0].

The target contracts differ because the prediction events differ. Reshaping or casting without understanding those events can make a wrong task appear accepted.

```python
classes = torch.tensor([2, 0], dtype=torch.long)
labels = torch.tensor([[1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
assert (
    tuple(classes.shape) == (2,)
    and tuple(labels.shape) == (2, 3)
    and classes.dtype == torch.long
    and labels.is_floating_point()
)
```

**Expected:** shapes(2, ) and(2, 3); long versus floating.

**Verify:** Compare the computed values or written argument with shapes(2, ) and(2, 3); long versus floating.

## Exercise 4: Check class-axis normalization

The question is: Apply `softmax(dim=1)` to a 2-by-3 matrix.

Normalizing over the batch axis would couple unrelated observations. Row mass is a direct axis check.

```python
scores = torch.tensor([[2.0, 0.0, -2.0], [0.0, 1.0, 3.0]])
probs = torch.softmax(scores, dim=1)
torch.testing.assert_close(probs.sum(1), torch.ones(2), atol=1e-6, rtol=0)
```

**Expected:** each row sums 1.

**Verify:** Compare the computed values or written argument with each row sums 1.

## Exercise 5: Name the multilabel denominator

The question is: Compute BCE over two rows and three labels of zero logits.

There are six binary events but two records. A mean per record of summed label loss would differ by a factor of three.

```python
per_entry = F.binary_cross_entropy_with_logits(torch.zeros_like(labels), labels, reduction="none")
np.testing.assert_allclose(
    [per_entry.sum().item(), per_entry.mean().item()], [6 * np.log(2), np.log(2)], atol=1e-6, rtol=0
)
```

**Expected:** sum 6 log2; mean log 2.

**Verify:** Compare the computed values or written argument with sum 6 log2; mean log 2.

## Exercise 6: Reject an out-of-vocabulary class

The question is: Use class index 3 for a three-class row.

Class indices are bounded by the output vocabulary. Validation at the data boundary gives a clearer diagnostic before loss calculation.

```python
try:
    F.cross_entropy(torch.zeros((1, 3)), torch.tensor([3]))
except (IndexError, RuntimeError):
    pass
else:
    raise AssertionError("unknown class accepted")
```

**Expected:** IndexError or RuntimeError identifying an invalid target.

**Verify:** Compare the computed values or written argument with IndexError or RuntimeError identifying an invalid target.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
