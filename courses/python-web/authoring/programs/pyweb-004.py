"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request

    app = Flask(__name__)

    @app.post("/echo")
    def echo():
        if not request.is_json:
            return {"error": "application/json is required"}, 415
        value = request.get_json(silent=True)
        if not isinstance(value, dict) or not isinstance(value.get("text"), str):
            return {"error": "a JSON object with text is required"}, 400
        return {"text": value["text"], "characters": len(value["text"])}

    with app.test_client() as client:
        valid = client.post("/echo", json={"text": "café"}, headers={"Accept": "application/json"})
        malformed = client.post("/echo", data=b'{"text":', content_type="application/json")
        wrong_type = client.post("/echo", data="café", content_type="text/plain; charset=utf-8")
        assert valid.json == {"text": "café", "characters": 4}
        assert malformed.status_code == 400 and wrong_type.status_code == 415
        assert len("café".encode()) == 5
    return {
        "parsed_representation": valid.json,
        "utf8_bytes": 5,
        "malformed_status": 400,
        "unsupported_media_type_status": 415,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
