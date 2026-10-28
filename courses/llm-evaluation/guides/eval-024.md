# eval-024: Off-policy evaluation and the final alignment audit

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-016`, `eval-020`, `eval-022`, `eval-023`.

Evaluate a changed finite policy from logged actions with explicit propensity/support assumptions, and connect the result to an independent alignment decision.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-024`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## A trained policy changes the observed distribution

A deployed policy determines which responses or actions are observed. If a new policy would choose different actions, its value cannot generally be estimated by averaging the old policy's observed rewards. Off-policy evaluation uses information about the logging process and, optionally, an outcome model to estimate a new policy's value under stated assumptions.

For context \(X\), logged action \(A\), observed reward \(R\), behavior probability \(b(A\mid X)\) and target policy \(\pi(A\mid X)\), the importance weight is \(w=\pi(A\mid X)/b(A\mid X)\). An ordinary importance estimate averages \(wR\). A self-normalized estimate divides the weighted reward sum by the weight sum; it can have a different finite-sample bias/variance tradeoff.

With an outcome estimate \(\widehat q(x,a)\), a contextual-bandit doubly robust value uses

\[
\widehat V_{DR}=\frac1n\sum_i\left[\sum_a\pi(a\mid X_i)\widehat q(X_i,a)
+\frac{\pi(A_i\mid X_i)}{b(A_i\mid X_i)}
\left(R_i-\widehat q(X_i,A_i)\right)\right].
\]

This unit treats one-step contextual decisions. Long trajectories require additional treatment of sequential probabilities and dependence; multiplying many ratios can create severe variance. The name doubly robust does not remove overlap, consistency, correct target-population weighting or appropriate nuisance-fitting assumptions.

## Worked case A: reconstruct a known finite value

Two contexts occur equally often. Their behavior policies are[0.8,0.2] and[0.3,0.7], while the target policies are[0.5,0.5] and[0.8,0.2]. The authored reward table favors action 0 in the first context and action 1 in the second. Exact target value is 0.35. A constructed log with action counts matching the behavior proportions gives that same importance estimate.

```python
import numpy as np


def policies(behavior, target):
    b = np.asarray(behavior, float)
    p = np.asarray(target, float)
    if (
        b.shape != p.shape
        or b.ndim != 2
        or np.any(b < 0)
        or np.any(p < 0)
        or not np.isfinite(b).all()
        or not np.isfinite(p).all()
        or not np.allclose(b.sum(1), 1)
        or not np.allclose(p.sum(1), 1)
    ):
        raise ValueError("Normalized finite contextual policies required")
    if np.any((p > 0) & (b == 0)):
        raise ValueError("Target has unsupported actions")
    return b, p


def estimate(log, behavior, target, outcome_model):
    b, p = policies(behavior, target)
    q = np.asarray(outcome_model, float)
    if q.shape != b.shape or not np.isfinite(q).all() or not log:
        raise ValueError("Outcome model and nonempty log required")
    weights = []
    weighted = []
    dr = []
    for context, action, reward in log:
        if (
            type(context) is not int
            or type(action) is not int
            or not 0 <= context < b.shape[0]
            or not 0 <= action < b.shape[1]
            or not np.isfinite(reward)
        ):
            raise ValueError("Malformed logged event")
        if b[context, action] <= 0:
            raise ValueError("Impossible logged action")
        weight = p[context, action] / b[context, action]
        weights.append(weight)
        weighted.append(weight * reward)
        dr.append(p[context] @ q[context] + weight * (reward - q[context, action]))
    w = np.asarray(weights)
    if w.sum() <= 0:
        raise ValueError("No observed target weight")
    return {
        "ips": float(np.mean(weighted)),
        "snis": float(np.sum(weighted) / w.sum()),
        "dr": float(np.mean(dr)),
        "weight_ess": float(w.sum() ** 2 / np.sum(w * w)),
    }


def fixture(counts):
    reward = np.array([[1.0, 0.0], [0.0, 1.0]])
    return [
        (s, a, float(reward[s, a])) for s in range(2) for a in range(2) for _ in range(counts[s][a])
    ]


def worked_a():
    behavior = [[0.8, 0.2], [0.3, 0.7]]
    target = [[0.5, 0.5], [0.8, 0.2]]
    reward = [[1.0, 0.0], [0.0, 1.0]]
    result = estimate(fixture([[16, 4], [6, 14]]), behavior, target, reward)
    assert (
        np.isclose(result["ips"], 0.35)
        and np.isclose(result["snis"], 0.35)
        and np.isclose(result["dr"], 0.35)
    )
    print("Constructed balanced log:", result)


worked_a()
```

## Worked case B: finite logs and an outcome model

A second possible log has different realized action counts while retaining the same behavior propensities. Ordinary and self-normalized estimates differ. With the known synthetic reward table as its outcome model, the doubly robust expression returns 0.35 because its residuals are zero and contexts remain balanced. In a real study, that counterfactual reward table is not known; it must be learned or otherwise justified and independently assessed.

```python
import numpy as np


def policies(behavior, target):
    b = np.asarray(behavior, float)
    p = np.asarray(target, float)
    if (
        b.shape != p.shape
        or b.ndim != 2
        or np.any(b < 0)
        or np.any(p < 0)
        or not np.isfinite(b).all()
        or not np.isfinite(p).all()
        or not np.allclose(b.sum(1), 1)
        or not np.allclose(p.sum(1), 1)
    ):
        raise ValueError("Normalized finite contextual policies required")
    if np.any((p > 0) & (b == 0)):
        raise ValueError("Target has unsupported actions")
    return b, p


def estimate(log, behavior, target, outcome_model):
    b, p = policies(behavior, target)
    q = np.asarray(outcome_model, float)
    if q.shape != b.shape or not np.isfinite(q).all() or not log:
        raise ValueError("Outcome model and nonempty log required")
    weights = []
    weighted = []
    dr = []
    for context, action, reward in log:
        if (
            type(context) is not int
            or type(action) is not int
            or not 0 <= context < b.shape[0]
            or not 0 <= action < b.shape[1]
            or not np.isfinite(reward)
        ):
            raise ValueError("Malformed logged event")
        if b[context, action] <= 0:
            raise ValueError("Impossible logged action")
        weight = p[context, action] / b[context, action]
        weights.append(weight)
        weighted.append(weight * reward)
        dr.append(p[context] @ q[context] + weight * (reward - q[context, action]))
    w = np.asarray(weights)
    if w.sum() <= 0:
        raise ValueError("No observed target weight")
    return {
        "ips": float(np.mean(weighted)),
        "snis": float(np.sum(weighted) / w.sum()),
        "dr": float(np.mean(dr)),
        "weight_ess": float(w.sum() ** 2 / np.sum(w * w)),
    }


def fixture(counts):
    reward = np.array([[1.0, 0.0], [0.0, 1.0]])
    return [
        (s, a, float(reward[s, a])) for s in range(2) for a in range(2) for _ in range(counts[s][a])
    ]


def worked_b():
    behavior = [[0.8, 0.2], [0.3, 0.7]]
    target = [[0.5, 0.5], [0.8, 0.2]]
    reward = [[1.0, 0.0], [0.0, 1.0]]
    log = fixture([[18, 2], [10, 10]])
    result = estimate(log, behavior, target, reward)
    assert not np.isclose(result["ips"], result["snis"])
    assert np.isclose(result["dr"], 0.35)
    assert np.isclose(estimate(log, behavior, target, [[0, 0], [0, 0]])["dr"], result["ips"])
    assert result["weight_ess"] < len(log)
    print("Finite-log estimates:", result, "decision: more independent evidence required")


worked_b()
```

## Support and data provenance

Every action assigned positive target probability needs positive behavior probability in the relevant context. A missing action cannot be recovered by a finite inverse weight. The helper rejects that support failure. Very small propensities can also make estimates unstable even when support is technically positive. Report weight concentration and sensitivity, and do not hide large weights by clipping without explaining the changed estimator.

The conditional reward law must also remain applicable under the target policy. A policy that changes service congestion, future user behavior or tool availability can violate a one-step transfer assumption even when the logged ratios are correct.

Logged probabilities must describe the policy that actually generated each action. An empirical action frequency is not automatically the correct propensity when the logging policy used private context, adaptive routing or changing versions. Retain behavior-policy identity, available context, action probability, outcome availability and eligibility. If nuisance models are estimated from the same data, consider appropriate sample separation or cross-fitting rather than assuming a fitted residual correction is automatically unbiased.

## Close the alignment loop

Keep preference-training reward distinct from the task utility used for final evaluation. A policy can optimize a proxy while making the independently defined task worse, as the earlier PyTorch counterexample showed. Assess the frozen policy using new task families, valid uncertainty, coverage and critical-policy conditions. Evaluating many candidate policies on the same log and choosing the best consumes that log for selection.

The authored log makes a known answer available for mathematical checking. Its point estimates do not justify a real release or a confidence claim for an external population. A final memo should state the target policy and population, logging and support assumptions, outcome definition, estimator, uncertainty procedure, selection history and unresolved risks. Where those requirements are unmet, the correct result can be more evidence required.


## Six investigations

### 1. Recover behavior value

Set the target policy equal to the behavior policy in case A.

**Expected:** All weights are 1 and the mean observed reward is 0.75.

**Hint:** The ratio cancels when the policies match.

### 2. Evaluate a useful target

Use target rows[0.9,0.1] and[0.1,0.9] with the exact synthetic outcome table.

**Expected:** The target value is 0.9.

**Hint:** Average the target reward over the two equally weighted contexts.

### 3. Remove behavior support

Give an action zero behavior probability but positive target probability.

**Expected:** The helper rejects the target.

**Hint:** No finite importance ratio supplies an unobserved action outcome.

### 4. Use a zero outcome model

Set every outcome-model prediction to zero.

**Expected:** The doubly robust expression reduces to ordinary importance sampling.

**Hint:** Its direct-model term vanishes.

### 5. Interpret self-normalization

Compare IPS and SNIS in case B.

**Expected:** Their finite-sample values differ.

**Hint:** Their denominators are n and the observed weight sum.

### 6. Audit the final claim

Choose a policy after inspecting many estimates from the same log.

**Expected:** Treat that log as selection evidence and obtain a protected final assessment.

**Hint:** The holdout rule still applies after policy optimization.

## Primary references

- [Doubly robust off-policy evaluation](https://arxiv.org/abs/1511.03722)
- [Existing ranking and policy evaluation](../../../courses/statistics-ml/tutorials/science/05-ranking-policy-and-allocation.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
