"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request

    app = Flask(__name__)
    records = {}

    @app.put("/items/<int:item_id>")
    def replace(item_id):
        body = request.get_json()
        if (
            not isinstance(body, dict)
            or set(body) != {"title"}
            or not isinstance(body["title"], str)
        ):
            return {"error": "a complete title representation is required"}, 400
        created = item_id not in records
        records[item_id] = body.copy()
        return {"id": item_id, **records[item_id]}, 201 if created else 200

    @app.delete("/items/<int:item_id>")
    def delete(item_id):
        if item_id not in records:
            return {"error": "not found"}, 404
        del records[item_id]
        return "", 204

    with app.test_client() as client:
        first = client.put("/items/1", json={"title": "HTTP"})
        repeated = client.put("/items/1", json={"title": "HTTP"})
        assert first.status_code == 201 and repeated.status_code == 200
        assert records == {1: {"title": "HTTP"}}
        removed = client.delete("/items/1")
        absent = client.delete("/items/1")
        assert removed.status_code == 204 and removed.data == b""
        assert absent.status_code == 404 and records == {}
    return {
        "put_statuses": [201, 200],
        "delete_statuses": [204, 404],
        "same_effect_does_not_require_same_status": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
