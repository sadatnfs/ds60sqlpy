# pyweb-006: HTML templates and context-aware escaping

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-005`, `web-002`.

## Starting point and result

A string can be valid application data while containing characters meaningful to HTML. Templates must preserve the intended distinction between text and markup. This chapter uses real Jinja rendering through Flask and then examines a separate URL-selection boundary.

## Mechanism: escaping depends on the output context

The template places a title inside an HTML heading. Jinja's HTML autoescaping converts characters such as `<` and `>` into their text representations so the browser does not interpret them as element syntax. The example also includes one author-owned constant marked as trusted `Markup` to show the explicit boundary between text and intended markup.

A trusted-markup marker is a promise made by the application author. Applying it to arbitrary request input removes the protection the template would otherwise provide. Escaping is also context-sensitive: HTML text, HTML attributes, JavaScript strings, CSS and URLs have different interpretation rules. Do not assume that one escaping operation validates every later use.

The second endpoint accepts a destination name and maps it to a small allowlist of local paths. It never treats the supplied string as a ready-to-use URL. This addresses a problem HTML escaping alone cannot solve: a syntactically valid attribute can still contain an unwanted URL scheme or destination.

## Worked case: untrusted title remains text

The client sends a title containing a script tag. The response contains an escaped representation and no literal `<script>` element. At the same time, the fixed reviewed badge remains a real `<strong>` element. Assertions check both behaviors, demonstrating that the template can preserve intentional author markup while escaping request data.

The test checks generated HTML. It does not execute a browser or prove every possible browser context safe. The relevant evidence is that these inputs were rendered according to the documented HTML text contract. A browser acceptance test belongs to a later layer.

A useful habit is to trace the origin of each template value. A literal in trusted application source and a string from a query parameter may have the same Python type, but they have different trust histories. The marker should follow the trust decision, not a desire to make formatting appear quickly.

## Worked case: an unwanted destination is rejected

The link endpoint supports the names `home` and `help`. A request for `help` produces the known local path `/help`. A request containing a JavaScript-style destination is not an allowlisted name and returns 400. There is no attempt to make that arbitrary URL safe by escaping it into an attribute.

This small mapping is appropriate when the product offers a finite set of navigation choices. Applications that truly accept arbitrary URLs need a more complete scheme, host and normalization policy. Keeping the product's actual requirements narrow can make the implementation easier to review.

## Failure diagnosis

Unexpected literal markup often comes from a trust marker, a disabled autoescape setting or string concatenation outside the template engine. Unexpected navigation can remain possible even when quotes are escaped correctly. Inspect the output context and the value's allowed meaning separately. Avoid using a regular expression to strip arbitrary HTML and then declaring the remainder universally safe.

## Interview discussion

**Why is input validation not enough for HTML output?** A name or message can be valid data and still contain HTML-significant characters. Rendering must preserve it as text in the intended context.

**When is trusted markup reasonable?** When the application deliberately owns or has appropriately processed that fragment under a clear policy. A request parameter does not become trusted because a template needs bold text.

## Next step

Handle form fields and uploaded bytes. Their filenames and declared media types are inputs to validate, not instructions about where the server should store data.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
