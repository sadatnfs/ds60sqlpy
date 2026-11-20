"""Every pinned build or preparation download retries brief throttling before failing."""

from __future__ import annotations

import ast
import io
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADERS = (
    "docker/workers/fetch_pinned.py",
    "docker/workers/native/install_native.py",
    "docker/kubernetes/download_kubectl.py",
    "docker/formatting/install-downloads.py",
    "scripts/prepare_kubernetes.py",
    "courses/apache-data-platforms/projects/ballista/install.py",
    "courses/apache-data-platforms/projects/cassandra/binary-image/install.py",
    "courses/apache-data-platforms/projects/flink/binary-image/install.py",
    "courses/apache-data-platforms/projects/hive/prepare_jdbc.py",
    "courses/apache-data-platforms/projects/pinot/binary-image/install.py",
    "courses/apache-data-platforms/projects/streaming/binary-image/install.py",
    "courses/tmb-modeling/projects/tmb-local/prepare_dependencies.py",
    "examples/native-ad-core/prepare_sdk.py",
    "packages/spark-tmbad/tooling/prepare.py",
)


def load_helper(relative: str) -> Any:
    """Compile only the file's helper, so loading it never starts a download."""
    tree = ast.parse((ROOT / relative).read_text(), relative)
    helpers = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "open_download"
    ]
    assert len(helpers) == 1, relative
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and "urlopen" in (getattr(node.func, "attr", None), getattr(node.func, "id", None))
    ]
    # The helper's own call is the only direct, single-attempt open in the file.
    assert [call.lineno for call in calls] == [
        node.lineno
        for node in ast.walk(helpers[0])
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "urlopen"
    ], relative
    namespace: dict[str, Any] = {}
    exec("import sys, time, urllib.error, urllib.request\nfrom typing import Any", namespace)
    body: list[ast.stmt] = [helpers[0]]
    exec(compile(ast.Module(body=body, type_ignores=[]), relative, "exec"), namespace)
    return namespace["open_download"]


def http_error(code: int, retry_after: str | None = None) -> urllib.error.HTTPError:
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    return urllib.error.HTTPError(
        "https://downloads.invalid/pinned", code, "busy", headers, io.BytesIO()
    )


@pytest.mark.parametrize("relative", DOWNLOADERS)
def test_pinned_download_waits_out_throttling_and_gateway_errors(
    relative: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = load_helper(relative)
    sleeps: list[float] = []
    events: list[Any] = [http_error(429, "7"), http_error(503), "response"]

    def scripted(source: Any, timeout: float) -> Any:
        event = events.pop(0)
        if isinstance(event, Exception):
            raise event
        return event

    monkeypatch.setattr(urllib.request, "urlopen", scripted)
    monkeypatch.setattr("time.sleep", sleeps.append)
    assert helper("https://downloads.invalid/pinned", 30) == "response"
    assert sleeps == [7.0, 4.0]


@pytest.mark.parametrize("relative", DOWNLOADERS)
def test_pinned_download_fails_fast_when_missing_and_stops_after_bounded_retries(
    relative: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = load_helper(relative)
    sleeps: list[float] = []
    monkeypatch.setattr("time.sleep", sleeps.append)
    for code, retry_after, waits in ((404, None, []), (429, "999999", [60.0] * 4)):
        sleeps.clear()

        def failing(source: Any, timeout: float, code: int = code, value: Any = retry_after) -> Any:
            raise http_error(code, value)

        monkeypatch.setattr(urllib.request, "urlopen", failing)
        with pytest.raises(urllib.error.HTTPError) as raised:
            helper("https://downloads.invalid/pinned", 30)
        assert raised.value.code == code and sleeps == waits
