# pyweb-041: WebSocket messages, validation and close behavior

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-040`.

## Starting point and result

A WebSocket begins with an HTTP handshake and then carries messages over a longer-lived connection. Authentication, origin checks, message schemas, size limits and close behavior all remain application responsibilities. This chapter exercises a finite one-message exchange through the real framework WebSocket interface.

## Key terms

- **WebSocket handshake:** The initial HTTP exchange that the server accepts or refuses before any messages flow over the long-lived connection.
- **Origin check:** Comparing the handshake's Origin header with an expected value, which blocks unwanted browser initiation but is not authentication.
- **Message schema:** A strict Pydantic model applied to every received message, independently of the checks made at the handshake.
- **Close code:** A numeric reason sent when closing a WebSocket: 1000 for normal completion, 1008 for a policy violation and 1009 for a message too big.

## Mechanism: handshake and message validation are separate

The handler checks a synthetic bearer credential and an expected Origin before accepting the connection. Origin is useful against unwanted browser initiation, but a nonbrowser client can supply arbitrary headers, so it is not a replacement for authentication. Real browser WebSocket clients also have different header-setting capabilities from this test fixture.

After acceptance, the handler receives text and applies a byte bound before parsing a strict Pydantic message. The schema requires a positive integer sequence and a bounded nonempty text field, rejecting extra keys. A message that passes the handshake can still fail this independent data boundary.

The example handles one message and then closes deliberately. Normal completion uses 1000. A policy or validation refusal uses 1008; oversized text uses 1009. Finally-based cleanup records that the handler released its owned context even when message handling ends early.

## Worked case: validate, respond and close normally

The client supplies the expected handshake headers and sends a valid JSON message. The server returns the same sequence with an uppercase text value, then closes with 1000. Assertions check both the response and the close frame.

This is actual ASGI WebSocket handling through TestClient, including acceptance and close semantics. It is not a TCP socket, reverse-proxy upgrade test or browser interaction. The owned workshop uses a real server and network WebSocket client for that additional evidence.

A sequence field can help applications identify messages, but this fixture does not implement durable replay or exactly-once processing. A real collaborative application needs to define ordering, acknowledgements and recovery when the connection drops after an effect but before its response.

## Worked case: reject malformed data and missing authority

A numeric string where the schema requires a strict integer is rejected after the handshake with 1008. A connection without the required authority is refused before successful acceptance. The program checks the disconnect code and the number of handler-cleanup observations.

These cases prevent two common shortcuts: validating only the initial connection and assuming every later message is safe, or accepting first and checking identity only after sending sensitive state. The correct ordering depends on the protocol, but it must be deliberate and tested.

Large-message protection has multiple layers. The application bound controls the text it processes after receipt; the server's protocol configuration should also limit frames/messages and connection resources. One in-handler check should not be presented as complete network resource protection.

## Worked example: a receive loop that ends on disconnect

```python
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

log = []


async def echo(websocket):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            await websocket.send_text(text[::-1])
    except WebSocketDisconnect as exc:
        log.append(f"client left with {exc.code}")
    finally:
        log.append("subscriptions released")


app = Starlette(routes=[WebSocketRoute("/echo", echo)])
with TestClient(app) as client:
    with client.websocket_connect("/echo") as ws:
        for word in ("ping", "socket"):
            ws.send_text(word)
            print(ws.receive_text())
        ws.close(code=1001)
print(log)
```

Expected output:

```text
gnip
tekcos
['client left with 1001', 'subscriptions released']
```

The lesson's handler reads one message and closes, while most real sockets run a loop like this one until the client leaves. There is no special return value for a closed connection: `receive_text` raises `WebSocketDisconnect`, carrying the close code the client sent, here 1001 for going away. Catching that exception is the normal exit path, not an error, and the `finally` block is where per connection state such as chat room membership or a subscription to a message broker must be released. A handler that forgets this leaks one subscription for every closed browser tab, and the leak grows quietly until memory or broker limits run out.

## Failure diagnosis and discussion

**Why can HTTP endpoints work while WebSockets fail behind a proxy?** The upgrade, timeout and forwarding configuration may differ. A successful ordinary GET does not establish the WebSocket path.

**Does a close code prove cleanup of every external operation?** No. The handler must still cancel and await owned tasks, return pooled resources and reconcile any durable effects. The fixture records only its explicitly owned cleanup.

If a client hangs waiting for another message, inspect the agreed finite protocol and close behavior. If reconnecting duplicates an action, inspect operation identities rather than merely increasing connection timeouts. Continue with SSE for a simpler server-to-client event stream and explicit resume cursor semantics.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, ConfigDict, Field, ValidationError

    class Message(BaseModel):
        model_config = ConfigDict(extra="forbid", strict=True)
        sequence: int = Field(ge=1)
        text: str = Field(min_length=1, max_length=40)

    app = FastAPI(docs_url=None, redoc_url=None)
    completed = []

    @app.websocket("/socket")
    async def socket(websocket: WebSocket):
        if (
            websocket.headers.get("origin") != "https://ui.example"
            or websocket.headers.get("authorization") != "Bearer fixture"
        ):
            await websocket.close(code=1008)
            return
        await websocket.accept()
        try:
            raw = await websocket.receive_text()
            if len(raw.encode()) > 200:
                await websocket.close(code=1009)
                return
            try:
                message = Message.model_validate_json(raw)
            except ValidationError:
                await websocket.close(code=1008)
                return
            await websocket.send_json({"sequence": message.sequence, "text": message.text.upper()})
            await websocket.close(code=1000)
        except WebSocketDisconnect:
            completed.append("client-disconnected")
        finally:
            completed.append("handler-cleaned")

    headers = {"Origin": "https://ui.example", "Authorization": "Bearer fixture"}
    with TestClient(app) as client:
        with client.websocket_connect("/socket", headers=headers) as ws:
            ws.send_json({"sequence": 1, "text": "hello"})
            assert ws.receive_json() == {"sequence": 1, "text": "HELLO"}
            assert ws.receive()["code"] == 1000
        with client.websocket_connect("/socket", headers=headers) as ws:
            ws.send_json({"sequence": "1", "text": "hello"})
            assert ws.receive()["code"] == 1008
        try:
            with client.websocket_connect("/socket"):
                raise AssertionError("Unauthenticated socket accepted")
        except WebSocketDisconnect as error:
            assert error.code == 1008
    assert completed.count("handler-cleaned") == 2
    return {
        "success_close": 1000,
        "invalid_close": 1008,
        "cleanup": completed,
        "scope": "in-process WebSocket protocol",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
