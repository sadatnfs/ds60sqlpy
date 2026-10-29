# Register and test a custom TMB model for Spark

A custom model enters this companion during an explicit image build. Runtime requests contain a prepared model ID, finite numeric data and parameter values. They cannot contain C++ source, R expressions, library paths or compiler flags. This separation makes the source under review concrete and lets each result identify the exact compiled artifact used.

## 1. State the observation unit and objective

Decide whether the objective factors over independent rows or over complete independent groups. For shared parameters \(\theta\), the supported global contract is

\[
\mathcal L(\theta)=\sum_g\mathcal L_g(\theta),\qquad
\nabla\mathcal L(\theta)=\sum_g\nabla\mathcal L_g(\theta).
\]

A unit may contain multiple rows. If its latent variables share covariance with another unit, this factorization generally fails. A spatial latent field, a global Gaussian process or a random effect shared across arbitrary Spark partitions cannot be made additive by declaring a new unit identifier. Keep the full dependent block together if it fits the bounded process, derive a mathematically valid alternative decomposition, or use another distributed numerical method.

The `factorization` registry value documents the allowed scientific unit. The current adapter accepts `independent_rows` and `complete_groups` only. This is a declared modeling contract, not a statistical test that proves independence.

## 2. Learn from the two prepared templates

[models/normal_mean.cpp](models/normal_mean.cpp) declares observations `y`, fixed `mu` and `log_sigma`, and returns the complete Normal NLL. The scale is exponentiated inside the templated objective. With \(s=\log\sigma\),

\[
\mathcal L=n\{s+\tfrac12\log(2\pi)\}
 +\tfrac12 e^{-2s}\sum_i(y_i-\mu)^2.
\]

Its analytic score is an independent test oracle. A custom transform of a parameter needs chain-rule derivatives but does not add a likelihood Jacobian merely because the optimizer coordinate changes.

[models/random_intercept.cpp](models/random_intercept.cpp) declares a complete group's observations, zero-based integer group indices, shared fixed `beta`, `log_sigma`, `log_tau`, and random vector `u`. Its joint model is

\[
u_g\sim N(0,\tau^2),\qquad y_{gi}\mid u_g\sim N(\beta+u_g,\sigma^2).
\]

The registry specifies `u` as random. TMB integrates that vector using its Laplace construction. For this Gaussian latent model the integral is exact, with marginal covariance \(\sigma^2I+\tau^2\mathbf1\mathbf1^\top\). `laplace_oracle` in `spark_tmb/fixed_bridge.py` uses a separate rank-one matrix derivation to check the value and all three fixed-parameter derivatives. For a non-Gaussian latent model, Laplace is generally an approximation, and derivative correctness does not establish approximation accuracy.

The library does not send a TMB objective or external pointer to Spark. Every evaluation creates a fresh R process, loads the declared native library, creates the tape, evaluates it, returns detached JSON and exits. Repeated tape construction costs time; this teaching implementation favors explicit ownership and correctness over a hidden process cache.

## 3. Declare a model in the registry

A model's source must be `models/MODEL_ID.cpp`. Model IDs and field names are restricted identifiers. Add its description to `registry.json`:

```json
{
  "source": "models/normal_mean.cpp",
  "factorization": "independent_rows",
  "response": "y",
  "data": {"y": "real_vector"},
  "fixed_parameters": ["mu", "log_sigma"],
  "random": null
}
```

This is the actual prepared Normal entry, not a second hidden model. To add a different trusted model, create a new ID and source and derive its own objective. `fixed_parameters` is the canonical flattened coordinate order. Registry v2 additionally declares scalar or fixed-size vector blocks in `parameter_layout`; native repeated vector names are checked separately from canonical coordinate names. Additional predictors can be declared as `real_vector`; integer categories use `integer_vector`. All observation vectors must be finite and equally long. The current maximum is 4,096 observations per unit payload and 64 fixed parameters.

For a group latent vector, declare `random` with its name and the integer group field. Its starts are constructed as zeros, one for each contiguous zero-based local group index. At most 256 groups are allowed per payload. The current API does not accept parameter matrices, data-inferred parameter dimensions, arbitrary random structures or user-provided R code. The registry and ABI receipt are installed application configuration, not fields accepted from a learner's numeric request.

## 4. Compile once and bind the artifact

Run the workshop build. `prepare_models.py` validates the registry, compiles each trusted template serially with the pinned TMB/CppAD environment, and writes `receipt.json` only after success. The receipt records:

- SHA-256 for the registry, each original C++ template and each compiled `.so`.
- R, TMB, Matrix and platform architecture identities.
- The fixed library filename associated with each model ID.

At runtime, changed source or library bytes fail the receipt check. R additionally compares its actual ABI metadata before creating an objective. A receipt is an integrity and reproducibility check, not a claim that the model's scientific assumptions are correct. Rebuild after a model change. Do not patch the checksum to make an old binary appear compatible.

## 5. Evaluate locally before introducing Spark

Inside the prepared project environment:

```python
from spark_tmb import evaluate_prepared

result = evaluate_prepared(
    "normal_mean",
    {"y": [1.0, 2.0, 4.0, 7.0]},
    [2.2, 0.3],
)
print(result["value"], result["gradient"])
```

Check an independent closed form or established distribution implementation, then check finite differences at several nontrivial parameter values. Include support failures, boundary cases and any latent approximation assumptions. A finite result and a small optimization score do not prove identification. The `registered-models` case supplies actual checks for both original templates.

## 6. Choose shared or independent estimation

The Spark adapter consumes an RDD of complete units:

```python
from spark_tmb import SparkTMBObjective

units = [
    {"unit_id": "subject-a", "data": {"y": [1.0, 2.0, 4.0]}},
    {"unit_id": "subject-b", "data": {"y": [2.0, 5.0, 8.0]}},
]
rdd = spark.sparkContext.parallelize(units, 2).cache()
objective = SparkTMBObjective(rdd, "normal_mean")
shared = objective.evaluate([2.2, 0.3])
separate = objective.fit_independent_units([0.0, 0.0])
```

`shared` is one global sum objective at one parameter vector. A driver optimizer may repeatedly call it. `separate` contains two separately optimized models using bounded `nlminb`; it is not a pooled model. Each fit must meet both its convergence condition and the declared score threshold, otherwise the call fails instead of silently retaining only favorable groups.

The materialized ledger records unique unit IDs, row counts and data checksums. Subsequent evaluations or fits reject changed data. There are at most 64 partitions and 256 units per partition in this bounded teaching adapter. Persist deterministic input if repeated evaluations would otherwise reread a changing source. Real remote clusters additionally need the exact prepared environment on every executor, compatible native libraries, resource budgeting, task retries and operational acceptance. A local passing case does not qualify those deployment concerns.

## Typed parameter blocks and declared prediction

The registered `linear_regression` model declares `beta` as a two-element real vector with canonical coordinates `beta_0`, `beta_1`, followed by scalar `log_sigma`. Python sends a flat parameter vector; the validated layout reconstructs `list(beta=c(...), log_sigma=...)` in R and checks TMB's native order. This avoids pretending two repeated native names identify distinct scientific coordinates. Sizes are explicit build-time declarations, not guessed from whichever DataFrame happens to arrive.

Prediction is opt-in. Its registry section declares a target, numeric input fields, their training-feature roles, a named C++ `REPORT`, and trusted typed constants selecting a prediction-only branch. Prediction constructors must preserve the full C++ data interface and its types. They cannot fabricate response observations: the response vector is empty, and the native prediction branch never reads it. The two prepared models produce a conditional mean only; neither claims predictive intervals or latent-state conditioning.

```python
from spark_tmb import predict_prepared

constant = predict_prepared("normal_location", {}, [2.0, 0.0], n_rows=3)
linear = predict_prepared(
    "linear_regression",
    {"x_prediction": [-1.0, 0.0, 2.0]},
    [1.0, 2.0, -0.5],
    n_rows=3,
    target="conditional_mean",
)
print(constant["prediction"], linear["prediction"])
```

The first model uses the explicit row count because it has no predictors. The second requires exactly the declared predictor vector. Supplying response labels, a different target or a mismatched row count fails. A model without a prediction declaration also fails rather than receiving an invented generic formula. See [DATAFRAME-ML.md](DATAFRAME-ML.md) for the corresponding fit/transform and persistence workflow.
