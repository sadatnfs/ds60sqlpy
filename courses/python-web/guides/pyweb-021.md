# pyweb-021: Flask uploads, downloads and path boundaries

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-020`.

## Starting point and result

A download endpoint must select files within its intended storage boundary. This chapter creates an owned temporary download directory and a separate synthetic file outside it. It verifies a valid download, a parent-directory traversal attempt and an outside-pointing symbolic link without touching any real private user file.

## Mechanism: compare canonical paths against a canonical root

The trusted parent directory is resolved first. The handler resolves the requested candidate and requires it to remain relative to the owned download directory before calling `send_file`. It also requires an ordinary file. This separates the URL input from the final filesystem object the application intends to serve.

Resolving only the candidate is insufficient when the configured root itself has a filesystem alias. The host test exposed exactly that issue on macOS: a temporary path under `/var` resolved through `/private/var`, so an otherwise valid file appeared outside an unresolved root. Resolving the trusted root repaired the comparison without allowing traversal or outside links.

The fixture owns the directory and its contents. A hostile actor able to mutate filesystem links concurrently introduces a separate time-of-check/time-of-use problem. A production storage design should control directory ownership and may use stronger descriptor-based or object-storage interfaces when that threat applies.

## Worked case: an owned file downloads correctly

The handler serves `report.txt` with the expected bytes and an attachment disposition. The test checks both the content and the response header, then closes the response so the underlying file handle is released before temporary storage is removed.

A returned path string is not enough evidence that the intended file was served. File responses can be lazy, conditional or streamed. Reading the bounded fixture response and closing it tests the relevant application behavior without leaving a handle open.

The example uses a filename route to make the boundary visible. A larger application may expose opaque file IDs and look up a server-owned storage key instead, which can simplify authorization and avoid accepting path-like input at all.

## Worked case: traversal and an outside link are refused

The request for `../private.txt` resolves outside the allowed directory and receives 404. A file inside the allowed directory that is a symbolic link to that same outside target is also refused. Both cases exercise actual path resolution, rather than simply checking whether the submitted text contains a suspicious substring.

A normalized path containing an earlier `..` segment can still end inside the allowed root; the application's contract should define whether that syntax is allowed. Here the decisive boundary is the resolved file location. It is not a general claim that every dot-containing path string is rejected.

## Failure diagnosis

If a valid file receives 404, compare canonical root and candidate paths, including platform aliases and symlinks. If a traversal succeeds, inspect whether the code compared only string prefixes or joined an absolute path that discarded the intended root. String prefix checks can confuse sibling names such as `uploads` and `uploads-old`.

Uploaded filenames also need collision, authorization and content policies. A safe download path does not establish that the uploaded bytes are suitable for a later parser or that the caller owns the file. Keep those responsibilities visible in the application design.

## Interview discussion

**Why use path-relative containment instead of string startswith?** Filesystem path components have semantics that string prefixes do not capture. Canonical paths and component-aware containment make the intended boundary clearer.

**Does this example solve hostile concurrent filesystem mutation?** Its directory is controlled by the fixture. Stronger adversarial filesystem scenarios require an additional ownership and atomic-access design, which must be tested separately.

## Next step

Add representation validators and cache policy. Correct file/resource selection still needs a deliberate decision about when clients may reuse a previous response.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
