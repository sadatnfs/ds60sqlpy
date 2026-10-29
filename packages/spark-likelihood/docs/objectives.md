# Define the statistical unit before the distributed calculation

Two protocols deliberately remain separate. `TorchLoss` returns a vector with one loss for each independent observation. `TorchUnitLoss` returns one scalar for a complete independent group, sequence or other declared joint unit. A scalar group likelihood cannot be sent through the row kernel, and splitting a group to meet a batch limit changes the model.

For rows with fixed weights, the sum objective is

\[
L(\theta)=\sum_i w_i\ell_i(\theta).
\]

The weighted mean divides by the global weight sum, not the number of partitions or the unweighted average of local means. Zero-weight records still need valid data and a finite model evaluation. Negative weights, nonfinite values and integral inputs that cannot be represented exactly as float64 are rejected. Exactly representable large integers remain valid; explicitly supplied finite floating values retain their declared value.

For complete units, the corresponding objective is

\[
L(\theta)=\sum_g w_g\ell_g(\theta).
\]

There is one weight per joint unit. `weighted_mean` divides by the sum of these unit weights. `row_count` and `unit_count` therefore describe different quantities. Frequency weights, importance weights and sampling weights can have different inferential interpretations even when their arithmetic is identical. An inverse Hessian does not automatically provide the right uncertainty for every weighted estimator.

## Exact Gaussian random-intercept example

The built-in `gaussian_random_intercept` model has fixed coordinates `(beta, log_sigma, log_tau)`. One complete group has

\[
Y_g\sim N\left(\beta\mathbf1,\;\sigma^2 I+\tau^2\mathbf1\mathbf1^\top\right).
\]

The implementation uses Torch's actual multivariate Normal and automatic differentiation. Its independent validation uses a rank-one covariance identity. With \(s=\sigma^2\), \(t=\tau^2\), group size \(n\), mean \(\overline y\) and centered sum of squares \(S_c\), its NLL is

\[
\frac12\left[n\log(2\pi)+(n-1)\log s+\log(s+nt)
 +\frac{S_c}{s}+\frac{n(\overline y-\beta)^2}{s+nt}\right].
\]

This Gaussian marginal is exact. It is not a generic Laplace approximation engine. Cross-group latent covariance destroys this factorization and is unsupported by the additive complete-unit adapter. Dense covariance work also has a cost: the default model bound is 256 observations per unit. Increasing a declared bound requires appropriate resource and numerical checks, not a throughput promise.

```python
from ds60_spark_likelihood import CompleteUnit, SparkUnitObjective, resolve_model

model = resolve_model("gaussian_random_intercept")
units = [
    CompleteUnit("group-a", [(0.1,), (0.4,)], weight=1.0),
    CompleteUnit("group-b", [(1.0,), (1.2,), (1.5,)], weight=2.0),
]
rdd = spark.sparkContext.parallelize(units, 2)
with SparkUnitObjective(rdd, model.loss, reduction="weighted_mean") as objective:
    result = objective.evaluate([0.5, -0.2, -0.5])
    print(result.value, result.gradient, result.row_count, result.unit_count)
```

Unit IDs must be unique. The adapter checks duplicates in Spark and collects only a bounded duplicate diagnostic, partition metadata and numerical summaries. It retains data/order digests to reject changed units during repeated evaluations. A cache is not a durable transaction or immutable source snapshot: prepare a deterministic input lineage and honor the declared grouping and ordering.

## Prediction targets remain explicit

A likelihood does not define every desired forecast automatically. The registered group model offers `new_group_mean`, equal to beta under its model. It does not return conditional fitted random effects for existing groups or prediction intervals. Normal, linear/nonlinear Gaussian, logistic and Poisson built-ins declare their own point targets.

Prediction callbacks receive parameters and feature rows, never target labels. Models without a registered target fail rather than receiving an invented generic prediction. An observed-group conditional forecast would need a separately defined state/data contract and its own validation.

## Optimization evidence

The driver L-BFGS-B helper is for at most 64 parameters. It records convergence, objective calls, raw gradient norms, projected gradient norms and active bounds. A bound-constrained optimum can have a nonzero raw gradient; the projected gradient answers the relevant optimization question. Neither criterion proves model identification, correct data collection or calibrated uncertainty.

Large neural-network training uses the separate [distributed training integrations](distributed-training.md), with its own sharding and process-failure requirements. It is not implemented by gathering millions of network parameters into this low-dimensional driver optimizer.
