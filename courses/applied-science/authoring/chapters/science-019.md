## Evidence synthesis needs compatible questions

A meta-analysis combines study estimates only after deciding whether their targets, populations, outcomes and designs are compatible enough for the intended synthesis. A common numeric scale does not guarantee a common scientific question. A study ledger should retain eligibility, estimand, effect scale, follow-up, population, design and relevant bias concerns before weights are calculated.

A simple random-effects model writes an observed estimate as \(y_i=\theta_i+\epsilon_i\), with within-study variance \(v_i\), and allows study-specific effects to vary around a mean \(\mu\) with variance \(\tau^2\). The extra variance describes a model for between-study heterogeneity; it does not turn systematic bias into random noise automatically.

This tutorial implements the DerSimonian-Laird method-of-moments estimate as a transparent calculation. It is one estimator, not a universal recommendation, particularly for a small number of studies or difficult variance structures.

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
