"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from flask import Blueprint, Flask, abort, url_for

    app = Flask(__name__)
    api = Blueprint("api", __name__, url_prefix="/api")

    @api.get("/items/<int:key>")
    def item(key):
        if key != 1:
            abort(404)
        return {"id": key}

    @api.errorhandler(404)
    def missing_item(error):
        return {"error": "not found", "handler": "blueprint"}, 404

    @app.errorhandler(404)
    def missing_route(error):
        return {"error": "not found", "handler": "application"}, 404

    app.register_blueprint(api)
    with app.test_request_context():
        assert url_for("api.item", key=1) == "/api/items/1"
    with app.test_client() as client:
        assert client.get("/api/items/1").json == {"id": 1}
        known_route = client.get("/api/items/99")
        unmatched = client.get("/api/no-route")
        assert known_route.status_code == unmatched.status_code == 404
        assert known_route.json["handler"] == "blueprint"
        assert unmatched.json["handler"] == "application"
    return {
        "inside_blueprint": known_route.json,
        "unmatched_route": unmatched.json,
        "url_endpoint": "api.item",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
