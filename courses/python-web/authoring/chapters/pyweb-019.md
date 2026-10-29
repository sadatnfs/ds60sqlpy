## Starting point and result

Authentication establishes an identity from credentials. A session mechanism then lets subsequent requests recover that identity. This chapter uses Flask-Login, an actual password hash and a real client cookie jar to observe anonymous refusal, a failed login, a successful login and logout.

## Mechanism: the loader restores identity

The User object supplies the identity contract expected by Flask-Login through UserMixin. The login manager's user loader maps a stored ID back to the current user record. `login_user` records the authenticated identity in the session; `login_required` checks it when the account endpoint is called. Logout removes the authenticated state.

The fixture uses Werkzeug password hashing and verification. The stored value is a hash, and the submitted password is checked through the library. The endpoint exposes neither the hash nor the password in its response. This is different from comparing a submitted password directly with a stored plaintext value.

The example returns JSON 401 responses for unauthenticated API requests through a configured unauthorized handler. A browser-oriented application may instead redirect to a login page. Choose the behavior intentionally; otherwise an API client can receive an HTML login page when it expected JSON.

## Worked case: anonymous and invalid credentials

The client first requests the protected account endpoint without a session and receives 401. It then submits an incorrect password and again receives 401. No authenticated account representation is returned.

A public invalid-credential message should avoid unnecessarily revealing whether the username or password was the failing component. Rate limits, monitoring, credential recovery and stronger authentication factors belong to the wider system. This small fixture focuses on the library's identity and session behavior, while later integration combines the surrounding controls.

## Worked case: login establishes and logout removes access

A correct password produces a successful login. A subsequent request through the same client cookie jar returns the intended user ID and name. After logout, the protected endpoint again returns 401. The program checks the entire sequence instead of treating the login response alone as sufficient evidence.

The user loader matters on later requests. A session may contain an ID whose user has since been disabled or deleted. A real loader should reflect the current authorization/account policy rather than reconstructing a privileged object from untrusted session fields. The next chapter adds per-object ownership checks after identity is established.

## Failure diagnosis

Unexpected anonymous responses can result from a missing user loader, inconsistent session keys or cookie scope. Unexpected authenticated responses in tests can result from reusing another test's client cookie jar. A successful login that survives an intended logout suggests incorrect state removal or testing the wrong client instance.

This program isolates authentication. Its finite JSON login fixture does not claim a complete browser login defense. The workshop combines the preceding CSRF controls, configuration and durable storage. Do not use the literal fixture signing key or test account as deployment configuration.

## Interview discussion

**What does `login_required` prove?** It checks the authentication state under the configured library. It does not by itself prove that the user owns a requested object or may perform every action.

**Why load the user again rather than trusting a complete serialized user object?** Account status and permissions can change. A stable identifier and a deliberate lookup make that lifecycle clearer and avoid carrying stale authority indiscriminately.

## Next step

Apply authorization to both lists and individual objects. An authenticated user should not gain access to someone else's data by changing a URL or query parameter.
