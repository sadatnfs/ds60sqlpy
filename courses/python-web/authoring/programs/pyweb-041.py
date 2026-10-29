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
