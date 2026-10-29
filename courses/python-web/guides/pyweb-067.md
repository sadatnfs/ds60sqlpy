# pyweb-067: Logs, metrics and tracing without sensitive payloads

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-066`.

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

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite cross-framework engineering investigation with explicit scope."""

import json
import logging
from io import StringIO


def run_cases():
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from prometheus_client import CollectorRegistry, Counter, generate_latest

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("finite-web")
    registry = CollectorRegistry()
    counter = Counter(
        "lesson_http_requests", "Bounded route outcomes", ["route", "status"], registry=registry
    )
    output = StringIO()
    logger = logging.getLogger("finite-web-observation")
    handler = logging.StreamHandler(output)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    app = FastAPI(docs_url=None, redoc_url=None)

    @app.middleware("http")
    async def observe(request: Request, call_next):
        with tracer.start_as_current_span("http.request") as span:
            response = await call_next(request)
            route = request.scope.get("route")
            pattern = getattr(route, "path", "unmatched")
            span.set_attribute("http.route", pattern)
            span.set_attribute("http.response.status_code", response.status_code)
            counter.labels(pattern, str(response.status_code)).inc()
            logger.info("route=%s status=%s", pattern, response.status_code)
            return response

    @app.get("/notes/{identifier}")
    def note(identifier: int):
        return {"identifier": identifier}

    try:
        with TestClient(app) as client:
            assert (
                client.get(
                    "/notes/7?token=synthetic-secret", headers={"Authorization": "Bearer hidden"}
                ).status_code
                == 200
            )
            assert client.get("/missing").status_code == 404
        spans = exporter.get_finished_spans()
        assert len(spans) == 2 and spans[0].attributes["http.route"] == "/notes/{identifier}"
        metrics = generate_latest(registry).decode()
        assert 'route="/notes/{identifier}"' in metrics
        combined = metrics + output.getvalue() + str([dict(span.attributes) for span in spans])
        assert (
            "synthetic-secret" not in combined
            and "hidden" not in combined
            and "/notes/7" not in combined
        )
        return {
            "spans": len(spans),
            "bounded_route_labels": True,
            "sensitive_headers_and_query_not_recorded": True,
            "exporter": "in-memory, no external telemetry",
        }
    finally:
        logger.removeHandler(handler)
        handler.close()
        provider.shutdown()


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
