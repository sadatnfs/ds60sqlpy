# First paired package studies

The first runner covers four existing model families. Each shard selects one
replication and two changed scenarios. Both backends receive the same retained
fixture bytes; the runner checks the returned objective against an independent
analytic expression and checks first-order stationarity in common scientific
coordinates. A failed optimizer is retained as a failed fit. An unclassified
execution error interrupts the shard rather than becoming a favorable result.

## sim-001: Gaussian means and unequal weights

Generate 48 independent observations from \(N(1.2,0.7^2)\). The first scenario
uses equal weights; the second uses the repeated pattern0,1,2,3 on the same
observations. The weighted objective has solutions

\[
 \hat\mu=\frac{\sum_iw_i y_i}{W},\qquad
 \hat\sigma^2=\frac{\sum_iw_i(y_i-\hat\mu)^2}{W},\quad W=\sum_iw_i.
\]

These are computational weighted-likelihood targets. In the generator, each row
remains one independent original observation. The unequal weights do not create
independent copies of that observation. Consequently the sampling variance of
the weighted mean is \(\sigma^2\sum_iw_i^2/W^2\), not automatically
\(\sigma^2/W\). Here \(W=72\) but the corresponding effective count is about30.86.
That changed case exposes a common confusion between objective weights and an
independence assumption.

The initial runner checks fits and response-free future predictions. Its current
future intervals are plug-in observation intervals, not parameter confidence
intervals. A later coverage extension can compare the competing mean-SE formulas
using the known generating scale as an oracle. Do not interpret the eight-rep
reference smoke as evidence that either interval has nominal coverage.

A useful additional run changes partition count while preserving the same
fixture. It must not change the global objective definition, weight denominator
or number of times a penalty is added. Small floating summation differences are
reported through numerical tolerances and source-bound receipts.

## sim-002: what all-coordinate L2 does

Generate \(Y=\beta_0+1.2X+\epsilon\) with \(X\) uniform on[-1,1]. Compare a
centered scenario with \(\beta_0=0,\sigma=1\) to an offset/scale scenario with
\(\beta_0=4,\sigma=2\), using common random numbers. Each dataset is fit with
lambda0 and lambda4, fixed in advance.

The package option penalizes \((\beta_0,\beta_1,\log\sigma)\). Its objective and
score are checked including that penalty once. The second scenario is deliberately
poorly centered for that implicit prior. Shrinking the intercept and noise scale
is an actual modeling choice; it must not be mistaken for conventional slope-only
ridge. Held-out outcomes score the predeclared methods and do not choose lambda.

Inspect fitted coordinates, objective, projected score and future marginal log
score. A lower training data loss and a lower penalized objective are different
comparisons. Do not rank an unpenalized fit against a penalized fit using an
objective that includes a penalty for only one method. For common predictive
assessment, use the same held-out response density and target for both.

## sim-006: nonlinear growth and limited observation windows

The original native model is

\[
 m(t)=b+A(1-e^{-rt}),\qquad A,r>0,
\]

with Gaussian observation noise. Its optimized coordinates are
\((b,\log A,\log r,\log\sigma)\). The current Torch decay model represents the
same curve as \(ae^{-rt}+c\), using \(a=-A\) and \(c=b+A\). The runner maps
coordinates and keeps the amplitude negative so the curve family agrees.

This comparison is unpenalized. Isotropic L2 in those two coordinate systems is
not the same prior, so reusing lambda would change the target. The runner refuses
that shortcut.

The first scenario observes times from0 to4. The second observes only a short
prefix ending at0.6, then predicts beyond it. On a short prefix,
\(A(1-e^{-rt})\approx Art\): many amplitude/rate pairs have similar likelihoods.
Small gradients or close in-sample curves do not imply identified asymptotes or
reliable extrapolation. Compare future error, active bounds, objective differences
and alternative starts before calling different fitted parameters a backend bug.

## sim-008: pooling and prediction conditioning

Generate eight independent groups under a Gaussian random-intercept model. One
scenario gives each group six observations; the other gives sizes3 through10.
The group effects and observation-noise streams are shared between scenarios
where their indices overlap. Complete groups remain intact when distributed.

The two packages fit the same exact marginal Gaussian target. Native forecasting
can request an observed group's conditional moments or a new group's prior-
integrated moments. The current Torch public target supplies the new-group mean.
The runner checks that actual target and separately labels the known-group means
and variances derived from fitted Torch parameters as mathematical references.
It does not claim a history-aware Torch forecast API exists.

Future metrics are split into known and unseen groups. Pointwise coverage and
coverage of the whole two-step path are both reported. These plug-in calculations
exclude population-parameter uncertainty. Parameter bootstrap and posterior-
predictive studies need the additional operations described in the API-gap plan.

## Reading the output

`status="completed"` means every planned scenario/method in that shard was
attempted. It does not mean every fit converged. Check `fit_failures` and each
record's `status`. A fit is accepted only when the backend status and the
independent common-coordinate projected score meet the declared criterion.
The source, fixture, package and runtime identities are retained.

The paired comparison reports parameter/objective differences and both prediction
scopes. It does not automatically turn weakly identified nonlinear differences
into a software regression. Monte Carlo aggregation keeps the failure denominator,
computes bias among returned estimates explicitly, and averages forecast metrics
within each independent generated dataset before calculating MCSE.

**Interview discussion:** Increasing Spark partitions is a computational choice;
changing the likelihood's independence unit is a statistical choice. A shared
model, independently fitted group models, conditional forecasts, and forecasts
for unseen latent groups answer different questions even when their code looks
similar.
