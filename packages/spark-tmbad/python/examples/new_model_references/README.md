# New-model mathematical references

`rows-v3.json` and `gaussian-v3.json` are unchanged independent 70-digit reference outputs. `supplement-v3.json` adds nine series/switch and three extreme-scale Gaussian cases using the independently implemented observation covariance and 80-digit arithmetic. Inputs denote exact binary64 values; output strings retain40 significant digits. All generating code was original MIT code.

Reference-generation flags describe that stage and are not runtime acceptance. `native-arm64-v4.json` is the separate actual local native qualification for its exact build and binary identity. It does not assert Spark, optimization, posterior sampling, distributed workers or cloud execution. Read `../../docs/NEW-MODEL-CHECKS.md` for commands, tolerances and limits.

Original reference source hashes and dependency versions are retained inside each JSON. The original reference outputs are preserved separately from the native answers. No native output was used to construct expected values.

The unchanged [local Spark receipt](spark-local-new-models-v1.json) records the actual installed 0.2.0 Python/JVM/native check of 18 declared parameter/data points across the nine added models on Linux ARM64, Spark 4.0.1 `local[2]`. It binds validator, manifest, model and reference identities. Its scope is fixed evaluation and response-free marginal prediction/forecasting with provenance; it makes no optimizer, posterior, repeated-data calibration, separate-worker or cloud qualification claim.
