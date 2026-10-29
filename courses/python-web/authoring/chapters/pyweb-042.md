## Starting point and result

Server-sent events carry server-to-client updates over an HTTP response. They are useful when the browser sends ordinary requests but receives a continuing stream of progress or notifications. This chapter builds valid finite event framing and an explicit resume cursor, while keeping delivery timing claims separate.

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

## Failure diagnosis and discussion

**Why use SSE instead of WebSockets?** SSE fits one-way server updates over HTTP and browser EventSource semantics. Bidirectional interactive protocols may need WebSockets. Choose according to data flow and operational requirements, not novelty.

**Why can a correct generator appear nonstreaming?** A client, server or proxy can buffer output. Test the actual wire path and a controlled ordering condition rather than relying on generator syntax.

If reconnects lose events, inspect identity persistence, retention and cursor interpretation. If duplicate updates appear, inspect client idempotency. Continue with OpenAPI and compatibility, which document the ordinary request surfaces surrounding these streaming routes.
