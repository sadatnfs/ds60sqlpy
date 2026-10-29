"""Complete finite framework-client investigation; no external server is started."""

import json


def make_app():
    from flask import Flask, session

    app = Flask(__name__)
    app.secret_key = "test-only-isolation-fixture"
    items = []

    @app.post("/items")
    def create():
        items.append("item")
        session["created"] = session.get("created", 0) + 1
        return {"server_items": len(items), "client_created": session["created"]}, 201

    @app.get("/state")
    def state():
        return {"server_items": len(items), "client_created": session.get("created", 0)}

    return app


def run_cases():
    shared = make_app()
    first, second = shared.test_client(), shared.test_client()
    assert first.post("/items").json == {"server_items": 1, "client_created": 1}
    other_client = second.get("/state").json
    assert other_client == {"server_items": 1, "client_created": 0}
    fresh = make_app().test_client().get("/state").json
    assert fresh == {"server_items": 0, "client_created": 0}
    return {
        "other_client_same_application": other_client,
        "new_application_fixture": fresh,
        "in_memory_items_survive_process_restart": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
