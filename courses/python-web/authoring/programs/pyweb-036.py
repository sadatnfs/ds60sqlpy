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
