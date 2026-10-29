## Starting point and result

Django class-based views package common request patterns into reusable classes. Their convenience depends on understanding dispatch, inheritance and the methods a generic view calls. This chapter uses a real ListView for pagination and a small mixin that guards a separate view before its handler runs.

## Mechanism: as_view creates the callable boundary

A URL pattern needs a callable. The class's as_view method produces one that creates and dispatches the view for a request. Dispatch selects the method handler, such as get or post. Generic views add hooks for obtaining objects, choosing templates and building context.

A ListView obtains a collection through get_queryset, optionally paginates it and renders a template. Despite the method name, the fixture can return a bounded list so the pagination mechanism is visible without a database. A real QuerySet adds lazy evaluation and query planning considerations from the preceding chapters.

A mixin participates in Python's method resolution order. A guard placed before the base View can check a condition and then call super().dispatch to continue the chain. Failing to call super, or placing classes in an inappropriate order, can bypass expected behavior or prevent the handler from running.

## Worked case: paginate a complete three-item collection

The ListView returns three named items and uses a page size of two. The first page renders two items; the second renders the remaining item. An out-of-range page receives 404. The assertions inspect the actual rendered content and refusal behavior.

The template is loaded from a controlled in-memory loader for this finite program. It uses the object_list context supplied by ListView. A normal application stores the template in its project/application structure, but the generic view's context and pagination behavior are the same mechanisms.

Ordering must be stable when pagination covers database rows. Without a defined order, rows may move between requests even when the page number is unchanged. For frequently changing large datasets, keyset pagination may provide a different and more suitable contract than page-number offsets.

## Worked case: guard dispatch before the handler

The second view combines GuardMixin and View. A request without the synthetic fixture header is refused with 403. A request with the expected value proceeds through super().dispatch and reaches get, returning the successful JSON body.

The header is explicitly a test seam, not authentication. Its purpose is to expose composition order. Real authentication should use Django's established user/session machinery or another reviewed principal boundary, and object permissions still need resource-specific checks.

Mixins should have narrow, documented responsibilities. A class with many overlapping dispatch overrides can become difficult to reason about. Trace the method resolution order and request sequence when behavior is unclear rather than adding another override until tests happen to pass.

## Failure diagnosis and discussion

**Why does a class-based view fail when passed directly to path?** The URL resolver expects the request callable created by as_view, not an uninstantiated class following a different call convention.

**Can a permission mixin replace scoped get_queryset?** Not necessarily. An operation-level permission can admit the view while its queryset still needs to restrict which objects the user can see.

If the wrong template or context appears, inspect the generic view's hook methods and inherited attributes. If a guard never runs, inspect class order and super calls. Continue with actual authentication so the principal consumed by such view composition is established through tested password and session behavior.
