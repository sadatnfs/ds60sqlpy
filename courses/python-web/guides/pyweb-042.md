# pyweb-042: Server-sent events and resumable event identities

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-041`.

## Starting point and result

Server-sent events carry server-to-client updates over an HTTP response. They are useful when the browser sends ordinary requests but receives a continuing stream of progress or notifications. This chapter builds valid finite event framing and an explicit resume cursor, while keeping delivery timing claims separate.

## Key terms

- **Server-sent events:** A one-way stream of server-to-client events carried over one long HTTP response with the `text/event-stream` media type.
- **Event frame:** One SSE event: lines of fields such as `id`, `event` and `data`, ended by a blank line.
- **Last-Event-ID:** The request header a reconnecting client sends with the last event id it received, so the server can resume after that point.
- **Resume cursor:** The ordered event identity used to choose which later events to resend; a malformed cursor returns 400 and an unknown future one returns 409.

## Mechanism: event identity is more than a line number

An SSE event consists of named fields followed by a blank line. The data field carries text; this example encodes a JSON object on one data line. An id field gives the client a cursor it can send as Last-Event-ID when reconnecting. The event field names the application event type.

JSON encoding escapes embedded newlines inside a value, so a multiline string does not accidentally split the SSE frame. Directly interpolating arbitrary text into protocol fields can corrupt framing or introduce unintended fields. Validate identifiers and encode payloads through the chosen serialization format.

The fixture has three durable-looking identities in a bounded in-memory list. Their ordering defines the resume rule: return events whose identity is greater than the supplied cursor. In a real service, identity and retention must belong to persistent event storage. A new process-local counter that restarts at one would not safely resume an older client's stream.

## Worked case: read the complete stream

The first request receives queued, running and finished events. The program counts the event frames and checks the response's event-stream representation. The final payload contains a newline inside a JSON string, which remains part of the decoded value rather than becoming a new protocol field.

The complete content is verified after TestClient handles the response. That proves framing and payload semantics, not incremental network delivery. A buffered test client can return all events together even when the server uses a generator. The network workshop includes a controlled event/release handshake to demonstrate actual delivery before the producer finishes.

Cache-Control and buffering hints communicate intent to clients and intermediaries. They do not guarantee that every reverse proxy is configured correctly. Actual deployment tests must inspect the full serving path.

## Worked case: resume and reject an impossible cursor

A request with Last-Event-ID 2 receives only event 3. A malformed cursor receives 400. A cursor ahead of the stream's known final identity receives 409 instead of silently returning an apparently complete empty history.

The ahead-of-stream check is one explicit fixture policy. A larger service also needs a policy for a cursor older than retained history, perhaps returning a reset/snapshot instruction. Silent truncation would make a reconnecting client believe it had seen all relevant changes when it had not.

Repeated delivery remains possible around reconnects. Clients should apply events idempotently or track the latest accepted identity. The stream's event ID and the business operation's idempotency key are related coordination tools, but they identify different things and should not be conflated.

## Worked example: why event data with a newline needs encoding

```python
import json


def frame(identifier, text):
    return f"id: {identifier}\ndata: {text}\n\n"


def parse(stream):
    events = []
    for block in stream.strip("\n").split("\n\n"):
        fields = {}
        for line in block.split("\n"):
            name, _, value = line.partition(": ")
            fields.setdefault(name, []).append(value)
        events.append((fields["id"][0], "\n".join(fields.get("data", []))))
    return events


raw = frame(3, "line one\nline two")
encoded = frame(3, json.dumps("line one\nline two"))
print(parse(raw))
print(parse(encoded))
print(repr(json.loads(parse(encoded)[0][1])))
```

Expected output:

```text
[('3', 'line one')]
[('3', '"line one\\nline two"')]
'line one\nline two'
```

In the event stream format a newline ends a field, so writing raw text that contains one after `data:` produced a second line, `line two`, that the parser read as a field with an unknown name and discarded. The client silently lost half the message. Passing the value through `json.dumps` first turns the newline into the two characters backslash and n, keeping the whole value on one `data:` line, and `json.loads` restores it on the receiving side. The lesson's `encode` generator applies the same rule to every event it yields.

## Failure diagnosis and discussion

**Why use SSE instead of WebSockets?** SSE fits one-way server updates over HTTP and browser EventSource semantics. Bidirectional interactive protocols may need WebSockets. Choose according to data flow and operational requirements, not novelty.

**Why can a correct generator appear nonstreaming?** A client, server or proxy can buffer output. Test the actual wire path and a controlled ordering condition rather than relying on generator syntax.

If reconnects lose events, inspect identity persistence, retention and cursor interpretation. If duplicate updates appear, inspect client idempotency. Continue with OpenAPI and compatibility, which document the ordinary request surfaces surrounding these streaming routes.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json
from typing import Annotated


def run_cases():
    from fastapi import FastAPI, Header, HTTPException
    from fastapi.responses import StreamingResponse
    from fastapi.testclient import TestClient

    app = FastAPI(docs_url=None, redoc_url=None)
    events = [
        (1, {"state": "queued"}),
        (2, {"state": "running"}),
        (3, {"state": "finished", "value": "line one\nline two"}),
    ]

    @app.get("/events")
    def stream(last_event_id: Annotated[str | None, Header()] = None):
        if last_event_id is not None and (
            not last_event_id.isascii() or not last_event_id.isdecimal() or len(last_event_id) > 6
        ):
            raise HTTPException(400, "Invalid event identity")
        after = int(last_event_id or 0)
        if after > events[-1][0]:
            raise HTTPException(409, "Event cursor is ahead of this stream")

        def encode():
            for identifier, value in events:
                if identifier > after:
                    yield f"id: {identifier}\nevent: progress\ndata: {json.dumps(value)}\n\n"

        return StreamingResponse(
            encode(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    with TestClient(app) as client:
        full = client.get("/events")
        resumed = client.get("/events", headers={"Last-Event-ID": "2"})
        assert full.text.count("event: progress") == 3
        assert resumed.text.count("event: progress") == 1 and "id: 3" in resumed.text
        data_line = next(line for line in resumed.text.splitlines() if line.startswith("data: "))
        assert json.loads(data_line[6:])["value"] == "line one\nline two"
        assert client.get("/events", headers={"Last-Event-ID": "no"}).status_code == 400
        assert client.get("/events", headers={"Last-Event-ID": "4"}).status_code == 409
    return {
        "full_events": 3,
        "resumed_events": 1,
        "scope": "finite framing and cursor semantics; not network latency",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
