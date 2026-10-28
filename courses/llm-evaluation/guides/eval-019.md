# eval-019: KL-regularized policies and reward exploitation

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-017`, `eval-016`.

Derive an exact finite-policy optimum and show why improving a proxy reward can reduce independently defined task utility.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-019`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## A policy is a conditional distribution over actions

For one context, a policy assigns probabilities to possible responses or actions. A language model makes many conditional token decisions, but a two-action policy is enough to expose the objective and its assumptions. This unit uses authored actions with known rewards; it does not generate natural-language answers.

Let \(p_i\) be the policy probability of action \(i\), \(q_i\) a fixed reference probability and \(r_i\) a reward. Consider

\[
J(p)=\sum_i p_i r_i-\beta\sum_i p_i\log\frac{p_i}{q_i},\qquad \beta>0.
\]

The second term penalizes divergence from the reference. The distributions must share suitable support. Assigning positive policy probability where the reference has zero probability makes this direction of KL infinite. Replacing a zero reference probability with a small positive constant changes the problem, rather than merely fixing a numerical issue.

Introducing a Lagrange multiplier for \(\sum_i p_i=1\) and setting derivatives to zero gives a normalized exponential tilt:

\[
p_i^*=\frac{q_i\exp(r_i/\beta)}{\sum_j q_j\exp(r_j/\beta)}.
\]

The implementation subtracts the maximum log weight before exponentiation. This leaves the normalized probabilities unchanged while avoiding overflow. The reference remains fixed during this calculation; it is different from the old rollout policy used later for PPO ratios.

## Worked case A: inspect the exact optimum

With rewards 1 and 0, a uniform reference and beta 1, the preferred action receives probability \(e/(1+e)\). Its regularized objective exceeds the reference objective. A second calculation compares the gradient through a softmax parameterization to central finite differences. This checks both the reward and KL derivatives rather than testing only a final scalar value.

```python
import numpy as np


def probability_vector(values):
    x = np.asarray(values, float)
    if (
        x.ndim != 1
        or not x.size
        or not np.isfinite(x).all()
        or np.any(x <= 0)
        or not np.isclose(x.sum(), 1)
    ):
        raise ValueError("Strictly positive normalized probabilities required")
    return x


def softmax(logits):
    x = np.asarray(logits, float)
    weights = np.exp(x - x.max())
    return weights / weights.sum()


def objective(p, q, reward, beta):
    p = probability_vector(p)
    q = probability_vector(q)
    r = np.asarray(reward, float)
    if p.shape != q.shape or p.shape != r.shape or beta <= 0 or not np.isfinite(r).all():
        raise ValueError("Aligned rewards and positive beta required")
    return float(p @ r - beta * np.sum(p * np.log(p / q)))


def optimal_policy(q, reward, beta):
    q = probability_vector(q)
    r = np.asarray(reward, float)
    if r.shape != q.shape or beta <= 0 or not np.isfinite(r).all() or not np.isfinite(beta):
        raise ValueError("Invalid policy objective")
    return softmax(np.log(q) + r / beta)


def logit_gradient(logits, q, reward, beta):
    p = softmax(logits)
    direction = np.asarray(reward) - beta * (np.log(p / np.asarray(q)) + 1)
    return p * (direction - p @ direction)


def worked_a():
    q = np.array([0.5, 0.5])
    r = np.array([1.0, 0.0])
    p = optimal_policy(q, r, 1.0)
    assert np.isclose(p[0], np.e / (1 + np.e))
    assert objective(p, q, r, 1) > objective(q, q, r, 1)
    logits = np.array([0.2, -0.1])
    h = 1e-5
    numeric = np.array(
        [
            (
                objective(softmax(logits + np.eye(2)[i] * h), q, r, 1)
                - objective(softmax(logits - np.eye(2)[i] * h), q, r, 1)
            )
            / (2 * h)
            for i in range(2)
        ]
    )
    np.testing.assert_allclose(logit_gradient(logits, q, r, 1), numeric, atol=1e-10)
    print("Exact policy:", p.tolist(), "regularized objective:", objective(p, q, r, 1))


worked_a()
```

## Worked case B: a wrong reward produces a wrong policy

Suppose the proxy assigns a high score to a verbose unsupported answer, while independently defined task utility penalizes that answer. Optimizing the proxy pushes probability toward the bad action and reduces true utility. A KL penalty limits how far the policy moves for a given reward scale, but does not turn the proxy into a correct measure of the task.

```python
import numpy as np


def probability_vector(values):
    x = np.asarray(values, float)
    if (
        x.ndim != 1
        or not x.size
        or not np.isfinite(x).all()
        or np.any(x <= 0)
        or not np.isclose(x.sum(), 1)
    ):
        raise ValueError("Strictly positive normalized probabilities required")
    return x


def softmax(logits):
    x = np.asarray(logits, float)
    weights = np.exp(x - x.max())
    return weights / weights.sum()


def objective(p, q, reward, beta):
    p = probability_vector(p)
    q = probability_vector(q)
    r = np.asarray(reward, float)
    if p.shape != q.shape or p.shape != r.shape or beta <= 0 or not np.isfinite(r).all():
        raise ValueError("Aligned rewards and positive beta required")
    return float(p @ r - beta * np.sum(p * np.log(p / q)))


def optimal_policy(q, reward, beta):
    q = probability_vector(q)
    r = np.asarray(reward, float)
    if r.shape != q.shape or beta <= 0 or not np.isfinite(r).all() or not np.isfinite(beta):
        raise ValueError("Invalid policy objective")
    return softmax(np.log(q) + r / beta)


def logit_gradient(logits, q, reward, beta):
    p = softmax(logits)
    direction = np.asarray(reward) - beta * (np.log(p / np.asarray(q)) + 1)
    return p * (direction - p @ direction)


def worked_b():
    q = np.array([0.5, 0.5])
    proxy = np.array([1.0, 3.0])
    utility = np.array([1.0, -2.0])
    optimized = optimal_policy(q, proxy, 0.2)
    assert optimized @ proxy > q @ proxy and optimized @ utility < q @ utility
    assert optimized[1] > 0.999
    print(
        "Proxy improved:",
        float(optimized @ proxy),
        "independent utility:",
        float(optimized @ utility),
    )


worked_b()
```

## Reward scale, temperature and reference choice

Multiplying all rewards and beta by the same positive factor preserves the optimal policy. Adding a common reward constant also preserves it. These invariances help diagnose implementations. Changing only the reward scale changes the tradeoff against KL and can alter the policy sharply. Report both scales when comparing training runs.

The reference distribution itself encodes a choice. A poor reference can assign too little probability to useful actions or omit them entirely. A strong reference may preserve valuable behavior, but closeness to it is not a proof of access-policy compliance, factuality or safety. Keep independent held-out and critical-condition assessments from the evaluation sequence.

## Interpretation and transfer

For an autoregressive model, sequence probabilities factor into conditional token probabilities. The context, stopping rule, mask and normalization determine which probability law the objective refers to. Summing token log ratios along a sampled response produces a sequence log ratio, but a sample average still needs the correct sampling distribution and weighting to estimate a population KL.

A real policy update should retain the reward model version, reference checkpoint, rollout policy, sampled responses and optimization configuration. Measure actual reward/utility behavior on independent cases after training. A decrease in the training loss or an increase in proxy reward is evidence about optimization, not proof that the deployed task improved.

The exact finite-action calculations here make support, derivatives and reward exploitation visible without a large model. Their closed-form optimum is a property of the stated objective. Later units compare DPO, PPO and group-relative updates while preserving these distinctions.


## Six investigations

### 1. Add a reward constant

Add 100 to every action reward.

**Expected:** The optimal distribution is unchanged.

**Hint:** The common exponential factor cancels in normalization.

### 2. Rescale reward and beta

Multiply both by 2.

**Expected:** The optimal distribution is unchanged.

**Hint:** Inspect the ratio reward/beta.

### 3. Inspect the gradient sum

Sum the two logit-gradient components.

**Expected:** The sum is approximately zero.

**Hint:** A common logit shift leaves softmax probabilities unchanged.

### 4. Handle large rewards

Use rewards 1000 and 999.

**Expected:** Stable normalization returns finite probabilities.

**Hint:** Subtract the maximum log weight before exponentiation.

### 5. Identify missing support

Give a useful action zero reference probability.

**Expected:** The bounded helper rejects the unsupported objective.

**Hint:** KL in this direction is infinite for positive mass outside reference support.

### 6. Test independent utility

Optimize the authored proxy from case B.

**Expected:** Proxy reward rises while independent task utility falls.

**Hint:** Keep the evaluation utility outside the training objective.

## Primary references

- [Preference-based reinforcement learning](https://arxiv.org/abs/1706.03741)
- [DPO derivation of the regularized policy](https://arxiv.org/abs/2305.18290)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.

## Interactive figure variant

Select **Interactive Plotly** in the lesson variant control. Its complete program uses the same authored inputs to draw the corresponding risk, calibration or policy curve. The captured figure retains a description and exact data table, and its JSON can be downloaded. Hovering a point does not create new statistical evidence. The default numerical reference remains separately saved.
