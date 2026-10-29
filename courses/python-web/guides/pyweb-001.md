# pyweb-001: From Python functions to HTTP responses

Tutorial mode. Stage: beginner. Direct prerequisites: `python-05`, `python-09`.

## Starting point and result

You already know Python functions, dictionaries and modules. A web application uses those tools to process a request and construct a response. This chapter follows one successful request and one unmatched request through a real Flask application. The complete program uses a test client and exits, so it works in the classroom's bounded Python web pad.

A request describes an action: a method such as GET, a target such as `/greet/Ada`, headers and sometimes a body. A response carries a status code, headers and an optional body. A browser is one kind of HTTP client; another program can be a client too. The protocol between the client and server is separate from the Python function that implements an application decision.

## Mechanism: routing connects protocol data to Python

`Flask(__name__)` creates an application object. The decorator `@app.get("/greet/<name>")` registers a route: GET requests matching that path pattern are sent to the decorated function. The `<name>` segment becomes a function argument. The function returns a dictionary and a status code. Flask serializes the dictionary as JSON and supplies an appropriate media-type header.

This registration happens when the program defines the function. The function body runs later, when a matching request arrives. Calling `greet("Ada")` directly would exercise ordinary Python logic, but it would skip routing, request context and response conversion. The test client goes through those application mechanisms, which is why it can expose errors that a direct function call misses.

The application object is also a WSGI callable. A deployed WSGI server translates network requests into that interface. The test client supplies the interface in process. No TCP listener, TLS certificate, DNS lookup or browser is involved in this first investigation.

## Worked case: a matching request produces a representation

The client requests `/greet/Ada`. The router extracts the name, the handler observes `request.method`, and the result is status 200 with the JSON representation `{"message": "Hello, Ada", "method": "GET"}`. The program checks the decoded body and that the Content-Type starts with `application/json`.

These assertions cover several different contracts. A status of 200 alone would not prove the body has the intended shape. A correct dictionary from a direct function call would not prove the route exists. A JSON-looking string with an HTML media type could confuse downstream clients. Checking the parts together gives a useful first application test.

## Worked case: an unmatched request stops before the handler

The client also requests `/unknown`. There is no matching route, so Flask returns 404. The greeting function is not responsible for every possible target. This distinction helps debugging: a missing route is different from a handler that found its route but could not find a database object.

A production service may choose a consistent JSON error representation for both cases. Here the assertion deliberately checks the routing result only. It does not claim that Flask's default HTML error page is your future API's final public error contract.

## Failure diagnosis

If every request returns 404, check the registered path, leading/trailing slash and method before examining business logic. If a handler raises an exception, a testing configuration may propagate that exception into the test instead of returning a generic 500 response. Later chapters make that behavior explicit. If an application runs through this client but is unreachable in a browser, investigate server startup, listening address, port publication and proxy configuration separately.

## Interview discussion

**What is the difference between an application and a server?** The application defines request behavior. A server accepts connections and invokes the application through an interface such as WSGI or ASGI.

**What does this successful test establish?** Routing, request-context access and response construction worked for these two inputs in the pinned environment. It does not establish deployment availability or browser behavior.

## Next step

Inspect how a target URL becomes path arguments and query values. Treat those two sources of input as separate parts of the request contract.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request

    app = Flask(__name__)

    @app.get("/greet/<name>")
    def greet(name):
        return {"message": "Hello, " + name, "method": request.method}, 200

    with app.test_client() as client:
        valid = client.get("/greet/Ada")
        missing = client.get("/unknown")
        assert valid.status_code == 200
        assert valid.json == {"message": "Hello, Ada", "method": "GET"}
        assert valid.headers["Content-Type"].startswith("application/json")
        assert missing.status_code == 404
    return {
        "valid": {"status": valid.status_code, "body": valid.json},
        "unmatched_route": missing.status_code,
        "surface": "real Flask WSGI test client; no TCP server",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
    print("pyweb-001: all reference checks passed")
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
