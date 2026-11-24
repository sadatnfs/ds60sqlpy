# A ranking score, a policy value and a resource decision

Tutorial ID: `statistics-science-005`. Prerequisites: `statistics-032`, `statistics-017`, `statistics-036`, `statistics-022`. Complete program: [science_05.py](examples/science_05.py).

## Key terms

- **Discounted cumulative gain:** A ranking score that adds each item's gain \(2^{r}-1\) divided by \(\log_2(k+1)\) at rank \(k\).
- **NDCG:** Discounted cumulative gain divided by its value under the ideal ordering, so a perfect ranking scores one.
- **Inverse propensity scoring:** Estimating a new policy's value by averaging logged rewards on rows where the new policy picks the logged action, each divided by the historical probability of that action.
- **Historical policy:** The logging policy that chose the recorded actions; its propensities must be positive wherever the new policy acts.
- **Linear allocation model:** An optimization that maximizes expected benefit under a budget; a fractional solution requires an integer model when partial interventions are meaningless.

## Evaluate order at the query level

Four candidates have relevance grades 3,2,0,1. A proposed ranking returns candidate indices 1,0,3,2. Discounted cumulative gain weights gain \(2^{r}-1\) by \(1/\log_2(k+1)\) at rank k. Dividing by the ideal ordering gives NDCG, approximately .843 in this fixture. Report the gain convention, cutoff, tie handling and query averaging; changing them changes the number.

A query with no relevant candidates needs an explicit convention. Pooling all candidates into one global ranking does not evaluate query-specific retrieval. Relevance judgments can also be missing or biased toward previously exposed items.

## Logged clicks reflect the historical policy

The second fixture has two context types and two actions. The historical policy chooses action one with probability .2 and action zero with probability .8. Matching the action to context gives reward probability .7; a mismatch gives .3. The new policy always matches context, so its known synthetic value is .7.

Inverse propensity scoring uses

\[
\widehat V(\pi)=\frac1n\sum_i
\frac{\mathbf1\{A_i=\pi(X_i)\}Y_i}{p_{\rm log}(A_i\mid X_i)}.
\]

Each observed matching action represents similar opportunities that the logger did not choose. The worked estimate is about .663 with SE .0285. The rare action has larger weights and contributes more variance. The code's proximity to the oracle is checked against a declared sampling tolerance; that does not validate a future logger's propensity records.

If the logger never chooses an action in a relevant context, no finite inverse weight can identify its value from those logs. Estimated propensities, delayed rewards, policy changes and repeated users all need additional care. Evaluating a policy on the same data used to learn it also creates selection bias; this example's policy is specified independently.

## Convert value into constrained allocation

Three interventions have expected benefits 3,1.8,2 and costs 2,1,2. With budget three and each available at most once, the linear allocation model selects the first two, yielding expected benefit 4.8. Here the optimum happens to be integral even though the solver permits fractions. If partial intervention is meaningless and a fractional optimum appears, an integer model is needed rather than rounding without checking feasibility.

Now subtract uncertainty allowances 1.5,.2,.1 from benefits. The conservative objective selects the second and third. Those allowances are declared scenarios, not automatically simultaneous confidence bounds. A scientifically defensible robust decision must explain how uncertainty was estimated and why that protection criterion matches the costs of error.

Fairness, capacity, eligibility and intervention effects can all constrain the decision. High predicted response is not necessarily high incremental benefit. A scoring model that predicts purchases among people who would buy anyway may be useless for choosing incentives.

**Answered discussion: Does higher NDCG prove higher business value?** It supports ordering under the relevance definition. Causal effects of changed exposure, user adaptation and shared-resource interference require additional evaluation. Connect offline ranking evidence to a credible online experiment before claiming incremental impact.

## Worked example: one ranking, four NDCG values

The guide reports an NDCG of about 0.843 for the fixture in `examples/science_05.py`. The same ranking scores differently under other common conventions.

```python
import numpy as np

rel, order = np.array([3, 2, 0, 1]), np.array([1, 0, 3, 2])


def ndcg(gain, k):
    disc = 1 / np.log2(np.arange(2, k + 2))
    got = (gain(rel[order])[:k] * disc).sum()
    ideal = (gain(np.sort(rel)[::-1])[:k] * disc).sum()
    return got / ideal


for name, gain in (("2^r - 1", lambda r: 2.0**r - 1), ("linear r", lambda r: r.astype(float))):
    print(f"gain {name:8s}: NDCG@4={ndcg(gain, 4):.3f} NDCG@2={ndcg(gain, 2):.3f}")
```

```text
gain 2^r - 1 : NDCG@4=0.843 NDCG@2=0.834
gain linear r: NDCG@4=0.922 NDCG@2=0.913
```

With exponential gain the full-list NDCG is 0.843, and truncating at two positions gives 0.834. Linear gain lifts both numbers to 0.922 and 0.913 because swapping the grade-3 and grade-2 candidates is penalized less when grade 3 is not worth seven times grade 1. None of these is wrong; they encode different views of how much a highly relevant item matters. Two teams comparing 0.84 with 0.92 may be using the same ranking and different formulas, so the gain and cutoff belong in every report.

## Worked example: when the rare action becomes rarer

Lower the logging probability of action one from 0.2 to 0.05 and 0.01, keeping the target policy and 2,000 rows, and compare inverse propensity scoring with its self-normalized variant.

```python
import numpy as np

rng = np.random.default_rng(3205)
n = 2000
for rare in (0.2, 0.05, 0.01):
    context = rng.integers(0, 2, n)
    action = rng.binomial(1, rare, n)
    reward = rng.binomial(1, np.where(action == context, 0.7, 0.3))
    prob = np.where(action == 1, rare, 1 - rare)
    match = action == context
    score = match * reward / prob
    snips = score.sum() / (match / prob).sum()
    print(
        f"p(action 1)={rare:.2f}: matches with action 1: {np.sum(match & (action == 1)):3d} "
        f"IPS {score.mean():.3f} (se {score.std(ddof=1) / np.sqrt(n):.3f}) SNIPS {snips:.3f}"
    )
```

```text
p(action 1)=0.20: matches with action 1: 194 IPS 0.663 (se 0.029) SNIPS 0.673
p(action 1)=0.05: matches with action 1:  37 IPS 0.685 (se 0.057) SNIPS 0.775
p(action 1)=0.01: matches with action 1:  14 IPS 0.734 (se 0.141) SNIPS 0.619
```

At 0.2 the logs contain 194 useful matches for action one, and IPS gives 0.663 with standard error 0.029. At 0.05 only 37 remain and the standard error doubles to 0.057. At 0.01 just 14 rows represent half of the target policy, each with weight 100, and the standard error reaches 0.141, so the estimate 0.734 could plausibly be anywhere from about 0.45 to 1.0. Self-normalized IPS trades a small bias for stability, but it too swings, from 0.775 to 0.619, because both depend on the same handful of rows.

## Diagnostics for offline policy evaluation

Report the count and effective sample size of matched rows for each action the new policy takes. Check logged propensities against observed action frequencies by context; a mismatch means the weights are wrong. Compare IPS with a self-normalized or doubly robust estimate. When few rows support a policy decision, plan an online test rather than shipping on the offline number.

Related route: [experimentation](../experimentation/README.md). Sources: [scikit-learn ranking metrics](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html), [SciPy linear programming](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html).
