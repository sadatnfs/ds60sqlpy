# llm-031: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Instruction tuning changes which text patterns a model learns from, and the loss mask specifies which target events count. In an answer-only objective, prompt tokens provide context but are excluded from the supervised loss. The first answer token must still be predicted from the preceding context, so align the mask with shifted targets rather than unshifted input positions. A full-sequence objective instead asks the model to predict prompt text too. Neither convention is automatically correct for every task, but their losses have different denominators. Split evaluation by template family to avoid measuring memorized prompt forms as generalization.

**Instruction tuning:** Training on task prompts paired with desired responses.

**Answer-only mask:** A target participation rule excluding prompt prediction events.

**Template family:** Related prompt forms grouped for evaluation isolation.

## Reading the implementation

Use a sequence with two prompt tokens followed by three answer tokens. Shift to four targets, then mark only target positions belonging to the answer. Replace excluded labels with -100 before cross entropy. The mask applies to targets, not input padding alone. Verify gradients at ignored logit positions and count the three active answer targets explicitly.

## Exercise 1: Align the target mask

The question is: Use sequence [1, 2, 5, 6, 3], where 1, 2 are prompt and 5, 6, 3 answer.

The first answer token 5 is a target at position 1 in the shifted array. Masking by unshifted input positions would introduce an off-by-one error.

```python
sequence = torch.tensor([[1, 2, 5, 6, 3]])
targets = sequence[:, 1:]
answer = torch.tensor([[False, True, True, True]])
assert targets.tolist() == [[2, 5, 6, 3]] and int(answer.sum()) == 3
```

**Expected:** targets [2, 5, 6, 3]; mask [False, True, True, True].

**Verify:** In a fresh process, the exercise checks confirm `targets.tolist() == [[2, 5, 6, 3]]` and `int(answer.sum()) == 3`.

## Exercise 2: Compute answer-only loss

The question is: Use zero vocabulary 8 logits and replace prompt targets with -100.

Uniform logits make each target loss identical. The mean stays \(\log 8\), but the active count differs from full-sequence training and affects summed objectives.

```python
logits = torch.zeros((1, 4, 8))
masked = targets.masked_fill(~answer, -100)
loss = F.cross_entropy(logits.reshape(-1, 8), masked.reshape(-1), ignore_index=-100)
np.testing.assert_allclose(loss.item(), np.log(8), atol=1e-6, rtol=0)
```

**Expected:** 3 active targets; mean \(\log 8\).

**Verify:** In a fresh process, the exercise checks confirm `loss.item()` matches `np.log(8)` within 1e-6.

## Exercise 3: Compare loss sums

The question is: Calculate full-sequence and answer-only summed losses.

Comparing unlabelled totals would confuse different numbers of supervised events with different model quality. Report the denominator alongside any mean.

```python
full = F.cross_entropy(logits.reshape(-1, 8), targets.reshape(-1), reduction="sum")
answer_sum = F.cross_entropy(
    logits.reshape(-1, 8), masked.reshape(-1), ignore_index=-100, reduction="sum"
)
np.testing.assert_allclose(
    [full.item(), answer_sum.item()], [4 * np.log(8), 3 * np.log(8)], atol=1e-6, rtol=0
)
```

**Expected:** 4 log 8 versus 3 log 8.

**Verify:** In a fresh process, the exercise checks confirm `[full.item(), answer_sum.item()]` matches `[4 * np.log(8), 3 * np.log(8)]` within 1e-6.

## Exercise 4: Inspect ignored gradients

The question is: Backpropagate answer-only loss and examine the first logit position.

The prompt remains context for later predictions even though its own target event is ignored. Excluding its loss is not the same as removing prompt input tokens.

```python
v = logits.clone().requires_grad_()
F.cross_entropy(v.reshape(-1, 8), masked.reshape(-1), ignore_index=-100).backward()
assert (
    torch.count_nonzero(v.grad[:, 0]).item() == 0 and torch.count_nonzero(v.grad[:, 1:]).item() > 0
)
```

**Expected:** first-position gradient all zero; answer gradients nonzero.

**Verify:** In a fresh process, the exercise checks confirm `torch.count_nonzero(v.grad[:, 0]).item() == 0` and `torch.count_nonzero(v.grad[:, 1:]).item() > 0`.

## Exercise 5: Detect template leakage

The question is: Assign two paraphrased prompts to family T and split them across train/test.

Different surface wording can preserve the same task template. Grouped evaluation tests transfer beyond that family rather than rewarding memorization of a familiar form.

```python
family = {"p1": "T", "p2": "T"}
assert {family["p1"]} & {family["p2"]} == {"T"}
```

**Expected:** family intersection T.

**Verify:** In a fresh process, the exercise checks confirm `{family['p1']} & {family['p2']} == {'T'}`.

## Exercise 6: Refuse missing answers

The question is: Set an all-false answer mask and check the denominator before training.

A record with no supervised answer should not contribute an invented zero loss. Handle it as a data-quality failure or an explicitly excluded record.

```python
empty = torch.zeros((1, 4), dtype=torch.bool)
try:
    if int(empty.sum()) == 0:
        raise ValueError("answer targets required")
except ValueError:
    pass
else:
    raise AssertionError("empty answer accepted")
```

**Expected:** no active answer targets; explicit ValueError.

**Verify:** In a fresh process, the exercise checks confirm `int(empty.sum()) != 0`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
