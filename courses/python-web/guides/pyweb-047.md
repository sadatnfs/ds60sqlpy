# pyweb-047: Django templates, inheritance and static assets

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-046`.

## Starting point and result

Django templates separate presentation from Python view logic and support inheritance for shared page structure. They also escape ordinary inserted text by default. This chapter renders a small inherited page, checks untrusted text handling and distinguishes generating a static-asset URL from actually serving that asset.

## Mechanism: blocks, context and escaping

A base template defines named blocks such as title and body. A child extends the base and replaces selected blocks. Context values supply data to the template. This keeps common document structure in one place while allowing individual pages to specialize their content.

Autoescaping converts characters that would otherwise be interpreted as HTML syntax. A user-provided script-like string should appear as text, not become an executable element. The safe filter overrides that protection and should be reserved for content whose trust and construction are explicitly controlled.

Escaping is context-sensitive. HTML text escaping does not automatically make a value safe inside JavaScript, a CSS declaration or an arbitrary URL scheme. Use appropriate structured mechanisms for those contexts rather than treating one safe marker as a universal sanitizer.

The static template tag builds an asset URL through the configured staticfiles storage. In deployment, collectstatic prepares files and the chosen server/storage layer delivers them. Merely seeing a static URL in rendered HTML does not prove the corresponding file is available offline.

## Worked case: inherit a page and escape its title

The child template overrides the page title and body while using the base document structure. Its context contains script-like text. The rendered result has the intended title, escaped text and a local static stylesheet path. The assertions inspect all three features.

The example uses Django's in-memory template loader so the entire finite fixture is visible and needs no hidden files. A normal project stores templates in its documented directories or applications. The template engine and escaping behavior are real in both cases.

An inherited block can accidentally omit accessibility or metadata provided by the base. Review the complete rendered page, not only the changed child fragment. A source-level block name does not guarantee that the final document structure remains appropriate.

## Worked case: an explicit trusted fragment bypasses escaping

A separate tiny template applies safe to a fixed original HTML fragment. The output contains actual markup. This demonstrates the mechanism rather than encouraging its use with user input. Replacing that fixed fragment with untrusted content would change the trust boundary and could introduce script execution.

The contrast explains why safe is a security-relevant operation. It is not a formatting convenience for strings that happen to contain angle brackets. If the product truly accepts rich user HTML, it needs a reviewed sanitizer and content policy, with tests for the allowed and refused constructs.

The local stylesheet path remains only a URL in this test. The owned Docker workshop prepares Django admin assets with collectstatic and serves local files through an explicit static middleware/server boundary. Browser acceptance checks the real asset requests separately.

## Failure diagnosis and discussion

**Why does a template display literal tags?** Autoescaping is working. Decide whether the value should be plain text or deliberately trusted markup before adding safe.

**Why does a page render while its styling is missing?** URL generation and asset delivery are separate. Inspect STATIC_URL, prepared static files and the server route, then check the actual network response.

If inheritance appears ignored, inspect extends placement, block names and template resolution order. Continue with models and migrations, where the database's persistent schema needs a similarly explicit preparation lifecycle.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        INSTALLED_APPS=["django.contrib.staticfiles"],
        STATIC_URL="/static/",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "OPTIONS": {
                    "loaders": [
                        (
                            "django.template.loaders.locmem.Loader",
                            {
                                "base.html": (
                                    "<!doctype html><title>{% block title %}Notes{% endblock %}"
                                    "</title><main>{% block body %}{% endblock %}</main>"
                                ),
                                "page.html": (
                                    "{% extends 'base.html' %}{% load static %}"
                                    "{% block title %}Review{% endblock %}"
                                    "{% block body %}<p>{{ title }}</p>"
                                    "<link rel='stylesheet' href='{% static \"site.css\" %}'>"
                                    "{% endblock %}"
                                ),
                            },
                        )
                    ]
                },
            }
        ],
    )
    import django

    django.setup()
    from django.template.loader import render_to_string

    rendered = render_to_string("page.html", {"title": "<script>alert(1)</script>"})
    assert "<title>Review</title>" in rendered
    assert "&lt;script&gt;" in rendered and "<script>" not in rendered
    assert "/static/site.css" in rendered
    from django.template import Context, Engine

    engine = Engine()
    unsafe = engine.from_string("{{ value|safe }}").render(
        Context({"value": "<b>trusted fixture</b>"})
    )
    assert unsafe == "<b>trusted fixture</b>"
    return {
        "template_inheritance": True,
        "untrusted_text_escaped": True,
        "static_url_only": "asset delivery requires collectstatic and an actual server",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
