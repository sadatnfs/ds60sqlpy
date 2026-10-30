# llm-033: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A preference objective compares two responses under a chosen and rejected label. A DPO-style margin subtracts the reference-policy log-probability difference from the current-policy difference, then scales by beta. A logistic loss rewards a positive margin for the chosen response. Equal margins give log2 loss. Reversing labels reverses the margin. These labels express a preference under a collection process; they do not automatically encode truth, harmlessness or universal user agreement. This worksheet calculates a fixed offline objective and does not run reinforcement learning, call a reward service or train a production model.

**Preference pair:** Two candidate responses labelled chosen and rejected.

**Reference policy:** A fixed comparison distribution in the objective.

**Preference margin:** The adjusted log-probability advantage of the chosen response.

## Reading the implementation

Let margin=beta*((policy_chosen-policy_rejected)-(reference_chosen-reference_rejected)). The negative log sigmoid equals logaddexp(0,-margin), which is stable for large magnitudes. Log probabilities are sequence scores under a declared tokenization and length policy. Keep those conventions fixed when comparing pairs, because length changes can affect sequence log probability.

## Exercise 1: Evaluate equal margins

The question is: Set both policy and reference chosen-minus-rejected differences to1 with beta.1.

Equal relative preferences cancel even though absolute sequence log probabilities differ. The objective compares a change in preference relative to the reference.

```python
margin = 0.1 * ((-2 - (-3)) - (-4 - (-5)))
loss = np.logaddexp(0, -margin)
assert margin == 0
np.testing.assert_allclose(loss, np.log(2), atol=1e-12, rtol=0)
```

**Expected:** margin0 and loss log 2.

**Verify:** Compare the computed values or written argument with margin0 and loss log 2.

## Exercise 2: Favor the chosen response

The question is: Use policy difference2,reference difference 0,beta.5.

A positive adjusted margin reduces the logistic loss. This expresses agreement with the supplied preference label, not independent correctness.

```python
margin = 0.5 * (2 - 0)
loss = np.logaddexp(0, -margin)
np.testing.assert_allclose(loss, np.log1p(np.exp(-1)), atol=1e-12, rtol=0)
```

**Expected:** margin1;loss \(\log(1+e^{-1})\).

**Verify:** Compare the computed values or written argument with margin1;loss \(\log(1+e^{-1})\).

## Exercise 3: Reverse the labels

The question is: Swap chosen and rejected while keeping their scores attached to the same response identities.

The sign must reverse because both policy and reference differences reverse. Swapping only one side would calculate a different and inconsistent objective.

```python
reversed_margin = -margin
reversed_loss = np.logaddexp(0, -reversed_margin)
assert reversed_margin == -1 and reversed_loss > loss
```

**Expected:** margin-1 and larger loss.

**Verify:** Compare the computed values or written argument with margin-1 and larger loss.

## Exercise 4: Check numeric stability

The question is: Evaluate margins1000 and-1000 withlogaddexp.

A naive `log(sigmoid())` calculation may underflow at extreme margins. The stable form computes the same objective without an unnecessary probability round trip.

```python
values = np.logaddexp(0, -np.array([1000.0, -1000.0]))
assert np.isfinite(values).all()
np.testing.assert_allclose(values, [0, 1000], atol=1e-12, rtol=0)
```

**Expected:** finite losses approximately0 and1000.

**Verify:** Compare the computed values or written argument with finite losses approximately0 and1000.

## Exercise 5: Track pair identity

The question is: Store response IDsr1,r2 and a preference label; reverse the label while retaining both identities.

Keeping scores keyed by response identity prevents an array-order error from changing which text a probability belongs to.

```python
scores = {"r1": -2.0, "r2": -4.0}
pair = {"chosen": "r1", "rejected": "r2"}
flipped = {"chosen": pair["rejected"], "rejected": pair["chosen"]}
assert flipped["chosen"] == "r2" and scores["r1"] == -2
```

**Expected:** chosen identity changes tor2; scores remain keyed by ID.

**Verify:** Compare the computed values or written argument with chosen identity changes tor2; scores remain keyed by ID.

## Exercise 6: Limit the claim

The question is: Record that a preferred response may still contain a false factual statement.

An objective can faithfully optimize noisy or incomplete labels. Reliability claims require separate evidence about the properties the labels do not establish.

```python
report = {"preference_agreement": True, "factuality_verified": False, "online_rl_executed": False}
assert not report["factuality_verified"] and not report["online_rl_executed"]
```

**Expected:** preference agreementTrue,factuality_verifiedFalse.

**Verify:** Compare the computed values or written argument with preference agreementTrue,factuality_verifiedFalse.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
