"""Actual local ASGI request contracts; no network server is started."""

import hashlib
import json
from threading import RLock

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field


class Delivery(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    delivery_id: str = Field(min_length=1, max_length=32, pattern=r".*\S.*")
    packages: int = Field(ge=1, le=100_000)


def application():
    app = FastAPI(docs_url=None, redoc_url=None)
    lock = RLock()
    state = {
        "rows": {
            key: {"delivery_id": key, "packages": value}
            for key, value in [("A", 2), ("B", 3), ("C", 1)]
        },
        "snapshots": {},
        "next_snapshot": 0,
        "receipts": {},
    }

    def current_rows():
        with lock:
            return [dict(state["rows"][key]) for key in sorted(state["rows"])]

    @app.get("/unsafe-pages")
    def unsafe_pages(offset: int = Query(0, ge=0)):
        with lock:
            return {"items": current_rows()[offset : offset + 2]}

    @app.get("/deliveries")
    def pages(cursor: str | None = None):
        with lock:
            if cursor is None:
                state["next_snapshot"] += 1
                snapshot = "s" + str(state["next_snapshot"])
                state["snapshots"][snapshot] = current_rows()
                if len(state["snapshots"]) > 4:
                    del state["snapshots"][next(iter(state["snapshots"]))]
                offset = 0
            else:
                try:
                    snapshot, raw_offset = cursor.split(":")
                    offset = int(raw_offset)
                    if offset < 0:
                        raise ValueError("Negative offset")
                except ValueError:
                    raise HTTPException(400, "Malformed cursor") from None
            if snapshot not in state["snapshots"]:
                raise HTTPException(410, "Snapshot expired or unknown")
            rows = state["snapshots"][snapshot]
            if offset > len(rows):
                raise HTTPException(400, "Cursor offset is outside its snapshot")
            next_offset = offset + 2
            next_cursor = f"{snapshot}:{next_offset}" if next_offset < len(rows) else None
            return {
                "items": rows[offset:next_offset],
                "next_cursor": next_cursor,
                "snapshot": snapshot,
            }

    @app.post("/deliveries")
    def create(record: Delivery, idempotency_key: str = Header(min_length=1, max_length=64)):
        with lock:
            document = record.model_dump()
            identity = hashlib.sha256(json.dumps(document, sort_keys=True).encode()).hexdigest()
            prior = state["receipts"].get(idempotency_key)
            if prior is not None:
                if prior["identity"] != identity:
                    raise HTTPException(409, "Idempotency key reused with different content")
                return JSONResponse(
                    {"delivery": prior["delivery"], "replayed": True}, status_code=200
                )
            if record.delivery_id in state["rows"]:
                raise HTTPException(409, "Delivery already exists")
            state["rows"][record.delivery_id] = document
            state["receipts"][idempotency_key] = {"identity": identity, "delivery": document}
            return JSONResponse({"delivery": document, "replayed": False}, status_code=201)

    return app, state


def identities(response):
    assert response.status_code == 200
    return [row["delivery_id"] for row in response.json()["items"]]


def example_one():
    app, _ = application()
    with TestClient(app) as client:
        unsafe_first = identities(client.get("/unsafe-pages?offset=0"))
        first = client.get("/deliveries")
        stable_first = identities(first)
        created = client.post(
            "/deliveries",
            json={"delivery_id": "0", "packages": 1},
            headers={"Idempotency-Key": "insert-0"},
        )
        assert created.status_code == 201
        unsafe_second = identities(client.get("/unsafe-pages?offset=2"))
        second = client.get("/deliveries", params={"cursor": first.json()["next_cursor"]})
        stable = stable_first + identities(second)
        assert stable == ["A", "B", "C"] and second.json()["next_cursor"] is None
        assert unsafe_first + unsafe_second == ["A", "B", "B", "C"]
        assert identities(client.get("/deliveries")) == ["0", "A"]
        return {
            "stable_start_population": stable,
            "unsafe_offset_result": unsafe_first + unsafe_second,
            "new_record_belongs_to_a_new_snapshot": "0",
        }


def example_two():
    app, state = application()
    with TestClient(app) as client:
        payload = {"delivery_id": "D", "packages": 4}
        headers = {"Idempotency-Key": "request-D"}
        # Discard a successful application response to model an unknown client outcome.
        client.post("/deliveries", json=payload, headers=headers)
        replay = client.post("/deliveries", json=payload, headers=headers)
        conflict = client.post(
            "/deliveries", json={"delivery_id": "D", "packages": 9}, headers=headers
        )
        assert replay.status_code == 200 and replay.json()["replayed"] is True
        assert replay.json()["delivery"] == payload and conflict.status_code == 409
        assert len(state["rows"]) == 4 and state["rows"]["D"]["packages"] == 4
        assert client.get("/deliveries?cursor=unknown:0").status_code == 410
        assert client.post("/deliveries", json=payload).status_code == 422
        return {
            "replayed_status": replay.status_code,
            "conflict_status": conflict.status_code,
            "one_created_delivery": state["rows"]["D"],
            "network_failure_was_modeled_not_executed": True,
        }


def main():
    print("Pagination under a changed population:", example_one())
    print("Retry identity at the actual application boundary:", example_two())


if __name__ == "__main__":
    main()
