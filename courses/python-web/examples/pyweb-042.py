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
