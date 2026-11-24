# science-008: Coherent hierarchical forecasts and covariance-weighted reconciliation

Tutorial mode. Stage: intermediate. Direct prerequisites: `science-007`.

## Coherence is a structural requirement

When a total equals the sum of its components, forecasts should respect that relationship if they are used together. A set of individually fitted predictions may violate it. Reconciliation adjusts those predictions to a coherent set while using a stated view of their relative uncertainty.

Let \(\mathbf b\) contain bottom-level series and let \(\mathbf S\) map them to every level of a hierarchy. Then a coherent vector satisfies \(\mathbf y=\mathbf S\mathbf b\). For base forecast \(\widehat{\mathbf y}\) and a positive-definite error covariance approximation \(\mathbf W\), weighted least squares solves

\[
\widetilde{\mathbf b}=(\mathbf S^{\mathsf T}\mathbf W^{-1}\mathbf S)^{-1}
\mathbf S^{\mathsf T}\mathbf W^{-1}\widehat{\mathbf y},
\qquad \widetilde{\mathbf y}=\mathbf S\widetilde{\mathbf b}.
\]

The code uses linear solves rather than explicitly forming the inverse of the smaller normal-equation matrix. The mathematical expression describes the solution; implementation should still consider conditioning and matrix structure. A covariance estimate from very little data may be unstable, singular or misleadingly precise.

## Key terms

- **Coherence:** The requirement that forecasts respect aggregation constraints, so every total equals the sum of its components.
- **Summing matrix:** The matrix S that maps bottom-level series b to every level of the hierarchy, so a coherent vector satisfies y = Sb.
- **MinT reconciliation:** Weighted least squares that adjusts base forecasts to a coherent set using an error covariance approximation W.
- **Error covariance approximation:** The positive-definite matrix W expressing relative forecast uncertainty; a small-sample estimate can be unstable or singular.

## Worked case 1: reconcile an inconsistent total

There are two bottom-level series and one total, so the rows of \(\mathbf S\) are \([1,1]\), \([1,0]\) and \([0,1]\). The base forecast is \([12,4,5]\). Under an identity covariance matrix, reconciliation produces \([11,5,6]\). The total moves down by one and each component moves up by one. All three predictions contribute to the compromise.

A second assertion sends an already coherent vector \([9,4,5]\) through the same transformation and checks that it is unchanged. This fixed-point property is a useful independent test of the algebra. A procedure that changes every coherent input may be implementing additional assumptions beyond reconciliation.

The weights matter. When the total forecast is assigned much smaller error variance than the two components, the reconciled total remains closer to 12. That is appropriate only if the relative uncertainty claim is defensible. Choosing a small variance because a total is politically important confuses preference with predictive precision; a decision constraint should be represented explicitly instead.

## Worked case 2: coherence does not guarantee physical plausibility

The second fixture supplies a negative component. Unconstrained reconciliation can preserve a negative bottom-level value while satisfying the summing identities exactly. If the series represents a nonnegative quantity such as demand, that may be inadmissible.

The code separately solves a nonnegative least-squares problem. It checks both the structural identity and the sign constraint. This constrained solution is a different optimization problem. Simple clipping after reconciliation can break coherence again, while clipping before reconciliation can still lead to a negative adjusted component. Treat all required constraints as part of the actual procedure.

Whether negative values are impossible depends on the target. Net flows, signed balances or changes can legitimately be negative. Imposing nonnegativity on those targets can introduce systematic error. The decision to constrain a forecast belongs in the data-definition contract, not in an aesthetic preference for an upward-only chart.

## Estimate the covariance for the intended horizon

Forecast errors can be correlated across series and can change by horizon. An identity matrix is a transparent baseline, not an automatic MinT estimate. Estimate or regularize a covariance appropriate to the forecast procedure and evaluation horizon, using only eligible historical errors. Shrinkage or structured approximations can be necessary when the number of series is large relative to the number of independent error vectors.

Evaluate reconciled and unreconciled procedures at the same origins, with losses reported at relevant levels. Improving the total while substantially damaging important components may not be desirable. A single unweighted average across thousands of small series can hide that tradeoff. Likewise, point-forecast coherence does not automatically make independently computed prediction intervals jointly coherent.

## Answered scientific discussion

**Why use aggregate forecasts if bottom-level forecasts already sum correctly?** Aggregates can contain a stronger signal-to-noise ratio or different useful predictors. Reconciliation combines their information under an explicit uncertainty model. It is not a theorem that every aggregate forecast improves every component.

**What should be delivered with a reconciled forecast?** Retain the hierarchy matrix, series definitions, base forecasts, covariance method, constraints, adjusted predictions and backtest. If a business reorganization changes the hierarchy, revise that structural contract before comparing the new output with an old series definition.

## Worked example: OLS and WLS reconciliation of a two-region total

```python
import numpy as np

S = np.array([[1, 1], [1, 0], [0, 1]], float)  # rows: total, region A, region B
base = np.array([100.0, 70.0, 20.0])  # incoherent: 70 + 20 != 100


def reconcile(W):
    Wi = np.linalg.inv(W)
    P = np.linalg.solve(S.T @ Wi @ S, S.T @ Wi)
    return S @ P @ base


ols = reconcile(np.eye(3))
wls = reconcile(np.diag([1.0, 25.0, 1.0]))  # region A forecast is noisy
print("base:", base, " incoherence", base[0] - base[1:].sum())
print("OLS :", ols.round(3))
print("WLS :", wls.round(3))

low_total = np.array([10.0, 2.0, 20.0])  # total far below children
print("OLS with small total:", (S @ np.linalg.solve(S.T @ S, S.T @ low_total)).round(3))
```

Observed output:

```text
base: [100.  70.  20.]  incoherence 10.0
OLS : [96.667 73.333 23.333]
WLS : [99.63  79.259 20.37 ]
OLS with small total: [14. -2. 16.]
```

The base forecasts are incoherent by 10 units, since the regions sum to 90 while the total says 100. Ordinary least-squares reconciliation splits that gap evenly over the three series: the total drops by \(10/3\) to 96.667 and each region rises by the same amount, to 73.333 and 23.333. That is reasonable only if every base forecast is equally reliable. Giving region A a variance 25 times larger makes it the cheap place to absorb error, so the weighted projection moves A by more than 9 units to 79.259 and barely touches the total (99.63) and region B (20.37). The final line shows why coherence is not plausibility. With a total of 10 and children of 2 and 20, the gap is \(-12\) and OLS shifts each series by 4, producing a region A forecast of \(-2\). The result adds up perfectly and is impossible for nonnegative demand. A nonnegativity constraint, or a better base forecast for the total, is needed.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def reconcile(base, summing, covariance):
    s = np.asarray(summing, float)
    w = np.asarray(covariance, float)
    precision = np.linalg.solve(w, np.eye(len(w)))
    bottom = np.linalg.solve(s.T @ precision @ s, s.T @ precision @ np.asarray(base))
    return s @ bottom


def run_cases():
    s = np.array([[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
    base = np.array([12.0, 4.0, 5.0])
    rec = reconcile(base, s, np.eye(3))
    assert np.allclose(rec, [11.0, 5.0, 6.0]) and rec[0] == rec[1] + rec[2]
    coherent = np.array([9.0, 4.0, 5.0])
    assert np.allclose(reconcile(coherent, s, np.eye(3)), coherent)
    certain_total = reconcile(base, s, np.diag([0.01, 4, 4]))
    assert abs(certain_total[0] - 12) < abs(rec[0] - 12)
    # Coherence alone can be compatible with an implausible negative component.
    unrestricted = reconcile([1.0, -8.0, 4.0], s, np.eye(3))
    constrained = optimize.lsq_linear(s, np.array([1.0, -8.0, 4.0]), bounds=(0, np.inf)).x
    assert unrestricted[1] < 0 and np.all(constrained >= 0)
    return dict(
        ols=rec.tolist(), weighted=certain_total.tolist(), nonnegative_bottom=constrained.tolist()
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    labels = ["Total", "First component", "Second component"]
    base = [12, 4, 5]
    adjusted = evidence["ols"]
    fig = go.Figure(
        [
            go.Bar(name="Base forecast", x=labels, y=base),
            go.Bar(name="Coherent forecast", x=labels, y=adjusted),
        ]
    )
    fig.update_layout(
        title="Forecast coherence under identity covariance",
        barmode="group",
        meta=dict(
            description="Base total 12 differs from components 4+5; reconciliation yields 11=5+6.",
            table=dict(
                columns=["Series", "Base", "Coherent"],
                rows=[list(row) for row in zip(labels, base, adjusted, strict=True)],
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-008 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
```

## Primary references

- [Forecasting: Principles and Practice, reconciliation](https://otexts.com/fpp3/reconciliation.html)
- [Forecasting principles, accuracy](https://otexts.com/fpp3/accuracy.html)
