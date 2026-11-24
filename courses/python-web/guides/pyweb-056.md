# pyweb-056: Django admin as a privileged application

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-055`.

## Starting point and result

Django's admin is a privileged application for managing registered models. It should not be confused with a general-purpose end-user interface or assumed safe merely because it is included in the framework. This chapter checks the distinction between an ordinary user, a staff user and a superuser through actual admin requests.

## Key terms

- **Django admin:** A privileged built-in application for managing registered models, intended for trusted staff rather than end users.
- **Staff status:** The `is_staff` flag that lets a user enter the admin without granting any model permission inside it.
- **Superuser:** A user with `is_superuser` who receives every permission, so such accounts should be rare and tightly controlled.
- **ModelAdmin:** The class that configures how one model appears and which actions are offered in the admin.
- **force_login():** A test Client method that attaches an authenticated session for a user without checking a password.

## Mechanism: entry permission and model permission differ

Staff status permits access to the admin under Django's normal policy, but it does not grant every model permission. Individual actions still depend on the user's permissions and the ModelAdmin configuration. A superuser has broad authority and should be used sparingly in real operations.

The fixture prepares the actual admin, auth, content-types, sessions, messages and staticfiles applications, along with the required template context and middleware. It runs migrations so the admin operates on real tables rather than mocked permission objects.

The example uses force_login to isolate admin authorization. Password verification is already covered elsewhere. This does not prove a deployed admin login page, rate limiting, external identity integration or TLS configuration. Those need their own acceptance tests.

## Worked case: compare ordinary and staff access

An ordinary authenticated user requesting the admin index is redirected to the login flow rather than admitted as staff. A staff user can open the index, but requesting the user-management changelist receives 403 because that user lacks the relevant model permission.

This is a concrete demonstration that staff is not a blanket authorization switch. A maintainer should grant the minimum intended permissions and inspect custom ModelAdmin methods that can widen visibility or execute actions. Querysets, readonly fields and custom actions each contribute to the actual administrative surface.

An admin index response can be 200 even when no useful models are available to that staff user. Therefore an index-only smoke test is insufficient for checking a particular administrative capability. Test the operation or page that the role is expected to use.

## Worked case: a controlled superuser fixture

The synthetic superuser can open the user changelist, and the rendered HTML contains local admin static-asset URLs. The program asserts that the page is rendered successfully and that those URLs are present.

That asset observation is deliberately limited. The test has not fetched the CSS or JavaScript files from a production server. The owned workshop runs collectstatic during preparation and serves the resulting local files through the chosen static delivery boundary. Browser acceptance verifies those requests without external CDNs.

A real admin must also protect secrets, uploads and custom actions. A model field appearing in an admin form may permit changes that bypass assumptions in a public API. Review administrative writes as another application entrypoint rather than assuming public-route validation covers them.

## Worked example: the staff flag opens the door, permissions open rooms

```python
def admin_status(user, path):
    if not (user["active"] and user["staff"]):
        return 302
    if path == "/admin/":
        return 200
    needed = {"auth.view_user", "auth.change_user"}
    return 200 if user["superuser"] or needed & user["perms"] else 403


people = {
    "ordinary": dict(active=True, staff=False, superuser=False, perms=set()),
    "staff": dict(active=True, staff=True, superuser=False, perms=set()),
    "viewer": dict(active=True, staff=True, superuser=False, perms={"auth.view_user"}),
    "superuser_not_staff": dict(active=True, staff=False, superuser=True, perms=set()),
}
for name, user in people.items():
    print(name, admin_status(user, "/admin/"), admin_status(user, "/admin/auth/user/"))
```

Expected output:

```text
ordinary 302 302
staff 200 403
viewer 200 200
superuser_not_staff 302 302
```

The first three rows reproduce the lesson's observed codes: an ordinary user is redirected to the login page, a staff user sees the empty index but gets 403 on the user changelist, and a staff user with `auth.view_user` can read it. The last row is the less obvious case. `AdminSite.has_permission` checks `is_active` and `is_staff` only, so a superuser account with `is_staff=False` is turned away before its unlimited permissions are consulted. Auditing who can reach the admin therefore means listing both the staff flag and the permission set for every account, not just counting superusers.

## Failure diagnosis and discussion

**Why can a staff member open the admin but not a model page?** Staff status controls entry, while model and custom permissions control specific capabilities. Inspect both levels.

**Why not make every internal operator a superuser?** It removes useful boundaries and increases the effect of mistakes or compromised accounts. Grant explicit roles and retain auditability.

If the admin looks unstyled, inspect collectstatic and actual static responses, not the model registration. If a custom action exposes another tenant's data, inspect its queryset and permission checks. Continue with REST Framework, which provides a different set of serialization and view abstractions for API clients.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    import tempfile
    from pathlib import Path

    from django.conf import settings

    with tempfile.TemporaryDirectory() as directory:
        settings.configure(
            SECRET_KEY="synthetic-local-fixture",
            DEBUG=False,
            ROOT_URLCONF=__name__,
            ALLOWED_HOSTS=["testserver"],
            STATIC_URL="/static/",
            INSTALLED_APPS=[
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
            ],
            MIDDLEWARE=[
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": str(Path(directory) / "db.sqlite3"),
                }
            },
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ]
                    },
                }
            ],
        )
        import django

        django.setup()
        from django.contrib import admin
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        from django.db import connection
        from django.test import Client
        from django.urls import path

        call_command("migrate", verbosity=0)
        User = get_user_model()
        ordinary = User.objects.create_user(username="ordinary")
        staff = User.objects.create_user(username="staff", is_staff=True)
        supervisor = User.objects.create_superuser(
            username="supervisor", email="", password="synthetic-only"
        )
        global urlpatterns
        urlpatterns = [path("admin/", admin.site.urls)]
        client = Client()
        client.force_login(ordinary)
        assert client.get("/admin/").status_code == 302
        client.force_login(staff)
        assert client.get("/admin/").status_code == 200
        assert client.get("/admin/auth/user/").status_code == 403
        client.force_login(supervisor)
        response = client.get("/admin/auth/user/")
        assert response.status_code == 200 and b"/static/admin/" in response.content
        connection.close()
    return {
        "staff_is_not_all_permissions": True,
        "superuser_fixture": True,
        "admin_asset_urls": "rendered only; workshop prepares collectstatic",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
