# pyweb-013: Flask application factories and configuration

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-012`.

## Starting point and result

An application factory is a function that constructs a configured application. This gives tests and deployments a deliberate initialization boundary. The example creates two Flask applications with different options and verifies that their request counters do not share mutable state.

## Mechanism: configuration is typed application input

`app.config.from_mapping` establishes defaults, and `update` applies explicit overrides. Values in environment variables usually begin as strings, so their interpretation needs a defined parser. The helper accepts only the strings `true` and `false`; anything else is rejected. Calling `bool("false")` would produce True because the string is nonempty, an easy configuration mistake to reproduce.

Each factory call also creates a new dictionary in `app.extensions`. The route closes over that specific application object and increments its own counter. Placing the dictionary at module scope would create a different sharing relationship. Copying a mapping that contains mutable nested objects also deserves care: a shallow copy does not necessarily isolate those nested objects.

The settings endpoint exposes only an explicit allowlist of harmless fixture values. Returning an entire configuration object could expose signing keys, database credentials or internal service locations. Test convenience is not a reason to create an unrestricted configuration-dump endpoint in an application.

## Worked case: two independent applications

The first application uses the default page size twenty and a parsed false feature flag. The second uses page size five and a true flag. Each client's first request reports its own settings and counter value one. This verifies both the override behavior and fresh mutable state.

The counter is a fixture, not a production request metric or shared database. Under multiple worker processes, each application instance may have a separate counter. A real metric system deliberately aggregates process-level observations; a real shared domain value belongs in storage with the required consistency semantics.

## Worked case: reject ambiguous configuration

The helper refuses `maybe` instead of guessing whether the feature should be enabled. It also demonstrates the surprising truthiness of the literal string `false`. A failed configuration check at startup is often easier to diagnose than a service silently running in the wrong mode.

Apply the same principle to ports, timeouts, body limits and environment names. Parse them into supported types, check useful bounds and give an actionable error. Some values may have defaults suitable for a local workshop, while a public deployment should require an explicit setting. Keep that distinction in configuration code rather than scattered conditionals throughout handlers.

## Failure diagnosis

If a test unexpectedly sees another test's data, inspect mutable module globals and nested default objects. If a feature flag changes unexpectedly, inspect the value's original representation and parser. If a factory requires an active request context just to construct the app, responsibilities may be mixed: application initialization should not depend on a particular user's request.

Factories also provide a place to register routes, extensions and lifecycle hooks consistently. Repeated ad hoc initialization can register handlers twice or produce partially configured applications. Later chapters use blueprints and explicit resource ownership to keep that assembly understandable.

## Interview discussion

**Why not construct one global application and import it everywhere?** A global object can work in a small program, but factories make configuration and dependency assembly explicit and allow isolated tests. The tradeoff is a little additional structure.

**Should configuration be reread from the environment on every request?** Usually configuration should be parsed at an intentional lifecycle boundary. Dynamic settings need their own consistency, validation and refresh contract rather than accidental per-request variation.

## Next step

Split related routes into a blueprint and observe how endpoint names and error boundaries behave after registration.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
