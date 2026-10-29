# pyweb-024: Flask outbound clients, timeouts and error translation

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-023`, `python-svc-01`.

## Starting point and result

Many web handlers call another service. That introduces latency, failures and a second response contract. This chapter uses a real HTTPX2 client with MockTransport to exercise the application's translation of success, a read timeout and an upstream error. No remote service is contacted.

## Mechanism: a bounded client is an owned resource

The HTTP client has an explicit base URL, timeout and transport. The endpoint accepts only three fixture case names, so it cannot become an arbitrary URL-fetching proxy. It performs the configured request, checks the upstream status and returns a controlled local response.

MockTransport runs a supplied Python handler instead of network I/O. That handler returns real HTTPX2 Response objects or raises the library's timeout exception. This gives a precise test of client/error-handling behavior. It does not establish DNS, TLS, connection pooling under load or an actual elapsed network timeout.

The client is closed in `finally`. A deployed application usually shares an appropriately configured client within its supported lifecycle rather than constructing a new connection pool for every request. Its concurrency limits, timeout dimensions and shutdown behavior should be deliberate.

## Worked case: successful upstream data

The valid fixture response contains value seven. The local endpoint verifies success and returns that value. The test checks the decoded representation, not merely the existence of a Response object.

A real application also needs to validate the upstream body schema. A 200 status can accompany incomplete or unexpected data. Treat the upstream response as input to your own application contract, especially when downstream code assumes specific types or fields. This small fixture keeps the successful body deliberately simple.

## Worked case: timeout and upstream failure receive different local responses

The slow fixture raises a ReadTimeout immediately. The endpoint translates it to 504. The unavailable fixture returns 503, and `raise_for_status` produces an HTTPStatusError that becomes a controlled 502 response. Neither response exposes raw internal exception details.

The timeout is simulated as an exception, so the test proves translation rather than actual timer enforcement. This distinction is useful when diagnosing failures: a deterministic test can validate the application's policy, while a real service test validates the network/runtime path that triggers it.

Retries must follow the upstream operation's semantics. A failed read can be different from a timed-out creation that may already have committed. The existing reliable-HTTP Python lesson and the later idempotency chapter provide the deeper retry contract; this endpoint does not silently retry every operation.

## Failure diagnosis

A handler that hangs may have an unbounded timeout, blocking work on an event loop or an exhausted connection pool. A response that misleads clients may collapse several failure types into a generic success. Log useful bounded context, such as dependency identity and error category, without dumping credentials or sensitive request bodies.

If a MockTransport test passes while deployment fails, inspect the untested layers rather than assuming the test was meaningless. DNS, TLS, network access, real server behavior and proxy settings need their own evidence.

## Interview discussion

**Does setting a client timeout prove an end-to-end service deadline?** No. Timeout components, retries, queueing and other work can contribute to total duration. An overall deadline needs explicit budgeting.

**Why avoid accepting an arbitrary target URL here?** The product needs a known upstream service. Restricting that choice avoids introducing an unnecessary server-side request-routing boundary and makes testing and authorization clearer.

## Next step

Examine async behavior under Flask's WSGI execution model. Awaited operations and durable background jobs have different lifetimes.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    import httpx2
    from flask import Flask

    def transport(request):
        if request.url.path == "/valid":
            return httpx2.Response(200, json={"value": 7})
        if request.url.path == "/slow":
            raise httpx2.ReadTimeout("fixture timeout", request=request)
        return httpx2.Response(503, json={"error": "fixture unavailable"})

    upstream = httpx2.Client(
        transport=httpx2.MockTransport(transport), base_url="https://upstream.example", timeout=1
    )
    app = Flask(__name__)

    @app.get("/proxy/<case>")
    def proxy(case):
        if case not in {"valid", "slow", "down"}:
            return {"error": "unsupported case"}, 404
        try:
            response = upstream.get("/" + case)
            response.raise_for_status()
        except httpx2.TimeoutException:
            return {"error": "upstream timeout"}, 504
        except httpx2.HTTPStatusError:
            return {"error": "upstream unavailable"}, 502
        return {"value": response.json()["value"]}

    try:
        client = app.test_client()
        assert client.get("/proxy/valid").json == {"value": 7}
        assert client.get("/proxy/slow").status_code == 504
        assert client.get("/proxy/down").status_code == 502
        return {
            "success": 200,
            "upstream_timeout": 504,
            "upstream_failure": 502,
            "transport": "actual HTTPX2 MockTransport; no remote requests",
        }
    finally:
        upstream.close()


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
