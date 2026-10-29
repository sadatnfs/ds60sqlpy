"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from itertools import count

    from flask import Flask, current_app, g, request

    app = Flask(__name__)
    app.config["TESTING"] = True
    identifiers, closed = count(1), []

    @app.before_request
    def open_resource():
        g.resource = {"id": next(identifiers)}

    @app.teardown_request
    def close_resource(error):
        resource = g.pop("resource", None)
        if resource is not None:
            closed.append({"id": resource["id"], "failed": error is not None})

    @app.get("/ok")
    def ok():
        return {"id": g.resource["id"], "path": request.path}

    @app.get("/fail")
    def fail():
        raise RuntimeError("intentional fixture failure")

    client = app.test_client()
    assert client.get("/ok").json == {"id": 1, "path": "/ok"}
    try:
        client.get("/fail")
    except RuntimeError as error:
        assert str(error) == "intentional fixture failure"
    else:
        raise AssertionError("Testing must propagate this intentional exception")
    assert closed == [{"id": 1, "failed": False}, {"id": 2, "failed": True}]
    with app.app_context():
        assert current_app is not None
        try:
            _ = request.path
        except RuntimeError:
            no_request = True
        else:
            no_request = False
    assert no_request
    return {"closed_resources": closed, "application_context_is_not_request_context": no_request}


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
