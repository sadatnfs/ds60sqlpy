"""Complete finite FastAPI investigation with original bounded fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Annotated


def run_cases():
    from fastapi import FastAPI, File, HTTPException, UploadFile
    from fastapi.responses import FileResponse, StreamingResponse
    from fastapi.testclient import TestClient

    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "report.txt"
        path.write_bytes(b"alpha\nbeta\n")
        app = FastAPI(docs_url=None, redoc_url=None)

        @app.post("/upload")
        async def upload(file: Annotated[UploadFile, File()]):
            try:
                body = await file.read(17)
                if len(body) > 16:
                    raise HTTPException(413, "Fixture accepts at most 16 bytes")
                try:
                    text = body.decode("utf-8")
                except UnicodeDecodeError as error:
                    raise HTTPException(422, "Expected UTF-8 text") from error
                return {"characters": len(text), "stored_client_path": False}
            finally:
                await file.close()

        @app.get("/report")
        def report():
            return FileResponse(path, filename="report.txt", media_type="text/plain")

        @app.get("/rows")
        def rows():
            return StreamingResponse(
                iter([b"id,value\n", b"1,3\n", b"2,5\n"]), media_type="text/csv"
            )

        with TestClient(app) as client:
            assert (
                client.post(
                    "/upload", files={"file": ("../../outside.txt", b"hello", "text/plain")}
                ).json()["characters"]
                == 5
            )
            assert client.post("/upload", files={"file": ("large", b"x" * 17)}).status_code == 413
            assert client.post("/upload", files={"file": ("binary", b"\xff")}).status_code == 422
            partial = client.get("/report", headers={"Range": "bytes=0-4"})
            assert partial.status_code == 206 and partial.content == b"alpha"
            assert client.get("/report", headers={"Range": "bytes=100-200"}).status_code == 416
            assert client.get("/rows").content == b"id,value\n1,3\n2,5\n"
    return {
        "range": [206, 416],
        "upload_content_bounds": True,
        "stream_content_checked": True,
        "wire_backpressure_not_tested": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
