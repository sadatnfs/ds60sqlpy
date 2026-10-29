## Starting point and result

A streaming generator can be correct while a client, server or proxy buffers its output. This chapter moves from in-process clients to the owned Docker web lab and uses an explicit ordering condition to test actual SSE delivery. It also compares the lifetime of a connection with the lifetime of a durable job.

## Mechanism: transport and work have different owners

The FastAPI service accepts a bounded calculation into PostgreSQL. A separate worker changes the job's state and commits event rows. The HTTP connection reads those events and formats SSE frames. Disconnecting that reader does not remove the database job or transfer ownership of the calculation back to the browser.

The test creates a held job that cannot finish until a separate release request arrives. It opens the SSE stream and waits for an actual queued or running event over the socket. Only after that event is received does the test send release. This proves a meaningful delivery order without relying on a fragile claim such as every chunk arrives within a particular number of milliseconds.

The service bounds each SSE connection and checks for disconnect. EventSource can reconnect while the user leaves streaming enabled. Event identities belong to persistent database rows, and a resume cursor must belong to the selected job. The example does not claim unlimited retention, a multi-host event bus or exactly-once client delivery.

## Worked case: receive bytes before allowing completion

Prepare and start the owned project using its README, then run workshop check. The check logs in through actual HTTP, creates a held job and opens its event stream. It receives an event while the stored released flag is still false. The worker therefore cannot have completed the calculation before that observation.

This distinguishes a real streaming path from a buffered response returned only after all work finishes. A client that waits for end-of-response would deadlock or time out against this controlled protocol instead of falsely passing a timing assertion.

The same acceptance runs a finite authenticated WebSocket echo against Uvicorn. It checks the returned message and closes the connection. That establishes the local handshake/message path; it does not establish an external reverse proxy, TLS termination or a browser's complete connection policy.

## Worked case: disconnect, resume and observe the stored result

After the first event, the test closes the SSE connection, releases the job and reconnects with Last-Event-ID. Returned events must have later identities. The final event reports the expected sum 10, and the database-backed job endpoint confirms the completed result.

A cursor that does not belong to the job is refused. This prevents a client from silently applying a global counter from another stream and missing its own history. A production service also needs an explicit policy for expired history, snapshots and client deduplication.

The browser offers separate Disconnect and Reconnect controls. Disconnect closes only the reader. It does not cancel the durable job. A product that supports job cancellation would need its own authenticated command and worker-state transition, not an assumption that closing a tab reverses work.

## Failure diagnosis and discussion

**Why can TestClient content checks pass while live streaming fails?** They can validate the final concatenated bytes without observing incremental network delivery. The held-job protocol tests ordering at the socket boundary.

**What is backpressure?** A slow consumer limits how quickly data can be transmitted or buffered. A complete design bounds buffers and production rate rather than accumulating unbounded events in application memory.

If events arrive only at completion, inspect buffering along the actual serving path. If reconnects lose state, inspect durable identities and cursor policy. If disconnected clients leave tasks alive, inspect connection-owned cleanup. Keep the exported source-bound service receipt separate from browser and deployment observations, then continue with threat modeling and container recovery.
