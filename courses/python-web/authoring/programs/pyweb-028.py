"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from typing import Annotated

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, ConfigDict, Field

    class Patch(BaseModel):
        model_config = ConfigDict(extra="forbid")
        display_name: str | None = None
        age: Annotated[int, Field(strict=True, ge=0)] | None = None

    app = FastAPI(docs_url=None, redoc_url=None)
    record = {"display_name": "Ada", "age": 37}

    @app.patch("/profile")
    def update(payload: Patch):
        record.update(payload.model_dump(exclude_unset=True))
        return record

    omitted = Patch.model_validate({})
    explicit = Patch.model_validate({"display_name": None})
    assert omitted.model_dump(exclude_unset=True) == {}
    assert explicit.model_dump(exclude_unset=True) == {"display_name": None}
    assert explicit.model_dump(exclude_none=True) == {}
    with TestClient(app) as client:
        assert client.patch("/profile", json={}).json() == {"display_name": "Ada", "age": 37}
        assert client.patch("/profile", json={"display_name": None}).json() == {
            "display_name": None,
            "age": 37,
        }
        assert client.patch("/profile", json={"age": "37"}).status_code == 422
        assert client.patch("/profile", json={"admin": True}).status_code == 422
    return {
        "omitted_fields": sorted(omitted.model_fields_set),
        "explicit_fields": sorted(explicit.model_fields_set),
        "explicit_null_preserved": True,
        "strict_integer_and_extra_fields_checked": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
