"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, render_template_string, request
    from markupsafe import Markup

    app = Flask(__name__)

    @app.get("/card")
    def card():
        return render_template_string(
            "<article><h1>{{ title }}</h1><p>{{ badge }}</p></article>",
            title=request.args.get("title", "Untitled"),
            badge=Markup("<strong>Reviewed fixture</strong>"),
        )

    @app.get("/link")
    def link():
        destinations = {"home": "/", "help": "/help"}
        target = destinations.get(request.args.get("destination", "home"))
        if target is None:
            return {"error": "unknown destination"}, 400
        return render_template_string('<a href="{{ target }}">Continue</a>', target=target)

    with app.test_client() as client:
        hostile = client.get("/card", query_string={"title": '<script>alert("x")</script>'})
        body = hostile.get_data(as_text=True)
        assert "<script>" not in body and "&lt;script&gt;" in body
        assert "<strong>Reviewed fixture</strong>" in body
        rejected = client.get("/link", query_string={"destination": "javascript:alert(1)"})
        assert rejected.status_code == 400
        assert 'href="/help"' in client.get("/link?destination=help").get_data(as_text=True)
    return {
        "escaped_html": body,
        "unrecognized_url_destination": 400,
        "trusted_markup_is_a_fixed_author_owned_literal": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
