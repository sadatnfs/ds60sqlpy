# pyweb-069: Web threat modeling, proxies and TLS boundaries

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-068`.

## Starting point and result

A reverse proxy can terminate TLS and forward requests to an application over another connection. The application may need to know the original scheme or host, but trusting forwarded headers from arbitrary clients is unsafe. This chapter demonstrates the exact effect of proxy trust configuration and a separate host allowlist.

## Key terms

- **Reverse proxy:** A server in front of the application that can terminate TLS and forward requests to it over another connection.
- **X-Forwarded-Proto:** A header describing the scheme of the original request, trustworthy only when a trusted proxy set or sanitized it.
- **ProxyFix:** Werkzeug middleware that applies forwarded values for a configured number of trusted hops per field, here `x_proto=1` and `x_host=0`.
- **TrustedHostMiddleware:** Starlette middleware that refuses requests whose Host header is not on the allowed list, here with 400.
- **TLS termination:** Ending the encrypted HTTPS connection at a proxy, which then forwards the request over a separate connection.

## Mechanism: a header is a claim until its source is trusted

X-Forwarded-Proto describes an earlier request scheme only when a trusted proxy set or sanitized it. A direct client can send the same header. ProxyFix changes which forwarded values Flask uses according to a configured number of trusted hops for each field.

The fixture trusts one forwarded scheme value but no forwarded host values. That choice makes the scheme change to https while the host remains localhost. It is valid only if the application server is actually reachable through the intended proxy boundary and the proxy controls the relevant header. The middleware cannot establish that network fact by itself.

A host allowlist addresses another input boundary. FastAPI's TrustedHostMiddleware checks the incoming Host against configured allowed names. It does not create TLS or authenticate the caller. Scheme, host, origin and user identity are related but distinct pieces of request context.

## Worked case: compare untrusted and configured forwarding

A Flask client sends forged-looking forwarded scheme and host headers. Without ProxyFix, the request retains its direct http scheme and localhost host. After the configured wrapper is installed, the scheme reflects the forwarded https claim but the host still ignores the forwarded host.

The program asserts both representations. This demonstrates that configuration changes application interpretation, not the physical transport. No encrypted socket was created in either test. A response reporting https is therefore not proof of TLS acceptance.

Trust counts must match the actual proxy chain. Too many trusted hops can let a caller-controlled value enter the trusted portion; too few can produce incorrect URLs or redirect loops. Document the topology and test direct-access refusal as well as the normal proxied path.

## Worked case: refuse an unapproved Host

A separate FastAPI app allows testserver. A normal request succeeds; a request with a forged host receives 400. The actual middleware decision is checked through TestClient.

Host validation can protect URL generation and routing assumptions, but it is not authorization for data access. An allowed Host with an invalid user credential must still be refused by the authentication layer. Likewise, a correct user credential should not make arbitrary forwarded infrastructure claims trustworthy.

Public deployment also needs certificate management, secure cookies, origin/CSRF policy, request-size bounds and secret handling. The local Docker workshop exposes loopback HTTP deliberately and does not claim to qualify a public TLS edge. The chapter explains the extension boundary without inventing a deployed proxy.

## Worked example: which X-Forwarded-For entry to believe

```python
def client_ip(forwarded_for, peer, trusted_hops):
    chain = [part.strip() for part in forwarded_for.split(",")] + [peer]
    return chain[-(trusted_hops + 1)]


header = "6.6.6.6, 203.0.113.9"
peer = "10.0.0.2"
print("leftmost:", header.split(",")[0])
print("one trusted proxy:", client_ip(header, peer, 1))
print("two trusted proxies:", client_ip(header, peer, 2))
```

Expected output:

```text
leftmost: 6.6.6.6
one trusted proxy: 203.0.113.9
two trusted proxies: 6.6.6.6
```

The client sent a forged `X-Forwarded-For: 6.6.6.6`, and the one real proxy at 10.0.0.2 appended the address it actually saw. Reading the leftmost entry trusts the attacker. Counting back one hop from the connected peer gives 203.0.113.9, which is what Werkzeug's `ProxyFix(x_for=1)` does. Claiming two hops when only one proxy exists hands the choice back to the client. The lesson applies the same reasoning to `x_proto=1`: the count must match the real deployment, and the app must not be reachable without passing through that proxy.

## Failure diagnosis and discussion

**Why can secure redirects loop behind a proxy?** The application may repeatedly see the internal HTTP hop because original-scheme information is missing or incorrectly trusted. Fix the topology/configuration rather than disabling all security behavior blindly.

**Why is trusting X-Forwarded-Host especially consequential?** It can influence absolute URLs, redirects and security decisions. Only accept it from a controlled path that sanitizes caller input.

If a forged header changes behavior unexpectedly, inspect the exact trust configuration and whether direct access bypasses the proxy. If host checks fail only in deployment, inspect the actual forwarded Host contract. Continue with container deployment, where ports, health, migrations and persistent state become concrete operational boundaries.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python isolated
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
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
