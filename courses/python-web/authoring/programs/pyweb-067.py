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
