"""Complete finite Flask investigation with original bounded fixtures."""

import json


def enabled(value):
    choices = {"true": True, "false": False}
    if value not in choices:
        raise ValueError("DEMO_ENABLED must be true or false")
    return choices[value]


def make_app(options):
    from flask import Flask

    app = Flask(__name__)
    app.config.from_mapping(TESTING=True, MAX_PAGE_SIZE=20, FEATURE_ENABLED=False)
    app.config.update(options)
    app.extensions["counter"] = {"value": 0}

    @app.get("/settings")
    def settings():
        app.extensions["counter"]["value"] += 1
        return {
            "page_size": app.config["MAX_PAGE_SIZE"],
            "feature": app.config["FEATURE_ENABLED"],
            "requests": app.extensions["counter"]["value"],
        }

    return app


def run_cases():
    first = make_app({"FEATURE_ENABLED": enabled("false")}).test_client()
    second = make_app({"MAX_PAGE_SIZE": 5, "FEATURE_ENABLED": enabled("true")}).test_client()
    assert first.get("/settings").json == {"page_size": 20, "feature": False, "requests": 1}
    assert second.get("/settings").json == {"page_size": 5, "feature": True, "requests": 1}
    assert bool("false") is True
    try:
        enabled("maybe")
    except ValueError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {
        "factory_state_isolated": True,
        "explicit_boolean_parsing": True,
        "unknown_boolean_rejected": rejected,
        "configuration_dump_exposed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
