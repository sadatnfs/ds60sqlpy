"""Ownership and target-admission checks for the external Spark deployment lab."""

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/spark-deployment"
PROJECT = BASE / "projects/cluster-lab"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_saved_state_is_not_overwritten(tmp_path):
    lab = module("deployment_lab", PROJECT / "lab.py")
    saved = tmp_path / "saved"
    saved.mkdir()
    sentinel = saved / "learner.txt"
    sentinel.write_text("retained")
    with pytest.raises(ValueError, match="State already exists"):
        lab.initialize(saved, "unused", None)
    assert sentinel.read_text() == "retained"


def test_image_admission_rejects_emulation(monkeypatch):
    lab = module("deployment_lab", PROJECT / "lab.py")
    monkeypatch.setattr(lab.platform, "machine", lambda: "arm64")
    monkeypatch.setattr(lab, "require_local_engine", lambda: None)
    monkeypatch.setattr(
        lab,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            [],
            0,
            json.dumps([{"Os": "linux", "Architecture": "amd64", "Id": "sha256:" + "a" * 64}]),
        ),
    )
    with pytest.raises(ValueError, match="native architecture"):
        lab.local_image("prepared-image")


def test_initialize_saves_image_and_private_state(tmp_path, monkeypatch):
    lab = module("deployment_lab", PROJECT / "lab.py")
    image = {"id": "sha256:" + "b" * 64, "architecture": "arm64", "reference": "prepared"}
    monkeypatch.setattr(lab, "local_image", lambda reference: image)
    saved = tmp_path / "new-state"
    lab.initialize(saved, "prepared", None)
    record = json.loads((saved / "owner.json").read_text())
    assert record["runtime"] == image
    assert saved.stat().st_mode & 0o777 == 0o700
    assert (saved / "private/notebook-token").read_text().strip()
    assert lab.load(saved)["owner"] == record["owner"]
    record["state"] = str(tmp_path / "different")
    (saved / "owner.json").write_text(json.dumps(record))
    with pytest.raises(ValueError, match="binding differs"):
        lab.load(saved)


def test_foreign_container_prevents_lifecycle(monkeypatch):
    lab = module("deployment_lab", PROJECT / "lab.py")
    calls = []

    def fake(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(
            args,
            0,
            "foreign\n"
            if args[1] == "ps"
            else json.dumps(
                [
                    {
                        "Config": {
                            "Labels": {
                                "ds60.owner": "somebody-else",
                                "com.docker.compose.service": "driver",
                            }
                        }
                    }
                ]
            ),
        )

    monkeypatch.setattr(lab, "run", fake)
    with pytest.raises(ValueError, match="outside the saved workshop"):
        lab.verify_containers({"owner": "ds60-spark-deploy-0123456789ab"})
    assert all(call[1] in {"ps", "inspect"} for call in calls)


def test_compose_uses_saved_identity_and_discards_ambient_overrides(monkeypatch):
    lab = module("deployment_lab", PROJECT / "lab.py")
    monkeypatch.setenv("COMPOSE_PROJECT_NAME", "unrelated-project")
    monkeypatch.setenv("DS60_SPARK_IMAGE", "moving:latest")
    record = {
        "owner": "ds60-spark-deploy-0123456789ab",
        "state": "/owned",
        "runtime": {"id": "sha256:" + "c" * 64},
        "notebook": None,
    }
    argv, env = lab.compose(record)
    assert "unrelated-project" not in argv
    assert "COMPOSE_PROJECT_NAME" not in env
    assert env["DS60_SPARK_IMAGE"] == record["runtime"]["id"]
    assert argv[argv.index("--project-name") + 1] == record["owner"]


def test_network_mount_and_resource_boundaries():
    compose = yaml.safe_load((PROJECT / "compose.yaml").read_text())
    assert compose["networks"]["lab"]["internal"] is True
    services = compose["services"]
    assert {"master", "worker-a", "worker-b", "driver", "history"} <= services.keys()
    for service in services.values():
        assert service["pull_policy"] == "never"
        assert service["read_only"] is True
        assert service["pids_limit"] <= 512
        assert all(port.startswith("127.0.0.1:") for port in service.get("ports", []))
        mounts = service["volumes"]
        assert not any("docker.sock" in mount or mount.startswith("./:") for mount in mounts)
        if service["hostname"] != "notebook":
            assert not any("/private" in mount for mount in mounts)
    assert services["ui"]["networks"] == ["lab", "ingress"]
    assert all(service["networks"] == ["lab"] for name, service in services.items() if name != "ui")
    assert "volumes" not in compose


def k8s_args(tmp_path):
    config = tmp_path / "owned-kubeconfig"
    config.write_text("explicit-test-fixture")
    return argparse.Namespace(
        namespace="ds60-spark-study",
        context="owned",
        kubeconfig=config,
        master="k8s://https://example.invalid:6443",
        image="example.invalid/spark@sha256:" + "d" * 64,
        spark_submit="spark-submit",
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("namespace", "default"),
        ("master", "k8s://http://example.invalid"),
        ("image", "example.invalid/spark:latest"),
    ],
)
def test_kubernetes_rejects_ambient_or_mutable_target(tmp_path, field, value):
    submit = module("deployment_submit", PROJECT / "kubernetes/submit.py")
    args = k8s_args(tmp_path)
    setattr(args, field, value)
    with pytest.raises(ValueError):
        submit.command(args)


def test_kubernetes_plan_retains_namespace_context_and_bounds(tmp_path):
    submit = module("deployment_submit", PROJECT / "kubernetes/submit.py")
    argv = submit.command(k8s_args(tmp_path))
    assert "spark.kubernetes.namespace=ds60-spark-study" in argv
    assert "spark.kubernetes.context=owned" in argv
    assert "spark.driver.maxResultSize=1m" in argv
    assert "spark.executor.instances=2" in argv
    assert argv[-1].startswith("local:///")


def test_generated_route_matches_maintained_chapters():
    author = module("deployment_author", BASE / "authoring/build.py")
    for path, expected in author.outputs().items():
        assert path.read_text() == expected, str(path)


def test_remote_docker_endpoint_is_rejected_without_contact(monkeypatch):
    lab = module("deployment_local_engine", PROJECT / "lab.py")
    monkeypatch.setenv("DOCKER_HOST", "tcp://example.invalid:2376")
    monkeypatch.delenv("DOCKER_CONTEXT", raising=False)
    monkeypatch.setattr(lab, "run", lambda *a, **k: pytest.fail("Remote engine contacted"))
    with pytest.raises(ValueError, match="local Unix-socket"):
        lab.require_local_engine()


@pytest.mark.parametrize(
    "endpoint",
    [
        "k8s://https://secret@example.invalid:6443",
        "k8s://https://example.invalid:6443?token=hidden",
        "k8s://https://example.invalid:6443/path",
    ],
)
def test_kubernetes_endpoint_excludes_credential_and_path_data(tmp_path, endpoint):
    submit = module("deployment_endpoint", PROJECT / "kubernetes/submit.py")
    args = k8s_args(tmp_path)
    args.master = endpoint
    with pytest.raises(ValueError, match="credentials, query or path"):
        submit.command(args)


def test_execution_rejects_context_endpoint_mismatch(tmp_path, monkeypatch):
    submit = module("deployment_context", PROJECT / "kubernetes/submit.py")
    observed = []

    def local_config(args, **kwargs):
        observed.append(args)
        return subprocess.CompletedProcess(args, 0, "https://different.invalid:6443")

    monkeypatch.setattr(submit.subprocess, "run", local_config)
    with pytest.raises(ValueError, match="differs from the explicit"):
        submit.verify_context_endpoint(k8s_args(tmp_path))
    assert observed[0][0] == "kubectl"
    assert observed[0][-1] == "jsonpath={.clusters[0].cluster.server}"
    assert "--raw" not in observed[0]


def test_qualified_runtime_sources_match_retained_execution_receipt():
    receipt = json.loads((PROJECT / "qualification-arm64.json").read_text())
    for relative, expected in receipt["runtime_source_sha256"].items():
        assert hashlib.sha256((PROJECT / relative).read_bytes()).hexdigest() == expected, relative
