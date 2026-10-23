"""Owned, one-shot Kubernetes learning operations with no ambient cluster fallback.

Learner YAML is data for a narrow Deployment/Service allowlist. It is never a
shell program, kubeconfig, context selector, image command or host mount request.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import hashlib
import json
import os
import re
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ds60sqlpy.module_worker import WorkerHTTPServer, WorkerState
from ds60sqlpy.worker_operations import OperationResult

FIXTURE_IMAGE = "ds60sqlpy-k8s-fixture:0.1.0"
FIXTURE_VERSION = "ds60-fixture-v1"
OWNER_LABEL = "learning.ds60sqlpy/owner"
JOB_LABEL = "learning.ds60sqlpy/job"
RESOURCE_NAME = "hello"
KIND_VERSION = "v0.33.0"
KUBECTL_VERSION = "v1.37.0"
NODE_IMAGE = (
    "kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5"
)
MAX_SOURCE_BYTES = 48_000
MAX_COMMAND_BYTES = 262_144
CLEANUP_SECONDS = 15.0
READINESS_WINDOW = 120.0 + CLEANUP_SECONDS + 5.0
NAME = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
OWNER = re.compile(r"[0-9a-f]{32}\Z")


class KubernetesRefusal(ValueError):
    """A boundary, identity or readiness condition was not established."""


class InterruptedOperation(RuntimeError):
    def __init__(self, status: str) -> None:
        super().__init__(status)
        self.status = status


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise KubernetesRefusal(f"{name} must be a string-keyed mapping.")
    return value


def _fields(value: dict[str, Any], allowed: set[str], required: set[str], name: str) -> None:
    if set(value) - allowed or not required <= set(value):
        raise KubernetesRefusal(f"{name} contains missing or unsupported fields.")


def _integer(value: Any, low: int, high: int, name: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise KubernetesRefusal(f"{name} must be an integer between {low} and {high}.")
    return value


def _labels(value: Any, name: str, *, expected: str | None = None) -> dict[str, str]:
    result = _mapping(value, name)
    if (
        set(result) != {"app"}
        or not isinstance(result["app"], str)
        or not NAME.fullmatch(result["app"])
    ):
        raise KubernetesRefusal(f"{name} must contain only one bounded app label.")
    if expected is not None and result["app"] != expected:
        raise KubernetesRefusal(f"{name} must select the fixed hello application.")
    return result


def _security(pod: dict[str, Any], container: dict[str, Any]) -> None:
    expected_pod = {
        "runAsNonRoot": True,
        "runAsUser": 65532,
        "seccompProfile": {"type": "RuntimeDefault"},
    }
    expected_container = {
        "allowPrivilegeEscalation": False,
        "readOnlyRootFilesystem": True,
        "capabilities": {"drop": ["ALL"]},
    }
    if pod.get("automountServiceAccountToken") is not False:
        raise KubernetesRefusal("Workload token mounting must be disabled.")
    if (
        pod.get("securityContext") != expected_pod
        or container.get("securityContext") != expected_container
    ):
        raise KubernetesRefusal(
            "Use the fixed nonroot, read-only, no-capabilities workload identity."
        )


def _resource_limits(value: Any) -> None:
    resources = _mapping(value, "resources")
    _fields(resources, {"requests", "limits"}, {"requests", "limits"}, "resources")
    parsed: dict[str, dict[str, int]] = {}
    for group in ("requests", "limits"):
        values = _mapping(resources[group], group)
        _fields(values, {"cpu", "memory"}, {"cpu", "memory"}, group)
        parsed[group] = {}
        for key, suffix, maximum in (("cpu", "m", 250), ("memory", "Mi", 128)):
            raw = values[key]
            if (
                not isinstance(raw, str)
                or len(raw) > 12
                or not re.fullmatch(r"[1-9][0-9]*" + suffix, raw)
            ):
                raise KubernetesRefusal("Use positive bounded millicores and Mi memory quantities.")
            number = int(raw[: -len(suffix)])
            if number > maximum:
                raise KubernetesRefusal("The lesson exceeds its CPU or memory resource cap.")
            parsed[group][key] = number
    if any(parsed["requests"][key] > parsed["limits"][key] for key in ("cpu", "memory")):
        raise KubernetesRefusal("Resource requests cannot exceed limits.")


def parse_manifests(source: str) -> list[dict[str, Any]]:
    """Reject aliases, duplicate keys, unknown fields and arbitrary workload execution."""
    if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise KubernetesRefusal("The manifest must contain at most48000 UTF-8 bytes.")
    try:
        import yaml  # type: ignore[import-untyped]  # Optional, pinned worker-only parser.
    except ImportError as exc:
        raise KubernetesRefusal(
            "The prepared Kubernetes worker needs its pinned YAML parser."
        ) from exc

    class StrictLoader(yaml.SafeLoader):  # type: ignore[misc]
        depth = 0
        count = 0

        def compose_node(self, parent: Any, index: Any) -> Any:
            if self.check_event(yaml.AliasEvent):
                raise KubernetesRefusal("YAML aliases are not supported.")
            self.depth += 1
            self.count += 1
            if self.depth > 24 or self.count > 2000:
                raise KubernetesRefusal("The YAML nesting or node budget is exceeded.")
            try:
                return super().compose_node(parent, index)
            finally:
                self.depth -= 1

        def construct_mapping(self, node: Any, deep: bool = False) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                if not isinstance(key, str) or key in result:
                    raise KubernetesRefusal("YAML mapping keys must be unique strings.")
                result[key] = self.construct_object(value_node, deep=deep)
            return result

    try:
        documents = list(yaml.load_all(source, Loader=StrictLoader))
    except yaml.YAMLError as exc:
        raise KubernetesRefusal("The lesson contains invalid YAML.") from exc
    if not 1 <= len(documents) <= 2:
        raise KubernetesRefusal("Supply one Deployment and at most one Service.")
    kinds: set[str] = set()
    for document in documents:
        doc = _mapping(document, "manifest")
        _fields(
            doc,
            {"apiVersion", "kind", "metadata", "spec"},
            {"apiVersion", "kind", "metadata", "spec"},
            "manifest",
        )
        kind = doc["kind"]
        if kind not in ("Deployment", "Service") or kind in kinds:
            raise KubernetesRefusal(
                "Only one hello Deployment and one hello Service are supported."
            )
        kinds.add(kind)
        meta = _mapping(doc["metadata"], "metadata")
        _fields(meta, {"name", "labels"}, {"name"}, "metadata")
        if meta["name"] != RESOURCE_NAME:
            raise KubernetesRefusal("The operation owns only the fixed resource name hello.")
        if "labels" in meta:
            _labels(meta["labels"], "metadata.labels", expected="hello")
        spec = _mapping(doc["spec"], "spec")
        if kind == "Service":
            if doc["apiVersion"] != "v1":
                raise KubernetesRefusal("The Service API version must be v1.")
            _fields(spec, {"selector", "ports"}, {"selector", "ports"}, "Service spec")
            _labels(spec["selector"], "Service selector")
            if spec["ports"] != [{"name": "http", "port": 8080, "targetPort": "http"}]:
                raise KubernetesRefusal("The Service must expose only its fixed8080 named port.")
            continue
        if doc["apiVersion"] != "apps/v1":
            raise KubernetesRefusal("The Deployment API version must be apps/v1.")
        _fields(
            spec,
            {"replicas", "selector", "template", "strategy"},
            {"replicas", "selector", "template"},
            "Deployment spec",
        )
        _integer(spec["replicas"], 1, 2, "replicas")
        if spec.get("strategy", {"type": "RollingUpdate"}) not in (
            {"type": "RollingUpdate"},
            {"type": "Recreate"},
        ):
            raise KubernetesRefusal("The optional strategy must be RollingUpdate or Recreate.")
        if spec["selector"] != {"matchLabels": {"app": "hello"}}:
            raise KubernetesRefusal("The Deployment selector must match app hello.")
        template = _mapping(spec["template"], "template")
        _fields(template, {"metadata", "spec"}, {"metadata", "spec"}, "template")
        if template["metadata"] != {"labels": {"app": "hello"}}:
            raise KubernetesRefusal("The Pod template must contain only its fixed app label.")
        pod = _mapping(template["spec"], "Pod spec")
        _fields(
            pod,
            {"automountServiceAccountToken", "securityContext", "containers"},
            {"automountServiceAccountToken", "securityContext", "containers"},
            "Pod spec",
        )
        if not isinstance(pod["containers"], list) or len(pod["containers"]) != 1:
            raise KubernetesRefusal("Exactly one fixed fixture container is supported.")
        container = _mapping(pod["containers"][0], "container")
        _fields(
            container,
            {
                "name",
                "image",
                "imagePullPolicy",
                "command",
                "ports",
                "readinessProbe",
                "resources",
                "securityContext",
            },
            {
                "name",
                "image",
                "imagePullPolicy",
                "command",
                "ports",
                "readinessProbe",
                "resources",
                "securityContext",
            },
            "container",
        )
        if container["name"] not in ("app", "hello") or container["image"] != FIXTURE_IMAGE:
            raise KubernetesRefusal("Use the approved local hello fixture container.")
        if container["imagePullPolicy"] != "Never" or container["command"] != [
            "python",
            "/fixture.py",
            "server",
        ]:
            raise KubernetesRefusal("Only the fixed offline fixture server command is allowed.")
        if container["ports"] != [{"name": "http", "containerPort": 8080}]:
            raise KubernetesRefusal("The fixture declares only its named8080 container port.")
        probe = _mapping(container["readinessProbe"], "readinessProbe")
        _fields(
            probe,
            {"httpGet", "periodSeconds", "failureThreshold"},
            {"httpGet", "periodSeconds", "failureThreshold"},
            "readinessProbe",
        )
        if probe["httpGet"] not in (
            {"path": "/ready", "port": "http"},
            {"path": "/missing", "port": "http"},
        ):
            raise KubernetesRefusal("The readiness probe may select only /ready or /missing.")
        _integer(probe["periodSeconds"], 1, 5, "probe period")
        _integer(probe["failureThreshold"], 1, 3, "probe failure threshold")
        _security(pod, container)
        _resource_limits(container["resources"])
    if "Deployment" not in kinds:
        raise KubernetesRefusal("Include the hello Deployment, not a Service alone.")
    return documents


def _windows_private_acl(path: Path, *, establish: bool = False) -> bool:
    # The path is data in one process-local environment variable, never interpolated
    # into PowerShell source. Only a newly created runtime directory is modified.
    script = r"""
$ErrorActionPreference='Stop'
$p=$env:DS60_PRIVATE_PATH
$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
$system=New-Object Security.Principal.SecurityIdentifier('S-1-5-18')
if($env:DS60_PRIVATE_ESTABLISH -eq '1') {
  $acl=New-Object Security.AccessControl.DirectorySecurity
  $acl.SetAccessRuleProtection($true,$false)
  $acl.SetOwner($sid)
  foreach($who in @($sid,$system)) {
    $values=@($who,'FullControl','ContainerInherit,ObjectInherit','None','Allow')
    $rule=New-Object Security.AccessControl.FileSystemAccessRule -ArgumentList $values
    $acl.AddAccessRule($rule)
  }
  Set-Acl -LiteralPath $p -AclObject $acl
}
$observed=Get-Acl -LiteralPath $p
$rules=@($observed.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]))
$owner=$observed.GetOwner([Security.Principal.SecurityIdentifier]).Value
if($owner -ne $sid.Value -or $rules.Count -eq 0){exit 2}
foreach($rule in $rules) {
  $other=($rule.IdentityReference.Value -notin @($sid.Value,$system.Value))
  if($rule.AccessControlType -eq 'Allow' -and $other){exit 3}
}
exit 0
"""
    environment = {
        key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR") if key in os.environ
    }
    environment.update(
        DS60_PRIVATE_PATH=str(path), DS60_PRIVATE_ESTABLISH="1" if establish else "0"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _private_file(path: Path, maximum: int) -> bytes:
    absolute = path.absolute()
    if any(part.casefold() == ".learning" for part in absolute.parts) or any(
        part.is_symlink() or getattr(part, "is_junction", lambda: False)()
        for part in (absolute, *absolute.parents)
    ):
        raise KubernetesRefusal(
            "Credentials must be external private files without symlink components."
        )
    info = absolute.stat()
    windows_private = os.name == "nt" and _windows_private_acl(absolute)
    protected_parent = (
        sys.platform == "linux"
        and os.geteuid() == 0
        and any(
            part.stat().st_uid == 0 and stat.S_IMODE(part.stat().st_mode) == 0o700
            for part in absolute.parents
        )
    )
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_size > maximum
        or (stat.S_IMODE(info.st_mode) & 0o077 and not protected_parent and not windows_private)
    ):
        raise KubernetesRefusal(
            "A bounded private runtime file or protected root-owned image directory is required."
        )
    return absolute.read_bytes()


@dataclass(frozen=True)
class KubernetesLease:
    owner_id: str
    cluster_name: str
    context: str
    namespace: str
    namespace_uid: str
    expires_at: float
    ca_sha256: str
    kubeconfig: bytes

    @classmethod
    def load(cls, path: Path, *, now: float | None = None) -> KubernetesLease:
        payload = json.loads(_private_file(path, 16_384))
        required = {
            "schema_version",
            "owner_id",
            "cluster_name",
            "context",
            "namespace",
            "namespace_uid",
            "expires_at",
            "ca_sha256",
            "kubeconfig_file",
            "fixture_image",
        }
        if (
            not isinstance(payload, dict)
            or set(payload) != required
            or type(payload["schema_version"]) is not int
            or payload["schema_version"] != 1
        ):
            raise KubernetesRefusal("Unsupported private Kubernetes lease.")
        for key in (
            "owner_id",
            "cluster_name",
            "context",
            "namespace",
            "namespace_uid",
            "ca_sha256",
            "kubeconfig_file",
            "expires_at",
        ):
            if not isinstance(payload[key], str) or not payload[key]:
                raise KubernetesRefusal("Lease identity fields must be nonempty strings.")
        owner = payload["owner_id"]
        if not OWNER.fullmatch(owner) or payload["cluster_name"] != "ds60-" + owner[:12]:
            raise KubernetesRefusal("The cluster must match its unique course ownership identity.")
        if (
            payload["namespace"] != "ds60-lesson-" + owner[:12]
            or payload["context"] != "ds60-owned"
        ):
            raise KubernetesRefusal("Use only the fixed owned lesson namespace/context.")
        if not re.fullmatch(r"[A-Za-z0-9-]{1,100}", payload["namespace_uid"]):
            raise KubernetesRefusal("The namespace UID is malformed.")
        if (
            payload["fixture_image"] != FIXTURE_IMAGE
            or payload["kubeconfig_file"] != "worker.kubeconfig.json"
        ):
            raise KubernetesRefusal(
                "The lease must bind the fixed fixture and private kubeconfig file."
            )
        if not re.fullmatch(r"[0-9a-f]{64}", payload["ca_sha256"]):
            raise KubernetesRefusal("The lease must record the exact cluster CA identity.")
        try:
            expiry = datetime.fromisoformat(payload["expires_at"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise KubernetesRefusal("Lease expiry must be an explicit UTC instant.") from exc
        if expiry.tzinfo is None or expiry.utcoffset() != UTC.utcoffset(expiry):
            raise KubernetesRefusal("Lease expiry must use UTC.")
        timestamp = expiry.timestamp()
        if timestamp <= (time.time() if now is None else now):
            raise KubernetesRefusal(
                "The Kubernetes lease has expired; prepare a new scoped session."
            )
        config = _private_file(path.parent / "worker.kubeconfig.json", 262_144)
        parsed = json.loads(config)
        _validate_kubeconfig(parsed, payload)
        return cls(
            owner,
            payload["cluster_name"],
            payload["context"],
            payload["namespace"],
            payload["namespace_uid"],
            timestamp,
            payload["ca_sha256"],
            config,
        )


def _validate_kubeconfig(config: Any, lease: dict[str, Any]) -> None:
    data = _mapping(config, "kubeconfig")
    _fields(
        data,
        {"apiVersion", "kind", "clusters", "contexts", "users", "current-context"},
        {"apiVersion", "kind", "clusters", "contexts", "users", "current-context"},
        "kubeconfig",
    )
    if (
        data["apiVersion"] != "v1"
        or data["kind"] != "Config"
        or data["current-context"] != "ds60-owned"
    ):
        raise KubernetesRefusal("The kubeconfig must use only its fixed explicit context.")
    for key in ("clusters", "contexts", "users"):
        if not isinstance(data[key], list) or len(data[key]) != 1:
            raise KubernetesRefusal("The kubeconfig must contain exactly one cluster/context/user.")
    cluster_entry = _mapping(data["clusters"][0], "cluster entry")
    user_entry = _mapping(data["users"][0], "user entry")
    context_entry = _mapping(data["contexts"][0], "context entry")
    if set(cluster_entry) != {"name", "cluster"} or cluster_entry["name"] != "ds60":
        raise KubernetesRefusal("Unexpected kubeconfig cluster alias.")
    cluster = _mapping(cluster_entry["cluster"], "cluster")
    if set(cluster) != {"server", "certificate-authority-data"}:
        raise KubernetesRefusal(
            "Kubeconfig plugins, proxy and insecure TLS overrides are forbidden."
        )
    if cluster["server"] != "https://" + lease["cluster_name"] + "-control-plane:6443":
        raise KubernetesRefusal(
            "The worker endpoint must be the owned internal kind control plane."
        )
    try:
        ca = base64.b64decode(cluster["certificate-authority-data"], validate=True)
    except (ValueError, TypeError) as exc:
        raise KubernetesRefusal("The cluster CA must be embedded base64 data.") from exc
    if not ca or hashlib.sha256(ca).hexdigest() != lease["ca_sha256"]:
        raise KubernetesRefusal("The cluster CA does not match the owned receipt.")
    if set(user_entry) != {"name", "user"} or user_entry["name"] != "scoped":
        raise KubernetesRefusal("Unexpected kubeconfig user alias.")
    user = _mapping(user_entry["user"], "user")
    token = user.get("token")
    if (
        set(user) != {"token"}
        or not isinstance(token, str)
        or not 32 <= len(token) <= 16_384
        or any(ord(char) < 33 or ord(char) > 126 for char in token)
    ):
        raise KubernetesRefusal("Use only a bounded short-lived scoped bearer token.")
    expected = {
        "name": "ds60-owned",
        "context": {"cluster": "ds60", "user": "scoped", "namespace": lease["namespace"]},
    }
    if context_entry != expected:
        raise KubernetesRefusal("Kubeconfig context must bind the exact owned namespace.")


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str = ""


def _stop(process: subprocess.Popen[bytes]) -> None:
    if os.name == "posix":
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
    else:
        process.kill()
    with contextlib.suppress(subprocess.TimeoutExpired):
        process.wait(timeout=2)


def run_kubectl(
    argv: list[str],
    *,
    input_data: bytes | None,
    deadline: float,
    cancel: threading.Event,
    directory: Path,
    isolate_user: bool,
) -> CommandResult:
    """Run fixed argv with a separate credential-only UID and bounded pipe capture."""
    environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(directory),
        "TMPDIR": str(directory),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GOMAXPROCS": "2",
    }
    command = argv
    if isolate_user:
        if sys.platform != "linux" or os.geteuid() != 0:
            raise KubernetesRefusal(
                "Prepared Kubernetes workers require the Linux credential supervisor."
            )
        wrapper = (
            "import os,sys;os.setgroups([]);os.setgid(65533);os.setuid(65533);"
            "os.execvpe(sys.argv[1],sys.argv[1:],os.environ)"
        )
        command = [sys.executable, "-c", wrapper, *argv]
    if cancel.is_set():
        raise InterruptedOperation("cancelled")
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise InterruptedOperation("timed_out")
    process = subprocess.Popen(
        command,
        cwd=directory,
        env=environment,
        stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=os.name == "posix",
    )
    captured = [bytearray(), bytearray()]
    exceeded = threading.Event()

    def drain(pipe: Any, index: int) -> None:
        try:
            while chunk := pipe.read(8192):
                if len(captured[index]) + len(chunk) > MAX_COMMAND_BYTES:
                    exceeded.set()
                missing = MAX_COMMAND_BYTES - len(captured[index])
                captured[index].extend(chunk[: max(0, missing)])
        finally:
            pipe.close()

    readers = [
        threading.Thread(target=drain, args=(process.stdout, 0), daemon=True),
        threading.Thread(target=drain, args=(process.stderr, 1), daemon=True),
    ]
    for reader in readers:
        reader.start()
    try:
        if input_data is not None:
            assert process.stdin is not None
            process.stdin.write(input_data)
            process.stdin.close()
        while process.poll() is None:
            if cancel.is_set():
                raise InterruptedOperation("cancelled")
            if time.monotonic() >= deadline:
                raise InterruptedOperation("timed_out")
            if exceeded.is_set():
                raise KubernetesRefusal("Kubectl output exceeded its bounded receipt budget.")
            cancel.wait(0.03)
    finally:
        _stop(process)
        for reader in readers:
            reader.join(timeout=2)
    if exceeded.is_set():
        raise KubernetesRefusal("Kubectl output exceeded its bounded receipt budget.")
    return CommandResult(
        process.returncode,
        captured[0].decode("utf-8", errors="replace"),
        captured[1].decode("utf-8", errors="replace"),
    )


class KubectlClient:
    def __init__(
        self,
        lease: KubernetesLease,
        directory: Path,
        *,
        executable: str = "/usr/local/bin/kubectl",
        isolate_user: bool = True,
        runner: Callable[..., CommandResult] = run_kubectl,
    ) -> None:
        self.lease = lease
        self.directory = directory
        self.isolate_user = isolate_user
        self.runner = runner
        self.executable = executable
        self.config = directory / "scoped.kubeconfig.json"
        self.config.write_bytes(lease.kubeconfig)
        self.config.chmod(0o600)
        if isolate_user:
            os.chown(directory, 65533, 65533)
            os.chown(self.config, 65533, 65533)

    def call(
        self,
        arguments: list[str],
        deadline: float,
        cancel: threading.Event,
        *,
        payload: dict[str, Any] | None = None,
        missing_ok: bool = False,
    ) -> dict[str, Any]:
        if cancel.is_set():
            raise InterruptedOperation("cancelled")
        if time.monotonic() >= deadline:
            raise InterruptedOperation("timed_out")
        if time.time() >= self.lease.expires_at:
            raise KubernetesRefusal("The scoped Kubernetes lease expired during the operation.")
        argv = [
            self.executable,
            "--kubeconfig",
            str(self.config),
            "--context",
            self.lease.context,
            "--namespace",
            self.lease.namespace,
            "--request-timeout=5s",
            *arguments,
        ]
        body = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
        result = self.runner(
            argv,
            input_data=body,
            deadline=deadline,
            cancel=cancel,
            directory=self.directory,
            isolate_user=self.isolate_user,
        )
        if result.returncode:
            if missing_ok and "NotFound" in result.stderr:
                return {}
            raise KubernetesRefusal(
                "The scoped Kubernetes API request failed; inspect the owned host "
                "lease and resource conditions."
            )
        if not result.stdout.strip():
            return {}
        try:
            value = json.loads(result.stdout)
        except ValueError as exc:
            raise KubernetesRefusal("Kubectl returned an invalid structured response.") from exc
        return _mapping(value, "API response")

    def namespace(self, deadline: float, cancel: threading.Event) -> None:
        value = self.call(
            ["get", "namespace", self.lease.namespace, "-o", "json"], deadline, cancel
        )
        meta = _mapping(value.get("metadata"), "namespace metadata")
        if (
            meta.get("uid") != self.lease.namespace_uid
            or meta.get("labels", {}).get(OWNER_LABEL) != self.lease.owner_id
        ):
            raise KubernetesRefusal(
                "The namespace identity or ownership marker changed; no mutation is authorized."
            )

    def apply(
        self, document: dict[str, Any], deadline: float, cancel: threading.Event
    ) -> dict[str, Any]:
        self.namespace(deadline, cancel)
        return self.call(["create", "-f", "-", "-o", "json"], deadline, cancel, payload=document)

    def cleanup(
        self,
        kind: str,
        name: str,
        uid: str,
        deadline: float,
        cancel: threading.Event,
        *,
        job_nonce: str | None = None,
    ) -> None:
        self.namespace(deadline, cancel)
        current = self.call(["get", kind, name, "-o", "json"], deadline, cancel, missing_ok=True)
        if not current:
            return
        meta = _mapping(current.get("metadata"), "cleanup metadata")
        if (
            meta.get("uid") != uid
            or meta.get("labels", {}).get(OWNER_LABEL) != self.lease.owner_id
            or (job_nonce is not None and meta.get("labels", {}).get(JOB_LABEL) != job_nonce)
        ):
            raise KubernetesRefusal(
                "Cleanup identity changed; refusing deletion of a replacement or unrelated object."
            )
        # UID preconditions make the comparison atomic at the API deletion boundary.
        roots = {"deployment": "/apis/apps/v1", "service": "/api/v1", "job": "/apis/batch/v1"}
        plurals = {"deployment": "deployments", "service": "services", "job": "jobs"}
        if kind not in roots or name not in ("hello", "hello-check"):
            raise KubernetesRefusal("Unsupported owned cleanup resource.")
        uri = roots[kind] + "/namespaces/" + self.lease.namespace + "/" + plurals[kind] + "/" + name
        options = {
            "apiVersion": "v1",
            "kind": "DeleteOptions",
            "preconditions": {"uid": uid},
            "propagationPolicy": "Foreground",
            "gracePeriodSeconds": 1,
        }
        self.call(["delete", "--raw", uri, "-f", "-"], deadline, cancel, payload=options)
        while True:
            remaining = self.call(
                ["get", kind, name, "-o", "json"], deadline, cancel, missing_ok=True
            )
            if not remaining:
                return
            if remaining.get("metadata", {}).get("uid") != uid:
                raise KubernetesRefusal("A replacement appeared during cleanup; it is preserved.")
            if cancel.is_set():
                raise InterruptedOperation("cancelled")
            if time.monotonic() >= deadline:
                raise InterruptedOperation("timed_out")
            cancel.wait(0.1)


def _metadata(value: dict[str, Any], lease: KubernetesLease, *, name: str) -> dict[str, Any]:
    meta = _mapping(value.get("metadata"), "resource metadata")
    if (
        meta.get("name") != name
        or meta.get("namespace") != lease.namespace
        or not isinstance(meta.get("uid"), str)
        or not meta["uid"]
        or meta.get("labels", {}).get(OWNER_LABEL) != lease.owner_id
    ):
        raise KubernetesRefusal("The API resource identity or ownership receipt does not match.")
    return meta


def observe_ready(
    client: KubectlClient,
    deployment_uid: str,
    desired: int,
    service_uid: str | None,
    deadline: float,
    cancel: threading.Event,
) -> tuple[bool, dict[str, Any]]:
    """Relate controller, Pod and endpoint identities; counts alone are insufficient."""
    client.namespace(deadline, cancel)
    deployment = client.call(["get", "deployment", "hello", "-o", "json"], deadline, cancel)
    meta = _metadata(deployment, client.lease, name="hello")
    if meta["uid"] != deployment_uid:
        raise KubernetesRefusal("The Deployment was replaced during observation.")
    status = _mapping(deployment.get("status", {}), "Deployment status")
    generation = meta.get("generation")
    converged = (
        type(generation) is int
        and status.get("observedGeneration", -1) >= generation
        and all(
            status.get(field, 0) == desired
            for field in ("updatedReplicas", "readyReplicas", "availableReplicas")
        )
    )
    selector = "app=hello," + OWNER_LABEL + "=" + client.lease.owner_id
    replica_sets = client.call(
        ["get", "replicasets", "-l", selector, "-o", "json"], deadline, cancel
    )
    rs_ids = {
        item.get("metadata", {}).get("uid")
        for item in replica_sets.get("items", [])
        if any(
            ref.get("uid") == deployment_uid and ref.get("controller") is True
            for ref in item.get("metadata", {}).get("ownerReferences", [])
        )
    }
    pods = client.call(["get", "pods", "-l", selector, "-o", "json"], deadline, cancel)
    ready_ids: set[str] = set()
    for pod in pods.get("items", []):
        info = pod.get("metadata", {})
        if info.get("deletionTimestamp"):
            continue
        if (
            info.get("labels", {}).get(OWNER_LABEL) == client.lease.owner_id
            and any(
                ref.get("uid") in rs_ids and ref.get("controller") is True
                for ref in info.get("ownerReferences", [])
            )
            and any(
                condition.get("type") == "Ready" and condition.get("status") == "True"
                for condition in pod.get("status", {}).get("conditions", [])
            )
        ):
            ready_ids.add(info["uid"])
    endpoints: set[str] = set()
    if service_uid is not None:
        service = client.call(["get", "service", "hello", "-o", "json"], deadline, cancel)
        service_meta = _metadata(service, client.lease, name="hello")
        if service_meta["uid"] != service_uid:
            raise KubernetesRefusal("The Service was replaced during observation.")
        slices = client.call(
            ["get", "endpointslices", "-l", "kubernetes.io/service-name=hello", "-o", "json"],
            deadline,
            cancel,
        )
        for item in slices.get("items", []):
            if not any(
                ref.get("uid") == service_uid and ref.get("controller") is True
                for ref in item.get("metadata", {}).get("ownerReferences", [])
            ):
                continue
            for endpoint in item.get("endpoints", []):
                target = endpoint.get("targetRef", {})
                if (
                    endpoint.get("conditions", {}).get("ready") is True
                    and target.get("kind") == "Pod"
                    and target.get("namespace", client.lease.namespace) == client.lease.namespace
                    and isinstance(target.get("uid"), str)
                ):
                    endpoints.add(target["uid"])
    healthy = converged and len(ready_ids) == desired
    if service_uid is not None:
        healthy = healthy and endpoints == ready_ids
    return healthy, {
        "desired": desired,
        "ready_pod_uids": sorted(ready_ids),
        "ready_endpoint_uids": sorted(endpoints),
        "controller_converged": converged,
    }


def _client_job(owner: str) -> dict[str, Any]:
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": "hello-check", "labels": {OWNER_LABEL: owner}},
        "spec": {
            "backoffLimit": 0,
            "activeDeadlineSeconds": 8,
            "template": {
                "metadata": {"labels": {OWNER_LABEL: owner}},
                "spec": {
                    "restartPolicy": "Never",
                    "automountServiceAccountToken": False,
                    "securityContext": {
                        "runAsNonRoot": True,
                        "runAsUser": 65532,
                        "seccompProfile": {"type": "RuntimeDefault"},
                    },
                    "containers": [
                        {
                            "name": "check",
                            "image": FIXTURE_IMAGE,
                            "imagePullPolicy": "Never",
                            "command": [
                                "python",
                                "/fixture.py",
                                "client",
                                "--url",
                                "http://hello:8080/version",
                                "--expect",
                                FIXTURE_VERSION,
                            ],
                            "resources": {
                                "requests": {"cpu": "10m", "memory": "16Mi"},
                                "limits": {"cpu": "100m", "memory": "64Mi"},
                            },
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "readOnlyRootFilesystem": True,
                                "capabilities": {"drop": ["ALL"]},
                            },
                        }
                    ],
                },
            },
        },
    }


def kubernetes_executor(
    lease: KubernetesLease,
    *,
    executable: str = "/usr/local/bin/kubectl",
    runner: Callable[..., CommandResult] = run_kubectl,
    stable_seconds: float = 2.0,
) -> Callable[..., OperationResult]:
    """Build an injectable one-shot worker executor; no engine/cluster is prepared here."""

    def execute(
        profile: str,
        source: str,
        directory: Path,
        timeout_seconds: int,
        cancel: threading.Event,
        on_status: Callable[[str], None],
        verification_id: str | None,
        *,
        isolate_user: bool = True,
        on_output: Callable[[str, bool], None] | None = None,
    ) -> OperationResult:
        checks: list[dict[str, Any]] = []
        logs: list[str] = []
        owned: list[tuple[str, str, str]] = []
        intended: list[tuple[str, str]] = []
        import uuid

        job_nonce = uuid.uuid4().hex
        result_status = "failed"
        detail = "The operation did not establish its bounded contract."
        deadline = time.monotonic() + timeout_seconds
        work_deadline = deadline
        client: KubectlClient | None = None

        def log(text: str) -> None:
            logs.append(text)
            if on_output:
                on_output("\n".join(logs)[-128_000:], False)

        def check(name: str, passed: bool, explanation: str) -> None:
            checks.append({"name": name, "passed": passed, "detail": explanation})

        def tick(until: float, event: threading.Event = cancel) -> None:
            if event.is_set():
                raise InterruptedOperation("cancelled")
            if time.monotonic() >= until:
                raise InterruptedOperation("timed_out")
            event.wait(min(0.15, max(0.0, until - time.monotonic())))

        try:
            if profile != "k8s-kind" or verification_id not in (None, "k8s-readiness-v1"):
                raise KubernetesRefusal("Unsupported Kubernetes profile or verifier.")
            if type(timeout_seconds) is not int or timeout_seconds not in (15, 60, 120):
                raise KubernetesRefusal("Choose a supported bounded operation timeout.")
            if lease.expires_at <= time.time() + timeout_seconds + CLEANUP_SECONDS + 5:
                raise KubernetesRefusal(
                    "The lease must outlive the entire operation and cleanup reserve."
                )
            documents = parse_manifests(source)
            client = KubectlClient(
                lease, directory, executable=executable, isolate_user=isolate_user, runner=runner
            )
            client.namespace(work_deadline, cancel)
            # Never adopt an old or manually created object by matching its name.
            for kind, name in (
                ("deployment", "hello"),
                ("service", "hello"),
                ("job", "hello-check"),
            ):
                existing = client.call(
                    ["get", kind, name, "-o", "json"], work_deadline, cancel, missing_ok=True
                )
                if existing:
                    raise KubernetesRefusal(
                        "The fixed lesson resource already exists; use owned host recovery"
                        " before another one-shot Run."
                    )
            on_status("running")
            deployment_uid = ""
            service_uid = None
            desired = 0
            for document in documents:
                labels = document["metadata"].setdefault("labels", {})
                labels[OWNER_LABEL] = lease.owner_id
                labels[JOB_LABEL] = job_nonce
                kind = "deployment" if document["kind"] == "Deployment" else "service"
                intended.append((kind, "hello"))
                if document["kind"] == "Deployment":
                    document["spec"]["template"]["metadata"]["labels"][OWNER_LABEL] = lease.owner_id
                created = client.apply(document, work_deadline, cancel)
                metadata = _metadata(created, lease, name="hello")
                kind = "deployment" if document["kind"] == "Deployment" else "service"
                owned.append((kind, "hello", metadata["uid"]))
                if kind == "deployment":
                    deployment_uid = metadata["uid"]
                    desired = document["spec"]["replicas"]
                else:
                    service_uid = metadata["uid"]
            log("Submitted only the validated owned hello resources.")
            on_status("verifying")
            stable_since: float | None = None
            snapshot: dict[str, Any] = {}
            while True:
                healthy, snapshot = observe_ready(
                    client, deployment_uid, desired, service_uid, work_deadline, cancel
                )
                if healthy:
                    if stable_since is None:
                        stable_since = time.monotonic()
                    if time.monotonic() - stable_since >= stable_seconds:
                        break
                else:
                    stable_since = None
                tick(work_deadline)
            check("controller-and-pods", True, json.dumps(snapshot, sort_keys=True))
            if service_uid is not None:
                check(
                    "ready-service-backends",
                    True,
                    "Unique ready EndpointSlice Pod UIDs match the owned Ready Pod UID set.",
                )
                job_document = _client_job(lease.owner_id)
                job_document["metadata"]["labels"][JOB_LABEL] = job_nonce
                intended.append(("job", "hello-check"))
                job = client.apply(job_document, work_deadline, cancel)
                metadata = _metadata(job, lease, name="hello-check")
                owned.append(("job", "hello-check", metadata["uid"]))
                while True:
                    observed = client.call(
                        ["get", "job", "hello-check", "-o", "json"], work_deadline, cancel
                    )
                    meta = _metadata(observed, lease, name="hello-check")
                    if meta["uid"] != metadata["uid"]:
                        raise KubernetesRefusal("The client Job identity changed.")
                    status = observed.get("status", {})
                    if status.get("failed", 0) > 0:
                        raise KubernetesRefusal("The bounded in-cluster version client failed.")
                    if status.get("succeeded", 0) == 1:
                        break
                    tick(work_deadline)
                check(
                    "in-cluster-version",
                    True,
                    (
                        "The fixed client Job succeeded only after exact trimmed /version "
                        "response matching."
                    ),
                )
            elif verification_id == "k8s-readiness-v1":
                raise KubernetesRefusal(
                    "The readiness verifier requires both Deployment and Service for i"
                    "ndependent routing proof."
                )
            result_status = "succeeded"
            detail = (
                (
                    "Owned resource execution and typed infrastructure checks passed; "
                    "explanation and the full six-task course are not automatically gr"
                    "aded."
                )
                if verification_id
                else (
                    "The owned operation completed; no course verifier was selected an"
                    "d no mastery was inferred."
                )
            )
        except InterruptedOperation as exc:
            result_status = exc.status
            detail = "The bounded operation was interrupted; owned cleanup follows."
            check("operation-interrupted", False, exc.status)
        except (KubernetesRefusal, OSError, ValueError, TypeError, KeyError) as exc:
            detail = (
                str(exc)
                if isinstance(exc, KubernetesRefusal)
                else "The owned API response or local operation was invalid."
            )
            check("operation", False, detail)
        finally:
            cleanup_ok = True
            cleanup_deadline = time.monotonic() + CLEANUP_SECONDS
            if client is not None:
                cleanup_cancel = threading.Event()
                # A create can commit before its response is lost or cancellation
                # arrives. Recover only this Run's nonce-labelled object, never an
                # unclaimed object that merely has the same fixed name.
                confirmed = {(kind, name) for kind, name, _ in owned}
                for kind, name in intended:
                    if (kind, name) in confirmed:
                        continue
                    try:
                        client.namespace(cleanup_deadline, cleanup_cancel)
                        observed = client.call(
                            ["get", kind, name, "-o", "json"],
                            cleanup_deadline,
                            cleanup_cancel,
                            missing_ok=True,
                        )
                        if observed:
                            metadata = _metadata(observed, lease, name=name)
                            if metadata.get("labels", {}).get(JOB_LABEL) != job_nonce:
                                raise KubernetesRefusal(
                                    "Uncertain create is not this Run; it is preserved."
                                )
                            owned.append((kind, name, metadata["uid"]))
                            confirmed.add((kind, name))
                    except (KubernetesRefusal, InterruptedOperation, OSError, ValueError):
                        cleanup_ok = False
                for kind, name, uid in reversed(owned):
                    try:
                        client.cleanup(
                            kind, name, uid, cleanup_deadline, cleanup_cancel, job_nonce=job_nonce
                        )
                    except (KubernetesRefusal, InterruptedOperation, OSError, ValueError):
                        cleanup_ok = False
                if intended:
                    check(
                        "owned-cleanup",
                        cleanup_ok,
                        (
                            "Only recorded object UIDs are eligible for deletion; the private "
                            "cluster lease remains for explicit host release."
                        ),
                    )
            if not cleanup_ok:
                result_status = "failed"
                detail = (
                    "Owned cleanup could not be proved; use the explicit host recovery"
                    " path. No replacement or unrelated object was deleted."
                )
        log(detail)
        return OperationResult(
            0 if result_status == "succeeded" else 1,
            "\n".join(logs)[-128_000:],
            False,
            result_status,
            detail,
            checks,
        )

    return execute


def _uid_cannot_read(path: Path, uid: int) -> bool:
    if sys.platform != "linux" or os.geteuid() != 0:
        return False
    code = (
        "import os,sys; os.setgroups([]); "
        "os.setgid(int(sys.argv[2])); os.setuid(int(sys.argv[2])); "
        "\ntry:\n open(sys.argv[1],'rb').close()\nexcept PermissionError:\n sys.exit(0)"
        "\nexcept OSError:\n sys.exit(2)\nelse:\n sys.exit(3)"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", code, str(path), str(uid)],
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _startup_ready(lease: KubernetesLease, lease_path: Path, token_path: Path) -> tuple[bool, str]:
    for path in (token_path, lease_path, lease_path.parent / "worker.kubeconfig.json"):
        if not _uid_cannot_read(path, 65533) or not _uid_cannot_read(path, 65534):
            return (
                False,
                (
                    "The demoted process identity can read a supervisor credential or "
                    "isolation could not be proved."
                ),
            )
    if lease.expires_at <= time.time() + READINESS_WINDOW:
        return (
            False,
            "The scoped lease expires too soon for a bounded operation; prepare a new session.",
        )
    try:
        with tempfile.TemporaryDirectory(prefix="ds60-k8s-probe-") as temporary:
            client = KubectlClient(lease, Path(temporary))
            client.namespace(time.monotonic() + 5, threading.Event())
    except (KubernetesRefusal, OSError, ValueError, InterruptedOperation):
        return False, "The owned API endpoint/namespace UID probe failed; no workload was created."
    return (
        True,
        "Actual private-identity and owned API/namespace probes passed; no workload has run yet.",
    )


class KubernetesWorkerState(WorkerState):
    """Shutdown waits for bounded external-resource cleanup, not just process exit."""

    def begin_shutdown(self) -> None:
        with self.lock:
            self.closing = True
            self.ready = False
            self.detail = "Stopping after bounded owned-resource cleanup."
            for job in self.jobs.values():
                if job.status not in {"succeeded", "failed", "cancelled", "timed_out"}:
                    job.cancel.set()

    def close(self) -> None:
        self.begin_shutdown()
        with self.lock:
            thread = self.thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=CLEANUP_SECONDS + 5)
        if thread is not None and thread.is_alive():
            self.detail = "Cleanup could not be confirmed before shutdown; use owned host recovery."


def install_graceful_stop(
    server: WorkerHTTPServer, state: KubernetesWorkerState
) -> Callable[[], None]:
    """Signals request cancellation; server.shutdown must run outside its serve thread."""
    stopping = threading.Event()
    previous = {kind: signal.getsignal(kind) for kind in (signal.SIGTERM, signal.SIGINT)}

    def stop(_number: int, _frame: Any) -> None:
        if stopping.is_set():
            return
        stopping.set()
        state.begin_shutdown()
        threading.Thread(target=server.shutdown, daemon=True).start()

    for kind in previous:
        signal.signal(kind, stop)

    def restore() -> None:
        for kind, handler in previous.items():
            signal.signal(kind, handler)

    return restore


def main(argv: list[str] | None = None) -> int:
    from ds60sqlpy.module_worker import (
        WorkerHTTPServer,
        probe_isolation,
        read_worker_token,
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8081)
    arguments = parser.parse_args(argv)
    try:
        lease_path = Path(os.environ["DS60_K8S_LEASE_FILE"])
        token_path = Path(os.environ["DS60_WORKER_TOKEN_FILE"])
        token = read_worker_token(token_path)
        if token_path.stat().st_uid == 65533:
            raise KubernetesRefusal(
                "The kubectl child UID must not own the global worker credential."
            )
        lease = KubernetesLease.load(lease_path)
        isolated, detail = probe_isolation(token_path)
        ready, detail = (
            _startup_ready(lease, lease_path, token_path) if isolated else (False, detail)
        )
        state = KubernetesWorkerState(
            "k8s-kind", executor=kubernetes_executor(lease), ready=ready, detail=detail
        )
        server = WorkerHTTPServer((arguments.host, arguments.port), state, token)
    except (KeyError, OSError, ValueError) as exc:
        print(f"Kubernetes worker startup refused: {exc}", file=sys.stderr)
        return 2

    def expiry_watch() -> None:
        while not state.closing:
            if lease.expires_at <= time.time() + READINESS_WINDOW:
                with state.lock:
                    state.ready = False
                    state.detail = "The scoped lease expires too soon; prepare a new session."
                return
            try:
                with tempfile.TemporaryDirectory(prefix="ds60-k8s-health-") as temporary:
                    health = KubectlClient(lease, Path(temporary))
                    health.namespace(time.monotonic() + 3, threading.Event())
                available = True
            except (KubernetesRefusal, InterruptedOperation, OSError, ValueError):
                available = False
            with state.lock:
                state.ready = available
                state.detail = (
                    "The last owned API/namespace probe passed."
                    if available
                    else "The owned API/namespace probe failed; no new job is accepted."
                )
            for _ in range(25):
                if state.closing:
                    return
                time.sleep(0.2)

    threading.Thread(target=expiry_watch, daemon=True).start()
    restore_signals = install_graceful_stop(server, state)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        restore_signals()
    return 0


@dataclass(frozen=True)
class HostTools:
    kind: str
    kubectl: str
    docker: str


def local_docker_endpoint(value: str) -> str:
    if value.startswith("unix:///") and "\n" not in value and "\r" not in value:
        return value
    if value.startswith("npipe:////./pipe/") and re.fullmatch(
        r"npipe:////\./pipe/[A-Za-z0-9_.-]+", value
    ):
        return value
    raise KubernetesRefusal(
        "Choose an explicit local Unix socket or Windows named-pipe Docker endpoint."
    )


def _write_private(path: Path, value: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(value)


def host_command(
    argv: list[str], *, environment: dict[str, str], data: bytes | None = None, timeout: float = 90
) -> CommandResult:
    """Trusted host companion only; argv never originates in learner content."""
    result = subprocess.run(
        argv, input=data, env=environment, capture_output=True, timeout=timeout, check=False
    )
    if len(result.stdout) > MAX_COMMAND_BYTES or len(result.stderr) > MAX_COMMAND_BYTES:
        raise KubernetesRefusal("Host preparation returned an oversized bounded response.")
    return CommandResult(
        result.returncode,
        result.stdout.decode("utf-8", errors="replace"),
        result.stderr.decode("utf-8", errors="replace"),
    )


def prepare_owned_session(
    directory: Path,
    tools: HostTools,
    docker_endpoint: str,
    *,
    allow_node_download: bool = False,
    node_image: str = NODE_IMAGE,
    runner: Callable[..., CommandResult] = host_command,
    owner_id: str | None = None,
) -> Path:
    """Explicit host action: one owned kind node, scoped RBAC and a short token.

    No default kubeconfig path is ever read or written. Image/tool provisioning
    happens beforehand; missing bytes do not cause a silent download.
    """
    import secrets
    import uuid

    endpoint = local_docker_endpoint(docker_endpoint)
    if node_image not in (NODE_IMAGE, "mirror.gcr.io/" + NODE_IMAGE):
        raise KubernetesRefusal(
            "The node image must retain the exact official release/index diges"
            "t and an explicit approved registry."
        )
    owner = uuid.uuid4().hex if owner_id is None else owner_id
    if not OWNER.fullmatch(owner):
        raise KubernetesRefusal("Malformed host ownership identity.")
    absolute = directory.absolute()
    if any(
        part.is_symlink() or getattr(part, "is_junction", lambda: False)()
        for part in (absolute, *absolute.parents)
    ):
        raise KubernetesRefusal("Runtime directory ancestors cannot be symlinks or junctions.")
    resolved = absolute.resolve()
    if any(part.casefold() == ".learning" for part in (*absolute.parts, *resolved.parts)):
        raise KubernetesRefusal("Use a private runtime directory outside .learning.")
    directory = resolved
    directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    if os.name == "nt" and not _windows_private_acl(directory, establish=True):
        raise KubernetesRefusal(
            "Could not establish a private current-user/SYSTEM runtime ACL; no"
            " credential was created."
        )
    cluster = "ds60-" + owner[:12]
    namespace = "ds60-lesson-" + owner[:12]
    auth_namespace = "ds60-auth-" + owner[:12]
    admin = directory / "admin.kubeconfig.json"
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR") if key in os.environ}
    env.update(DOCKER_HOST=endpoint, HOME=str(directory), KUBECONFIG=str(admin))

    # DOCKER_CONTEXT and ambient KUBECONFIG are deliberately not inherited.
    def call(
        argv: list[str],
        data: dict[str, Any] | None = None,
        timeout: float = 90,
        *,
        may_fail: bool = False,
    ) -> CommandResult:
        result = runner(
            argv,
            environment=env,
            data=None if data is None else json.dumps(data).encode(),
            timeout=timeout,
        )
        if result.returncode and not may_fail:
            raise KubernetesRefusal(
                "The fixed host preparation command failed; private diagnostics re"
                "main outside learner exports."
            )
        return result

    def kubectl(arguments: list[str], data: dict[str, Any] | None = None) -> dict[str, Any]:
        result = call(
            [
                tools.kubectl,
                "--kubeconfig",
                str(admin),
                "--context",
                "kind-" + cluster,
                "--request-timeout=10s",
                *arguments,
            ],
            data,
        )
        return _mapping(json.loads(result.stdout), "host API response")

    created_id: str | None = None
    try:
        kind_version = call([tools.kind, "version"], timeout=10).stdout
        kubectl_version = json.loads(
            call([tools.kubectl, "version", "--client", "-o", "json"], timeout=10).stdout
        )
        if (
            not kind_version.startswith("kind " + KIND_VERSION + " ")
            or kubectl_version.get("clientVersion", {}).get("gitVersion") != KUBECTL_VERSION
        ):
            raise KubernetesRefusal(
                "Prepare the exact pinned kind and kubectl tools before creating a cluster."
            )
        call(
            [tools.docker, "--host", endpoint, "info", "--format", "{{json .ServerVersion}}"],
            timeout=10,
        )
        clusters = call([tools.kind, "get", "clusters"], timeout=10).stdout.splitlines()
        if cluster in clusters:
            raise KubernetesRefusal(
                "The generated cluster name already exists; it will not be reused or replaced."
            )
        node_cached = call(
            [tools.docker, "--host", endpoint, "image", "inspect", node_image],
            timeout=10,
            may_fail=True,
        )
        if node_cached.returncode and not allow_node_download:
            raise KubernetesRefusal(
                "The pinned kind node image is absent; explicitly approve its conn"
                "ected preparation first."
            )
        call([tools.docker, "--host", endpoint, "image", "inspect", FIXTURE_IMAGE], timeout=10)
        config = {
            "kind": "Cluster",
            "apiVersion": "kind.x-k8s.io/v1alpha4",
            "networking": {"apiServerAddress": "127.0.0.1"},
            "nodes": [
                {"role": "control-plane", "image": node_image, "labels": {OWNER_LABEL: owner}}
            ],
        }
        config_path = directory / "kind-config.json"
        _write_private(config_path, json.dumps(config).encode())
        _write_private(
            directory / "creation-intent.json",
            json.dumps(
                {
                    "owner_id": owner,
                    "cluster_name": cluster,
                    "docker_endpoint": endpoint,
                    "node_image": node_image,
                }
            ).encode(),
        )
        call(
            [
                tools.kind,
                "create",
                "cluster",
                "--name",
                cluster,
                "--image",
                node_image,
                "--config",
                str(config_path),
                "--kubeconfig",
                str(admin),
                "--wait",
                "90s",
            ],
            timeout=150,
        )
        owned_node = json.loads(
            call(
                [tools.docker, "--host", endpoint, "inspect", cluster + "-control-plane"],
                timeout=10,
            ).stdout
        )[0]
        if owned_node.get("Config", {}).get("Labels", {}).get(
            "io.x-k8s.kind.cluster"
        ) != cluster or not isinstance(owned_node.get("Id"), str):
            raise KubernetesRefusal("The newly created control-plane identity is unproved.")
        created_id = owned_node["Id"]
        _write_private(
            directory / "creation-receipt.json",
            json.dumps(
                {
                    "owner_id": owner,
                    "cluster_name": cluster,
                    "control_plane_id": created_id,
                    "docker_endpoint": endpoint,
                }
            ).encode(),
        )
        # Convert only this newly created explicit config; never consult ~/.kube/config.
        viewed = call(
            [
                tools.kubectl,
                "--kubeconfig",
                str(admin),
                "--context",
                "kind-" + cluster,
                "config",
                "view",
                "--raw",
                "--minify",
                "-o",
                "json",
            ],
            timeout=10,
        )
        admin_config = _mapping(json.loads(viewed.stdout), "generated admin kubeconfig")
        cluster_data = admin_config["clusters"][0]["cluster"]
        server = cluster_data.get("server", "")
        if not re.fullmatch(r"https://127\.0\.0\.1:[1-9][0-9]{0,4}", server):
            raise KubernetesRefusal("The host API endpoint must bind only loopback.")
        user_data = admin_config["users"][0]["user"]
        if set(cluster_data) != {"server", "certificate-authority-data"} or set(user_data) != {
            "client-certificate-data",
            "client-key-data",
        }:
            raise KubernetesRefusal(
                "The generated admin config contains unsupported credential/plugin fields."
            )
        # Atomic replacement stays inside the private runtime directory.
        converted = directory / "admin-converted.json"
        _write_private(converted, json.dumps(admin_config).encode())
        converted.replace(admin)
        admin.chmod(0o600)
        namespace_objects = [
            {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {"name": name, "labels": {OWNER_LABEL: owner}},
            }
            for name in (namespace, auth_namespace)
        ]
        observed = [
            kubectl(["create", "-f", "-", "-o", "json"], item) for item in namespace_objects
        ]
        namespace_uid = observed[0]["metadata"]["uid"]
        sa = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "worker",
                "namespace": auth_namespace,
                "labels": {OWNER_LABEL: owner},
            },
            "automountServiceAccountToken": False,
        }
        kubectl(["create", "-f", "-", "-o", "json"], sa)
        rules = [
            {
                "apiGroups": ["apps"],
                "resources": ["deployments"],
                "verbs": ["create", "get", "delete"],
            },
            {"apiGroups": ["apps"], "resources": ["replicasets"], "verbs": ["get", "list"]},
            {"apiGroups": [""], "resources": ["pods", "pods/log"], "verbs": ["get", "list"]},
            {"apiGroups": [""], "resources": ["services"], "verbs": ["create", "get", "delete"]},
            {"apiGroups": ["batch"], "resources": ["jobs"], "verbs": ["create", "get", "delete"]},
            {
                "apiGroups": ["discovery.k8s.io"],
                "resources": ["endpointslices"],
                "verbs": ["get", "list"],
            },
        ]
        role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": "ds60-worker",
                "namespace": namespace,
                "labels": {OWNER_LABEL: owner},
            },
            "rules": rules,
        }
        subject = {"kind": "ServiceAccount", "name": "worker", "namespace": auth_namespace}
        binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": "ds60-worker",
                "namespace": namespace,
                "labels": {OWNER_LABEL: owner},
            },
            "subjects": [subject],
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "Role",
                "name": "ds60-worker",
            },
        }
        read_name = "ds60-ns-" + owner[:12]
        read_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {"name": read_name, "labels": {OWNER_LABEL: owner}},
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["namespaces"],
                    "resourceNames": [namespace],
                    "verbs": ["get"],
                }
            ],
        }
        read_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {"name": read_name, "labels": {OWNER_LABEL: owner}},
            "subjects": [subject],
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": read_name,
            },
        }
        for obj in (role, binding, read_role, read_binding):
            kubectl(["create", "-f", "-", "-o", "json"], obj)
        token_response = kubectl(
            [
                "--namespace",
                auth_namespace,
                "create",
                "token",
                "worker",
                "--duration=15m",
                "-o",
                "json",
            ]
        )
        token_status = _mapping(token_response.get("status"), "TokenRequest status")
        token, expiration = token_status.get("token"), token_status.get("expirationTimestamp")
        if not isinstance(token, str) or not token or not isinstance(expiration, str):
            raise KubernetesRefusal("The API did not issue a short-lived token receipt.")
        actual_expiry = datetime.fromisoformat(expiration.replace("Z", "+00:00")).timestamp()
        if not READINESS_WINDOW < actual_expiry - time.time() <= 3600:
            raise KubernetesRefusal(
                "The issued token lifetime is outside the bounded session policy."
            )
        call([tools.kind, "load", "docker-image", FIXTURE_IMAGE, "--name", cluster], timeout=90)
        ca = cluster_data["certificate-authority-data"]
        ca_hash = hashlib.sha256(base64.b64decode(ca, validate=True)).hexdigest()
        worker = {
            "apiVersion": "v1",
            "kind": "Config",
            "current-context": "ds60-owned",
            "clusters": [
                {
                    "name": "ds60",
                    "cluster": {
                        "server": "https://" + cluster + "-control-plane:6443",
                        "certificate-authority-data": ca,
                    },
                }
            ],
            "users": [{"name": "scoped", "user": {"token": token}}],
            "contexts": [
                {
                    "name": "ds60-owned",
                    "context": {"cluster": "ds60", "user": "scoped", "namespace": namespace},
                }
            ],
        }
        lease = {
            "schema_version": 1,
            "owner_id": owner,
            "cluster_name": cluster,
            "context": "ds60-owned",
            "namespace": namespace,
            "namespace_uid": namespace_uid,
            "expires_at": expiration,
            "ca_sha256": ca_hash,
            "kubeconfig_file": "worker.kubeconfig.json",
            "fixture_image": FIXTURE_IMAGE,
        }
        _write_private(directory / "worker.kubeconfig.json", json.dumps(worker).encode())
        _write_private(directory / "worker.token", secrets.token_urlsafe(48).encode())
        _write_private(directory / "lease.json", json.dumps(lease).encode())
        inspect = json.loads(
            call(
                [tools.docker, "--host", endpoint, "inspect", cluster + "-control-plane"],
                timeout=10,
            ).stdout
        )[0]
        if (
            inspect.get("Config", {}).get("Labels", {}).get("io.x-k8s.kind.cluster") != cluster
            or inspect.get("Id") != created_id
        ):
            raise KubernetesRefusal(
                "The control-plane container ownership could not be established."
            )
        receipt = {
            "schema_version": 1,
            "owner_id": owner,
            "cluster_name": cluster,
            "namespace": namespace,
            "namespace_uid": namespace_uid,
            "control_plane_id": inspect["Id"],
            "docker_endpoint": endpoint,
            "kind_version": KIND_VERSION,
            "kubectl_version": KUBECTL_VERSION,
            "node_image": node_image,
            "fixture_image": FIXTURE_IMAGE,
            "host_server": server,
        }
        _write_private(directory / "host-receipt.json", json.dumps(receipt).encode())
        return directory / "lease.json"
    except Exception as error:
        cleaned = False
        if created_id is not None:
            try:
                node_result = call(
                    [tools.docker, "--host", endpoint, "inspect", cluster + "-control-plane"],
                    timeout=10,
                    may_fail=True,
                )
                current = json.loads(node_result.stdout)[0] if node_result.returncode == 0 else {}
                if (
                    current.get("Id") == created_id
                    and current.get("Config", {}).get("Labels", {}).get("io.x-k8s.kind.cluster")
                    == cluster
                ):
                    deleted = call(
                        [
                            tools.kind,
                            "delete",
                            "cluster",
                            "--name",
                            cluster,
                            "--kubeconfig",
                            str(admin),
                        ],
                        timeout=90,
                        may_fail=True,
                    )
                    absent = call(
                        [tools.docker, "--host", endpoint, "inspect", cluster + "-control-plane"],
                        timeout=10,
                        may_fail=True,
                    )
                    cleaned = (
                        deleted.returncode == 0
                        and absent.returncode != 0
                        and "No such" in absent.stderr
                    )
            except (OSError, ValueError, subprocess.TimeoutExpired):
                cleaned = False
        _write_private(
            directory / "preparation-failure.json",
            json.dumps(
                {
                    "owner_id": owner,
                    "cluster_name": cluster,
                    "owned_node_recorded": created_id is not None,
                    "cleanup_confirmed": cleaned,
                    "manual_inspection_required": not cleaned,
                }
            ).encode(),
        )
        if cleaned:
            for name in (
                "worker.kubeconfig.json",
                "worker.token",
                "lease.json",
                "admin.kubeconfig.json",
            ):
                (directory / name).unlink(missing_ok=True)
        if isinstance(error, KubernetesRefusal) and created_id is None:
            raise
        raise KubernetesRefusal(
            "Preparation failed; inspect the private recovery receipt. "
            + (
                "Only the recorded owned node was removed."
                if cleaned
                else "Cleanup could not be proved; no ambiguous resource was removed."
            )
        ) from error


def release_owned_session(
    directory: Path, tools: HostTools, *, runner: Callable[..., CommandResult] = host_command
) -> None:
    receipt = json.loads(_private_file(directory / "host-receipt.json", 16_384))
    owner = receipt.get("owner_id")
    if (
        not isinstance(owner, str)
        or not OWNER.fullmatch(owner)
        or receipt.get("cluster_name") != "ds60-" + owner[:12]
    ):
        raise KubernetesRefusal("The private release receipt has an invalid cluster identity.")
    cluster = receipt["cluster_name"]
    endpoint = local_docker_endpoint(receipt["docker_endpoint"])
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR") if key in os.environ}
    env.update(
        DOCKER_HOST=endpoint,
        HOME=str(directory),
        KUBECONFIG=str(directory / "admin.kubeconfig.json"),
    )

    def owned_node_present() -> bool:
        # Successful structured listings prove absence independently of localized
        # daemon stderr. Check both the exact name and full recorded ID so a
        # renamed original or a same-name replacement is never silently adopted.
        name = cluster + "-control-plane"
        expected = receipt.get("control_plane_id")
        if not isinstance(expected, str) or not expected:
            raise KubernetesRefusal("The private receipt lacks its recorded node ID.")
        rows: set[tuple[str, str]] = set()
        for selection in ("name=^/" + name + "$", "id=" + expected):
            listing = runner(
                [
                    tools.docker,
                    "--host",
                    endpoint,
                    "container",
                    "ls",
                    "--all",
                    "--no-trunc",
                    "--filter",
                    selection,
                    "--format",
                    "{{.ID}}\t{{.Names}}",
                ],
                environment=env,
                timeout=10,
            )
            if listing.returncode:
                raise KubernetesRefusal(
                    "The engine could not list the exact owned node; private evidence is retained."
                )
            for line in listing.stdout.splitlines():
                fields = line.split("\t")
                if len(fields) != 2 or not all(fields):
                    raise KubernetesRefusal(
                        "The engine node listing was malformed; release refused."
                    )
                rows.add((fields[0], fields[1]))
        if not rows:
            return False
        if rows != {(expected, name)}:
            raise KubernetesRefusal(
                "The control-plane container was replaced or renamed; release refused."
            )
        return True

    if owned_node_present():
        observed = runner(
            [tools.docker, "--host", endpoint, "inspect", cluster + "-control-plane"],
            environment=env,
            timeout=10,
        )
        if observed.returncode:
            raise KubernetesRefusal(
                "The exact owned control-plane identity cannot be checked; release refused."
            )
        info = json.loads(observed.stdout)[0]
        if (
            info.get("Id") != receipt.get("control_plane_id")
            or info.get("Config", {}).get("Labels", {}).get("io.x-k8s.kind.cluster") != cluster
        ):
            raise KubernetesRefusal("The control-plane container was replaced; release refused.")
        admin = directory / "admin.kubeconfig.json"
        _private_file(admin, 262_144)
        result = runner(
            [
                tools.kubectl,
                "--kubeconfig",
                str(admin),
                "--context",
                "kind-" + cluster,
                "--request-timeout=10s",
                "get",
                "namespace",
                receipt["namespace"],
                "-o",
                "json",
            ],
            environment=env,
            timeout=15,
        )
        if result.returncode:
            raise KubernetesRefusal("Namespace identity cannot be checked; release refused.")
        meta = json.loads(result.stdout).get("metadata", {})
        if (
            meta.get("uid") != receipt.get("namespace_uid")
            or meta.get("labels", {}).get(OWNER_LABEL) != owner
        ):
            raise KubernetesRefusal("The namespace was replaced; release refused.")
        result = runner(
            [tools.kind, "delete", "cluster", "--name", cluster, "--kubeconfig", str(admin)],
            environment=env,
            timeout=90,
        )
        if result.returncode:
            raise KubernetesRefusal(
                "Owned cluster release did not complete; private recovery evidence is retained."
            )
        if owned_node_present():
            raise KubernetesRefusal(
                "The owned control-plane remains; private recovery evidence is retained."
            )
    for name in ("worker.kubeconfig.json", "worker.token", "admin.kubeconfig.json", "lease.json"):
        target = directory / name
        if target.is_symlink():
            raise KubernetesRefusal("Private runtime path changed during release.")
        target.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
