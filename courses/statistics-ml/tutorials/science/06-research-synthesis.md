# Synthesize comparable effects and retain heterogeneity

Tutorial ID: `statistics-science-006`. Prerequisites: `statistics-008`, `statistics-039`, `statistics-learning-002`. Complete program: [science_06.py](examples/science_06.py).

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

Related chapter: [research synthesis](../../chapters/39-research-synthesis-and-specialized-statistical-methodologies.md). Primary methodological guidance: [Cochrane Handbook, meta-analysis](https://training.cochrane.org/handbook/current/chapter-10).
