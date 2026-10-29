"""Qualify optional scientific projects from this run's staged native worker digests.

No ordinary worker image is built or published here. Import/build steps may use
scoped registry authentication; runtime qualification deliberately has none.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import selectors
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import docker_release as release  # noqa: E402
from scripts.docker_registry import (  # noqa: E402
    ReleaseError,
    descriptor,
    require_digest,
    same_head,
)
from scripts.scientific_receipts import (  # noqa: E402
    BASES,
    digest,
    observation_checks,
    policy,
    require_runner_cases,
    selected_ordinary,
    source_binding,
    source_manifest,
    validate_base_records,
    validate_receipt,
)


def owned_path(value: Path, root: Path = ROOT) -> Path:
    absolute = value if value.is_absolute() else root / value
    if not absolute.absolute().is_relative_to(root / "work") or ".." in absolute.parts:
        raise ReleaseError("Keep scientific CI evidence under the checkout work directory")
    for parent in (absolute, *absolute.parents):
        if parent.is_symlink():
            raise ReleaseError("Scientific CI paths must not follow links")
        if parent == root:
            break
    return absolute


def capture(
    arguments: list[str], log: Path, *, timeout: int, maximum: int, input_bytes: bytes | None = None
) -> bytes:
    """Bound wall time and total output without logging environment or credentials."""
    log.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        arguments,
        stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    selector = selectors.DefaultSelector()
    output = bytearray()
    try:
        if input_bytes is not None:
            assert process.stdin is not None
            process.stdin.write(input_bytes)
            process.stdin.close()
        assert process.stdout is not None
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + timeout
        with log.open("wb") as stream:
            while selector.get_map():
                if time.monotonic() >= deadline:
                    raise ReleaseError("Scientific operation exceeded its deadline")
                for key, _ in selector.select(0.5):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    if len(output) + len(chunk) > maximum:
                        raise ReleaseError("Scientific operation output exceeded its bound")
                    output.extend(chunk)
                    stream.write(chunk)
            code = process.wait(timeout=max(0.1, deadline - time.monotonic()))
        if code != 0:
            raise ReleaseError(
                f"Scientific operation failed with exit code {code}; "
                "inspect retained diagnostic log"
            )
        return bytes(output)
    finally:
        selector.close()
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        if process.stdout is not None:
            process.stdout.close()


def source_request(root: Path, mapping: dict[str, str]) -> dict[str, str]:
    files = source_manifest(root, mapping)
    result = {}
    for relative in files:
        matching = [
            (source, installed)
            for source, installed in mapping.items()
            if Path(relative).is_relative_to(source)
        ]
        if len(matching) != 1:
            raise ReleaseError("Ambiguous sealed source mapping")
        source, installed = matching[0]
        result[relative] = str(Path(installed) / Path(relative).relative_to(source))
    return result


def observations(output: bytes) -> list[dict[str, Any]]:
    result = []
    for line in output.decode("utf-8").splitlines():
        line = line.removeprefix("DS60_SCIENTIFIC_RESULT ").strip()
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and ("case" in value or "kind" in value):
            result.append(value)
    return result


def docker_run(
    image: str,
    name: str,
    declared: dict[str, Any],
    *,
    entrypoint: str,
    arguments: list[str],
    workdir: str = "/tmp",
    interactive: bool = False,
) -> list[str]:
    resources = declared["resources"]
    return [
        "docker",
        "run",
        "--rm",
        "--init",
        *(["--interactive"] if interactive else []),
        "--pull",
        "never",
        "--name",
        name,
        "--hostname",
        "ds60-scientific",
        "--add-host",
        "ds60-scientific:127.0.0.1",
        "--network",
        "none",
        "--user",
        "65534:65534",
        "--memory",
        resources["memory"],
        "--cpus",
        str(resources["cpus"]),
        "--pids-limit",
        str(resources["pids"]),
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--read-only",
        "--tmpfs",
        f"/tmp:rw,exec,nosuid,size={resources['scratch_bytes']}",
        "--env",
        "HOME=/tmp",
        "--env",
        "GLOO_SOCKET_IFNAME=lo",
        "--env",
        "JAVA_TOOL_OPTIONS=-Duser.home=/tmp -Divy.home=/tmp/ivy "
        "-XX:ActiveProcessorCount=2 -XX:ParallelGCThreads=2 -XX:ConcGCThreads=1",
        "--workdir",
        workdir,
        "--entrypoint",
        entrypoint,
        require_digest(image),
        *arguments,
    ]


def import_bases(
    context: release.Context,
    profiles: dict[str, release.Profile],
    receipts: Path,
    architecture: str,
    registry: Any,
    docker: release.Docker,
    root: Path = ROOT,
) -> dict[str, Any]:
    declared = policy(root)
    if len(profiles) != declared["ordinary_profile_count"]:
        raise ReleaseError(
            "Scientific gate must preserve the complete declared ordinary-image release"
        )
    docker.native(architecture)
    natives = release.promotion_inputs(receipts, context, profiles, registry, root)
    selected = selected_ordinary(receipts, context, profiles, root)
    records = {}
    for key in sorted(BASES):
        original = selected[(declared["base_profiles"][key], architecture)]
        image = next(row for row in original["images"] if row["profile"] == key)
        native = natives[key][architecture]
        if not same_head(registry.head(native.digest), native):
            raise ReleaseError("Qualified scientific native image is unavailable")
        native_manifest = registry.get(native.digest)
        config = release.config_digest(native_manifest)
        if image["config_digest"] is not None and image["config_digest"] != config:
            raise ReleaseError("Scientific image config changed after ordinary qualification")
        pulled = docker.pull(context.repository, native.digest, architecture)
        inspected = release.inspected_image(pulled, profiles[key], context, architecture)
        if inspected["tested_image_id"] not in {native.digest, config}:
            raise ReleaseError("Imported image differs from qualified native/config identity")
        if (
            inspected["local_descriptor"] is not None
            and descriptor(inspected["local_descriptor"]) != native
        ):
            raise ReleaseError("Imported scientific base descriptor differs")
        records[key] = {
            "receipt": original,
            "receipt_sha256": digest(original),
            "reference": context.repository + "@" + native.digest,
            "local_image_id": inspected["tested_image_id"],
            "config_digest": config,
        }
    validate_base_records(records, context, architecture, profiles, natives, declared, root)
    return {
        "schema_version": 1,
        "kind": "ds60-scientific-bases",
        "context": asdict(context),
        "architecture": architecture,
        "base_images": records,
        "seed_native_digests": {key: natives[key][architecture].digest for key in release.SEEDS},
        "seed_native_descriptors": {
            image["profile"]: image["native"]
            for image in selected[("python-core", architecture)]["images"]
        },
        "policy_sha256": digest(declared),
        "source_manifest_sha256": source_binding(root, declared),
    }


def load_bases(
    path: Path, context: release.Context, architecture: str, root: Path = ROOT
) -> dict[str, Any]:
    raw = release.read_json(path)
    release.bound_context(raw, context)
    declared = policy(root)
    if (
        raw.get("kind") != "ds60-scientific-bases"
        or raw.get("schema_version") != 1
        or raw.get("architecture") != architecture
        or raw.get("policy_sha256") != digest(declared)
        or raw.get("source_manifest_sha256") != source_binding(root, declared)
    ):
        raise ReleaseError(
            "Scientific base import does not match this source/policy/native attempt"
        )
    expected_fields = {
        "schema_version",
        "kind",
        "context",
        "architecture",
        "base_images",
        "seed_native_digests",
        "seed_native_descriptors",
        "policy_sha256",
        "source_manifest_sha256",
    }
    if (
        set(raw) != expected_fields
        or set(raw.get("base_images", {})) != BASES
        or type(raw["schema_version"]) is not int
    ):
        raise ReleaseError("Scientific base import is incomplete")
    if (
        set(raw["seed_native_descriptors"]) != release.SEEDS
        or set(raw["seed_native_digests"]) != release.SEEDS
    ):
        raise ReleaseError("Scientific base import lacks its exact App/Core binding")
    natives: dict[str, dict[str, Any]] = {}
    for key, record in raw["base_images"].items():
        images = [row for row in record["receipt"]["images"] if row["profile"] == key]
        if len(images) != 1:
            raise ReleaseError("Scientific imported profile selection changed")
        natives[key] = {architecture: release.native_descriptor(images[0]["native"], architecture)}
    for key, record in raw["seed_native_descriptors"].items():
        native = release.native_descriptor(record, architecture)
        if native.digest != raw["seed_native_digests"][key]:
            raise ReleaseError("Scientific seed descriptor changed")
        natives[key] = {architecture: native}
    validate_base_records(
        raw["base_images"], context, architecture, release.catalog(root), natives, declared, root
    )
    return raw


def image_id(docker: release.Docker, reference: str, architecture: str) -> str:
    raw = docker.inspect(reference)
    if raw.get("Os") != "linux" or raw.get("Architecture") != architecture:
        raise ReleaseError("Scientific image was not built for the native runner")
    return require_digest(raw.get("Id"))


def owner_labels(context: release.Context, architecture: str) -> dict[str, str]:
    return {
        "io.ds60.scientific.owner": f"{context.run_id}.{context.run_attempt}.{architecture}",
        "io.ds60.scientific.revision": context.revision,
    }


def cleanup_owned_images(
    context: release.Context, architecture: str, docker: release.Docker
) -> None:
    """Retire only this job's explicitly labeled ephemeral project tags, never volumes or bases."""
    for suffix in ("spark-torch", "spark-tmb", "spark-tmb-dependencies"):
        tag = f"ds60-scientific-{context.run_id}-{context.run_attempt}-{architecture}-{suffix}"
        present = docker.output(
            ["image", "ls", "--filter", "reference=" + tag, "--format", "{{.ID}}"]
        )
        if not present.strip():
            continue
        raw = docker.inspect(tag)
        labels = raw.get("Config", {}).get("Labels", {})
        if any(
            labels.get(key) != value for key, value in owner_labels(context, architecture).items()
        ):
            raise ReleaseError(
                "Refusing to remove an image without this scientific job's owner labels"
            )
        docker.output(["image", "rm", "--no-prune", tag])


def build_project(
    project: str,
    context: release.Context,
    architecture: str,
    bases: dict[str, Any],
    directory: Path,
    docker: release.Docker,
    root: Path = ROOT,
) -> dict[str, Any]:
    declared = policy(root)
    if project not in {"spark-torch", "spark-tmb"}:
        raise ReleaseError("Build only the two scientific project images")
    require_runner_cases(root, project, declared["projects"][project])
    docker.native(architecture)
    for record in bases["base_images"].values():
        if image_id(docker, record["reference"], architecture) != record["local_image_id"]:
            raise ReleaseError("Qualified imported base changed before build")
    tag = f"ds60-scientific-{context.run_id}-{context.run_attempt}-{architecture}-{project}"

    def reference(key: str) -> str:
        return str(bases["base_images"][key]["reference"])

    preparation = None
    if project == "spark-torch":
        arguments = {
            "SPARK_IMAGE": reference("spark-local-python"),
            "TORCH_IMAGE": reference("llm-torch-cpu"),
        }
        inputs = {key: reference(key) for key in ("spark-local-python", "llm-torch-cpu")}
    elif project == "spark-tmb":
        dependency_tag = tag + "-dependencies"
        dependency = root / "courses/tmb-modeling/projects/tmb-local"
        command = [
            "docker",
            "build",
            "--pull=false",
            "--progress=plain",
            "--platform",
            "linux/" + architecture,
            "--label",
            "io.ds60.scientific.owner="
            + owner_labels(context, architecture)["io.ds60.scientific.owner"],
            "--label",
            "io.ds60.scientific.revision=" + context.revision,
            "--target",
            "dependencies",
            "--build-arg",
            "R_BASE_IMAGE=" + reference("r-statistics"),
            "-f",
            str(dependency / "Dockerfile"),
            "-t",
            dependency_tag,
            str(dependency),
        ]
        capture(
            command,
            directory / "tmb-dependencies-build.log",
            timeout=3600,
            maximum=declared["resources"]["maximum_log_bytes"],
        )
        dependency_id = image_id(docker, dependency_tag, architecture)
        preparation = {
            "target": "dependencies",
            "image_id": dependency_id,
            "r_base": reference("r-statistics"),
            "log_sha256": "sha256:"
            + hashlib.sha256((directory / "tmb-dependencies-build.log").read_bytes()).hexdigest(),
        }
        arguments = {
            "SPARK_IMAGE": reference("spark-local-python"),
            "JAVA_IMAGE": reference("java21"),
            "TMB_IMAGE": dependency_tag,
        }
        inputs = {key: reference(key) for key in ("spark-local-python", "r-statistics", "java21")}
    else:
        raise ReleaseError("Build only the two scientific project images")
    command = [
        "docker",
        "build",
        "--pull=false",
        "--progress=plain",
        "--platform",
        "linux/" + architecture,
        "--label",
        "io.ds60.scientific.owner="
        + owner_labels(context, architecture)["io.ds60.scientific.owner"],
        "--label",
        "io.ds60.scientific.revision=" + context.revision,
        "-f",
        str(root / f"courses/advanced-spark-modeling/projects/{project}/Dockerfile"),
        "-t",
        tag,
    ]
    for key, value in sorted(arguments.items()):
        command.extend(["--build-arg", key + "=" + value])
    command.append(str(root))
    capture(
        command,
        directory / f"{project}-build.log",
        timeout=5400,
        maximum=declared["resources"]["maximum_log_bytes"],
    )
    result = {
        "schema_version": 1,
        "kind": "ds60-scientific-build",
        "context": asdict(context),
        "architecture": architecture,
        "project": project,
        "image_id": image_id(docker, tag, architecture),
        "build_inputs": inputs,
        "build_args": arguments,
        "preparation": preparation,
        "source_manifest_sha256": source_binding(root, declared),
    }
    release.write_json(directory / f"{project}-build.json", result)
    return result


def qualify_project(
    project: str,
    context: release.Context,
    architecture: str,
    directory: Path,
    docker: release.Docker,
    root: Path = ROOT,
) -> list[dict[str, Any]]:
    declared = policy(root)
    docker.native(architecture)
    built = release.read_json(directory / f"{project}-build.json")
    release.bound_context(built, context)
    if (
        built.get("project") != project
        or built.get("architecture") != architecture
        or built.get("source_manifest_sha256") != source_binding(root, declared)
    ):
        raise ReleaseError("Scientific build source or architecture changed")
    identity = image_id(docker, built["image_id"], architecture)
    targets = [project] if project == "spark-torch" else [project, "tmb-public-api", "tmb-cpp-api"]
    reports = []
    for target in targets:
        specification = declared["projects"][target]
        require_runner_cases(root, target, specification)
        name = f"ds60-sci-{context.run_id}-{context.run_attempt}-{architecture}-{target}"
        try:
            request = {
                "sources": source_request(root, specification["maps"]),
                "runtime": list(specification["runtime"]),
            }
            command = docker_run(
                identity,
                name,
                declared,
                entrypoint="python",
                arguments=["-c", (root / "scripts/scientific_image_probe.py").read_text()],
                interactive=True,
            )
            output = capture(
                command,
                directory / f"{target}-source-readback.log",
                timeout=120,
                maximum=4 * 1024 * 1024,
                input_bytes=json.dumps(request).encode(),
            )
            probe = json.loads(output.decode().splitlines()[-1])
            expected = source_manifest(root, specification["maps"])
            if (
                probe.get("sources") != expected
                or probe["runtime"].get("architecture") != architecture
                or probe["runtime"].get("system") != "Linux"
            ):
                raise ReleaseError("Scientific sealed image/source/platform readback differs")
            if target == "spark-torch":
                entrypoint, arguments = "python", ["/opt/spark-torch/runner.py", "check"]
            elif target == "spark-tmb":
                entrypoint, arguments = "python", ["/opt/spark-tmb/runner.py", "check"]
            elif target == "tmb-public-api":
                entrypoint, arguments = (
                    "Rscript",
                    ["--vanilla", "/opt/tmb-project/tests/public_api.R"],
                )
            else:
                entrypoint, arguments = (
                    "Rscript",
                    [
                        "--vanilla",
                        "/opt/tmb-cpp-api/check.R",
                        "/opt/tmb-cpp-api",
                        "/tmp/tmb-cpp-api-build",
                    ],
                )
            log = directory / f"{target}-check.log"
            output = capture(
                docker_run(
                    identity,
                    name,
                    declared,
                    entrypoint=entrypoint,
                    arguments=arguments,
                    workdir="/opt/tmb-project" if target == "tmb-public-api" else "/tmp",
                ),
                log,
                timeout=5400,
                maximum=declared["resources"]["maximum_log_bytes"],
            )
            observed = observations(output)
            checks = observation_checks(target, observed, declared, architecture, root)
            reports.append(
                {
                    "id": target,
                    "image_id": identity,
                    "build_inputs": built["build_inputs"],
                    "preparation": built["preparation"],
                    "source_manifest_sha256": digest(expected),
                    "sealed_source_manifest_sha256": digest(probe["sources"]),
                    "runtime": probe["runtime"],
                    "fixtures": specification["fixtures"],
                    "checks": checks,
                    "log_sha256": "sha256:" + hashlib.sha256(output).hexdigest(),
                    "observations_sha256": digest(observed),
                    "execution_scope": "native-single-host-cpu-offline",
                }
            )
        finally:
            subprocess.run(
                ["docker", "rm", "-f", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=30,
            )
    release.write_json(
        directory / f"{project}-checks.json",
        {
            "context": asdict(context),
            "architecture": architecture,
            "projects": reports,
            "preparation": built["preparation"],
        },
    )
    return reports


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("import-bases", "build", "qualify", "complete", "cleanup")
    )
    parser.add_argument("--gate", required=True, type=Path)
    parser.add_argument("--architecture", required=True, choices=release.ARCHITECTURES)
    parser.add_argument("--receipts-dir", type=Path)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--project", choices=("spark-torch", "spark-tmb"))
    args = parser.parse_args(argv)
    raw_gate = release.read_json(args.gate)
    if "selection" in raw_gate:
        raise ReleaseError("Scientific gate is only for complete ordinary releases")
    context, profiles, mode = release.load_gate(args.gate)
    if mode not in {"build", "promote-existing"}:
        raise ReleaseError("Scientific work requires an active full release")
    directory = owned_path(args.directory)
    directory.mkdir(parents=True, exist_ok=True)
    docker = release.Docker()
    docker.native(args.architecture)
    bases_path = directory / "bases.json"
    if args.command == "cleanup":
        cleanup_owned_images(context, args.architecture, docker)
        print("Removed only labeled images owned by this scientific job")
        return 0
    if args.command == "import-bases":
        if args.receipts_dir is None:
            raise ReleaseError("Qualified ordinary receipts are required")
        value = import_bases(
            context,
            profiles,
            args.receipts_dir,
            args.architecture,
            release.registry_for(context),
            docker,
        )
        release.write_json(bases_path, value)
    else:
        bases = load_bases(bases_path, context, args.architecture)
        if args.command == "build":
            if args.project is None:
                raise ReleaseError("Choose a scientific project")
            build_project(args.project, context, args.architecture, bases, directory, docker)
        elif args.command == "qualify":
            if args.project is None:
                raise ReleaseError("Choose a scientific project")
            qualify_project(args.project, context, args.architecture, directory, docker)
        else:
            declared = policy()
            reports = []
            for key in ("spark-torch", "spark-tmb"):
                result = release.read_json(directory / f"{key}-checks.json")
                release.bound_context(result, context)
                if result["architecture"] != args.architecture:
                    raise ReleaseError("Scientific reports mix architectures")
                reports.extend(result["projects"])
            result = {
                "schema_version": 1,
                "kind": "ds60-scientific-projects",
                "context": asdict(context),
                "architecture": args.architecture,
                "runner": declared["architectures"][args.architecture],
                "passed": True,
                "complete": True,
                "policy_sha256": digest(declared),
                "source_manifest_sha256": source_binding(ROOT, declared),
                "seed_native_digests": bases["seed_native_digests"],
                "base_images": bases["base_images"],
                "projects": reports,
                "evidence_manifest_sha256": digest(reports),
                "machine": {
                    "host_system": platform.system(),
                    "host_architecture": args.architecture,
                    "docker_os": "linux",
                    "docker_architecture": args.architecture,
                },
            }
            # Reconstruct only already-validated selected descriptors for local final validation.
            natives = {
                key: {
                    args.architecture: release.native_descriptor(
                        next(row for row in value["receipt"]["images"] if row["profile"] == key)[
                            "native"
                        ],
                        args.architecture,
                    )
                }
                for key, value in bases["base_images"].items()
            }
            for key, value in bases["seed_native_descriptors"].items():
                natives[key] = {
                    args.architecture: release.native_descriptor(value, args.architecture)
                }
            validate_receipt(result, context, profiles, natives)
            if (
                len(json.dumps(result, sort_keys=True, indent=2, allow_nan=False).encode()) + 1
                > release.MAX_RECEIPT
            ):
                raise ReleaseError(
                    "Scientific promotion receipt exceeds its bounded artifact contract"
                )
            release.write_json(directory / "scientific-receipt.json", result)
    print("Scientific qualification operation completed: " + args.command)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ReleaseError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        print(
            "Scientific qualification failed; inspect bounded retained diagnostics, "
            "then rerun this native job",
            file=sys.stderr,
        )
        raise SystemExit(2) from None
