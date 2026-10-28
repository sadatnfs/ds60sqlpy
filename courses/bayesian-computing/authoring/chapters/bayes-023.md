## A dynamic model defines conditional transitions

An autoregressive model relates a current observation to previous state. For a stationary AR(1) process with mean mu,

\[
y_t=\mu+\phi(y_{t-1}-\mu)+\epsilon_t,
\qquad \epsilon_t\sim\mathcal N(0,\sigma^2),\quad |\phi|<1.
\]

The example uses twelve equally spaced synthetic observations. The equality of spacing and the chosen time unit are assumptions; an irregular sequence cannot be treated as the same model merely by discarding timestamps.

The positive innovation scale sigma differs from the marginal stationary standard deviation, which is \(\sigma/\sqrt{1-\phi^2}\). Confusing them changes the likelihood and the interpretation of uncertainty. The prior on phi is restricted to the stationary interval by its parameter declaration.

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
