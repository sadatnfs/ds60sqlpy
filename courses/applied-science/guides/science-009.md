# science-009: Forecast calibration, quantiles and operational decision loss

Tutorial mode. Stage: intermediate. Direct prerequisites: `science-007`, `statistics-027`.

## Prediction quality depends on the decision

Squared error favors the conditional mean. Absolute error favors a conditional median. An asymmetric decision loss can favor another quantile. The choice is not merely a scoring convention: it expresses which mistakes matter for the downstream action.

Suppose quantity \(q\) is chosen before demand \(D\) is known. Underage costs \(c_u\) per missing unit and overage costs \(c_o\) per excess unit. The loss is

\[
L(q,D)=c_u(D-q)_+ + c_o(q-D)_+.
\]

For a continuous demand distribution, minimizing expected loss gives a quantile with level \(\tau=c_u/(c_u+c_o)\). With discrete demand, multiple quantities can share an optimum and the appropriate inequality formulation should be used. Costs, constraints and timing must be stated before this result is treated as a recommendation.

## Key terms

- **Pinball loss:** An asymmetric piecewise-linear loss whose expected value is minimized by a conditional quantile instead of a mean.
- **Newsvendor problem:** Choosing a quantity before demand is known when shortages cost c_u per unit and excess costs c_o per unit.
- **Critical fractile:** The quantile level c_u/(c_u + c_o) that minimizes expected newsvendor loss for continuous demand.
- **Calibration:** Agreement between predicted probabilities or intervals and observed outcome frequencies, checked separately by horizon or group.

## Worked case 1: choose an asymmetric-loss quantity

The synthetic demand observations are 0,1,1,2,3,8. Underage costs four and overage costs one, giving \(\tau=.8\). The code evaluates every integer quantity from zero through eight and finds that three minimizes the empirical decision loss. It independently verifies the identity between this loss and a scaled pinball loss:

\[
\rho_\tau(u)=\max\{\tau u,(\tau-1)u\},\qquad
L(q,D)=(c_u+c_o)\rho_\tau(D-q).
\]

The empirical mean demand is 2.5. It is a sensible squared-error prediction but has a larger cost for this particular asymmetric decision. A model can therefore improve RMSE and still worsen the action that matters. Conversely, optimizing a quantile loss does not establish that the cost ratio or empirical demand distribution is correct for deployment.

The fixture has a large upper-tail observation to make the asymmetry visible. It contains only six observations, so the empirical optimum is unstable evidence about an external demand population. A proper deployment analysis would investigate parameter uncertainty, covariates, nonstationarity, capacity constraints and the reliability of the stated cost ratio.

## Worked case 2: aggregate coverage hides horizon failure

The program records interval coverage separately for two horizons. The first horizon covers all five synthetic outcomes; the second covers only two. Averaging the ten indicators obscures the different behavior. A headline coverage rate can similarly mix groups, seasons, horizons and operating regimes whose uncertainty properties differ.

Calibration asks whether predicted probabilities or intervals agree with appropriate outcome frequencies. Sharpness concerns how concentrated those predictions are. A very wide interval can achieve high empirical coverage while offering little decision value. A narrow interval can look informative while badly under-covering. Examine both, using evaluation units that match the repeated forecasting procedure.

Prediction intervals concern future outcomes, while confidence intervals concern an estimated parameter or mean. Parameter uncertainty is often only one contribution to predictive uncertainty. Using a narrow coefficient interval as a forecast interval can ignore irreducible outcome variation, temporal dependence or future covariate uncertainty.

## Evaluate a full forecast-to-decision procedure

Separate data used to fit a forecast distribution, data used to choose a cost-sensitive rule, and data used to evaluate the resulting policy. If the cost ratio or threshold is optimized against the final test outcomes, the reported decision performance is selected on its own assessment set.

Compare against an operational baseline, such as a fixed stock level or the current planning rule. Record not only average cost but also tail events, constraint violations and subgroup outcomes. A policy with slightly lower mean cost can still produce unacceptable service failures. Constraints may require optimization beyond the simple one-period quantile rule.

Stress-test the rule under changed costs and distributional scenarios. Demand may respond to the action, capacity can couple several products, and leftover units can carry into later periods. Those mechanisms change the decision problem. The simple newsvendor model is a useful derivation precisely because its assumptions can be stated and then deliberately relaxed.

## Answered scientific discussion

**Should the chosen quantity equal the .8 sample quantile returned by every library?** Quantile interpolation conventions differ for small discrete samples. Directly calculating the stated loss, as the program does, exposes ties and verifies the actual decision objective.

**Can a forecast be called calibrated from ten checks?** Ten outcomes provide a very coarse diagnostic. The table demonstrates how aggregation can conceal a problem; it is not a precise calibration assessment. Report uncertainty, dependence and the intended forecasting population before making a broad claim.

## Worked example: Critical fractile, pinball loss and horizon-level coverage

```python
import numpy as np

cu, co = 4.0, 1.0  # lost margin per unit short, cost per unit left over
fractile = cu / (cu + co)
demand = np.array([8, 9, 10, 10, 11, 12, 12, 13, 15, 20])
order = np.quantile(demand, fractile, method="inverted_cdf")
print(f"critical fractile {fractile:.2f}, order quantity {order}")


def pinball(q, y, tau):
    return np.mean(np.maximum(tau * (y - q), (tau - 1) * (y - q)))


for q in (10, 13, 15):
    print(f"q={q}: pinball loss at tau 0.8 = {pinball(q, demand, 0.8):.3f}")

hit = {1: [1] * 19 + [0], 2: [1] * 17 + [0] * 3, 3: [1] * 12 + [0] * 8}
for h, v in hit.items():
    print(f"horizon {h}: 80% interval coverage {np.mean(v):.2f}")
print(f"pooled coverage {np.mean(sum(hit.values(), [])):.3f}")
```

Observed output:

```text
critical fractile 0.80, order quantity 13
q=10: pinball loss at tau 0.8 = 1.900
q=13: pinball loss at tau 0.8 = 1.100
q=15: pinball loss at tau 0.8 = 1.100
horizon 1: 80% interval coverage 0.95
horizon 2: 80% interval coverage 0.85
horizon 3: 80% interval coverage 0.60
pooled coverage 0.800
```

Losing 4 per unit short and 1 per unit left over gives the critical fractile \(4/(4+1)=0.8\), so the order should be the 80th percentile of demand. With ten equally likely values, the inverted empirical distribution reaches 0.8 at the eighth sorted value, 13. The pinball loss confirms it: ordering 10 costs 1.900 per period, while 13 and 15 both cost 1.100. The tie is informative. Moving from 13 to 15 adds 0.2 per unit for the eight demands at or below 13 and saves 0.8 per unit for the two demands at 15 and 20, and \(8(0.2)=2(0.8)\), so the loss is flat on that interval. Any order between 13 and 15 is equally good for this sample. The coverage table shows a separate failure. Pooled over horizons the 80 percent intervals cover exactly 0.800, but horizon 1 covers 0.95, horizon 2 covers 0.85 and horizon 3 covers only 0.60. A planner ordering three periods ahead would be short far more often than the pooled number promises.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def pinball(y, q, tau):
    residual = np.asarray(y) - q
    return np.maximum(tau * residual, (tau - 1) * residual)


def run_cases():
    demand = np.array([0.0, 1.0, 1.0, 2.0, 3.0, 8.0])
    under, over = 4.0, 1.0
    tau = under / (under + over)
    candidates = np.arange(9.0)
    loss = np.array(
        [
            np.mean(under * np.maximum(demand - q, 0) + over * np.maximum(q - demand, 0))
            for q in candidates
        ]
    )
    optimum = float(candidates[np.argmin(loss)])
    assert optimum == 3 and np.allclose(
        loss, (under + over) * np.array([pinball(demand, q, tau).mean() for q in candidates])
    )
    # Mean-accurate models need not minimize asymmetric inventory cost.
    mean_quantity = float(demand.mean())
    mean_cost = float(
        np.mean(
            under * np.maximum(demand - mean_quantity, 0)
            + over * np.maximum(mean_quantity - demand, 0)
        )
    )
    assert mean_cost > loss.min()
    # Calibration by horizon, not an aggregate whose errors can cancel.
    covered = np.array([[1, 1, 1, 1, 1], [0, 0, 1, 0, 1]], bool)
    return dict(
        critical_fractile=tau,
        optimal_quantity=optimum,
        minimum_cost=float(loss.min()),
        mean_policy_cost=mean_cost,
        coverage_by_horizon=covered.mean(axis=1).tolist(),
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    demand = np.array([0.0, 1.0, 1.0, 2.0, 3.0, 8.0])
    quantities = list(range(9))
    costs = [float(5 * pinball(demand, q, 0.8).mean()) for q in quantities]
    fig = go.Figure(go.Scatter(x=quantities, y=costs, mode="lines+markers"))
    fig.update_layout(
        title="Asymmetric inventory cost by quantity",
        xaxis_title="Quantity",
        yaxis_title="Mean cost",
        meta=dict(
            description="Underage costs four and overage one. The empirical decision cost is minimized at quantity three.",
            table=dict(
                columns=["Quantity", "Mean cost"],
                rows=[[q, c] for q, c in zip(quantities, costs, strict=True)],
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-009 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
```

## Primary references

- [Forecasting: Principles and Practice, reconciliation](https://otexts.com/fpp3/reconciliation.html)
- [Forecasting principles, accuracy](https://otexts.com/fpp3/accuracy.html)
