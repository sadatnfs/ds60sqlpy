# bayes-015: Bayesian resource decisions and Monte Carlo uncertainty

Tutorial mode. Stage: intermediate. Direct prerequisites: `bayes-005`, `bayes-014`.

## A decision can be sensitive to Monte Carlo error

Posterior sampling approximates integrals. A downstream optimizer can amplify a small approximation error when two actions have similar expected utilities. The stability of the selected action therefore needs its own review, even when posterior means appear plausible.

The example observes five count periods 2,3,2,5,4. A Gamma(2,1) prior uses the shape/rate convention. With Poisson observations and unit exposure, the exact posterior is Gamma(18,6), with mean three. Actual PyMC sampling approximates that posterior, providing a computational comparison with a known answer.

Future demand integrates the Poisson likelihood over this gamma posterior, yielding a negative-binomial predictive distribution under the stated parameterization. The program uses that exact distribution as a decision oracle, rather than trusting a finite simulation to choose the final action automatically.

## Key terms

- **Gamma-Poisson posterior:** The conjugate update in which a Gamma(2, 1) prior and five counts summing to 16 give Gamma(18, 6).
- **Negative-binomial predictive:** The distribution of future demand obtained by integrating the Poisson likelihood over the gamma posterior.
- **Monte Carlo error:** Approximation error from finite sampling that can change the selected action when expected costs are close.
- **Decision oracle:** The exact predictive distribution used to verify the optimal quantity instead of trusting a short simulation.

## Worked case 1: optimize an exact posterior predictive cost

Underage costs four per unit and overage costs one. Candidate quantities range from zero through ten. The code evaluates expected cost under the exact predictive mass function, including enough count support that omitted tail mass is negligible for this fixture. The optimal quantity is four.

The posterior mean rate is three, which is not the optimal inventory quantity for this asymmetric loss. Parameter uncertainty and future count variation both enter the predictive decision. A point estimate alone cannot reproduce that calculation.

The exact result is conditional on the count model, prior, exposure and cost ratio. It does not establish that a real demand process is independent Poisson or that the same costs apply during a capacity shortage. Those scientific and operational assumptions should accompany the optimized quantity.

## Worked case 2: compare a short-chain simulation decision

The program also generates predictive demand from the sampled rates and computes empirical expected costs. Its selected quantity can differ by one from the exact oracle under the deliberately small sampling budget. The output explicitly reports whether it differs, the Monte Carlo cost discrepancy and the regret of that simulated action under the exact predictive model.

A different selected action does not require a dramatic error in the posterior mean. Near an optimum, two actions may have similar values, so noise can reverse their order. The example retains that disagreement as a diagnostic instead of increasing the budget or changing a seed until the desired action appears.

For this tractable case, the reported oracle action provides the final model-based choice. In an intractable case, investigate target-specific Monte Carlo errors, repeated runs, analytic integration of parts of the loss, common random numbers or other variance-reduction methods. The goal is sufficient precision for the decision, not a generic number of posterior draws.

## Diagnose each source of uncertainty separately

There is sampling uncertainty about the unknown rate, outcome randomness conditional on that rate, Monte Carlo error in approximating the posterior and predictive integrals, and uncertainty about the model and costs. These have different remedies. Collecting more data does not directly repair a poor sampler; drawing more samples does not validate a misspecified demand process.

A decision report should include the expected-value gap between plausible actions and how accurately that gap has been calculated. If the gap is negligible compared with operational costs or model uncertainty, a stable simpler action may be reasonable. That is a decision judgment that should be made explicitly.

The finite program uses a fixed seed for reproducibility, but a fixed seed is not a guarantee of accuracy. Review the actual diagnostics and the exact-oracle discrepancy. Short-run R-hat or effective-size summaries can pass the screen for one parameter (R-hat below 1.01, at least 100 bulk effective draws per chain) while the expected loss difference remains imprecise; the decision needs its own Monte Carlo error.

## Answered scientific discussion

**Should an analyst always rerun until the simulated action matches an expected answer?** No. That selects favorable numerical noise. Use independent oracles where available, state a precision criterion and improve the computation transparently.

**What transfers to a larger optimization system?** Preserve posterior uncertainty through the relevant loss, evaluate the precision of action comparisons, record the chosen rule and retain a rollback or reassessment condition. A successful sampling command is only one component of that scientific decision process.

## Worked example: How flat the expected cost is around the optimal order

```python
import numpy as np
from scipy import stats

a, b = 2 + 41, 0.1 + 4  # Gamma posterior for a Poisson demand rate
pred = stats.nbinom(a, b / (b + 1))  # posterior predictive demand for one period
under, over = 5.0, 1.0
d = np.arange(0, 60)
pmf = pred.pmf(d)


def cost(q):
    return pmf @ (under * np.maximum(d - q, 0) + over * np.maximum(q - d, 0))


q_star = int(pred.ppf(under / (under + over)))
print(f"predictive mean {pred.mean():.2f}, sd {pred.std():.2f}, optimal order {q_star}")
for q in range(q_star - 3, q_star + 4):
    print(f"q={q}: expected cost {cost(q):.4f}, excess {cost(q) - cost(q_star):.4f}")
```

Observed output:

```text
predictive mean 10.49, sd 3.61, optimal order 14
q=11: expected cost 7.7210, excess 2.0012
q=12: expected cost 6.5275, excess 0.8076
q=13: expected cost 5.8921, excess 0.1723
q=14: expected cost 5.7198, excess 0.0000
q=15: expected cost 5.9108, excess 0.1909
q=16: expected cost 6.3723, excess 0.6525
q=17: expected cost 7.0262, excess 1.3063
```

The gamma posterior for the demand rate gives a negative binomial predictive with mean 10.49 and standard deviation 3.61. With shortage cost 5 and overage cost 1, the critical fractile is \(5/6=0.833\), and the predictive quantile is 14, about three and a half units above the mean. The cost table shows how much precision that answer needs. Moving one unit either way costs only 0.17 or 0.19 per period, about 3 percent of the optimum 5.72. Moving three units costs between 1.3 and 2.0. The curve is flat near the optimum and asymmetric farther out, because running short is five times as expensive as overstocking: ordering 11 costs more extra than ordering 17. This flatness decides how much simulation effort is worthwhile. A Monte Carlo approximation that sometimes picks 13 or 15 loses less than 0.2 per period, so a modest number of predictive draws is usually enough, whereas an error that lands on 11 deserves attention. The Monte Carlo standard error should be judged on the cost scale, not on the quantity scale.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. These teaching-sized chains can fail the convergence screen from `bayes-006` (R-hat below 1.01, at least 100 bulk and tail effective draws per chain, no divergences); read the printed diagnostics against it before interpreting any estimate. Runtime: `bayesian-cpu`.

```python
"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import stats


def sample_model(model, seed):
    import pymc as pm

    with model:
        return pm.sample(
            draws=120,
            tune=120,
            chains=2,
            cores=1,
            random_seed=seed,
            progressbar=False,
            target_accept=0.9,
            idata_kwargs={"log_likelihood": True},
        )


def diagnostics(trace, names):
    import arviz as az

    rhat = np.asarray(az.rhat(trace, var_names=names).to_dataarray(), float)
    ess = np.asarray(az.ess(trace, var_names=names, method="bulk").to_dataarray(), float)

    def finite_extreme(values, maximum):
        values = values[np.isfinite(values)]
        return float(values.max() if maximum else values.min()) if len(values) else None

    return dict(
        rhat_max=finite_extreme(rhat, True),
        bulk_ess_min=finite_extreme(ess, False),
        divergences=int(trace.sample_stats["diverging"].sum()),
        chains=int(trace.posterior.sizes["chain"]),
        retained_per_chain=int(trace.posterior.sizes["draw"]),
    )


def run_cases():
    import pymc as pm

    y = np.array([2, 3, 2, 5, 4])
    a, b = 2 + int(y.sum()), 1 + len(y)
    with pm.Model() as model:
        rate = pm.Gamma("rate", alpha=2, beta=1)
        pm.Poisson("obs", rate, observed=y)
    trace = sample_model(model, 6015)
    rates = np.asarray(trace.posterior["rate"]).ravel()
    rng = np.random.default_rng(615)
    future = rng.poisson(rates[:, None], size=(len(rates), 100)).ravel()
    grid = np.arange(11)
    loss = lambda q, d: 4 * np.maximum(d - q, 0) + np.maximum(q - d, 0)
    empirical = np.array([loss(q, future).mean() for q in grid])
    counts = np.arange(100)
    mass = stats.nbinom.pmf(counts, a, b / (b + 1))
    exact = np.array([loss(q, counts) @ mass for q in grid])
    assert abs(float(rates.mean()) - a / b) < 0.3
    assert abs(int(empirical.argmin()) - int(exact.argmin())) <= 1
    return dict(
        sample_rate=float(rates.mean()),
        analytic_rate=a / b,
        simulation_quantity=int(grid[empirical.argmin()]),
        exact_quantity=int(grid[exact.argmin()]),
        exact_expected_cost=float(exact.min()),
        oracle_decision=int(grid[exact.argmin()]),
        simulation_decision_differs=bool(empirical.argmin() != exact.argmin()),
        simulation_policy_regret=float(exact[empirical.argmin()] - exact.min()),
        monte_carlo_max_cost_error=float(np.max(np.abs(empirical - exact))),
        diagnostics=diagnostics(trace, ["rate"]),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-015 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Stan posterior prediction](https://mc-stan.org/docs/stan-users-guide/posterior-prediction.html)
