"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from itertools import count

    from flask import Flask, request, url_for

    app = Flask(__name__)
    records = {}
    identifiers = count(1)

    @app.post("/tasks")
    def create():
        body = request.get_json(silent=True)
        if (
            not isinstance(body, dict)
            or set(body) != {"title"}
            or not isinstance(body["title"], str)
            or not 1 <= len(body["title"]) <= 80
        ):
            return {"error": "one bounded title required"}, 422
        key = next(identifiers)
        records[key] = {"id": key, "title": body["title"]}
        return {**records[key], "links": {"self": url_for("read", task_id=key)}}, 201

    @app.get("/tasks/<int:task_id>")
    def read(task_id):
        if task_id not in records:
            return {"error": "not found"}, 404
        return records[task_id]

    with app.test_client() as client:
        first = client.post("/tasks", json={"title": "Study HTTP"})
        second = client.post("/tasks", json={"title": "Study HTTP"})
        assert first.status_code == second.status_code == 201
        assert first.json["id"] != second.json["id"]
        representation = client.get(first.json["links"]["self"]).json
        assert representation == {"id": 1, "title": "Study HTTP"}
        assert client.get("/tasks/99").status_code == 404
        assert (
            client.post("/tasks", json={"title": "x", "owner": "someone-else"}).status_code == 422
        )
    return {
        "first_representation": representation,
        "repeated_post_created_two_resources": len(records) == 2,
        "resource_url": first.json["links"]["self"],
        "whole_REST_architecture_certified": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
