# Fixed model boundary, schema version 1

Run from a fresh prepared R process:

```bash
TMB_BUILD_DIR=/opt/tmb-models Rscript --vanilla R/evaluate.R "$PWD" request.json
```

The driver accepts an existing JSON file no larger than 10 MB. Model names are
allowlisted in `R/api.R`. Evaluation cannot compile arbitrary code, load arbitrary
libraries, install packages, call a remote endpoint or choose compiler flags.
`TMB_BUILD_DIR` is a trusted launcher setting, not a field from the request.
It points to libraries compiled together for this exact R/TMB/Matrix/architecture.

```json
{
  "schema_version": 1,
  "model": "normal_mean",
  "data": { "y": [1, 2, 4, 7] },
  "parameters": { "mu": 0, "log_sigma": 0 },
  "theta": [2.2, 0.3],
  "random": null
}
```

`parameters` supplies tape shapes and starts. `theta` has the exact flattened
fixed-parameter order declared in the C++ template, after removing `random`.
The interface permits `random: "u"` only for `random_intercept`, `ar1` and
`panel_trend`. `random: null` instead returns the joint objective, with latent
states in `theta`. This changes the mathematical target and must be recorded.

For a group-integrated normal intercept, pass zero-based `group`, at least two
observations and one `u` start per group. Fixed order is `beta, log_sigma,
log_tau`; the returned gradient is the derivative of the Laplace-marginal NLL.
This Gaussian model has an exact dense marginal oracle in `tests/acceptance.R`.
Groups with shared latent covariance cannot be split into independent calls.

Outputs are detached JSON values with schema, model, NLL, gradient, parameter
names, observation count, R/TMB/architecture and source MD5 identity. MD5 here is
an identity checksum, not a security signature. Retain the build source SHA256
and dependency locks separately for publication. One call makes one objective;
there is no hidden cache of fitted parameters. R external pointers must never
cross process or Spark serialization boundaries.
