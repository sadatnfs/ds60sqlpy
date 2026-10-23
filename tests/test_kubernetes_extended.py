"""Fixed ConfigMap/task/probe operations with ownership, failure and offline fixture proofs."""

from __future__ import annotations

import copy
import importlib.util
import json
import runpy
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, cast

import pytest

from ds60sqlpy.kubernetes_module import (
    CONFIG_NAME,
    FIXTURE_IMAGE,
    JOB_LABEL,
    OWNER_LABEL,
    TASK_NAME,
    CommandResult,
    HostTools,
    InterruptedOperation,
    KubernetesLease,
    KubernetesRefusal,
    kubernetes_executor,
    parse_manifests,
    prepare_owned_session,
)

ROOT = Path(__file__).resolve().parents[1]
SUPPORT = runpy.run_path(str(ROOT / "tests/test_kubernetes_module.py"))
OWNER = SUPPORT["OWNER"]
NAMESPACE = SUPPORT["NAMESPACE"]


@pytest.fixture
def lease() -> KubernetesLease:
    return KubernetesLease(
        OWNER,
        "ds60-" + OWNER[:12],
        "ds60-owned",
        NAMESPACE,
        "namespace-uid",
        time.time() + 900,
        "c" * 64,
        b"{}",
    )


def source_documents() -> list[dict[str, Any]]:
    return parse_manifests((ROOT / "courses/kubernetes/lessons/k8s-008.yaml").read_text())


def config_documents() -> list[dict[str, Any]]:
    deployment, service = source_documents()
    pod = deployment["spec"]["template"]["spec"]
    container = pod["containers"][0]
    container["env"] = [
        {
            "name": "DS60_MESSAGE",
            "valueFrom": {"configMapKeyRef": {"name": CONFIG_NAME, "key": "message"}},
        }
    ]
    pod["volumes"] = [
        {
            "name": "lesson-config",
            "configMap": {"name": CONFIG_NAME, "items": [{"key": "message", "path": "message"}]},
        }
    ]
    container["volumeMounts"] = [
        {"name": "lesson-config", "mountPath": "/config", "readOnly": True}
    ]
    config = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": CONFIG_NAME},
        "data": {"message": "reviewer"},
    }
    return [config, deployment, service]


def task_document(outcome: str = "success") -> dict[str, Any]:
    pod = copy.deepcopy(source_documents()[0]["spec"]["template"]["spec"])
    container = pod["containers"][0]
    container.pop("ports")
    container.pop("readinessProbe")
    container["name"] = "task"
    container["command"] = ["python", "/fixture.py", "task", "--outcome", outcome]
    pod["restartPolicy"] = "Never"
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": TASK_NAME},
        "spec": {
            "backoffLimit": 0,
            "activeDeadlineSeconds": 20,
            "completions": 1,
            "parallelism": 1,
            "template": {"metadata": {"labels": {"app": "hello"}}, "spec": pod},
        },
    }


def dump(documents: list[dict[str, Any]]) -> str:
    yaml = pytest.importorskip("yaml")
    return str(yaml.safe_dump_all(documents))


def execute(
    source: str,
    tmp_path: Path,
    lease: KubernetesLease,
    runner: Any,
    cancel: threading.Event | None = None,
) -> Any:
    return kubernetes_executor(lease, runner=runner, stable_seconds=0)(
        "k8s-kind",
        source,
        tmp_path,
        60,
        cancel or threading.Event(),
        lambda _: None,
        None,
        isolate_user=False,
    )


def arguments(argv: list[str]) -> list[str]:
    return argv[argv.index("--request-timeout=5s") + 1 :]


def test_config_map_value_checks_and_uid_cleanup(tmp_path: Path, lease: KubernetesLease) -> None:
    cluster = SUPPORT["FakeCluster"](lease)
    result = execute(dump(config_documents()), tmp_path, lease, cluster)
    assert result.status == "succeeded", result.detail
    assert not cluster.objects
    checks = {item["name"]: item["passed"] for item in result.checks}
    assert checks["configmap-environment"] and checks["configmap-mounted-file"]
    created = [payload for args, payload in cluster.calls if args[0] == "create"]
    assert created[0]["kind"] == "ConfigMap"
    client = next(item for item in created if item["kind"] == "Job")
    command = client["spec"]["template"]["spec"]["containers"][0]["command"]
    assert command[-4:] == ["--expect-message", "reviewer", "--expect-file-message", "reviewer"]
    assert any(
        args[0] == "delete"
        and "/configmaps/hello-config" in args[2]
        and payload["preconditions"]["uid"]
        for args, payload in cluster.calls
    )


@pytest.mark.parametrize("outcome,expected", [("success", "succeeded"), ("failure", "failed")])
def test_finite_task_success_and_deliberate_failure_are_cleaned(
    tmp_path: Path,
    lease: KubernetesLease,
    outcome: str,
    expected: str,
) -> None:
    cluster = SUPPORT["FakeCluster"](lease)
    result = execute(dump([task_document(outcome)]), tmp_path, lease, cluster)
    assert result.status == expected, result.detail
    assert not cluster.objects
    assert any(args[0] == "delete" and "/jobs/hello-task" in args[2] for args, _ in cluster.calls)
    if outcome == "success":
        assert any(item["name"] == "owned-finite-task" and item["passed"] for item in result.checks)
        assert any(args[0] == "logs" and "--limit-bytes=4096" in args for args, _ in cluster.calls)


@pytest.mark.parametrize(
    "field", ["namespace", "owner", "nonce", "controller", "exit", "container"]
)
def test_job_completion_count_cannot_replace_pod_identity(
    tmp_path: Path,
    lease: KubernetesLease,
    field: str,
) -> None:
    cluster = SUPPORT["FakeCluster"](lease)

    def runner(argv: list[str], **kwargs: Any) -> CommandResult:
        result = cast(CommandResult, cluster(argv, **kwargs))
        args = arguments(argv)
        if args[:2] == ["get", "pods"] and "batch.kubernetes.io/job-name=" in args[3]:
            payload = json.loads(result.stdout)
            pod = payload["items"][0]
            if field == "namespace":
                pod["metadata"]["namespace"] = "foreign"
            elif field == "owner":
                pod["metadata"]["labels"][OWNER_LABEL] = "foreign"
            elif field == "nonce":
                pod["metadata"]["labels"][JOB_LABEL] = "foreign"
            elif field == "controller":
                pod["metadata"]["ownerReferences"][0]["uid"] = "foreign"
            elif field == "exit":
                pod["status"]["containerStatuses"][0]["state"]["terminated"]["exitCode"] = 2
            else:
                pod["status"]["containerStatuses"][0]["name"] = "unrelated"
            return CommandResult(0, json.dumps(payload))
        return result

    result = execute(dump([task_document()]), tmp_path, lease, runner)
    assert result.status == "failed"
    assert not cluster.objects
    assert not any(args[0] == "logs" for args, _ in cluster.calls)


def test_finite_task_output_is_checked_independently(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = SUPPORT["FakeCluster"](lease)

    def runner(argv: list[str], **kwargs: Any) -> CommandResult:
        result = cast(CommandResult, cluster(argv, **kwargs))
        if arguments(argv)[0] == "logs":
            return CommandResult(
                0, json.dumps({"accepted": 3, "rejected": 2, "total": 34, "fixture_contract": 2})
            )
        return result

    result = execute(dump([task_document()]), tmp_path, lease, runner)
    assert result.status == "failed" and "independent fixed ledger" in result.detail
    assert not cluster.objects


@pytest.mark.parametrize("kind,status", [("ConfigMap", "cancelled"), ("Job", "timed_out")])
def test_uncertain_new_kind_create_uses_nonce_recovery_and_fresh_cleanup(
    tmp_path: Path,
    lease: KubernetesLease,
    kind: str,
    status: str,
) -> None:
    cluster = SUPPORT["FakeCluster"](lease)
    interrupted = False

    def runner(argv: list[str], **kwargs: Any) -> CommandResult:
        nonlocal interrupted
        result = cast(CommandResult, cluster(argv, **kwargs))
        payload = json.loads(kwargs["input_data"]) if kwargs["input_data"] else None
        if (
            not interrupted
            and arguments(argv)[0] == "create"
            and payload is not None
            and payload["kind"] == kind
        ):
            interrupted = True
            raise InterruptedOperation(status)
        return result

    source = config_documents() if kind == "ConfigMap" else [task_document()]
    result = execute(dump(source), tmp_path, lease, runner)
    assert result.status == status and not cluster.objects
    deletes = [(args, payload) for args, payload in cluster.calls if args[0] == "delete"]
    assert deletes and all(payload["preconditions"]["uid"] for _, payload in deletes)


def test_uncertain_configmap_with_foreign_nonce_is_preserved(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = SUPPORT["FakeCluster"](lease)
    interrupted = False

    def runner(argv: list[str], **kwargs: Any) -> CommandResult:
        nonlocal interrupted
        result = cast(CommandResult, cluster(argv, **kwargs))
        args = arguments(argv)
        if not interrupted and args[0] == "create":
            payload = json.loads(kwargs["input_data"])
            if payload["kind"] == "ConfigMap":
                interrupted = True
                cluster.objects[("configmap", CONFIG_NAME)]["metadata"]["labels"][JOB_LABEL] = (
                    "foreign"
                )
                raise InterruptedOperation("cancelled")
        return result

    result = execute(dump(config_documents()), tmp_path, lease, runner)
    assert result.status == "failed" and ("configmap", CONFIG_NAME) in cluster.objects
    assert not any(args[0] == "delete" for args, _ in cluster.calls)


@pytest.mark.parametrize(
    "mutation",
    [
        "secret",
        "host-path",
        "arbitrary-env",
        "config-value",
        "config-name",
        "missing-config",
        "unused-config",
        "probe-host",
        "probe-path",
        "task-shell",
        "task-deadline",
        "task-parallel",
        "task-with-service",
    ],
)
def test_extension_preserves_a_closed_manifest_boundary(mutation: str) -> None:
    docs = config_documents()
    pod = docs[1]["spec"]["template"]["spec"]
    container = pod["containers"][0]
    if mutation == "secret":
        container["env"][0]["valueFrom"] = {"secretKeyRef": {"name": "real", "key": "token"}}
    elif mutation == "host-path":
        pod["volumes"] = [{"name": "lesson-config", "hostPath": {"path": "/"}}]
    elif mutation == "arbitrary-env":
        container["env"] = [{"name": "PYTHONPATH", "value": "/config"}]
    elif mutation == "config-value":
        docs[0]["data"]["message"] = "arbitrary private data"
    elif mutation == "config-name":
        docs[0]["metadata"]["name"] = "other"
    elif mutation == "missing-config":
        docs = docs[1:]
    elif mutation == "unused-config":
        container.pop("env")
        container.pop("volumeMounts")
        pod.pop("volumes")
    elif mutation == "probe-host":
        container["livenessProbe"] = {
            "httpGet": {"path": "/live", "port": "http", "host": "external.example"},
            "periodSeconds": 1,
            "failureThreshold": 1,
        }
    elif mutation == "probe-path":
        container["startupProbe"] = {
            "httpGet": {"path": "/arbitrary", "port": "http"},
            "periodSeconds": 1,
            "failureThreshold": 1,
        }
    else:
        docs = [task_document()]
        if mutation == "task-shell":
            docs[0]["spec"]["template"]["spec"]["containers"][0]["command"] = [
                "sh",
                "-c",
                "echo unsafe",
            ]
        elif mutation == "task-deadline":
            docs[0]["spec"]["activeDeadlineSeconds"] = 999
        elif mutation == "task-parallel":
            docs[0]["spec"]["parallelism"] = 2
        else:
            docs.append(source_documents()[1])
    with pytest.raises(KubernetesRefusal):
        parse_manifests(dump(docs))


def test_old_saved_image_has_actionable_refusal_without_rewrite() -> None:
    source = dump(source_documents()).replace(FIXTURE_IMAGE, "ds60sqlpy-k8s-fixture:0.1.0")
    with pytest.raises(KubernetesRefusal, match="Saved learner source is not rewritten"):
        parse_manifests(source)
    assert "0.1.0" in source


def test_host_role_adds_only_required_namespaced_configmap_permissions(tmp_path: Path) -> None:
    host = SUPPORT["FakeHost"]()
    prepare_owned_session(
        tmp_path / "session",
        HostTools("kind", "kubectl", "docker"),
        "unix:///explicit/local.sock",
        runner=host,
        owner_id=OWNER,
    )
    objects = [json.loads(data) for _, _, data in host.calls if data is not None]
    role = next(obj for obj in objects if obj.get("kind") == "Role")
    rules = [rule for rule in role["rules"] if "configmaps" in rule["resources"]]
    assert rules == [
        {"apiGroups": [""], "resources": ["configmaps"], "verbs": ["create"]},
        {
            "apiGroups": [""],
            "resources": ["configmaps"],
            "resourceNames": [CONFIG_NAME],
            "verbs": ["get", "delete"],
        },
    ]
    assert role["metadata"]["namespace"] == NAMESPACE
    assert all(
        "secrets" not in rule["resources"] and "pods/exec" not in rule["resources"]
        for rule in role["rules"]
    )


def fixture_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "extended_k8s_fixture", ROOT / "docker/kubernetes/fixture.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixture_endpoints_are_bounded_and_preserve_legacy_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = fixture_module()
    assert fixture.fixture_response("/ready") == (200, b"ready\n")
    assert fixture.fixture_response("/version") == (200, b"ds60-fixture-v1\n")
    assert fixture.fixture_response("/live") == (200, b"live\n")
    monkeypatch.setenv("DS60_STARTUP_DELAY_SECONDS", "3")
    monkeypatch.setattr(fixture, "START_TIME", time.monotonic())
    assert fixture.fixture_response("/startup")[0] == 503
    monkeypatch.setattr(fixture, "START_TIME", time.monotonic() - 4)
    assert fixture.fixture_response("/startup")[0] == 200
    monkeypatch.setenv("DS60_MESSAGE", "reviewer")
    assert fixture.fixture_response("/message") == (200, b"reviewer\n")
    message = tmp_path / "message"
    message.write_text("hello")
    monkeypatch.setattr(fixture, "CONFIG_FILE", message)
    assert fixture.fixture_response("/file-message") == (200, b"hello\n")
    message.write_text("reviewer")
    assert fixture.fixture_response("/file-message") == (200, b"reviewer\n")
    message.write_bytes(b"x" * 65)
    assert fixture.fixture_response("/file-message")[0] == 503
    assert fixture.fixture_response("/missing")[0] == 404


@pytest.mark.parametrize("outcome,code", [("success", 0), ("failure", 2)])
def test_actual_finite_fixture_cli_has_exact_exit_and_output(outcome: str, code: int) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "docker/kubernetes/fixture.py"), "task", "--outcome", outcome],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == code and not result.stderr
    output = json.loads(result.stdout)
    assert output["fixture_contract"] == 2
    if outcome == "success":
        assert output == {"accepted": 3, "rejected": 2, "total": 35, "fixture_contract": 2}
    else:
        assert output["status"] == "injected-failure"


@pytest.mark.parametrize(
    "name,kinds",
    [
        ("hello-configured.yaml", ["ConfigMap", "Deployment", "Service"]),
        ("hello-startup.yaml", ["Deployment", "Service"]),
        ("hello-task.yaml", ["Job"]),
        ("hello-task-failure.yaml", ["Job"]),
    ],
)
def test_curated_contract_two_files_pass_the_actual_parser(name: str, kinds: list[str]) -> None:
    documents = parse_manifests((ROOT / "courses/kubernetes/fixtures" / name).read_text())
    assert [document["kind"] for document in documents] == kinds


def test_actual_http_client_checks_both_configmap_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from http.server import ThreadingHTTPServer

    fixture = fixture_module()
    message = tmp_path / "message"
    message.write_text("reviewer")
    monkeypatch.setattr(fixture, "CONFIG_FILE", message)
    monkeypatch.setenv("DS60_MESSAGE", "reviewer")
    server = ThreadingHTTPServer(("127.0.0.1", 0), fixture.FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/version"
        assert (
            fixture.main(
                [
                    "client",
                    "--url",
                    url,
                    "--expect",
                    "ds60-fixture-v1",
                    "--expect-message",
                    "reviewer",
                    "--expect-file-message",
                    "reviewer",
                ]
            )
            == 0
        )
        assert (
            fixture.main(
                ["client", "--url", url, "--expect", "ds60-fixture-v1", "--expect-message", "hello"]
            )
            == 2
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
