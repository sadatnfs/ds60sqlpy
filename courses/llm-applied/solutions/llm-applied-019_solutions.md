# llm-applied-019: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Preference optimization uses labels describing which of two responses is preferred. A DPO-style objective compares the policy chosen-versus-rejected log-probability advantage with the same advantage under a fixed reference policy, then applies a logistic loss scaled by beta. Equal adjusted margins give loss log 2. The objective can be differentiated directly from offline preference pairs without running an online reinforcement-learning environment.

RLHF is a broader family of workflows in which human feedback informs a reward or preference signal and a policy optimization procedure. A reward model and an online policy update introduce additional state, exploration and reward-hacking risks. This chapter performs a real scalar PyTorch update on a DPO-style preference margin and contrasts its evidence with an RLHF workflow. It does not claim to train a reward model, execute onlineRL, or establish factuality. A preferred answer can still be unsupported or wrong if the preference labels reward style over truth.

**Preference margin:** The policy advantage adjusted by a reference-policy advantage.

**DPO-style loss:** A logistic objective over offline chosen/rejected comparisons.

**Reference policy:** A fixed distribution anchoring the preference comparison.

**RLHF distinction:** Additional reward and policy-learning machinery beyond this offline loss.

## Reading the implementation

Represent the policy log-probability difference as a trainable scalar for the smallest diagnostic. The reference difference is fixed. Compute `margin=beta*(policy_difference-reference_difference)` and `loss=softplus(-margin)`. Backpropagate and apply one SGD update. Reversing chosen/rejected labels reverses the margin and gradient direction. Keep response identities attached to scores when forming pairs.

## Derive the DPO-style scalar update

Let d be the policy chosen-minus-rejected log-probability difference and r the same difference under a fixed reference. The adjusted margin is \(z=\beta\cdot (d-r)\), and the loss is \(\log(1+\exp(-z))\), implemented through softplus for numerical stability. Its derivative with respect to d is \(-\beta\operatorname{sigmoid}(-z)\). The second derivative is \({\beta}^{2}\cdot \sigma(z)\cdot \sigma(-z)\), nonnegative, so this scalar loss is convex in d for a fixed reference.

At \(d=r=0\) and beta 0.5, the loss is log2, about0.693147. The derivative is-0.5*0.5=-0.25, and the curvature is 0.25*0.25=0.0625. SGD with learning rate 0.2 moves d to0-0.2*(-0.25)=0.05. The new adjusted margin is 0.025 and the loss is about0.680725. This is an actual scalar gradient update in the reference.

A positive step increases the chosen-response advantage relative to the reference, but it does not uniquely specify the two response probabilities. Many pairs of chosen/rejected log probabilities can have the same difference. The fixture optimizes a free scalar and does not implement a vocabulary softmax, sequence model, KL measurement or normalized policy distribution. Calling it DPO-style margin mechanics preserves that distinction.

In a language model, a response log probability is normally assembled from token-level conditional log probabilities under a declared response mask. Summing them and averaging by response length are different scoring rules. Prompt tokens, end markers, truncation and chosen/rejected identities must be handled consistently for both policy and reference. Otherwise the margin can reward a formatting or length artifact instead of the intended preference.

Reversing a preference means reversing the corresponding chosen-minus-rejected comparisons. At the symmetric zero-reference fixture, the derivative changes from-0.25 to+0.25. In a nonzero-reference case, swapping only a label string while leaving score orientation unchanged would not define the intended opposite comparison. Preserve both response records and their model scores rather than manipulating an anonymous scalar after the fact.

The full DPO formulation connects offline preference comparisons to a reference-regularized policy objective. That theoretical relationship is broader than this scalar probe, which does not train a complete language model. Likewise, the example does not train a reward model or run online reinforcement learning. [Direct Preference Optimization](https://arxiv.org/abs/2305.18290).

Feedback quality remains decisive. If annotators prefer a confident but unsupported denominator, the optimization signal rewards that preference. A lower preference loss can coexist with worse grounded correctness. Evaluate source support, abstention, domain task utility and retained capabilities separately from agreement with training pair labels.

### Interview reasoning with explanatory answers

**Why include a reference difference?** It anchors the policy's chosen/rejected advantage relative to a fixed comparison distribution. Omitting or changing the reference changes the adjusted margin being optimized.

**Does a lower preference loss establish factuality?** It establishes better agreement with the supplied preference objective on the measured pairs. Factual support depends on the rubric, evidence and independent evaluation.

**Why does beta matter beyond a name in configuration?** It scales the margin, derivative and curvature. At zero margin the gradient magnitude is \(\frac{\beta}{2}\); changing it changes the update even before considering a full model's dynamics.

## Exercise 1: Calculate the equal-margin loss

The question is: Set policy difference 0, reference difference 0, beta.5.

The objective has no preference advantage at equal margins. This exact value is an independent arithmetic check of the loss convention.

```python
difference=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); reference=0.; beta=.5
loss=F.softplus(-beta*(difference-reference))
np.testing.assert_allclose(loss.item(),np.log(2),atol=1e-12,rtol=0)
```

**Expected:** loss log 2.

**Verify:** Compare the computed values or written argument with loss log 2.

## Exercise 2: Inspect the preference gradient

The question is: Backpropagate the equal-margin loss.

The negative gradient means gradient descent increases the chosen-response advantage. The scale includes beta and the sigmoid derivative at zero.

```python
loss.backward(); np.testing.assert_allclose(difference.grad.item(),-.25,atol=1e-12,rtol=0)
```

**Expected:** gradient-.25.

**Verify:** Compare the computed values or written argument with gradient-.25.

## Exercise 3: Perform an actual update

The question is: TakeSGD.2 on the scalar policy difference and recompute the loss.

The reference remains fixed while the policy margin changes. A smaller loss demonstrates agreement with the supplied preference label, not independent answer quality.

```python
opt=torch.optim.SGD([difference],lr=.2); opt.step(); after=F.softplus(-beta*(difference-reference))
np.testing.assert_allclose(difference.item(),.05,atol=1e-12,rtol=0); assert after.item()<loss.item()
```

**Expected:** difference.05; loss belowlog2.

**Verify:** Compare the computed values or written argument with difference.05; loss belowlog2.

## Exercise 4: Reverse the preference

The question is: At zero policy difference, reverse the chosen/rejected orientation and inspect the gradient.

Both response identities and score differences must reverse consistently. Swapping only a label string without changing the associated scores would corrupt the objective.

```python
reversed_difference=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); reversed_loss=F.softplus(beta*(reversed_difference-reference)); reversed_loss.backward()
np.testing.assert_allclose(reversed_difference.grad.item(),.25,atol=1e-12,rtol=0)
```

**Expected:** gradient+.25.

**Verify:** Compare the computed values or written argument with gradient+.25.

## Exercise 5: Separate objective and factual support

The question is: Record a preferred fluent answer that invents a metric denominator.

Preference labels may encode presentation quality or annotator bias. Grounded factual support requires its own rubric and evidence.

```python
answer={'preferred':True,'source_supported':False,'claim':'Conversion rate divides by all employees.'}
assert answer['preferred'] and not answer['source_supported']
```

**Expected:** preferenceTrue; source_supportedFalse; not accepted as a grounded answer.

**Verify:** Compare the computed values or written argument with preferenceTrue; source_supportedFalse; not accepted as a grounded answer.

## Exercise 6: Name the unexecuted RLHF machinery

The question is: Create an execution receipt distinguishing the scalar offline update from reward-model training and online policy optimization.

Accurate scope prevents a small differentiable calculation from being advertised as a complete alignment pipeline. A full workflow would need data, policy, reward and evaluation evidence for each stage.

```python
receipt={'offline_preference_update':True,'reward_model_trained':False,'online_rl':False,'production_alignment_established':False}
assert receipt['offline_preference_update'] and not receipt['online_rl'] and not receipt['reward_model_trained']
```

**Expected:** offline update True; reward_model_trained False; online_rl False.

**Verify:** Compare the computed values or written argument with offline update True; reward_model_trained False; online_rl False.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
