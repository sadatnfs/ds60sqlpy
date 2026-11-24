# pyweb-068: Network streaming, backpressure and disconnects

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-067`.

## Starting point and result

A streaming generator can be correct while a client, server or proxy buffers its output. This chapter moves from in-process clients to the owned Docker web lab and uses an explicit ordering condition to test actual SSE delivery. It also compares the lifetime of a connection with the lifetime of a durable job.

## Key terms

- **Buffering:** Holding streamed output in a client, server or proxy before forwarding it, which can delay events even when the generator is correct.
- **Delivery-order test:** Waiting for an actual queued or running event before releasing the held job, which proves bytes arrived before completion.
- **Connection lifetime:** The span of one HTTP stream; closing it does not cancel or take ownership of the durable job it reports on.
- **Job-scoped cursor:** A resume position that refers to persistent event rows of the selected job, so reconnecting cannot read another job's events.

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

## Worked example: a bounded queue makes a fast producer wait

```python
import asyncio


async def main():
    queue = asyncio.Queue(maxsize=2)
    deepest = 0

    async def producer():
        nonlocal deepest
        for chunk in range(6):
            await queue.put(chunk)
            deepest = max(deepest, queue.qsize())
        await queue.put(None)

    async def consumer():
        received = []
        while (chunk := await queue.get()) is not None:
            received.append(chunk)
            await asyncio.sleep(0.01)
        return received

    _, received = await asyncio.gather(producer(), consumer())
    return received, deepest


print(asyncio.run(main()))
```

Expected output:

```text
([0, 1, 2, 3, 4, 5], 2)
```

The producer could generate all six chunks instantly, but `put` suspends whenever two items are waiting, so memory held between the stages never exceeds two chunks while the slow consumer catches up. That suspension is backpressure: the slowest party sets the pace. An unbounded queue would accept everything and grow with every slow client. In a streaming endpoint the consumer is the network socket, and awaiting the send or drain step plays the role of the full queue. When the client disconnects, that await is where cancellation arrives.

## Failure diagnosis and discussion

**Why can TestClient content checks pass while live streaming fails?** They can validate the final concatenated bytes without observing incremental network delivery. The held-job protocol tests ordering at the socket boundary.

**What is backpressure?** A slow consumer limits how quickly data can be transmitted or buffered. A complete design bounds buffers and production rate rather than accumulating unbounded events in application memory.

If events arrive only at completion, inspect buffering along the actual serving path. If reconnects lose state, inspect durable identities and cursor policy. If disconnected clients leave tasks alive, inspect connection-owned cleanup. Keep the exported source-bound service receipt separate from browser and deployment observations, then continue with threat modeling and container recovery.

## Worked project reference

This is a complete reading/project reference. It has no ordinary pad Run action. Prepare and execute any linked project through its own documented entrypoint. A command reference or hand calculation is not an execution receipt. Runtime: `reading`.

Read the [owned web-lab instructions](../projects/web-lab/README.md) from the course
source tree, then run its explicit lifecycle in a prepared Linux Docker engine:

```sh
cd courses/python-web/projects/web-lab
./workshop prepare
./workshop start
./workshop check
```

The actual test opens an SSE connection and receives a queued/running event while
the job is still unreleased. Only after receiving bytes does it release the job.
It disconnects, reconnects with Last-Event-ID and verifies the committed result 10.
It also performs a real one-message WebSocket exchange. Inspect the source-bound
receipt under this owned project's `.workshop/acceptance.json`.

A prepared image or this command reference is not an execution receipt. Network
acceptance is separate from browser rendering and from public TLS/proxy behavior.

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
