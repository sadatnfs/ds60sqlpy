## Starting point and result

Useful observability connects requests to outcomes without recording secrets or creating unbounded metric dimensions. This chapter instruments a real FastAPI request path with an OpenTelemetry in-memory exporter, Prometheus counters and a controlled logger. It checks both useful evidence and the absence of sensitive values.

## Mechanism: each observation surface has a purpose

A trace span describes one operation and its attributes. A metric aggregates repeated observations under a bounded label set. A log records a discrete diagnostic event. Copying the entire request into all three creates cost and privacy problems without necessarily improving diagnosis.

The middleware starts a request span, awaits the application, then records the resolved route pattern and status. The route pattern notes/{identifier} has bounded cardinality; the literal path containing every individual identifier would create many distinct labels. Unmatched requests use one fixed fallback label.

The example never records Authorization or the query string. A token in either place remains outside the metrics, logs and span attributes. Real applications also need policies for exception messages, request bodies and domain identifiers, since sensitive values can enter diagnostics through many routes.

## Worked case: record a successful parameterized route

The client requests a note with a synthetic secret in its query and an Authorization header. The endpoint returns successfully. The finished span contains the route pattern and status, and the metric output uses the same bounded route label.

The test inspects actual exported span objects and actual Prometheus text rather than merely checking that instrumentation functions were called. The logger's output is also retained in a StringIO buffer for inspection. These are real library integrations with local sinks.

No external telemetry collector is contacted. A production exporter introduces batching, retries, shutdown and network failure behavior that need separate qualification. The in-memory result proves attribute selection and instrumentation flow, not remote delivery.

## Worked case: an unmatched request and sensitive-data absence

A second request receives 404 and produces another span/metric observation under the unmatched label. The program combines the observed output and checks that neither synthetic secret nor raw identifier path appears.

Negative assertions are important here. A successful request count does not prove that instrumentation avoided a private header. Conversely, a redaction function can remove one field while another code path still records the same value. Inspect the actual emitted surfaces that the application owns.

Metrics should not use user IDs, request IDs, email addresses or arbitrary error strings as labels. Those values can create high cardinality and expose sensitive information. A request correlation ID belongs in an appropriately controlled trace/log context when needed, not in an unbounded counter label.

## Failure diagnosis and discussion

**Why record the route after call_next?** The framework has resolved the route by then, allowing a stable pattern instead of a raw path. Failure paths still need an explicit fallback.

**Does sampling traces eliminate the need for privacy review?** No. A sampled secret is still a disclosed secret. Minimize attributes before export and review retention/access separately.

If telemetry volume grows unexpectedly, inspect label cardinality and repeated exporters. If shutdown hangs, inspect exporter lifecycle and pending flushes. Continue with the network workshop to observe streaming and disconnect behavior at the actual transport boundary, then apply these diagnostics to those service tests.
