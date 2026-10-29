# Prepared-model JSON CLI, schema version 1

Run `python -m spark_tmb.cli` in the prepared environment. Each process accepts one UTF-8 JSON document from stdin, bounded to 1,000,000 bytes. Duplicate JSON keys, nonfinite JSON constants, unknown operations and extra fields are rejected. A successful call writes one JSON document and exits zero. Failure writes a bounded JSON error to stderr, writes no success result, and exits two. There is no source compilation, package installation or network request in this interface.

Evaluation request:

```json
{"schema_version":1,"operation":"evaluate","model_id":"normal_mean","data":{"y":[1,2,4,7]},"parameters":[2.2,0.3]}
```

Replace `evaluate` with `fit` for an independent bounded local fit starting at `parameters`. This is not a shared distributed optimizer. Success has exactly the envelope `schema_version`, `operation`, `model_id`, `result`. The result is the prepared runtime's validated detached object, including objective, gradient, parameter names, observation count, ABI, input parameter digest and source/library hashes. Fit additionally returns fitted parameters and convergence diagnostics.

Read-only description request:

```json
{"schema_version":1,"operation":"describe","model_id":"normal_mean"}
```

Its result has `spec`, `max_rows`, `max_parameters`, `max_groups` and `prepared`. `spec` is the validated installed model declaration. `prepared` contains `source_sha256`, `library_sha256`, `registry_sha256` and `abi`. Description verifies installed artifacts without starting R. Scala/JVM callers must use this same registry description rather than invent a second model schema. A first independent-row adapter can explicitly refuse `complete_groups` or non-null `random` until its complete-unit handling is implemented and tested.

No request may supply a project path, library path, compiler flags, R expressions, C++ source or timeout override. Trusted launcher configuration selects the installed source and artifact directories. Integer vectors must remain within R's non-NA signed32 range, from -2147483647 through 2147483647 inclusive. This check occurs before Python float conversion and again before and after R integer coercion. Booleans are not numeric observations.

Registered prediction request:

```json
{"schema_version":1,"operation":"predict","model_id":"linear_regression","data":{"x_prediction":[-1,0,2]},"parameters":[1,2,-0.5],"n_rows":3,"target":"conditional_mean"}
```

Prediction requires exactly these extra fields: data, parameters, n_rows and target. The registered response-free inputs and report semantics are authoritative. Results contain prediction (one finite scalar per row), target, nobs, parameter_names, input parameter digest and the same source/library/registry/ABI identities. Undeclared predictions and response inputs are rejected. Evaluating a likelihood does not implicitly define a transform method.

Registry v2 supports explicit scalar and fixed-size vector parameter blocks while retaining the same CLI envelope version. describe returns normalized parameter_layout and native_parameter_names along with canonical fixed_parameters. Prediction and all evaluation results include artifact_registry_sha256 so callers can bind data/parameter/random-effect semantics as well as native library bytes.
