# llm-017: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Training predicts the next token at each active position. A four-token sequence gives three input-target pairs, and padding creates storage slots without creating observations. Cross entropy can ignore a sentinel target such as-100, but the denominator must still count only active targets. Summing losses and dividing by padded width understates error when sequences are short. The vocabulary dimension belongs to logits, while labels are integer class indices. This lesson uses zero logits so each active target has exactly \(\log(\mathrm{vocabulary\ size})\) loss, making padding and reduction errors visible without a trained model.

**Active target:** A real next-token observation included in the objective.

**Ignore index:** A sentinel label excluded from loss calculation.

**Loss denominator:** The count of participating prediction events.

## Reading the implementation

ids[:, :-1] and ids[:, 1:] produce shifted input and target tensors. F.cross_entropy expects classes on dimension 1, so flatten(batch, time, vocabulary) logits to (-1, vocabulary) and labels to (-1). With ignore_index=-100, ignored targets contribute no loss. reduction='sum' followed by an explicit active count makes the denominator auditable.

## Exercise 1: Shift the sequence

The question is: Use IDs [2, 5, 7, 3] and create three input-target pairs.

The model may see the current input token but not its target at the next position. The diagonal causal mask is consistent with this shifted objective.

```python
ids = torch.tensor([[2, 5, 7, 3]])
inputs = ids[:, :-1]
targets = ids[:, 1:]
assert inputs.tolist() == [[2, 5, 7]] and targets.tolist() == [[5, 7, 3]]
```

**Expected:** inputs 2, 5, 7 and targets 5, 7, 3.

**Verify:** In a fresh process, the exercise checks confirm `inputs.tolist() == [[2, 5, 7]]` and `targets.tolist() == [[5, 7, 3]]`.

## Exercise 2: Score uniform logits

The question is: Use zero logits with vocabulary 8 for the three targets.

Each target has probability one eighth. Target identity does not change the loss under this uniform distribution, which isolates the denominator calculation.

```python
logits = torch.zeros((1, 3, 8))
loss = F.cross_entropy(logits.reshape(-1, 8), targets.reshape(-1))
np.testing.assert_allclose(loss.item(), np.log(8), atol=1e-6, rtol=0)
```

**Expected:** mean loss \(\log 8\) and count 3.

**Verify:** In a fresh process, the exercise checks confirm `loss.item()` matches `np.log(8)` within 1e-6.

## Exercise 3: Append ignored targets

The question is: Add two labels of -100 and corresponding zero-logit positions.

Additional storage positions do not add evidence. This invariance is a strong test for a masked language-model objective.

```python
padded = torch.tensor([[5, 7, 3, -100, -100]])
plogits = torch.zeros((1, 5, 8))
new = F.cross_entropy(plogits.reshape(-1, 8), padded.reshape(-1), ignore_index=-100)
assert int((padded != -100).sum()) == 3
torch.testing.assert_close(new, loss, atol=1e-6, rtol=0)
```

**Expected:** mean loss unchanged; active count 3.

**Verify:** In a fresh process, the exercise checks confirm `int((padded != -100).sum()) == 3` and `new` matches `loss` within 1e-6.

## Exercise 4: Expose the wrong denominator

The question is: Compute summed active loss and divide by padded length 5 instead of active count 3.

The wrong score appears better merely because more padding was added. It is not a model improvement.

```python
summed = F.cross_entropy(
    plogits.reshape(-1, 8), padded.reshape(-1), ignore_index=-100, reduction="sum"
)
wrong = summed / 5
np.testing.assert_allclose(wrong.item(), 3 * np.log(8) / 5, atol=1e-6, rtol=0)
assert wrong < loss
```

**Expected:** wrong loss \(3\log 8/5\), below the correct loss.

**Verify:** In a fresh process, the exercise checks confirm `wrong.item()` matches `3 * np.log(8) / 5` within 1e-6 and `wrong < loss`.

## Exercise 5: Check gradient masking

The question is: Differentiate summed loss and inspect gradient rows at ignored positions.

Masking must affect the objective and its derivative. A post-hoc reporting adjustment would not prevent padded targets from influencing training.

```python
v = plogits.clone().requires_grad_()
objective = F.cross_entropy(
    v.reshape(-1, 8), padded.reshape(-1), ignore_index=-100, reduction="sum"
)
objective.backward()
assert torch.count_nonzero(v.grad[:, 3:]).item() == 0
```

**Expected:** ignored-position gradients exactly zero.

**Verify:** In a fresh process, the exercise checks confirm `torch.count_nonzero(v.grad[:, 3:]).item() == 0`.

## Exercise 6: Reject all-padding batches

The question is: Check active count before a mean loss on targets [-100, -100].

A mean over no observations is undefined. Returning a perfect zero loss would let a broken batching pipeline masquerade as successful learning.

```python
empty = torch.tensor([[-100, -100]])
active = int((empty != -100).sum())
assert active == 0
try:
    if active == 0:
        raise ValueError("no active targets")
except ValueError:
    pass
```

**Expected:** zero active count triggers an explicit failure policy.

**Verify:** In a fresh process, the exercise checks confirm `active == 0` and `active != 0`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
