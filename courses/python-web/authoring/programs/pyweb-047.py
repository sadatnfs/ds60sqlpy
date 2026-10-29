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
