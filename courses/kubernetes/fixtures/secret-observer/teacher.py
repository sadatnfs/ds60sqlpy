"""Run the fixed synthetic observer in an explicit, already prepared owned session."""

from __future__ import annotations

import argparse
import base64
import contextlib
import hashlib
import http.client
import json
import os
import queue
import re
import signal
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))
from render import manifest  # noqa: E402

from ds60sqlpy.kubernetes_module import (  # noqa: E402
    FIXTURE_IMAGE,
    KUBECTL_VERSION,
    OWNER_LABEL,
    KubernetesLease,
    KubernetesRefusal,
    _private_file,
)

APP = "synthetic-secret-observer"
NONCE_LABEL = "learning.ds60sqlpy/secret-observer-run"
NAMES = (
    ("secrets", "synthetic-message"),
    ("configmaps", "synthetic-secret-observer-program"),
    ("deployments", APP),
)
API = {
    "secrets": "/api/v1",
    "configmaps": "/api/v1",
    "pods": "/api/v1",
    "deployments": "/apis/apps/v1",
}


class Refusal(RuntimeError):
    """A safe, value-free failure suitable for the evidence record."""


def owned(meta: dict[str, Any], owner: str, nonce: str, uid: str | None = None) -> bool:
    labels = meta.get("labels", {})
    return (
        labels.get(OWNER_LABEL) == owner
        and labels.get(NONCE_LABEL) == nonce
        and isinstance(meta.get("uid"), str)
        and bool(meta["uid"])
        and (uid is None or meta["uid"] == uid)
    )


def delete_options(uid: str) -> dict[str, Any]:
    return {
        "apiVersion": "v1",
        "kind": "DeleteOptions",
        "preconditions": {"uid": uid},
        "propagationPolicy": "Foreground",
        "gracePeriodSeconds": 1,
    }


def rotation_patch(uid: str, version: str) -> list[dict[str, Any]]:
    return [
        {"op": "test", "path": "/metadata/uid", "value": uid},
        {"op": "test", "path": "/metadata/resourceVersion", "value": version},
        {
            "op": "replace",
            "path": "/data/lesson-message",
            "value": base64.b64encode(b"DUMMY_LESSON_ROTATED").decode("ascii"),
        },
    ]


def owner_uid(obj: dict[str, Any], kind: str) -> str | None:
    references = obj.get("metadata", {}).get("ownerReferences", [])
    controllers = [ref for ref in references if ref.get("controller") is True]
    if len(controllers) == 1 and controllers[0].get("kind") == kind:
        return str(controllers[0].get("uid", ""))
    return None


class Teacher:
    def __init__(self, session: Path, kubectl: Path, output: Path) -> None:
        self.session = session.resolve(strict=True)
        self.kubectl = kubectl.resolve(strict=True)
        self.lease = KubernetesLease.load(self.session / "lease.json")
        self.receipt = json.loads(_private_file(self.session / "host-receipt.json", 16384))
        for field in ("owner_id", "cluster_name", "namespace", "namespace_uid"):
            if self.receipt.get(field) != getattr(self.lease, field):
                raise Refusal("Host receipt and worker lease disagree.")
        if self.receipt.get("fixture_image") != FIXTURE_IMAGE:
            raise Refusal("Host fixture image differs from the prepared contract.")
        if self.lease.expires_at < time.time() + 420:
            raise Refusal("Prepare a fresh session: this observation needs seven minutes of lease.")
        self.config = self.session / "admin.kubeconfig.json"
        config = json.loads(_private_file(self.config, 262144))
        self.context = "kind-" + self.lease.cluster_name
        self._check_config(config)
        self.environment = {
            k: os.environ[k] for k in ("PATH", "SYSTEMROOT", "WINDIR") if k in os.environ
        }
        self.environment.update(HOME=str(self.session), KUBECONFIG=str(self.config))
        self.nonce = uuid.uuid4().hex
        self.directory = output.resolve()
        self.directory.mkdir(mode=0o700, parents=False, exist_ok=False)
        self.ledger: list[dict[str, str]] = []
        self.evidence: dict[str, Any] = {
            "schema_version": 1,
            "lesson_id": "k8s-019",
            "run_nonce": self.nonce,
            "namespace": self.lease.namespace,
            "namespace_uid": self.lease.namespace_uid,
            "context": self.context,
            "fixture_image": FIXTURE_IMAGE,
            "source_sha256": {
                name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                for name in ("app.py", "render.py", "teacher.py", "manifest.json")
            },
            "objects": self.ledger,
            "observations": [],
            "cleanup_confirmed": False,
            "credentials_printed": False,
            "ordinary_worker_permissions_changed": False,
        }
        self.deadline = time.monotonic() + 360
        self.cleaning = False

    def _check_config(self, config: dict[str, Any]) -> None:
        def require(condition: Any) -> None:
            if not condition:
                raise ValueError("Invalid private context")

        try:
            require(config["current-context"] == self.context)
            require(len(config["clusters"]) == len(config["users"]) == len(config["contexts"]) == 1)
            cluster = config["clusters"][0]
            user = config["users"][0]
            context = config["contexts"][0]
            require(cluster["name"] == user["name"] == context["name"] == self.context)
            require(context["context"]["cluster"] == context["context"]["user"] == self.context)
            connection = cluster["cluster"]
            require(set(connection) == {"server", "certificate-authority-data"})
            require(connection["server"] == self.receipt["host_server"])
            require(re.fullmatch(r"https://127\.0\.0\.1:[0-9]+", connection["server"]))
            ca = base64.b64decode(connection["certificate-authority-data"], validate=True)
            require(hashlib.sha256(ca).hexdigest() == self.lease.ca_sha256)
            require(set(user["user"]) == {"client-certificate-data", "client-key-data"})
            for value in user["user"].values():
                require(base64.b64decode(value, validate=True))
        except (KeyError, ValueError, TypeError) as exc:
            raise Refusal(
                "The private teacher context is not the prepared local identity."
            ) from exc

    def args(self, *arguments: str) -> list[str]:
        return [
            str(self.kubectl),
            "--kubeconfig",
            str(self.config),
            "--context",
            self.context,
            "--namespace",
            self.lease.namespace,
            "--request-timeout=8s",
            *arguments,
        ]

    def call(self, *arguments: str, body: dict[str, Any] | list[Any] | None = None) -> str:
        if not self.cleaning and (
            time.monotonic() >= self.deadline or time.time() >= self.lease.expires_at - 60
        ):
            raise Refusal("Observation budget exhausted; preserving time for cleanup.")
        result = subprocess.run(
            self.args(*arguments),
            input=None if body is None else json.dumps(body),
            capture_output=True,
            text=True,
            timeout=12,
            env=self.environment,
            check=False,
        )
        if result.returncode:
            # kubectl error bodies can contain submitted fields. Do not publish them.
            raise Refusal("A scoped kubectl request failed; inspect the owned target privately.")
        if len(result.stdout.encode()) > 262144:
            raise Refusal("The scoped response exceeded the teaching bound.")
        return result.stdout

    def target(self) -> None:
        namespace = json.loads(self.call("get", "namespace", self.lease.namespace, "-o", "json"))
        meta = namespace.get("metadata", {})
        if (
            meta.get("uid") != self.lease.namespace_uid
            or meta.get("labels", {}).get(OWNER_LABEL) != self.lease.owner_id
            or meta.get("deletionTimestamp")
        ):
            raise Refusal("Owned namespace identity changed; no mutation is allowed.")

    def get(self, resource: str, name: str) -> dict[str, Any] | None:
        raw = self.call("get", resource, name, "--ignore-not-found", "-o", "json")
        return json.loads(raw) if raw.strip() else None

    def save(self) -> None:
        destination = self.directory / "evidence.json"
        temporary = self.directory / "evidence.next.json"
        temporary.write_text(json.dumps(self.evidence, indent=2) + "\n", encoding="utf-8")
        temporary.replace(destination)

    def checked(self, resource: str, name: str, uid: str | None = None) -> dict[str, Any]:
        obj = self.get(resource, name)
        if obj is None or not owned(obj.get("metadata", {}), self.lease.owner_id, self.nonce, uid):
            raise Refusal("A fixture object is missing or has different ownership.")
        return obj

    def create(self) -> None:
        self.target()
        version = json.loads(self.call("version", "--client", "-o", "json"))
        if version["clientVersion"]["gitVersion"] != KUBECTL_VERSION:
            raise Refusal("Use the prepared pinned kubectl version.")
        self.evidence["kubectl_version"] = version["clientVersion"]["gitVersion"]
        for resource, name in NAMES:
            if self.get(resource, name) is not None:
                raise Refusal("A fixed fixture name already exists; it is preserved.")
        for (resource, name), obj in zip(
            NAMES, manifest(Path(__file__).parent)["items"], strict=True
        ):
            self.target()
            labels = {OWNER_LABEL: self.lease.owner_id, NONCE_LABEL: self.nonce}
            obj["metadata"]["namespace"] = self.lease.namespace
            obj["metadata"]["labels"].update(labels)
            if resource == "deployments":
                obj["spec"]["template"]["metadata"]["labels"].update(labels)
            # Save intent first. If create times out after acceptance, recovery requires this nonce.
            intent = {"resource": resource, "name": name, "uid": ""}
            self.ledger.append(intent)
            self.save()
            try:
                self.call("create", "-f", "-", "-o", "name", body=obj)
            finally:
                observed = self.get(resource, name)
                if observed is not None and owned(
                    observed.get("metadata", {}), self.lease.owner_id, self.nonce
                ):
                    intent["uid"] = observed["metadata"]["uid"]
                    self.save()
            if not intent["uid"]:
                raise Refusal("Created object identity could not be recorded.")

    def selected(self, resource: str) -> list[dict[str, Any]]:
        selector = f"app={APP},{OWNER_LABEL}={self.lease.owner_id},{NONCE_LABEL}={self.nonce}"
        return json.loads(self.call("get", resource, "-l", selector, "-o", "json"))["items"]

    def ready_pod(self, previous_uid: str | None = None) -> dict[str, Any]:
        until = min(self.deadline, time.monotonic() + 65)
        deployment_uid = next(o["uid"] for o in self.ledger if o["resource"] == "deployments")
        while time.monotonic() < until:
            self.target()
            self.checked("deployments", APP, deployment_uid)
            replicas = self.selected("replicasets")
            replica_uids = set()
            for replica in replicas:
                if (
                    not owned(replica["metadata"], self.lease.owner_id, self.nonce)
                    or owner_uid(replica, "Deployment") != deployment_uid
                ):
                    raise Refusal("ReplicaSet ownership does not match the fixture Deployment.")
                replica_uids.add(replica["metadata"]["uid"])
            ready = []
            for pod in self.selected("pods"):
                meta = pod["metadata"]
                if (
                    not owned(meta, self.lease.owner_id, self.nonce)
                    or owner_uid(pod, "ReplicaSet") not in replica_uids
                ):
                    raise Refusal("Pod ownership does not match the fixture controller graph.")
                if (
                    not meta.get("deletionTimestamp")
                    and meta["uid"] != previous_uid
                    and any(
                        c.get("type") == "Ready" and c.get("status") == "True"
                        for c in pod.get("status", {}).get("conditions", [])
                    )
                ):
                    ready.append(pod)
            if len(ready) == 1:
                statuses = ready[0]["status"].get("containerStatuses", [])
                self.evidence.setdefault("pod_images", []).append(
                    {
                        "pod_uid": ready[0]["metadata"]["uid"],
                        "images": [s.get("imageID", "") for s in statuses],
                    }
                )
                return ready[0]
            if len(ready) > 1:
                raise Refusal("Expected exactly one ready fixture Pod.")
            time.sleep(1)
        raise Refusal("The owned fixture Pod did not become ready within 65 seconds.")

    @contextlib.contextmanager
    def forward(self, pod: dict[str, Any]) -> Iterator[int]:
        meta = pod["metadata"]
        self.target()
        self.checked("pods", meta["name"], meta["uid"])
        process = subprocess.Popen(
            self.args("port-forward", "--address=127.0.0.1", "pod/" + meta["name"], "0:8080"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=self.environment,
        )
        lines: queue.Queue[str] = queue.Queue(maxsize=32)

        def read_output() -> None:
            assert process.stdout is not None
            for line in process.stdout:
                with contextlib.suppress(queue.Full):
                    lines.put_nowait(line)

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()
        try:
            until = time.monotonic() + 15
            while time.monotonic() < until:
                if process.poll() is not None:
                    raise Refusal("The owned Pod port-forward stopped.")
                try:
                    line = lines.get(timeout=0.2)
                except queue.Empty:
                    continue
                match = re.fullmatch(r"Forwarding from 127\.0\.0\.1:(\d+) -> 8080\s*", line)
                if match:
                    yield int(match.group(1))
                    return
            raise Refusal("Loopback port-forward did not become ready within 15 seconds.")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            reader.join(timeout=2)
            if process.stdout:
                process.stdout.close()

    def observation(self, port: int, pod_uid: str, *, reload: bool = False) -> dict[str, str]:
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
        try:
            connection.request(
                "POST" if reload else "GET",
                "/reload" if reload else "/observe",
                headers={"Content-Length": "0"},
            )
            response = connection.getresponse()
            body = response.read(4097)
            if response.status != 200 or len(body) > 4096:
                raise Refusal("Observer did not return a bounded successful response.")
            data = json.loads(body)
        finally:
            connection.close()
        fields = {"pod_uid", "boot_id", "environment", "projected_file", "application_cache"}
        if (
            set(data) != fields
            or data["pod_uid"] != pod_uid
            or not re.fullmatch(r"[0-9a-f]{32}", data["boot_id"])
            or any(
                data[k] not in ("initial", "rotated")
                for k in ("environment", "projected_file", "application_cache")
            )
        ):
            raise Refusal("Observer response identity or label contract failed.")
        return data

    def retain(self, stage: str, data: dict[str, str]) -> None:
        self.evidence["observations"].append({"stage": stage, **data})
        self.save()

    def delete(self, resource: str, name: str, uid: str) -> None:
        self.target()
        current = self.get(resource, name)
        if current is None:
            return
        if not owned(current["metadata"], self.lease.owner_id, self.nonce, uid):
            raise Refusal("Cleanup preserved a replacement or unrelated object.")
        path = f"{API[resource]}/namespaces/{self.lease.namespace}/{resource}/{name}"
        self.call("delete", "--raw", path, "-f", "-", body=delete_options(uid))

    def run(self) -> None:
        self.create()
        pod = self.ready_pod()
        uid = pod["metadata"]["uid"]
        with self.forward(pod) as port:
            initial = self.observation(port, uid)
            if any(
                initial[k] != "initial"
                for k in ("environment", "projected_file", "application_cache")
            ):
                raise Refusal("Initial marker state did not match all three channels.")
            self.retain("initial", initial)
            secret_uid = next(o["uid"] for o in self.ledger if o["resource"] == "secrets")
            self.target()
            secret = self.checked("secrets", "synthetic-message", secret_uid)
            patch = rotation_patch(secret_uid, secret["metadata"]["resourceVersion"])
            patch_path = self.directory / "rotation-patch.json"
            patch_path.write_text(json.dumps(patch) + "\n", encoding="utf-8")
            self.call(
                "patch",
                "secret",
                "synthetic-message",
                "--type=json",
                "--patch-file",
                str(patch_path),
                "-o",
                "name",
            )
            rotated = self.checked("secrets", "synthetic-message", secret_uid)
            self.evidence["secret_resource_versions"] = [
                secret["metadata"]["resourceVersion"],
                rotated["metadata"]["resourceVersion"],
            ]
            started = time.monotonic()
            while time.monotonic() - started < 150:
                self.target()
                observed = self.observation(port, uid)
                if (
                    observed["boot_id"] != initial["boot_id"]
                    or observed["environment"] != "initial"
                    or observed["application_cache"] != "initial"
                ):
                    raise Refusal(
                        "Process identity or snapshot changed during projection observation."
                    )
                if observed["projected_file"] == "rotated":
                    self.evidence["projection_observed_seconds"] = round(
                        time.monotonic() - started, 3
                    )
                    self.retain("projected_before_reload", observed)
                    break
                time.sleep(1)
            else:
                raise Refusal(
                    "Projection was not observed in 150 seconds; no timing guarantee is inferred."
                )
            reloaded = self.observation(port, uid, reload=True)
            if (
                reloaded["boot_id"] != initial["boot_id"]
                or reloaded["environment"] != "initial"
                or reloaded["projected_file"] != "rotated"
                or reloaded["application_cache"] != "rotated"
            ):
                raise Refusal(
                    "Explicit application reload did not satisfy the three-channel contract."
                )
            self.retain("application_reloaded", reloaded)
        self.delete("pods", pod["metadata"]["name"], uid)
        replacement = self.ready_pod(previous_uid=uid)
        with self.forward(replacement) as port:
            restarted = self.observation(port, replacement["metadata"]["uid"])
            if restarted["boot_id"] == initial["boot_id"] or any(
                restarted[k] != "rotated"
                for k in ("environment", "projected_file", "application_cache")
            ):
                raise Refusal("Replacement process did not capture the rotated marker.")
            self.retain("replacement_pod", restarted)
        self.evidence["observation_passed"] = True

    def cleanup(self) -> None:
        self.cleaning = True
        errors = []
        for obj in reversed(self.ledger):
            try:
                if obj["uid"]:
                    self.delete(obj["resource"], obj["name"], obj["uid"])
                elif self.get(obj["resource"], obj["name"]) is not None:
                    raise Refusal("An unrecorded object needs private ownership review.")
            except (Refusal, OSError, ValueError, subprocess.TimeoutExpired):
                errors.append(obj["resource"] + "/" + obj["name"])
        until = time.monotonic() + 40
        absent = False
        while not errors and time.monotonic() < until:
            try:
                self.target()
                absent = all(self.get(o["resource"], o["name"]) is None for o in self.ledger)
                absent = absent and not self.selected("pods") and not self.selected("replicasets")
            except (Refusal, OSError, ValueError, subprocess.TimeoutExpired):
                errors.append("cleanup-readback")
                break
            if absent:
                break
            time.sleep(1)
        self.evidence["cleanup_confirmed"] = bool(absent and not errors)
        self.evidence["cleanup_review_required"] = errors
        self.save()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--kubectl", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, required=True, help="New evidence directory; its parent must exist"
    )
    parser.add_argument("--confirm-synthetic-secret", action="store_true")
    args = parser.parse_args()
    if not args.confirm_synthetic_secret:
        parser.error("The teacher-only synthetic Secret operation requires explicit confirmation")
    runner = None
    previous = signal.getsignal(signal.SIGTERM)

    def cancel(signum: int, frame: Any) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, cancel)
    try:
        runner = Teacher(args.session, args.kubectl, args.output)
        runner.run()
    except (
        Refusal,
        KubernetesRefusal,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.TimeoutExpired,
        KeyboardInterrupt,
    ) as exc:
        if runner:
            runner.evidence["observation_passed"] = False
            runner.evidence["failure_type"] = type(exc).__name__
            if isinstance(exc, Refusal):
                runner.evidence["failure_message"] = str(exc)
        print(
            "Synthetic observation did not complete; inspect the value-free evidence record.",
            file=sys.stderr,
        )
    finally:
        # A second signal must not interrupt the bounded cleanup sequence.
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        old_interrupt = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            if runner:
                runner.cleanup()
        finally:
            signal.signal(signal.SIGTERM, previous)
            signal.signal(signal.SIGINT, old_interrupt)
    if (
        runner
        and runner.evidence.get("observation_passed")
        and runner.evidence["cleanup_confirmed"]
    ):
        print(
            json.dumps(
                {
                    "observation_passed": True,
                    "cleanup_confirmed": True,
                    "evidence": str(runner.directory / "evidence.json"),
                }
            )
        )
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
