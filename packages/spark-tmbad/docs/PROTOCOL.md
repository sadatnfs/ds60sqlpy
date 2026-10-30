# Native Spark/TMBad protocol and facade, draft v1

This is the agreed implementation boundary for package 0.1.0. Changes require
coordination with all three owners. It is not evidence of completed execution.

## Prepared artifact

A public manifest has exactly these required top-level fields:

```json
{
  "schema_version": 1,
  "kind": "spark-tmbad-artifact",
  "package_version": "0.1.0",
  "protocol": 1,
  "build_id": "64 lowercase hexadecimal SHA256 characters",
  "platform": { "os": "linux", "arch": "arm64" },
  "binary": { "path": "/absolute/path/tmbad-worker", "sha256": "64hex" },
  "engine": { "name": "TMBad", "version": "1.9.25", "source_sha256": "64hex" },
  "models": []
}
```

Optional `jvm` is an object with `path`, `sha256`, `spark_version` (4.0.1),
`scala_binary_version` (2.13) and `java_min` (17). Optional `provenance` holds
preparation metadata and dependency notices. Arch is amd64 or arm64. A driver
may be on another OS, but every executing native task must match this platform.
Relocatable file paths are not scientific identity. Bind build_id, binary digest,
engine, platform and selected model descriptor; include the JVM digest when
provided. Verify files before execution and fail on a different prepared artifact.
Build preparation records compiler/flags and source/dependency identities.

The native owner supplies the authoritative model descriptor in `--describe`:

```json
{
  "id": "normal",
  "version": "1",
  "digest": "64hex",
  "fit_kind": "rows",
  "fit_fields": ["y"],
  "parameter_names": ["mu", "log_sigma"],
  "parameter_bounds": [
    [null, null],
    [-20, 20]
  ],
  "marginalization": "none",
  "random_dimension": 0,
  "ordered": false,
  "max_unit_rows": 256,
  "derivative_orders": [1, 2],
  "predict": {
    "response": {
      "fields": [],
      "columns": ["mean", "sd"],
      "needs_history": false,
      "conditioning": "fitted parameters",
      "uncertainty": "observation only"
    }
  },
  "forecast": {}
}
```

`fit_kind` is rows or unit. Marginalization is none, exact or laplace. A prediction
or forecast target must declare its input fields, output columns, history need,
conditioning and uncertainty. Prediction of an existing group and a new group
are distinct named targets. A model without a forecast hook rejects forecasting.
No automatic conditional interpretation is inferred from a likelihood.

## Wire framing and process lifecycle

The fixed binary commands are `tmbad-worker --describe` (one JSON description,
then exit) and `tmbad-worker --stdio`. Stdio reads a four-byte unsigned big-endian
length followed by exactly that many UTF-8 JSON bytes, then emits the same frame
format. Maximum frame is 4 MiB. EOF between frames finishes successfully; a
partial frame, malformed UTF-8/JSON, duplicate keys, unsupported schema or invalid
numeric contract produces an error and nonzero exit. Maximum depth is32, object
fields1024, array elements8192, field names256Unicode scalar values and strings
1,000,000Unicode scalar values, always within the4MiB UTF-8 byte cap. Integral
JSON tokens must lie within the safe-integer interval from-9007199254740991 to
9007199254740991. Floating tokens must be finite doubles.
Only fixed argv is allowed. Never construct a shell command from model data.

One child processes requests serially. It cannot spawn descendants or compile
models. A failed AD construction/evaluation makes the process unusable: emit a
bounded error if possible and exit nonzero. Parent tasks must drain bounded
stderr, enforce deadlines, terminate/reap on all exits and reject all provisional
summaries unless protocol completion AND exit zero are observed. No tape/native
pointer travels in a Spark closure. No cross-action native cache initially.

Every request has `protocol:1`, `request_id` (1..128 ASCII characters), and `op`.
A describe request has no model data. Every other request includes `model_id`,
`model_digest`, `theta` and `rows`. The native worker verifies descriptor identity,
parameter dimension/domain, strict finite numbers and exact supported integers.
The response includes `protocol`, `request_id`, `status` (ok/error),
`request_sha256` computed from the exact received payload bytes, and, for a model
operation, matching `model_id`, `model_digest` and `build_id`. Errors include
bounded `error.code` and `error.message`, never raw observations or credentials.

Supported initial operations:

- `describe`: returns `build_id`, `engine`, `models`.
- `evaluate`: adds `kind` (rows/unit), optional `hessian` boolean and the declared
  weight field. Rows is a numeric matrix in descriptor fit_fields order. Row mode
  requires `weights` with one nonnegative finite value per row. Unit mode requires
  scalar `unit_weight`, applied once to the entire joint/marginal loss; row weights
  are not silently substituted. Response: `loss`, `gradient`, `row_count`,
  `unit_count`, `weight_sum`, optional flattened row-major `hessian`, and bounded
  `diagnostics`. Empty row batches yield shaped zeros; an empty unit is rejected.
- `predict`: adds `target`, with rows in that target's field order. If the target
  requires history, include `history` in fit_fields order. Prediction has no
  future response column. Response: `columns`, `values` (one numeric row per input
  row), `row_count`, `conditioning`, `uncertainty`. Featureless requests carry
  one empty array per requested output row to preserve cardinality.
- `forecast`: adds `target` and complete `history`; rows are the future inputs in
  the target's declared field order. Response has the same cardinality/column
  contract as prediction. Validate model-specific time cadence and future order.
  One or multiple future steps must be supported by a declared hook, not invented
  by the transport. Known-parameter uncertainty excludes parameter-estimation
  uncertainty unless an explicitly implemented target says otherwise.

Row batches are at most 8192 rows, parameters at most64, fit/prediction fields at
most256, and complete units/forecast horizons at most256 rows initially. Dense
Laplace uses d+q<=16 and q<=8. A model may impose stricter limits. Laplace outer
Hessians are not promised; derivative_orders is authoritative. Exact Gaussian
marginalization must not be reported as a general Laplace implementation.

## Spark fit specification

A spec has `model_id`, `columns` mapping every native fit_fields name to an actual
Spark column, `id_columns`, `group_columns`, `order_columns` (all lists), and
`weight_column` (null or one column name). Do not infer field roles from names.
A complete-unit model requires grouping; ordered models require unique declared
order keys. Refuse null keys, missing fields, unsupported types, nonfinite values,
lossy integer-to-float conversion and oversized units before unsafe native work.

For row-shared fitting, stream bounded batches per partition. For unit-shared
fitting, shuffle complete groups together and evaluate each group as one unit.
For independent fits, produce a DataFrame of group keys and fitted model JSON;
never collect every group model on the driver. Preserve input identifiers during
prediction and future-row identifiers during forecasting. No global row order is
promised. Unknown output-column collisions are refused, not overwritten.

Shared fitting collects only bounded partition summaries (maximum4096) at each
common theta. Validate logical partition coverage, request/model/artifact identities,
counts and an order-independent data ledger across evaluations. Add a global L2
penalty once after the global sum or weighted mean, not once per partition. A
mean divides by global row-weight mass or unit-weight mass according to kind.
Only derived estimator-owned caches may be removed. Immutable input snapshots
remain a user-visible prerequisite; caching alone is not a storage transaction.

Options are explicit JSON data, never commands or loader paths. Initial fit
options: `initial_parameters` (required), `max_iterations` (default100),
`gradient_tolerance` (1e-6), `function_tolerance` (1e-12), `max_line_search` (25),
`reduction` (sum/weighted_mean), `l2_strength` (0), `batch_rows` (1024),
`task_timeout_seconds` (120), `max_partitions` (4096). Use model parameter_bounds;
report raw and projected gradients and active bounds. A small objective change
without an adequate score is stalling, not convergence. No global-optimum claim.

## Fitted model and Scala/Python facade

Fitted-model JSON: `schema_version:1`, `kind:"spark-tmbad-model"`,
`package_version:"0.1.0"`, `model_id`, `model_digest`, `artifact_identity` (the
path-independent artifact binding), `parameters`, `parameter_names`, `spec`, and
`fit` (converged/status/reason/iterations/objective_calls/loss/raw_gradient_inf/
projected_gradient_inf/active_bounds/row_count/unit_count/weight_sum/trace).
Optional fit fields are `reduction`, `l2_strength`, `data_ledger` and
`rejected_candidates`. The last is an integer from zero through `objective_calls`
and counts only explicitly rejected numerical trial evaluations. Initial
objective rejection is fatal. A rejected trial contributes no loss or gradient;
all partial partition sums are discarded after complete logical partition and
data-ledger coverage is verified. Independent objective evaluations use fresh
native sessions and require a successful exit before accepting their result.

Only `DOMAIN_ERROR`, `INNER_MODE_FAILURE`, `BAD_CURVATURE` and
`NONFINITE_EVALUATION` may classify a proposed trial as numerically inadmissible.
The response must match request, model and build identity, followed by EOF and
native exit code 2. Schema, identity, transport, resource and AD-invariant errors
remain fatal, as do unexpected exit codes or trailing output. This contract does
not weaken the native inner score or curvature requirements.

artifact_identity is an object with build_id, binary_sha256, platform, engine
(the three engine fields from the artifact), and jvm_sha256 (string or null).
Compare this object structurally, not by cross-language JSON floating formatting.
The top-level model_digest separately binds the selected model. Public Spark
execution requires the prepared JVM identity; native-only artifacts may omit it.
JSON is bounded, finite and duplicate-key strict. No pickle, arbitrary class
imports or native pointers. Loading requires a matching prepared runtime. Saving
is explicit to an owned local file; filesystem/remote storage support is labeled.

Java-friendly facade is `io.ds60.spark.tmbad.PythonBridge`:

- describe(artifactJson,modelId): String
- fitShared(df,specJson,artifactJson,optionsJson): String
- fitGroups(df,specJson,artifactJson,optionsJson): DataFrame
- predict(df,modelJson,artifactJson,optionsJson): DataFrame
- predictConditional(historyDf,targetsDf,modelJson,artifactJson,optionsJson): DataFrame
- forecast(historyDf,futureDf,modelJson,artifactJson,optionsJson): DataFrame
- predictGroups(df,modelsDf,artifactJson,optionsJson): DataFrame
- predictConditionalGroups(historyDf,targetsDf,modelsDf,artifactJson,optionsJson): DataFrame
- forecastGroups(historyDf,futureDf,modelsDf,artifactJson,optionsJson): DataFrame

The JVM owner may add a typed Scala API underneath this facade. Prediction options
have `target`, `columns` and `output_prefix` (default tmbad_). Forecast options have
`target`, `history_columns`, `future_columns`, optional explicit future group/order
column mapping, and output_prefix. Grouped existing-group prediction uses predictConditional and its group form,
with native op predict and history plus rows. Ordinary predict rejects
needs_history targets. Fitted JSON retains no training rows or unbounded group
posterior map. Do not invent history-free conditional predictions. Independent fitted
models use group-key columns plus `tmbad_model_json` and visible fit diagnostics.
Python passes `_jdf` and validated JSON through Py4J; it does not create Python
UDFs or numerical workers. Python and Scala expose matching behavior and bounds.

## Initial actual model/acceptance targets

Native owner: normal, linear Gaussian, Poisson/exposure; exact Gaussian random
intercept; generic bounded joint-model Laplace (including a non-Gaussian count
example); ordered AR1 forecasting. Include random-effect existing/new-group
prediction and forecasting hooks with explicit uncertainty scope. A combined
Gaussian AR1/random-intercept model is desirable if it can be independently
qualified; do not label unsupported models passed.

Acceptance must use actual compiled native code and actual Spark partition tasks,
including unequal/empty partitions, derivative oracles, marginalization contrasts,
shared versus independent fitting, label-free prediction, multi-step forecasts,
JSON round trips, stale/wrong binary refusal, malformed/oversized frames, nonzero
exit after valid output, timeout/cancellation and cache/identity preservation.
A local[2] execution is not multi-node or performance-scale evidence. Retain source,
binary/compiler, numerical and runtime records separately. No publication or
shared classroom admission occurs before root's coordinated release decision.

## JVM/Python options

`describe(artifactJson, modelId)` returns `{artifact_identity, model}` from the
validated prepared metadata. It does not start Spark work or prove runtime
readiness. `probe(sparkSession, artifactJson, modelId)` is the separate explicit
bounded executor/native handshake. Every fit/predict/forecast task still checks
its own binary and native description before numerical requests.

Prediction options may add `id_columns` (default fitted spec IDs),
`group_columns` (default fitted groups), and `order_columns` (default empty).
Conditional prediction additionally supplies `history_columns` and may override
`history_group_columns` and `history_order_columns`, defaulting to the fitted spec.
Target-side `group_columns` are positional counterparts of the history group keys.
Forecasting may override `future_id_columns`, `future_group_columns`,
`future_order_columns`, `history_group_columns` and `history_order_columns`; their
defaults are the corresponding fitted-spec lists. The future and history column
maps remain explicit native-field-name to Spark-column mappings.

Shared prediction/forecasting does not retain training rows or an unbounded group
posterior map in fitted JSON. Conditional operations require an explicit history
DataFrame. A history-free declared target may use an empty/absent history; it is
never silently reinterpreted as conditioning on training data.

A task may spool bounded prediction output to its own private scratch file so
that no result is emitted before the native child completes with exit zero.
Exceeding that explicit output bound fails the task; partial result success is
not an allowed fallback. Iteration completion and task completion both clean the
owned spool. This is not a claim of global output ordering or transactional input
snapshot isolation.

## Forecast history and numerical qualification

Future rows must be nonempty. Empty history is accepted only for a target with
`needs_history:false`, such as an explicitly unconditional new-group forecast.
Conditional targets fail when a future group lacks history. Future groups must
never disappear through an inner join. Group-key correspondence and output IDs
are explicit; a DataFrame does not promise global row order.

Native compilation, native numerical oracles, JVM adapter checks and actual
Spark fit/predict/forecast runs are separate qualification tiers. Prediction and
forecasting reject unconverged fitted models by default. Any diagnostic override
must be explicit and must preserve the fit's unconverged status.
