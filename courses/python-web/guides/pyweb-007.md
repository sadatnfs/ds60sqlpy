# pyweb-007: Forms, multipart data and upload limits

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-006`, `python-08`.

## Starting point and result

HTML forms and file uploads use representations different from JSON. A form can submit repeated fields, and a multipart request can combine text fields with uploaded byte streams. This chapter parses both through a real Flask client, validates a small CSV contract and observes an actual request-size refusal.

## Mechanism: names and declared types remain client input

`request.form` is a multidict of parsed text fields. `request.files` contains uploaded-file objects. The upload's filename and content type are supplied by the client; neither proves what the bytes contain or where they belong on disk. The example reads UTF-8 CSV and requires exactly one column named `value`, then converts every value to an integer.

`MAX_CONTENT_LENGTH` supplies an application-level request-body limit. That limit includes multipart overhead, not just the nominal file payload. A real deployment also needs compatible server/proxy limits, disk quotas and streaming behavior. This finite client test establishes the framework's response for its constructed requests, not every possible network transfer or decompression scenario.

The filename is passed through Werkzeug's `secure_filename` only for a returned display/storage candidate. The program saves no file. A real storage implementation still needs an owned directory, collision policy, authorization and safe readback. Filename cleanup does not validate file content, and a cleaned name can be empty.

## Worked case: repeated form fields retain their meaning

The form contains a name and two values under `tag`. The endpoint uses `getlist`, so both tags survive parsing. This is the same multiplicity issue encountered in query strings, now expressed in a form body. Converting too early to an ordinary single-value dictionary would lose information.

The client constructs the encoded form for the program. That is useful for testing application behavior, but it does not prove that a particular browser form has correct labels, controls or submission behavior. Those are separate browser/accessibility checks in the owned application project.

## Worked case: valid CSV and an oversized upload

A small file contains the header `value` and values two and three. Its submitted filename includes `../`. The handler returns the cleaned name `report.csv`, two rows and a sum of five. The assertion checks the data contract as well as the filename transformation.

The second request contains a payload larger than the configured request limit. Flask returns 413. The program does not persist a partial file or report a successful upload. Other invalid cases, such as undecodable bytes or the wrong column name, have an explicit controlled 400 path in the handler.

A CSV parser is more reliable than splitting lines and commas manually because quoting and record boundaries have defined rules. Even so, a real import pipeline needs additional limits on rows, columns and field lengths. This example's tiny body bound makes its work small; it is not a universal safe-import implementation for arbitrary archives or spreadsheets.

## Failure diagnosis

If a handler cannot find a file, inspect the multipart field name and encoding before changing filesystem permissions. If a request is rejected before the handler runs, inspect body limits and multipart overhead. If a valid-looking filename causes a collision, the storage design needs a generated identity or another explicit policy rather than overwriting an existing user's file.

Do not use uploaded extensions as the sole content check. A file named `.csv` can contain unrelated bytes, and an image can have metadata or dimensions that exceed a downstream budget. Match validation to the operation you actually intend to perform.

## Interview discussion

**Does `secure_filename` make an upload safe?** It helps construct a conservative filename. Content validation, storage ownership, authorization and resource limits remain separate responsibilities.

**Why test both content and request size?** They fail at different boundaries. A structurally invalid small file and a body that exceeds the transport budget need predictable handling without accidental partial success.

## Next step

Inspect how a client retains cookies between requests and how the server decides whether a signed session value is trustworthy.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    import csv
    import io

    from flask import Flask, request
    from werkzeug.utils import secure_filename

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 1024

    @app.post("/form")
    def form():
        return {"name": request.form.get("name"), "tags": request.form.getlist("tag")}

    @app.post("/upload")
    def upload():
        uploaded = request.files.get("file")
        if uploaded is None:
            return {"error": "file required"}, 400
        try:
            reader = csv.DictReader(io.StringIO(uploaded.read().decode("utf-8")))
            if reader.fieldnames != ["value"]:
                raise ValueError("expected value column")
            values = [int(row["value"]) for row in reader]
        except (UnicodeError, ValueError, KeyError):
            return {"error": "invalid CSV contract"}, 400
        return {
            "safe_name": secure_filename(uploaded.filename or "data.csv"),
            "rows": len(values),
            "sum": sum(values),
        }

    with app.test_client() as client:
        form_result = client.post("/form", data={"name": "Ada", "tag": ["one", "two"]})
        assert form_result.json == {"name": "Ada", "tags": ["one", "two"]}
        valid = client.post(
            "/upload", data={"file": (io.BytesIO(b"value\n2\n3\n"), "../report.csv")}
        )
        assert valid.json == {"safe_name": "report.csv", "rows": 2, "sum": 5}
        too_large = client.post("/upload", data={"file": (io.BytesIO(b"x" * 2048), "large.csv")})
        assert too_large.status_code == 413
    return {
        "form": form_result.json,
        "validated_upload": valid.json,
        "oversized_status": 413,
        "files_persisted": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
