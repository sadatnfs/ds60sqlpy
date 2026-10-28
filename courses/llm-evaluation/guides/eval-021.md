# eval-021: Temporal credit, GAE and the PPO clipped objective

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-019`, `torch-004`.

Compute temporal advantages with correct episode boundaries and inspect PPO clipping for both positive and negative advantages.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-021`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Keep the three policies and states distinct

PPO collects trajectories using an old policy and then optimizes a surrogate using those stored actions and log probabilities. The old policy is a snapshot of the collector. A separate reference policy may define a KL regularization target. The current policy changes during optimization. Confusing these roles changes the ratios and the learning problem.

A value function estimates expected future return under a declared policy and discount. A rollout with \(T\) steps needs \(T\) rewards and terminal flags plus \(T+1\) value estimates, including the final bootstrap value. Both discount and trace factors are in \([0,1]\). For reward \(r_t\), value estimate \(V(s_t)\), discount \(\gamma\) and a true terminal indicator \(d_t\), the temporal residual is

\[
\delta_t=r_t+\gamma(1-d_t)V(s_{t+1})-V(s_t).
\]

Generalized advantage estimation combines residuals using a trace factor \(\lambda\). In the finite rollout below, work backwards with \(\widehat A_t=\delta_t+\gamma\lambda(1-d_t)\widehat A_{t+1}\). A true terminal state removes bootstrapping. A rollout cut short by a time limit may still need the final value estimate. A separate episode boundary must also stop a trace from leaking into a new episode.

## Worked case A: terminal versus truncated trajectories

The authored two-step trajectory has rewards 1 and 2, values 0.5,0.4,0.2, gamma 0.9 and lambda 0.8. With a true final terminal, its advantages are 2.012 and 1.6. Treating the final step as a truncated continuation uses the final value and changes them to 2.1416 and 1.78. The helper accepts one contiguous rollout; it does not concatenate unrelated episodes.

```python
import numpy as np


def gae(rewards, values, terminals, gamma=0.9, lam=0.8):
    r = np.asarray(rewards, float)
    v = np.asarray(values, float)
    d = np.asarray(terminals)
    if (
        d.dtype.kind != "b"
        or r.ndim != 1
        or v.shape != (len(r) + 1,)
        or d.shape != r.shape
        or not 0 <= gamma <= 1
        or not 0 <= lam <= 1
    ):
        raise ValueError("One aligned rollout required")
    if not np.isfinite(r).all() or not np.isfinite(v).all():
        raise ValueError("Finite rewards and values required")
    result = np.zeros_like(r)
    carry = 0.0
    for t in reversed(range(len(r))):
        residual = r[t] + gamma * (not d[t]) * v[t + 1] - v[t]
        carry = residual + gamma * lam * (not d[t]) * carry
        result[t] = carry
    return result


def clipped_terms(ratio, advantage, epsilon=0.2):
    ratio = np.asarray(ratio, float)
    advantage = np.asarray(advantage, float)
    if (
        ratio.shape != advantage.shape
        or np.any(ratio < 0)
        or not np.isfinite(ratio).all()
        or not np.isfinite(advantage).all()
        or not 0 < epsilon < 1
    ):
        raise ValueError("Invalid PPO arrays")
    return np.minimum(ratio * advantage, np.clip(ratio, 1 - epsilon, 1 + epsilon) * advantage)


def kl(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    return float(np.sum(p * np.log(p / q)))


def worked_a():
    terminal = gae([1, 2], [0.5, 0.4, 0.2], [False, True])
    truncated = gae([1, 2], [0.5, 0.4, 0.2], [False, False])
    np.testing.assert_allclose(terminal, [2.012, 1.6])
    np.testing.assert_allclose(truncated, [2.1416, 1.78])
    print("Terminal advantages:", terminal.tolist(), "truncated:", truncated.tolist())


worked_a()
```

## Worked case B: clipping depends on the advantage sign

For a collected action, the probability ratio is \(\rho_t=\pi_\theta(a_t\mid s_t)/\pi_{\mathrm{old}}(a_t\mid s_t)\). PPO's clipped maximization term is

\[
\min\left(\rho_t\widehat A_t,
\operatorname{clip}(\rho_t,1-\epsilon,1+\epsilon)\widehat A_t\right).
\]

With positive advantage, the favorable increase is clipped above the upper ratio boundary. With negative advantage, the favorable decrease is clipped below the lower boundary. A bad-direction change can still be penalized outside the interval. Multiplying a clipped ratio by advantage without taking the minimum is not the same objective.

```python
import numpy as np


def gae(rewards, values, terminals, gamma=0.9, lam=0.8):
    r = np.asarray(rewards, float)
    v = np.asarray(values, float)
    d = np.asarray(terminals)
    if (
        d.dtype.kind != "b"
        or r.ndim != 1
        or v.shape != (len(r) + 1,)
        or d.shape != r.shape
        or not 0 <= gamma <= 1
        or not 0 <= lam <= 1
    ):
        raise ValueError("One aligned rollout required")
    if not np.isfinite(r).all() or not np.isfinite(v).all():
        raise ValueError("Finite rewards and values required")
    result = np.zeros_like(r)
    carry = 0.0
    for t in reversed(range(len(r))):
        residual = r[t] + gamma * (not d[t]) * v[t + 1] - v[t]
        carry = residual + gamma * lam * (not d[t]) * carry
        result[t] = carry
    return result


def clipped_terms(ratio, advantage, epsilon=0.2):
    ratio = np.asarray(ratio, float)
    advantage = np.asarray(advantage, float)
    if (
        ratio.shape != advantage.shape
        or np.any(ratio < 0)
        or not np.isfinite(ratio).all()
        or not np.isfinite(advantage).all()
        or not 0 < epsilon < 1
    ):
        raise ValueError("Invalid PPO arrays")
    return np.minimum(ratio * advantage, np.clip(ratio, 1 - epsilon, 1 + epsilon) * advantage)


def kl(p, q):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    return float(np.sum(p * np.log(p / q)))


def worked_b():
    result = clipped_terms([1.5, 0.5, 0.5, 1.5], [1, 1, -1, -1])
    np.testing.assert_allclose(result, [1.2, 0.5, -0.8, -1.5])
    old = np.array([0.5, 0.49, 0.01])
    p = np.array([0.6, 0.39, 0.01])
    other = np.array([0.6, 0.01, 0.39])
    assert np.isclose(
        clipped_terms([p[0] / old[0]], [1])[0], clipped_terms([other[0] / old[0]], [1])[0]
    )
    assert kl(other, old) > kl(p, old)
    print("Clipped terms:", result.tolist(), "different full KL:", kl(p, old), kl(other, old))


worked_b()
```

## What clipping does not guarantee

The surrogate is not a hard constraint that every probability ratio stays within the interval. An optimizer step can overshoot a boundary, and parameters shared across actions can move unobserved actions. The reference constructs two valid policies with the same probability for the one observed action but very different probabilities elsewhere. Their sampled clipped terms agree while their full KL divergences differ.

Monitor actual divergence, entropy, clipping frequency, value error and task reward rather than assuming the clipping parameter supplies a universal trust-region guarantee. Old log probabilities and computed advantages should be treated as fixed data during the policy update. Allowing gradients through the old snapshot or an unintended value baseline changes the optimization.

## Connect to language-model training

Autoregressive responses are trajectories with a declared stopping rule. A final response-level reward can be distributed through value estimates and temporal advantages, while token masks determine which positions contribute. Variable lengths, padding, truncation and rewards assigned at intermediate steps require careful accounting. A copied generic PPO loop without these contracts is not a complete language-model training implementation.

The code demonstrates exact advantage arithmetic and surrogate behavior on small arrays. It does not collect language-model rollouts. The next unit performs actual PyTorch updates on a finite contextual policy, keeping the limitations explicit. The comparison with an independently evaluated utility remains necessary even when the optimizer and gradients are correct.


## Six investigations

### 1. Remove the trace

Set lambda 0 in case A.

**Expected:** Advantages reduce to residuals 0.86 and 1.6.

**Hint:** No later residual receives positive trace weight.

### 2. Terminate the first step

Mark both steps terminal in the arithmetic helper.

**Expected:** The first result is 0.5 and does not inherit the second residual.

**Hint:** A terminal boundary cuts both bootstrap and trace.

### 3. Positive advantage outside the interval

Use ratio 1.5 and advantage 1 with epsilon 0.2.

**Expected:** The clipped term is 1.2.

**Hint:** Take the minimum of the two products.

### 4. Negative advantage outside the interval

Use ratio 1.5 and advantage-1.

**Expected:** The term is -1.5, not-1.2.

**Hint:** Multiplication reverses the relevant ordering.

### 5. Check an unobserved action

Compare the two policies in case B.

**Expected:** Their sampled terms agree while global KL differs.

**Hint:** Only action 0 appears in the hypothetical sampled batch.

### 6. Freeze rollout quantities

Explain which tensors should be detached during policy optimization.

**Expected:** Stored old log probabilities and computed advantages are fixed.

**Hint:** The old collector and reference policy have different roles.

## Primary references

- [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)
- [Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
