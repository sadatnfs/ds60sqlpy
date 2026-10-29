## Starting point and result

A blueprint groups related Flask routes and handlers so an application can compose them deliberately. It does not create a completely separate server. This chapter registers an API blueprint and compares an error raised inside a matched blueprint route with a request that matches no route at all.

## Mechanism: registration determines names and boundaries

The blueprint has the name `api` and URL prefix `/api`. Its item function becomes the endpoint `api.item`, while its path is `/api/items/<int:key>`. Endpoint names support URL construction; path prefixes organize request targets. They are connected but not interchangeable identifiers.

A blueprint can register error handlers for errors arising while its route is being handled. An unmatched URL may be rejected before Flask knows which blueprint, if any, should own it. The application therefore also supplies a global 404 handler. This difference matters when designing a consistent API error format.

The application registers the blueprint once during initialization. Adding routes after the app has started handling requests or repeatedly registering the same named blueprint without a deliberate naming strategy can produce lifecycle problems. Assemble the application predictably in its factory.

## Worked case: an error inside a known blueprint route

`/api/items/1` matches the route and returns its item. `/api/items/99` also matches the same route, but the handler intentionally calls `abort(404)` because the fixture contains no such item. The blueprint-specific error handler returns a JSON response identifying its scope.

Both routing and business lookup matter here. The second request found a handler, so the error came from a domain decision within that handler. In a larger application, a typed domain exception could be translated to the public error representation instead of scattering low-level response construction throughout the code.

## Worked case: an unmatched URL uses the application boundary

`/api/no-route` does not match the blueprint's item route. Its 404 is handled by the application's global handler. The URL happens to begin with `/api`, but that textual prefix alone does not establish which blueprint should handle an unmatched route.

The program checks that both failures have status 404 while their handler labels differ. This exposes a common misconception: defining one blueprint 404 handler is not sufficient to guarantee that every URL under a prefix receives the same custom body. Plan your application-level fallback as well.

## Failure diagnosis

If `url_for` cannot find an endpoint, check whether the blueprint name is part of the endpoint identity and whether the blueprint was registered. If a custom error body appears for some 404s but not others, distinguish matched-route failures from routing failures. If the application has several blueprints, avoid inferring authorization or ownership merely from their prefixes.

Blueprints are organizational boundaries. They can help structure a product by domain, but they do not automatically provide database isolation, independent deployment or a security boundary. Shared application configuration and extensions still need coherent ownership.

## Interview discussion

**Why can the global 404 handler run for a URL beginning with a blueprint prefix?** A failed route match may occur before a blueprint has been selected. The prefix string does not by itself bind the request to a registered handler.

**When would separate applications be preferable?** When the deployment, configuration or trust boundaries require it. A blueprint is useful composition within one Flask application; it does not independently establish those wider boundaries.

## Next step

Follow the contexts that make `request`, `g` and `current_app` available, and close resources reliably when a request fails.
