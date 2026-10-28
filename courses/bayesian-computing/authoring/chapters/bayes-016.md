## A Gaussian process is a joint model over function values

A Gaussian process specifies a mean function and covariance kernel for collections of latent function values. For Gaussian observation noise and fixed kernel hyperparameters, conditional predictions can be calculated with linear algebra. This provides an exact reference for a library implementation and a clear distinction between conditional and fully integrated uncertainty.

The example uses six input positions on the unit interval, a sinusoidal synthetic signal, an exponentiated-quadratic kernel with fixed length scale .25, and observation standard deviation .1. Three new input positions receive latent-function predictions. Hyperparameters are deliberately fixed; the program does not claim to have learned their uncertainty.

## Worked case 1: match PyMC with a direct covariance calculation

Let \(K\) be the training covariance including observation noise, \(K_*\) the train-to-test covariance and \(K_{**}\) the test covariance. The conditional mean and covariance are

\[
m_*=K_*^{\mathsf T}K^{-1}y,\qquad
V_*=K_{**}-K_*^{\mathsf T}K^{-1}K_*.
\]

The implementation uses solves rather than explicitly forming an inverse for those predictions. It compares its results with actual `pm.gp.Marginal.predict` output under the declared API and parameters.

The prepared implementation adds numerical jitter to stabilize covariance calculations. The program declares that jitter explicitly and includes the same small diagonal perturbation in both its training and latent predictive covariance oracle. This detail matters: an allegedly independent comparison can fail because it compared slightly different numerical models rather than exposing a library bug. Jitter should be recorded, not hidden by an unexplained looser tolerance.

The result is a latent-function prediction. Including future observation noise would require adding the relevant noise covariance and asking the library for the corresponding prediction type. A narrow latent interval should not be labeled as an interval for a noisy future observation.

## Worked case 2: integrate over uncertain hyperparameters

A second exact calculation uses two hypothetical conditional predictive distributions with means zero and two and variance .1 each. Averaging their conditional variances gives .1, but the total mixture variance is 1.1 because the conditional means differ.

The law of total variance is

\[
\operatorname{Var}(Y\mid y)=
\mathbb E[\operatorname{Var}(Y\mid\theta,y)\mid y]
+\operatorname{Var}(\mathbb E[Y\mid\theta,y]\mid y).
\]

This illustrates the uncertainty that can be omitted by conditioning on a single length scale, amplitude or noise estimate. It is not a posterior over the actual GP hyperparameters in the first case. The example separates the general identity from a computation it has not performed.

A full Bayesian GP workflow would sample or otherwise integrate over hyperparameters and combine the resulting conditional predictions consistently. That can be computationally demanding and sensitive to identifiability. A plug-in estimate may still be useful, but its uncertainty interpretation should remain explicit.

## Model choice, scaling and validation

Kernel choice encodes assumptions about smoothness and dependence. Input units affect the meaning of a length scale; a prior appropriate for normalized time is not automatically appropriate after changing to raw seconds. A smooth kernel can extrapolate confidently under assumptions that are wrong outside the observed region.

Assess predictions at the locations and horizons that match deployment. Random holdouts inside a dense design differ from forecasts beyond the observed range or predictions in a new spatial region. Preserve the training/validation boundary when selecting kernels and hyperparameters.

Numerical conditioning can worsen when inputs are nearly duplicated or noise is very small. A stable solver, explicit jitter and a scientifically justified observation model are complementary. Increasing jitter until a matrix factorization succeeds changes the effective model; diagnose the source of near-singularity and report the numerical choices.

## Answered scientific discussion

**Does a small GP example require MCMC?** Not when hyperparameters are fixed and the Gaussian model has an analytic conditional distribution. This unit intentionally uses that tractable case as an oracle for actual library computation.

**Why distinguish conditional from integrated uncertainty?** A precise conditional prediction can be misleading when there is substantial uncertainty about the conditions. The two-component variance example makes the missing term exact and visible before a larger model makes the distinction harder to inspect.
