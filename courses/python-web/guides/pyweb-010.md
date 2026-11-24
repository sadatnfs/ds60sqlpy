# pyweb-010: Named routes, redirects and navigation

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-009`.

## Starting point and result

Hard-coded URLs become fragile when route patterns change. Framework URL builders connect a stable endpoint name to its current path. Redirects then ask a client to make another request to a selected target. This chapter generates a resource URL and implements a bounded post-redirect-get flow.

## Key terms

- **Endpoint name:** The identifier Flask registers for a route, normally the view function's name, used to look up the route instead of hard-coding its path.
- **url_for:** Flask's URL builder, which fills path parameters from keyword arguments and places the remaining arguments in the query string.
- **Location header:** The response header that names the URL the client should request next after a redirect.
- **303 See Other:** A redirect status telling the client to retrieve the Location target with GET, commonly sent after a successful form POST.
- **Post/redirect/get:** A pattern in which a state-changing POST answers with a redirect, so a browser refresh repeats a harmless GET instead of the submission.

## Mechanism: route identity and destination policy

Flask normally uses the view function's name as an endpoint identity. `url_for("item", item_id=7, language="en")` fills the path parameter and places the remaining option in the query string. This keeps path construction aligned with the registered route instead of duplicating formatting logic across templates and handlers.

The continuation endpoint accepts a destination name, not an arbitrary URL. Its allowlist maps `dashboard` to the corresponding endpoint. The handler then calls `url_for` and returns a 303 redirect. This design fits a product that offers a known finite set of navigation destinations and avoids interpreting untrusted URL schemes or hosts.

A 303 response tells the client to retrieve the other resource using the appropriate follow-up retrieval semantics. The program keeps redirect following explicit so it can inspect the initial status and Location header before requesting the target. Automatic following is convenient, but it can hide the intermediate response you meant to test.

## Worked case: build a URL from its route

The item route expects an integer ID. Within a test request context, the URL builder produces `/items/7?language=en`. The assertion checks the complete path and query. If the route later changes, callers using its endpoint identity can adapt without manually replacing every string occurrence.

A URL builder does not prove that the resource exists or that the caller can access it. It knows the route's construction rules. Database existence and authorization still happen when a request is handled. This is another reason to separate syntactic routing from domain decisions.

## Worked case: accept one known redirect and reject another input

The client posts destination `dashboard`. The response is 303 with Location `/dashboard`. The client then requests that target and receives the dashboard representation. This is a complete application-level redirect trace.

Posting an external URL as the destination fails with 400 because it is not an allowlisted endpoint name. The program never attempts to validate or fetch that external host. If an application genuinely needs arbitrary return URLs, its contract needs careful scheme, host and normalization checks, including browser interpretation. A narrow named-destination API avoids that additional complexity when it is not a product requirement.

## Worked example: url_for options and redirect statuses

```python
from flask import Flask, redirect, url_for

app = Flask(__name__)


@app.get("/items/<int:item_id>")
def item(item_id):
    return {"id": item_id}


with app.test_request_context(base_url="https://shop.example"):
    print(url_for("item", item_id=7))
    print(url_for("item", item_id=7, _external=True))
    print(url_for("item", item_id=7, _anchor="reviews", sort="new"))
    for code in (302, 303, 307):
        response = redirect(url_for("item", item_id=7), code=code)
        print(code, response.headers["Location"])
```

Expected output:

```text
/items/7
https://shop.example/items/7
/items/7?sort=new#reviews
302 /items/7
303 /items/7
307 /items/7
```

`url_for` builds paths from the endpoint name `item`, not from a hand-typed string, so renaming the URL rule later keeps every generated link correct. An unknown keyword such as `sort` became a query parameter, `_anchor` added a fragment, and `_external=True` used the request's scheme and host to produce an absolute URL. All three redirects share the same `Location`; the difference is what the client does next. After a form POST, 303 tells the browser to follow with GET, which is why the lesson uses it, while 307 would repeat the POST with its body. A misspelled endpoint such as `url_for("items")` raises `BuildError` at link-building time instead of producing a broken link.

## Failure diagnosis

A redirect loop may come from conflicting slash rules, login requirements or proxy scheme information. A test that always follows redirects may show only the last failure and obscure the loop's first response. Inspect each status and Location value deliberately. If URL building fails, check the endpoint name and required parameters rather than concatenating a path as a quick workaround.

Do not treat a parameter named `next` as trusted merely because another endpoint originally generated it. Clients can edit requests. Validate the actual value at the point where it controls navigation, and keep allowed destinations consistent with the deployment's origin policy.

## Interview discussion

**Why use named routes?** They centralize URL construction and preserve the relationship between a handler and its path. They do not replace authorization or resource lookup.

**Why inspect a redirect before following it?** The intermediate status and target are part of the API contract. Automatic client behavior can otherwise conceal an incorrect or unsafe destination.

## Next step

Build repeatable application fixtures and separate client state from server state. This makes later database and authentication tests easier to interpret.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, redirect, request, url_for

    app = Flask(__name__)

    @app.get("/items/<int:item_id>")
    def item(item_id):
        return {"id": item_id}

    @app.get("/dashboard")
    def dashboard():
        return {"page": "dashboard"}

    @app.post("/continue")
    def continue_to():
        allowed = {"dashboard": "dashboard"}
        endpoint = allowed.get(request.form.get("destination"))
        if endpoint is None:
            return {"error": "choose a known destination"}, 400
        return redirect(url_for(endpoint), code=303)

    with app.test_request_context():
        built = url_for("item", item_id=7, language="en")
        assert built == "/items/7?language=en"
    with app.test_client() as client:
        accepted = client.post("/continue", data={"destination": "dashboard"})
        assert accepted.status_code == 303 and accepted.headers["Location"] == "/dashboard"
        assert client.get(accepted.headers["Location"]).json == {"page": "dashboard"}
        denied = client.post("/continue", data={"destination": "https://untrusted.example"})
        assert denied.status_code == 400
    return {
        "generated_url": built,
        "redirect_status": 303,
        "unrecognized_destination": 400,
        "destination_is_an_endpoint_allowlist": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
