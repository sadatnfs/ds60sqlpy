# Priors, penalties and the quantity being estimated

A prior is a probability distribution on a declared parameter space. A penalty
can have a prior interpretation, but only after its coordinates, normalization,
weighting and placement are specified. Begin by writing the density or objective;
matching a software argument name is not enough.

## Four distinct operations

1. **Marginal maximum likelihood:** a generative random effect \(u\) has a density
   such as \(N(0,\tau^2)\). Integrating it out produces
   \(p(y\mid\theta)=\int p(y\mid u,\theta)p(u\mid\theta)\,du\).
   Maximizing this over population parameters is still marginal ML.
2. **Marginal MAP:** add a declared prior \(p(\theta)\) to that marginal likelihood
   and optimize \(-\log p(y\mid\theta)-\log p(\theta)\). This returns one mode.
3. **Random-effect Laplace:** approximate the integral over \(u\) around its
   conditional mode. This numerical method does not, by itself, introduce a prior
   over the population parameters or return their posterior.
4. **Parameter-posterior inference:** normalize/sample/approximate
   \(p(\theta\mid y)\). A Gaussian posterior approximation around a MAP, exact
   conjugate posterior, and MCMC are distinct methods with distinct checks.

Our current native generic Laplace implementation concerns item 3. Its conditional
random-effect moments condition on fitted population parameters. Calling those
moments a complete Bayesian posterior prediction would omit another uncertainty
layer. The current Torch Gaussian random-intercept model uses an exact Gaussian
integral, not a generic latent Laplace engine.

## Worked case: what scalar L2 actually means

For Gaussian regression, the prepared native vector is
\(\theta=(\beta_0,\beta_1,\rho)\), where \(\rho=\log\sigma\).
The current scalar option adds

\[
 P(\theta)=\frac{\lambda}{2}(\beta_0^2+\beta_1^2+\rho^2).
\]

Under a **summed** negative log likelihood, this corresponds, up to constants, to
independent zero-centered normal priors with precision \(\lambda\) on all three
optimization coordinates. It shrinks the intercept toward zero and the noise
standard deviation toward one through its log coordinate. It is not the usual
slope-only ridge objective. A scenario with an intercept of 5 and noise scale 2 is
therefore a meaningful contrast with a centered scenario having noise scale 1.
Predictive improvement or degradation must be measured, not assumed.

A prior only on the slope would instead use
\(P=\lambda\beta_1^2/2\). A prior centered at a scientifically motivated slope
\(m\) uses \(\lambda(\beta_1-m)^2/2\). Neither is obtained by silently penalizing
all coordinates. They need a named-coordinate penalty or an explicit study-level
wrapper around a public unpenalized evaluator.

If \(L\) is a summed likelihood with global weight mass \(W\), then
\(L+P\) and \(L/W+P/W\) have the same optimum. The objective \(L/W+P\) generally
has a different optimum. Keeping the same numeric lambda while switching
reduction changes the inferential target. Likewise, adding \(P\) once per
partition changes the prior when partition count changes.

## Worked case: MLE coordinates and posterior density measure

Let a positive rate \(\lambda\) have Gamma prior with shape \(a\) and rate
\(b\), and observe Poisson counts with total count \(S\) and total exposure \(E\).
The posterior is Gamma with \(A=a+S\), \(B=b+E\).
For \(A>1\), its mode in rate coordinates is

\[
 \lambda_{\mathrm{MAP},d\lambda}=\frac{A-1}{B},
 \qquad E[\lambda\mid y]=\frac{A}{B}.
\]

Now set \(\eta=\log\lambda\). The same posterior probability measure has density

\[
 p_\eta(\eta\mid y)=p_\lambda(e^\eta\mid y)e^\eta.
\]

Its log-coordinate mode maps back to \(A/B\), rather than \((A-1)/B\).
For example, \(A=5,B=3\) gives natural-coordinate MAP \(4/3\) and mapped
log-coordinate MAP \(5/3\). The posterior distribution has not changed; the
location of a density maximum depends on the measure used to describe it.
Posterior probabilities and correctly transformed quantiles remain consistent.

When \(A<1\), the natural-coordinate density has an unbounded supremum at zero;
there is no finite interior natural-coordinate mode. The log-coordinate density
still has a finite mode. This is a second worked case, not an optimizer problem
to hide by clipping the parameter and declaring convergence.

MLE is different. Optimizing \(L(e^\eta)\) merely re-expresses the parameter and
adds no Jacobian. If a MAP target is explicitly the natural-coordinate density,
optimizing that same density through \(e^\eta\) also adds no Jacobian to its
chosen target. A Jacobian is required when expressing a density with respect to
a different integration measure, as needed by posterior sampling in transformed
coordinates. Always state which of these operations is intended.

## Exact lasso is not smooth ridge

On a centered orthogonal design with \(X^\top X=nI\), known observation variance
\(\sigma^2\), and an L1 penalty \(\lambda\sum_j|\beta_j|\), the solution on penalized
coordinates is

\[
 \hat\beta_j=\operatorname{sign}(\hat\beta_j^{OLS})
 \max\!\left(|\hat\beta_j^{OLS}|-\lambda\sigma^2/n,0\right).
\]

Ridge instead scales a coefficient continuously and generally does not make it
exactly zero. For lasso, a zero coordinate satisfies \(|g_j|\le\lambda\), while
an active coordinate satisfies \(g_j+\lambda\operatorname{sign}(\beta_j)=0\).
These KKT checks are the relevant optimality diagnostic. The current smooth
optimizers must not be described as exact lasso solvers. A Laplace prior can give
an L1 MAP target, but a MAP vector is still not a posterior draw.

## Study interpretation and interview discussion

**Does a random-effect prior make the fitted model fully Bayesian?** No. It may
be part of a generative mixed model whose latent effects are integrated for ML.
Population-parameter priors and their posterior uncertainty are separate choices.

**Can I compare a penalized native growth fit with a Torch decay fit after changing
coordinates?** Unpenalized likelihoods can describe the same curve under a
bijection. An isotropic L2 penalty usually changes under that transformation, so
reusing the same lambda does not preserve the MAP target.

**Why can a 95% Bayesian credible interval miss a fixed true parameter too often?**
A strong prior can be poorly centered at that particular truth. Prior-predictive
calibration and fixed-truth frequentist coverage ask different questions. The
simulation must report its parameter-generating regime.

The pinned [glmmTMB prior vignette](https://github.com/glmmTMB/glmmTMB/blob/1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c/glmmTMB/vignettes/priors.rmd)
explicitly discusses MAP and a separately requested posterior sampler. Its
parameter-scale conventions must be checked before attempting a comparison.
The historical AFModel helper named `prior_coefs_mean` performs post-fit sign
filtering. Such selection is neither a density prior nor automatically valid
post-selection inference.
