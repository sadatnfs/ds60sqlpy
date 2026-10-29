"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request
    from pydantic import BaseModel, ConfigDict, Field, ValidationError

    class Order(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        item: str = Field(min_length=1, max_length=30)
        quantity: int = Field(ge=1, le=10)

    app = Flask(__name__)

    @app.post("/orders")
    def create():
        try:
            value = Order.model_validate(request.get_json(silent=True))
        except ValidationError as error:
            problems = [
                {"path": list(item["loc"]), "type": item["type"]} for item in error.errors()
            ]
            return {"errors": problems}, 422
        return value.model_dump(), 201

    with app.test_client() as client:
        valid = client.post("/orders", json={"item": "book", "quantity": 2})
        invalid = [
            client.post("/orders", json=body)
            for body in (
                {"item": "book", "quantity": "2"},
                {"item": "book", "quantity": True},
                {"item": "book", "quantity": 2, "approved": True},
            )
        ]
        assert valid.status_code == 201 and valid.json["quantity"] == 2
        assert all(response.status_code == 422 for response in invalid)
        assert invalid[2].json["errors"][0]["type"] == "extra_forbidden"
    return {
        "valid": valid.json,
        "invalid_types": [response.json for response in invalid],
        "validation_does_not_replace_authorization": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
