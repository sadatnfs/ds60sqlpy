# eval-017: Preference data and Bradley-Terry reward models

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-003`, `eval-011`, `llm-applied-020`.

Derive a pairwise reward likelihood, test its invariances and identify what comparison data cannot determine.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-017`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Preferences define a different target from correctness

A preference label states that one response was chosen over another under a particular prompt, rubric and annotator context. It may reflect correctness, usefulness, style or an undesired shortcut. A reward model trained from preferences inherits that target. It is not automatically a correctness model or a universal measure of human welfare.

The Bradley-Terry model assigns scalar scores and converts a score difference into a comparison probability. The logistic function is \(\sigma(z)=1/(1+\exp(-z))\); it maps a real score difference to a number between zero and one. For preferred response \(a\), alternative \(b\), reward function \(r\) and logistic function \(\sigma\),

\[
P(a\succ b\mid x)=\sigma(r(x,a)-r(x,b)).
\]

For a positive comparison, the negative log likelihood is \(\log(1+\exp(-(r_a-r_b)))\). A numerically stable softplus calculation is preferable to taking the logarithm of a probability that may round to zero. The code uses `logaddexp` and checks extreme score differences.

## Worked case A: reward offsets are unidentified

Adding the same constant to both responses leaves their score difference and preference probability unchanged. If comparisons occur only within a prompt, the offset can be different for each prompt. A reward level from one prompt should therefore not be interpreted as directly comparable with a level from another merely because both came from one pairwise objective.

The gradient of one positive-comparison loss with respect to the two scores sums to zero. The data inform a relative difference, not a common translation. The reference verifies this analytically and with finite differences.

```python
import numpy as np


def sigmoid(x):
    return np.exp(-np.logaddexp(0.0, -np.asarray(x, float)))


def pair_loss(scores):
    a, b = np.asarray(scores, float)
    return float(np.logaddexp(0.0, -(a - b)))


def pair_gradient(scores):
    a, b = np.asarray(scores, float)
    g = float(sigmoid(a - b) - 1)
    return np.array([g, -g])


def mle_difference(wins, losses):
    if not np.isfinite([wins, losses]).all() or wins <= 0 or losses <= 0:
        raise ValueError("Finite unregularized MLE needs wins and losses")
    return float(np.log(wins / losses))


def worked_a():
    scores = np.array([1.0, -1.0])
    shifted = scores + 100
    assert np.isclose(pair_loss(scores), pair_loss(shifted))
    analytic = pair_gradient(scores)
    h = 1e-5
    numeric = np.array(
        [
            (pair_loss(scores + np.eye(2)[i] * h) - pair_loss(scores - np.eye(2)[i] * h)) / (2 * h)
            for i in range(2)
        ]
    )
    np.testing.assert_allclose(analytic, numeric, rtol=1e-8, atol=1e-10)
    assert np.isclose(analytic.sum(), 0)
    print("Pair loss:", pair_loss(scores), "gradient:", analytic.tolist())


worked_a()
```

## Worked case B: empirical preference rates and inconsistent cycles

Three wins and one loss for the same pair produce a maximum-likelihood difference of \(\log 3\), giving a probability of three quarters. The label frequency is uncertain in a finite sample; the fitted probability is not a certainty that the response is better in every context.

A strict cycle A preferred to B, B to C and C to A cannot all be satisfied by a single deterministic scalar ordering. Such labels need not be corrupt: they may represent stochastic choices, multiple criteria or heterogeneous annotators. A scalar probabilistic model can still fit a compromise, but its interpretation and residual failures matter.

```python
import numpy as np


def sigmoid(x):
    return np.exp(-np.logaddexp(0.0, -np.asarray(x, float)))


def pair_loss(scores):
    a, b = np.asarray(scores, float)
    return float(np.logaddexp(0.0, -(a - b)))


def pair_gradient(scores):
    a, b = np.asarray(scores, float)
    g = float(sigmoid(a - b) - 1)
    return np.array([g, -g])


def mle_difference(wins, losses):
    if not np.isfinite([wins, losses]).all() or wins <= 0 or losses <= 0:
        raise ValueError("Finite unregularized MLE needs wins and losses")
    return float(np.log(wins / losses))


def worked_b():
    delta = mle_difference(3, 1)
    assert np.isclose(sigmoid(delta), 0.75)
    # Strict scalar inequalities a>b, b>c, c>a cannot all hold.
    a, b, c = 2.0, 1.0, 0.0
    assert (a > b) and (b > c) and not (c > a)
    print("Pairwise MLE difference:", delta, "probability:", float(sigmoid(delta)))


worked_b()
```

## Comparison design and data quality

A disconnected comparison graph permits separate shifts for disconnected components. More comparisons inside one component do not identify its offset relative to another. Choose comparison coverage to support the questions you intend to answer. Keep prompt identity, candidate identity, display order, labeler/rubric version and ties or abstentions in the ledger.

Ties require a declared treatment. Assigning half a binary win to each side is one scoring convention, not a universal model of indifference. Missing or inapplicable comparisons should not be silently encoded as ties. Position and length biases from earlier units can become learned reward shortcuts if they are present in the training labels.

## From a fitted reward to an optimization signal

Optimization searches for responses with high predicted reward. It can discover regions where the model extrapolates poorly, especially when the reward predictor was trained on a narrow response distribution. Keep reward-model validation separate from policy evaluation, and test shifted candidate distributions as training changes the policy.

The finite examples expose the likelihood, identifiability and numerical behavior before any neural training. They do not claim that a scalar reward captures all relevant preferences or that preference optimization improves factual accuracy. The next unit fits a small real PyTorch reward model and tests a deliberate length shortcut on a held-out comparison.


## Six investigations

### 1. Equal scores

Evaluate a positive comparison when both scores are zero.

**Expected:** Preference probability 0.5 and loss log 2.

**Hint:** Use the logistic link and softplus form.

### 2. Shift both rewards

Add 100 to both responses.

**Expected:** Loss and score gradient remain unchanged.

**Hint:** Only the difference is identified.

### 3. Reverse empirical counts

Use one win and three losses.

**Expected:** The fitted preference probability is 0.25.

**Hint:** The MLE difference is log(wins/losses).

### 4. All wins and no losses

Fit an unregularized pair with four wins and zero losses.

**Expected:** No finite maximum-likelihood difference exists.

**Hint:** Log odds diverge at a boundary probability.

### 5. Test numerical stability

Use scores-1000 and 1000 for the preferred/rejected pair.

**Expected:** Loss remains finite at 2000.

**Hint:** Avoid log(sigmoid(delta)) computed naively.

### 6. Interpret a preference cycle

Observe A>B, B>C and C>A across labels.

**Expected:** A deterministic scalar ordering cannot satisfy all three.

**Hint:** Add the three proposed positive score differences.

## Primary references

- [Preference-based reward learning](https://arxiv.org/abs/1706.03741)
- [Direct Preference Optimization model assumptions](https://arxiv.org/abs/2305.18290)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
