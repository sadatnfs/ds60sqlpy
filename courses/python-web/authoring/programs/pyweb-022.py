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
