# llm-applied-019: Preference optimization, DPO and the RLHF distinction

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-018`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Preference optimization uses labels describing which of two responses is preferred. The central investigation is concrete: Set policy difference0, reference difference0, beta.5. The finish condition is losslog2. offline updateTrue; reward_model_trainedFalse; online_rlFalse. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Preference optimization uses labels describing which of two responses is preferred. A DPO-style objective compares the policy chosen-versus-rejected log-probability advantage with the same advantage under a fixed reference policy, then applies a logistic loss scaled bybeta. Equal adjusted margins give losslog2. The objective can be differentiated directly from offline preference pairs without running an online reinforcement-learning environment.

RLHF is a broader family of workflows in which human feedback informs a reward or preference signal and a policy optimization procedure. A reward model and an online policy update introduce additional state, exploration and reward-hacking risks. This chapter performs a real scalar PyTorch update on a DPO-style preference margin and contrasts its evidence with an RLHF workflow. It does not claim to train a reward model, execute onlineRL, or establish factuality. A preferred answer can still be unsupported or wrong if the preference labels reward style over truth.

## Design decisions and when to use this method

Use preference optimization when examples can meaningfully distinguish better and worse responses under a stable rubric. Audit pair quality, contradictory preferences, length effects and source support before training. Keep the reference model, tokenizer, sequence scoring convention andbeta in the artifact metadata. Evaluate whether preferred behavior improves held-out task utility rather than only matching training preferences.

Do not treat DPO orRLHF as a factuality guarantee. The objective follows the feedback signal, which may reward confidence, verbosity or pleasing wording. Include adversarial and unsupported-answer cases, abstention and domain-specific correctness checks. OnlineRL adds exploration and reward-model interactions that this offline fixture does not exercise. Compare methods under matched evidence and budgets before making a deployment claim.

## Vocabulary and concepts

**Preference margin:** The policy advantage adjusted by a reference-policy advantage.

**DPO-style loss:** A logistic objective over offline chosen/rejected comparisons.

**Reference policy:** A fixed distribution anchoring the preference comparison.

**RLHF distinction:** Additional reward and policy-learning machinery beyond this offline loss.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-019/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-019.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-019.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Represent the policy log-probability difference as a trainable scalar for the smallest diagnostic. The reference difference is fixed. Compute margin=beta*(policy_difference-reference_difference) andloss=softplus(-margin). Backpropagate and apply oneSGD update. Reversing chosen/rejected labels reverses the margin and gradient direction. Keep response identities attached to scores when forming pairs.

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

**Expected:** losslog2.

### Example B: Inspect the preference gradient

The negative gradient means gradient descent increases the chosen-response advantage. The scale includesbeta and the sigmoid derivative atzero.

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

**Expected:** difference.05; loss belowlog2.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: losslog2. offline updateTrue; reward_model_trainedFalse; online_rlFalse. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate the equal-margin loss.** Set policy difference0, reference difference0, beta.5.
   **Expected:** losslog2.
   **Verify:** Save the assertion results for exercise 1, including losslog2.

2. **Inspect the preference gradient.** Backpropagate the equal-margin loss.
   **Expected:** gradient-.25.
   **Verify:** Save the assertion results for exercise 2, including gradient-.25.

3. **Perform an actual update.** TakeSGD.2 on the scalar policy difference and recompute the loss.
   **Expected:** difference.05; loss belowlog2.
   **Verify:** Save the assertion results for exercise 3, including difference.05; loss belowlog2.

4. **Reverse the preference.** Atzero policy difference, reverse the chosen/rejected orientation and inspect the gradient.
   **Expected:** gradient+.25.
   **Verify:** Save the assertion results for exercise 4, including gradient+.25.

5. **Separate objective and factual support.** Record a preferred fluent answer that invents a metric denominator.
   **Expected:** preferenceTrue; source_supportedFalse; not accepted as a grounded answer.
   **Verify:** Save the assertion results for exercise 5, including preferenceTrue; source_supportedFalse; not accepted as a grounded answer.

6. **Name the unexecuted RLHF machinery.** Create an execution receipt distinguishing the scalar offline update from reward-model training and online policy optimization.
   **Expected:** offline updateTrue; reward_model_trainedFalse; online_rlFalse.
   **Verify:** Save the assertion results for exercise 6, including offline updateTrue; reward_model_trainedFalse; online_rlFalse.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Preference margin, DPO-style loss, Reference policy using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-018` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Direct Preference Optimization](https://arxiv.org/abs/2305.18290), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-019, Preference optimization, DPO and the RLHF distinction.
Read courses/llm-applied/guides/llm-applied-019.md and courses/llm-applied/lessons/llm-applied-019.py. Direct prerequisites: `llm-applied-018`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
