"""New D3, Docker and deep-networking contracts, separate from runtime acceptance."""

from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import re
import runpy
import shutil
import socket
import subprocess
import threading
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def records(subject: str) -> dict[str, dict[str, Any]]:
    return {
        row["id"]: row
        for row in json.loads((ROOT / f"courses/{subject}/lessons.json").read_text())["lessons"]
    }


@pytest.mark.parametrize(
    "subject,prefix,first,last,profile,minimum",
    [
        ("docker", "docker", 1, 42, "reading", 1100),
        ("javascript-typescript", "js", 43, 66, "javascript-browser", 1100),
        ("kubernetes", "k8s", 43, 66, "reading", 1250),
    ],
)
def test_complete_extension_bundles_preserve_honest_capabilities(
    subject: str,
    prefix: str,
    first: int,
    last: int,
    profile: str,
    minimum: int,
) -> None:
    entries = records(subject)
    for number in range(first, last + 1):
        row = entries[f"{prefix}-{number:03d}"]
        assert row["runtime_profile"] == profile and row["verification_id"] is None
        assert row["language"] == ("javascript" if profile == "javascript-browser" else "markdown")
        guide = (ROOT / row["guide_path"]).read_text()
        source = (ROOT / row["source_path"]).read_text()
        explanation = (ROOT / row["solution_paths"][-1]).read_text()
        assert len(guide.split()) >= minimum
        assert re.findall(r"^### Exercise ([1-6]):", guide, re.M) == list("123456")
        assert re.findall(r"^## Exercise ([1-6]):", explanation, re.M) == list("123456")
        assert len(re.findall(r"^### Worked example [12]:", guide, re.M)) == 2
        assert "## Ask an AI tutor about this lesson" in guide
        assert row["guide_path"] in guide and row["source_path"] in guide
        assert source != explanation
        assert "\u2014" not in guide + source + explanation
        if profile == "reading":
            assert "My prediction:" in source
            assert "no engine socket" in guide if subject == "docker" else "no API calls" in guide
        else:
            assert "Answer-free learner artifact" in source and "throw new Error" in source
            assert "not a trusted backend verifier" in guide


def test_networking_fixture_checks_are_offline_and_do_not_fabricate_acceptance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def denied(*args: object, **kwargs: object) -> None:
        raise AssertionError("Static networking fixture attempted network access")

    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    module = runpy.run_path(str(ROOT / "courses/kubernetes/fixtures/networking/check_fixtures.py"))
    result = module["check"]()
    assert result["status"] == "passed" and result["api_calls"] == 0
    assert result["ready_fixture_uids"] == ["pod-a"]
    assert result["manifest_documents"] == 8
    assert "offline synthetic" in result["scope"]


def test_docker_fixture_serializes_one_process_writes_and_preserves_bad_state(
    tmp_path: Path,
) -> None:
    path = ROOT / "courses/docker/fixtures/compose-lab/server.py"
    spec = importlib.util.spec_from_file_location("docker_study_fixture", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.__dict__["DATA"] = tmp_path
    assert module.read_counter() == 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        values = list(executor.map(lambda _: module.increment(), range(40)))
    assert sorted(values) == list(range(1, 41))
    assert module.read_counter() == 40
    for invalid in (
        '{"schema_version":1,"counter":true}',
        '{"schema_version":true,"counter":0}',
        "[]",
    ):
        (tmp_path / "counter.json").write_text(invalid)
        with pytest.raises(ValueError, match="invalid counter state"):
            module.read_counter()
        assert (tmp_path / "counter.json").read_text() == invalid


def test_docker_fixture_retains_local_scope_and_explicit_storage() -> None:
    yaml = pytest.importorskip("yaml")
    base = ROOT / "courses/docker/fixtures/compose-lab"
    compose = yaml.safe_load((base / "compose.yaml").read_text())
    app = compose["services"]["app"]
    assert app["ports"] == ["127.0.0.1:18080:8080"]
    assert app["read_only"] is True and app["cap_drop"] == ["ALL"]
    assert app["volumes"] == ["study-data:/data"]
    assert app["pull_policy"] == "never"
    assert compose["services"]["client"]["profiles"] == ["tools"]
    assert "docker.sock" not in (base / "compose.yaml").read_text()
    assert "USER 10001:10001" in (base / "Dockerfile").read_text()
    assert "POST `/increment`" in (base / "README.md").read_text()


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Node absent; actual browser qualification is separate"
)
def test_d3_references_and_worked_snippets_parse_without_claiming_node_execution(
    tmp_path: Path,
) -> None:
    entries = records("javascript-typescript")
    for number in range(43, 67):
        row = entries[f"js-{number:03d}"]
        reference = (ROOT / row["solution_paths"][0]).read_text()
        guide = (ROOT / row["guide_path"]).read_text()
        examples = re.findall(r"```javascript\n(.*?)\n```", guide, re.S)
        assert len(examples) == 2
        for index, source in enumerate([reference, *examples]):
            path = tmp_path / f"{row['id']}-{index}.mjs"
            path.write_text(source)
            result = subprocess.run(
                ["node", "--check", str(path)], capture_output=True, text=True, timeout=10
            )
            assert result.returncode == 0, result.stderr


@pytest.mark.skipif(
    not socket.has_dualstack_ipv6(),
    reason="Host lacks dual-stack sockets; cluster qualification is separate",
)
@pytest.mark.parametrize(
    "bind,address,family",
    [("::1", "::1", socket.AF_INET6), ("::ffff:127.0.0.1", "127.0.0.1", socket.AF_INET)],
)
def test_optional_dual_stack_app_serves_each_family_on_owned_loopback(
    bind: str,
    address: str,
    family: int,
) -> None:
    base = ROOT / "courses/kubernetes/fixtures/networking/dual-stack"
    server = runpy.run_path(str(base / "server.py"))
    client = runpy.run_path(str(base / "probe.py"))
    assert server["VERSION"] == client["EXPECTED"] == b"ds60-dualstack-v1\n"
    instance = server["DualStackServer"]((bind, 0), server["Handler"])
    thread = threading.Thread(
        target=instance.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True
    )
    thread.start()
    try:
        result = client["probe"](address, instance.server_port, family)
        assert result == {
            "family": "IPv4" if family == socket.AF_INET else "IPv6",
            "status": "passed",
            "version": "ds60-dualstack-v1",
        }
        if family == socket.AF_INET:
            # Mapped IPv4 needs dual-stack mode. Linux may set IPV6_V6ONLY
            # after a native IPv6-only bind, which still serves IPv6 correctly.
            assert instance.socket.getsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY) == 0
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive()


@pytest.mark.parametrize(
    "address,family",
    [
        ("::1", socket.AF_INET),
        ("::ffff:127.0.0.1", socket.AF_INET6),
        ("8.8.8.8", socket.AF_INET),
        ("0.0.0.0", socket.AF_INET),
    ],
)
def test_dual_stack_probe_rejects_wrong_family_public_or_unspecified_targets_before_socket(
    address: str,
    family: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = runpy.run_path(
        str(ROOT / "courses/kubernetes/fixtures/networking/dual-stack/probe.py")
    )

    def denied(*args: object, **kwargs: object) -> None:
        raise AssertionError("Invalid target reached socket creation")

    monkeypatch.setattr(socket, "socket", denied)
    with pytest.raises(ValueError, match="owned lab receipt"):
        client["probe"](address, 8080, family)
