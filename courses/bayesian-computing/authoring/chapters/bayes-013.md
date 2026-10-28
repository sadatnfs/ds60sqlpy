## Posterior geometry reflects the information in the design

Correlated predictors can make separate coefficients weakly identified even when a prediction contrast is well determined. A posterior describes that joint uncertainty. Reporting independent marginal summaries without their covariance can conceal the geometry that matters for predictions and scientific interpretation.

The synthetic design has an intercept and two nearly identical predictor columns. Their true generating slopes are two and minus 1.5, but the observed design strongly emphasizes their sum. The model uses independent standard-normal coefficient priors and known observation standard deviation .1. Those priors regularize weak directions; they are part of the model, not an invisible numerical repair.

## Worked case 1: derive the full normal posterior

With prior covariance I, design X and known observation variance \(\sigma^2\), the posterior covariance and mean are

\[
V=(I+X^{\mathsf T}X/\sigma^2)^{-1},\qquad
m=VX^{\mathsf T}y/\sigma^2.
\]

The program computes this exact conjugate oracle and fits the same model with actual PyMC sampling. It reports both coefficient means and checks broad numerical agreement. The short chains can have noticeable Monte Carlo error along a weakly identified direction, so close agreement of every printed digit is neither required nor claimed.

The posterior means of the individual slopes need not equal the data-generating slopes. The likelihood does not provide strong separate information, and the prior pulls the weak direction toward its preferred range. A correct posterior can therefore differ from a known generating parameter in one finite dataset without being a computational failure.

An independent analytic oracle is especially useful here. It separates posterior uncertainty and regularization from sampling error. If a sampled mean differs, examine Monte Carlo precision and geometry before assuming that a different number means a different statistical model.

## Worked case 2: a stable contrast inside unstable coefficients

The posterior covariance shows strong negative dependence between the two slopes. The variance of their sum is

\[
\operatorname{Var}(\beta_1+\beta_2\mid y)
=V_{11}+V_{22}+2V_{12}.
\]

Because the covariance term is negative, the sum can be much more precise than either coefficient alone. The code calculates that contrast variance from the analytic matrix and checks that it is smaller than both individual variances.

Ignoring covariance would overstate the uncertainty of this particular sum. For another contrast, ignoring covariance could understate uncertainty. The correct calculation follows the joint distribution and the target function, not a rule to add marginal interval widths or variances blindly.

The contrast is well supported near the observed relationship between predictors. Predicting a setting where one predictor changes independently of the other can require extrapolation along a weak direction. Good interpolation inside the training manifold does not establish reliable intervention or transport behavior outside it.

## Priors, scaling and computation

Coefficient priors have units. A standard-normal prior on a predictor measured in millimeters differs from the same numerical prior after measuring it in meters. Standardization can help express prior information and improve geometry, but its fitted transformation must be included in the prediction and evaluation procedure.

Strong posterior correlation can make numerical exploration inefficient. Reparameterization, orthogonal designs or an adapted metric may help. Those computational choices should preserve the intended target density. Changing the prior merely to obtain easier diagnostics changes the statistical model and should be reported as such.

Review diagnostic quantities for both individual coefficients and important contrasts. A sampler may estimate a stable prediction well while poorly characterizing a broad, scientifically relevant direction. Effective sample size and Monte Carlo error are quantity-specific, and a single average across parameters can conceal the important failure.

## Answered scientific discussion

**Does a tight posterior prediction imply precise feature effects?** No. Several coefficient combinations can generate nearly identical predictions over the observed feature relationship. The example demonstrates that distinction through an exact covariance calculation.

**Should the coefficient with the larger posterior mean be called more important?** That ignores scale, covariance, causal meaning and the target prediction population. Define the desired contrast or decision and evaluate it directly, with its uncertainty and assumptions.
