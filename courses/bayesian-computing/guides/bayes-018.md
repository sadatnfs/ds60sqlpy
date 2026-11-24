# bayes-018: Stan matrix regression and typed shape contracts

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-017`, `bayes-013`.

## Types and shapes are part of the model contract

Stan distinguishes scalars, vectors, row vectors, matrices and arrays. A compiler can use those distinctions to reject some malformed calculations before inference begins. Correct types still do not guarantee that rows represent the intended observational units or that a coefficient has the desired scientific interpretation.

The regression fixture has five observations and two design columns. The first column is an intercept and the second contains values from minus two to two. The unknown coefficient vector has length two, and the predicted mean vector is \(\mu=X\beta\), with shape five. Observation scale is a separate positive parameter.

The self-contained constants are in `transformed data`. In a reusable project, N, X and y would normally be declared in a data block and supplied separately. Keeping that distinction explicit prevents a learner from confusing a bounded classroom convenience with the preferred structure of a general analysis program.

## Key terms

- **Stan container types:** The distinct scalar, vector, row_vector, matrix and array types that let the compiler reject malformed calculations.
- **Design matrix:** The N by K matrix X of predictors, here an intercept column and a covariate column.
- **Linear predictor:** The mean vector mu = X beta, whose shape must match the number of observations.
- **New mean versus new outcome:** The difference between predicting mu at a new x and predicting an observation that also includes noise.

## Worked case 1: follow one observation through the model

The code constructs the design matrix row by row using Stan's one-based indexing. `beta[1]` is the intercept and `beta[2]` is the slope. `transformed parameters` calculates the full mean vector, and a vectorized normal statement contributes the likelihood for all observed outcomes.

The prior `beta ~ normal(0,2)` applies independent normal density contributions to the vector elements under this model. It does not introduce a full multivariate covariance matrix. If correlated coefficient priors are intended, that structure must be declared explicitly.

Each observed value contributes `normal_lpdf(y[n] | mu[n], sigma)` to the stored log-likelihood vector. Retaining those contributions supports later predictive evaluation only when the chosen factorization matches the held-out unit. Repeated or clustered observations require a different interpretation of which units are left out.

## Worked case 2: distinguish a new mean from a new outcome

The generated quantities calculate the mean at a covariate value .5 and a random future outcome around that mean. Across posterior draws, the new mean varies because the coefficients are uncertain. The future outcome varies for that reason and because of the conditional observation noise.

For an appropriate predictive target, the total variance includes the expected conditional variance plus variance in the conditional mean. Inspecting only `new_mean` would omit observation variation. Conversely, using the spread of `new_outcome` as uncertainty about the regression mean would conflate two targets.

The fixture's covariate .5 lies within the observed design range. Predicting far outside that range relies more heavily on the assumed linear relationship and priors. A technically valid matrix multiplication does not validate extrapolation or a causal intervention on the covariate.

## Diagnose compiler and model failures separately

A mismatch between the number of design columns and coefficient length is a shape error. A misplaced row/vector transpose can cause a type error or express a different calculation. Read the compiler's line and column information against the exact submitted source; do not assume a diagnostic from an older saved run refers to a later edited pad.

A model can compile while being poorly identified. Nearly duplicate columns can create a strong posterior correlation, as the earlier PyMC geometry tutorial demonstrated. Weak data on sigma can also make prior choices important. Examine actual sampler diagnostics and predictive behavior after type correctness is established.

Scale priors in the units of the variables. A prior standard deviation of two on a slope has different meaning when the covariate is measured in meters rather than millimeters. If preprocessing standardizes a variable, retain that transformation with the model and apply it consistently for prediction.

## Answered scientific discussion

**Does vectorization change the independence assumption?** The vectorized normal statement expresses the elementwise density contributions supplied by that distribution interface. It is a concise implementation of this model, not a replacement for reviewing its conditional independence structure.

**Why retain a tiny matrix example after learning a library regression?** It exposes indices, shapes, priors, deterministic transforms and predictions in one compiled program. Those contracts remain important when a model grows large enough that a dimension mistake is harder to recognize from its output.

## Worked example: Shape contract and two interval widths at a new design row

```python
import numpy as np

X = np.array([[1, 0.0], [1, 1.0], [1, 2.0], [1, 3.0], [1, 4.0]])
y = np.array([1.2, 2.1, 2.8, 4.2, 4.9])
sigma = 0.3  # treat the noise scale as known
V = sigma**2 * np.linalg.inv(X.T @ X)
beta = np.linalg.solve(X.T @ X, X.T @ y)
print("X", X.shape, "beta", beta.shape, "X @ beta", (X @ beta).shape)
for x0 in (np.array([1, 2.0]), np.array([1, 8.0])):
    sd_mean = np.sqrt(x0 @ V @ x0)
    sd_new = np.sqrt(sd_mean**2 + sigma**2)
    print(
        f"x={x0[1]}: mean {x0 @ beta:.3f}, sd of mean {sd_mean:.3f}, sd of new outcome {sd_new:.3f}"
    )
```

Observed output:

```text
X (5, 2) beta (2,) X @ beta (5,)
x=2.0: mean 3.040, sd of mean 0.134, sd of new outcome 0.329
x=8.0: mean 8.740, sd of mean 0.585, sd of new outcome 0.657
```

The shapes line restates the Stan type contract in NumPy: a matrix with 5 rows and 2 columns times a vector of length 2 returns a vector of length 5, one linear predictor per observation. Declaring those dimensions in Stan makes a mismatch a compile or data error instead of silent broadcasting. With the noise scale held at 0.3, the coefficients have a normal posterior, and two different predictive questions follow. At \(x=2\), the center of the design, the mean line is known to within a standard deviation of 0.134, but a new outcome there has standard deviation \(\sqrt{0.134^2+0.3^2}=0.329\), dominated by observation noise. At \(x=8\), four units beyond the last observed input, as far again as the data's own range, uncertainty about the line grows to 0.585 and the new-outcome standard deviation to 0.657; extrapolation has made parameter uncertainty the larger part. A Stan generated quantities block that draws normal_rng(mu, sigma) answers the second question, while reporting mu alone answers the first.

## Complete reproducible program

The prepared Stan pad compiles `main.stan` and samples two chains with 100 warmup and 100 retained draws each. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. These teaching-sized chains can fail the convergence screen from `bayes-006` (R-hat below 1.01, at least 100 bulk and tail effective draws per chain, no divergences); read the printed diagnostics against it before interpreting any estimate. Runtime: `stan-cpu`.

```stan
transformed data {
  int N = 5;
  matrix[N, 2] X;
  vector[N] y = [-1.8, -0.7, 0.4, 1.8, 2.9]';
  for (n in 1 : N) {
    X[n, 1] = 1;
    X[n, 2] = n - 3;
  }
}
parameters {
  vector[2] beta;
  real<lower=0> sigma;
}
transformed parameters {
  vector[N] mu = X * beta;
}
model {
  beta ~ normal(0, 2);
  sigma ~ normal(0, 0.5);
  y ~ normal(mu, sigma);
}
generated quantities {
  real new_mean = beta[1] + 0.5 * beta[2];
  real new_outcome = normal_rng(new_mean, sigma);
  vector[N] log_lik;
  for (n in 1 : N)
    log_lik[n] = normal_lpdf(y[n] | mu[n], sigma);
}
```

## Primary references

- [Stan regression models](https://mc-stan.org/docs/stan-users-guide/regression.html)
