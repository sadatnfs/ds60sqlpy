# pyweb-039: FastAPI file handling and streaming responses

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-038`.

## Starting point and result

Files cross several boundaries at once: multipart parsing, memory or temporary storage, content validation, filesystem identity and response transfer. This chapter handles a small upload, a fixed server-owned download and a finite streaming response. It reports exactly which parts are tested without claiming network backpressure from a buffered client.

## Mechanism: bound content and keep path authority on the server

UploadFile exposes a file-like object whose storage may be spooled rather than kept entirely in memory. The example reads at most one byte beyond its permitted content limit, enough to distinguish an accepted small value from an oversized value without reading an arbitrarily large body into application memory. It closes the upload in a finally block.

That application read limit does not automatically bound every byte the multipart parser or upstream server may already have received. A deployed service also needs request-body and transport limits at appropriate layers. The lesson separates these claims rather than treating one read call as complete denial-of-service protection.

The client filename is metadata, not an authorized server path. The fixture never writes to a path derived from it. Downloads use a fixed file selected by the application. FileResponse supplies response metadata and range handling, while a separate StreamingResponse demonstrates a finite sequence of CSV chunks.

## Worked case: accept text and serve a byte range

A small UTF-8 upload returns its decoded character count. Its deliberately hostile-looking filename does not influence storage because the handler does not use it as a path. The download route serves a known text file, and a Range request retrieves only the requested first bytes with 206.

Byte counts and character counts differ for non-ASCII text. Bounds applied before decoding are byte bounds; string lengths after decoding count Python characters. The fixture makes its byte cap explicit and reports characters only after successful decoding.

The partial-download assertion checks both status and content. A response that returns 206 but sends the whole file would violate the range contract. A deployed cache or proxy can introduce another layer of behavior, which requires actual network acceptance beyond this client test.

## Worked case: oversized, invalid and unsatisfiable inputs

An upload one byte over the limit receives 413. Invalid UTF-8 receives 422. A range beyond the file's length receives 416. These refusals occur without storing a client-controlled path or leaving the upload object open.

The finite CSV stream is checked for its complete expected content. TestClient may buffer that content, so this observation does not prove that a remote consumer received each chunk promptly or that a slow consumer applies backpressure correctly. The network workshop includes a separately controlled streaming test.

For large real files, also consider content type validation, antivirus or domain-specific parsing, storage quotas, atomic publication and safe cleanup after interruption. File extensions and browser-provided MIME types are hints, not trustworthy proof of content.

## Failure diagnosis and discussion

**Why read limit plus one?** Exactly the limit could also be the prefix of a larger file. Reading one extra byte provides a bounded way to detect excess content.

**Why not join an upload filename to the project directory?** Even sanitized names can collide or create ownership confusion. The server should assign storage identities and preserve original names only as validated display metadata.

If a download fails after its temporary directory closes, inspect response consumption and file lifetime. Continue with background work, where returning a response and completing an effect are also separate events.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
