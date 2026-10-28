# eval-023: GRPO groups, normalization and KL estimators

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-021`, `eval-019`.

Compute group-relative advantages, expose degeneracy and weighting choices, and identify the sampling law required by a KL estimator.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-023`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Relative rewards provide a comparison signal

Group-relative methods compare several responses to the same prompt. For an outcome-reward group \(r_1,\ldots,r_G\), a common normalization subtracts the group mean and divides by a stated standard-deviation convention. This removes a learned value baseline from that part of the mechanism, but it does not remove the need for meaningful rewards or independent evaluation.

This lesson uses population standard deviation within each authored group. Other implementations may use a sample correction or an epsilon; these choices change advantage scales and should be recorded. Groups are formed by prompt. Combining rewards from unrelated prompts before normalization defines a different comparison and can mix prompt difficulty with response quality.

For a nonconstant group,

\[
\widehat A_i=\frac{r_i-\bar r}{\sqrt{G^{-1}\sum_j(r_j-\bar r)^2}}.
\]

The centered advantages sum to zero. That does not imply that the policy gradient is zero, because each advantage multiplies a different score-function or probability-ratio derivative. The value of a centered objective at the old policy and its derivative are different objects.

## Worked case A: constant groups and invariances

The group 0,1,2,3 has nonzero relative signal, with mean-zero, unit-variance advantages under the stated convention. A common reward shift or positive scaling preserves those advantages when the variance remains numerically resolved. A constant group yields zero advantages by an explicit policy, preventing division by zero.

Both an all-correct group and an all-incorrect group can be constant. Record raw pass rates and group variability as well as normalized advantages. Zero relative signal does not establish that the task is solved. A separate KL regularizer can still produce an update when the reward term is zero.

```python
import numpy as np


def group_advantages(rewards):
    r = np.asarray(rewards, float)
    if r.ndim != 1 or len(r) < 2 or not np.isfinite(r).all():
        raise ValueError("At least two finite group rewards required")
    centered = r - r.mean()
    scale = float(np.sqrt(np.mean(centered**2)))
    return np.zeros_like(r) if scale == 0 else centered / scale


def kl_terms(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    if (
        p.shape != q.shape
        or p.ndim != 1
        or not np.isfinite(p).all()
        or not np.isfinite(q).all()
        or np.any(p <= 0)
        or np.any(q <= 0)
        or not np.isclose(p.sum(), 1)
        or not np.isclose(q.sum(), 1)
    ):
        raise ValueError("Positive normalized distributions required")
    ratio = q / p
    return ratio - np.log(ratio) - 1


def worked_a():
    a = group_advantages([0, 1, 2, 3])
    assert np.isclose(a.mean(), 0) and np.isclose(np.mean(a * a), 1)
    np.testing.assert_allclose(a, group_advantages([10, 11, 12, 13]))
    np.testing.assert_allclose(a, group_advantages([0, 2, 4, 6]))
    assert group_advantages([0, 0, 0]).tolist() == [0.0, 0.0, 0.0]
    print("Group advantages:", a.tolist(), "constant group:", group_advantages([1, 1]).tolist())


worked_a()
```

## Worked case B: the KL sampling distribution matters

For positive distributions \(p\) and \(q\), define the pointwise quantity \(k(a)=q(a)/p(a)-\log(q(a)/p(a))-1\). It is nonnegative. Its expectation under \(a\sim p\) equals \(D_{KL}(p\Vert q)\), because the ratio term averages to one. Sampling under a different old policy generally gives another expectation.

The code enumerates two actions and compares the exact current-policy expectation, an old-policy average and an importance-corrected old-policy average. This is a value-estimator identity under explicit support assumptions. It does not prove that differentiating any sampled expression gives an unbiased KL gradient.

```python
import numpy as np


def group_advantages(rewards):
    r = np.asarray(rewards, float)
    if r.ndim != 1 or len(r) < 2 or not np.isfinite(r).all():
        raise ValueError("At least two finite group rewards required")
    centered = r - r.mean()
    scale = float(np.sqrt(np.mean(centered**2)))
    return np.zeros_like(r) if scale == 0 else centered / scale


def kl_terms(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    if (
        p.shape != q.shape
        or p.ndim != 1
        or not np.isfinite(p).all()
        or not np.isfinite(q).all()
        or np.any(p <= 0)
        or np.any(q <= 0)
        or not np.isclose(p.sum(), 1)
        or not np.isclose(q.sum(), 1)
    ):
        raise ValueError("Positive normalized distributions required")
    ratio = q / p
    return ratio - np.log(ratio) - 1


def worked_b():
    p = np.array([0.8, 0.2])
    q = np.array([0.5, 0.5])
    old = np.array([0.5, 0.5])
    terms = kl_terms(p, q)
    exact = float(np.sum(p * np.log(p / q)))
    assert np.all(terms >= 0) and np.isclose(p @ terms, exact)
    assert not np.isclose(old @ terms, exact)
    assert np.isclose(old @ ((p / old) * terms), exact)
    print("Exact current KL:", exact, "old-law average:", float(old @ terms))


worked_b()
```

## Length and group weighting

An outcome advantage may be assigned to every generated token in a response. Averaging per response and then per group gives responses equal total weight; averaging all token terms together gives longer responses more weight. The reference shows a two-token response with advantage-1 and a four-token response with advantage+1. Their response-average term is zero while their token-average term is one third at unit ratios.

That difference is a modeling decision, not a formatting detail. State how prompts, responses and tokens are weighted, where masks apply, and whether end-of-sequence and truncated positions contribute. Preserve the old policy used to generate the group separately from any reference policy used for regularization.

## Interpretation and practical limits

The lesson computes GRPO-related mechanisms; it does not train a large reasoning model. The paper introduced a family of objectives and supervision choices, while later implementations can alter normalization and loss details. Use the exact declared algorithm and source when comparing runs.

Inspect constant groups, reward scale, response length, support coverage, clipping and actual held-out task behavior. A small positive sampled KL penalty is not a safety certificate, and a high raw reward can reflect exploitation of a flawed judge. Independent evaluation and a reproducible decision packet remain required after policy optimization.


## Six investigations

### 1. Shift all rewards

Add a common constant to 0,1,2,3.

**Expected:** The normalized advantages stay unchanged.

**Hint:** Both the mean and every reward shift together.

### 2. Inspect a constant group

Compare all-zero and all-one reward groups.

**Expected:** Both produce zero relative advantages under the declared rule.

**Hint:** Record the raw rewards separately.

### 3. Change length weighting

Give advantages-1,+1 to responses of length 2,4.

**Expected:** Response average 0; token average 1/3.

**Hint:** Write the two denominators explicitly.

### 4. Check the sampling law

Average case B KL terms under the old uniform policy.

**Expected:** The value differs from current-policy KL.

**Hint:** The identity requires expectation under the numerator policy p.

### 5. Separate value from derivative

Evaluate the centered two-action surrogate at zero log odds.

**Expected:** Its value is 0 while its derivative is 0.5.

**Hint:** Each centered advantage multiplies a different probability derivative.

### 6. Declare algorithm variants

Change standard-deviation correction, epsilon or token reduction.

**Expected:** Record the change as part of the training algorithm.

**Hint:** These settings alter advantage or gradient weighting.

## Primary references

- [GRPO outcome supervision and KL expression](https://arxiv.org/html/2402.03300v3)
- [PPO surrogate context](https://arxiv.org/abs/1707.06347)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
