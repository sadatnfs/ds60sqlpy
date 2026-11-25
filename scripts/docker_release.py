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
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import image_scan  # noqa: E402
from scripts.docker_registry import (  # noqa: E402
    IMAGE_TYPES,
    INDEX_TYPES,
    NAMESPACE,
    OCI_INDEX,
    WRITE_VISIBILITY_WAITS,
    Descriptor,
    Head,
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
# DS60 PostgreSQL is not a learner profile in the image catalog, but it ships
# with every release seed so Hub learners pull it instead of building it.
DATABASE = image_scan.DATABASE_PROFILE
SEEDS = frozenset({"app", "python-core", DATABASE})
# First stable release whose seed publishes the database image. Older Hub
# releases have no database tag, and their launcher builds the image locally.
DATABASE_SINCE = (2, 0, 0)
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
SCOPE = "io.ds60.release.scope"
GROUP = "io.ds60.release.group"
# Qualified scientific project images publish beside the catalog in the same
# repository. The scientific CI job stages two native images per platform; the
# TMB public API and C++ API projects are qualified inside the Spark TMB image.
SCIENTIFIC_STAGED = frozenset(image_scan.SCIENTIFIC_PROFILES)
SCIENTIFIC_RELEASES = {
    "project-spark-torch": "project-spark-torch",
    "project-spark-tmb": "project-spark-tmb",
    "project-tmb-public-api": "project-spark-tmb",
    "project-tmb-cpp-api": "project-spark-tmb",
}


@dataclass(frozen=True)
class Profile:
    profile: str
    local_repository: str
    suffix: str


def scientific_profiles() -> dict[str, Profile]:
    """Published scientific profiles: `VERSION-project-<id>` and `latest-project-<id>`."""
    return {
        key: Profile(key, "ds60-" + key.removeprefix("project-"), key)
        for key in SCIENTIFIC_RELEASES
    }


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
            or DATABASE in {profile, suffix}
        ):
            raise ReleaseError("Image catalog is ambiguous or malformed")
        seen_ids.add(profile)
        seen_suffixes.add(suffix)
        if kind != "gpu":
            result[profile] = Profile(profile, local, suffix)
    result[DATABASE] = Profile(DATABASE, "ds60sqlpy-postgres", DATABASE)
    if not result.keys() >= SEEDS:
        raise ReleaseError("Image catalog needs the app, Core and PostgreSQL seed")
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


def github_context(root: Path, namespace: str, *, target_group: str | None = None) -> Context:
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
        or not isinstance(event.get("repository"), dict)
        or event["repository"].get("full_name") != context.source_repository
    ):
        raise ReleaseError("The main push HEAD commit does not match the release context")
    from scripts.ci_targeted_images import parse_marker

    try:
        event_intent = parse_marker(head["message"], root)
        checkout_intent = parse_marker(git_output(root, ["log", "-1", "--format=%B"]), root)
    except ValueError as error:
        raise ReleaseError("Invalid Docker publication marker: " + str(error)) from None
    if (
        git_output(root, ["rev-parse", "HEAD"]) != context.revision
        or event_intent != checkout_intent
    ):
        raise ReleaseError("Checkout HEAD differs from the marked push commit")
    if target_group is None:
        if event_intent is None or event_intent.mode != "full":
            raise ReleaseError("The main push HEAD commit must contain only [publish-docker]")
    elif (
        event_intent is None or event_intent.mode != "publish" or event_intent.group != target_group
    ):
        raise ReleaseError("The main push HEAD commit must select this targeted publish group")
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


def index_body(
    context: Context,
    profile: str,
    natives: dict[str, Descriptor],
    *,
    target_group: str | None = None,
) -> bytes:
    if set(natives) != set(ARCHITECTURES):
        raise ReleaseError("Promotion requires both native architectures")
    annotations = {
        SCHEMA: "1",
        PROFILE: profile,
        REVISION: context.revision,
        RELEASE_VERSION: context.version,
        SOURCE: "https://github.com/" + context.source_repository,
    }
    if target_group is not None:
        annotations.update({SCOPE: "partial", GROUP: target_group})
    body = {
        "schemaVersion": 2,
        "mediaType": OCI_INDEX,
        "manifests": [
            {**natives[arch].record(), "platform": {"os": "linux", "architecture": arch}}
            for arch in ARCHITECTURES
        ],
        "annotations": annotations,
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


def require_scope(manifest: Manifest, target_group: str | None) -> None:
    annotations = manifest.document.get("annotations", {})
    if target_group is None:
        if SCOPE in annotations or GROUP in annotations:
            raise ReleaseError("A partial version tag cannot complete a full release")
    elif annotations.get(SCOPE) != "partial" or annotations.get(GROUP) != target_group:
        raise ReleaseError("Existing version tag belongs to another publication scope")


def database_published(version: str) -> bool:
    match = re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version)
    return match is not None and tuple(int(part) for part in match.groups()) >= DATABASE_SINCE


def selected_release_profiles(
    profiles: dict[str, Profile], target_group: str | None, root: Path
) -> set[str]:
    if target_group is None:
        return set(profiles)
    declared_groups = release_groups(profiles, root)
    if target_group not in declared_groups:
        raise ReleaseError("Unknown targeted release group")
    return set(SEEDS | declared_groups[target_group])


def gate_release(
    context: Context,
    profiles: dict[str, Profile],
    registry: Registry,
    *,
    target_group: str | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    selected = selected_release_profiles(profiles, target_group, root)
    published: dict[str, Manifest] = {}
    for key, profile in profiles.items():
        value = load_published(registry, profile, context)
        if value is not None and key in selected:
            require_scope(value, target_group)
            published[key] = value
    if published and set(published) != selected:
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
                    same_head(registry.head(latest_tag(profiles[key])), published[key].descriptor)
                    for key in selected
                )
            )
        ):
            mode = "noop"
    result = {
        "schema_version": 1,
        "kind": "ds60-release-gate",
        "context": asdict(context),
        "mode": mode,
        "profiles": [asdict(p) for p in profiles.values()],
    }
    if target_group is not None:
        result["selection"] = {"group": target_group, "profiles": sorted(selected)}
    return result


def load_gate(path: Path, root: Path = ROOT) -> tuple[Context, dict[str, Profile], str]:
    raw = read_json(path)
    base_fields = {"schema_version", "kind", "context", "mode", "profiles"}
    if (
        set(raw) not in (base_fields, base_fields | {"selection"})
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or raw.get("kind") != "ds60-release-gate"
        or raw.get("mode") not in {"build", "promote-existing", "noop"}
    ):
        raise ReleaseError("Invalid release gate receipt")
    context = context_record(raw["context"])
    profiles = catalog(root)
    if raw["profiles"] != [asdict(p) for p in profiles.values()]:
        raise ReleaseError("Image catalog changed after the publication gate")
    target_group = None
    if "selection" in raw:
        selection = raw["selection"]
        declared_groups = release_groups(profiles, root)
        if (
            not isinstance(selection, dict)
            or set(selection) != {"group", "profiles"}
            or not isinstance(selection["group"], str)
            or selection["group"] not in declared_groups
            or selection["profiles"] != sorted(SEEDS | declared_groups[selection["group"]])
        ):
            raise ReleaseError("Invalid targeted release group in gate receipt")
        target_group = selection["group"]
    current = github_context(root, context.namespace, target_group=target_group)
    bound_context({"context": asdict(context)}, current, earlier=True)
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
    if not isinstance(labels, dict) or labels.get(REVISION) != context.revision:
        raise ReleaseError("Local image revision label must match the release revision")
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
            not isinstance(key, str)
            or key not in profiles
            or key in {"app", DATABASE}
            or key in seen
            for key in members
        ) or len(members) != len(set(members)):
            raise ReleaseError("Release qualification groups overlap or include unknown images")
        seen.update(members)
        result[row["id"]] = frozenset(members)
    if seen != set(profiles) - {"app", DATABASE} or result.get("python-core") != frozenset(
        {"python-core"}
    ):
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


SCAN_KEYS = frozenset(
    {
        "evidence_sha256",
        "scanner_image",
        "scanner_version",
        "db_updated_at",
        "java_db_updated_at",
        "policy_sha256",
        "scanned_at",
        "images",
    }
)
SCAN_IMAGE_KEYS = frozenset({"profile", "tested_image_id", "counts", "suppressed", "report_sha256"})
SUPPRESSED_KEYS = frozenset({"id", "package", "expires_at"})
TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z")
MAX_SCAN_EVIDENCE = 64 * 1024 * 1024
MAX_SUPPRESSED = 500


def utc_now() -> datetime:
    return datetime.now(UTC)


def scan_time(value: Any) -> datetime:
    if not isinstance(value, str) or TIMESTAMP.fullmatch(value) is None:
        raise ReleaseError("Scan evidence timestamps must be UTC ISO 8601 seconds")
    try:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        raise ReleaseError("Scan evidence has an invalid timestamp") from None


def committed_policy(root: Path, today: date) -> image_scan.Policy:
    """The committed DS60 CVE policy; malformed or expired entries reject the release."""
    try:
        return image_scan.load_policy(
            root / "docker/cve-policy.json", today, image_scan.policy_profiles(root)
        )
    except image_scan.ScanError as error:
        raise ReleaseError("Committed CVE policy is invalid or expired: " + str(error)) from None


def fresh_scan_database(updated: Any, now: datetime) -> None:
    moment = scan_time(updated)
    if moment > now or now - moment > image_scan.MAX_DB_AGE:
        raise ReleaseError("Scan evidence vulnerability DB is not from the last 24 hours")


def scan_binding(
    evidence: Any,
    evidence_sha256: str,
    tested: dict[str, Any],
    root: Path = ROOT,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Bind clean, fresh, policy-current scan evidence to every tested image ID (D-02)."""
    now = now or utc_now()
    if (
        not isinstance(evidence, dict)
        or type(evidence.get("schema")) is not int
        or evidence["schema"] != 1
        or evidence.get("kind") != "ds60-scan-evidence"
    ):
        raise ReleaseError("Invalid image scan evidence")
    if evidence.get("context") != tested["context"]:
        raise ReleaseError("Scan evidence belongs to another source, run or attempt")
    if evidence.get("architecture") != tested["architecture"]:
        raise ReleaseError("Scan evidence covers another architecture")
    scanner = evidence.get("scanner")
    if (
        not isinstance(scanner, dict)
        or scanner.get("image") != image_scan.TRIVY_IMAGE
        or scanner.get("version") != image_scan.TRIVY_VERSION
    ):
        raise ReleaseError("Scan evidence was not produced by the pinned scanner")
    fresh_scan_database(scanner.get("db_updated_at"), now)
    scan_time(scanner.get("java_db_updated_at"))
    scan_time(evidence.get("scanned_at"))
    policy = committed_policy(root, now.date())
    if evidence.get("policy_sha256") != policy.sha256:
        raise ReleaseError("Scan evidence used a different CVE policy than the committed one")
    if evidence.get("passed") is not True:
        raise ReleaseError("Scan evidence has blocking findings; nothing may be staged")
    rows = evidence.get("images")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ReleaseError("Invalid scan evidence image list")
    images = []
    for image in tested["images"]:
        matches = [row for row in rows if row.get("profile") == image["profile"]]
        if len(matches) != 1:
            raise ReleaseError("Scan evidence must cover each tested profile exactly once")
        row = matches[0]
        if row.get("tested_image_id") != image["tested_image_id"] or row.get("reference"):
            raise ReleaseError("Scan evidence covers a different image than was qualified")
        if row.get("revision_label") != tested["context"]["revision"]:
            raise ReleaseError("Scanned image revision label differs from the release revision")
        if row.get("blocking") != []:
            raise ReleaseError("Scan evidence has blocking findings; nothing may be staged")
        suppressed = row.get("suppressed")
        if not isinstance(suppressed, list) or any(
            not isinstance(found, dict) for found in suppressed
        ):
            raise ReleaseError("Invalid suppressed scan findings")
        kept = {
            (found.get("id"), found.get("package"), found.get("expires_at")) for found in suppressed
        }
        images.append(
            scan_image_record(
                {
                    "profile": image["profile"],
                    "tested_image_id": image["tested_image_id"],
                    "counts": row.get("counts"),
                    "report_sha256": row.get("report_sha256"),
                    "suppressed": [
                        {"id": key, "package": package, "expires_at": expires}
                        for key, package, expires in sorted(kept, key=str)
                    ],
                }
            )
        )
    return {
        "evidence_sha256": evidence_sha256,
        "scanner_image": scanner["image"],
        "scanner_version": scanner["version"],
        "db_updated_at": scanner["db_updated_at"],
        "java_db_updated_at": scanner["java_db_updated_at"],
        "policy_sha256": policy.sha256,
        "scanned_at": evidence["scanned_at"],
        "images": images,
    }


def load_scan(
    path: Path, tested: dict[str, Any], root: Path = ROOT, now: datetime | None = None
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SCAN_EVIDENCE:
        raise ReleaseError("Scan evidence must be a bounded ordinary file")
    data = path.read_bytes()
    return scan_binding(
        json_object(data, MAX_SCAN_EVIDENCE),
        sha256(data).removeprefix("sha256:"),
        tested,
        root,
        now,
    )


def scan_image_record(image: Any) -> dict[str, Any]:
    if not isinstance(image, dict) or set(image) != SCAN_IMAGE_KEYS:
        raise ReleaseError("Invalid scan image fields")
    require_digest(image["tested_image_id"])
    counts = image["counts"]
    if (
        not isinstance(counts, dict)
        or set(counts) != set(image_scan.SEVERITIES)
        or any(type(value) is not int or value < 0 for value in counts.values())
    ):
        raise ReleaseError("Invalid scan severity counts")
    if (
        not isinstance(image["report_sha256"], str)
        or HASH.fullmatch(image["report_sha256"]) is None
    ):
        raise ReleaseError("Invalid scan report hash")
    suppressed = image["suppressed"]
    if not isinstance(suppressed, list) or len(suppressed) > MAX_SUPPRESSED:
        raise ReleaseError("Invalid suppressed scan findings")
    for found in suppressed:
        if (
            not isinstance(found, dict)
            or set(found) != SUPPRESSED_KEYS
            or not isinstance(found["id"], str)
            or not isinstance(found["package"], str)
            or not 1 <= len(found["id"]) <= 200
            or not 1 <= len(found["package"]) <= 500
            or image_scan.policy_date(found["expires_at"]) is None
        ):
            raise ReleaseError("Invalid suppressed scan finding")
    return image


def scan_block(value: Any, images: list[dict[str, Any]]) -> dict[str, Any]:
    """Structural check of a receipt's scan block; freshness is enforced at stage and promote."""
    if not isinstance(value, dict) or set(value) != SCAN_KEYS:
        raise ReleaseError("Staged receipt lacks its exact scan evidence block")
    for name in ("evidence_sha256", "policy_sha256"):
        if not isinstance(value[name], str) or HASH.fullmatch(value[name]) is None:
            raise ReleaseError("Invalid scan evidence hash")
    if (
        value["scanner_image"] != image_scan.TRIVY_IMAGE
        or value["scanner_version"] != image_scan.TRIVY_VERSION
    ):
        raise ReleaseError("Staged receipt scan used another scanner")
    for name in ("db_updated_at", "java_db_updated_at", "scanned_at"):
        scan_time(value[name])
    rows = value["images"]
    if not isinstance(rows, list):
        raise ReleaseError("Invalid scan image list")
    scanned = {}
    for row in rows:
        scan_image_record(row)
        if row["profile"] in scanned:
            raise ReleaseError("Duplicate scan image record")
        scanned[row["profile"]] = row["tested_image_id"]
    if scanned != {image["profile"]: image["tested_image_id"] for image in images}:
        raise ReleaseError("Scan evidence does not cover exactly the staged image IDs")
    return value


def promotion_scan_check(scan: dict[str, Any], root: Path, now: datetime) -> None:
    """Re-verify staged scan evidence at promote time (D-02, D-05)."""
    fresh_scan_database(scan["db_updated_at"], now)
    if scan["policy_sha256"] != committed_policy(root, now.date()).sha256:
        raise ReleaseError("Staged scan used a CVE policy that differs from the committed one")
    today = now.date()
    for image in scan["images"]:
        for found in image["suppressed"]:
            expires = image_scan.policy_date(found["expires_at"])
            if expires is None or expires < today:
                raise ReleaseError("A suppression the staged scan relied on has expired")


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


def qualified_profiles(selected: set[str]) -> set[str]:
    """Return the module-qualified profiles; the app and PostgreSQL ride on Core."""
    seed = {"python-core"} if "app" in selected else set()
    return (selected - {"app", DATABASE}) | seed


def qualification_records(
    paths: list[Path], context: Context, architecture: str, selected: set[str], root: Path
) -> list[dict[str, Any]]:
    required = qualified_profiles(selected)
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


def head_after_write(
    registry: Registry, reference: str, expected: Descriptor | None = None
) -> Head | None:
    """Read back a manifest this run just wrote, waiting out a brief stale read.

    Docker Hub can answer 404 for a newly pushed or written tag for a short
    time, and can still serve a moved tag's previous manifest. Absence is
    retried for about a minute in total; with an expected descriptor, so is a
    different manifest. A mismatch that outlasts the waits still fails its check.
    """

    def settled(head: Head | None) -> bool:
        return head is not None and (expected is None or same_head(head, expected))

    head = registry.head(reference)
    for delay in WRITE_VISIBILITY_WAITS:
        if settled(head):
            break
        time.sleep(delay)
        head = registry.head(reference)
    return head


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


def stage_candidate(
    registry: Registry,
    docker: Docker,
    context: Context,
    image: dict[str, Any],
    architecture: str,
) -> dict[str, Any]:
    """Push one already scanned and qualified local image ID to its candidate tag."""
    tag = candidate_tag(context, image["profile"], architecture)
    if registry.head(tag) is None:
        target = context.repository + ":" + tag
        docker.tag(image["tested_image_id"], target)
        docker.push(target)
        head_after_write(registry, tag)
    return verify_candidate(registry, context, image, architecture)


def stage_images(
    context: Context,
    profiles: dict[str, Profile],
    tested: dict[str, Any],
    qualifications: list[dict[str, Any]],
    registry: Registry,
    docker: Docker,
    root: Path = ROOT,
    *,
    scan: dict[str, Any],
) -> dict[str, Any]:
    architecture = tested["architecture"]
    scan_block(scan, tested["images"])
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
        print(f"Verifying qualified candidate: {image['profile']} ({architecture})", flush=True)
        staged.append(stage_candidate(registry, docker, context, image, architecture))
        print(f"Candidate verified: {image['profile']} ({architecture})", flush=True)
    return {
        "schema_version": 2,
        "kind": "ds60-staged-images",
        "context": asdict(context),
        "architecture": architecture,
        "group": tested["group"],
        "seed_native_digests": seed_bindings,
        "qualification": qualifications,
        "scan": scan,
        "images": staged,
    }


STAGED_IMAGE_KEYS = frozenset(
    {
        "profile",
        "local_repository",
        "tested_image_id",
        "candidate_tag",
        "candidate_root",
        "native",
        "config_digest",
        "identity_basis",
    }
)


def staged_image_proof(image: dict[str, Any], context: Context, architecture: str) -> str | None:
    """Check one staged candidate's tag and identity proof; returns its config digest."""
    if image["candidate_tag"] != candidate_tag(context, image["profile"], architecture):
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
    return config if isinstance(config, str) else None


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
            "scan",
            "images",
        }
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 2
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
        if not isinstance(image, dict) or set(image) != STAGED_IMAGE_KEYS:
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
        config = staged_image_proof(image, recorded_context, architecture)
        if key in SEEDS and config is None:
            raise ReleaseError("Seed receipts require the native image config digest")
    if raw.get("group") != image_group(selected, profiles, root):
        raise ReleaseError("Staged receipt profile set differs from its qualification group")
    scan_block(raw["scan"], images)
    bindings = raw.get("seed_native_digests")
    if not isinstance(bindings, dict) or set(bindings) != (
        set() if selected == SEEDS else set(SEEDS)
    ):
        raise ReleaseError("Staged receipt is missing its exact seed binding")
    for value in bindings.values():
        require_digest(value)
    required = qualified_profiles(selected)
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
            "Seed import requires exactly the app, Core and PostgreSQL seed of this architecture"
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


def promotion_scan_record(
    image: dict[str, Any], native: Descriptor, row: dict[str, Any], scan: dict[str, Any]
) -> dict[str, Any]:
    """The compact per-platform scan record a release report keeps for one native image."""
    return {
        "tested_image_id": image["tested_image_id"],
        "native_digest": native.digest,
        "counts": row["counts"],
        "suppressed": sorted({found["id"] for found in row["suppressed"]}),
        "report_sha256": row["report_sha256"],
        "evidence_sha256": scan["evidence_sha256"],
        "scanner_image": scan["scanner_image"],
        "db_updated_at": scan["db_updated_at"],
        "policy_sha256": scan["policy_sha256"],
        "scanned_at": scan["scanned_at"],
    }


def promotion_inputs(
    directory: Path,
    context: Context,
    profiles: dict[str, Profile],
    registry: Registry,
    root: Path = ROOT,
    *,
    target_group: str | None = None,
    now: datetime | None = None,
    scans: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Descriptor]]:
    """Select qualified natives; `scans` receives the per-profile/architecture scan record."""
    now = now or utc_now()
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for path in receipt_files(directory):
        raw = staged_receipt(read_json(path), context, profiles, root=root)
        promotion_scan_check(raw["scan"], root, now)
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
    required_groups = set(groups) if target_group is None else {"python-core", target_group}
    if target_group is not None and target_group not in groups:
        raise ReleaseError("Unknown targeted promotion group")
    if set(selected) != {(group, arch) for group in required_groups for arch in ARCHITECTURES}:
        raise ReleaseError(
            "Promotion requires every native qualification group on both architectures"
            if target_group is None
            else "Promotion requires each selected native qualification group on both architectures"
        )
    seeds = {
        arch: {
            image["profile"]: image["native"]["digest"]
            for image in selected[("python-core", arch)]["images"]
        }
        for arch in ARCHITECTURES
    }
    selected_profiles = set(profiles) if target_group is None else set(SEEDS | groups[target_group])
    result: dict[str, dict[str, Descriptor]] = {key: {} for key in selected_profiles}
    records: dict[str, dict[str, Any]] = {key: {} for key in selected_profiles}
    for (group, arch), raw in selected.items():
        scanned = {row["profile"]: row for row in raw["scan"]["images"]}
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
            records[key][arch] = promotion_scan_record(image, expected, scanned[key], raw["scan"])
    if any(set(items) != set(ARCHITECTURES) for items in result.values()):
        raise ReleaseError(
            "Promotion requires complete catalog coverage on amd64 and arm64"
            if target_group is None
            else "Promotion requires complete selected coverage on amd64 and arm64"
        )
    if scans is not None:
        scans.clear()
        scans.update(records)
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


def scientific_plan(
    context: Context,
    registry: Registry,
    natives: dict[str, dict[str, Descriptor]],
    scan: dict[str, dict[str, Any]] | None,
) -> tuple[dict[str, Profile], dict[str, Manifest], dict[str, Any]]:
    """Validate every scientific version tag before any write and choose each index.

    An index already published for this version and revision wins, because a
    workflow rerun rebuilds the scientific images and cannot reproduce their
    digests. Every project derived from one staged image shares one native set.
    """
    if set(natives) != SCIENTIFIC_STAGED or any(
        set(natives[key]) != set(ARCHITECTURES) for key in natives
    ):
        raise ReleaseError("Scientific natives must cover each staged project on both platforms")
    if scan is not None and (
        set(scan) != SCIENTIFIC_STAGED
        or any(
            set(scan[key]) != set(ARCHITECTURES)
            or any(
                scan[key][arch]["native_digest"] != natives[key][arch].digest for arch in scan[key]
            )
            for key in scan
        )
    ):
        raise ReleaseError("Scientific scan records do not cover exactly the staged native digests")
    profiles = scientific_profiles()
    published = {
        key: load_published(registry, profile, context) for key, profile in profiles.items()
    }
    effective: dict[str, dict[str, Descriptor]] = {}
    for key, existing in published.items():
        if existing is None:
            continue
        require_scope(existing, None)
        _, _, recorded = published_index(existing, key, context.source_repository)
        source = SCIENTIFIC_RELEASES[key]
        if effective.setdefault(source, recorded) != recorded:
            raise ReleaseError("Published scientific projects disagree on their shared image")
    releases: dict[str, Manifest] = {}
    images: dict[str, Any] = {}
    for key in profiles:
        source = SCIENTIFIC_RELEASES[key]
        chosen = effective.get(source, natives[source])
        existing = published[key]
        if existing is not None:
            releases[key] = existing
        else:
            body = index_body(context, key, chosen)
            releases[key] = Manifest(
                Descriptor(OCI_INDEX, sha256(body), len(body)), json_object(body), body
            )
        images[key] = {
            "source": source,
            "reused": chosen != natives[source],
            "natives": {arch: chosen[arch].digest for arch in ARCHITECTURES},
        }
    record: dict[str, Any] = {"version_tags": [], "latest_tags": [], "images": images}
    if scan is not None:
        record["scan"] = scan
    return profiles, releases, record


def promote_release(
    context: Context,
    profiles: dict[str, Profile],
    registry: Registry,
    *,
    natives: dict[str, dict[str, Descriptor]] | None,
    output: Path,
    target_group: str | None = None,
    root: Path = ROOT,
    scan: dict[str, dict[str, Any]] | None = None,
    scientific: dict[str, dict[str, Descriptor]] | None = None,
    scientific_scan: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    selected = selected_release_profiles(profiles, target_group, root)
    if scientific is None and scientific_scan is not None:
        raise ReleaseError("Scientific scan records require scientific native images")
    if scientific is not None and target_group is not None:
        raise ReleaseError("Scientific project images publish only with a full release")
    if natives is not None and set(natives) != selected:
        raise ReleaseError("Qualified native selection differs from the promotion scope")
    if scan is not None and (
        natives is None
        or set(scan) != selected
        or any(
            set(scan[key]) != set(ARCHITECTURES)
            or any(
                scan[key][arch]["native_digest"] != natives[key][arch].digest for arch in scan[key]
            )
            for key in selected
        )
    ):
        raise ReleaseError("Scan records do not cover exactly the promoted native digests")
    scoped_profiles = {key: profile for key, profile in profiles.items() if key in selected}
    releases: dict[str, Manifest] = {}
    # Validate the entire version set before any canonical write, including when
    # recovering a previous invocation that committed only part of the set.
    published = {
        key: load_published(registry, profile, context) for key, profile in profiles.items()
    }
    # Even an unselected occupied version tag must have the same source revision.
    for key in profiles:
        if key not in selected:
            continue
        existing = published[key]
        if existing is not None:
            require_scope(existing, target_group)
        if natives is None:
            if existing is None:
                raise ReleaseError("Existing-release recovery requires every immutable version tag")
            releases[key] = existing
            continue
        body = index_body(context, key, natives[key], target_group=target_group)
        expected = Manifest(Descriptor(OCI_INDEX, sha256(body), len(body)), json_object(body), body)
        if existing is not None:
            _, _, recorded = published_index(existing, key, context.source_repository)
            if recorded != natives[key]:
                raise ReleaseError("Immutable version descriptors differ; bump the patch version")
            releases[key] = existing  # Matching content/revision is never rewritten.
        else:
            releases[key] = expected
    science_profiles: dict[str, Profile] = {}
    science_record: dict[str, Any] | None = None
    if scientific is not None:
        if set(profiles) & set(SCIENTIFIC_RELEASES):
            raise ReleaseError("Scientific project tags collide with catalog profiles")
        science_profiles, science_releases, science_record = scientific_plan(
            context, registry, scientific, scientific_scan
        )
        releases.update(science_releases)
    every_profile = {**profiles, **science_profiles}
    latest = current_latest(registry, context)
    skip_latest = latest_would_downgrade(
        registry, context, {**scoped_profiles, **science_profiles}, releases, latest
    )
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
    if target_group is not None:
        report["scope"] = "partial"
        report["group"] = target_group
        report["profiles"] = sorted(selected)
    if scan is not None:
        report["scan"] = scan
    if science_record is not None:
        report["scientific"] = science_record
    # Scientific tags follow every ordinary worker and precede the app pointer,
    # so a published app version or alias implies the complete scientific set.
    order = [key for key in scoped_profiles if key != "app"] + [*science_profiles, "app"]
    final = json.loads(json.dumps(report))
    final["status"] = "published"
    for key in order:
        rows = final["scientific"] if key in science_profiles else final
        rows["version_tags"].append(
            {
                "tag": version_tag(every_profile[key], context.version),
                **releases[key].descriptor.record(),
            }
        )
        if not skip_latest:
            rows["latest_tags"].append(
                {"tag": latest_tag(every_profile[key]), **releases[key].descriptor.record()}
            )
    if len(json.dumps(final, sort_keys=True, indent=2, allow_nan=False)) + 1 > MAX_RECEIPT:
        raise ReleaseError("Release metadata would exceed its 256 KiB bound; no tag was written")
    write_json(output, report)

    def record(key: str, kind: str, tag: str, value: Descriptor) -> None:
        rows = report["scientific"][kind] if key in science_profiles else report[kind]
        rows.append({"tag": tag, **value.record()})
        write_json(output, report)

    for key in order:
        tag = version_tag(every_profile[key], context.version)
        expected = releases[key]
        head = registry.head(tag)
        if head is None:
            registry.put(tag, expected.body, OCI_INDEX)
        elif not same_head(head, expected.descriptor):
            raise ReleaseError("Version tag changed before publication; no overwrite is permitted")
        if not same_head(head_after_write(registry, tag), expected.descriptor):
            raise ReleaseError("Immutable version tag failed readback")
        record(key, "version_tags", tag, expected.descriptor)
        print("Verified immutable version tag: " + tag, flush=True)
    # All immutable worker versions and app VERSION are verified before aliases.
    if not skip_latest:
        for key in order:
            now = registry.head("latest")
            if (now.digest if now is not None else None) != latest_snapshot:
                raise ReleaseError("Latest changed concurrently; no further aliases were moved")
            tag = latest_tag(every_profile[key])
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
            if not same_head(
                head_after_write(registry, tag, expected.descriptor), expected.descriptor
            ):
                raise ReleaseError("Latest alias failed readback")
            record(key, "latest_tags", tag, expected.descriptor)
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
    gate.add_argument("--target-group")
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
            command.add_argument("--scan", required=True, type=Path)
            command.add_argument("--output", required=True, type=Path)
        elif name == "import-seed":
            command.add_argument("--receipt", required=True, type=Path)
            command.add_argument("--architecture", required=True, choices=ARCHITECTURES)
        else:
            command.add_argument("--receipts-dir", required=True, type=Path)
            command.add_argument("--project-receipts-dir", type=Path)
            command.add_argument("--output", required=True, type=Path)
    try:
        args = parser.parse_args(argv)
        if args.command == "gate":
            context = github_context(
                ROOT, os.environ.get("DOCKERHUB_USERNAME", ""), target_group=args.target_group
            )
            registry = registry_for(context, push=True)
            registry.check_push_grant()
            value = gate_release(context, catalog(ROOT), registry, target_group=args.target_group)
            write_json(args.output, value)
            if args.github_output:
                with args.github_output.open("a", encoding="utf-8") as stream:
                    stream.write(f"mode={value['mode']}\nversion={context.version}\n")
            print("Release gate: " + value["mode"] + " for " + context.version)
            return 0
        context, profiles, mode = load_gate(args.gate)
        selection = read_json(args.gate).get("selection")
        target_group = selection["group"] if selection is not None else None
        if args.command == "inspect":
            if mode != "build":
                raise ReleaseError("Image inspection is only part of a new qualified build")
            if target_group is not None and image_group(
                set(args.profiles.split()), profiles
            ) not in {"python-core", target_group}:
                raise ReleaseError("Inspected profiles differ from the targeted gate")
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
            if target_group is not None and tested["group"] not in {
                "python-core",
                target_group,
            }:
                raise ReleaseError("Staged profiles differ from the targeted gate")
            # The scan gate runs before qualification files, local preflight, tags or pushes.
            scan = load_scan(args.scan, tested)
            records = qualification_records(
                args.qualification,
                context,
                tested["architecture"],
                {row["profile"] for row in tested["images"]},
                ROOT,
            )
            value = stage_images(
                context,
                profiles,
                tested,
                records,
                registry_for(context, push=True),
                Docker(),
                scan=scan,
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
            scans: dict[str, dict[str, Any]] = {}
            natives = (
                promotion_inputs(
                    args.receipts_dir,
                    context,
                    profiles,
                    registry,
                    target_group=target_group,
                    scans=scans,
                )
                if mode == "build" or target_group is None
                else None
            )
            scientific = None
            scientific_scan = None
            if target_group is None:
                # Full recovery must retain the same scientific evidence as a new
                # full promotion. Published tags alone never bypass this gate.
                from scripts.scientific_receipts import (
                    published_natives,
                    validate_scientific_receipts,
                )

                assert natives is not None
                chosen = validate_scientific_receipts(
                    args.project_receipts_dir, context, profiles, natives, ROOT, registry=registry
                )
                scientific, scientific_scan = published_natives(chosen)
            promote_release(
                context,
                profiles,
                registry,
                natives=natives,
                output=args.output,
                target_group=target_group,
                scan=scans if natives is not None else None,
                scientific=scientific,
                scientific_scan=scientific_scan,
            )
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
