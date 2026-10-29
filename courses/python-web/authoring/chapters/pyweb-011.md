## Starting point and result

A repeatable web test needs a clear owner for every piece of state. A client cookie jar, an application object's in-memory data and a persistent database have different lifetimes. This chapter uses a real application factory to show which state is shared and which is isolated.

## Mechanism: create the application deliberately

`make_app()` constructs a Flask application, a fresh item list and its route functions. The functions close over that list, so clients of the same application see the same server-side fixture. Each test client separately owns its cookies. The session's created-count therefore belongs to the client's signed session, while the total item count belongs to the application fixture.

Factories are useful beyond tests. They let deployment code construct an application from explicit configuration and make dependencies easier to replace. They also discourage accidental reliance on a single import-time global object. A factory does not, however, make in-memory state durable or shared across multiple operating-system processes.

The program uses explicit assertions rather than depending on previous examples having run. Every fixture begins from a known state. In the classroom, each ordinary run starts a fresh process, so a Python list from an earlier run should not be expected to remain available. Saved editor drafts and notes have a different persistence mechanism.

## Worked case: two clients share server data but not cookies

The first client creates an item. Its response shows one server item and one item created by that client. The second client uses the same application object but a different cookie jar. It sees one server item and a client-created count of zero.

This result is expected. Client isolation does not mean every client receives a private copy of public server resources. Conversely, sharing one application does not mean every client should inherit another client's authenticated session or private preferences. The test makes both boundaries observable with separate values.

When testing authentication, create distinct client instances for different users. Reusing a cookie jar can accidentally make a supposedly anonymous request authenticated, producing a misleading permission test. Similarly, a shared database fixture can retain records from a previous case unless its transaction/reset policy is explicit.

## Worked case: a new application starts with a fresh fixture

A third client belongs to a newly constructed application. Both counts start at zero. This verifies the factory's state boundary. It would fail if the list were defined as a module global and every factory invocation reused it unintentionally.

The example intentionally reports that the item list does not survive process restart. Later workshops use an explicitly persistent database and test stop/resume behavior. An in-memory dictionary should not be presented as a production storage layer merely because a client test passes.

## Failure diagnosis

Tests that pass individually but fail in a suite often share state accidentally. Inspect module globals, default mutable arguments, reused cookies, global dependency overrides and database cleanup. Tests that pass only in a particular order may be relying on another test to create data. Make each case's setup and expected initial state explicit.

Avoid fixing test contamination by blindly resetting an entire developer or learner database. Use owned temporary state, transactional test databases or clearly scoped fixtures. The classroom and its service workshops preserve learner data independently from these disposable test examples.

## Interview discussion

**What does a fresh client isolate?** Primarily client-side request state such as its cookie jar. It does not automatically create a new server application or database.

**Why can globals fail under multiple workers?** Each process can have its own copy. Changes in one worker may not appear in another, and all copies disappear when their processes end. Shared state needs an appropriate external consistency model.

## Next step

Use explicit resource identities and representations so clients can act without depending on hidden conversational state in a particular server process.
