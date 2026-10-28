#!/usr/bin/env python3
"""GitHub-only native image qualification, digest staging and ordered app-pointer promotion.

Registry metadata uses stdlib HTTPS, Docker moves layers, and artifacts contain
only bounded source/digest receipts. No command reads Docker credential files
or persists supplied tokens.
Version tags are checked before writes. Repository-wide workflow concurrency is
required because Registry v2 does not provide a portable compare-and-swap tag API.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import selectors
import subprocess
import sys
import tempfile
import time
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.docker_registry import (  # noqa: E402
    IMAGE_TYPES,
    INDEX_TYPES,
    NAMESPACE,
    OCI_INDEX,
    Descriptor,
    Manifest,
    Registry,
    ReleaseError,
    descriptor,
    json_object,
    require_digest,
    same_head,
    sha256,
)

ARCHITECTURES = ("amd64", "arm64")
SEEDS = frozenset({"app", "python-core"})
VERSION = re.compile(r"(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})\Z")
SHA = re.compile(r"[a-f0-9]{40}\Z")
HASH = re.compile(r"[a-f0-9]{64}\Z")
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,39}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
MAX_RECEIPT = 256 * 1024
MAX_REPORT = 16 * 1024 * 1024
SCHEMA = "io.ds60.release.schema"
PROFILE = "io.ds60.release.profile"
REVISION = "org.opencontainers.image.revision"
RELEASE_VERSION = "org.opencontainers.image.version"
SOURCE = "org.opencontainers.image.source"


@dataclass(frozen=True)
class Profile:
    profile: str
    local_repository: str
    suffix: str


@dataclass(frozen=True)
class Context:
    namespace: str
    repository: str
    source_repository: str
    version: str
    revision: str
    run_id: str
    run_attempt: str


def release_version(value: Any) -> str:
    if not isinstance(value, str) or VERSION.fullmatch(value) is None:
        raise ReleaseError("Publication requires a stable canonical major.minor.patch version")
    return value


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(item) for item in release_version(value).split("."))


def positive_identity(value: Any) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[1-9][0-9]{0,19}", value) is None:
        raise ReleaseError("Invalid workflow run or attempt identity")
    return value


def context_record(value: Any) -> Context:
    fields = set(Context.__dataclass_fields__)
    if not isinstance(value, dict) or set(value) != fields:
        raise ReleaseError("Invalid release context schema")
    if any(not isinstance(value[name], str) for name in fields):
        raise ReleaseError("Release context fields must be strings")
    if (
        NAMESPACE.fullmatch(value["namespace"]) is None
        or value["repository"] != value["namespace"] + "/ds60sqlpy"
    ):
        raise ReleaseError("Release repository does not match its declared Docker Hub namespace")
    if (
        REPOSITORY.fullmatch(value["source_repository"]) is None
        or SHA.fullmatch(value["revision"]) is None
    ):
        raise ReleaseError("Invalid source repository or revision")
    release_version(value["version"])
    positive_identity(value["run_id"])
    positive_identity(value["run_attempt"])
    return Context(**value)


def read_json(path: Path, maximum: int = MAX_RECEIPT) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise ReleaseError("Metadata input must be a bounded ordinary file")
    with path.open("rb") as stream:
        return json_object(stream.read(maximum + 1), maximum)


def write_json(path: Path, value: dict[str, Any]) -> None:
    data = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ReleaseError("Receipt output must not be a symbolic link")
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = stream.name
            stream.write(data)
        Path(temporary).replace(path)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def catalog(root: Path = ROOT) -> dict[str, Profile]:
    path = root / "docker/classroom-images.tsv"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 64_000:
        raise ReleaseError("Invalid image catalog")
    result: dict[str, Profile] = {}
    seen_ids: set[str] = set()
    seen_suffixes: set[str] = set()
    for line in path.read_text("utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 6:
            raise ReleaseError("Image catalog rows must have six fields")
        profile, _service, local, suffix, _variable, kind = fields
        if (
            IDENTIFIER.fullmatch(profile) is None
            or IDENTIFIER.fullmatch(suffix) is None
            or re.fullmatch(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", local) is None
            or profile in seen_ids
            or suffix in seen_suffixes
            or kind not in {"app", "ordinary", "gpu"}
            or (kind == "app") != (profile == "app")
        ):
            raise ReleaseError("Image catalog is ambiguous or malformed")
        seen_ids.add(profile)
        seen_suffixes.add(suffix)
        if kind != "gpu":
            result[profile] = Profile(profile, local, suffix)
    if not result.keys() >= SEEDS or len(result) < 2:
        raise ReleaseError("Image catalog needs the app and Core seed")
    return result


def source_version(root: Path = ROOT) -> str:
    try:
        with (root / "pyproject.toml").open("rb") as stream:
            return release_version(tomllib.load(stream)["project"]["version"])
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        raise ReleaseError("Cannot read the checkout release version") from None


def git_output(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False, timeout=30
    )
    if result.returncode:
        raise ReleaseError("Cannot validate the checked-out source revision")
    return result.stdout.strip()


def github_context(root: Path, namespace: str) -> Context:
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_EVENT_NAME") != "push"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
    ):
        raise ReleaseError("Publication is permitted only for a GitHub push to main")
    values = {
        "namespace": namespace,
        "repository": namespace + "/ds60sqlpy",
        "source_repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "version": source_version(root),
        "revision": os.environ.get("GITHUB_SHA", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
    }
    context = context_record(values)
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path:
        raise ReleaseError("The GitHub push event payload is required")
    event = read_json(Path(event_path), MAX_REPORT)
    head = event.get("head_commit")
    if (
        event.get("ref") != "refs/heads/main"
        or event.get("deleted") is True
        or not isinstance(head, dict)
        or head.get("id") != context.revision
        or not isinstance(head.get("message"), str)
        or "[publish-docker]" not in head["message"]
        or not isinstance(event.get("repository"), dict)
        or event["repository"].get("full_name") != context.source_repository
    ):
        raise ReleaseError("The main push HEAD commit must contain [publish-docker]")
    if git_output(
        root, ["rev-parse", "HEAD"]
    ) != context.revision or "[publish-docker]" not in git_output(
        root, ["log", "-1", "--format=%B"]
    ):
        raise ReleaseError("Checkout HEAD differs from the marked push commit")
    if git_output(root, ["status", "--porcelain", "--untracked-files=normal"]):
        raise ReleaseError("Release source must be a clean exact checkout")
    return context


def version_tag(profile: Profile, version: str) -> str:
    return version if profile.profile == "app" else version + "-" + profile.suffix


def latest_tag(profile: Profile) -> str:
    return "latest" if profile.profile == "app" else "latest-" + profile.suffix


def candidate_tag(context: Context, profile: str, architecture: str) -> str:
    if IDENTIFIER.fullmatch(profile) is None or architecture not in ARCHITECTURES:
        raise ReleaseError("Invalid candidate image identity")
    tag = f"ci-{context.revision}-{context.run_id}-{context.run_attempt}-{profile}-{architecture}"
    if len(tag) > 128:
        raise ReleaseError("Candidate image identity exceeds Docker tag limits")
    return tag


def native_descriptor(value: Any, architecture: str) -> Descriptor:
    result = descriptor(value, image_only=True)
    if value.get("platform") != {"os": "linux", "architecture": architecture}:
        raise ReleaseError("Native image descriptor platform does not match qualification")
    return result


def config_digest(manifest: Manifest) -> str:
    if manifest.descriptor.media_type not in IMAGE_TYPES or not isinstance(
        manifest.document.get("config"), dict
    ):
        raise ReleaseError("Native manifest has no image config")
    return require_digest(manifest.document["config"].get("digest"))


def select_native(manifest: Manifest, architecture: str) -> Descriptor:
    if manifest.descriptor.media_type in IMAGE_TYPES:
        return manifest.descriptor
    if manifest.descriptor.media_type not in INDEX_TYPES:
        raise ReleaseError("Unsupported pushed root descriptor")
    entries = manifest.document.get("manifests")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 16:
        raise ReleaseError("Pushed image index has invalid entries")
    selected: list[Descriptor] = []
    attestations: list[dict[str, Any]] = []
    for entry in entries:
        item = descriptor(entry, image_only=True)
        platform_record = entry.get("platform")
        if (
            isinstance(platform_record, dict)
            and platform_record.get("os") == "linux"
            and platform_record.get("architecture") == architecture
        ):
            if set(platform_record) - {"os", "architecture", "variant"} or platform_record.get(
                "variant", ""
            ) not in ({"", "v8"} if architecture == "arm64" else {""}):
                raise ReleaseError("Unsupported native platform variant")
            selected.append(item)
        elif platform_record == {"os": "unknown", "architecture": "unknown"}:
            annotations = entry.get("annotations", {})
            if (
                not isinstance(annotations, dict)
                or annotations.get("vnd.docker.reference.type") != "attestation-manifest"
            ):
                raise ReleaseError("Unrecognized auxiliary image descriptor")
            attestations.append(annotations)
        else:
            raise ReleaseError("Candidate contains another or unspecified native platform")
    if len(selected) != 1:
        raise ReleaseError("Candidate must contain exactly one tested native image")
    for annotation in attestations:
        if annotation.get("vnd.docker.reference.digest") != selected[0].digest:
            raise ReleaseError("Attestation descriptor refers to another native image")
    return selected[0]


def index_body(context: Context, profile: str, natives: dict[str, Descriptor]) -> bytes:
    if set(natives) != set(ARCHITECTURES):
        raise ReleaseError("Promotion requires both native architectures")
    body = {
        "schemaVersion": 2,
        "mediaType": OCI_INDEX,
        "manifests": [
            {**natives[arch].record(), "platform": {"os": "linux", "architecture": arch}}
            for arch in ARCHITECTURES
        ],
        "annotations": {
            SCHEMA: "1",
            PROFILE: profile,
            REVISION: context.revision,
            RELEASE_VERSION: context.version,
            SOURCE: "https://github.com/" + context.source_repository,
        },
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def published_index(
    manifest: Manifest, profile: str, source_repository: str
) -> tuple[str, str, dict[str, Descriptor]]:
    if (
        manifest.descriptor.media_type != OCI_INDEX
        or manifest.document.get("mediaType") != OCI_INDEX
    ):
        raise ReleaseError("Existing release tag is not a managed OCI index")
    annotations = manifest.document.get("annotations")
    if (
        not isinstance(annotations, dict)
        or annotations.get(SCHEMA) != "1"
        or annotations.get(PROFILE) != profile
        or annotations.get(SOURCE) != "https://github.com/" + source_repository
    ):
        raise ReleaseError("Existing release tag has different ownership metadata")
    version = release_version(annotations.get(RELEASE_VERSION))
    revision = annotations.get(REVISION)
    if not isinstance(revision, str) or SHA.fullmatch(revision) is None:
        raise ReleaseError("Existing release revision is invalid")
    entries = manifest.document.get("manifests")
    if not isinstance(entries, list) or len(entries) != 2:
        raise ReleaseError("Existing release does not contain both native platforms")
    natives: dict[str, Descriptor] = {}
    for entry in entries:
        platform_record = entry.get("platform") if isinstance(entry, dict) else None
        arch = platform_record.get("architecture") if isinstance(platform_record, dict) else None
        if arch not in ARCHITECTURES or arch in natives:
            raise ReleaseError("Existing release platforms are incomplete or duplicated")
        natives[arch] = native_descriptor(entry, arch)
    return version, revision, natives


def load_published(registry: Registry, profile: Profile, context: Context) -> Manifest | None:
    tag = version_tag(profile, context.version)
    head = registry.head(tag)
    if head is None:
        return None
    value = registry.get(head.digest)
    if not same_head(head, value.descriptor):
        raise ReleaseError("Version tag changed during inspection")
    version, revision, natives = published_index(value, profile.profile, context.source_repository)
    if any(not same_head(registry.head(item.digest), item) for item in natives.values()):
        raise ReleaseError("Existing immutable version references a missing native image")
    if version != context.version or revision != context.revision:
        raise ReleaseError(
            "Version is occupied by another revision; bump the patch version before publication"
        )
    return value


def gate_release(
    context: Context, profiles: dict[str, Profile], registry: Registry
) -> dict[str, Any]:
    published: dict[str, Manifest] = {}
    for key, profile in profiles.items():
        value = load_published(registry, profile, context)
        if value is not None:
            published[key] = value
    if published and set(published) != set(profiles):
        raise ReleaseError(
            "Version tags are incomplete or occupied. Retry the original failed promotion "
            "with its successful receipts, or bump the patch version; do not rebuild over them."
        )
    latest = registry.head("latest")
    latest_value = registry.get(latest.digest) if latest is not None else None
    latest_version = None
    if latest_value is not None:
        latest_version, latest_revision, _ = published_index(
            latest_value, "app", context.source_repository
        )
        if latest_version == context.version and latest_revision != context.revision:
            raise ReleaseError(
                "Latest claims this version for another revision; bump the patch version"
            )
    mode = "build"
    if published:
        mode = "promote-existing"
        if (
            latest_version is not None
            and version_tuple(latest_version) > version_tuple(context.version)
            or (
                latest is not None
                and latest.digest == published["app"].descriptor.digest
                and all(
                    same_head(registry.head(latest_tag(profile)), published[key].descriptor)
                    for key, profile in profiles.items()
                )
            )
        ):
            mode = "noop"
    return {
        "schema_version": 1,
        "kind": "ds60-release-gate",
        "context": asdict(context),
        "mode": mode,
        "profiles": [asdict(p) for p in profiles.values()],
    }


def load_gate(path: Path, root: Path = ROOT) -> tuple[Context, dict[str, Profile], str]:
    raw = read_json(path)
    if (
        set(raw) != {"schema_version", "kind", "context", "mode", "profiles"}
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or raw.get("kind") != "ds60-release-gate"
        or raw.get("mode") not in {"build", "promote-existing", "noop"}
    ):
        raise ReleaseError("Invalid release gate receipt")
    context = context_record(raw["context"])
    current = github_context(root, context.namespace)
    bound_context({"context": asdict(context)}, current, earlier=True)
    profiles = catalog(root)
    if raw["profiles"] != [asdict(p) for p in profiles.values()]:
        raise ReleaseError("Image catalog changed after the publication gate")
    return current, profiles, str(raw["mode"])


class Docker:
    def output(self, args: list[str], *, timeout: int = 120) -> str:
        process: subprocess.Popen[bytes] | None = None
        selector = selectors.DefaultSelector()
        captured = bytearray()
        total = 0
        try:
            process = subprocess.Popen(
                ["docker", *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert process.stdout is not None and process.stderr is not None
            selector.register(process.stdout, selectors.EVENT_READ, "stdout")
            selector.register(process.stderr, selectors.EVENT_READ, "stderr")
            deadline = time.monotonic() + timeout
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ReleaseError("Docker metadata request exceeded its deadline")
                for key, _ in selector.select(min(remaining, 1)):
                    chunk = os.read(key.fd, 65_536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    total += len(chunk)
                    if total > 8 * 1024 * 1024:
                        raise ReleaseError("Docker metadata output exceeds limits")
                    if key.data == "stdout":
                        captured.extend(chunk)
            status = process.wait(timeout=max(0.1, deadline - time.monotonic()))
            if status:
                raise ReleaseError(f"Docker metadata operation failed with exit code {status}")
            return captured.decode("utf-8")
        except (OSError, subprocess.TimeoutExpired, UnicodeError):
            raise ReleaseError("Docker metadata operation could not complete") from None
        finally:
            selector.close()
            if process is not None:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=10)
                if process.stdout is not None:
                    process.stdout.close()
                if process.stderr is not None:
                    process.stderr.close()

    def inspect(self, reference: str) -> dict[str, Any]:
        raw = json_object(
            self.output(["image", "inspect", "--format", "{{json .}}", reference]).encode()
        )
        return raw

    def native(self, architecture: str) -> None:
        aliases = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
        if (
            architecture not in ARCHITECTURES
            or platform.system() != "Linux"
            or aliases.get(platform.machine().lower()) != architecture
        ):
            raise ReleaseError("Qualification requires the matching native Linux runner")
        engine = self.output(
            ["info", "--format", "{{.OSType}} {{.Architecture}}"], timeout=30
        ).split()
        if (
            len(engine) != 2
            or engine[0] != "linux"
            or aliases.get(engine[1].lower()) != architecture
        ):
            raise ReleaseError("Docker engine does not match the native qualification architecture")

    def tag(self, identity: str, target: str) -> None:
        self.output(["image", "tag", require_digest(identity), target])

    def transfer(self, args: list[str], *, timeout: int) -> None:
        # Transfers can emit unbounded progress, so do not collect it as metadata.
        # Diagnostics are controlled status messages, never untrusted auth bodies.
        try:
            result = subprocess.run(
                ["docker", *args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=timeout,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise ReleaseError(
                "Docker transfer outcome is unverified; inspect the candidate before retrying"
            ) from None
        if result.returncode:
            raise ReleaseError(f"Docker transfer failed with exit code {result.returncode}")

    def push(self, target: str) -> None:
        self.transfer(["image", "push", "--quiet", target], timeout=1800)

    def pull(self, repository: str, digest: str, architecture: str) -> dict[str, Any]:
        reference = repository + "@" + require_digest(digest)
        self.transfer(
            ["image", "pull", "--quiet", "--platform", "linux/" + architecture, reference],
            timeout=900,
        )
        return self.inspect(reference)


def inspected_image(
    raw: dict[str, Any], profile: Profile, context: Context, architecture: str
) -> dict[str, Any]:
    identity = require_digest(raw.get("Id"))
    if raw.get("Os") != "linux" or raw.get("Architecture") != architecture:
        raise ReleaseError("Local image does not match the tested native platform")
    root_descriptor = None
    if raw.get("Descriptor") is not None:
        root_descriptor = descriptor(raw["Descriptor"]).record()
    labels = raw.get("Config", {}).get("Labels", {})
    if profile.profile in SEEDS and (
        not isinstance(labels, dict) or labels.get(RELEASE_VERSION) != context.version
    ):
        raise ReleaseError("App/Core image release label must match pyproject.toml")
    return {
        "profile": profile.profile,
        "local_repository": profile.local_repository,
        "tested_image_id": identity,
        "local_descriptor": root_descriptor,
    }


def release_groups(profiles: dict[str, Profile], root: Path = ROOT) -> dict[str, frozenset[str]]:
    raw = read_json(root / "docker/ci-profile-groups.json")
    if (
        set(raw) != {"schema_version", "groups"}
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or not isinstance(raw["groups"], list)
    ):
        raise ReleaseError("Invalid release qualification groups")
    result: dict[str, frozenset[str]] = {}
    seen: set[str] = set()
    for row in raw["groups"]:
        if (
            not isinstance(row, dict)
            or set(row) != {"id", "profiles"}
            or not isinstance(row["id"], str)
            or IDENTIFIER.fullmatch(row["id"]) is None
            or row["id"] in result
            or not isinstance(row["profiles"], list)
            or not row["profiles"]
        ):
            raise ReleaseError("Invalid release qualification group")
        members = row["profiles"]
        if any(
            not isinstance(key, str) or key not in profiles or key == "app" or key in seen
            for key in members
        ) or len(members) != len(set(members)):
            raise ReleaseError("Release qualification groups overlap or include unknown images")
        seen.update(members)
        result[row["id"]] = frozenset(members)
    if seen != set(profiles) - {"app"} or result.get("python-core") != frozenset({"python-core"}):
        raise ReleaseError("Release groups must cover every worker with a separate Core seed")
    result["python-core"] = SEEDS
    return result


def image_group(selected: set[str], profiles: dict[str, Profile], root: Path = ROOT) -> str:
    matches = [
        key for key, members in release_groups(profiles, root).items() if members == selected
    ]
    if len(matches) != 1:
        raise ReleaseError("Inspect exactly one declared native qualification group")
    return matches[0]


def verify_seed_local(
    context: Context,
    profiles: dict[str, Profile],
    receipt: dict[str, Any],
    architecture: str,
    docker: Docker,
    root: Path = ROOT,
) -> dict[str, str]:
    staged_receipt(receipt, context, profiles, root=root)
    if (
        receipt["group"] != "python-core"
        or receipt["architecture"] != architecture
        or {row["profile"] for row in receipt["images"]} != SEEDS
    ):
        raise ReleaseError(
            "Worker qualification requires the selected native app/Core seed receipt"
        )
    bindings = {}
    for image in receipt["images"]:
        key = image["profile"]
        actual = inspected_image(
            docker.inspect(profiles[key].local_repository + ":" + context.version),
            profiles[key],
            context,
            architecture,
        )
        native = descriptor(image["native"], image_only=True)
        accepted = {native.digest, image["config_digest"], image["tested_image_id"]}
        if actual["tested_image_id"] not in accepted:
            raise ReleaseError("Local qualification seed differs from its selected receipt")
        local = actual["local_descriptor"]
        if local is not None and descriptor(local) not in {
            native,
            descriptor(image["candidate_root"]),
        }:
            raise ReleaseError("Local seed descriptor differs from its qualified native/root image")
        bindings[key] = native.digest
    return bindings


def inspect_images(
    context: Context,
    profiles: dict[str, Profile],
    selected: list[str],
    architecture: str,
    docker: Docker,
    *,
    seed: dict[str, Any] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    if not selected or len(selected) != len(set(selected)) or set(selected) - profiles.keys():
        raise ReleaseError("Choose unique ordinary catalog image profiles")
    group = image_group(set(selected), profiles, root)
    docker.native(architecture)
    if group == "python-core":
        if seed is not None:
            raise ReleaseError("The native seed job must not import another seed receipt")
    elif seed is None:
        raise ReleaseError(
            "Worker inspection requires --seed-receipt from its selected native seed"
        )
    else:
        verify_seed_local(context, profiles, seed, architecture, docker, root)
    images = [
        inspected_image(
            docker.inspect(profiles[key].local_repository + ":" + context.version),
            profiles[key],
            context,
            architecture,
        )
        for key in selected
    ]
    return {
        "schema_version": 1,
        "kind": "ds60-tested-images",
        "context": asdict(context),
        "architecture": architecture,
        "group": group,
        "seed_receipt": seed,
        "images": images,
    }


def bound_context(raw: dict[str, Any], expected: Context, *, earlier: bool = False) -> Context:
    recorded = context_record(raw.get("context"))
    left, right = asdict(recorded), asdict(expected)
    old_attempt, current_attempt = int(left.pop("run_attempt")), int(right.pop("run_attempt"))
    if left != right or (
        old_attempt > current_attempt if earlier else old_attempt != current_attempt
    ):
        raise ReleaseError(
            "Receipt belongs to another source/run or an invalid attempt; "
            "use successful artifacts from this run only"
        )
    return recorded


def load_tested(
    path: Path, context: Context, profiles: dict[str, Profile], root: Path = ROOT
) -> dict[str, Any]:
    raw = read_json(path)
    if (
        set(raw)
        != {"schema_version", "kind", "context", "architecture", "group", "seed_receipt", "images"}
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or raw.get("kind") != "ds60-tested-images"
        or raw.get("architecture") not in ARCHITECTURES
    ):
        raise ReleaseError("Invalid pre-qualification image snapshot")
    bound_context(raw, context)
    seen = set()
    if not isinstance(raw["images"], list) or not raw["images"]:
        raise ReleaseError("Image snapshot is empty")
    for image in raw["images"]:
        if not isinstance(image, dict) or set(image) != {
            "profile",
            "local_repository",
            "tested_image_id",
            "local_descriptor",
        }:
            raise ReleaseError("Invalid tested image record")
        key = image["profile"]
        if (
            not isinstance(key, str)
            or key not in profiles
            or key in seen
            or image["local_repository"] != profiles[key].local_repository
        ):
            raise ReleaseError("Image snapshot has an unknown or duplicated profile")
        seen.add(key)
        require_digest(image["tested_image_id"])
        if image["local_descriptor"] is not None:
            descriptor(image["local_descriptor"])
    if raw.get("group") != image_group(seen, profiles, root):
        raise ReleaseError("Image snapshot differs from its declared qualification group")
    if raw["group"] == "python-core":
        if raw.get("seed_receipt") is not None:
            raise ReleaseError("Seed snapshot must not claim an imported seed")
    elif not isinstance(raw.get("seed_receipt"), dict):
        raise ReleaseError("Worker snapshot must retain its selected seed receipt")
    return raw


def source_file(root: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative.startswith("courses/") or "\\" in relative:
        raise ReleaseError("Qualification must name a course source file")
    parts = Path(relative).parts
    if Path(relative).is_absolute() or any(part in {".", ".."} for part in parts):
        raise ReleaseError("Qualification source path escapes the checkout")
    cursor = root
    for part in parts:
        cursor /= part
        if cursor.is_symlink():
            raise ReleaseError("Qualification source must not traverse links")
    if not cursor.is_file() or cursor.stat().st_size > 262_144:
        raise ReleaseError("Qualification source is missing or oversized")
    return cursor


def expected_references(root: Path, required: set[str]) -> dict[str, Any]:
    from scripts.check_module_references import collect_cases

    cases, _ = collect_cases(root, sorted(required))
    return {case.lesson_id: case for case in cases}


def mandatory_ci_checks(group: str) -> frozenset[str]:
    from scripts.ci_classroom import required_checks

    return required_checks(group)


def qualification_records(
    paths: list[Path], context: Context, architecture: str, selected: set[str], root: Path
) -> list[dict[str, Any]]:
    required = (selected - {"app"}) | ({"python-core"} if "app" in selected else set())
    records = []
    expected_cases = expected_references(root, required)
    have_corpus = have_summary = False
    if not paths or len(paths) > 8 or len(set(paths)) != len(paths):
        raise ReleaseError("Supply distinct bounded qualification reports")
    for path in paths:
        report = read_json(path, MAX_REPORT)
        if (
            type(report.get("schema_version")) is not int
            or report["schema_version"] != 1
            or report.get("passed") is not True
            or report.get("complete") is not True
        ):
            raise ReleaseError("Every qualification report must be complete and passed")
        profiles = report.get("profiles")
        if (
            not isinstance(profiles, list)
            or any(not isinstance(item, str) for item in profiles)
            or len(profiles) != len(set(profiles))
            or set(profiles) != required
        ):
            raise ReleaseError("Qualification profiles differ from the tested image selection")
        record: dict[str, Any] = {
            "sha256": sha256(path.read_bytes()),
            "profiles": sorted(required),
            "passed": True,
            "complete": True,
        }
        if "results" in report:
            if have_corpus:
                raise ReleaseError("Supply exactly one complete reference corpus report")
            results = report["results"]
            if (
                not isinstance(results, list)
                or not results
                or type(report.get("selected_cases")) is not int
                or report["selected_cases"] != len(results)
            ):
                raise ReleaseError("Reference corpus cardinality is incomplete")
            seen: set[str] = set()
            covered: set[str] = set()
            for row in results:
                if (
                    not isinstance(row, dict)
                    or not isinstance(row.get("lesson_id"), str)
                    or row["lesson_id"] in seen
                    or row.get("profile") not in required
                    or row.get("status") != "passed"
                    or row.get("worker_status") != "succeeded"
                    or type(row.get("returncode")) is not int
                    or row["returncode"] != 0
                    or row.get("truncated") is not False
                    or not isinstance(row.get("job_id"), str)
                    or re.fullmatch(r"[a-f0-9]{32}", row["job_id"]) is None
                ):
                    raise ReleaseError(
                        "Reference corpus contains missing, duplicate or failed execution evidence"
                    )
                expected_case = expected_cases.get(row["lesson_id"])
                if (
                    expected_case is None
                    or any(
                        row.get(field) != getattr(expected_case, field)
                        for field in (
                            "profile",
                            "source_path",
                            "source_sha256",
                            "language",
                            "learning_mode",
                            "verification_id",
                        )
                    )
                    or row.get("expected_outputs") != expected_case.output_contract
                ):
                    raise ReleaseError(
                        "Reference evidence differs from the admitted source/metadata"
                    )
                expected_hash = row.get("source_sha256")
                if not isinstance(expected_hash, str) or HASH.fullmatch(expected_hash) is None:
                    raise ReleaseError("Reference source hash is invalid")
                content = source_file(root, row.get("source_path")).read_bytes()
                if sha256(content) != "sha256:" + expected_hash:
                    raise ReleaseError("Reference source changed after qualification")
                seen.add(row["lesson_id"])
                covered.add(row["profile"])
            if covered != required or seen != set(expected_cases):
                raise ReleaseError("Reference corpus omitted admitted cases or a selected runtime")
            record.update(kind="module-references", references=len(results))
            have_corpus = True
        else:
            if have_summary:
                raise ReleaseError("Supply exactly one CI lifecycle qualification summary")
            for field, expected in {
                "architecture": architecture,
                "revision": context.revision,
                "version": context.version,
                "run_id": context.run_id,
                "run_attempt": context.run_attempt,
            }.items():
                if report.get(field) != expected:
                    raise ReleaseError(
                        "CI qualification belongs to another version, platform or run attempt"
                    )
            checks = report.get("checks")
            if not isinstance(checks, list) or not checks or len(checks) > 100:
                raise ReleaseError("CI qualification needs named completed checks")
            names = []
            for check in checks:
                if (
                    not isinstance(check, dict)
                    or set(check) != {"name", "passed"}
                    or check["passed"] is not True
                    or not isinstance(check["name"], str)
                    or not 1 <= len(check["name"]) <= 200
                ):
                    raise ReleaseError("CI qualification contains an invalid or failed check")
                names.append(check["name"])
            if len(names) != len(set(names)):
                raise ReleaseError("CI qualification check names must be unique")
            group = image_group(selected, catalog(root), root)
            if report.get("group") != group:
                raise ReleaseError("CI summary group differs from the inspected images")
            if set(names) != mandatory_ci_checks(group):
                raise ReleaseError("CI summary is missing or changed mandatory group checks")
            record.update(kind="ci-summary", group=group, checks=names)
            have_summary = True
        records.append(record)
    if not have_corpus or not have_summary:
        raise ReleaseError(
            "Staging requires both the full reference corpus and CI lifecycle summary"
        )
    return records


def verify_candidate(
    registry: Registry, context: Context, image: dict[str, Any], architecture: str
) -> dict[str, Any]:
    tag = candidate_tag(context, image["profile"], architecture)
    head = registry.head(tag)
    if head is None:
        raise ReleaseError("Staged candidate manifest is missing")
    root = registry.get(head.digest)
    if not same_head(head, root.descriptor):
        raise ReleaseError("Candidate root changed during verification")
    local = image["local_descriptor"]
    if local is not None and descriptor(local) != root.descriptor:
        raise ReleaseError("Pushed root descriptor differs from the tested local descriptor")
    native = select_native(root, architecture)
    if not same_head(registry.head(native.digest), native):
        raise ReleaseError("Staged native descriptor is absent or inconsistent")
    identity = image["tested_image_id"]
    config = None
    if root.descriptor.media_type in IMAGE_TYPES:
        config = config_digest(root)
    elif identity != root.descriptor.digest or image["profile"] in SEEDS:
        child = registry.get(native.digest)
        if child.descriptor != native:
            raise ReleaseError("Native manifest changed its descriptor")
        config = config_digest(child)
    basis = "root" if identity == root.descriptor.digest else "config"
    if basis == "config" and identity != config:
        raise ReleaseError(
            "Pushed image is neither the tested root descriptor nor its tested config ID"
        )
    return {
        "profile": image["profile"],
        "local_repository": image["local_repository"],
        "tested_image_id": identity,
        "candidate_tag": tag,
        "candidate_root": root.descriptor.record(),
        "native": {**native.record(), "platform": {"os": "linux", "architecture": architecture}},
        "config_digest": config,
        "identity_basis": basis,
    }


def stage_images(
    context: Context,
    profiles: dict[str, Profile],
    tested: dict[str, Any],
    qualifications: list[dict[str, Any]],
    registry: Registry,
    docker: Docker,
    root: Path = ROOT,
) -> dict[str, Any]:
    architecture = tested["architecture"]
    docker.native(architecture)
    seed_bindings = {}
    if tested["group"] != "python-core":
        seed_bindings = verify_seed_local(
            context, profiles, tested["seed_receipt"], architecture, docker, root
        )
    # Complete local preflight precedes every tag or push.
    for image in tested["images"]:
        profile = profiles[image["profile"]]
        actual = inspected_image(
            docker.inspect(profile.local_repository + ":" + context.version),
            profile,
            context,
            architecture,
        )
        if actual != image:
            raise ReleaseError("A tested local image changed after qualification")
    staged = []
    for image in tested["images"]:
        tag = candidate_tag(context, image["profile"], architecture)
        print(f"Verifying qualified candidate: {image['profile']} ({architecture})", flush=True)
        if registry.head(tag) is None:
            target = context.repository + ":" + tag
            docker.tag(image["tested_image_id"], target)
            docker.push(target)
        staged.append(verify_candidate(registry, context, image, architecture))
        print(f"Candidate verified: {image['profile']} ({architecture})", flush=True)
    return {
        "schema_version": 1,
        "kind": "ds60-staged-images",
        "context": asdict(context),
        "architecture": architecture,
        "group": tested["group"],
        "seed_native_digests": seed_bindings,
        "qualification": qualifications,
        "images": staged,
    }


def staged_receipt(
    raw: dict[str, Any], context: Context, profiles: dict[str, Profile], *, root: Path = ROOT
) -> dict[str, Any]:
    if (
        set(raw)
        != {
            "schema_version",
            "kind",
            "context",
            "architecture",
            "group",
            "seed_native_digests",
            "qualification",
            "images",
        }
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or raw.get("kind") != "ds60-staged-images"
        or raw.get("architecture") not in ARCHITECTURES
    ):
        raise ReleaseError("Invalid staged-image receipt")
    recorded_context = bound_context(raw, context, earlier=True)
    architecture = raw["architecture"]
    images = raw["images"]
    if not isinstance(images, list) or not 1 <= len(images) <= len(profiles):
        raise ReleaseError("Invalid staged image count")
    selected: set[str] = set()
    for image in images:
        if not isinstance(image, dict) or set(image) != {
            "profile",
            "local_repository",
            "tested_image_id",
            "candidate_tag",
            "candidate_root",
            "native",
            "config_digest",
            "identity_basis",
        }:
            raise ReleaseError("Invalid staged native image fields")
        key = image["profile"]
        if (
            not isinstance(key, str)
            or key not in profiles
            or key in selected
            or image["local_repository"] != profiles[key].local_repository
        ):
            raise ReleaseError("Staged image profile is unknown or duplicated")
        selected.add(key)
        if image["candidate_tag"] != candidate_tag(recorded_context, key, architecture):
            raise ReleaseError("Candidate tag does not bind the source/run/attempt/platform")
        root_descriptor = descriptor(image["candidate_root"])
        native = native_descriptor(image["native"], architecture)
        identity = require_digest(image["tested_image_id"])
        config = image["config_digest"]
        if config is not None:
            require_digest(config)
        if (
            (image["identity_basis"] == "root" and identity != root_descriptor.digest)
            or (image["identity_basis"] == "config" and identity != config)
            or image["identity_basis"] not in {"root", "config"}
        ):
            raise ReleaseError("Staged identity proof is inconsistent")
        if root_descriptor.media_type in IMAGE_TYPES and root_descriptor != native:
            raise ReleaseError("A single-image root must be the selected native descriptor")
        if key in SEEDS and config is None:
            raise ReleaseError("Seed receipts require the native image config digest")
    if raw.get("group") != image_group(selected, profiles, root):
        raise ReleaseError("Staged receipt profile set differs from its qualification group")
    bindings = raw.get("seed_native_digests")
    if not isinstance(bindings, dict) or set(bindings) != (
        set() if selected == SEEDS else set(SEEDS)
    ):
        raise ReleaseError("Staged receipt is missing its exact seed binding")
    for value in bindings.values():
        require_digest(value)
    required = (selected - {"app"}) | ({"python-core"} if "app" in selected else set())
    records = raw["qualification"]
    if (
        not isinstance(records, list)
        or len(records) != 2
        or {row.get("kind") for row in records if isinstance(row, dict)}
        != {"module-references", "ci-summary"}
    ):
        raise ReleaseError("Staged receipt lacks both qualification proofs")
    for record in records:
        kind = record["kind"]
        expected = {
            "kind",
            "sha256",
            "profiles",
            "passed",
            "complete",
            "references" if kind == "module-references" else "checks",
        }
        if kind == "ci-summary":
            expected.add("group")
            if record.get("group") != raw["group"]:
                raise ReleaseError("Lifecycle proof belongs to another qualification group")
        if (
            set(record) != expected
            or record["passed"] is not True
            or record["complete"] is not True
            or record["profiles"] != sorted(required)
        ):
            raise ReleaseError("Staged qualification proof changed its fields or selection")
        require_digest(record["sha256"])
        if kind == "module-references" and (
            type(record["references"]) is not int or record["references"] < 1
        ):
            raise ReleaseError("Empty reference qualification")
        if kind == "ci-summary" and (
            not isinstance(record["checks"], list)
            or not record["checks"]
            or any(
                not isinstance(name, str) or not 1 <= len(name) <= 200 for name in record["checks"]
            )
        ):
            raise ReleaseError("Invalid lifecycle qualification proof")
        if kind == "ci-summary" and (
            len(record["checks"]) != len(set(record["checks"]))
            or set(record["checks"]) != mandatory_ci_checks(raw["group"])
        ):
            raise ReleaseError("Staged lifecycle proof omits mandatory group checks")
    return raw


def import_seed(
    context: Context,
    profiles: dict[str, Profile],
    receipt: dict[str, Any],
    architecture: str,
    registry: Registry,
    docker: Docker,
    root: Path = ROOT,
) -> None:
    staged_receipt(receipt, context, profiles, root=root)
    if (
        receipt["architecture"] != architecture
        or {row["profile"] for row in receipt["images"]} != SEEDS
    ):
        raise ReleaseError(
            "Seed import requires exactly app and Core from the selected native architecture"
        )
    docker.native(architecture)
    for image in receipt["images"]:
        expected = native_descriptor(image["native"], architecture)
        if not same_head(registry.head(expected.digest), expected):
            raise ReleaseError("Qualified seed native digest is missing or changed")
    for image in receipt["images"]:
        expected = native_descriptor(image["native"], architecture)
        raw = docker.pull(context.repository, expected.digest, architecture)
        profile = profiles[image["profile"]]
        inspected = inspected_image(raw, profile, context, architecture)
        if inspected["tested_image_id"] not in {expected.digest, image["config_digest"]}:
            raise ReleaseError(
                "Pulled seed identity differs from its qualified native manifest/config"
            )
        local = inspected["local_descriptor"]
        if local is not None and descriptor(local) != expected:
            raise ReleaseError("Pulled seed descriptor differs from its qualified native digest")
        docker.tag(inspected["tested_image_id"], profile.local_repository + ":" + context.version)


def receipt_files(directory: Path) -> list[Path]:
    if directory.is_symlink() or not directory.is_dir():
        raise ReleaseError("Choose the owned receipt artifact directory")
    files = []
    for current, directories, names in os.walk(directory, followlinks=False):
        if len(Path(current).relative_to(directory).parts) > 5:
            raise ReleaseError("Receipt directories exceed their depth bound")
        for name in [*directories, *names]:
            path = Path(current) / name
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise ReleaseError("Receipt artifacts must not contain links or special files")
        for name in names:
            path = Path(current) / name
            if path.suffix != ".json" or path.stat().st_size > MAX_RECEIPT:
                raise ReleaseError("Publication artifacts must contain only small JSON receipts")
            files.append(path)
            if len(files) > 100:
                raise ReleaseError("Too many release receipt artifacts")
    return sorted(files)


def promotion_inputs(
    directory: Path,
    context: Context,
    profiles: dict[str, Profile],
    registry: Registry,
    root: Path = ROOT,
) -> dict[str, dict[str, Descriptor]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for path in receipt_files(directory):
        raw = staged_receipt(read_json(path), context, profiles, root=root)
        identity = (raw["group"], raw["architecture"])
        attempt = int(raw["context"]["run_attempt"])
        prior = selected.get(identity)
        if prior is not None and int(prior["context"]["run_attempt"]) == attempt:
            raise ReleaseError(
                "Ambiguous duplicate receipt for one successful group/architecture attempt"
            )
        if prior is None or attempt > int(prior["context"]["run_attempt"]):
            selected[identity] = raw
    groups = release_groups(profiles, root)
    if set(selected) != {(group, arch) for group in groups for arch in ARCHITECTURES}:
        raise ReleaseError(
            "Promotion requires every native qualification group on both architectures"
        )
    seeds = {
        arch: {
            image["profile"]: image["native"]["digest"]
            for image in selected[("python-core", arch)]["images"]
        }
        for arch in ARCHITECTURES
    }
    result: dict[str, dict[str, Descriptor]] = {key: {} for key in profiles}
    for (group, arch), raw in selected.items():
        if group != "python-core" and raw["seed_native_digests"] != seeds[arch]:
            raise ReleaseError(
                "Worker receipts used different seeds; rerun those groups against "
                "the selected successful native seed"
            )
        for image in raw["images"]:
            key = image["profile"]
            if arch in result[key]:
                raise ReleaseError("Duplicate component/platform across qualification groups")
            expected = native_descriptor(image["native"], arch)
            if not same_head(
                registry.head(image["candidate_tag"]), descriptor(image["candidate_root"])
            ):
                raise ReleaseError("Candidate root no longer matches its qualified receipt")
            if not same_head(registry.head(expected.digest), expected):
                raise ReleaseError("Qualified native manifest is missing")
            result[key][arch] = expected
    if any(set(items) != set(ARCHITECTURES) for items in result.values()):
        raise ReleaseError("Promotion requires complete catalog coverage on amd64 and arm64")
    return result


def current_latest(registry: Registry, context: Context) -> Manifest | None:
    head = registry.head("latest")
    if head is None:
        return None
    value = registry.get(head.digest)
    if not same_head(head, value.descriptor):
        raise ReleaseError("Latest changed during inspection")
    version, revision, _ = published_index(value, "app", context.source_repository)
    if version == context.version and revision != context.revision:
        raise ReleaseError("Latest points to another revision of this release")
    return value


def latest_would_downgrade(
    registry: Registry,
    context: Context,
    profiles: dict[str, Profile],
    releases: dict[str, Manifest],
    latest: Manifest | None,
) -> bool:
    app_version = None
    if latest is not None:
        app_version, _, _ = published_index(latest, "app", context.source_repository)
        if version_tuple(app_version) > version_tuple(context.version):
            return True
    for key, profile in profiles.items():
        if key == "app":
            continue
        head = registry.head(latest_tag(profile))
        if head is None or head.digest == releases[key].descriptor.digest:
            continue
        # On a normal upgrade the worker aliases match the previous app version.
        # HEAD comparisons avoid downloading every old worker index again.
        old = registry.head(version_tag(profile, app_version)) if app_version is not None else None
        if old is not None and old.digest == head.digest:
            continue
        value = registry.get(head.digest)
        version, revision, _ = published_index(value, key, context.source_repository)
        if version_tuple(version) > version_tuple(context.version):
            return True
        if version == context.version and revision != context.revision:
            raise ReleaseError("A latest worker alias conflicts with this release revision")
    return False


def promote_release(
    context: Context,
    profiles: dict[str, Profile],
    registry: Registry,
    *,
    natives: dict[str, dict[str, Descriptor]] | None,
    output: Path,
) -> dict[str, Any]:
    releases: dict[str, Manifest] = {}
    # Validate the entire version set before any canonical write, including when
    # recovering a previous invocation that committed only part of the set.
    for key, profile in profiles.items():
        existing = load_published(registry, profile, context)
        if natives is None:
            if existing is None:
                raise ReleaseError("Existing-release recovery requires every immutable version tag")
            releases[key] = existing
            continue
        body = index_body(context, key, natives[key])
        expected = Manifest(Descriptor(OCI_INDEX, sha256(body), len(body)), json_object(body), body)
        if existing is not None:
            _, _, recorded = published_index(existing, key, context.source_repository)
            if recorded != natives[key]:
                raise ReleaseError("Immutable version descriptors differ; bump the patch version")
            releases[key] = existing  # Matching content/revision is never rewritten.
        else:
            releases[key] = expected
    latest = current_latest(registry, context)
    skip_latest = latest_would_downgrade(registry, context, profiles, releases, latest)
    latest_snapshot = latest.descriptor.digest if latest is not None else None
    report: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ds60-release-promotion",
        "context": asdict(context),
        "status": "promoting",
        "version_tags": [],
        "latest_tags": [],
        "latest_skipped_newer_release": skip_latest,
    }
    write_json(output, report)
    order = [key for key in profiles if key != "app"] + ["app"]
    for key in order:
        tag = version_tag(profiles[key], context.version)
        expected = releases[key]
        head = registry.head(tag)
        if head is None:
            registry.put(tag, expected.body, OCI_INDEX)
        elif not same_head(head, expected.descriptor):
            raise ReleaseError("Version tag changed before publication; no overwrite is permitted")
        if not same_head(registry.head(tag), expected.descriptor):
            raise ReleaseError("Immutable version tag failed readback")
        report["version_tags"].append({"tag": tag, **expected.descriptor.record()})
        write_json(output, report)
        print("Verified immutable version tag: " + tag, flush=True)
    # All immutable worker versions and app VERSION are verified before aliases.
    if not skip_latest:
        for key in order:
            now = registry.head("latest")
            if (now.digest if now is not None else None) != latest_snapshot:
                raise ReleaseError("Latest changed concurrently; no further aliases were moved")
            tag = latest_tag(profiles[key])
            expected = releases[key]
            current = registry.head(tag)
            if not same_head(current, expected.descriptor):
                # Fail closed if another publisher advanced this individual alias.
                if current is not None:
                    value = registry.get(current.digest)
                    version, revision, _ = published_index(value, key, context.source_repository)
                    if version_tuple(version) > version_tuple(context.version) or (
                        version == context.version and revision != context.revision
                    ):
                        raise ReleaseError(
                            "Refusing to downgrade or replace a conflicting latest alias"
                        )
                registry.put(tag, expected.body, OCI_INDEX)
            if not same_head(registry.head(tag), expected.descriptor):
                raise ReleaseError("Latest alias failed readback")
            report["latest_tags"].append({"tag": tag, **expected.descriptor.record()})
            write_json(output, report)
            print("Verified latest alias: " + tag, flush=True)
    report["status"] = "published"
    write_json(output, report)
    return report


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ReleaseError("Invalid release command arguments; use --help")


def registry_for(context: Context | None = None, *, push: bool = False) -> Registry:
    username, token = (
        os.environ.get("DOCKERHUB_USERNAME", ""),
        os.environ.get("DOCKERHUB_TOKEN", ""),
    )
    if context is not None and username != context.namespace:
        raise ReleaseError("Registry secret username differs from the gated namespace")
    return Registry(username, token, push=push)


def main(argv: list[str] | None = None) -> int:
    parser = Parser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    gate = sub.add_parser("gate")
    gate.add_argument("--output", required=True, type=Path)
    gate.add_argument("--github-output", type=Path)
    for name in ("inspect", "stage", "import-seed", "promote"):
        command = sub.add_parser(name)
        command.add_argument("--gate", required=True, type=Path)
        if name == "inspect":
            command.add_argument("--profiles", required=True)
            command.add_argument("--seed-receipt", type=Path)
            command.add_argument("--architecture", required=True, choices=ARCHITECTURES)
            command.add_argument("--output", required=True, type=Path)
        elif name == "stage":
            command.add_argument("--tested-images", required=True, type=Path)
            command.add_argument("--qualification", required=True, action="append", type=Path)
            command.add_argument("--output", required=True, type=Path)
        elif name == "import-seed":
            command.add_argument("--receipt", required=True, type=Path)
            command.add_argument("--architecture", required=True, choices=ARCHITECTURES)
        else:
            command.add_argument("--receipts-dir", required=True, type=Path)
            command.add_argument("--output", required=True, type=Path)
    try:
        args = parser.parse_args(argv)
        if args.command == "gate":
            context = github_context(ROOT, os.environ.get("DOCKERHUB_USERNAME", ""))
            registry = registry_for(context, push=True)
            registry.check_push_grant()
            value = gate_release(context, catalog(ROOT), registry)
            write_json(args.output, value)
            if args.github_output:
                with args.github_output.open("a", encoding="utf-8") as stream:
                    stream.write(f"mode={value['mode']}\nversion={context.version}\n")
            print("Release gate: " + value["mode"] + " for " + context.version)
            return 0
        context, profiles, mode = load_gate(args.gate)
        if args.command == "inspect":
            if mode != "build":
                raise ReleaseError("Image inspection is only part of a new qualified build")
            value = inspect_images(
                context,
                profiles,
                args.profiles.split(),
                args.architecture,
                Docker(),
                seed=read_json(args.seed_receipt) if args.seed_receipt else None,
            )
            write_json(args.output, value)
        elif args.command == "stage":
            if mode != "build":
                raise ReleaseError("Existing releases cannot stage replacement images")
            tested = load_tested(args.tested_images, context, profiles)
            records = qualification_records(
                args.qualification,
                context,
                tested["architecture"],
                {row["profile"] for row in tested["images"]},
                ROOT,
            )
            value = stage_images(
                context, profiles, tested, records, registry_for(context, push=True), Docker()
            )
            write_json(args.output, value)
        elif args.command == "import-seed":
            if mode != "build":
                raise ReleaseError("Seed import is only part of a new qualified build")
            import_seed(
                context,
                profiles,
                read_json(args.receipt),
                args.architecture,
                registry_for(context),
                Docker(),
            )
        else:
            if mode == "noop":
                raise ReleaseError("A no-op gate does not authorize another promotion")
            registry = registry_for(context, push=True)
            natives = (
                promotion_inputs(args.receipts_dir, context, profiles, registry)
                if mode == "build"
                else None
            )
            promote_release(context, profiles, registry, natives=natives, output=args.output)
        print("Release operation completed: " + args.command)
        return 0
    except ReleaseError as error:
        print("Release rejected: " + str(error), file=sys.stderr)
        return 2
    except (OSError, KeyError, TypeError, ValueError, RecursionError):
        print("Release rejected: invalid or unavailable release metadata", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
