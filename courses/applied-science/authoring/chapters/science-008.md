## Coherence is a structural requirement

When a total equals the sum of its components, forecasts should respect that relationship if they are used together. A set of individually fitted predictions may violate it. Reconciliation adjusts those predictions to a coherent set while using a stated view of their relative uncertainty.

Let \(\mathbf b\) contain bottom-level series and let \(\mathbf S\) map them to every level of a hierarchy. Then a coherent vector satisfies \(\mathbf y=\mathbf S\mathbf b\). For base forecast \(\widehat{\mathbf y}\) and a positive-definite error covariance approximation \(\mathbf W\), weighted least squares solves

\[
\widetilde{\mathbf b}=(\mathbf S^{\mathsf T}\mathbf W^{-1}\mathbf S)^{-1}
\mathbf S^{\mathsf T}\mathbf W^{-1}\widehat{\mathbf y},
\qquad \widetilde{\mathbf y}=\mathbf S\widetilde{\mathbf b}.
\]

The code uses linear solves rather than explicitly forming the inverse of the smaller normal-equation matrix. The mathematical expression describes the solution; implementation should still consider conditioning and matrix structure. A covariance estimate from very little data may be unstable, singular or misleadingly precise.

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
