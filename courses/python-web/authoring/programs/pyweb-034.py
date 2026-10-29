"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from fastapi import FastAPI
    from fastapi.exceptions import ResponseValidationError
    from fastapi.testclient import TestClient
    from pydantic import BaseModel

    class PublicUser(BaseModel):
        id: int
        name: str

    app = FastAPI(docs_url=None, redoc_url=None)

    @app.get("/user", response_model=PublicUser)
    def user():
        return {
            "id": 1,
            "name": "Ada",
            "password_hash": "fixture-must-not-leak",
            "internal_role": "admin",
        }

    @app.get("/broken", response_model=PublicUser)
    def broken():
        return {"id": "not-an-integer", "name": None}

    with TestClient(app) as client:
        public = client.get("/user").json()
        assert public == {"id": 1, "name": "Ada"}
        try:
            client.get("/broken")
        except ResponseValidationError:
            diagnosed = True
        else:
            diagnosed = False
    assert diagnosed
    with TestClient(app, raise_server_exceptions=False) as client:
        error = client.get("/broken")
        assert error.status_code == 500 and "not-an-integer" not in error.text
    return {
        "filtered_public_fields": public,
        "response_bug_exposed_to_test": True,
        "public_server_error": 500,
        "response_validation_is_not_client_input_validation": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
