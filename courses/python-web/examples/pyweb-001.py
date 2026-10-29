"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request

    app = Flask(__name__)

    @app.get("/greet/<name>")
    def greet(name):
        return {"message": "Hello, " + name, "method": request.method}, 200

    with app.test_client() as client:
        valid = client.get("/greet/Ada")
        missing = client.get("/unknown")
        assert valid.status_code == 200
        assert valid.json == {"message": "Hello, Ada", "method": "GET"}
        assert valid.headers["Content-Type"].startswith("application/json")
        assert missing.status_code == 404
    return {
        "valid": {"status": valid.status_code, "body": valid.json},
        "unmatched_route": missing.status_code,
        "surface": "real Flask WSGI test client; no TCP server",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
    print("pyweb-001: all reference checks passed")
