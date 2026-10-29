## Starting point and result

Authentication combines credential verification with a session that identifies later requests. Django supplies password hashing, authentication backends and session integration, but the application must still connect those pieces correctly. This chapter runs a real password check, login, authenticated request and logout against migrated temporary tables.

## Mechanism: verify a credential, then establish session identity

Create_user hashes the password using the configured password hasher. The stored value is not the original password. Authenticate asks the configured backend to verify the submitted credentials and return a user when allowed. Login records the authenticated user in the session; AuthenticationMiddleware reconstructs request.user on later requests.

SessionMiddleware must run before AuthenticationMiddleware in this standard setup. The database-backed session table is created by actual migrations. A successful password check without a session write would not make an unrelated later request authenticated.

The fixture uses one synthetic password and a temporary database. Its login/logout views are intentionally focused on the authentication mechanism. CSRF enforcement is treated explicitly in chapter 055 and combined in the later walkthrough; this chapter does not claim that a default test client has validated CSRF protections.

## Worked case: authenticate and carry identity across requests

The program creates the user and checks both that the stored password differs from the submitted password and that check_password accepts the original. A client initially receives 401 from the protected me endpoint. Submitting correct credentials to login establishes the session, and the next request returns the expected username.

The same client matters because it retains cookies between calls. Constructing an unrelated client for the second request would omit the session continuity being tested. This is similar to a browser's cookie jar at the framework level, although the test does not establish real browser cookie policy or network transport.

A production login flow also needs account policy, abuse controls, secure transport and safe error messages. Those additions should preserve the core distinction between verifying a password and authorizing a later resource operation.

## Worked case: wrong credentials and logout

A wrong password returns a generic authentication refusal and does not establish identity. After a later successful login, logout removes the authenticated session state. A subsequent protected request again receives 401. The program checks the complete transition sequence rather than only the login response.

A response saying logged out is insufficient if the server still accepts the old session context. Conversely, clearing only a display variable in the frontend does not revoke the server session. The relevant boundary is the framework's session state and how later requests are interpreted.

Password hashing is deliberately computationally costly. Do not replace it with a plain hash or plaintext comparison for production performance. Test fixtures can choose controlled settings, but should clearly distinguish those settings from the deployed security policy.

## Failure diagnosis and discussion

**Why is force_login not used here?** It intentionally bypasses credential verification and is useful for testing authorized views. This chapter specifically needs to test actual authentication, so it exercises authenticate and login.

**Does request.user being authenticated imply access to every record?** No. Permissions and ownership still restrict operations and data. The next chapter demonstrates those separate checks.

If login returns success but later requests are anonymous, inspect cookie continuity, session backend configuration and middleware order. If passwords appear in logs, fix diagnostic handling immediately rather than masking only the response. Continue with groups and object access to apply an established identity safely.
