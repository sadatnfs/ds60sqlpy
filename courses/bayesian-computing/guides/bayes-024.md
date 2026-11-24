# bayes-024: Stan censored survival workflow and decision dossier

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-019`, `bayes-020`, `bayes-014`, `bayes-015`, `science-011`.

## Construct the likelihood from the observation process

The final Stan model combines a positive event-time distribution, covariates, right censoring and delayed entry. Its purpose is to connect code, probability accounting, diagnostics and interpretation in one inspectable compiled workflow. The eight observations are synthetic and too small to support a broad external conclusion.

A Weibull distribution has shape a and scale s. The model sets \(s_i=\exp(\beta_0+\beta_1x_i)\), so a covariate acts on the time scale. An event row contributes a density at its observed time; a right-censored row contributes survival beyond that time. Conditioning on survival to entry divides either contribution by the survival probability at the entry time.

## Key terms

- **Weibull AFT model:** A Weibull event-time model whose scale exp(beta_0 + beta_1 x) lets a covariate stretch the time axis.
- **Right-censored contribution:** The survival probability beyond the last observed time, used instead of a density when no event was seen.
- **Left truncation:** Delayed entry handled by dividing each contribution by the survival probability at the entry time.
- **Hazard ratio:** The multiplicative change in hazard per unit of the covariate, which under this Weibull AFT model equals exp(-a beta_1), not exp(beta_1).

## Worked case 1: write the censored and truncated contribution

For event indicator delta and entry e before endpoint t, the log contribution is

\[
\delta\log f(t)+(1-\delta)\log S(t)-\log S(e).
\]

The program uses `weibull_lpdf` for an observed event and `weibull_lccdf` for censoring and entry. At entry zero, the survival normalization is one, so the code omits that zero log term explicitly. The transformed-data block rejects entry at or after the observed endpoint.

Stan's special target accumulator accepts `target +=`. To subtract the entry log survival, the code uses `target += -weibull_lccdf(...)`. Writing `target -=` is not valid Stan syntax, even though ordinary stored variables can use compound subtraction. The corrected statement preserves the mathematical conditioning term rather than dropping it to make compilation succeed.

The positive shape has a lognormal prior and the regression coefficients have normal priors. These choices affect tail behavior and weakly informed directions. Prior predictive checks should be performed in the units of time before interpreting the fitted quantities as plausible event-time behavior.

## Worked case 2: derive AFT and hazard interpretations

For a common Weibull shape, the time-scale ratio between x equal to one and zero is \(\exp(\beta_1)\). The corresponding hazard ratio is \(\exp(-a\beta_1)\). The code calculates both, along with the control median \(\exp(\beta_0)(\log(2))^{1/a}\) and survival at a stated horizon.

A longer time scale corresponds to a smaller hazard multiplier under this shared-shape model. Reporting the same exponentiated coefficient as both an acceleration factor and a hazard ratio would therefore be wrong. The relationship depends on the model family and parameterization; it should not be transferred blindly to another survival model.

A prediction for an already observed entrant can require conditioning on survival to its entry time. The generated population survival at time six is not automatically that conditional prediction. State the population, time origin and conditioning information attached to every reported probability.

## Complete the scientific dossier

The log-likelihood vector records each row's actual event/censoring/entry contribution. Any predictive evaluation must respect the observation unit and the conditioning scheme. Comparing latent replicated event times directly with censored observed endpoints would mix different quantities. A full posterior predictive simulation should also reproduce the relevant censoring and entry mechanisms when those are known.

Review shape, regression and derived-quantity diagnostics separately. Short chains can be particularly unreliable for tail survival or a hazard ratio combining several parameters. Undefined diagnostics for constants are expected, but poor diagnostics for sampled quantities need investigation: an R-hat at or above 1.01, bulk or tail effective sizes below about 100 per chain or any divergence means the classroom run cannot support the dossier's numbers. Compilation and a zero execution status are distinct from adequate inference.

Retain model source, data definition, compiler/runtime version, sampling settings, actual diagnostics and the decision target. The optional standard data-block project demonstrates how to separate data from code and preserve output files in a deliberately prepared environment. The classroom pad remains a bounded single-source workflow with fixed sampler settings.

## Answered scientific discussion

**Why not treat censoring times as failures and rely on a flexible distribution?** That supplies the wrong likelihood information. Flexibility cannot repair a data record whose meaning has been changed incorrectly.

**What establishes readiness for an external use?** A defensible observation model, identification of the target, adequate computational diagnostics, predictive criticism, sensitivity analysis and an appropriate decision evaluation. This tutorial supplies a complete reproducible example of those distinctions, while making clear that its tiny synthetic dataset and short chains do not certify a real deployment.

## Worked example: Weibull AFT contributions for event, censored and truncated records

```python
import numpy as np
from scipy import integrate

k, b0, b1 = 1.5, np.log(10.0), 0.4  # shape, log scale intercept, treatment shift


def log_f(t, x):
    lam = np.exp(b0 + b1 * x)
    return np.log(k / lam) + (k - 1) * np.log(t / lam) - (t / lam) ** k


def log_S(t, x):
    return -((t / np.exp(b0 + b1 * x)) ** k)


print(f"event at 6, control:       {log_f(6.0, 0):.4f}")
print(f"censored at 12, treated:   {log_S(12.0, 1):.4f}")
print(f"event at 9, entered at 4:  {log_f(9.0, 0) - log_S(4.0, 0):.4f}")
mass = integrate.quad(lambda t: np.exp(log_f(t, 0) - log_S(4.0, 0)), 4.0, np.inf)[0]
print(f"truncated density integrates to {mass:.6f} over t > 4")
print(f"acceleration factor {np.exp(b1):.4f}, hazard ratio {np.exp(-k * b1):.4f}")
```

Observed output:

```text
event at 6, control:       -2.6173
censored at 12, treated:   -0.7214
event at 9, entered at 4:  -2.5506
truncated density integrates to 1.000000 over t > 4
acceleration factor 1.4918, hazard ratio 0.5488
```

Each record contributes a different piece of the Weibull model. A control event at time 6 adds the log density, \(-2.6173\). A treated subject still event-free at 12 adds only the log survival, \(-0.7214\), because all we know is that the event time exceeds 12. A control event at 9 for someone who entered observation at 4 adds the log density minus the log survival at entry, \(-2.5506\): people who failed before 4 could never have been enrolled, so the likelihood must condition on surviving to 4. The quadrature check confirms that this conditional density integrates to 1.000000 over times after 4. Omitting the truncation term would treat late entrants as if their early risk had been observed, making early survival look better than it is. The summary line converts the coefficient 0.4 into two scales. On the time scale treatment multiplies survival times by \(e^{0.4}=1.4918\); on the hazard scale the same Weibull model implies a hazard ratio of \(1.4918^{-1.5}=0.5488\).

## Complete reproducible program

The prepared Stan pad compiles `main.stan` and samples two chains with 100 warmup and 100 retained draws each. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. These teaching-sized chains can fail the convergence screen from `bayes-006` (R-hat below 1.01, at least 100 bulk and tail effective draws per chain, no divergences); read the printed diagnostics against it before interpreting any estimate. Runtime: `stan-cpu`.

```stan
transformed data {
  int N = 8;
  vector[N] time = [1.1, 2.3, 3, 4, 5.2, 6, 8, 9]';
  vector[N] entry = [0, 0, 1, 0, 2, 1, 0, 2]';
  vector[N] x = [0, 1, 0, 1, 0, 1, 0, 1]';
  array[N] int event = {1, 1, 0, 1, 0, 1, 0, 1};
  for (n in 1 : N)
    if (entry[n] >= time[n])
      reject("Entry must precede observed endpoint");
}
parameters {
  real<lower=0> shape;
  vector[2] beta;
}
transformed parameters {
  vector[N] scale = exp(beta[1] + beta[2] * x);
}
model {
  shape ~ lognormal(0, 0.5);
  beta ~ normal(0, 1.5);
  for (n in 1 : N) {
    if (event[n])
      target += weibull_lpdf(time[n] | shape, scale[n]);
    else
      target += weibull_lccdf(time[n] | shape, scale[n]);
    if (entry[n] > 0)
      target += -weibull_lccdf(entry[n] | shape, scale[n]);
  }
}
generated quantities {
  vector[N] log_lik;
  real acceleration_factor = exp(beta[2]);
  real hazard_ratio = exp(-shape * beta[2]);
  real median_control = exp(beta[1]) * pow(log(2), inv(shape));
  real survival_control_at_six = exp(weibull_lccdf(6 | shape, exp(beta[1])));
  for (n in 1 : N) {
    if (event[n])
      log_lik[n] = weibull_lpdf(time[n] | shape, scale[n]);
    else
      log_lik[n] = weibull_lccdf(time[n] | shape, scale[n]);
    if (entry[n] > 0)
      log_lik[n] -= weibull_lccdf(entry[n] | shape, scale[n]);
  }
}
```

## Primary references

- [Stan survival models](https://mc-stan.org/docs/stan-users-guide/survival.html)
