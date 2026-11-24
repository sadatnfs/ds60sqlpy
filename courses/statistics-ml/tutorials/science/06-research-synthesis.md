# Synthesize comparable effects and retain heterogeneity

Tutorial ID: `statistics-science-006`. Prerequisites: `statistics-008`, `statistics-039`, `statistics-learning-002`. Complete program: [science_06.py](examples/science_06.py).

## Key terms

- **Inverse-variance weight:** The weight \(1/s_i^2\) given to each study, so more precise estimates count more in the pooled mean.
- **Heterogeneity statistic:** The weighted sum \(Q\) of squared deviations of study estimates from the common-effect mean, used to estimate between-study variance.
- **Between-study variance:** The variance \(\tau^2\) of true effects across studies, estimated here by the DerSimonian-Laird method of moments.
- **Random-effects model:** A synthesis that treats study effects as varying around a mean effect, adding \(\tau^2\) to each sampling variance in the weights.
- **Prediction interval:** A range for the true effect in a comparable future study, wider than the mean interval because it includes between-study variability.

## The study ledger precedes the weighted mean

Five studies estimate a common type of outcome contrast with effects .1,.3,.8,1.0,-.2 and SEs .1,.15,.2,.18,.12. Before combining them, a real ledger must identify populations, interventions, control conditions, horizons, units, estimands, standard-error methods and overlapping samples. Two similarly named outcomes are not necessarily the same measurement.

For ratios, synthesize on a defensible transformed scale such as log risk ratio and transform uncertainty consistently. For continuous effects, changing units by factor c also multiplies SE by c and variance by \(c^2\). The program checks this scale transformation explicitly. Converting only the point estimates would produce meaningless weights.

## Start with a common-effect reference

Inverse-variance weights \(w_i=1/s_i^2\) give \(\widehat\mu=\sum_iw_i\widehat\theta_i/\sum_iw_i\). That reference treats true effects as the same and assumes independent valid study estimates with suitable variance estimates. Shared participants or a shared control create covariance; counting their estimates independently can overstate information.

The heterogeneity statistic is \(Q=\sum_iw_i(\widehat\theta_i-\widehat\mu)^2\). A method-of-moments estimate of between-study variance is

\[
\widehat\tau^2=\max\left(0,\frac{Q-(k-1)}{\sum_iw_i-\sum_iw_i^2/\sum_iw_i}\right).
\]

This DerSimonian-Laird estimate is convenient for a transparent worked calculation but can be unstable with few studies. A zero estimate is not proof of no heterogeneity.

## Estimate a mean and a new-study range

Random-effects weights become \(1/(s_i^2+\widehat\tau^2)\). The example gives mean effect about .379 and between-study variance about .184. It uses a modified Hartung-Knapp scale, bounded below by one, and a t critical value for the mean interval. The resulting interval is approximately [-.233,.992].

An approximate prediction interval additionally includes between-study variability and uses a small-study t reference. Here it is about [-1.157,1.915], much wider. It addresses the effect of a comparable future study, not a new individual outcome. Both intervals remain approximate, especially with only five studies and estimated heterogeneity. The synthetic calculation demonstrates why those targets must not be conflated.

## Change one study and one assumption

Leave-one-out pooled means range roughly .222 to .530. Report which study changes the conclusion and why; do not remove it simply because it disagrees. Differences in population or design may explain heterogeneity and motivate a different target or subgroup synthesis.

Publication selection can bias all observed studies in the same direction. A random-effects model does not repair unseen missing studies, selective endpoints or weak original identification. A sensitivity scenario should make explicit how selection or bias would have to behave to change the decision. Funnel patterns are diagnostics, not a definitive test that publication bias is absent.

**Answered discussion: Is the largest study always the most relevant?** Precision and applicability are different. A huge study in a different population can dominate inverse-variance weighting while poorly representing the decision population. Define inclusion and transport assumptions before choosing the estimator.

## Worked example: from common effect to random effects

The guide quotes the random-effects mean. This snippet computes the intermediate quantities from the five studies in `examples/science_06.py` and shows how the weights move once \(\tau^2\) enters.

```python
import numpy as np

effect = np.array([0.1, 0.3, 0.8, 1.0, -0.2])
se = np.array([0.1, 0.15, 0.2, 0.18, 0.12])
w = 1 / se**2
fixed = np.sum(w * effect) / w.sum()
q = np.sum(w * (effect - fixed) ** 2)
tau2 = max(0.0, (q - 4) / (w.sum() - np.sum(w**2) / w.sum()))
wr = 1 / (se**2 + tau2)
print(f"common-effect mean {fixed:.3f} (se {np.sqrt(1 / w.sum()):.3f}); Q {q:.1f} on 4 df")
print(f"I^2 {max(0, (q - 4) / q):.3f}; tau^2 {tau2:.3f}")
print("study  fixed weight  random weight")
for i in range(5):
    print(f"{i + 1:5d}  {w[i] / w.sum():12.3f}  {wr[i] / wr.sum():13.3f}")
```

```text
common-effect mean 0.224 (se 0.061); Q 41.2 on 4 df
I^2 0.903; tau^2 0.184
study  fixed weight  random weight
    1         0.371          0.214
    2         0.165          0.201
    3         0.093          0.185
    4         0.114          0.192
    5         0.257          0.209
```

The common-effect mean is 0.224 with a standard error of 0.061, which would look decisive on its own. But Q is 41.2 on four degrees of freedom, far beyond its expected value of four, and \(I^2=0.903\) says about 90% of the observed spread is between-study rather than sampling noise. Adding \(\tau^2=0.184\) to every variance flattens the weights: study 1, which carried 0.371 of the common-effect weight because of its small SE, falls to 0.214, while study 3 rises from 0.093 to 0.185. That redistribution toward the larger effects 0.8 and 1.0 is why the random-effects mean, 0.379, sits above the common-effect mean.

## Worked example: a study counted twice

Duplicate reporting is a ledger failure, not a modeling choice. Enter study 4 a second time, as can happen when a conference abstract and its journal article are both included, and recompute.

```python
import numpy as np


def dersimonian_laird(effect, se):
    w = 1 / se**2
    fixed = np.sum(w * effect) / w.sum()
    q = np.sum(w * (effect - fixed) ** 2)
    tau2 = max(0.0, (q - (len(effect) - 1)) / (w.sum() - np.sum(w**2) / w.sum()))
    wr = 1 / (se**2 + tau2)
    return fixed, np.sum(wr * effect) / wr.sum(), np.sqrt(1 / wr.sum())


effect = np.array([0.1, 0.3, 0.8, 1.0, -0.2])
se = np.array([0.1, 0.15, 0.2, 0.18, 0.12])
for name, e, s in (
    ("five independent studies", effect, se),
    ("study 4 entered twice", np.append(effect, 1.0), np.append(se, 0.18)),
):
    fixed, rand, rse = dersimonian_laird(e, s)
    print(f"{name:25s} common {fixed:.3f} random {rand:.3f} (naive se {rse:.3f})")
```

```text
five independent studies  common 0.224 random 0.379 (naive se 0.204)
study 4 entered twice     common 0.303 random 0.483 (naive se 0.204)
```

The common-effect mean moves from 0.224 to 0.303 and the random-effects mean from 0.379 to 0.483, simply because one result of 1.0 now votes twice. The reported standard error stays at 0.204, so nothing in the output warns the reader; the extra apparent heterogeneity happens to offset the extra apparent information here. Only the study ledger, with sample identities and registration numbers, catches this error.

## Diagnostics worth reporting

Give Q, \(I^2\) and \(\tau^2\) together, since \(I^2\) depends on study precision while \(\tau^2\) is on the effect scale. Show the weights under both models. Report leave-one-out results and the prediction interval beside the mean interval. With five studies, consider a restricted maximum likelihood or Paule-Mandel estimate of \(\tau^2\) as a sensitivity check on DerSimonian-Laird.

Related chapter: [research synthesis](../../chapters/39-research-synthesis-and-specialized-statistical-methodologies.md). Primary methodological guidance: [Cochrane Handbook, meta-analysis](https://training.cochrane.org/handbook/current/chapter-10).
