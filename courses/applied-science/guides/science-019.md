# science-019: Estimated heterogeneity and prediction in research synthesis

Tutorial mode. Stage: advanced. Direct prerequisites: `statistics-039`.

## Evidence synthesis needs compatible questions

A meta-analysis combines study estimates only after deciding whether their targets, populations, outcomes and designs are compatible enough for the intended synthesis. A common numeric scale does not guarantee a common scientific question. A study ledger should retain eligibility, estimand, effect scale, follow-up, population, design and relevant bias concerns before weights are calculated.

A simple random-effects model writes an observed estimate as \(y_i=\theta_i+\epsilon_i\), with within-study variance \(v_i\), and allows study-specific effects to vary around a mean \(\mu\) with variance \(\tau^2\). The extra variance describes a model for between-study heterogeneity; it does not turn systematic bias into random noise automatically.

This tutorial implements the DerSimonian-Laird method-of-moments estimate as a transparent calculation. It is one estimator, not a universal recommendation, particularly for a small number of studies or difficult variance structures.

## Key terms

- **Between-study heterogeneity:** Variation in true effects across studies, summarized by the variance tau^2.
- **Random-effects model:** A synthesis model in which each study estimates its own true effect drawn around an overall mean.
- **DerSimonian-Laird estimator:** The moment estimator of tau^2 from Cochran's Q, truncated at zero.
- **Prediction interval:** An interval for a new study's true effect that adds tau^2 to the uncertainty of the mean, so it is wider than the confidence interval.

## Worked case 1: estimate heterogeneity rather than assume it

The four effects are .1,.2,.7,.9, each with within-study variance .04. Inverse-variance weights give a fixed-effect mean of .475. The heterogeneity statistic and moment denominator are

\[
Q=\sum_i w_i(y_i-\widehat\mu_F)^2,\qquad
C=\sum_iw_i-\frac{\sum_iw_i^2}{\sum_iw_i},\qquad
\widehat\tau^2=\max\left\{0,\frac{Q-(k-1)}{C}\right\}.
\]

Here \(w_i=1/v_i\), and \(k\) is the number of studies. The program estimates a positive heterogeneity variance and then recomputes weights as \(1/(v_i+\widehat\tau^2)\). Because all within-study variances are equal, the mean remains .475, but its uncertainty and the interpretation of a new study differ.

A second exact case sets every observed effect to .2. The moment estimate becomes zero. This checks the nonnegative boundary of the estimator. It does not establish that true heterogeneity is absent whenever an estimate lands on that boundary; limited evidence can leave substantial uncertainty about \(\tau\).

## Worked case 2: distinguish a mean interval from prediction

The code compares an illustrative normal-approximation interval half-width for the mean with one for a new underlying study effect. The latter includes both uncertainty in the estimated mean and the estimated heterogeneity variance, so it is wider in this example.

A precise estimate of the mean can coexist with meaningful variation across settings. A decision about a new setting may therefore need a prediction distribution or a model for effect modifiers, rather than only a confidence interval for the pooled mean. If the new setting is unlike the included studies, even that prediction model may be an extrapolation.

The displayed 1.96 multiplier is an arithmetic illustration. With only four studies, normal approximations and plug-in treatment of heterogeneity can understate uncertainty. Alternative estimators, interval procedures and sensitivity analyses should be considered for actual work. The program does not claim calibrated 95% coverage from this tiny fixture.

## Review the inputs before interpreting the pooled value

Within-study variances may be estimated, effect scales can require transformations, and several results may come from one study. Log ratios, mean differences and standardized effects have different interpretations. Converting them requires appropriate assumptions and uncertainty propagation; averaging numbers merely because they are labeled effect is not a valid synthesis.

Inspect whether heterogeneity plausibly reflects populations, designs, follow-up or measurement choices. A large heterogeneity estimate does not identify which explanation is correct. Meta-regression with few studies can be unstable and can confuse study-level relationships with individual-level effects. Prespecification and substantive reasoning matter alongside the numerical model.

Missing studies and selective outcome reporting can bias the included evidence. A random-effects model alone does not correct that selection. The next tutorial examines dependent estimates and an explicit missing-study sensitivity scenario, while keeping the assumed scenarios separate from observed evidence.

## Answered scientific discussion

**Does a narrow pooled interval mean an intervention works similarly everywhere?** No. It can describe the mean of a heterogeneous collection. The prediction question and effect-modification structure are separate.

**What should accompany the summary estimate?** Provide the study ledger, effect transformations, variance assumptions, heterogeneity method, interval method, influence checks and scope of transport to a new setting. The synthetic example verifies the mechanics of an estimated-heterogeneity workflow; it does not replace study appraisal or domain expertise.

## Worked example: DerSimonian-Laird on five studies

```python
import numpy as np
from scipy import stats

y = np.array([0.10, 0.30, 0.35, 0.65, 0.45])
v = np.array([0.010, 0.020, 0.015, 0.025, 0.010])
w = 1 / v
fixed = w @ y / w.sum()
Q = w @ (y - fixed) ** 2
k = len(y)
tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w**2).sum() / w.sum()))
wr = 1 / (v + tau2)
mu = wr @ y / wr.sum()
se = np.sqrt(1 / wr.sum())
z = stats.norm.ppf(0.975)
t = stats.t.ppf(0.975, k - 2)
half_pi = t * np.sqrt(tau2 + se**2)
print(f"fixed {fixed:.4f}, Q {Q:.3f}, I2 {max(0, (Q - (k - 1)) / Q):.3f}, tau2 {tau2:.4f}")
print(f"random-effects mean {mu:.4f}, 95% CI [{mu - z * se:.4f}, {mu + z * se:.4f}]")
print(f"95% prediction interval [{mu - half_pi:.4f}, {mu + half_pi:.4f}]")
```

Observed output:

```text
fixed 0.3346, Q 10.890, I2 0.633, tau2 0.0249
random-effects mean 0.3548, 95% CI [0.1793, 0.5304]
95% prediction interval [-0.2227, 0.9323]
```

The inverse-variance weights pull the fixed-effect mean to 0.3346. Cochran's \(Q=10.890\) with \(k-1=4\) degrees of freedom is well above 4, so the studies disagree more than sampling error explains; \(I^2=0.633\) says 63 percent of the observed spread is between-study variation. The method-of-moments estimate \(\tau^2=0.0249\), a between-study standard deviation of about 0.158, is added to every study's variance. That flattens the weights and shifts the mean to 0.3548, with a 95 percent confidence interval of [0.179, 0.530]. That interval describes the average effect across studies like these. A new study's true effect is far less certain: the prediction interval adds \(\tau^2\) and uses a \(t\) quantile with \(k-2=3\) degrees of freedom (3.18 rather than 1.96), producing [\(-0.223\), 0.932]. A program team expecting a positive result in a new site should read the second interval: it includes harm. With only five studies, \(\tau^2\) itself is very uncertain.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def dl_meta(effect, variance):
    y, v = np.asarray(effect, float), np.asarray(variance, float)
    w = 1 / v
    fixed = float(w @ y / w.sum())
    q = float(w @ ((y - fixed) ** 2))
    c = float(w.sum() - (w @ w) / w.sum())
    tau2 = max(0.0, (q - (len(y) - 1)) / c)
    random_w = 1 / (v + tau2)
    mean = float(random_w @ y / random_w.sum())
    se = float(np.sqrt(1 / random_w.sum()))
    return dict(mean=mean, se=se, tau2=tau2, q=q, weights=random_w)


def run_cases():
    y = np.array([0.1, 0.2, 0.7, 0.9])
    v = np.array([0.04, 0.04, 0.04, 0.04])
    r = dl_meta(y, v)
    assert np.isclose(r["mean"], 0.475) and r["tau2"] > 0
    confidence = 1.96 * r["se"]
    prediction = 1.96 * np.sqrt(r["se"] ** 2 + r["tau2"])
    assert prediction > confidence
    equal = dl_meta([0.2, 0.2, 0.2], [0.04, 0.04, 0.04])
    assert equal["tau2"] == 0
    return dict(
        mean=r["mean"],
        tau2=r["tau2"],
        confidence_halfwidth=float(confidence),
        prediction_halfwidth=float(prediction),
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    labels = ["Study1", "Study2", "Study3", "Study4"]
    values = [0.1, 0.2, 0.7, 0.9]
    fig = go.Figure(
        go.Scatter(
            x=values, y=labels, mode="markers", error_x=dict(type="constant", value=1.96 * 0.2)
        )
    )
    fig.add_vline(x=evidence["mean"], line_dash="dash")
    fig.update_layout(
        title="Observed effects and illustrative within-study intervals",
        xaxis_title="Additive effect",
        meta=dict(
            description="Four synthetic effects with common standard error 0.2; dashed line marks pooled mean 0.475. Intervals illustrate a normal approximation.",
            table=dict(
                columns=["Study", "Effect", "Standard error"],
                rows=[[label, value, 0.2] for label, value in zip(labels, values, strict=True)],
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-019 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
```

## Primary references

- [Cochrane handbook, analysis and meta-analysis](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-10)
