"""No live cluster: adversarial manifest/lease and fake API identity proofs."""

from __future__ import annotations

import base64
import contextlib
import copy
import hashlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.kubernetes_module import (
    FIXTURE_IMAGE,
    OWNER_LABEL,
    CommandResult,
    InterruptedOperation,
    KubectlClient,
    KubernetesLease,
    KubernetesRefusal,
    kubernetes_executor,
    observe_ready,
    parse_manifests,
    run_kubectl,
)

ROOT = Path(__file__).resolve().parents[1]
OWNER = "a" * 32
NAMESPACE = "ds60-lesson-" + OWNER[:12]
SOURCE = ROOT / "courses/kubernetes/lessons/k8s-008.yaml"


class PrivateAclModel:
    """Model the external ACL boundary in fake-host tests, not native ACL proof."""

    def __init__(self) -> None:
        self.roots: set[Path] = set()
        self.calls: list[tuple[Path, bool]] = []

    def __call__(self, path: Path, *, establish: bool = False) -> bool:
        resolved = path.resolve()
        self.calls.append((resolved, establish))
        if establish:
            if not resolved.is_dir():
                return False
            self.roots.add(resolved)
        return any(resolved == root or root in resolved.parents for root in self.roots)


def model_private_acl(monkeypatch: pytest.MonkeyPatch) -> PrivateAclModel:
    from ds60sqlpy import kubernetes_module

    policy = PrivateAclModel()
    monkeypatch.setattr(kubernetes_module, "_windows_private_acl", policy)
    return policy


@pytest.fixture
def private_acl(monkeypatch: pytest.MonkeyPatch) -> PrivateAclModel:
    return model_private_acl(monkeypatch)


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


class FakeCluster:
    def __init__(self, lease: KubernetesLease) -> None:
        self.lease = lease
        self.objects: dict[tuple[str, str], dict[str, Any]] = {}
        self.calls: list[tuple[list[str], dict[str, Any] | None]] = []
        self.namespace_uid = lease.namespace_uid
        self.replacement_on_cleanup = False
        self.sequence = 0
        self.had_job = False

    def __call__(self, argv: list[str], **kwargs: Any) -> CommandResult:
        args = argv[argv.index("--request-timeout=5s") + 1 :]
        payload = json.loads(kwargs["input_data"]) if kwargs["input_data"] else None
        self.calls.append((args, payload))
        result: dict[str, Any]
        assert "--kubeconfig" in argv and "--context" in argv and "--namespace" in argv
        if args[:2] == ["get", "namespace"]:
            result = {"metadata": {"uid": self.namespace_uid, "labels": {OWNER_LABEL: OWNER}}}
        elif args[0] == "create":
            assert payload is not None
            kind = {
                "Deployment": "deployment",
                "Service": "service",
                "Job": "job",
                "ConfigMap": "configmap",
            }[payload["kind"]]
            name = payload["metadata"]["name"]
            if (kind, name) in self.objects:
                return CommandResult(1, "", "AlreadyExists")
            result = copy.deepcopy(payload)
            self.sequence += 1
            result["metadata"].update(namespace=NAMESPACE, uid=f"uid-{self.sequence}", generation=1)
            if kind == "deployment":
                count = result["spec"]["replicas"]
                result["status"] = {
                    "observedGeneration": 1,
                    "updatedReplicas": count,
                    "readyReplicas": count,
                    "availableReplicas": count,
                }
            if kind == "job":
                self.had_job = True
                result["status"] = {
                    "succeeded": 1,
                    "conditions": [{"type": "Complete", "status": "True"}],
                }
                command = result["spec"]["template"]["spec"]["containers"][0]["command"]
                if command[-1] == "failure":
                    result["status"] = {
                        "failed": 1,
                        "conditions": [{"type": "Failed", "status": "True"}],
                    }
            self.objects[(kind, name)] = result
        elif args[0] == "delete":
            assert args[1] == "--raw" and args[-2:] == ["-f", "-"]
            assert payload is not None
            kind = {
                "deployments": "deployment",
                "services": "service",
                "jobs": "job",
                "configmaps": "configmap",
            }[args[2].split("/")[-2]]
            name = args[2].split("/")[-1]
            current = self.objects[(kind, name)]
            assert payload["preconditions"]["uid"] == current["metadata"]["uid"]
            del self.objects[(kind, name)]
            result = {"kind": "Status", "status": "Success"}
        elif args[:2] == ["get", "replicasets"]:
            deployment = self.objects[("deployment", "hello")]
            result = {
                "items": [
                    {
                        "metadata": {
                            "uid": "rs-uid",
                            "ownerReferences": [
                                {"uid": deployment["metadata"]["uid"], "controller": True}
                            ],
                        }
                    }
                ]
            }
        elif args[:2] == ["get", "pods"] and "batch.kubernetes.io/job-name=" in args[3]:
            name = args[3].split("batch.kubernetes.io/job-name=", 1)[1]
            job = self.objects[("job", name)]
            template = job["spec"]["template"]
            result = {
                "items": [
                    {
                        "metadata": {
                            "name": name + "-pod",
                            "namespace": NAMESPACE,
                            "uid": name + "-pod-uid",
                            "labels": copy.deepcopy(template["metadata"]["labels"]),
                            "ownerReferences": [
                                {"uid": job["metadata"]["uid"], "controller": True, "kind": "Job"}
                            ],
                        },
                        "status": {
                            "phase": "Succeeded",
                            "containerStatuses": [
                                {
                                    "name": template["spec"]["containers"][0]["name"],
                                    "state": {"terminated": {"exitCode": 0}},
                                }
                            ],
                        },
                    }
                ]
            }
        elif args[0] == "logs":
            result = {"accepted": 3, "rejected": 2, "total": 35, "fixture_contract": 2}
        elif args[:2] == ["get", "pods"]:
            deployment = self.objects[("deployment", "hello")]
            count = deployment["spec"]["replicas"]
            ready = (
                deployment["spec"]["template"]["spec"]["containers"][0]["readinessProbe"][
                    "httpGet"
                ]["path"]
                == "/ready"
            )
            result = {
                "items": [
                    {
                        "metadata": {
                            "uid": f"pod-{n}",
                            "labels": {OWNER_LABEL: OWNER},
                            "ownerReferences": [{"uid": "rs-uid", "controller": True}],
                        },
                        "status": {
                            "conditions": [
                                {"type": "Ready", "status": "True" if ready else "False"}
                            ]
                        },
                    }
                    for n in range(count)
                ]
            }
        elif args[:2] == ["get", "endpointslices"]:
            deployment = self.objects[("deployment", "hello")]
            service = self.objects[("service", "hello")]
            count = deployment["spec"]["replicas"]
            ready = service["spec"]["selector"] == {"app": "hello"}
            endpoints = (
                [
                    {
                        "conditions": {"ready": True},
                        "targetRef": {"kind": "Pod", "namespace": NAMESPACE, "uid": f"pod-{n}"},
                    }
                    for n in range(count)
                ]
                if ready
                else []
            )
            # Two IP families may repeat identities; the verifier must deduplicate.
            result = {
                "items": [
                    {
                        "metadata": {
                            "ownerReferences": [
                                {"uid": service["metadata"]["uid"], "controller": True}
                            ]
                        },
                        "endpoints": endpoints,
                    },
                    {
                        "metadata": {
                            "ownerReferences": [
                                {"uid": service["metadata"]["uid"], "controller": True}
                            ]
                        },
                        "endpoints": endpoints,
                    },
                ]
            }
        elif args[0] == "get":
            key = (args[1], args[2])
            if key not in self.objects:
                return CommandResult(1, "", "Error from server (NotFound)")
            result = copy.deepcopy(self.objects[key])
            if self.replacement_on_cleanup and key == ("service", "hello") and self.had_job:
                result["metadata"]["uid"] = "replacement-service"
        else:
            raise AssertionError(args)
        return CommandResult(0, json.dumps(result))


def test_actual_lesson_sources_pass_narrow_manifest_contract() -> None:
    for name in ("k8s-003.yaml", "k8s-008.yaml"):
        docs = parse_manifests((SOURCE.parent / name).read_text())
        assert docs[0]["kind"] == "Deployment"
        assert docs[0]["metadata"]["name"] == "hello"


@pytest.mark.parametrize(
    "mutation",
    [
        "namespace",
        "other-name",
        "image",
        "shell",
        "host-network",
        "volume",
        "privileged",
        "token",
        "replicas",
        "node-port",
        "probe-url",
    ],
)
def test_manifest_cannot_escape_owned_fixed_fixture(mutation: str) -> None:
    yaml = pytest.importorskip("yaml")
    docs = parse_manifests(SOURCE.read_text())
    dep, service = docs
    pod = dep["spec"]["template"]["spec"]
    container = pod["containers"][0]
    if mutation == "namespace":
        dep["metadata"]["namespace"] = "default"
    elif mutation == "other-name":
        dep["metadata"]["name"] = "billing"
    elif mutation == "image":
        container["image"] = "arbitrary:latest"
    elif mutation == "shell":
        container["command"] = ["sh", "-c", "anything"]
    elif mutation == "host-network":
        pod["hostNetwork"] = True
    elif mutation == "volume":
        pod["volumes"] = [{"name": "host", "hostPath": {"path": "/"}}]
    elif mutation == "privileged":
        container["securityContext"]["privileged"] = True
    elif mutation == "token":
        pod["automountServiceAccountToken"] = True
    elif mutation == "replicas":
        dep["spec"]["replicas"] = 3
    elif mutation == "node-port":
        service["spec"]["type"] = "NodePort"
    else:
        container["readinessProbe"]["httpGet"]["host"] = "external.example"
    with pytest.raises(KubernetesRefusal):
        parse_manifests(yaml.safe_dump_all(docs))


@pytest.mark.parametrize(
    "source",
    [
        "kind: Deployment\nkind: Service\n",
        "apiVersion: v1\nkind: &a Service\nmetadata: *a\n",
        '!!python/object/apply:os.system ["echo unsafe"]',
    ],
)
def test_duplicate_alias_and_unsafe_yaml_tags_are_refused(source: str) -> None:
    with pytest.raises(KubernetesRefusal):
        parse_manifests(source)


def test_fake_one_shot_proves_routing_then_cleans_only_owned_uids(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = FakeCluster(lease)
    execute = kubernetes_executor(lease, runner=cluster, stable_seconds=0)
    phases: list[str] = []
    result = execute(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        threading.Event(),
        phases.append,
        "k8s-readiness-v1",
        isolate_user=False,
    )
    assert result.status == "succeeded", result.detail
    assert phases == ["running", "verifying"]
    assert {c["name"] for c in result.checks} >= {
        "controller-and-pods",
        "ready-service-backends",
        "in-cluster-version",
        "owned-cleanup",
    }
    assert all(c["passed"] for c in result.checks)
    assert not cluster.objects
    for args, payload in cluster.calls:
        if args[0] == "delete":
            assert payload is not None
            assert payload["kind"] == "DeleteOptions"
            assert payload["preconditions"]["uid"].startswith("uid-")
            assert "/namespaces/" + NAMESPACE + "/" in args[2]


def test_equal_backend_counts_with_wrong_identities_fail(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = FakeCluster(lease)
    client = KubectlClient(lease, tmp_path, runner=cluster, isolate_user=False)
    deadline = time.monotonic() + 5
    cancel = threading.Event()
    docs = parse_manifests(SOURCE.read_text())
    ids = []
    for doc in docs:
        doc["metadata"].setdefault("labels", {})[OWNER_LABEL] = OWNER
        result = client.apply(doc, deadline, cancel)
        ids.append(result["metadata"]["uid"])
    service = cluster.objects[("service", "hello")]
    service["spec"]["selector"] = {"app": "wrong"}
    healthy, evidence = observe_ready(client, ids[0], 2, ids[1], deadline, cancel)
    assert not healthy
    assert len(evidence["ready_pod_uids"]) == 2
    assert evidence["ready_endpoint_uids"] == []


def test_namespace_replacement_refuses_before_any_create(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = FakeCluster(lease)
    cluster.namespace_uid = "replacement-namespace"
    execute = kubernetes_executor(lease, runner=cluster, stable_seconds=0)
    result = execute(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        threading.Event(),
        lambda _: None,
        None,
        isolate_user=False,
    )
    assert result.status == "failed"
    assert not any(args[0] == "create" for args, _ in cluster.calls)


def test_uid_change_during_cleanup_preserves_replacement(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = FakeCluster(lease)
    cluster.replacement_on_cleanup = True
    execute = kubernetes_executor(lease, runner=cluster, stable_seconds=0)
    result = execute(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        threading.Event(),
        lambda _: None,
        "k8s-readiness-v1",
        isolate_user=False,
    )
    assert result.status == "failed"
    assert ("service", "hello") in cluster.objects
    assert not any(args[0] == "delete" and "/services/" in args[2] for args, _ in cluster.calls)


def test_existing_unclaimed_resource_is_never_adopted(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = FakeCluster(lease)
    cluster.objects[("deployment", "hello")] = {"metadata": {"name": "hello", "uid": "manual"}}
    execute = kubernetes_executor(lease, runner=cluster)
    result = execute(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        threading.Event(),
        lambda _: None,
        None,
        isolate_user=False,
    )
    assert result.status == "failed"
    assert not any(args[0] in ("create", "delete") for args, _ in cluster.calls)


def test_expiry_and_cancellation_do_not_create_resources(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    expired = KubernetesLease(
        lease.owner_id,
        lease.cluster_name,
        lease.context,
        lease.namespace,
        lease.namespace_uid,
        time.time() - 1,
        lease.ca_sha256,
        lease.kubeconfig,
    )
    cluster = FakeCluster(expired)
    result = kubernetes_executor(expired, runner=cluster)(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        threading.Event(),
        lambda _: None,
        None,
        isolate_user=False,
    )
    assert result.status == "failed" and not cluster.calls
    cancelled = threading.Event()
    cancelled.set()
    with pytest.raises(InterruptedOperation, match="cancelled"):
        run_kubectl(
            ["not-invoked"],
            input_data=None,
            deadline=time.monotonic() + 2,
            cancel=cancelled,
            directory=tmp_path,
            isolate_user=False,
        )


def test_private_lease_checks_ca_endpoint_and_expiry(
    tmp_path: Path, private_acl: PrivateAclModel
) -> None:
    assert private_acl(tmp_path, establish=True)
    ca = base64.b64encode(b"fixture-ca").decode()
    config: dict[str, Any] = {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "ds60-owned",
        "clusters": [
            {
                "name": "ds60",
                "cluster": {
                    "server": "https://ds60-" + OWNER[:12] + "-control-plane:6443",
                    "certificate-authority-data": ca,
                },
            }
        ],
        "users": [{"name": "scoped", "user": {"token": "t" * 64}}],
        "contexts": [
            {
                "name": "ds60-owned",
                "context": {"cluster": "ds60", "user": "scoped", "namespace": NAMESPACE},
            }
        ],
    }
    payload: dict[str, Any] = {
        "schema_version": 1,
        "owner_id": OWNER,
        "cluster_name": "ds60-" + OWNER[:12],
        "context": "ds60-owned",
        "namespace": NAMESPACE,
        "namespace_uid": "namespace-uid",
        "expires_at": datetime.fromtimestamp(time.time() + 900, UTC).isoformat(),
        "ca_sha256": hashlib.sha256(b"fixture-ca").hexdigest(),
        "kubeconfig_file": "worker.kubeconfig.json",
        "fixture_image": FIXTURE_IMAGE,
    }
    cfg = tmp_path / "worker.kubeconfig.json"
    cfg.write_text(json.dumps(config))
    cfg.chmod(0o600)
    path = tmp_path / "lease.json"
    path.write_text(json.dumps(payload))
    path.chmod(0o600)
    assert KubernetesLease.load(path).namespace == NAMESPACE
    config["clusters"][0]["cluster"]["server"] = "https://unrelated.example"
    cfg.write_text(json.dumps(config))
    with pytest.raises(KubernetesRefusal, match="endpoint"):
        KubernetesLease.load(path)


class FakeHost:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], dict[str, str], bytes | None]] = []
        self.cluster = "ds60-" + OWNER[:12]
        self.namespace_uid = "namespace-uid"
        self.container_id = "d" * 64
        self.fail_token = False
        self.node_cached = True
        self.deleted = False

    def __call__(
        self,
        argv: list[str],
        *,
        environment: dict[str, str],
        data: bytes | None = None,
        timeout: float = 90,
    ) -> CommandResult:
        self.calls.append((argv, environment, data))
        assert "DOCKER_CONTEXT" not in environment
        assert environment["DOCKER_HOST"].startswith("unix:///")
        assert ".kube/config" not in " ".join(argv)
        if argv[0] == "kind" and argv[1:] == ["version"]:
            return CommandResult(0, "kind v0.33.0 go-test linux/arm64\n")
        if argv[0] == "kubectl" and argv[1:3] == ["version", "--client"]:
            return CommandResult(0, json.dumps({"clientVersion": {"gitVersion": "v1.37.0"}}))
        if argv[0] == "docker":
            if "image" in argv:
                return CommandResult(0 if self.node_cached or FIXTURE_IMAGE in argv else 1, "[{}]")
            if "container" in argv and "rm" in argv:
                assert argv[-2] == "--force"
                if argv[-1] != self.container_id:
                    return CommandResult(1, "", "error: no such container")
                self.deleted = True
                return CommandResult(0, self.container_id)
            if "container" in argv and "ls" in argv:
                return CommandResult(
                    0,
                    ""
                    if self.deleted
                    else self.container_id + "\t" + self.cluster + "-control-plane\n",
                )
            if "inspect" in argv:
                if self.deleted:
                    return CommandResult(1, "", "Error: No such object: control-plane")
                return CommandResult(
                    0,
                    json.dumps(
                        [
                            {
                                "Id": self.container_id,
                                "Config": {"Labels": {"io.x-k8s.kind.cluster": self.cluster}},
                            }
                        ]
                    ),
                )
            return CommandResult(0, '"test-engine"')
        if argv[0] == "kind":
            if argv[1:3] == ["delete", "cluster"]:
                self.deleted = True
            if argv[1:3] == ["get", "clusters"]:
                return CommandResult(0, "")
            if argv[1:3] == ["create", "cluster"]:
                assert "--kubeconfig" in argv
                admin = Path(argv[argv.index("--kubeconfig") + 1])
                admin.write_text("{}")
                admin.chmod(0o600)
                config = json.loads(Path(argv[argv.index("--config") + 1]).read_text())
                assert config["networking"]["apiServerAddress"] == "127.0.0.1"
                assert len(config["nodes"]) == 1
            return CommandResult(0, "")
        assert argv[0] == "kubectl"
        assert "--kubeconfig" in argv and "--context" in argv
        if "view" in argv:
            return CommandResult(
                0,
                json.dumps(
                    {
                        "apiVersion": "v1",
                        "kind": "Config",
                        "current-context": "kind-" + self.cluster,
                        "clusters": [
                            {
                                "name": "kind-" + self.cluster,
                                "cluster": {
                                    "server": "https://127.0.0.1:54433",
                                    "certificate-authority-data": base64.b64encode(
                                        b"fixture-ca"
                                    ).decode(),
                                },
                            }
                        ],
                        "users": [
                            {
                                "name": "kind-" + self.cluster,
                                "user": {
                                    "client-certificate-data": "Y2VydA==",
                                    "client-key-data": "a2V5",
                                },
                            }
                        ],
                        "contexts": [
                            {
                                "name": "kind-" + self.cluster,
                                "context": {
                                    "cluster": "kind-" + self.cluster,
                                    "user": "kind-" + self.cluster,
                                },
                            }
                        ],
                    }
                ),
            )
        if "token" in argv:
            if self.fail_token:
                return CommandResult(1, "", "token failed")
            return CommandResult(
                0,
                json.dumps(
                    {
                        "status": {
                            "token": "t" * 64,
                            "expirationTimestamp": datetime.fromtimestamp(
                                time.time() + 900, UTC
                            ).isoformat(),
                        }
                    }
                ),
            )
        if "namespace" in argv and "get" in argv:
            return CommandResult(
                0,
                json.dumps(
                    {"metadata": {"uid": self.namespace_uid, "labels": {OWNER_LABEL: OWNER}}}
                ),
            )
        assert data is not None
        obj = json.loads(data)
        result = copy.deepcopy(obj)
        result["metadata"]["uid"] = (
            self.namespace_uid if obj["kind"] == "Namespace" else "other-uid"
        )
        if obj["kind"] == "Role":
            assert all(
                "*" not in rule["verbs"] and "*" not in rule["resources"] for rule in obj["rules"]
            )
            assert not any("secrets" in rule["resources"] for rule in obj["rules"])
        if obj["kind"] == "ClusterRole":
            assert obj["rules"] == [
                {
                    "apiGroups": [""],
                    "resources": ["namespaces"],
                    "resourceNames": [NAMESPACE],
                    "verbs": ["get"],
                }
            ]
        return CommandResult(0, json.dumps(result))


def test_host_preparation_never_uses_ambient_context_and_bounds_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, private_acl: PrivateAclModel
) -> None:
    from ds60sqlpy.kubernetes_module import HostTools, prepare_owned_session

    monkeypatch.setenv("DOCKER_CONTEXT", "unrelated-remote")
    monkeypatch.setenv("KUBECONFIG", "/unrelated/real.config")
    host = FakeHost()
    session = tmp_path / "private-session"
    path = prepare_owned_session(
        session,
        HostTools("kind", "kubectl", "docker"),
        "unix:///explicit/local.sock",
        runner=host,
        owner_id=OWNER,
    )
    loaded = KubernetesLease.load(path)
    assert loaded.namespace == NAMESPACE
    assert loaded.context == "ds60-owned"
    assert loaded.expires_at > time.time() + 125
    assert loaded.kubeconfig.find(b"client-key-data") == -1
    if os.name == "nt":
        assert session.resolve() in private_acl.roots and private_acl(path)
    else:
        assert path.stat().st_mode & 0o077 == 0
    assert all(
        env["KUBECONFIG"] == str(session / "admin.kubeconfig.json") for _, env, _ in host.calls
    )
    create = next(argv for argv, _, _ in host.calls if argv[:3] == ["kind", "create", "cluster"])
    assert create[create.index("--kubeconfig") + 1] == str(session / "admin.kubeconfig.json")
    token_requests = [argv for argv, _, _ in host.calls if "token" in argv]
    assert token_requests and "--duration=15m" in token_requests[0]


def test_host_node_download_requires_explicit_consent(
    tmp_path: Path, private_acl: PrivateAclModel
) -> None:
    from ds60sqlpy.kubernetes_module import HostTools, prepare_owned_session

    host = FakeHost()
    host.node_cached = False
    with pytest.raises(KubernetesRefusal, match="node image is absent"):
        prepare_owned_session(
            tmp_path / "private",
            HostTools("kind", "kubectl", "docker"),
            "unix:///explicit/local.sock",
            runner=host,
            owner_id=OWNER,
        )
    assert not any(argv[:3] == ["kind", "create", "cluster"] for argv, _, _ in host.calls)


@pytest.mark.parametrize(
    "endpoint", ["tcp://remote.example:2375", "ssh://remote", "http://127.0.0.1:2375"]
)
def test_host_refuses_nonlocal_engine_before_creating_any_state(
    tmp_path: Path, endpoint: str
) -> None:
    from ds60sqlpy.kubernetes_module import HostTools, prepare_owned_session

    host = FakeHost()
    session = tmp_path / "not-created"
    with pytest.raises(KubernetesRefusal, match="local Unix socket"):
        prepare_owned_session(
            session, HostTools("kind", "kubectl", "docker"), endpoint, runner=host
        )
    assert not session.exists() and not host.calls


def test_host_release_preserves_replaced_namespace_and_other_clusters(
    tmp_path: Path, private_acl: PrivateAclModel
) -> None:
    from ds60sqlpy.kubernetes_module import HostTools, prepare_owned_session, release_owned_session

    host = FakeHost()
    tools = HostTools("kind", "kubectl", "docker")
    session = tmp_path / "private"
    prepare_owned_session(
        session, tools, "unix:///explicit/local.sock", runner=host, owner_id=OWNER
    )
    host.namespace_uid = "replacement"
    with pytest.raises(KubernetesRefusal, match="namespace was replaced"):
        release_owned_session(session, tools, runner=host)
    assert not any("container" in argv and "rm" in argv for argv, _, _ in host.calls)
    assert (session / "worker.kubeconfig.json").exists()
    host.namespace_uid = "namespace-uid"
    release_owned_session(session, tools, runner=host)
    deletes = [argv for argv, _, _ in host.calls if "container" in argv and "rm" in argv]
    assert len(deletes) == 1 and deletes[0][-1] == host.container_id
    assert not (session / "worker.kubeconfig.json").exists()


def test_pinned_mirror_cannot_change_the_node_digest(
    tmp_path: Path, private_acl: PrivateAclModel
) -> None:
    from ds60sqlpy.kubernetes_module import NODE_IMAGE, HostTools, prepare_owned_session

    host = FakeHost()
    prepare_owned_session(
        tmp_path / "mirror",
        HostTools("kind", "kubectl", "docker"),
        "unix:///explicit/local.sock",
        runner=host,
        owner_id=OWNER,
        node_image="mirror.gcr.io/" + NODE_IMAGE,
    )
    create = next(argv for argv, _, _ in host.calls if argv[:3] == ["kind", "create", "cluster"])
    assert create[create.index("--image") + 1] == "mirror.gcr.io/" + NODE_IMAGE
    with pytest.raises(KubernetesRefusal, match="exact official release/index digest"):
        prepare_owned_session(
            tmp_path / "bad",
            HostTools("kind", "kubectl", "docker"),
            "unix:///explicit/local.sock",
            runner=host,
            node_image="mirror.gcr.io/kindest/node:latest",
        )


def test_fixture_actual_http_has_independent_ready_and_version_checks() -> None:
    import importlib.util
    from http.server import ThreadingHTTPServer

    spec = importlib.util.spec_from_file_location(
        "ds60_owned_fixture", ROOT / "docker/kubernetes/fixture.py"
    )
    assert spec and spec.loader
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    server = ThreadingHTTPServer(("127.0.0.1", 0), fixture.FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        assert fixture.check_version(base + "/version", "ds60-fixture-v1")
        assert not fixture.check_version(base + "/version", "wrong-version")
        with pytest.raises(ValueError):
            fixture.check_version("http://external.example:8080/version", "ds60-fixture-v1")
        with pytest.raises(ValueError):
            fixture.check_version(base + "/ready", "ready")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_host_symlinked_parent_cannot_place_credentials_in_learning(tmp_path: Path) -> None:
    from ds60sqlpy.kubernetes_module import HostTools, prepare_owned_session

    portable = tmp_path / ".learning"
    portable.mkdir()
    parent = tmp_path / "apparently-private"
    parent.symlink_to(portable, target_is_directory=True)
    host = FakeHost()
    with pytest.raises(KubernetesRefusal, match="ancestors"):
        prepare_owned_session(
            parent / "session",
            HostTools("kind", "kubectl", "docker"),
            "unix:///explicit/local.sock",
            runner=host,
            owner_id=OWNER,
        )
    assert not host.calls and list(portable.iterdir()) == []


def test_cancel_after_create_commit_recovers_only_own_job_uid(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cancel = threading.Event()
    cluster = FakeCluster(lease)

    def uncertain(argv: list[str], **kwargs: Any) -> CommandResult:
        result = cluster(argv, **kwargs)
        args = argv[argv.index("--request-timeout=5s") + 1 :]
        if args[0] == "create":
            cancel.set()
            raise InterruptedOperation("cancelled")
        return result

    result = kubernetes_executor(lease, runner=uncertain, stable_seconds=0)(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        cancel,
        lambda _: None,
        None,
        isolate_user=False,
    )
    assert result.status == "cancelled", result.detail
    assert not cluster.objects
    cleanup = next(c for c in result.checks if c["name"] == "owned-cleanup")
    assert cleanup["passed"] is True
    assert any(args[0] == "delete" for args, _ in cluster.calls)


def test_uncertain_create_with_other_nonce_is_preserved_and_failed(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    from ds60sqlpy.kubernetes_module import JOB_LABEL

    cluster = FakeCluster(lease)

    def uncertain(argv: list[str], **kwargs: Any) -> CommandResult:
        result = cluster(argv, **kwargs)
        args = argv[argv.index("--request-timeout=5s") + 1 :]
        if args[0] == "create":
            cluster.objects[("deployment", "hello")]["metadata"]["labels"][JOB_LABEL] = (
                "another-run"
            )
            raise InterruptedOperation("cancelled")
        return result

    result = kubernetes_executor(lease, runner=uncertain, stable_seconds=0)(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        threading.Event(),
        lambda _: None,
        None,
        isolate_user=False,
    )
    assert result.status == "failed"
    assert ("deployment", "hello") in cluster.objects
    assert not any(args[0] == "delete" for args, _ in cluster.calls)
    assert any(c["name"] == "owned-cleanup" and c["passed"] is False for c in result.checks)


def test_host_preparation_failure_cleans_only_recorded_node(
    tmp_path: Path, private_acl: PrivateAclModel
) -> None:
    from ds60sqlpy.kubernetes_module import HostTools, prepare_owned_session

    host = FakeHost()
    host.fail_token = True
    session = tmp_path / "failure"
    with pytest.raises(KubernetesRefusal, match="recorded owned node was removed"):
        prepare_owned_session(
            session,
            HostTools("kind", "kubectl", "docker"),
            "unix:///explicit/local.sock",
            runner=host,
            owner_id=OWNER,
        )
    receipt = json.loads((session / "preparation-failure.json").read_text())
    assert receipt["owned_node_recorded"] and receipt["cleanup_confirmed"]
    assert host.deleted
    assert not (session / "admin.kubeconfig.json").exists()


def test_cli_generated_temp_base_is_canonical_but_user_alias_is_not(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "ds60_prepare_test", ROOT / "scripts/prepare_kubernetes.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    real = tmp_path / "real-temp"
    real.mkdir()
    alias = tmp_path / "temp-alias"
    alias.symlink_to(real, target_is_directory=True)
    tools = tmp_path / "tools"
    tools.mkdir()
    operating, architecture, suffix = module.tool_targets()
    del operating, architecture
    (tools / f"kind-{module.KIND_VERSION}{suffix}").write_text("fixture")
    (tools / f"kubectl-{module.KUBECTL_VERSION}{suffix}").write_text("fixture")
    selected: list[Path] = []
    monkeypatch.setattr(module.tempfile, "gettempdir", lambda: str(alias))

    def capture_prepare(directory: Path, *args: Any, **kwargs: Any) -> Path:
        selected.append(directory)
        return directory / "lease.json"

    monkeypatch.setattr(module, "prepare_owned_session", capture_prepare)
    assert (
        module.main(
            [
                "prepare",
                "--tools-dir",
                str(tools),
                "--docker",
                str(tools / "docker"),
                "--docker-host",
                "unix:///explicit/local.sock",
                "--confirm-create",
            ]
        )
        == 0
    )
    assert selected[0].parent == real.resolve()


def test_cleanup_has_fresh_budget_after_work_deadline(
    tmp_path: Path, lease: KubernetesLease, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    cluster = FakeCluster(lease)
    interrupted = False
    cleanup_deadlines: list[float] = []

    def runner(argv: list[str], **kwargs: Any) -> CommandResult:
        nonlocal interrupted
        assert kwargs["deadline"] > clock[0]
        response = cluster(argv, **kwargs)
        args = argv[argv.index("--request-timeout=5s") + 1 :]
        if args[0] == "create" and not interrupted:
            interrupted = True
            clock[0] = 116.0
            raise InterruptedOperation("timed_out")
        if interrupted:
            cleanup_deadlines.append(kwargs["deadline"])
        return response

    result = kubernetes_executor(lease, runner=runner, stable_seconds=0)(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        15,
        threading.Event(),
        lambda _: None,
        None,
        isolate_user=False,
    )
    assert result.status == "timed_out", result.detail
    assert not cluster.objects
    assert cleanup_deadlines and all(value == 131.0 for value in cleanup_deadlines)
    assert any(item["name"] == "owned-cleanup" and item["passed"] for item in result.checks)


def _wait_for_active_worker(process: subprocess.Popen[str], started: Path) -> None:
    deadline = time.monotonic() + 10
    while not started.exists() and process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.02)
    if not started.exists() or process.poll() is not None:
        if process.poll() is None:
            with contextlib.suppress(ProcessLookupError):
                process.kill()
        stdout, stderr = process.communicate(timeout=5)
        pytest.fail(
            "The fake operation never entered a live active phase. "
            f"Child return code: {process.returncode}.\n"
            f"stdout:\n{stdout[-4000:]}\nstderr:\n{stderr[-4000:]}"
        )


def test_worker_startup_failure_reports_child_stderr(tmp_path: Path) -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", "raise RuntimeError('synthetic startup exception')"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    try:
        with pytest.raises(pytest.fail.Exception, match="synthetic startup exception"):
            _wait_for_active_worker(process, tmp_path / "never-started")
        assert process.returncode == 1
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)


@pytest.mark.skipif(os.name == "nt", reason="POSIX SIGTERM protocol; Windows has a separate row")
def test_sigterm_waits_for_active_operation_cleanup(tmp_path: Path) -> None:
    child = tmp_path / "shutdown.py"
    started = tmp_path / "started"
    cleaned = tmp_path / "cleaned"
    child.write_text(
        """import json, sys, threading, time
from pathlib import Path
from ds60sqlpy.kubernetes_module import KubernetesWorkerState, install_graceful_stop
from ds60sqlpy.module_worker import WorkerHTTPServer
from ds60sqlpy.worker_operations import OperationResult
started, cleaned = map(Path, sys.argv[1:])
def execute(profile, source, directory, timeout_seconds, cancel, on_status, verifier, **kw):
    on_status('running')
    started.write_text('active')
    if not cancel.wait(10):
        raise RuntimeError('cancel never arrived')
    time.sleep(0.1)
    cleaned.write_text('owned-cleanup confirmed')
    return OperationResult(1, '', False, 'cancelled', 'owned cleanup confirmed', [])
state = KubernetesWorkerState('k8s-kind', scratch_root=started.parent,
                              executor=execute, ready=True, isolate_jobs=False)
server = WorkerHTTPServer(('127.0.0.1', 0), state, 'x' * 64)
restore = install_graceful_stop(server, state)
try:
    state.submit({'job_id': 'b' * 32, 'profile': 'k8s-kind', 'operation': 'execute',
                  'source': 'kind: Deployment', 'language': 'yaml', 'timeout_seconds': 15,
                  'verification_id': None})
    last_status = None
    while not started.exists():
        snapshot = state.get('b' * 32)
        if snapshot['status'] != last_status:
            print('Startup state: ' + json.dumps(snapshot), file=sys.stderr, flush=True)
            last_status = snapshot['status']
        if snapshot['status'] in {'succeeded', 'failed', 'cancelled', 'timed_out'}:
            raise RuntimeError(
                'Synthetic worker ended before its active phase: ' + json.dumps(snapshot)
            )
        time.sleep(0.02)
    server.serve_forever(poll_interval=0.02)
finally:
    server.server_close()
    restore()
assert state.get('b' * 32)['status'] == 'cancelled'
""",
        encoding="utf-8",
    )
    process = subprocess.Popen(
        [sys.executable, str(child), str(started), str(cleaned)],
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    try:
        _wait_for_active_worker(process, started)
        process.send_signal(signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=10)
        assert process.returncode == 0, stdout + stderr
        assert cleaned.read_text() == "owned-cleanup confirmed"
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)


@pytest.mark.parametrize(
    "mode", ["lowercase-absent", "already-absent", "engine-failure", "replacement"]
)
def test_release_uses_successful_exact_listings_not_daemon_error_text(
    tmp_path: Path, mode: str, private_acl: PrivateAclModel
) -> None:
    from ds60sqlpy.kubernetes_module import HostTools, prepare_owned_session, release_owned_session

    host = FakeHost()
    tools = HostTools("kind", "kubectl", "docker")
    session = tmp_path / "private"
    prepare_owned_session(
        session, tools, "unix:///explicit/local.sock", runner=host, owner_id=OWNER
    )
    if mode == "already-absent":
        host.deleted = True

    def runner(argv: list[str], **kwargs: Any) -> CommandResult:
        if "container" in argv and "ls" in argv:
            if mode == "engine-failure":
                return CommandResult(1, "", "connection failed")
            if mode == "replacement":
                return CommandResult(0, "replacement-id\t" + host.cluster + "-control-plane\n")
        if "inspect" in argv and host.deleted:
            return CommandResult(1, "", "error: no such object: control-plane")
        return host(argv, **kwargs)

    if mode in ("engine-failure", "replacement"):
        with pytest.raises(KubernetesRefusal):
            release_owned_session(session, tools, runner=runner)
        assert (session / "worker.kubeconfig.json").exists()
        assert not host.deleted
    else:
        release_owned_session(session, tools, runner=runner)
        release_owned_session(session, tools, runner=runner)
        assert not (session / "worker.kubeconfig.json").exists()
        assert (session / "host-receipt.json").exists()
        assert len([a for a, _, _ in host.calls if "container" in a and "rm" in a]) == (
            0 if mode == "already-absent" else 1
        )


def test_submitted_synthetic_pods_have_one_second_termination_grace(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = FakeCluster(lease)
    result = kubernetes_executor(lease, runner=cluster, stable_seconds=0)(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        threading.Event(),
        lambda _: None,
        "k8s-readiness-v1",
        isolate_user=False,
    )
    assert result.status == "succeeded"
    submitted = [payload for args, payload in cluster.calls if args[0] == "create"]
    templates = [
        item["spec"]["template"]["spec"]
        for item in submitted
        if item and item["kind"] in ("Deployment", "Job")
    ]
    assert len(templates) == 2
    assert all(item["terminationGracePeriodSeconds"] == 1 for item in templates)


def test_cleanup_failure_output_names_the_preserved_resource(
    tmp_path: Path, lease: KubernetesLease
) -> None:
    cluster = FakeCluster(lease)
    cluster.replacement_on_cleanup = True
    result = kubernetes_executor(lease, runner=cluster, stable_seconds=0)(
        "k8s-kind",
        SOURCE.read_text(),
        tmp_path,
        60,
        threading.Event(),
        lambda _: None,
        None,
        isolate_user=False,
    )
    assert result.status == "failed"
    assert "Owned cleanup failed for service/hello:" in result.output
    assert "replacement" in result.output


@pytest.mark.parametrize("phase", ["release", "rollback"])
def test_immutable_node_deletion_preserves_name_replacement_race(
    tmp_path: Path, phase: str, private_acl: PrivateAclModel
) -> None:
    from ds60sqlpy.kubernetes_module import HostTools, prepare_owned_session, release_owned_session

    host = FakeHost()
    original = host.container_id
    replacement = "e" * 64
    tools = HostTools("kind", "kubectl", "docker")
    session = tmp_path / "private"
    armed = phase == "rollback"
    if armed:
        host.fail_token = True

    def runner(argv: list[str], **kwargs: Any) -> CommandResult:
        result = host(argv, **kwargs)
        if armed and phase == "release" and "get" in argv and "namespace" in argv:
            host.container_id = replacement
        if armed and phase == "rollback" and "inspect" in argv and "image" not in argv:
            count = sum("inspect" in a and "image" not in a for a, _, _ in host.calls)
            if count == 2:
                host.container_id = replacement
        return result

    if phase == "release":
        prepare_owned_session(
            session, tools, "unix:///explicit/local.sock", runner=runner, owner_id=OWNER
        )
        armed = True
        with pytest.raises(KubernetesRefusal):
            release_owned_session(session, tools, runner=runner)
        assert (session / "admin.kubeconfig.json").exists()
    else:
        with pytest.raises(KubernetesRefusal):
            prepare_owned_session(
                session, tools, "unix:///explicit/local.sock", runner=runner, owner_id=OWNER
            )
        assert (
            json.loads((session / "preparation-failure.json").read_text())["cleanup_confirmed"]
            is False
        )
    assert host.container_id == replacement and not host.deleted
    removal = [a for a, _, _ in host.calls if "container" in a and "rm" in a]
    assert all(a[-1] == original for a in removal)
    assert not any(a[:3] == ["kind", "delete", "cluster"] for a, _, _ in host.calls)


@pytest.mark.parametrize("tag", [0xA0000003, 0xA000000C])
def test_python311_reparse_ancestors_are_refused_before_any_host_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tag: int
) -> None:
    from types import SimpleNamespace

    from ds60sqlpy.kubernetes_module import HostTools, _private_file, prepare_owned_session

    ancestor = tmp_path / "redirect"
    ancestor.mkdir()
    original = Path.lstat

    def information(path: Path) -> Any:
        if path == ancestor:
            return SimpleNamespace(st_mode=0o40700, st_reparse_tag=tag)
        return original(path)

    monkeypatch.setattr(Path, "lstat", information)
    host = FakeHost()
    with pytest.raises(KubernetesRefusal, match="ancestors"):
        prepare_owned_session(
            ancestor / "private",
            HostTools("kind", "kubectl", "docker"),
            "unix:///explicit/local.sock",
            runner=host,
            owner_id=OWNER,
        )
    with pytest.raises(KubernetesRefusal, match="symlink components"):
        _private_file(ancestor / "token", 100)
    assert not host.calls


def test_private_file_rejects_resolved_portable_state_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy.kubernetes_module import _private_file

    path = tmp_path / "ordinary" / "token"
    original = Path.resolve

    def resolved(item: Path, strict: bool = False) -> Path:
        if item == path:
            return tmp_path / ".learning" / "token"
        return original(item, strict=strict)

    monkeypatch.setattr(Path, "resolve", resolved)
    with pytest.raises(KubernetesRefusal, match="symlink components"):
        _private_file(path, 100)


@pytest.mark.parametrize("empty_shape", [None, []])
def test_empty_nullable_endpoint_slice_is_unhealthy_not_an_api_error(
    tmp_path: Path, lease: KubernetesLease, empty_shape: Any
) -> None:
    cluster = FakeCluster(lease)

    def runner(argv: list[str], **kwargs: Any) -> CommandResult:
        response = cluster(argv, **kwargs)
        args = argv[argv.index("--request-timeout=5s") + 1 :]
        if args[:2] == ["get", "endpointslices"]:
            value = json.loads(response.stdout)
            for item in value["items"]:
                item["endpoints"] = empty_shape
            return CommandResult(0, json.dumps(value))
        return response

    client = KubectlClient(lease, tmp_path, runner=runner, isolate_user=False)
    deadline = time.monotonic() + 5
    event = threading.Event()
    uids = []
    for document in parse_manifests(SOURCE.read_text()):
        document["metadata"].setdefault("labels", {})[OWNER_LABEL] = OWNER
        uids.append(client.apply(document, deadline, event)["metadata"]["uid"])
    healthy, evidence = observe_ready(client, uids[0], 2, uids[1], deadline, event)
    assert not healthy
    assert evidence["ready_endpoint_uids"] == []
    assert len(evidence["ready_pod_uids"]) == 2


def test_nullable_controller_status_stays_unhealthy(tmp_path: Path, lease: KubernetesLease) -> None:
    cluster = FakeCluster(lease)
    client = KubectlClient(lease, tmp_path, runner=cluster, isolate_user=False)
    deadline = time.monotonic() + 5
    event = threading.Event()
    document = parse_manifests(SOURCE.read_text())[0]
    document["metadata"].setdefault("labels", {})[OWNER_LABEL] = OWNER
    uid = client.apply(document, deadline, event)["metadata"]["uid"]
    cluster.objects[("deployment", "hello")]["status"] = {
        "observedGeneration": None,
        "readyReplicas": None,
    }
    healthy, _ = observe_ready(client, uid, 2, None, deadline, event)
    assert not healthy


@pytest.mark.parametrize("returncode", [0, 1, 2, 3])
def test_windows_acl_command_keeps_paths_as_data_and_refuses_failed_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, returncode: int
) -> None:
    from ds60sqlpy import kubernetes_module

    monkeypatch.setenv("SYSTEMROOT", r"C:\Windows")
    path = tmp_path / "runtime with spaces ' and ; punctuation"
    calls: list[tuple[list[str], dict[str, Any]]] = []
    monkeypatch.setenv("DS60_WORKER_TOKEN", "synthetic-private-value")
    monkeypatch.setenv("KUBECONFIG", "synthetic-private-config")

    def run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, returncode)

    monkeypatch.setattr("ds60sqlpy.kubernetes_module.subprocess.run", run)
    assert kubernetes_module._windows_private_acl(path, establish=True) is (returncode == 0)
    argv, options = calls[0]
    assert argv[:5] == [
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
    ]
    assert str(path) not in argv[-1]
    # The bounded helper must not reintroduce cmdlet module discovery before
    # reaching the ACL policy. Real policy behavior is covered by the native smoke.
    assert not any(cmdlet in argv[-1] for cmdlet in ("New-Object", "Get-Acl", "Set-Acl"))
    assert options["env"]["DS60_PRIVATE_PATH"] == str(path)
    assert options["env"]["DS60_PRIVATE_ESTABLISH"] == "1"
    assert not {"DS60_WORKER_TOKEN", "KUBECONFIG"} & options["env"].keys()
    assert options["timeout"] == 15
    assert options["stdin"] == options["stdout"] == options["stderr"] == subprocess.DEVNULL


@pytest.mark.parametrize(
    "error", [OSError("unavailable"), subprocess.TimeoutExpired("fixture", 15)]
)
def test_windows_acl_command_failure_never_establishes_trust(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    from ds60sqlpy import kubernetes_module

    monkeypatch.setenv("SYSTEMROOT", r"C:\Windows")

    def failed(*args: Any, **kwargs: Any) -> Any:
        raise error

    monkeypatch.setattr("ds60sqlpy.kubernetes_module.subprocess.run", failed)
    assert kubernetes_module._windows_private_acl(tmp_path) is False


def test_windows_acl_runtime_preserves_startup_directories_but_not_hooks_or_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ds60sqlpy.kubernetes_module import _windows_powershell_runtime

    monkeypatch.setenv("SYSTEMROOT", r"C:\Windows")
    for name in ("TMP", "TEMP", "USERPROFILE", "LOCALAPPDATA", "APPDATA", "PROGRAMFILES"):
        monkeypatch.setenv(name, "synthetic-" + name)
    for name in ("PSModulePath", "PSExecutionPolicyPreference", "KUBECONFIG", "HTTP_PROXY"):
        monkeypatch.setenv(name, "must-not-be-inherited")
    monkeypatch.setenv("PATH", r"C:\untrusted-tools")
    executable, environment = _windows_powershell_runtime()
    assert executable == r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    for name in ("TMP", "TEMP", "USERPROFILE", "LOCALAPPDATA", "APPDATA", "PROGRAMFILES"):
        assert environment[name] == "synthetic-" + name
    assert (
        not {"PSModulePath", "PSExecutionPolicyPreference", "KUBECONFIG", "HTTP_PROXY"}
        & environment.keys()
    )
    assert "untrusted-tools" not in environment["PATH"]
    assert environment["PATH"].split(";") == [
        r"C:\Windows\System32\WindowsPowerShell\v1.0",
        r"C:\Windows\System32",
        r"C:\Windows",
    ]


@pytest.mark.parametrize("root", ["", "relative", r"\\server\windows", r"C:Windows"])
def test_windows_acl_runtime_refuses_missing_or_nonlocal_system_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, root: str
) -> None:
    from ds60sqlpy import kubernetes_module

    monkeypatch.delenv("WINDIR", raising=False)
    monkeypatch.setenv("SYSTEMROOT", root)

    def unexpected(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No PATH fallback may run without a trusted system directory")

    monkeypatch.setattr("ds60sqlpy.kubernetes_module.subprocess.run", unexpected)
    assert kubernetes_module._windows_private_acl(tmp_path) is False
