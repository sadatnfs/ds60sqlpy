## Starting point and result

A reverse proxy can terminate TLS and forward requests to an application over another connection. The application may need to know the original scheme or host, but trusting forwarded headers from arbitrary clients is unsafe. This chapter demonstrates the exact effect of proxy trust configuration and a separate host allowlist.

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

## Failure diagnosis and discussion

**Why can secure redirects loop behind a proxy?** The application may repeatedly see the internal HTTP hop because original-scheme information is missing or incorrectly trusted. Fix the topology/configuration rather than disabling all security behavior blindly.

**Why is trusting X-Forwarded-Host especially consequential?** It can influence absolute URLs, redirects and security decisions. Only accept it from a controlled path that sanitizes caller input.

If a forged header changes behavior unexpectedly, inspect the exact trust configuration and whether direct access bypasses the proxy. If host checks fail only in deployment, inspect the actual forwarded Host contract. Continue with container deployment, where ports, health, migrations and persistent state become concrete operational boundaries.
