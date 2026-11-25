# pyweb-061: Django deployment settings and management checks

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-060`.

## Starting point and result

Django's deployment checks inspect settings for known risky combinations. They are useful diagnostics, but a clean configuration report does not prove that TLS, proxies, static files or database recovery actually work. This chapter runs the real check framework against an intentionally incomplete configuration and a more deliberate one.

## Key terms

- **Deployment check:** A Django system check run with `include_deployment_checks` that reports risky production settings under stable IDs such as security.W018.
- **DEBUG:** The setting that enables detailed error pages; leaving it on in deployment exposes internal data and triggers security.W018.
- **HSTS:** HTTP Strict Transport Security: a response header telling browsers to use only HTTPS for the host for `max-age` seconds.
- **HSTS preload:** Inclusion in browser-shipped HTTPS-only lists, which requires a one-year max-age with includeSubDomains and is slow to undo.
- **Content Security Policy:** A response header, configured here through SECURE_CSP, that limits which sources a page may load scripts and other resources from.

## Mechanism: static checks evaluate declared configuration

Run_checks with include_deployment_checks enables checks aimed at deployment settings. Debug mode, host configuration, secure cookie settings, redirect behavior and middleware choices can produce identified warnings. The identifiers are useful for stable assertions and for finding the framework's explanation.

The first configuration deliberately enables DEBUG and leaves ALLOWED_HOSTS empty. The program expects the corresponding warning IDs. The second context changes a reviewed set of settings and confirms that several specific warnings disappear.

These settings are not a universal deployment recipe. Enabling a secure redirect behind a proxy that reports the wrong scheme can cause loops. HSTS has consequences for future browser access and subdomains. Preload-list submission additionally requires a max-age of at least 31536000 seconds (one year) with includeSubDomains, and removal from browser preload lists is slow, so this fixture tests a one-hour max-age without SECURE_HSTS_PRELOAD and records the resulting security.W021 warning as a deliberate decision. Raise max-age in steps only after HTTPS works for every subdomain. A local HTTP workshop may deliberately use different settings from a public HTTPS service and should explain that boundary rather than copying production-looking flags blindly.

## Worked case: detect known unsafe declarations

The initial check run returns a set of issue IDs. The assertions require the debug-mode and empty-host warnings to be present. The program prints the full set so learners can see other findings from the pinned framework version.

A warning list should be investigated, not simply silenced until a command exits cleanly. Some findings may be deliberate in a local fixture; others indicate a missing protection. Record the reason for an exception and test the actual behavior it affects.

The fixture uses a synthetic secret string. Real deployments need secret generation, storage and rotation outside committed source. A string that satisfies a checker's length or character heuristic is not automatically a securely generated secret.

## Worked case: revise settings and inspect the changed findings

An override_settings context disables DEBUG, supplies an allowed host, enables secure cookies and redirect/HSTS declarations, adds clickjacking middleware and changes the fixture secret. The targeted warning IDs are absent in the second result, while security.W021 remains because preload is deliberately not declared.

The same context also enables Django's built-in Content Security Policy support, added in Django 6.0: `django.middleware.csp.ContentSecurityPolicyMiddleware` with `SECURE_CSP = {"default-src": [CSP.SELF]}`, where `CSP` comes from `django.utils.csp`. A test-client request marked secure, with an allowed Host header, then shows the actual response headers: `Strict-Transport-Security: max-age=3600; includeSubDomains` and `Content-Security-Policy: default-src 'self'`. A policy this strict blocks inline scripts and third-party assets, so real pages usually need explicit sources or the `CSP.NONCE` placeholder together with the `csp` template context processor; `SECURE_CSP_REPORT_ONLY` lets you observe violations before enforcing a policy.

This proves that the real framework checks recognized those declarations. It does not establish a TLS handshake, trusted proxy isolation or correct certificate management. Those require actual network tests and infrastructure configuration. The chapter intentionally reports the result as configuration diagnostics.

A production rollout should also check migration state, static-asset delivery, health/readiness semantics and persistent data. A web process can start successfully while its database schema is incompatible. A health endpoint can return 200 while the application cannot complete its principal workflow.

## Worked example: building the HSTS value and its preload threshold

```python
def hsts(seconds, include_subdomains, preload):
    parts = [f"max-age={seconds}"]
    if include_subdomains:
        parts.append("includeSubDomains")
    if preload:
        parts.append("preload")
    return "; ".join(parts)


def preload_ready(seconds, include_subdomains):
    return seconds >= 31536000 and include_subdomains


print(hsts(3600, True, False), preload_ready(3600, True))
print(hsts(31536000, True, True), preload_ready(31536000, True))
```

Expected output:

```text
max-age=3600; includeSubDomains False
max-age=31536000; includeSubDomains; preload True
```

The first line is the header the lesson asserts under its revised settings, built from `SECURE_HSTS_SECONDS=3600` and `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`. It fails the preload list's one year minimum, which is why `security.W021` stays in the revised check ids as a recorded decision. Browsers cache this header for the whole max-age, so a short first value limits the damage if some subdomain still serves plain HTTP.

## Failure diagnosis and discussion

**Why can SECURE_SSL_REDIRECT cause a loop?** The application may see the proxy-to-app HTTP hop without a correctly trusted indication of the original HTTPS request. Trust only headers from the actual controlled proxy path.

**Should every local classroom server enable HSTS?** No. The local serving contract differs from a public HTTPS deployment. HSTS should be applied deliberately to the intended host and subdomain policy.

If checks change after a framework upgrade, read the new check semantics and assess the actual deployment. Do not merely replace expected IDs. Continue with the Django walkthrough to combine validated forms, authenticated ownership, CSRF and real database effects before moving into cross-framework operational design.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python isolated
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
    from django.test import Client, override_settings
    from django.urls import path
    from django.utils.csp import CSP

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
        # A one-hour max-age is a first rollout step. Preload is deliberately
        # absent: the preload list requires at least one year and is slow to undo.
        SECURE_HSTS_SECONDS=3600,
        SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
        SECURE_CSP={"default-src": [CSP.SELF]},
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            "django.middleware.csp.ContentSecurityPolicyMiddleware",
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
        # The missing preload declaration is a recorded decision, not an oversight.
        assert "security.W021" in revised
        response = Client().get("/", secure=True, HTTP_HOST="web.example")
        assert response.status_code == 200
        headers = {
            name: response[name]
            for name in ("Strict-Transport-Security", "Content-Security-Policy")
        }
        assert headers == {
            "Strict-Transport-Security": "max-age=3600; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
        }
    return {
        "initial_check_ids": sorted(ids),
        "revised_check_ids": sorted(revised),
        "revised_headers": headers,
        "scope": "configuration diagnostics, not actual TLS or proxy acceptance",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
