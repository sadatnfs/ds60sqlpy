"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, ConfigDict, Field

    class Create(BaseModel):
        model_config = ConfigDict(extra="forbid")
        title: str = Field(min_length=1, max_length=60)

    class Note(BaseModel):
        identifier: int
        title: str

    app = FastAPI(title="Notes contract", version="1.0.0", docs_url=None, redoc_url=None)

    @app.post("/notes", response_model=Note, status_code=201, operation_id="createNote")
    def create(payload: Create):
        return {"identifier": 1, "title": payload.title}

    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        operation = schema["paths"]["/notes"]["post"]
        assert operation["operationId"] == "createNote"
        assert "201" in operation["responses"] and "422" in operation["responses"]
        assert schema["components"]["schemas"]["Create"]["required"] == ["title"]
        assert schema["components"]["schemas"]["Create"]["additionalProperties"] is False
        assert client.get("/docs").status_code == 404 and client.get("/redoc").status_code == 404
        assert client.post("/notes", json={"title": "Contract"}).json() == {
            "identifier": 1,
            "title": "Contract",
        }
        assert (
            client.post("/notes", json={"title": "Contract", "owner": "other"}).status_code == 422
        )
    previous_required = {"title"}
    proposed_required = {"title", "category"}
    assert proposed_required - previous_required == {"category"}
    return {
        "operation_id": "createNote",
        "required_request_addition_is_breaking": ["category"],
        "offline_docs": "workshop serves its own local explorer; no default CDN UI",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
