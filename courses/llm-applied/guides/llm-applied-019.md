# llm-applied-019: Preference optimization, DPO and the RLHF distinction

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-018`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Preference learning optimizes a comparison supplied by its feedback data. This chapter develops that comparison for a domain assistant, derives what the relative-probability objective rewards, and separates improved preference fit from factual support and a complete RLHF workflow.

## Purpose and mental model

Preference optimization uses labels describing which of two responses is preferred. A DPO-style objective compares the policy chosen-versus-rejected log-probability advantage with the same advantage under a fixed reference policy, then applies a logistic loss scaled by beta. Equal adjusted margins give loss \(\log(2)\). The objective can be differentiated directly from offline preference pairs without running an online reinforcement-learning environment.

RLHF is a broader family of workflows in which human feedback informs a reward or preference signal and a policy optimization procedure. A reward model and an online policy update introduce additional state, exploration and reward-hacking risks. This chapter performs a real scalar PyTorch update on a DPO-style preference margin and contrasts its evidence with an RLHF workflow. It does not claim to train a reward model, execute online RL, or establish factuality. A preferred answer can still be unsupported or wrong if the preference labels reward style over truth.

## A preference label needs a substantive reason

The Methods Desk can produce two responses to the same question. One is concise, cites the applicable definition and preserves the computed denominator. The other is more polished but substitutes an unsupported population. A preference dataset should record why one is chosen. If the rubric rewards presentation alone, the training signal can favor the less trustworthy answer.

Other pairs may involve two supported answers with different levels of detail, or an appropriate abstention compared with an unsupported confident claim. These are legitimate but different feedback dimensions. Mixing them without a clear rubric makes the meaning of a lower preference loss hard to interpret. Retain the question, evidence, response identities, annotation rationale and disagreement state.

A pair is also conditional on its context. An answer that is preferable under one policy version or access scope may be unsuitable under another. If the chosen response includes evidence the actual caller could not access, the pair teaches an invalid behavior for that request. Data admission from the earlier chapters remains relevant after changing the optimization objective.

## Compare the policy with a fixed reference

For responses y_plus and y_minus to the same input x, define the policy log-probability difference as log pi_theta(y_plus given x) minus log pi_theta(y_minus given x). Define the analogous difference under a fixed reference policy. A DPO-style margin scales the policy-minus-reference advantage by beta, then applies a logistic loss that becomes smaller when that adjusted advantage increases.

The worked scalar example isolates this arithmetic: at equal adjusted margins, loss is log2 and the derivative has a known sign and magnitude. It performs a real SGD step on that scalar. A full language model would obtain the two log probabilities from token-level predictions and backpropagate through its parameters. The scalar itself is not a complete normalized policy over possible responses.

The reference makes the comparison relative to an existing distribution. A response pair already strongly favored by the reference has a different adjusted margin from an equally scored pair, even if the policy's raw difference is the same. Changing the reference checkpoint therefore changes the training objective. It belongs in the experiment's identity alongside tokenizer, response masks and beta.

## Relative advantage does not determine absolute probability

An illustrative probability example makes the distinction concrete. Suppose the reference assigns probabilities 0.4 to the chosen response and 0.3 to the rejected response, leaving 0.3 for other responses. A candidate assigns 0.3 and 0.1, leaving 0.6 elsewhere. The chosen response became less probable in absolute terms, but its advantage over the rejected response increased from \(\frac{4}{3}\) to 3.

The adjusted log-ratio is \(\log(\frac{3}{\frac{4}{3}})=\log(\frac{9}{4})\), about 0.81093. At beta 0.5, the margin is \(\log(\frac{3}{2})\), and the logistic loss is \(\log(\frac{5}{3})\), about 0.51083, below log2. This is a hand calculation for valid illustrative distributions, not a measured model update. It shows why a preference-loss improvement should not be paraphrased as “every chosen answer became more likely” or as a task-accuracy improvement without examining the actual outputs.

Sequence scoring adds another assumption. A joint response log probability is a sum of conditional token log probabilities under the chosen mask and stopping convention. Averaging by response length defines a different score. Prompt positions, end markers and truncation must be handled consistently for policy and reference. A convenient normalization should not be introduced silently while retaining the interpretation of a different objective.

## Feedback can reward a shortcut

If preferred answers are consistently longer, the model may learn length-related behavior that correlates with the labels without improving evidence use. If a judge prefers confident language, a cautious supported answer can be penalized. If almost every chosen response contains a particular boilerplate phrase, that phrase can become a shortcut. Review such correlations before treating the feedback as an unambiguous quality signal.

Counterexamples help define the desired behavior. Include a fluent answer with a wrong denominator, a correct concise answer, a legitimate unknown, an irrelevant citation and a qualified explanation that preserves the source's assumptions. A model-based annotator can help produce proposals, but its labels need the same validation and disagreement analysis as any other measurement process.

The evaluation should retain the underlying domain contracts: source support, numerical fidelity, access boundaries, useful coverage and baseline retention. Preference agreement is another outcome. It does not replace them. A candidate can match training preferences more closely while making an unacceptable change on a rare but consequential question family.

## Place DPO within the broader feedback landscape

Many RLHF workflows train a reward model from feedback and then optimize a policy using generated rollouts and a regularization or reference relationship. Those stages introduce additional learned state, sampling and reward-model behavior. Offline preference objectives such as DPO use a different route from fixed preference pairs to parameter updates.

The distinction is about the executed mechanism, not a hierarchy of reassuring names. This chapter does not train a reward model or run online reinforcement learning. A larger workflow would need artifacts and measurements for each stage, including how its feedback relates to actual task utility. The original DPO paper supplies the method behind the simplified margin exercise; the local numerical proof does not inherit every result from that larger setting.

For the Methods Desk, preference learning is useful only if it improves the behaviors the application values under an independent assessment. The next chapter returns to another trainable component: the retriever and reranker that determine which evidence reaches the answer model in the first place.

## Design decisions and when to use this method

Use preference optimization when examples can meaningfully distinguish better and worse responses under a stable rubric. Audit pair quality, contradictory preferences, length effects and source support before training. Keep the reference model, tokenizer, sequence scoring convention and beta in the artifact metadata. Evaluate whether preferred behavior improves held-out task utility rather than only matching training preferences.

Do not treat DPO or RLHF as a factuality guarantee. The objective follows the feedback signal, which may reward confidence, verbosity or pleasing wording. Include adversarial and unsupported-answer cases, abstention and domain-specific correctness checks. OnlineRL adds exploration and reward-model interactions that this offline fixture does not exercise. Compare methods under matched evidence and budgets before making a deployment claim.

Use preference learning only when the chosen/rejected relation has a stable, reviewed meaning. A pair can encode helpfulness, style, brevity, factual support or a mixture. Record the rubric and disagreements before treating preference optimization as a solution to a domain-quality problem.

Keep the reference policy fixed under the declared experiment, and preserve response identities with their scores. Changing sequence normalization, response truncation or the reference checkpoint changes the objective even when the final scalar formula looks the same.

## Vocabulary and concepts

**Preference margin:** The policy advantage adjusted by a reference-policy advantage.

**DPO-style loss:** A logistic objective over offline chosen/rejected comparisons.

**Reference policy:** A fixed distribution anchoring the preference comparison.

**RLHF distinction:** Additional reward and policy-learning machinery beyond this offline loss.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-019/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `llm-torch-cpu` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-019.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Represent the policy log-probability difference as a trainable scalar for the smallest diagnostic. The reference difference is fixed. Compute margin=beta*(policy_difference-reference_difference) and loss=softplus(-margin). Backpropagate and apply one SGD update. Reversing chosen/rejected labels reverses the margin and gradient direction. Keep response identities attached to scores when forming pairs.

## Derive the DPO-style scalar update

Let d be the policy chosen-minus-rejected log-probability difference and r the same difference under a fixed reference. The adjusted margin is \(z=\beta\cdot (d-r)\), and the loss is \(\log(1+\exp(-z))\), implemented through softplus for numerical stability. Its derivative with respect to d is \(-\beta\operatorname{sigmoid}(-z)\). The second derivative is \({\beta}^{2}\cdot \sigma(z)\cdot \sigma(-z)\), nonnegative, so this scalar loss is convex in d for a fixed reference.

At \(d=r=0\) and beta 0.5, the loss is log2, about 0.693147. The derivative is-0.5*0.5=-0.25, and the curvature is \(0.25\cdot 0.25=0.0625\). SGD with learning rate 0.2 moves d to \(0-0.2\cdot (-0.25)=0.05\). The new adjusted margin is 0.025 and the loss is about 0.680725. This is an actual scalar gradient update in the reference.

A positive step increases the chosen-response advantage relative to the reference, but it does not uniquely specify the two response probabilities. Many pairs of chosen/rejected log probabilities can have the same difference. The fixture optimizes a free scalar and does not implement a vocabulary softmax, sequence model, KL measurement or normalized policy distribution. Calling it DPO-style margin mechanics preserves that distinction.

In a language model, a response log probability is normally assembled from token-level conditional log probabilities under a declared response mask. Summing them and averaging by response length are different scoring rules. Prompt tokens, end markers, truncation and chosen/rejected identities must be handled consistently for both policy and reference. Otherwise the margin can reward a formatting or length artifact instead of the intended preference.

Reversing a preference means reversing the corresponding chosen-minus-rejected comparisons. At the symmetric zero-reference fixture, the derivative changes from-0.25 to+0.25. In a nonzero-reference case, swapping only a label string while leaving score orientation unchanged would not define the intended opposite comparison. Preserve both response records and their model scores rather than manipulating an anonymous scalar after the fact.

The full DPO formulation connects offline preference comparisons to a reference-regularized policy objective. That theoretical relationship is broader than this scalar probe, which does not train a complete language model. Likewise, the example does not train a reward model or run online reinforcement learning. [Direct Preference Optimization](https://arxiv.org/abs/2305.18290).

Feedback quality remains decisive. If annotators prefer a confident but unsupported denominator, the optimization signal rewards that preference. A lower preference loss can coexist with worse grounded correctness. Evaluate source support, abstention, domain task utility and retained capabilities separately from agreement with training pair labels.

### Interview reasoning with explanatory answers

**Why include a reference difference?** It anchors the policy's chosen/rejected advantage relative to a fixed comparison distribution. Omitting or changing the reference changes the adjusted margin being optimized.

**Does a lower preference loss establish factuality?** It establishes better agreement with the supplied preference objective on the measured pairs. Factual support depends on the rubric, evidence and independent evaluation.

**Why does beta matter beyond a name in configuration?** It scales the margin, derivative and curvature. At zero margin the gradient magnitude is \(\frac{\beta}{2}\); changing it changes the update even before considering a full model's dynamics.

## Worked example / walkthrough

### Example A: Calculate the equal-margin loss

The objective has no preference advantage at equal margins. This exact value is an independent arithmetic check of the loss convention.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

difference=nn.Parameter(torch.tensor(0.,dtype=torch.float64)); reference=0.; beta=.5
loss=F.softplus(-beta*(difference-reference))
np.testing.assert_allclose(loss.item(),np.log(2),atol=1e-12,rtol=0)
```

**Expected:** loss \(\log(2)\).

### Example B: Inspect the preference gradient

The negative gradient means gradient descent increases the chosen-response advantage. The scale includes beta and the sigmoid derivative at zero.

```python
loss.backward(); np.testing.assert_allclose(difference.grad.item(),-.25,atol=1e-12,rtol=0)
```

**Expected:** gradient-.25.

### Example C: Perform an actual update

The reference remains fixed while the policy margin changes. A smaller loss demonstrates agreement with the supplied preference label, not independent answer quality.

```python
opt=torch.optim.SGD([difference],lr=.2); opt.step(); after=F.softplus(-beta*(difference-reference))
np.testing.assert_allclose(difference.item(),.05,atol=1e-12,rtol=0); assert after.item()<loss.item()
```

**Expected:** difference.05; loss below \(\log(2)\).

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: loss \(\log(2)\). offline update True; reward_model_trained False; online_rl False. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate the equal-margin loss.** Set policy difference 0, reference difference 0, beta.5.
   **Expected:** loss \(\log(2)\).
   **Verify:** Save the assertion results for exercise 1, including loss \(\log(2)\).

2. **Inspect the preference gradient.** Backpropagate the equal-margin loss.
   **Expected:** gradient-.25.
   **Verify:** Save the assertion results for exercise 2, including gradient-.25.

3. **Perform an actual update.** Take SGD at 0.2 on the scalar policy difference and recompute the loss.
   **Expected:** difference.05; loss below \(\log(2)\).
   **Verify:** Save the assertion results for exercise 3, including difference.05; loss below \(\log(2)\).

4. **Reverse the preference.** At zero policy difference, reverse the chosen/rejected orientation and inspect the gradient.
   **Expected:** gradient+.25.
   **Verify:** Save the assertion results for exercise 4, including gradient+.25.

5. **Separate objective and factual support.** Record a preferred fluent answer that invents a metric denominator.
   **Expected:** preference True; source_supported False; not accepted as a grounded answer.
   **Verify:** Save the assertion results for exercise 5, including preference True; source_supported False; not accepted as a grounded answer.

6. **Name the unexecuted RLHF machinery.** Create an execution receipt distinguishing the scalar offline update from reward-model training and online policy optimization.
   **Expected:** offline update True; reward_model_trained False; online_rl False.
   **Verify:** Save the assertion results for exercise 6, including offline update True; reward_model_trained False; online_rl False.

## Common pitfalls and diagnosis

If the first update moves toward the rejected response, check orientation and the sign inside softplus. If two implementations disagree by a factor, inspect beta and sequence reduction. If score differences change after tokenization updates, verify the response mask and end-marker handling in both policy and reference.

If preference metrics improve while factual support declines, inspect the labels and rubric before increasing training. If a scalar probe is presented as a complete RLHF run, identify the missing policy, reward/environment and evaluation artifacts. Preserve disagreement cases instead of treating preference as an unquestionable ground truth.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Preference margin, DPO-style loss, Reference policy using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-018` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Direct Preference Optimization](https://arxiv.org/abs/2305.18290), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-019, Preference optimization, DPO and the RLHF distinction.
Read courses/llm-applied/guides/llm-applied-019.md and courses/llm-applied/lessons/llm-applied-019.py. Direct prerequisites: `llm-applied-018`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
