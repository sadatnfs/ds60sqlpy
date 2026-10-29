## Starting point and result

Django organizes an application around settings, URL configuration, views and reusable applications. This chapter reduces that structure to a complete finite example so each connection is visible. It also demonstrates a subtle boundary: declaring ALLOWED_HOSTS does not mean every arbitrary view automatically calls the host-validation API.

## Mechanism: configuration connects components

Settings define installed applications, middleware, database connections and other process-level choices. Django setup initializes its application registry. A URL configuration contains ordered patterns that resolve an incoming path into a view and captured arguments. A named route supports reverse construction of a URL without duplicating its literal path throughout the code.

A view accepts a request and returns a response. The integer path converter turns matching path text into a Python integer before calling the view. It also determines which text matches the route at all. A word does not reach this view and then fail business logic; it fails URL resolution.

These finite examples configure settings once in a fresh process. A normal project uses a settings module and manage.py rather than calling settings.configure in every file. The larger workshop supplies that multi-file layout. Reconfiguring Django globally inside many tests in one process is not equivalent to isolated project startup.

## Worked case: resolve and reverse one resource URL

The route notes/<int:identifier>/ maps a URL to the detail view. A request for identifier 7 returns its numeric identity and request method. Reversing the named route with identifier 7 produces the same path. The assertions connect inbound routing and outbound URL construction.

A request containing a word in the identifier position receives 404. That response reflects the routing contract. A valid integer referring to a nonexistent database row would require a separate lookup decision inside the view. The two failures can share a public status while arising at different layers.

Named routes help when the URL shape changes. Templates and redirects using reverse can follow the new pattern without hard-coded string edits. They do not automatically preserve external API compatibility, since clients outside the project may still depend on the old URL.

## Worked case: exercise the actual host boundary

The minimal JSON view does not read request.get_host. With no relevant middleware, an untrusted Host header can still reach that view. The program then installs CommonMiddleware and creates a fresh client so the middleware chain is rebuilt. The same untrusted host receives 400.

This is not a recommendation to omit host validation. It demonstrates why a security claim should identify the actual enforcement point. ALLOWED_HOSTS configures Django's host-validation behavior when that boundary is invoked; raw access to request metadata is not the same API.

A production project must review middleware order, trusted proxy behavior and direct access to the application server. Forwarded host settings are meaningful only when the request comes through an actually trusted proxy path. A configuration value alone is not network acceptance evidence.

## Failure diagnosis and discussion

**Why did a route start failing after adding a converter?** The converter changes matching and argument conversion. Inspect URL resolution before debugging the view body.

**Why does changing MIDDLEWARE after constructing a client not affect an already loaded chain?** The client/server may have initialized its handler. Build a new controlled handler for a configuration comparison rather than assuming live mutation rebuilds everything.

If reverse raises a missing-route error, check the route name, namespace and keyword names. If host behavior surprises you, trace get_host and middleware instead of assuming every request follows a particular path. Continue with middleware ordering, which explains how cross-cutting request behavior surrounds the view.
