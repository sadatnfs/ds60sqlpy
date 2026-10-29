"""Finite cross-framework engineering investigation with explicit scope."""

import json


def run_cases():
    from flask import Flask, request
    from werkzeug.middleware.proxy_fix import ProxyFix

    app = Flask(__name__)

    @app.get("/origin")
    def origin():
        return {"scheme": request.scheme, "host": request.host}

    with app.test_client() as client:
        direct = client.get(
            "/origin", headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "forged.example"}
        ).json
    assert direct == {"scheme": "http", "host": "localhost"}
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=0)
    with app.test_client() as client:
        trusted = client.get(
            "/origin", headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "forged.example"}
        ).json
    assert trusted == {"scheme": "https", "host": "localhost"}
    # This configured app must be reachable only through its actual trusted proxy.
    # A directly reachable client can forge the now-trusted proto header.
    from fastapi import FastAPI
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.testclient import TestClient

    api = FastAPI(docs_url=None, redoc_url=None)
    api.add_middleware(TrustedHostMiddleware, allowed_hosts=["testserver"])

    @api.get("/")
    def home():
        return {"ok": True}

    with TestClient(api) as client:
        assert client.get("/").status_code == 200
        assert client.get("/", headers={"Host": "forged.example"}).status_code == 400
    return {
        "untrusted_forwarding_ignored": direct,
        "configured_proxy_claim": trusted,
        "host_refusal": 400,
        "TLS": "no encrypted socket established by these tests",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True))
