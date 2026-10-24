"""Offline application and teacher-ownership contracts, never a live cluster proof."""

from __future__ import annotations

import copy
import http.client
import importlib.util
import json
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from ds60sqlpy.kubernetes_module import KubernetesRefusal, parse_manifests

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "courses/kubernetes/fixtures/secret-observer"


def load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "secret_observer_" + name, FOLDER / (name + ".py")
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def modules(monkeypatch: pytest.MonkeyPatch) -> tuple[ModuleType, ModuleType, ModuleType]:
    app = load("app")
    render = load("render")
    monkeypatch.setitem(sys.modules, "render", render)
    return app, render, load("teacher")


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"unknown",
        b"DUMMY_LESSON_ONLY\n",
        b"DUMMY_LESSON_ONLY" + b"\n" * 80,
        b"DUMMY_LESSON_ROTATED" + b"x" * 100,
    ],
)
def test_marker_rejects_unknown_or_nonexact_bytes(
    modules: Any, tmp_path: Path, value: bytes
) -> None:
    path = tmp_path / "marker"
    path.write_bytes(value)
    with pytest.raises(ValueError):
        modules[0].marker_label(path)


def test_three_lifetimes_and_restart(modules: Any, tmp_path: Path) -> None:
    app = modules[0]
    path = tmp_path / "marker"
    path.write_bytes(b"DUMMY_LESSON_ONLY")
    observation = app.Observation(path, "DUMMY_LESSON_ONLY", "pod-first")
    initial = observation.observe()
    assert [initial[k] for k in ("environment", "projected_file", "application_cache")] == [
        "initial"
    ] * 3
    replacement = tmp_path / "replacement"
    replacement.write_bytes(b"DUMMY_LESSON_ROTATED")
    replacement.replace(path)
    projected = observation.observe()
    assert projected == {**initial, "projected_file": "rotated"}
    reloaded = observation.reload()
    assert reloaded == {**projected, "application_cache": "rotated"}
    restarted = app.Observation(path, "DUMMY_LESSON_ROTATED", "pod-second").observe()
    assert restarted["boot_id"] != initial["boot_id"]
    assert restarted["pod_uid"] == "pod-second"
    assert [restarted[k] for k in ("environment", "projected_file", "application_cache")] == [
        "rotated"
    ] * 3
    assert "DUMMY_" not in json.dumps([initial, projected, reloaded, restarted])


def test_reload_reads_once_and_failed_reload_preserves_cache(
    modules: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = modules[0]
    path = tmp_path / "marker"
    path.write_bytes(b"DUMMY_LESSON_ONLY")
    observation = app.Observation(path, "DUMMY_LESSON_ONLY", "pod")
    values = iter(["rotated"])
    monkeypatch.setattr(app, "marker_label", lambda _: next(values))
    assert observation.reload()["projected_file"] == "rotated"
    with pytest.raises(StopIteration):
        observation.reload()
    assert observation.cached == "rotated"


def test_http_labels_errors_body_and_transfer_encoding(modules: Any, tmp_path: Path) -> None:
    app = modules[0]
    path = tmp_path / "marker"
    path.write_bytes(b"DUMMY_LESSON_ONLY")
    observation = app.Observation(path, "DUMMY_LESSON_ONLY", "pod-uid")
    with app.ThreadingHTTPServer(("127.0.0.1", 0), app.handler_for(observation)) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def request(
            method: str, endpoint: str, headers: list[tuple[str, str]]
        ) -> tuple[int, dict[str, str]]:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            try:
                connection.putrequest(method, endpoint)
                for key, value in headers:
                    connection.putheader(key, value)
                connection.endheaders()
                response = connection.getresponse()
                content = response.read()
                assert "DUMMY_" not in content.decode()
                assert response.getheader("Cache-Control") == "no-store"
                return response.status, json.loads(content)
            finally:
                connection.close()

        try:
            assert request("GET", "/ready", [])[0] == 200
            assert request("GET", "/observe?token=do-not-reflect", [])[0] == 404
            for headers in (
                [("Transfer-Encoding", "chunked")],
                [("Content-Length", "1")],
                [("Content-Length", "0"), ("Content-Length", "0")],
            ):
                assert request("POST", "/reload", headers)[0] == 400
            path.write_bytes(b"DUMMY_LESSON_ROTATED")
            assert request("GET", "/observe", [])[1]["application_cache"] == "initial"
            assert (
                request("POST", "/reload", [("Content-Length", "0")])[1]["application_cache"]
                == "rotated"
            )
            path.write_bytes(b"private-value-must-not-be-reflected")
            status, error = request("GET", "/observe", [])
            assert status == 503 and error == {"error": "Synthetic marker unavailable or invalid"}
        finally:
            server.shutdown()
            thread.join(timeout=2)


def test_rendered_manifest_is_exact_and_restricted(modules: Any) -> None:
    rendered = modules[1].manifest(FOLDER)
    assert json.loads((FOLDER / "manifest.json").read_text()) == rendered
    secret, program, deployment = rendered["items"]
    assert secret["stringData"] == {"lesson-message": "DUMMY_LESSON_ONLY"}
    assert program["data"]["app.py"] == (FOLDER / "app.py").read_text()
    pod = deployment["spec"]["template"]["spec"]
    assert pod["automountServiceAccountToken"] is False
    assert pod["securityContext"]["fsGroup"] == 65532
    container = pod["containers"][0]
    assert container["image"] == "ds60sqlpy-k8s-fixture:0.2.0"
    assert container["imagePullPolicy"] == "Never"
    assert container["command"] == ["python", "-u", "/lesson/app.py"]
    assert container["securityContext"]["readOnlyRootFilesystem"] is True
    assert container["securityContext"]["capabilities"] == {"drop": ["ALL"]}
    assert all(mount["readOnly"] and "subPath" not in mount for mount in container["volumeMounts"])
    assert pod["volumes"][1]["secret"]["defaultMode"] == 0o440
    assert json.loads((FOLDER / "rotate.json").read_text()) == {
        "stringData": {"lesson-message": "DUMMY_LESSON_ROTATED"}
    }
    with pytest.raises(KubernetesRefusal):
        parse_manifests(json.dumps(rendered))


def fake_teacher(module: ModuleType, tmp_path: Path) -> Any:
    teacher = module.Teacher.__new__(module.Teacher)
    teacher.lease = SimpleNamespace(
        owner_id="a" * 32, namespace="owned", namespace_uid="ns-uid", expires_at=time.time() + 900
    )
    teacher.nonce = "b" * 32
    teacher.ledger = []
    teacher.evidence = {"objects": teacher.ledger, "observations": []}
    teacher.directory = tmp_path
    teacher.deadline = time.monotonic() + 60
    teacher.cleaning = False
    teacher.target = lambda: None
    return teacher


def metadata(module: ModuleType, uid: str, *, nonce: str = "b" * 32) -> dict[str, Any]:
    return {"uid": uid, "labels": {module.OWNER_LABEL: "a" * 32, module.NONCE_LABEL: nonce}}


def test_delete_and_rotation_require_identity(modules: Any, tmp_path: Path) -> None:
    module = modules[2]
    teacher = fake_teacher(module, tmp_path)
    current = {"metadata": metadata(module, "replacement")}
    teacher.get = lambda *_: current
    calls: list[Any] = []
    teacher.call = lambda *args, **kwargs: calls.append((args, kwargs))
    with pytest.raises(module.Refusal, match="replacement"):
        teacher.delete("secrets", "synthetic-message", "old")
    assert calls == []
    current["metadata"]["uid"] = "old"
    teacher.delete("secrets", "synthetic-message", "old")
    args, kwargs = calls[0]
    assert args == (
        "delete",
        "--raw",
        "/api/v1/namespaces/owned/secrets/synthetic-message",
        "-f",
        "-",
    )
    assert kwargs["body"]["preconditions"] == {"uid": "old"}
    assert kwargs["body"]["propagationPolicy"] == "Foreground"
    patch = module.rotation_patch("secret-uid", "rv7")
    assert patch[:2] == [
        {"op": "test", "path": "/metadata/uid", "value": "secret-uid"},
        {"op": "test", "path": "/metadata/resourceVersion", "value": "rv7"},
    ]


def test_collision_is_preserved_before_any_create(modules: Any, tmp_path: Path) -> None:
    module = modules[2]
    teacher = fake_teacher(module, tmp_path)
    teacher.get = lambda *_: {"metadata": {"uid": "preexisting"}}
    calls: list[Any] = []

    def call(*args: Any, **kwargs: Any) -> str:
        calls.append(args)
        return json.dumps({"clientVersion": {"gitVersion": module.KUBECTL_VERSION}})

    teacher.call = call
    with pytest.raises(module.Refusal, match="already exists"):
        teacher.create()
    assert teacher.ledger == []
    assert all(args[0] != "create" for args in calls)


def test_timeout_after_create_records_uid_and_cleans_owned_object(
    modules: Any, tmp_path: Path
) -> None:
    module = modules[2]
    teacher = fake_teacher(module, tmp_path)
    objects: dict[tuple[str, str], Any] = {}
    teacher.get = lambda resource, name: copy.deepcopy(objects.get((resource, name)))

    def call(*args: str, body: Any = None) -> str:
        if args[0] == "version":
            return json.dumps({"clientVersion": {"gitVersion": module.KUBECTL_VERSION}})
        if args[0] == "create":
            objects[("secrets", "synthetic-message")] = {
                "metadata": {**body["metadata"], "uid": "created-before-timeout"}
            }
            raise subprocess.TimeoutExpired("fixed kubectl create", 12)
        if args[0] == "delete":
            assert body["preconditions"]["uid"] == "created-before-timeout"
            objects.pop(("secrets", "synthetic-message"))
            return "{}"
        raise AssertionError(args)

    teacher.call = call
    teacher.selected = lambda _: []
    with pytest.raises(subprocess.TimeoutExpired):
        teacher.create()
    assert teacher.ledger == [
        {"resource": "secrets", "name": "synthetic-message", "uid": "created-before-timeout"}
    ]
    teacher.cleanup()
    assert teacher.evidence["cleanup_confirmed"] is True
    assert objects == {}


def test_cleanup_preserves_replacement_and_marks_failure(modules: Any, tmp_path: Path) -> None:
    module = modules[2]
    teacher = fake_teacher(module, tmp_path)
    teacher.ledger.append({"resource": "secrets", "name": "synthetic-message", "uid": "original"})
    teacher.get = lambda *_: {"metadata": metadata(module, "replacement")}
    teacher.cleanup()
    assert teacher.evidence["cleanup_confirmed"] is False
    assert teacher.evidence["cleanup_review_required"] == ["secrets/synthetic-message"]


def test_namespace_uid_mismatch_refuses_mutation(modules: Any, tmp_path: Path) -> None:
    module = modules[2]
    teacher = fake_teacher(module, tmp_path)
    del teacher.target
    teacher.call = lambda *_: json.dumps(
        {"metadata": {"uid": "other", "labels": {module.OWNER_LABEL: "a" * 32}}}
    )
    with pytest.raises(module.Refusal, match="namespace identity"):
        teacher.target()


def test_wrong_controller_graph_refused(modules: Any, tmp_path: Path) -> None:
    module = modules[2]
    teacher = fake_teacher(module, tmp_path)
    teacher.ledger.append({"resource": "deployments", "name": module.APP, "uid": "deployment"})
    teacher.checked = lambda *_: {}
    teacher.selected = lambda _: [
        {
            "metadata": {
                **metadata(module, "replica"),
                "ownerReferences": [
                    {"controller": True, "kind": "Deployment", "uid": "different-deployment"}
                ],
            }
        }
    ]
    with pytest.raises(module.Refusal, match="ReplicaSet ownership"):
        teacher.ready_pod()


@pytest.mark.parametrize("interrupt", ["signal", "keyboard"])
def test_main_interrupt_runs_cleanup_and_restores_handlers(
    modules: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, interrupt: str
) -> None:
    module = modules[2]
    observed: list[str] = []

    class Runner:
        def __init__(self, *args: Any) -> None:
            self.evidence: dict[str, Any] = {}

        def run(self) -> None:
            if interrupt == "signal":
                handler = signal.getsignal(signal.SIGTERM)
                assert callable(handler)
                handler(signal.SIGTERM, None)
            raise KeyboardInterrupt

        def cleanup(self) -> None:
            observed.append("cleanup")
            self.evidence["cleanup_confirmed"] = True

    monkeypatch.setattr(module, "Teacher", Runner)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "teacher.py",
            "--session",
            str(tmp_path),
            "--kubectl",
            str(tmp_path / "kubectl"),
            "--output",
            str(tmp_path / "out"),
            "--confirm-synthetic-secret",
        ],
    )
    before = signal.getsignal(signal.SIGTERM)
    assert module.main() == 2
    assert observed == ["cleanup"]
    assert signal.getsignal(signal.SIGTERM) == before


def test_private_context_binding_rejects_plugin_or_wrong_endpoint(
    modules: Any, tmp_path: Path
) -> None:
    import base64
    import hashlib

    module = modules[2]
    teacher = fake_teacher(module, tmp_path)
    teacher.context = "kind-owned"
    teacher.receipt = {"host_server": "https://127.0.0.1:12345"}
    teacher.lease.ca_sha256 = hashlib.sha256(b"synthetic-ca").hexdigest()
    config = {
        "current-context": teacher.context,
        "clusters": [
            {
                "name": teacher.context,
                "cluster": {
                    "server": teacher.receipt["host_server"],
                    "certificate-authority-data": base64.b64encode(b"synthetic-ca").decode(),
                },
            }
        ],
        "contexts": [
            {
                "name": teacher.context,
                "context": {
                    "cluster": teacher.context,
                    "user": teacher.context,
                },
            }
        ],
        "users": [
            {
                "name": teacher.context,
                "user": {
                    "client-certificate-data": base64.b64encode(b"synthetic-certificate").decode(),
                    "client-key-data": base64.b64encode(b"synthetic-key").decode(),
                },
            }
        ],
    }
    teacher._check_config(config)
    for kind in ("plugin", "endpoint", "ca", "context"):
        changed = copy.deepcopy(config)
        if kind == "plugin":
            changed["users"][0]["user"]["exec"] = {"command": "must-not-run"}
        elif kind == "endpoint":
            changed["clusters"][0]["cluster"]["server"] = "https://example.invalid:443"
        elif kind == "ca":
            changed["clusters"][0]["cluster"]["certificate-authority-data"] = base64.b64encode(
                b"different"
            ).decode()
        else:
            changed["current-context"] = "other"
        with pytest.raises(module.Refusal):
            teacher._check_config(changed)


def test_fixture_guide_and_source_are_durably_integrated() -> None:
    guide = (ROOT / "courses/kubernetes/guides/k8s-019.md").read_text()
    author = (ROOT / "courses/kubernetes/authoring/complete/batch15_20.py").read_text()
    assert (
        "fixtures/secret-observer/README.md" in guide
        and "fixtures/secret-observer/README.md" in author
    )
    solution = json.loads((ROOT / "courses/kubernetes/solutions/k8s-019_solution.json").read_text())
    assert solution == json.loads((FOLDER / "manifest.json").read_text())
    entries = json.loads((ROOT / "courses/kubernetes/lessons.json").read_text())["lessons"]
    assert next(row for row in entries if row["id"] == "k8s-019")["runtime_profile"] == "reading"
    for path in FOLDER.iterdir():
        if path.is_file():
            assert "\u2014" not in path.read_text()


def test_teacher_full_flow_uses_real_patch_file_and_preserves_phase_identities(
    modules: Any, tmp_path: Path
) -> None:
    import contextlib

    module = modules[2]
    teacher = fake_teacher(module, tmp_path)
    teacher.ledger.append({"resource": "secrets", "name": "synthetic-message", "uid": "secret-uid"})
    teacher.create = lambda: None
    pods = iter(
        [
            {"metadata": {"name": "first", "uid": "pod-first"}},
            {"metadata": {"name": "second", "uid": "pod-second"}},
        ]
    )
    teacher.ready_pod = lambda **_: next(pods)
    teacher.forward = lambda _: contextlib.nullcontext(12345)
    teacher.checked = lambda *_: {"metadata": {"resourceVersion": "opaque-version"}}
    initial = {
        "pod_uid": "pod-first",
        "boot_id": "c" * 32,
        "environment": "initial",
        "projected_file": "initial",
        "application_cache": "initial",
    }
    projected = {**initial, "projected_file": "rotated"}
    reloaded = {**projected, "application_cache": "rotated"}
    restarted = {**reloaded, "pod_uid": "pod-second", "boot_id": "d" * 32, "environment": "rotated"}
    observations = iter([initial, projected, reloaded, restarted])
    teacher.observation = lambda *_, **__: next(observations)
    requests: list[Any] = []

    def call(*args: Any, body: Any = None) -> str:
        assert args[:4] == ("patch", "secret", "synthetic-message", "--type=json")
        assert args[4] == "--patch-file" and args[5] != "-" and body is None
        patch = json.loads(Path(args[5]).read_text())
        assert patch[:2] == module.rotation_patch("secret-uid", "opaque-version")[:2]
        requests.append(args)
        return "secret/synthetic-message"

    teacher.call = call
    deleted: list[Any] = []
    teacher.delete = lambda *args: deleted.append(args)
    teacher.run()
    assert len(requests) == 1
    assert deleted == [("pods", "first", "pod-first")]
    assert [item["stage"] for item in teacher.evidence["observations"]] == [
        "initial",
        "projected_before_reload",
        "application_reloaded",
        "replacement_pod",
    ]
    assert teacher.evidence["observation_passed"] is True
