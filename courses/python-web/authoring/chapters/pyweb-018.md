## Starting point and result

A browser form needs both field validation and a decision about whether the request is authorized to use the client's ambient credentials. CSRF protection addresses one part of that request-origin problem. This chapter uses Flask-WTF and its actual CSRF machinery rather than substituting a manually checked placeholder field.

## Mechanism: a form token participates in a larger session contract

The application enables CSRF protection and uses a test-only signing key. The form contains a name field with DataRequired and length validation. Rendering `hidden_tag()` supplies the framework's hidden fields, including the CSRF token. A client must return the appropriate token while retaining the associated session context.

Field validation and CSRF validation are distinct. A request can contain a valid name but lack a valid token, or it can contain a valid token but an invalid name. Keeping those cases separate makes the public behavior and tests easier to understand.

The test uses an HTML parser to locate the token by its field name. It does not depend on one brittle attribute ordering in the rendered HTML. This is a small example of testing a semantic contract rather than a serialization accident.

## Worked case: a complete valid form

The client first retrieves the form, retains the response cookies and extracts its token. It posts a valid name together with that token. The real form validation succeeds and returns status 201 with the validated name.

The response proves that this client request passed the configured server checks. It does not establish browser SameSite behavior, TLS or a deployed identity-provider flow. The owned application combines the relevant controls and provides separate browser/network acceptance.

For real deployments, the signing key, cookie settings, token lifetime and origin configuration must follow the deployment's trust boundary. The literal key here exists only to make the finite test fixture self-contained.

## Worked case: missing token versus invalid field

The next request submits a valid name without a token and receives 400. Another request submits the token but an empty name and also receives 400. Those equal status codes do not mean the failures had the same cause. The example exercises both checks deliberately.

Testing configurations sometimes disable CSRF to simplify unrelated tests. That can be useful for isolated business logic, but it would invalidate a test claiming to check CSRF. This fixture explicitly leaves the protection enabled and obtains a real token through the application.

## Failure diagnosis

If a valid-looking token fails, inspect session continuity, signing-key consistency, expiration and the configured field/header name. A token copied from a different session may not satisfy the intended contract. If an entire test suite accepts forms without tokens, inspect its configuration before concluding that CSRF protection works.

A hidden input is not automatically secret or trustworthy. The browser client can inspect and modify it. Its usefulness comes from the server's validation and association with the appropriate context, not from hiding it visually in a form.

## Interview discussion

**Why does authentication not eliminate CSRF?** A browser may attach cookies automatically. Authentication identifies the credentials; CSRF controls help determine whether the state-changing request should be accepted under the application's browser-origin/session design.

**Should a CSRF test simply hard-code a token string?** Use the real framework's token generation and request flow unless the test is explicitly a lower-level unit test. A placeholder comparison does not qualify the framework integration.

## Next step

Use the authentication library's actual login and logout behavior, then apply object-level authorization to the identity it establishes.
