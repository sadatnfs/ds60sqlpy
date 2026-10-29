"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="x" * 64,
        DEBUG=True,
        ALLOWED_HOSTS=[],
        INSTALLED_APPS=[],
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
        ],
        ROOT_URLCONF=__name__,
        SESSION_COOKIE_SECURE=False,
        CSRF_COOKIE_SECURE=False,
        SECURE_SSL_REDIRECT=False,
    )
    import django

    django.setup()
    from django.core.checks import run_checks
    from django.http import JsonResponse
    from django.test import override_settings
    from django.urls import path

    def view(request):
        return JsonResponse({"ok": True})

    global urlpatterns
    urlpatterns = [path("", view)]
    ids = {issue.id for issue in run_checks(include_deployment_checks=True)}
    assert {"security.W018", "security.W020"}.issubset(ids)
    with override_settings(
        DEBUG=False,
        ALLOWED_HOSTS=["web.example"],
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
        SECURE_SSL_REDIRECT=True,
        SECURE_HSTS_SECONDS=3600,
        SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
        SECURE_HSTS_PRELOAD=True,
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
        SECRET_KEY="fixture-only-72-char-mixed-string-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ-abcdef",
    ):
        revised = {issue.id for issue in run_checks(include_deployment_checks=True)}
        assert not {
            "security.W018",
            "security.W020",
            "security.W008",
            "security.W012",
            "security.W016",
        }.intersection(revised)
    return {
        "initial_check_ids": sorted(ids),
        "revised_check_ids": sorted(revised),
        "scope": "configuration diagnostics, not actual TLS or proxy acceptance",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
