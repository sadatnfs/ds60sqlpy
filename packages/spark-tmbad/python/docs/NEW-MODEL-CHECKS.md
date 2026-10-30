# Checks for the added 0.2 models

The 0.2 registry adds binomial logistic, beta-binomial, beta regression, lognormal regression, Student-t regression, zero-truncated Poisson, zero-inflated Poisson, hurdle Poisson and a correlated Gaussian random intercept/slope model. These check programs use fixed, declared parameter points. They distinguish direct native mathematics from Spark adapter execution and from fitting studies.

The row references retain two or more parameter/data points per family, normalized log densities, gradients, Hessians and response-free future moments. They include zero trials, mixture zeros, zero weights, tiny positive rates, extreme scales and changed parameters. The correlated model integrates a bivariate Gaussian effect exactly. Its reference uses a dense observation covariance, independently of the native augmented QR computation. Existing-group prediction conditions on complete supplied history. New-group prediction integrates the Gaussian prior. Returned variances are marginal observation variances; the interface does not return the reference's off-diagonal joint covariance.

## Direct native comparison

Run this in native Linux with the prepared runtime at the path recorded by its manifest. The runner uses only Python's standard library and the executable protocol. It verifies the binary hash and the complete live model description before comparing any mathematical result. It starts a fresh process for each request and requires successful termination before accepting a reply.

```sh
python python/examples/validate_new_model_oracles.py \
  --manifest /opt/spark-tmbad/artifact.json \
  --rows python/examples/new_model_references/rows-v3.json \
  --gaussian python/examples/new_model_references/gaussian-v3.json \
  --supplement python/examples/new_model_references/supplement-v3.json \
  --output /out/fresh-native-new-model-check
```

The output directory must not exist. It receives the exact requests/replies and a qualification document, including failure information. Its accepted scope is values, gradients, Hessians, target moments and intended domain refusals. The original row-oracle ordinary and tiny-positive thresholds are preserved. The beta-binomial endpoint regression has a separately specified absolute threshold that detects the previously observed subtractive gamma cancellation. Thresholds are not tuned after a run.

Local ARM64 execution on build `5d3cfec94ba65f7c39711f109b09dc3ec6883bcb062e68cecb50345434a35383`, binary SHA256 `3351a1619ec13d7eb19f2d80333146b3cbd156f4ae9e940a338b99fed4cac357`, passed 50 parameter/data cases and ten domain refusals through 170 serial native requests. This receipt applies to those exact bytes. It does not transfer to another artifact or establish Spark, optimizer or managed-runtime acceptance.

Tiny derivatives deserve separate interpretation. The Student-t extreme-scale case has Hessian entries near 1e-40 to 1e-28 that may incur cancellation noise below 1.7e-24 or round to zero. This satisfies the stated absolute comparison criterion; it does not establish uniform relative precision for every near-zero entry. Values below binary64 range cannot be represented by the executable. The nonlinear random-amplitude model with multiple stationary modes is not registered or included in this check.

## Installed Python facade and Spark

Use a noneditable 0.2 wheel and the matching native/JVM artifact. Start a fresh Spark application with the JAR attached at submission time. Do not add the package's source directory to PYTHONPATH.

```sh
spark-submit --master 'local[2]' \
  --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/validate_new_models.py \
  --manifest /opt/spark-tmbad/artifact.json \
  --row-references python/examples/new_model_references/rows-v3.json \
  --gaussian-references python/examples/new_model_references/gaussian-v3.json \
  --output /out/fresh-python-new-model-check.json
```

This program checks two parameter/data points for each of the nine models through public fixed evaluation and the separate `PreparedParameters` API. It uses typed Spark SQL fixture rows, real JVM/native execution, bounded collected prediction rows and explicit row identities. It verifies named-coordinate resolution, weights, complete-unit grouping, source-bound parameter persistence and prediction provenance. Correlated effects exercise both conditional and new-group prediction/forecast targets. Future inputs contain no responses.

A `PreparedParameters` object represents a declared vector, not a fitted or converged model. A sensitivity-reference hash does not certify a posterior draw. These checks do not run an optimizer or assess parameter recovery, repeated-sample coverage, independent fits or posterior calibration. Those require the separate study programs and their own observed receipts. The [retained local Spark receipt](../examples/new_model_references/spark-local-new-models-v1.json) records a passed actual run of all 18 parameter/data points across the nine models on Linux ARM64, Spark 4.0.1 `local[2]`, with the installed 0.2.0 wheel. It covers fixed values/scores, response-free prediction/forecasting and the declared-parameter contracts above. Its exact identities are:

| Input | SHA256 or build identity |
| --- | --- |
| Validator source | `6dcc03889fc07d68bb37d201b47935a06bfa6238ba4e8d097aa0ed84fec9141a` |
| Manifest | `b6d73e248009a0f0dd23b804f70c6544cb938cc7623ab83bddc2929a0025a69f` |
| Native build | `5d3cfec94ba65f7c39711f109b09dc3ec6883bcb062e68cecb50345434a35383` |
| Native binary | `3351a1619ec13d7eb19f2d80333146b3cbd156f4ae9e940a338b99fed4cac357` |
| JVM adapter | `4bc78a3be973d8e3e62eea12df2bf1e2410299b7bf39144b2f75257958814b8c` |
| Observed receipt bytes | `2393a51d8934d513fc958c98460ad0a346ab0565def21ca3fb8e273a66d238ef` |

This is local Spark adapter/native execution at declared parameter points. It does not qualify distributed workers, managed cloud runtimes, model fitting, Hessians or Monte Carlo calibration.

## Retained references and pure checks

The `rows-v3.json`, `gaussian-v3.json` and `supplement-v3.json` files under `examples/new_model_references/` are mathematical reference outputs. Their historical `native_executed:false` and `spark_executed:false` flags describe reference generation, not a later executable comparison. The separate native and Spark receipts describe their own observed runs. Never rewrite those flags to describe another stage. Each runtime report binds the reference bytes separately.

Run the Python contracts from a prepared development environment:

```sh
PYTHONPATH=python/src python -m unittest discover -s python/tests -v
```

The source-tree path is appropriate for pure development tests. Actual installed-wheel checks use the separate command above. No pure test starts Spark or executes native mathematics.
