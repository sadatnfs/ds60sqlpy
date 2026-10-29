"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    import tempfile
    from pathlib import Path

    from flask import Flask, abort, send_file

    with tempfile.TemporaryDirectory(prefix="pyweb-download-") as temporary:
        parent = Path(temporary).resolve()
        directory = parent / "uploads"
        directory.mkdir()
        (directory / "report.txt").write_text("owned report", encoding="utf-8")
        (parent / "private.txt").write_text("outside the allowed download root", encoding="utf-8")
        (directory / "linked.txt").symlink_to(parent / "private.txt")
        app = Flask(__name__)

        @app.get("/files/<path:name>")
        def download(name):
            try:
                target = (directory / name).resolve(strict=True)
            except (OSError, ValueError):
                abort(404)
            if not target.is_relative_to(directory) or not target.is_file():
                abort(404)
            return send_file(target, as_attachment=True, download_name=target.name)

        with app.test_client() as client:
            response = client.get("/files/report.txt")
            assert response.status_code == 200 and response.data == b"owned report"
            assert "attachment" in response.headers["Content-Disposition"]
            escaped = client.get("/files/../private.txt")
            linked = client.get("/files/linked.txt")
            assert escaped.status_code == linked.status_code == 404
            response.close()
            escaped.close()
            linked.close()
        return {
            "owned_file_read": True,
            "parent_traversal_rejected": True,
            "outside_symlink_rejected": True,
            "filesystem_assumption": (
                "directory is owned by this fixture; concurrent hostile mutation is separate"
            ),
        }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
