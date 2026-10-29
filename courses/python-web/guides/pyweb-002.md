# pyweb-002: URLs, path parameters and query strings

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-001`.

## Starting point and result

A URL can identify a resource and carry options for viewing it. The path and query string have different roles and different parsing rules. This chapter observes a percent-encoded name, repeated query parameters and an integer path converter through a real Flask client. The goal is to recognize what the application actually receives before adding validation or database queries.

## Mechanism: encoding is part of transport

The path `/people/Ada%20Lovelace` represents a name containing a space. Percent encoding expresses bytes that cannot appear literally in that location. The framework decodes the path into the route argument `name`. The raw query string remains available as bytes through `request.query_string`, while `request.args` provides a parsed multidict.

A multidict can retain several values under the same key. For `tag=one&tag=two`, asking for one value and asking for the full list are different operations. The example uses `getlist("tag")` because the contract permits multiple tags. For a parameter that must occur once, explicitly reject duplicates or define a single-value policy instead of relying on an accidental first/last-value choice.

Path converters also affect matching. `<int:item_id>` attempts to match a supported integer segment and passes a Python integer to the handler. Conversion here belongs to routing. Later frameworks may report some parameter problems as validation errors after matching a more general route. A status code should be interpreted in the context of the actual routing/validation design.

## Worked case: a decoded path and repeated query

The request combines a space-containing name with two tags. The response records the decoded name, the complete tag list, the decoded path and the original ASCII query string. Assertions require `Ada Lovelace` and `["one", "two"]`, demonstrating that neither encoding nor repetition should be guessed from a printed URL alone.

The name is application input, even after successful decoding. Decoding does not make a value safe for HTML, SQL, a filename or an authorization decision. Each later use needs its own contract. Similarly, a query parameter called `owner` does not become a trusted user identity merely because the framework parsed it successfully.

## Worked case: an integer route versus an unmatched segment

`/items/7` matches the integer converter and produces an integer value seven. `/items/seven` does not match and returns 404. The example verifies the value and its Python type in the successful case, then the routing failure in the second case.

Do not infer that every integer accepted by a converter is a valid database identifier. The application still needs to decide whether zero, negative numbers, extremely large numbers or absent records make sense. The precise converter's domain is also framework-specific, so test boundaries rather than assuming it behaves like unrestricted `int(text)`.

## Failure diagnosis

Losing repeated filters often comes from treating a multidict as an ordinary dictionary too early. Unexpected path behavior can come from encoding, slash normalization or a reverse proxy rewriting the target. Compare the original target, the route pattern and the parsed values. Avoid decoding a value repeatedly: multiple decoding layers can disagree about the intended path.

A URL fragment, the part after `#`, is generally processed by the client and is not sent as the HTTP request target. A server route cannot depend on reading a browser fragment from an ordinary request. Browser-side routing is covered in the existing web-development route.

## Interview discussion

**When should information be in a path or a query?** A path commonly identifies the resource; a query commonly selects filtering, ordering or representation options. Consistency and a documented contract matter more than memorizing one naming convention.

**Does percent decoding validate input?** It produces a representation of transmitted input. It does not establish type, ownership, safety in another language or business validity.

## Next step

Attach methods and status codes to resource operations. Repeating a request can preserve its intended effect even when the second response has a different status.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request

    app = Flask(__name__)

    @app.get("/people/<name>")
    def person(name):
        return {
            "name": name,
            "tags": request.args.getlist("tag"),
            "query": request.query_string.decode("ascii"),
            "path": request.path,
        }

    @app.get("/items/<int:item_id>")
    def item(item_id):
        return {"id": item_id, "python_type": type(item_id).__name__}

    with app.test_client() as client:
        encoded = client.get("/people/Ada%20Lovelace?tag=one&tag=two")
        numeric = client.get("/items/7")
        invalid = client.get("/items/seven")
        assert encoded.json["name"] == "Ada Lovelace"
        assert encoded.json["tags"] == ["one", "two"]
        assert numeric.json == {"id": 7, "python_type": "int"}
        assert invalid.status_code == 404
    return {
        "decoded_path_and_repeated_query": encoded.json,
        "converted_path": numeric.json,
        "unmatched_converter": invalid.status_code,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
