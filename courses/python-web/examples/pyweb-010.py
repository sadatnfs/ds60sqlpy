"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, redirect, request, url_for

    app = Flask(__name__)

    @app.get("/items/<int:item_id>")
    def item(item_id):
        return {"id": item_id}

    @app.get("/dashboard")
    def dashboard():
        return {"page": "dashboard"}

    @app.post("/continue")
    def continue_to():
        allowed = {"dashboard": "dashboard"}
        endpoint = allowed.get(request.form.get("destination"))
        if endpoint is None:
            return {"error": "choose a known destination"}, 400
        return redirect(url_for(endpoint), code=303)

    with app.test_request_context():
        built = url_for("item", item_id=7, language="en")
        assert built == "/items/7?language=en"
    with app.test_client() as client:
        accepted = client.post("/continue", data={"destination": "dashboard"})
        assert accepted.status_code == 303 and accepted.headers["Location"] == "/dashboard"
        assert client.get(accepted.headers["Location"]).json == {"page": "dashboard"}
        denied = client.post("/continue", data={"destination": "https://untrusted.example"})
        assert denied.status_code == 400
    return {
        "generated_url": built,
        "redirect_status": 303,
        "unrecognized_destination": 400,
        "destination_is_an_endpoint_allowlist": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
