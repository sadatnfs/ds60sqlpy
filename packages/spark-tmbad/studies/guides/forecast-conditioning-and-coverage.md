# Forecast conditioning, leakage and joint uncertainty

A forecasting study states what was known at each prediction time. A model can
fit a complete dataset accurately while producing a misleading backtest if
future observations, future realized covariates, normalization statistics or
hyperparameter decisions leak into its training inputs.

## Two different evaluation populations

For a known group, retain its observed prefix and forecast later observations.
The population parameters are estimated using the training period; the group's
latent posterior is conditioned only on its available history. For an unseen
group, exclude that group's history from both parameter fitting and conditioning.
Use the new-group target and its prior latent uncertainty. Splitting random rows
from every group does not assess unseen-group performance.

Create independent outer Monte Carlo datasets. Within each dataset use rolling
origins, such as 12, 18 and 24, with a fixed horizon. All preprocessing and tuning are
fit inside each origin's training prefix. Hyperparameter selection uses inner
origins that finish before the outer forecast origin. Report metrics per horizon
and per group type, then aggregate within each dataset before calculating MCSE
across independent replicates. Treating overlapping origins as independent
replicates understates Monte Carlo uncertainty.

## Worked case: Gaussian random intercept

Suppose \(Y_{gt}=\beta+u_g+\epsilon_{gt}\), with independent
\(u_g\sim N(0,\tau^2)\), \(\epsilon_{gt}\sim N(0,\sigma^2)\).
For a known group with history of size \(n\), define

\[
 v_g=(\tau^{-2}+n\sigma^{-2})^{-1},\qquad
 m_g=v_g\sigma^{-2}\sum_t(Y_{gt}-\beta).
\]

A future observation has mean \(\beta+m_g\) and variance \(\sigma^2+v_g\).
Two future observations in the same known group have covariance \(v_g\).
For a new group, replace \(m_g\) with zero and \(v_g\) with \(\tau^2\).
The changed case is not merely a different group label: the uncertainty and
conditioning actually differ. These formulas condition on fixed population
parameters; plugging in estimates does not add their uncertainty.

A paired simulation varies history length while keeping future innovations and
the group effect fixed by separate seed keys. The known-group variance should
shrink toward observation variance as history grows. The unseen-group variance
does not shrink because some other group has a long history. Test that accidental
history joins cannot silently drop unseen future groups or use the wrong group.

## Worked case: AR1 residuals and a shared intercept

For a directly observed stationary AR1 process, `sigma` is an innovation SD and
\(\phi\) is its correlation coefficient. Conditional on the last exact value,

\[
 E[Y_{T+h}]=\mu+\phi^h(Y_T-\mu),\quad
 \operatorname{Var}(Y_{T+h})=\sigma^2\sum_{r=0}^{h-1}\phi^{2r}.
\]

The cross-horizon covariance for \(j\le k\) is

\[
 \operatorname{Cov}(Y_{T+j},Y_{T+k}\mid Y_T)
 =\sigma^2\phi^{k-j}\sum_{r=0}^{j-1}\phi^{2r}.
\]

For the prepared random-intercept/AR1 model, the conditional group effect adds
\((1-\phi^j)(1-\phi^k)v_g\) to this covariance, where \(v_g\) is computed from the
complete correlated history. The mean includes the corresponding posterior
latent contribution. A new stationary group instead has covariance
\(\tau^2+\sigma^2\phi^{|j-k|}/(1-\phi^2)\).
Negative phi is a meaningful changed case: forecast means and some cross-horizon
covariances alternate in sign even though variances remain nonnegative.

These are not formulas for a latent AR1 state observed with separate measurement
error. That model needs filtering/conditioning on noisy observations and has a
different covariance. An irregular time gap also cannot silently become one AR1
step. The initial native target checks exact unit cadence; an OU extension must
use actual elapsed time.

## Nonlinear links: align the prediction target before comparing software

For a log-linked Poisson response, let the existing group's approximate latent
posterior contribution be \(U\mid D,\hat\theta\sim N(m,v)\), with fixed predictor
\(a\). These are different quantities:

| Target | Value | Interpretation |
| --- | --- | --- |
| Link prediction at the latent mode | \(a+m\) | A predictor on the log scale |
| Response at the latent mode | \(\exp(a+m)\) | Poisson mean conditional on one latent value |
| Existing-group latent-integrated response | \(\exp(a+m+v/2)\) | Average response under the conditional latent approximation |
| New-group response with random effects set to zero | \(\exp(a)\) | Response at the prior mode, not a prior average |
| New-group prior-integrated response | \(\exp(a+\tau^2/2)\) | Average over a new Gaussian group effect |
| Full posterior-predictive response | \(E_{\theta\mid D}E_{U\mid\theta,D}[Y_*]\) | Also integrates population-parameter uncertainty |

For example, if \(a+m=\log 2\) and \(v=0.5\), the conditional-mode response is 2,
while the latent-integrated mean is \(2\exp(0.25)\approx 2.5681\). The difference
is a change of target, not necessarily a regression in either implementation.
The corresponding pointwise count variance is
\(M+M^2\operatorname{expm1}(v)\), where \(M\) is the integrated mean.

The pinned [glmmTMB prediction documentation](https://github.com/glmmTMB/glmmTMB/blob/1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c/glmmTMB/man/predict.glmmTMB.Rd)
sets `do.bias.correct=FALSE` by default and explicitly defines `re.form=NA` or
`~0` as setting random effects to zero. In that interface, `type="conditional"`
means the mean of the non-zero-inflation response component, not a promise to
integrate random effects. The pinned C++ prediction branch applies the inverse
link and the requested zero-inflation adjustment to its current latent values.

Its optional bias-correction route is documented as a Taylor-based correction
and needs its own qualified comparison. Do not assume it equals the analytic
lognormal moment used by our prepared Poisson targets. With zero inflation and
correlated latent components, even the average of the product is generally not
the product of separate averages. Compare the same conditioning, latent measure,
fixed-parameter treatment, link and component before setting a numerical tolerance.

## Pointwise coverage is not path coverage

A pointwise 95% interval is evaluated separately at each horizon. Whole-path
coverage requires every true future value in the path to fall inside its band.
Even independent 95% pointwise intervals have only \(0.95^H\) simultaneous
coverage over \(H\) steps. Correlation changes that calculation; it does not turn
pointwise intervals into a calibrated simultaneous band.

The first comparison reports both metrics. A conservative Bonferroni band uses
a per-coordinate tail allocation of \(\alpha/(2H)\). A joint Gaussian reference
can instead simulate the maximum standardized error using the full forecast
covariance. Such a reference is labeled separately because the current native
API returns pointwise moments, not a generic full covariance matrix.

## Parameter uncertainty and resampling

A plug-in forecast conditions on fitted population parameters. A parameter
bootstrap or posterior-predictive calculation also varies those parameters.
Do not add the same latent uncertainty twice when the inner forecast already
integrates a group effect. For bootstrap comparisons, resample whole independent
training units and give duplicate bootstrap copies new unit IDs. Preserving the
same ID would incorrectly merge duplicated clusters into one latent unit.

For a Bayesian reference, draw parameters from their actual posterior and then
future latent effects/innovations according to the requested conditioning.
Sampling from an inverse Hessian without a prior and calling the result Bayesian
is not valid. A Gaussian approximation to the posterior must identify its mode,
coordinate measure, curvature and failure conditions. A frequentist bootstrap is
not renamed a posterior distribution.

## AFModel-inspired extensions

The original AFModel sources motivate explicit covariate paths, level/difference
models and recursive forecasting. Our synthetic extension will compare:

- constant-mean versus covariate-trend panels;
- observed covariates versus forecast/scenario covariates available at the origin;
- coherent innovations versus an independently added random-walk uncertainty layer;
- direct levels versus reconstructed first differences;
- one conditional mean path versus the mean of back-transformed stochastic paths.

For a nonlinear inverse transform, transforming the expected latent outcome is
usually not the same as the expected transformed outcome. Store the target scale
and score on the scale that answers the scientific question. These are original
experiments inspired by architecture, not an execution or numerical reproduction
of every historical AFModel branch or its operational environment.

**Interview discussion:** A low future RMSE can coexist with badly undercovered
intervals because prediction bias and uncertainty calibration are different
properties. A model can pass pointwise coverage while failing path coverage. A
random train/test split can look excellent while evaluating interpolation rather
than forecasting. Each claim needs the corresponding split and metric.
