# Author a custom likelihood and prediction contract

Start with the observation unit, support and probability law. The package does not infer these from a function name. A row callback receives a float64 parameter tensor, a two-dimensional feature tensor and a one-dimensional target tensor. It returns one normalized NLL contribution per independent row. A complete-unit callback instead receives one whole bounded group's tensors and returns a scalar joint NLL. See [objective and unit contracts](objectives.md) before choosing between them.

Callbacks must be deterministic functions of their arguments and explicit configuration. A minibatch mean inside a supposedly per-row loss changes the objective when partitions or batch sizes change. Dropout, random sampling, mutable global state and parameter-dependent data filtering also need a deliberately different estimation contract. Passing shape checks alone does not prove a statistical model is correct.

## A complete original example

The package's `example_models.py` provides a small template with

\[
Y_i\sim N(\theta_0+\theta_1t_i^2,\sigma^2),
\]

where sigma is known configuration. This mean is nonlinear in the observed feature but remains linear in its fitted coefficients. It is useful for learning the interface without pretending to be a difficult nonlinear optimizer benchmark.

```python
from ds60_spark_likelihood import register_model_factory, resolve_model
from ds60_spark_likelihood.example_models import quadratic_model

register_model_factory("quadratic_mean", quadratic_model)
model = resolve_model("quadratic_mean", {"sigma": 0.5})
print(model.parameter_names, model.feature_names, model.descriptor())
```

The loss includes the Normal normalization terms. Its configured sigma is positive and finite; booleans and unknown fields are rejected. The prediction callback receives only parameters and features, and explicitly declares `conditional_mean`. There is no response label available to that callback and no automatically invented forecasting formula.

To create your own model, place the functions and factory in an importable module, validate its configuration, return `RegisteredModel` and explicitly register its stable ID. Deploy that module to every executor before fitting, for example through the normal environment build or an explicit Spark `addPyFile` preparation step. Fitting does not install or download code.

## Metadata and persistence

A registered model declares parameter names, ordered feature names, model version, row or complete-group factorization and prediction targets. Complete-group models additionally declare whether observation order is required and their maximum unit size. The resolved descriptor binds these choices, source identities and bounded JSON configuration into a fingerprint.

Persistent factories and callbacks must be named functions that resolve to the same symbol in importable source modules. Lambdas, closures and unsupported hidden state are rejected. Fingerprints include bounded JSON defaults, keyword defaults, explicit partial bindings and directly referenced JSON module constants, as well as module source and normalized live bytecode/constant structure. The live-code digest excludes absolute filenames and source line positions so a prepared module can be relocated, but it binds Python major/minor version: changing Python minor versions requires explicitly requalifying and recreating saved model identities. Replacing a callback code object is detected even if its source file has not changed. Configuration belongs in validated factory input and explicit partial arguments; do not depend on mutable external resources or runtime changes to imported libraries. Raw `TorchLoss` remains available for ephemeral exploratory callables, but an executable closure is not written into a saved JSON model. A saved model can be loaded only when its trusted registration exists and the expected identity matches. JSON artifacts do not import arbitrary module names or unpickle supplied code.

Source fingerprints are reproducibility checks, not signatures authenticating an untrusted artifact. Keep registered code and configuration validation under review, and restart/redeploy code consistently after source changes. Mutable external state violates the deterministic callback contract even if a function's name remains unchanged.

## Independent checks before distributed execution

For a new likelihood, compare at least one value with a separate distribution implementation or handwritten formula. Check gradients at multiple parameter values, including finite-difference step-size variation. Test invalid support, parameter transforms, normalization constants, unknown shapes and nonfinite output. Include a changed case that would fail a plausible incorrect implementation.

Then verify invariance under different partition and row-batch layouts for a row model. For a complete-group model, move entire units between partitions and verify the same joint objective; do not split units. Check sum versus weighted-mean semantics and ensure a global regularizer is applied once. Only after these numerical contracts pass should timing or larger-scale deployment be investigated.

## Prediction is a separate scientific target

The built-in Gaussian group model predicts `new_group_mean`, not a fitted latent effect for an observed group. A conditional same-group forecast would require a declared state/input contract and validation. Likewise, a point mean is not a prediction interval, and exponentiating a log mean is not generally the arithmetic mean of a lognormal outcome.

A model can intentionally omit prediction targets. It can still define a useful likelihood investigation, but generic transform must refuse it. Use an explicit target instead of letting an ML interface guess the scientific meaning.
