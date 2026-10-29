## Starting point and result

Django's admin is a privileged application for managing registered models. It should not be confused with a general-purpose end-user interface or assumed safe merely because it is included in the framework. This chapter checks the distinction between an ordinary user, a staff user and a superuser through actual admin requests.

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

## Failure diagnosis and discussion

**Why can a staff member open the admin but not a model page?** Staff status controls entry, while model and custom permissions control specific capabilities. Inspect both levels.

**Why not make every internal operator a superuser?** It removes useful boundaries and increases the effect of mistakes or compromised accounts. Grant explicit roles and retain auditability.

If the admin looks unstyled, inspect collectstatic and actual static responses, not the model registration. If a custom action exposes another tenant's data, inspect its queryset and permission checks. Continue with REST Framework, which provides a different set of serialization and view abstractions for API clients.
