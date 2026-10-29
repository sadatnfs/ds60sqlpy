# pyweb-009: WSGI, ASGI and the server boundary

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-008`.

## Starting point and result

Python web frameworks sit behind application interfaces. WSGI describes a synchronous HTTP application boundary. ASGI supports asynchronous event-oriented application interactions, including HTTP and WebSockets. This chapter observes each interface through its real framework client and explains what an `async def` handler actually changes.

## Mechanism: an interface is a contract between components

A WSGI server supplies an environment dictionary and a response-start callback, then consumes the application's response iterable. Flask exposes that interface. Values such as request method and path are represented in the environment, including the WSGI version tuple.

ASGI supplies a connection scope and asynchronous receive/send callables. The scope identifies the interaction type and connection metadata. An ASGI application can await events and send response messages. FastAPI builds on Starlette's ASGI machinery. A deployment server such as Uvicorn translates actual network activity into those messages.

The asynchronous syntax permits cooperative scheduling when code awaits operations that yield control. It does not turn blocking database calls, CPU-heavy loops or arbitrary synchronous libraries into nonblocking operations. Likewise, a synchronous framework may be deployed with several processes or threads. Concurrency is a property of the full execution design, not a ranking implied by one keyword.

## Worked case: observe the WSGI environment

The Flask endpoint reads `request.environ["wsgi.version"]` and returns it with a label. Through the real WSGI test client, the result identifies WSGI version one, zero. The handler is a normal Python function.

This observation helps locate responsibility. A route sees the application-level environment, while the deployed server owns connection handling and invocation. If a reverse proxy forwards incorrect scheme or host information, the application may construct incorrect URLs even when its handler logic is otherwise sound. Proxy trust receives a separate treatment later in the course.

## Worked case: observe an ASGI HTTP scope

The FastAPI endpoint is asynchronous. It awaits a zero-delay scheduling point and returns the scope type from a real Request object. The TestClient drives the ASGI application and obtains `http` as the scope type. The complete program checks both interface outputs and then exits.

The zero-delay await is a mechanism demonstration. It is not a performance benchmark or evidence that this application serves more users than the Flask example. There is no actual TCP connection, TLS handshake or process pool in either case. A fair deployment comparison would require comparable workloads, resource limits and measured server behavior.

## Failure diagnosis

An application can pass TestClient checks yet fail behind a server because of an incorrect application import, wrong interface adapter or missing startup resources. An async route that blocks its event loop may show long delays for unrelated requests. A sync operation moved to a thread still needs explicit limits and cancellation expectations; threads do not make every resource unlimited.

Lifespan is another boundary. An ASGI application may initialize connections or other resources during startup. A test that never enters the relevant lifespan can accidentally exercise a different environment. Later FastAPI chapters use actual startup/shutdown contexts and verify resource ownership.

## Interview discussion

**Does ASGI mean every operation is asynchronous?** No. The interface supports asynchronous coordination. Individual libraries and code paths still determine whether work blocks and how it should be scheduled.

**Can a TestClient prove server throughput?** No. It is valuable for application contracts. Network servers, worker processes, queueing and external services require additional measurements and acceptance tests.

## Next step

Generate navigation targets from registered route identities. Then test redirects as protocol transitions rather than treating them as arbitrary URL strings.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    import asyncio

    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient
    from flask import Flask, request

    wsgi = Flask(__name__)

    @wsgi.get("/interface")
    def sync_view():
        return {"interface": "WSGI", "version": list(request.environ["wsgi.version"])}

    asgi = FastAPI()

    @asgi.get("/interface")
    async def async_view(request: Request):
        await asyncio.sleep(0)
        return {"interface": "ASGI", "scope": request.scope["type"]}

    with wsgi.test_client() as client:
        wsgi_result = client.get("/interface").json
    with TestClient(asgi) as client:
        asgi_result = client.get("/interface").json()
    assert wsgi_result == {"interface": "WSGI", "version": [1, 0]}
    assert asgi_result == {"interface": "ASGI", "scope": "http"}
    return {
        "synchronous_application": wsgi_result,
        "asynchronous_application": asgi_result,
        "network_or_throughput_benchmark": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
