"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request

    app = Flask(__name__)

    @app.get("/people/<name>")
    def person(name):
        return {
            "name": name,
            "tags": request.args.getlist("tag"),
            "query": request.query_string.decode("ascii"),
            "path": request.path,
        }

    @app.get("/items/<int:item_id>")
    def item(item_id):
        return {"id": item_id, "python_type": type(item_id).__name__}

    with app.test_client() as client:
        encoded = client.get("/people/Ada%20Lovelace?tag=one&tag=two")
        numeric = client.get("/items/7")
        invalid = client.get("/items/seven")
        assert encoded.json["name"] == "Ada Lovelace"
        assert encoded.json["tags"] == ["one", "two"]
        assert numeric.json == {"id": 7, "python_type": "int"}
        assert invalid.status_code == 404
    return {
        "decoded_path_and_repeated_query": encoded.json,
        "converted_path": numeric.json,
        "unmatched_converter": invalid.status_code,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
