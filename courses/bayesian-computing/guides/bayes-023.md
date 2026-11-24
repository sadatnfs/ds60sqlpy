# bayes-023: Stan stationary dynamics and multi-step prediction

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-018`, `bayes-016`.

## A dynamic model defines conditional transitions

An autoregressive model relates a current observation to previous state. For a stationary AR(1) process with mean mu,

\[
y_t=\mu+\phi(y_{t-1}-\mu)+\epsilon_t,
\qquad \epsilon_t\sim\mathcal N(0,\sigma^2),\quad |\phi|<1.
\]

The example uses twelve equally spaced synthetic observations. The equality of spacing and the chosen time unit are assumptions; an irregular sequence cannot be treated as the same model merely by discarding timestamps.

The positive innovation scale sigma differs from the marginal stationary standard deviation, which is \(\sigma/\sqrt{1-\phi^2}\). Confusing them changes the likelihood and the interpretation of uncertainty. The prior on phi is restricted to the stationary interval by its parameter declaration.

## Key terms

- **AR(1) process:** A model in which y_t = mu + phi(y_(t-1) - mu) plus normal innovation noise.
- **Stationarity:** A constant marginal distribution over time, which for AR(1) requires the absolute value of phi to be less than one.
- **Innovation scale:** The standard deviation sigma of each new shock, distinct from the stationary standard deviation sigma/sqrt(1 - phi^2).
- **Multi-step forecast:** A prediction h steps ahead with conditional mean mu + phi^h(y_N - mu) and variance that accumulates future innovations.

## Worked case 1: include the initial-state distribution

The first observation has a normal density under the stationary distribution. Later observations have normal conditional densities around the autoregressive transition mean. This specifies a complete joint model for the small sequence.

Conditioning on the first observation and omitting its density would define a related but different likelihood. In a long series the difference can become less influential, but in a short example it should not be hidden as a performance optimization. A nonstationary or externally initialized process may need a different initial-state model altogether.

A posterior near the stationarity boundary can be difficult to explore and interpret. A finite series may have limited information distinguishing a persistent stationary process from a different long-run mechanism. Constraints and priors regularize the question; they do not prove that the real process is stationary.

## Worked case 2: propagate uncertainty across horizons

Conditional on the latest observation and one parameter draw, the h-step mean is \(\mu+\phi^h(y_N-\mu)\). For h equal to three, the innovation variance is

\[
\sigma^2(1+\phi^2+\phi^4).
\]

The generated quantities calculate those values and draw both one-step and three-step future outcomes. Reusing only sigma squared at every horizon would omit accumulated future innovations. Substituting the stationary marginal variance at every horizon would answer a different question about an unconditioned process.

Across posterior draws, the future outcome distribution also includes parameter uncertainty. A forecast made with one posterior-mean parameter vector generally does not reproduce that full mixture. The same total-variance distinction from the GP tutorial applies here.

## Align forecasting evaluation with information time

A real forecast must use only outcomes and covariates available at its origin. Revising the historical series after the fact can change a backtest if its original vintages are not retained. The small constant fixture avoids that data-engineering issue for computation, while the applied-science forecasting route teaches it explicitly.

Evaluate at horizons and origins that match intended use. Randomly removing an interior point while observing later values is an interpolation task, not the same as forecasting the future. Overlapping horizons create dependent errors, so uncertainty about performance should respect that structure.

Inspect residual and posterior predictive patterns for remaining dependence, changing scale, outliers and structural breaks. An AR(1) term can capture some persistence while missing seasonality or a change in the mean. A low training residual error is not a complete dynamic-model assessment.

The compiled classroom run uses the fixed short-chain budget. Its successful execution demonstrates the specified model and forecast calculations. Adequate inference for persistence near a boundary or a tail decision may need substantially more computation, different parameterization and a more appropriate model.

## Answered scientific discussion

**Why is the three-step variance larger than the one-step innovation variance?** Several future innovations can affect the later outcome. Their coefficients form the squared autoregressive powers in the sum. This is conditional forecast uncertainty, not simply a larger standard error for mu.

**Can an AR coefficient be interpreted causally?** Not from temporal association alone. Feedback, omitted variables and the observation process can generate persistence. Define an intervention and an identification argument separately before interpreting the transition coefficient as an effect of changing a previous outcome.

## Worked example: Closed-form AR(1) forecast variance by horizon

```python
import numpy as np

phi, sigma, y_T = 0.8, 1.0, 3.0
stationary = sigma**2 / (1 - phi**2)
print(f"stationary variance of y_1: {stationary:.4f}")
for h in range(1, 6):
    mean = phi**h * y_T
    var = sigma**2 * (1 - phi ** (2 * h)) / (1 - phi**2)
    print(f"h={h}: conditional mean {mean:.3f}, innovation variance {var:.4f}")

rng = np.random.default_rng(23)
sims = np.full(200000, y_T)
for _ in range(3):
    sims = phi * sims + rng.normal(0, sigma, sims.size)
print(f"simulated h=3: mean {sims.mean():.3f}, variance {sims.var():.4f}")
```

Observed output:

```text
stationary variance of y_1: 2.7778
h=1: conditional mean 2.400, innovation variance 1.0000
h=2: conditional mean 1.920, innovation variance 1.6400
h=3: conditional mean 1.536, innovation variance 2.0496
h=4: conditional mean 1.229, innovation variance 2.3117
h=5: conditional mean 0.983, innovation variance 2.4795
simulated h=3: mean 1.537, variance 2.0437
```

With \(\phi=0.8\) and unit innovations the stationary variance is \(1/(1-0.64)=2.7778\). That is the variance the model assigns to the first observation when the series is assumed to have been running long before data collection began, and including it is what the initial-state term in the Stan model does. Forecasting from a last value of 3.0, the conditional mean decays geometrically, \(3\times0.8^h\): 2.400, 1.920, 1.536, 1.229 and 0.983. The innovation variance grows as \((1-0.64^h)/(1-0.64)\), from 1.0 at one step to 2.4795 at five, approaching the stationary 2.7778 from below. So the forecast forgets the last value and settles at the unconditional distribution. Simulating 200,000 three-step paths gives mean 1.537 and variance 2.0437, matching the closed form 1.536 and 2.0496 within Monte Carlo error. These numbers hold the parameters fixed. A Bayesian forecast also averages over posterior uncertainty in \(\phi\), which widens long-horizon intervals further, especially when \(\phi\) might be near 1.

## Complete reproducible program

The prepared Stan pad compiles `main.stan` and samples two chains with 100 warmup and 100 retained draws each. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. These teaching-sized chains can fail the convergence screen from `bayes-006` (R-hat below 1.01, at least 100 bulk and tail effective draws per chain, no divergences); read the printed diagnostics against it before interpreting any estimate. Runtime: `stan-cpu`.

```stan
transformed data {
  int N = 12;
  vector[N] y = [0.1, 0.3, 0.2, 0.5, 0.4, 0.2, -0.1, -0.2, 0, 0.2, 0.1, 0.05]';
}
parameters {
  real mu;
  real<lower=-1, upper=1> phi;
  real<lower=0> sigma;
}
model {
  mu ~ normal(0, 1);
  phi ~ normal(0, 0.5);
  sigma ~ normal(0, 0.5);
  y[1] ~ normal(mu, sigma / sqrt(1 - square(phi)));
  for (n in 2 : N)
    y[n] ~ normal(mu + phi * (y[n - 1] - mu), sigma);
}
generated quantities {
  real next_mean = mu + phi * (y[N] - mu);
  real next_outcome = normal_rng(next_mean, sigma);
  real horizon_three_mean = mu + pow(phi, 3) * (y[N] - mu);
  real horizon_three_variance = square(sigma) * (1 + square(phi) + pow(phi, 4));
  real horizon_three_outcome = normal_rng(horizon_three_mean, sqrt(horizon_three_variance));
}
```

## Primary references

- [Stan time-series models](https://mc-stan.org/docs/stan-users-guide/time-series.html)
