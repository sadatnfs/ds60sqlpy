## Starting point and result

A cookie is a value a server asks a client to retain and send on later matching requests. A session mechanism can use that value to recognize application state. Flask's default session stores signed data in a client cookie. This chapter observes a valid round trip and a deliberately corrupted signature.

## Mechanism: integrity, confidentiality and client policy differ

A signature lets the server detect changes made without the signing key. It does not automatically hide the contents from the client. Sensitive information should not be placed into a readable session cookie merely because it is signed. The example stores only a small visit count and uses an explicitly test-only key.

The response declares Secure, HttpOnly and SameSite=Lax. Secure asks browsers to restrict transmission to secure transport; HttpOnly limits ordinary browser-script access; SameSite influences cross-site cookie behavior. These flags address different concerns. They do not replace authentication, authorization, CSRF design or protection against every form of script injection.

The test client has its own cookie jar, but it is not a browser implementation of all cookie policies. We therefore inspect the declared attributes and the server's signature handling without claiming to have tested browser enforcement or real TLS. The synthetic HTTPS base URL used here does not create a TLS connection.

## Worked case: a valid session survives another request

The `/remember` endpoint writes a visit count into the session. The response emits a Set-Cookie header. The program checks the three declared attributes, then requests `/state` through the same client's cookie jar. The server restores the signed value and reports one visit.

The lifecycle spans two requests, but the fixture does not require a long-running external server. The test client invokes the real application interface for each request. That gives useful evidence about serialization and signature verification while keeping the example finite and reproducible.

For a deployed application, choose a strong secret outside source code, keep it stable across the workers that must accept the same sessions, and define rotation and expiry behavior. The separate workshop owns its configured key and state. Copying this test-only key into a public deployment would invalidate the intended trust boundary.

## Worked case: a modified cookie is not trusted

The program reads its own fixture cookie, appends text and sends it back. The signature no longer verifies. Flask treats the request as a fresh anonymous session, and the state endpoint reports zero visits. This endpoint allows anonymous access, so zero is an expected application response rather than an authentication success.

A protected endpoint should separately require an authenticated identity. An empty session after tampering must not accidentally grant a default administrator role. Keep authentication defaults explicit and conservative instead of interpreting a missing field as a privileged state.

## Failure diagnosis

Sessions that disappear between requests may indicate different signing keys across workers, cookie path/domain mismatches, expiry or browser policy. A signed-cookie session that grows very large can exceed client/header limits; it is not a substitute for an unlimited database. Concurrent requests can also update client-held session state in surprising orders, so important shared state should use an appropriate server-side consistency model.

Cookie ports deserve attention in local development: cookie scoping and browser origin rules are different. Applications on different localhost ports should not assume their cookies are isolated solely by the port number. Use distinct names and deliberate path/domain settings in the owned workshops.

## Interview discussion

**Does signing encrypt session data?** No. Signing protects integrity under the key's assumptions. Confidentiality requires a separate mechanism and careful data minimization.

**Does HttpOnly remove the need for CSRF protection?** No. A browser can still attach cookies to requests. Script access and cross-site request authorization are different issues.

## Next step

Connect these application behaviors to the synchronous WSGI and asynchronous ASGI interfaces used by Python web servers.
