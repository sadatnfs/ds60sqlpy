# docker-037: TLS, reverse proxies and publishing responsibly

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-036`

## Learning objectives

Draw proxy and upstream trust boundaries. State what would be required before public exposure. Use TLS, reverse proxy and certificate accurately when you explain what you observed.

## Purpose, vocabulary and mental model

TLS authenticates a server identity and encrypts traffic in transit under its certificate trust model. A reverse proxy receives client requests and forwards them to an upstream application. It can terminate TLS, route hostnames and paths, apply limits and emit access logs. It does not automatically make the upstream application authorized or safe for public use.

The study app is intentionally host-loopback only and uses HTTP for local teaching. Publishing it to the internet would create new requirements: identity, access control, TLS certificates, input limits, abuse handling, patching and operational ownership. This chapter designs that boundary without exposing your machine.

Proxy headers such as a forwarded client address are claims from the proxy chain. An application should trust them only from known proxies under an explicit configuration. Accepting arbitrary client-supplied forwarding headers can break rate limits or audit attribution.

### Key terms

- **TLS:** A protocol that authenticates the server identity and encrypts traffic in transit under a certificate trust model.
- **Certificate:** A signed document binding a server name to a public key, which clients verify through trusted issuers.
- **Reverse proxy:** A server that receives client requests and forwards them to an upstream application, often terminating TLS.
- **Public exposure:** Making a service reachable from the internet, which adds identity, access control, patching and abuse handling duties.
- **Forwarded header:** A proxy-added claim about the original client, which an application should trust only from known proxies.

## Anatomy and a trace you can follow

Draw the full request path before configuring a proxy: client name resolution, public endpoint, TLS handshake, proxy routing, upstream connection and application response. Each hop has its own timeout and identity. A certificate for one hostname does not validate a different name merely because both resolve to the same IP.

Use a synthetic configuration review and diagrams here. The course does not register a domain, request certificates or open firewall ports. A production configuration must use the chosen proxy’s actual documentation and a separate deployment review.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-037.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Read what the fixture tells clients about itself, then sketch the TLS hop it lacks. Run `curl -sv http://127.0.0.1:18080/ 2>&1 | grep '^< '` and read the response headers: `Cache-Control: no-store`, a JSON content type, and a `Server` header naming Python's built-in HTTP server. There is no TLS, no authentication and no forwarded-header handling, which is why the fixture publishes only on loopback. Next run `curl -sv https://127.0.0.1:18080/` and read the failure: the client opens a TLS handshake that a plain HTTP listener cannot answer, an SSL protocol error rather than a certificate problem. Draw the design real exposure would need, browser to a proxy holding a certificate for a DNS name, proxy to `app:8080` on a private network, and label each hop with its identity and timeout.

## Worked example / walkthrough

### Worked example 1: Trace a protected request

This is a conceptual public architecture.

```text
browser -> DNS name -> TLS proxy -> private app endpoint
          certificate name        bounded upstream timeout
```

**Expected observation:** TLS protects the client-to-proxy hop; upstream protection and trust are separate design choices.

### Worked example 2: Compare identity and routing failures

These synthetic symptoms occur at different stages.

```text
certificate name mismatch: TLS identity problem
HTTP 502 from proxy: upstream handling problem
HTTP 401 from app: application authentication requirement
```

**Expected observation:** Changing a container port does not repair an invalid certificate identity.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Distinguish TLS and application authorization.

**Hint:** Ask what TLS proves about the server and what it says about the user.

### Exercise 2: Predict the effect of a certificate name mismatch.

**Hint:** Compare the requested host name with the names in the certificate.

### Exercise 3: Draw proxy and upstream trust boundaries.

**Hint:** Mark where TLS ends and which identity each hop trusts.

### Exercise 4: Diagnose a proxy 502 separately from an app 404.

**Hint:** Check whether the response came from the proxy or from the app.

### Exercise 5: Explain forwarded-header spoofing.

**Hint:** Ask who can set an X-Forwarded-For header.

### Exercise 6: State what would be required before public exposure.

**Expected evidence:** A separate deployment design covering access, TLS, limits, operations and data.

**Hint:** List the access, TLS, limits, operations and data requirements for public use.

## Common mistakes and diagnosis

Treating HTTPS as authorization. Trusting forwarded headers from any client. Publishing the learning server to the internet.

Exercise 4 is this chapter's boundary case: Diagnose a proxy 502 separately from an app 404. Read the proxy log for the upstream it contacted and request the app route directly from an owned vantage point before changing either side.

A proxy in front of an app often keeps its default upstream timeout, and the resulting symptom is misread as an app bug. When the app is slow, the proxy gives up first and returns `504`, while the app finishes the request and, for a `POST /increment`, commits it. The client sees a failure, retries, and the counter moves twice. When the proxy cannot reach the app at all, because of a refused connection or a failed name lookup, it returns `502` instead. Set upstream timeouts deliberately against the app's own limits, log the upstream status beside the proxy status, and treat a proxy `504` on a non-idempotent route as an unknown outcome to reconcile.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Match a certificate mismatch, a proxy 502 and an app 401 to the layer that failed.

**Transfer case.** Users see a browser warning that the certificate is not valid for the site name, and someone suggests changing the app's container port from 8080 to 443. What is wrong with that plan, and what fixes the warning?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Port publishing and mapping](https://docs.docker.com/engine/network/port-publishing/)
- [nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-037: TLS, reverse proxies and publishing responsibly.
Read courses/docker/guides/docker-037.md and courses/docker/lessons/docker-037.md. Direct prerequisites: `docker-036`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
