# llm-033: explanatory solutions

Read these preference objectives and what they do not prove answers after attempting *Compute a margin from log probabilities* through *Limit the claim*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Reverse the labels* points to one step. `llm-033_solution.py` holds the assertions; this page explains how they test preference pair. Then try *Limit the claim* on a fresh input you chose before looking.

## Mechanism review

A preference objective compares two responses under a chosen and rejected label. A DPO-style margin subtracts the reference-policy log-probability difference from the current-policy difference, then scales by beta. A logistic loss rewards a positive margin for the chosen response. Equal margins give log 2 loss. Reversing labels reverses the margin. These labels express a preference under a collection process; they do not automatically encode truth, harmlessness or universal user agreement. This worksheet calculates a fixed offline objective and does not run reinforcement learning, call a reward service or train a production model.

**Preference pair:** Two candidate responses labelled chosen and rejected.

**Reference policy:** A fixed comparison distribution in the objective.

**Preference margin:** The adjusted log-probability advantage of the chosen response.

## Reading the implementation

Let margin=beta*((policy_chosen-policy_rejected)-(reference_chosen-reference_rejected)). The negative log sigmoid equals logaddexp(0, -margin), which is stable for large magnitudes. Log probabilities are sequence scores under a declared tokenization and length policy. Keep those conventions fixed when comparing pairs, because length changes can affect sequence log probability.

## Exercise 1: Compute a margin from log probabilities

The question is: Use policy log probabilities -1 (chosen) and -4 (rejected), reference -2 and -3, and beta 0.25.

The policy prefers the chosen answer by 3 while the reference prefers it by 1, so the relative preference is 2 before scaling by beta. Any positive margin gives a loss below the zero-margin value \(\log 2\).

```python
margin2 = 0.25 * ((-1 - (-4)) - (-2 - (-3)))
loss2 = np.logaddexp(0, -margin2)
assert margin2 == 0.5
np.testing.assert_allclose(loss2, np.log1p(np.exp(-0.5)), atol=1e-12, rtol=0)
assert loss2 < np.log(2)
```

**Expected:** margin 0.5; loss \(\log(1+e^{-0.5})\approx 0.474\), below \(\log 2\).

**Verify:** For *Compute a margin from log probabilities*, a fresh-process check confirms `margin2 == 0.5`, `loss2` matches `np.log1p(np.exp(-0.5))` within 1e-12 and `loss2 < np.log(2)`.

## Exercise 2: Predict the effect of beta

The question is: Keep the same log probabilities and raise beta to 1. Predict the margin and whether the loss rises or falls.

Beta scales the same relative preference, so a larger beta makes a positive margin look more decisive and lowers the loss. It also makes a negative margin more costly.

```python
margin3 = 1.0 * ((-1 - (-4)) - (-2 - (-3)))
loss3 = np.logaddexp(0, -margin3)
assert margin3 == 2
np.testing.assert_allclose(loss3, np.log1p(np.exp(-2)), atol=1e-12, rtol=0)
assert loss3 < loss2
```

**Expected:** margin 2; loss \(\log(1+e^{-2})\approx 0.127\), smaller than at beta 0.25.

**Verify:** For *Predict the effect of beta*, a fresh-process check confirms `margin3 == 2`, `loss3` matches `np.log1p(np.exp(-2))` within 1e-12 and `loss3 < loss2`.

## Exercise 3: Reverse the labels

The question is: Swap chosen and rejected while keeping their scores attached to the same response identities.

The sign must reverse because both policy and reference differences reverse. Swapping only one side would calculate a different and inconsistent objective.

```python
reversed_margin = -margin
reversed_loss = np.logaddexp(0, -reversed_margin)
assert reversed_margin == -1 and reversed_loss > loss
```

**Expected:** margin -1 and larger loss.

**Verify:** For *Reverse the labels*, a fresh-process check confirms `reversed_margin == -1` and `reversed_loss > loss`.

## Exercise 4: Check numeric stability

The question is: Evaluate margins 1000 and -1000 with logaddexp.

A naive `log(sigmoid())` calculation may underflow at extreme margins. The stable form computes the same objective without an unnecessary probability round trip.

```python
values = np.logaddexp(0, -np.array([1000.0, -1000.0]))
assert np.isfinite(values).all()
np.testing.assert_allclose(values, [0, 1000], atol=1e-12, rtol=0)
```

**Expected:** finite losses approximately 0 and 1000.

**Verify:** For *Check numeric stability*, a fresh-process check confirms `np.isfinite(values).all()` and `values` matches `[0, 1000]` within 1e-12.

## Exercise 5: Track pair identity

The question is: Store response IDs r1, r2 and a preference label; reverse the label while retaining both identities.

Keeping scores keyed by response identity prevents an array-order error from changing which text a probability belongs to.

```python
scores = {"r1": -2.0, "r2": -4.0}
pair = {"chosen": "r1", "rejected": "r2"}
flipped = {"chosen": pair["rejected"], "rejected": pair["chosen"]}
assert flipped["chosen"] == "r2" and scores["r1"] == -2
```

**Expected:** chosen identity changes to r2; scores remain keyed by ID.

**Verify:** For *Track pair identity*, a fresh-process check confirms `flipped['chosen'] == 'r2'` and `scores['r1'] == -2`.

## Exercise 6: Limit the claim

The question is: Record that a preferred response may still contain a false factual statement.

An objective can faithfully optimize noisy or incomplete labels. Reliability claims require separate evidence about the properties the labels do not establish.

```python
report = {"preference_agreement": True, "factuality_verified": False, "online_rl_executed": False}
assert not report["factuality_verified"] and not report["online_rl_executed"]
```

**Expected:** preference agreement True, factuality_verified False.

**Verify:** For *Limit the claim*, a fresh-process check confirms `not report['factuality_verified']` and `not report['online_rl_executed']`.

## Review after comparison

Change one input to *Check numeric stability* and predict the result first; keep *Track pair identity* failing beside the repair. Log a missing NumPy separately from a wrong preference pair value in `llm-033`.
