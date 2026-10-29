## Starting point and result

Flask can run async view functions when its async support is installed. The surrounding WSGI execution model still matters. This chapter compares work awaited by a view with a task created and abandoned when that view returns. Both behaviors are observed through actual Flask client requests in the pinned environment.

## Mechanism: the request owns the async view's lifetime

An async function can coordinate awaitable operations. The first route uses `asyncio.gather` to await two small operations and returns their completed sum. Those operations belong to the request's computation, and the response depends on their results.

A background task created with `asyncio.create_task` has a different relationship. Under this ordinary Flask WSGI async bridge, the event loop used for the request completes when the async view returns. Pending tasks are cancelled as that loop is retired. Creating a task does not turn the WSGI process into a durable task service.

The fixture's pending task records startup and records its cancellation in `finally`. It has a long sleep so it remains pending when the view returns, but the test does not wait for that whole sleep. Cancellation is the behavior being observed.

## Worked case: awaited work completes before the result

The awaited route computes two values using coroutines that yield at a scheduling point. Their sum is five, and the client receives that representation. This shows correct coordination of the request's required results.

It does not prove that async is faster for this workload or that the server handles more simultaneous clients. The example is tiny and in process. Real throughput depends on the WSGI server's process/thread model, the libraries called by the handler, connection limits and the workload's I/O/CPU mix.

## Worked case: an abandoned task is cancelled

The second route starts the pending task, yields so it begins, then returns a successful response. By the time the client request finishes under the tested bridge, the event list contains both startup and cancellation. A successful HTTP response therefore did not prove that the requested background work would finish later.

A durable job needs an explicit submission/processing contract. Queues, database-backed work ledgers or an appropriate long-lived async service can provide different lifecycles, but each still needs failure, retry and idempotency design. The owned workshop demonstrates a separate worker and persistent job state; this program deliberately reports that no durable queue ran.

## Failure diagnosis

Missing emails, reports or updates after a successful request may come from work whose lifetime ended with the request. Blocking synchronous calls inside an async view can also eliminate the expected concurrency benefits. Inspect the actual adapter and library behavior rather than assuming that an async signature makes all underlying work nonblocking.

Cancellation cleanup should release resources and avoid disguising failure as completion. A `finally` block can record cleanup, but it does not retroactively make an interrupted side effect atomic. Important external effects need their own transactional or idempotent protocol.

## Interview discussion

**Can Flask async views be useful?** Yes, for appropriate awaitable work within the supported request lifecycle. Their usefulness does not imply that unawaited tasks become reliable background jobs.

**Why does a successful response not prove the background operation succeeded?** The response can be produced independently of that task's completion. The application must expose and verify the relevant job state if later completion matters.

## Next step

Combine routing, authentication, CSRF and storage in one finite application investigation before moving to an actual long-running workshop deployment.
