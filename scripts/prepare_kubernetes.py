"""Explicit host companion for one owned kind course session.

Tool preparation, cluster creation and release are separate visible actions.
No default kubeconfig or ambient context is selected or modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import sys
import tempfile
import time
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ds60sqlpy.kubernetes_module import (  # noqa: E402
    KIND_VERSION,
    KUBECTL_VERSION,
    NODE_IMAGE,
    READINESS_WINDOW,
    HostTools,
    KubernetesLease,
    KubernetesRefusal,
    _private_file,
    local_docker_endpoint,
    prepare_owned_session,
    release_owned_session,
)


def tool_targets(system: str | None = None, machine: str | None = None) -> tuple[str, str, str]:
    operating = (platform.system() if system is None else system).lower()
    cpu = (platform.machine() if machine is None else machine).lower()
    architecture = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "amd64", "amd64": "amd64"}.get(
        cpu
    )
    if operating not in ("linux", "darwin", "windows") or architecture is None:
        raise KubernetesRefusal("This host OS/CPU needs a separate tool qualification row.")
    if operating == "windows" and architecture != "amd64":
        raise KubernetesRefusal("Use a qualified Linux/WSL route for this Windows architecture.")
    return operating, architecture, ".exe" if operating == "windows" else ""


def download_tool(url: str, checksum_suffix: str, target: Path) -> None:
    """Connected explicit preparation: verify official checksum before publication."""
    with urllib.request.urlopen(url + checksum_suffix, timeout=30) as response:
        text = response.read(1024).decode("ascii").strip()
    checksum = text.split()[0] if text else ""
    if not re.fullmatch(r"[0-9a-fA-F]{64}", checksum):
        raise KubernetesRefusal("The official tool checksum response is malformed.")
    if target.exists():
        if (
            target.is_symlink()
            or hashlib.sha256(target.read_bytes()).hexdigest() != checksum.lower()
        ):
            raise KubernetesRefusal(
                "An existing tool differs from its pinned checksum; it is preserved for review."
            )
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".download-" + uuid.uuid4().hex)
    digest = hashlib.sha256()
    total = 0
    try:
        with urllib.request.urlopen(url, timeout=60) as response, temporary.open("xb") as output:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > 128 * 1024 * 1024:
                    raise KubernetesRefusal("The tool download exceeds128 MiB.")
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != checksum.lower():
            raise KubernetesRefusal("The tool body failed SHA256 verification.")
        temporary.chmod(0o755)
        # Do not replace a target created concurrently by another preparation.
        if target.exists():
            raise KubernetesRefusal(
                "The tool destination appeared during preparation; no file was overwritten."
            )
        temporary.rename(target)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("doctor", "tools", "prepare", "release", "inspect"))
    parser.add_argument("--tools-dir", type=Path, default=ROOT / "work/kubernetes-tools")
    parser.add_argument("--session", type=Path)
    parser.add_argument("--docker", default=shutil.which("docker"))
    parser.add_argument("--docker-host")
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--allow-node-download", action="store_true")
    parser.add_argument("--node-image", default=NODE_IMAGE)
    parser.add_argument("--confirm-create", action="store_true")
    parser.add_argument("--confirm-release", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            if args.session is None or not args.docker_host:
                raise KubernetesRefusal(
                    "Inspect requires --session and the selected local --docker-host."
                )
            lease = KubernetesLease.load(args.session / "lease.json")
            receipt = json.loads(_private_file(args.session / "host-receipt.json", 16_384))
            if not isinstance(receipt, dict) or any(
                receipt.get(field) != getattr(lease, field)
                for field in ("owner_id", "cluster_name", "namespace", "namespace_uid")
            ):
                raise KubernetesRefusal("The private host receipt and worker lease do not agree.")
            if local_docker_endpoint(args.docker_host) != receipt.get("docker_endpoint"):
                raise KubernetesRefusal("This lease belongs to another local engine endpoint.")
            if lease.expires_at <= time.time() + READINESS_WINDOW:
                raise KubernetesRefusal(
                    "The lease expires too soon; release and prepare a fresh owned session."
                )
            print(
                json.dumps(
                    {
                        "session_dir": str(args.session.absolute()),
                        "private_lease_valid": True,
                        "cluster_mutated": False,
                        "credentials_printed": False,
                    }
                )
            )
            return 0
        operating, architecture, suffix = tool_targets()
        kind = args.tools_dir / f"kind-{KIND_VERSION}{suffix}"
        kubectl = args.tools_dir / f"kubectl-{KUBECTL_VERSION}{suffix}"
        if args.action == "doctor":
            print(
                json.dumps(
                    {
                        "kind_version": KIND_VERSION,
                        "kubectl_version": KUBECTL_VERSION,
                        "kind_present": kind.is_file(),
                        "kubectl_present": kubectl.is_file(),
                        "docker_cli_present": bool(args.docker),
                        "cluster_created": False,
                        "download_performed": False,
                    }
                )
            )
            return 0 if kind.is_file() and kubectl.is_file() and args.docker else 2
        if args.action == "tools":
            if not args.allow_download:
                raise KubernetesRefusal(
                    "Use tools --allow-download only after reviewing the explicit conn"
                    "ected preparation."
                )
            kind_url = f"https://github.com/kubernetes-sigs/kind/releases/download/{KIND_VERSION}/kind-{operating}-{architecture}"
            kubectl_url = f"https://dl.k8s.io/release/{KUBECTL_VERSION}/bin/{operating}/{architecture}/kubectl{suffix}"
            download_tool(kind_url, ".sha256sum", kind)
            download_tool(kubectl_url, ".sha256", kubectl)
            print(json.dumps({"kind": str(kind), "kubectl": str(kubectl), "verified_sha256": True}))
            return 0
        if not kind.is_file() or not kubectl.is_file() or not args.docker:
            raise KubernetesRefusal(
                "Prepare the pinned tools and a local Docker CLI first; no automat"
                "ic install occurs."
            )
        tools = HostTools(
            str(kind.resolve()), str(kubectl.resolve()), str(Path(args.docker).resolve())
        )
        if args.action == "release":
            if not args.confirm_release or args.session is None:
                raise KubernetesRefusal(
                    "Release requires --session and --confirm-release for the exact pr"
                    "ivate receipt."
                )
            release_owned_session(args.session, tools)
            print(
                json.dumps(
                    {"released_owned_session": str(args.session), "learner_work_preserved": True}
                )
            )
            return 0
        if not args.confirm_create or not args.docker_host:
            raise KubernetesRefusal(
                "Prepare requires --confirm-create and an explicit local --docker-host."
            )
        endpoint = local_docker_endpoint(args.docker_host)
        session = args.session or Path(tempfile.gettempdir()).resolve() / (
            "ds60-k8s-" + uuid.uuid4().hex
        )
        prepared_lease_path = prepare_owned_session(
            session,
            tools,
            endpoint,
            allow_node_download=args.allow_node_download,
            node_image=args.node_image,
        )
        print(
            json.dumps(
                {
                    "session_dir": str(session),
                    "lease_path": str(prepared_lease_path),
                    "DS60_K8S_SESSION_DIR": str(session),
                    "credentials_printed": False,
                }
            )
        )
        return 0
    except (KubernetesRefusal, OSError, ValueError, TimeoutError) as exc:
        print(f"Kubernetes preparation refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
