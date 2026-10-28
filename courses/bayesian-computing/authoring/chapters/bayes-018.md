## Types and shapes are part of the model contract

Stan distinguishes scalars, vectors, row vectors, matrices and arrays. A compiler can use those distinctions to reject some malformed calculations before inference begins. Correct types still do not guarantee that rows represent the intended observational units or that a coefficient has the desired scientific interpretation.

The regression fixture has five observations and two design columns. The first column is an intercept and the second contains values from minus two to two. The unknown coefficient vector has length two, and the predicted mean vector is \(\mu=X\beta\), with shape five. Observation scale is a separate positive parameter.

The self-contained constants are in `transformed data`. In a reusable project, N, X and y would normally be declared in a data block and supplied separately. Keeping that distinction explicit prevents a learner from confusing a bounded classroom convenience with the preferred structure of a general analysis program.

## Worked case 1: follow one observation through the model

The code constructs the design matrix row by row using Stan's one-based indexing. `beta[1]` is the intercept and `beta[2]` is the slope. `transformed parameters` calculates the full mean vector, and a vectorized normal statement contributes the likelihood for all observed outcomes.

The prior `beta ~ normal(0,2)` applies independent normal density contributions to the vector elements under this model. It does not introduce a full multivariate covariance matrix. If correlated coefficient priors are intended, that structure must be declared explicitly.

Each observed value contributes `normal_lpdf(y[n] | mu[n], sigma)` to the stored log-likelihood vector. Retaining those contributions supports later predictive evaluation only when the chosen factorization matches the held-out unit. Repeated or clustered observations require a different interpretation of which units are left out.

## Worked case 2: distinguish a new mean from a new outcome

The generated quantities calculate the mean at a covariate value .5 and a random future outcome around that mean. Across posterior draws, the new mean varies because the coefficients are uncertain. The future outcome varies for that reason and because of the conditional observation noise.

For an appropriate predictive target, the total variance includes the expected conditional variance plus variance in the conditional mean. Inspecting only `new_mean` would omit observation variation. Conversely, using the spread of `new_outcome` as uncertainty about the regression mean would conflate two targets.

The fixture's covariate .5 lies within the observed design range. Predicting far outside that range relies more heavily on the assumed linear relationship and priors. A technically valid matrix multiplication does not validate extrapolation or a causal intervention on the covariate.

## Diagnose compiler and model failures separately

A mismatch between the number of design columns and coefficient length is a shape error. A misplaced row/vector transpose can cause a type error or express a different calculation. Read the compiler's line and column information against the exact submitted source; do not assume a diagnostic from an older receipt refers to a later edited pad.

A model can compile while being poorly identified. Nearly duplicate columns can create a strong posterior correlation, as the earlier PyMC geometry tutorial demonstrated. Weak data on sigma can also make prior choices important. Examine actual sampler diagnostics and predictive behavior after type correctness is established.

Scale priors in the units of the variables. A prior standard deviation of two on a slope has different meaning when the covariate is measured in meters rather than millimeters. If preprocessing standardizes a variable, retain that transformation with the model and apply it consistently for prediction.

## Answered scientific discussion

**Does vectorization change the independence assumption?** The vectorized normal statement expresses the elementwise density contributions supplied by that distribution interface. It is a concise implementation of this model, not a replacement for reviewing its conditional independence structure.

**Why retain a tiny matrix example after learning a library regression?** It exposes indices, shapes, priors, deterministic transforms and predictions in one compiled program. Those contracts remain important when a model grows large enough that a dimension mistake is harder to recognize from its output.
