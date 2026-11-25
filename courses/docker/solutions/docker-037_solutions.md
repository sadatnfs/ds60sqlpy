# docker-037: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-037.md).

## Exercise 1: Distinguish TLS and application authorization.

**Expected answer:** Encrypted authenticated transport versus permission for an action.

**Why:** A correctly encrypted request can still be unauthorized. The application must decide who may read or change its data.

**Approach:** Separate two checks: TLS confirms the server's name and encrypts the hop; the app decides whether this caller may change the counter.

**Why this is correct:** An encrypted POST /increment from any client reaches the same handler, and server.py checks no identity.

**A plausible wrong approach:** Treating HTTPS as access control publishes a writable counter to anyone who can connect.

**How to verify:** Send a request over TLS with no credentials; if it succeeds, authorization is still missing.

## Exercise 2: Predict the effect of a certificate name mismatch.

**Expected answer:** The client cannot validate the requested server name normally.

**Why:** Do not disable verification as the default fix. Correct the intended hostname and certificate relationship.

**Approach:** Compare the hostname the browser used with the names in the certificate.

**Why this is correct:** If they differ, the client cannot confirm it reached the intended server, so it stops before sending HTTP.

**A plausible wrong approach:** Turning off verification makes the error vanish and also accepts an impostor with any certificate.

**How to verify:** Issue a certificate for the hostname clients use, or use the name on the certificate; verification then passes.

## Exercise 3: Draw proxy and upstream trust boundaries.

**Expected answer:** Explicit client-facing and internal hops with identities and timeouts.

**Why:** The drawing should show where TLS terminates and which component validates each request or header.

**Approach:** Draw the client-to-proxy hop and the proxy-to-app hop separately, marking where TLS ends and which component checks headers.

**Why this is correct:** The proxy terminates TLS, so the second hop has its own trust and timeout settings.

**A plausible wrong approach:** Drawing one arrow from browser to app hides that the inner hop may be unencrypted and unauthenticated.

**How to verify:** The drawing names the certificate on hop one, the upstream address and timeout on hop two, and the header policy.

## Exercise 4: Diagnose a proxy 502 separately from an app 404.

**Expected answer:** Upstream failure versus a completed app route response.

**Why:** Use logs and direct owned upstream observations to locate the first failing hop without exposing new ports unnecessarily.

**Approach:** Read the status source: 502 is the proxy saying its upstream failed; 404 with unknown route is server.py answering.

**Why this is correct:** A 404 proves the request reached the handler, while a 502 means it never did or the reply failed.

**A plausible wrong approach:** Republishing the app port on the host to bypass the proxy adds exposure instead of reading proxy logs.

**How to verify:** Proxy logs show the upstream error for the 502, and the app log shows the 404 route.

## Exercise 5: Explain forwarded-header spoofing.

**Expected answer:** Untrusted clients can send headers unless the proxy boundary sanitizes them.

**Why:** Treat those values as claims, not facts. Trust only the configured proxy chain and document how original client identity is derived.

**Approach:** Treat X-Forwarded-For and similar headers as values a client can set unless the proxy overwrites them.

**Why this is correct:** Only a proxy you control that replaces the header gives the app a value worth using.

**A plausible wrong approach:** Rate limiting or logging by a header the client wrote lets anyone claim another address.

**How to verify:** Send a request with a forged header through the proxy; the app sees the proxy's value, not the forged one.

## Exercise 6: State what would be required before public exposure.

**Expected evidence:** A separate deployment design covering access, TLS, limits, operations and data.

**Why:** The local fixture’s simplicity is intentional. Do not advertise a loopback teaching app as public production hosting merely by changing the bind address.

**Approach:** List what public use would need: authentication, TLS, request limits, monitoring, backups and an operator.

**Why this is correct:** The fixture binds 127.0.0.1:18080 because it has none of these, which is acceptable only locally.

**A plausible wrong approach:** Changing the bind to 0.0.0.0 and calling it published exposes an unauthenticated writable counter.

**How to verify:** The publication note marks each item as designed, tested or missing before any exposure.

## Check your transfer

The warning comes from the TLS identity check between the browser and the proxy: the certificate the proxy presents does not list the DNS name users typed. The container port sits behind the proxy and plays no part in that check, so changing it fixes nothing and may break the upstream route. The fix is a certificate whose subject alternative names include that DNS name, installed on the proxy. `openssl s_client -connect` with `-servername` set to that name should show it; if the warning persists, users are reaching a different endpoint.
