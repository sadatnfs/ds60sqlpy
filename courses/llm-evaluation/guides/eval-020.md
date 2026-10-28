# eval-020: Direct Preference Optimization from ratios to gradients

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-019`, `llm-applied-015`.

Derive the DPO loss from a regularized preference model and distinguish sequence log probabilities, temperature effects and held-out evaluation.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-020`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Connect the preference model to a policy

The previous unit gives an exponential-tilt optimum for a KL-regularized finite policy. Rearranging that relation writes its reward as a reference-relative log probability plus a context-specific normalizing constant. A Bradley-Terry comparison subtracts the two rewards for the same context, so that shared constant cancels.

For a chosen response \(y_w\), rejected response \(y_l\), policy \(\pi_\theta\) and frozen reference \(\pi_{\mathrm{ref}}\), define

\[
m_\theta=\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}
-\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)},\qquad
\ell_{\mathrm{DPO}}=-\log\sigma(\beta m_\theta).
\]

This derivation depends on its preference and regularization assumptions. It does not mean that every preference dataset obeys them, or that a trained policy becomes a calibrated judge of factual correctness. DPO avoids a separately fitted reward predictor in this objective; it still uses response likelihoods, preference labels and a reference model.

## Worked case A: loss and derivative at the reference

When policy and reference coincide, the margin is zero and the loss is \(\log2\). For a two-action softmax, the policy log-odds difference is a single parameter. The code differentiates the loss with respect to that parameter and compares the analytic gradient to finite differences. With a positive preference and beta 2, the derivative at the reference is -1.

```python
import numpy as np


def sigmoid(x):
    return np.exp(-np.logaddexp(0.0, -np.asarray(x, float)))


def dpo_loss(delta, reference_delta, beta=1.0, win_fraction=1.0):
    if (
        not np.isfinite([delta, reference_delta, beta, win_fraction]).all()
        or beta <= 0
        or not 0 <= win_fraction <= 1
    ):
        raise ValueError("Positive beta and valid frequency required")
    z = beta * (delta - reference_delta)
    return float(win_fraction * np.logaddexp(0.0, -z) + (1 - win_fraction) * np.logaddexp(0.0, z))


def dpo_gradient(delta, reference_delta, beta=1.0, win_fraction=1.0):
    dpo_loss(delta, reference_delta, beta, win_fraction)
    return float(beta * (sigmoid(beta * (delta - reference_delta)) - win_fraction))


def fitted_delta(wins, losses, beta, reference_delta=0.0):
    if (
        not np.isfinite([wins, losses, beta, reference_delta]).all()
        or wins <= 0
        or losses <= 0
        or beta <= 0
    ):
        raise ValueError("Finite preference fit requires both labels")
    return reference_delta + np.log(wins / losses) / beta


def worked_a():
    assert np.isclose(dpo_loss(0, 0, 2), np.log(2))
    assert dpo_gradient(0, 0, 2) == -1
    delta = 0.4
    h = 1e-5
    numeric = (dpo_loss(delta + h, 0, 2) - dpo_loss(delta - h, 0, 2)) / (2 * h)
    assert np.isclose(numeric, dpo_gradient(delta, 0, 2), atol=1e-10)
    print("Reference loss:", dpo_loss(0, 0, 2), "initial gradient:", dpo_gradient(0, 0, 2))


worked_a()
```

## Worked case B: beta changes more than an initial step size

For three positive and one negative comparison of the same pair, the fitted classifier logit is \(\log3\). The policy log-odds shift is that value divided by beta. A larger beta can produce a larger initial gradient yet a smaller optimum shift for the same empirical preference frequency. This counterexample prevents the simplistic interpretation that increasing beta always pushes the learned policy further from the reference.

```python
import numpy as np


def sigmoid(x):
    return np.exp(-np.logaddexp(0.0, -np.asarray(x, float)))


def dpo_loss(delta, reference_delta, beta=1.0, win_fraction=1.0):
    if (
        not np.isfinite([delta, reference_delta, beta, win_fraction]).all()
        or beta <= 0
        or not 0 <= win_fraction <= 1
    ):
        raise ValueError("Positive beta and valid frequency required")
    z = beta * (delta - reference_delta)
    return float(win_fraction * np.logaddexp(0.0, -z) + (1 - win_fraction) * np.logaddexp(0.0, z))


def dpo_gradient(delta, reference_delta, beta=1.0, win_fraction=1.0):
    dpo_loss(delta, reference_delta, beta, win_fraction)
    return float(beta * (sigmoid(beta * (delta - reference_delta)) - win_fraction))


def fitted_delta(wins, losses, beta, reference_delta=0.0):
    if (
        not np.isfinite([wins, losses, beta, reference_delta]).all()
        or wins <= 0
        or losses <= 0
        or beta <= 0
    ):
        raise ValueError("Finite preference fit requires both labels")
    return reference_delta + np.log(wins / losses) / beta


def worked_b():
    deltas = [fitted_delta(3, 1, beta) for beta in (0.5, 1.0, 2.0)]
    probabilities = sigmoid(deltas)
    np.testing.assert_allclose(probabilities, [0.9, 0.75, np.sqrt(3) / (1 + np.sqrt(3))])
    assert all(
        abs(dpo_gradient(delta, 0, beta, 0.75)) < 1e-12
        for delta, beta in zip(deltas, (0.5, 1.0, 2.0), strict=True)
    )
    print("Policy probabilities at empirical optima:", probabilities.tolist())


worked_b()
```

## Sequence likelihoods and masks

A response log probability is a sum over its predicted tokens under the declared conditional histories. Prompt tokens used as conditioning are not necessarily part of the response loss. Padding and tokens after stopping must be excluded consistently, and the treatment of the end-of-sequence token must be stated. A length-normalized mean log probability defines a different objective from the sequence sum.

The reference includes a numerical counterexample where dividing chosen and rejected log ratios by their different lengths reverses the margin's sign. Neither calculation should be substituted for the other without changing the declared training objective. Keep tokenizer identity, masks, reference outputs and sequence lengths in the training artifact contract.

## Data and evaluation boundaries

Preference pairs may have been collected under a different policy. Their coverage and labeling process determine which comparisons the update sees. Missing response regions, annotator mixtures and presentation shortcuts remain relevant. A dataset of only unanimous wins can lead to a separable objective with no finite unconstrained optimum; regularization, early stopping or additional comparisons alter that situation.

Evaluate the resulting policy with independent task and critical-risk evidence. Do not use the same preferences both to choose hyperparameters and to make an untouched-final-set claim. A lower DPO loss demonstrates better fit to this objective, not necessarily a better assistant under an external task distribution.

This unit performs exact finite-action calculations. It does not fine-tune pretrained weights. The existing supervised adaptation route supplies real tiny decoder mechanics, while the next PPO units expose rollout policies, advantage estimation and actual small CPU policy updates under their own contracts.


## Six investigations

### 1. Evaluate the reference

Set policy and reference log odds equal for any positive beta.

**Expected:** The loss for a positive preference is log 2.

**Hint:** Both reference-relative log ratios cancel.

### 2. Differentiate the two-action loss

Use beta 2 and zero reference-relative log-odds shift.

**Expected:** The derivative is -1.

**Hint:** Differentiate softplus(-beta times the shift).

### 3. Compare beta optima

Fit a3:1 preference ratio with beta 0.5,1 and 2 under a uniform reference.

**Expected:** Preferred-action probabilities are 0.9,0.75 and approximately 0.634.

**Hint:** The optimum policy-logit shift is log 3 divided by beta.

### 4. Change length normalization

Use the token log-ratio arrays in the reference exercise.

**Expected:** The sequence-sum margin is negative while the mean-token margin is positive.

**Hint:** Chosen and rejected sequences have different lengths.

### 5. Protect the reference

Update the reference parameters while retaining the same loss label.

**Expected:** The objective has changed.

**Hint:** The reference is part of the training specification.

### 6. Bound the claim

Observe a lower training DPO loss.

**Expected:** Conclude improved fit to the declared preference objective only.

**Hint:** Separate training labels from independent task outcomes.

## Primary references

- [Direct Preference Optimization](https://arxiv.org/abs/2305.18290)
- [Existing causal decoder training mechanics](../../../courses/llm-applied/guides/llm-applied-015.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
