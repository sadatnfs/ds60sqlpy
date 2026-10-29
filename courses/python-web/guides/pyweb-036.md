# pyweb-036: Bearer tokens, JWT claims and authentication

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-035`.

## Starting point and result

A bearer token grants access to whoever possesses it, so its validation and handling are part of the authentication boundary. A JSON Web Token is a signed claims representation; decoding its JSON is not the same as verifying its authority. This chapter creates a local RSA key pair and checks actual signatures and claims with PyJWT.

## Mechanism: establish issuer, audience and time

The signing key proves that the token was produced by an entity controlling that key. The issuer claim names the expected issuing authority. The audience claim identifies the intended recipient. Expiration limits when the recipient may accept the token. Subject identifies the principal within the issuer's namespace. These checks answer different questions and all need an explicit policy.

The verifier supplies an allowed algorithm list rather than trusting the token header to choose arbitrary verification behavior. It uses the public key and requires the expected claims. A token signed correctly for a different API must still be refused. A correctly signed but expired token must also be refused.

The example generates keys only for its disposable local fixture. It is not an OAuth authorization server or an OpenID Connect discovery implementation. Real identity integration needs trusted issuer configuration, key rotation, revocation/session policy where required, secure transport and careful logging. Never print a real bearer token merely to make a debugging example convenient.

## Worked case: a valid signed identity

The program creates claims for one synthetic subject, signs them with RS256 and sends the token in an Authorization header. The FastAPI dependency extracts the credential, verifies the signature and claims, and returns the subject. The route exposes only that verified identity.

The successful assertion proves that actual asymmetric verification and request dependency resolution agree. It does not prove that a user completed a login ceremony or that a remote issuer is trustworthy. Those are separate boundaries that the fixture deliberately does not simulate as a full identity provider.

Notice that the private key remains inside the issuing fixture and verification uses its public counterpart. A production verifier should not need the issuer's private signing key. Key distribution and rotation must preserve that separation.

## Worked case: valid-looking but unacceptable tokens

Three tokens fail for different reasons: one targets another audience, one has expired, and one is signed by a different private key. The program also checks a missing credential. Each receives an authentication refusal with a Bearer challenge rather than reaching the route's successful response.

These cases prevent a common mistake: treating the presence of a syntactically valid token as authentication. The JSON can be well formed and its subject can look plausible while the token has no authority for this API. Claim checks must happen after cryptographic verification under trusted configuration.

Time-based tests should avoid relying on a token expiring during execution. This fixture uses an already-expired timestamp and a comfortably future timestamp. A real verifier may define a small clock-skew allowance, but that allowance should be deliberate and bounded.

## Failure diagnosis and discussion

**Does a JWT encrypt its payload?** A signed JWT normally does not. Anyone holding it can inspect its encoded claims. Do not place private data in claims simply because the token looks opaque.

**Does successful authentication grant access to every object?** No. It establishes a principal. Scope, role, tenant and ownership checks still decide which operation that principal may perform.

If every token fails after rotation, inspect trusted key selection and issuer configuration before weakening signature checks. If only one API rejects a token, inspect its audience. Continue with cookies and browser origins, where credential transport introduces different request-forgery concerns.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json
from datetime import UTC, datetime, timedelta
from typing import Annotated


def run_cases():
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from fastapi import Depends, FastAPI, HTTPException
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from fastapi.testclient import TestClient

    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key()
    now = datetime.now(UTC)
    claims = {
        "sub": "learner-17",
        "iss": "https://issuer.example",
        "aud": "notes-api",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    token = jwt.encode(claims, private, algorithm="RS256")
    app = FastAPI(docs_url=None, redoc_url=None)
    bearer = HTTPBearer(auto_error=False)

    def identity(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
        if credentials is None:
            raise HTTPException(
                401, "Authentication required", headers={"WWW-Authenticate": "Bearer"}
            )
        try:
            return jwt.decode(
                credentials.credentials,
                public,
                algorithms=["RS256"],
                audience="notes-api",
                issuer="https://issuer.example",
                options={"require": ["sub", "iss", "aud", "iat", "exp"]},
            )["sub"]
        except jwt.InvalidTokenError as error:
            raise HTTPException(
                401, "Invalid bearer token", headers={"WWW-Authenticate": "Bearer"}
            ) from error

    @app.get("/me")
    def me(user: Annotated[str, Depends(identity)]):
        return {"user": user}

    with TestClient(app) as client:
        assert client.get("/me", headers={"Authorization": "Bearer " + token}).json() == {
            "user": "learner-17"
        }
        bad = [
            jwt.encode({**claims, "aud": "other-api"}, private, algorithm="RS256"),
            jwt.encode({**claims, "exp": now - timedelta(minutes=1)}, private, algorithm="RS256"),
            jwt.encode(
                claims,
                rsa.generate_private_key(public_exponent=65537, key_size=2048),
                algorithm="RS256",
            ),
        ]
        assert client.get("/me").status_code == 401
        assert all(
            client.get("/me", headers={"Authorization": "Bearer " + value}).status_code == 401
            for value in bad
        )
    return {
        "signed_identity": "learner-17",
        "wrong_audience_expiry_and_signature_rejected": True,
        "scope": "local synthetic issuer, no OIDC discovery",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
