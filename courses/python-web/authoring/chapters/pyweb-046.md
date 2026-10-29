## Starting point and result

Middleware wraps the view with behavior that can inspect requests and responses. Ordering determines which component sees an input first and which sees the response last. This chapter records the real Django middleware sequence for a successful view and for a view that raises an exception.

## Mechanism: nested wrappers form a request pipeline

A middleware factory receives get_response and returns a callable. That callable performs work before invoking the next component, then can inspect or modify the response afterward. With an outer and inner middleware, the request travels outer-to-inner-to-view; the response returns view-to-inner-to-outer.

This nesting is why middleware ordering is part of application behavior. Session middleware must prepare session state before components that use it. Authentication middleware relies on session handling in a standard session-auth configuration. Security headers, compression and caching can also interact according to their positions.

Django places exception-to-response handling around relevant stages. A view exception may therefore be converted into an HTTP response before an outer middleware's after section runs. That is different from assuming every view exception propagates unchanged through all wrapper functions. The example observes the actual behavior instead of relying on a generic decorator analogy.

## Worked case: trace a successful request

The two middleware record before and after markers. The view records its own marker and returns JSON. The expected order is Outer before, Inner before, view, Inner after, Outer after. The program asserts the complete sequence and the successful response.

The middleware also adds response headers, showing that after work can modify the returned representation. In a real application, such headers should have clear ownership to avoid multiple layers overwriting each other unpredictably. A trace test can reveal accidental ordering changes during refactoring.

The list is deliberately local to one finite test. Production request traces need correlation identities and concurrency-safe observation. A shared global list is not a suitable tracing backend for a multi-worker service, and this example does not advertise it as one.

## Worked case: a view failure still yields a response path

The second view raises an exception containing private diagnostic text. The client is configured to observe the resulting HTTP response rather than reraising the exception to the test. It receives 500, and both middleware after markers still appear in the expected reverse order.

The public response does not contain the private diagnostic phrase. That assertion distinguishes safe public handling from internal error visibility. Production logs can retain a controlled traceback and request identity without exposing those details to the caller.

A middleware that needs cleanup regardless of all possible errors should still use appropriate finally/context-manager ownership. The observed view-exception conversion does not justify assuming that every failure inside middleware initialization, streaming iteration or external cleanup will behave identically.

## Failure diagnosis and discussion

**Why did adding middleware change authentication behavior?** Its position may alter when session or user state exists. Read the required ordering of each component and test the actual chain.

**Why might an after hook see 500 instead of catching the original exception?** Django may have converted the downstream exception to a response. Use the framework's documented exception hooks or logging behavior for the diagnostic you need.

When debugging order, record safe stage names and statuses rather than copying request bodies. If a response header disappears, inspect every layer that can replace the response. Continue with templates, where composition has a different structure but similarly requires explicit escaping and asset boundaries.
