# pyweb-022: Flask conditional requests and cache policy

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-021`.

## Starting point and result

Caching can avoid transferring an unchanged representation, but it must respect privacy and consistency. An ETag is a validator associated with a representation. This chapter computes one from fixed JSON bytes, tests a conditional request and contrasts a publicly cacheable resource with a private account response.

## Key terms

- **ETag:** A validator string that identifies one specific version of a representation, here a hash of the fixed JSON bytes.
- **If-None-Match:** A request header carrying an ETag the client already holds, asking the server to send the body only if the representation has changed.
- **304 Not Modified:** A response without a body telling the client that its stored representation is still current.
- **Cache-Control:** The header that states reuse policy, such as `public, max-age=60` for shared caching or `private, no-store` for an account response.
- **Strong validator:** An ETag that changes whenever the representation's bytes change, so a match means the stored bytes are identical.

## Mechanism: a validator describes a representation

The resource's byte string is hashed to produce a strong ETag. The response supplies that validator and a public max-age policy. `make_conditional` examines the incoming request and can return 304 when the client's validator matches.

A strong validator must correspond to the relevant representation bytes under the declared HTTP semantics. Two serializers can produce semantically equivalent JSON with different bytes, so an implementation must decide where the validator is computed and how content encoding or variants affect it. This fixture fixes the bytes explicitly to make the relationship testable.

Cache-Control and ETag serve different roles. A cache policy states when reuse is permitted; a validator helps determine whether a stored representation still matches. An authenticated or personalized response may need private or no-store handling even if its content changes rarely.

## Worked case: reuse an unchanged representation

The first request receives status 200 and an ETag. The next request sends that value in If-None-Match. The server returns 304 with no response body. A third request sends another validator and receives the full 200 response.

The program verifies status, empty conditional body and the exact validator derived from the known bytes. It also inspects the declared max-age/public policy. These are application/protocol observations. The test client is not being claimed as a browser cache that actually stores and reuses the response automatically.

Conditional requests can reduce transfer cost, but they do not necessarily eliminate all server work. If an expensive database calculation is needed before computing the ETag, the representation may still be costly to validate. Version counters, modification metadata or other domain-specific validators can be useful when their semantics are correct.

## Worked case: a private account response has a different policy

The account fixture returns `Cache-Control: private, no-store`. The program checks the exact declaration instead of applying the public resource's policy everywhere. This matters because shared intermediary caches can serve responses to multiple clients under their configured rules.

A cache key must also account for relevant representation differences. Language, content negotiation, authorization scope and query filters can affect the result. A convenient key that omits one of those dimensions can return a valid representation to the wrong request.

## Worked example: Last-Modified as a second validator

```python
from datetime import datetime, timezone

from flask import Flask, Response, request

app = Flask(__name__)
changed_at = datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)


@app.get("/report")
def report():
    response = Response(b"quarterly totals", mimetype="text/plain")
    response.last_modified = changed_at
    response.cache_control.max_age = 0
    response.cache_control.must_revalidate = True
    return response.make_conditional(request)


client = app.test_client()
first = client.get("/report")
print(first.status_code, first.headers["Last-Modified"])
same = client.get("/report", headers={"If-Modified-Since": first.headers["Last-Modified"]})
older = client.get("/report", headers={"If-Modified-Since": "Sat, 28 Feb 2026 00:00:00 GMT"})
print(same.status_code, len(same.data), older.status_code, len(older.data))
print(first.headers["Cache-Control"])
```

Expected output:

```text
200 Sun, 01 Mar 2026 12:00:00 GMT
304 0 200 16
max-age=0, must-revalidate
```

The server sent a timestamp validator instead of the lesson's ETag. A client that echoed the same date in `If-Modified-Since` got 304 with an empty body, while a client whose copy dated from February received the full 16 bytes. The `max-age=0, must-revalidate` policy says the response may be stored but must be checked on every use, so the savings come from small 304 responses rather than from skipping requests, unlike the lesson's `max-age=60` resource. Timestamps have one-second resolution: two edits within the same second would share a Last-Modified value and a client could keep the stale copy, which is why an ETag derived from the exact bytes is the stronger validator when both are available.

## Failure diagnosis

Stale data can come from an overly broad freshness period, a validator that does not change with the representation or an incomplete cache key. Privacy leaks can arise from caching personalized content as public. Unexpected 200 responses to conditional requests can result from quotation/validator mismatches or comparing a different representation variant.

Do not use caching to conceal a correctness problem in the underlying resource. Later chapters address invalidation and shared-worker coordination explicitly. A process-local dictionary cache has different durability and consistency behavior from a browser or reverse-proxy cache.

## Interview discussion

**Is a 304 response an error?** No. It communicates that the client's stored representation can be used under the conditional request contract. The client must already have the relevant representation.

**Does an ETag authorize access?** No. Authorization still applies to the request. A validator is not a credential or proof that the caller may read a protected resource.

## Next step

Use explicit CLI and migration operations to evolve stored state. A new application version must remain compatible with the schema and data it encounters.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python isolated
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    import hashlib

    from flask import Flask, Response, request

    representation = b'{"id":1,"title":"HTTP"}'
    etag = hashlib.sha256(representation).hexdigest()
    app = Flask(__name__)

    @app.get("/resource")
    def resource():
        response = Response(representation, mimetype="application/json")
        response.set_etag(etag)
        response.cache_control.public = True
        response.cache_control.max_age = 60
        return response.make_conditional(request)

    @app.get("/account")
    def account():
        response = Response(b'{"fixture":"private account"}', mimetype="application/json")
        response.headers["Cache-Control"] = "private, no-store"
        return response

    client = app.test_client()
    fresh = client.get("/resource")
    cached = client.get("/resource", headers={"If-None-Match": fresh.headers["ETag"]})
    changed = client.get("/resource", headers={"If-None-Match": '"another-representation"'})
    private = client.get("/account")
    assert (
        fresh.status_code == changed.status_code == 200
        and cached.status_code == 304
        and cached.data == b""
    )
    assert fresh.headers["ETag"] == '"' + etag + '"'
    assert (
        "public" in fresh.headers["Cache-Control"]
        and "max-age=60" in fresh.headers["Cache-Control"]
    )
    assert private.headers["Cache-Control"] == "private, no-store"
    return {
        "conditional_status": 304,
        "changed_validator_status": 200,
        "etag_binds_exact_bytes": True,
        "private_policy": private.headers["Cache-Control"],
        "browser_cache_executed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
