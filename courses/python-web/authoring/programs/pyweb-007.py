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
