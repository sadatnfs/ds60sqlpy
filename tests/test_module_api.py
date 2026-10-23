from __future__ import annotations

import json
import threading
from dataclasses import replace
from http.client import HTTPConnection
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lab import LabServer


def test_module_api_has_its_own_bounded_body_and_retains_authentication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Catalog.load()
    catalog = Catalog(tmp_path, (replace(root.get("python-01"), prerequisites=()),))
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})

    class Service:
        def __init__(self, catalog: Any, directory: Any) -> None:
            pass

        def action(self, payload: dict[str, Any]) -> dict[str, Any]:
            fields = payload.get("fields", {})
            return {"length": len(fields.get("source", "")), "action": payload["action"]}

        def close(self) -> None:
            pass

    monkeypatch.setattr("ds60sqlpy.lab.ModuleService", Service)
    server = LabServer(catalog, progress_path=tmp_path / "progress.json")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = server.url.rstrip("/")
        headers = {"Content-Type": "application/json", "Origin": url, "X-DS60-Token": server.token}
        payload = {
            "action": "module-save",
            "lesson_id": "cpp-009",
            "fields": {
                "source": "\n" * 48000,
                "prediction": "x" * 12000,
                "explanation": "y" * 12000,
            },
        }
        encoded = json.dumps(payload).encode()
        assert 64 * 1024 < len(encoded) < 512 * 1024
        with urlopen(
            Request(url + "/api/modules", data=encoded, headers=headers), timeout=5
        ) as response:
            assert json.load(response)["length"] == 48000
        with pytest.raises(HTTPError) as legacy:
            urlopen(Request(url + "/api/lab", data=encoded, headers=headers), timeout=5)
        assert legacy.value.code == 400
        with pytest.raises(HTTPError) as unauthenticated:
            urlopen(
                Request(
                    url + "/api/modules",
                    data=b"{}",
                    headers={"Content-Type": "application/json", "Origin": url},
                ),
                timeout=5,
            )
        assert unauthenticated.value.code == 403
        with pytest.raises(HTTPError) as wrong_origin:
            urlopen(
                Request(
                    url + "/api/modules",
                    data=b"{}",
                    headers={**headers, "Origin": "https://elsewhere.example"},
                ),
                timeout=5,
            )
        assert wrong_origin.value.code == 403
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        try:
            connection.request(
                "POST", "/api/modules", headers={**headers, "Content-Length": str(512 * 1024 + 1)}
            )
            assert connection.getresponse().status == 400
        finally:
            connection.close()
        with pytest.raises(HTTPError) as other_action:
            urlopen(
                Request(url + "/api/modules", data=b'{"action":"paths"}', headers=headers),
                timeout=5,
            )
        assert other_action.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
