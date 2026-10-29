"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from typing import Annotated

    from fastapi import FastAPI, Path, Query
    from fastapi.testclient import TestClient
    from pydantic import BaseModel

    class Item(BaseModel):
        id: int
        tags: list[str]

    app = FastAPI(docs_url=None, redoc_url=None)

    @app.get("/items/{item_id}", response_model=Item)
    def item(item_id: Annotated[int, Path(ge=1)], limit: Annotated[int, Query(ge=1, le=5)] = 2):
        return {"id": item_id, "tags": [f"tag-{i}" for i in range(limit)]}

    with TestClient(app) as client:
        valid = client.get("/items/7?limit=3")
        assert valid.status_code == 200 and valid.json() == {
            "id": 7,
            "tags": ["tag-0", "tag-1", "tag-2"],
        }
        invalid = [client.get(url) for url in ("/items/0", "/items/seven", "/items/7?limit=6")]
        assert all(response.status_code == 422 for response in invalid)
    return {
        "valid": valid.json(),
        "invalid_statuses": [r.status_code for r in invalid],
        "typed_inputs_and_response_executed": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
