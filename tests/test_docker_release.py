"""Source, image identity and ordered release promotion without registry writes."""

from __future__ import annotations

import copy
import hashlib
import json
import platform
from dataclasses import asdict, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from scripts import docker_release as release
from scripts import image_scan
from scripts.docker_registry import (
    OCI_INDEX,
    OCI_MANIFEST,
    WRITE_VISIBILITY_WAITS,
    Descriptor,
    Head,
    Manifest,
    Registry,
    ReleaseError,
    json_object,
    sha256,
)


@pytest.fixture(autouse=True)
def reject_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.request

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("Release tests must not make real registry/authentication calls")

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", forbidden)


class FakeRegistry(Registry):
    def __init__(self) -> None:
        self.objects: dict[str, Manifest] = {}
        self.tags: dict[str, str] = {}
        self.puts: list[str] = []
        self.gets: list[str] = []
        self.heads: list[str] = []
        self.fail_tag: str | None = None

    def add(self, body: bytes, tag: str | None = None) -> Manifest:
        value = json_object(body)
        manifest = Manifest(Descriptor(value["mediaType"], sha256(body), len(body)), value, body)
        self.objects[manifest.descriptor.digest] = manifest
        if tag is not None:
            self.tags[tag] = manifest.descriptor.digest
        return manifest

    def head(self, reference: str) -> Head | None:
        self.heads.append(reference)
        digest = self.tags.get(reference, reference)
        value = self.objects.get(digest)
        return (
            None
            if value is None
            else Head(value.descriptor.media_type, digest, value.descriptor.size)
        )

    def get(self, reference: str) -> Manifest:
        self.gets.append(reference)
        digest = self.tags.get(reference, reference)
        if digest not in self.objects:
            raise ReleaseError("Missing fake manifest")
        return self.objects[digest]

    def put(self, tag: str, body: bytes, media_type: str = OCI_INDEX) -> Descriptor:
        assert media_type == OCI_INDEX
        self.puts.append(tag)
        if self.fail_tag == tag:
            raise ReleaseError("Injected publication interruption")
        return self.add(body, tag).descriptor


class LaggingRegistry(FakeRegistry):
    """Answers 404 for a newly written tag's first reads, as Docker Hub briefly can."""

    def __init__(self, misses: int) -> None:
        super().__init__()
        self.misses = misses
        self.settled: set[str] = set()
        self.pending: dict[str, int] = {}

    def settle(self) -> None:
        self.settled.update(self.tags)

    def head(self, reference: str) -> Head | None:
        if reference in self.tags and reference not in self.settled:
            left = self.pending.setdefault(reference, self.misses)
            if left:
                self.pending[reference] = left - 1
                self.heads.append(reference)
                return None
        return super().head(reference)


class StaleAliasRegistry(FakeRegistry):
    """Serves a moved tag's previous manifest once after the move, as Docker Hub can."""

    def __init__(self) -> None:
        super().__init__()
        self.previous: dict[str, str] = {}

    def put(self, tag: str, body: bytes, media_type: str = OCI_INDEX) -> Descriptor:
        if tag in self.tags:
            self.previous[tag] = self.tags[tag]
        return super().put(tag, body, media_type)

    def head(self, reference: str) -> Head | None:
        stale = self.previous.pop(reference, None)
        if stale is None:
            return super().head(reference)
        self.heads.append(reference)
        value = self.objects[stale]
        return Head(value.descriptor.media_type, stale, value.descriptor.size)


def encoded(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def native(registry: FakeRegistry, name: str) -> tuple[Manifest, str]:
    config = sha256(("config:" + name).encode())
    manifest = registry.add(
        encoded(
            {
                "schemaVersion": 2,
                "mediaType": OCI_MANIFEST,
                "config": {
                    "mediaType": "application/vnd.oci.image.config.v1+json",
                    "digest": config,
                    "size": 128,
                },
                "layers": [],
            }
        )
    )
    return manifest, config


def root_index(
    registry: FakeRegistry, image: Manifest, arch: str, *, attestation: bool = False
) -> Manifest:
    entries = [{**image.descriptor.record(), "platform": {"os": "linux", "architecture": arch}}]
    if attestation:
        attest, _ = native(registry, "attestation:" + image.descriptor.digest)
        entries.append(
            {
                **attest.descriptor.record(),
                "platform": {"os": "unknown", "architecture": "unknown"},
                "annotations": {
                    "vnd.docker.reference.type": "attestation-manifest",
                    "vnd.docker.reference.digest": image.descriptor.digest,
                },
            }
        )
    return registry.add(encoded({"schemaVersion": 2, "mediaType": OCI_INDEX, "manifests": entries}))


POLICY = b'{"schema": 1, "entries": []}\n'
POLICY_SHA = hashlib.sha256(POLICY).hexdigest()
COUNTS = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}


def stamp(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def scan_block(
    images: list[dict[str, Any]], *, db_age: timedelta = timedelta(hours=1)
) -> dict[str, Any]:
    """Receipt scan block for synthetic tested images; never presented as real evidence."""
    now = datetime.now(UTC)
    return {
        "evidence_sha256": "e" * 64,
        "scanner_image": image_scan.TRIVY_IMAGE,
        "scanner_version": image_scan.TRIVY_VERSION,
        "db_updated_at": stamp(now - db_age),
        "java_db_updated_at": stamp(now - timedelta(days=2)),
        "policy_sha256": POLICY_SHA,
        "scanned_at": stamp(now - timedelta(minutes=30)),
        "images": [
            {
                "profile": image["profile"],
                "tested_image_id": image["tested_image_id"],
                "counts": dict(COUNTS),
                "suppressed": [],
                "report_sha256": "f" * 64,
            }
            for image in images
        ],
    }


@pytest.fixture
def context() -> release.Context:
    return release.Context(
        "exampleuser", "exampleuser/ds60sqlpy", "example/classroom", "1.0.0", "a" * 40, "12345", "1"
    )


@pytest.fixture
def profiles(tmp_path: Path) -> dict[str, release.Profile]:
    (tmp_path / "docker").mkdir()
    (tmp_path / "docker/cve-policy.json").write_bytes(POLICY)
    (tmp_path / "docker/classroom-images.tsv").write_text(
        "app lab ds60sqlpy-lab lab DS60_LAB_IMAGE app\n"
        "python-core core ds60sqlpy-worker-python-core worker-python-core "
        "DS60_CORE_IMAGE ordinary\n"
        "java21 java ds60sqlpy-worker-java21 worker-java21 DS60_JAVA_IMAGE ordinary\n"
    )
    (tmp_path / "docker/ci-profile-groups.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "groups": [
                    {"id": "python-core", "profiles": ["python-core"]},
                    {"id": "java", "profiles": ["java21"]},
                ],
            }
        )
    )
    return release.catalog(tmp_path)


def proofs(selected: set[str], group: str) -> list[dict[str, Any]]:
    required = (selected - {"app", release.DATABASE}) | (
        {"python-core"} if "app" in selected else set()
    )
    common = {
        "sha256": sha256(b"report"),
        "profiles": sorted(required),
        "passed": True,
        "complete": True,
    }
    return [
        {**common, "kind": "module-references", "references": 2},
        {
            **common,
            "kind": "ci-summary",
            "group": group,
            "checks": sorted(release.mandatory_ci_checks(group)),
        },
    ]


def receipt(
    registry: FakeRegistry,
    context: release.Context,
    profiles: dict[str, release.Profile],
    arch: str,
    group: str,
    *,
    seed_digests: dict[str, str] | None = None,
    content: str = "first",
) -> dict[str, Any]:
    selected = release.SEEDS if group == "python-core" else {"java21"}
    images = []
    for key in sorted(selected):
        image, config = native(registry, f"{content}:{key}:{arch}")
        root = root_index(registry, image, arch, attestation=True)
        candidate = release.candidate_tag(context, key, arch)
        registry.tags[candidate] = root.descriptor.digest
        images.append(
            {
                "profile": key,
                "local_repository": profiles[key].local_repository,
                "tested_image_id": root.descriptor.digest,
                "candidate_tag": candidate,
                "candidate_root": root.descriptor.record(),
                "native": {
                    **image.descriptor.record(),
                    "platform": {"os": "linux", "architecture": arch},
                },
                "config_digest": config if key in release.SEEDS else None,
                "identity_basis": "root",
            }
        )
    return {
        "schema_version": 2,
        "kind": "ds60-staged-images",
        "context": asdict(context),
        "architecture": arch,
        "group": group,
        "seed_native_digests": seed_digests or {},
        "qualification": proofs(set(selected), group),
        "scan": scan_block(images),
        "images": images,
    }


def complete_receipts(
    directory: Path,
    registry: FakeRegistry,
    context: release.Context,
    profiles: dict[str, release.Profile],
) -> dict[str, dict[str, Descriptor]]:
    directory.mkdir()
    expected: dict[str, dict[str, Descriptor]] = {key: {} for key in profiles}
    for arch in release.ARCHITECTURES:
        seed = receipt(registry, context, profiles, arch, "python-core")
        bindings = {image["profile"]: image["native"]["digest"] for image in seed["images"]}
        worker = receipt(registry, context, profiles, arch, "java", seed_digests=bindings)
        for value in (seed, worker):
            folder = directory / f"{value['group']}-{arch}"
            folder.mkdir()
            (folder / "release-receipt.json").write_text(json.dumps(value))
            for image in value["images"]:
                expected[image["profile"]][arch] = release.native_descriptor(image["native"], arch)
    return expected


def test_oci_index_selects_native_and_recognized_attestation_only() -> None:
    registry = FakeRegistry()
    image, _ = native(registry, "native")
    root = root_index(registry, image, "arm64", attestation=True)
    assert release.select_native(root, "arm64") == image.descriptor
    for mutate in (
        "another-native",
        "duplicate-native",
        "unrecognized-attestation",
        "wrong-subject",
    ):
        changed = copy.deepcopy(root.document)
        entries = changed["manifests"]
        if mutate == "another-native":
            entries[1]["platform"] = {"os": "linux", "architecture": "amd64"}
        elif mutate == "duplicate-native":
            entries.append(copy.deepcopy(entries[0]))
        elif mutate == "unrecognized-attestation":
            entries[1]["annotations"].clear()
        else:
            entries[1]["annotations"]["vnd.docker.reference.digest"] = "sha256:" + "0" * 64
        with pytest.raises(ReleaseError):
            release.select_native(registry.add(encoded(changed)), "arm64")


def test_docker29_worker_index_id_is_verified_without_refetching_children(
    context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    image, _ = native(registry, "java")
    root = root_index(registry, image, "amd64", attestation=True)
    registry.tags[release.candidate_tag(context, "java21", "amd64")] = root.descriptor.digest
    local = {
        "profile": "java21",
        "local_repository": profiles["java21"].local_repository,
        "tested_image_id": root.descriptor.digest,
        "local_descriptor": root.descriptor.record(),
    }
    result = release.verify_candidate(registry, context, local, "amd64")
    assert result["identity_basis"] == "root" and result["config_digest"] is None
    assert result["native"]["digest"] == image.descriptor.digest
    assert registry.gets == [root.descriptor.digest]


def test_old_config_id_fallback_and_changed_root_are_not_confused(
    context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    image, config = native(registry, "legacy")
    root = root_index(registry, image, "amd64")
    registry.tags[release.candidate_tag(context, "java21", "amd64")] = root.descriptor.digest
    local = {
        "profile": "java21",
        "local_repository": profiles["java21"].local_repository,
        "tested_image_id": config,
        "local_descriptor": None,
    }
    result = release.verify_candidate(registry, context, local, "amd64")
    assert result["identity_basis"] == "config" and result["config_digest"] == config
    with pytest.raises(ReleaseError, match="root descriptor"):
        release.verify_candidate(
            registry,
            context,
            {
                **local,
                "local_descriptor": {**root.descriptor.record(), "digest": "sha256:" + "0" * 64},
            },
            "amd64",
        )
    with pytest.raises(ReleaseError, match="neither"):
        release.verify_candidate(
            registry, context, {**local, "tested_image_id": "sha256:" + "0" * 64}, "amd64"
        )


def test_complete_promotion_orders_workers_before_each_app_pointer(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    expected = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    inputs = release.promotion_inputs(tmp_path / "receipts", context, profiles, registry, tmp_path)
    assert inputs == expected
    report = release.promote_release(
        context, profiles, registry, natives=inputs, output=tmp_path / "promotion.json"
    )
    assert registry.puts == [
        "1.0.0-worker-python-core",
        "1.0.0-worker-java21",
        "1.0.0-postgres",
        "1.0.0",
        "latest-worker-python-core",
        "latest-worker-java21",
        "latest-postgres",
        "latest",
    ]
    assert report["status"] == "published"
    assert len(report["version_tags"]) == len(report["latest_tags"]) == 4
    assert registry.gets == []  # Descriptor HEAD verification and direct index PUT only.
    release.promote_release(
        context, profiles, registry, natives=inputs, output=tmp_path / "repeat.json"
    )
    assert len(registry.puts) == 8  # Exact repeat never rewrites immutable or matching aliases.
    assert release.gate_release(context, profiles, registry)["mode"] == "noop"


def test_promotion_readback_waits_out_a_brief_registry_lag(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr("time.sleep", sleeps.append)
    registry = LaggingRegistry(misses=1)
    complete_receipts(tmp_path / "receipts", registry, context, profiles)
    registry.settle()
    inputs = release.promotion_inputs(tmp_path / "receipts", context, profiles, registry, tmp_path)
    report = release.promote_release(
        context, profiles, registry, natives=inputs, output=tmp_path / "promotion.json"
    )
    assert report["status"] == "published"
    assert sleeps == [2] * 8  # One brief absence per written tag, each read back.


def add_unselected_group(root: Path) -> dict[str, release.Profile]:
    image_catalog = root / "docker/classroom-images.tsv"
    image_catalog.write_text(
        image_catalog.read_text()
        + "cpp20 cpp ds60sqlpy-worker-cpp20 worker-cpp20 DS60_CPP_IMAGE ordinary\n"
    )
    group_catalog = root / "docker/ci-profile-groups.json"
    groups = json.loads(group_catalog.read_text())
    groups["groups"].append({"id": "cpp", "profiles": ["cpp20"]})
    group_catalog.write_text(json.dumps(groups))
    return release.catalog(root)


def test_targeted_publication_binds_exact_group_and_only_moves_selected_aliases(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    profiles = add_unselected_group(tmp_path)
    registry = FakeRegistry()
    gate = release.gate_release(context, profiles, registry, target_group="java", root=tmp_path)
    assert gate["mode"] == "build"
    assert gate["selection"] == {
        "group": "java",
        "profiles": ["app", "java21", "postgres", "python-core"],
    }
    complete_receipts(tmp_path / "receipts", registry, context, profiles)
    inputs = release.promotion_inputs(
        tmp_path / "receipts", context, profiles, registry, tmp_path, target_group="java"
    )
    assert set(inputs) == {"app", "python-core", "java21", release.DATABASE}
    report = release.promote_release(
        context,
        profiles,
        registry,
        natives=inputs,
        output=tmp_path / "partial.json",
        target_group="java",
        root=tmp_path,
    )
    assert report["scope"] == "partial" and report["group"] == "java"
    assert report["profiles"] == ["app", "java21", "postgres", "python-core"]
    assert registry.puts == [
        "1.0.0-worker-python-core",
        "1.0.0-worker-java21",
        "1.0.0-postgres",
        "1.0.0",
        "latest-worker-python-core",
        "latest-worker-java21",
        "latest-postgres",
        "latest",
    ]
    assert not any("cpp20" in tag for tag in registry.tags)
    for key in ("app", "python-core", "java21", release.DATABASE):
        manifest = registry.get(release.version_tag(profiles[key], context.version))
        assert manifest.document["annotations"][release.SCOPE] == "partial"
        assert manifest.document["annotations"][release.GROUP] == "java"
    assert (
        release.gate_release(context, profiles, registry, target_group="java", root=tmp_path)[
            "mode"
        ]
        == "noop"
    )
    with pytest.raises(ReleaseError, match="partial version tag"):
        release.gate_release(context, profiles, registry, root=tmp_path)
    newer = replace(context, version="1.0.1", revision="b" * 40)
    assert release.gate_release(newer, profiles, registry, root=tmp_path)["mode"] == "build"
    full = complete_receipts(tmp_path / "new-receipts", registry, newer, profiles)
    for architecture in release.ARCHITECTURES:
        cpp, _ = native(registry, "new-cpp-" + architecture)
        full["cpp20"][architecture] = cpp.descriptor
    complete = release.promote_release(
        newer,
        profiles,
        registry,
        natives=full,
        output=tmp_path / "complete.json",
    )
    assert complete["status"] == "published"
    assert registry.puts[-1] == "latest"
    assert "latest-worker-cpp20" in registry.puts


def test_targeted_publication_rejects_other_source_version_before_any_write(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    profiles = add_unselected_group(tmp_path)
    registry = FakeRegistry()
    complete_receipts(tmp_path / "receipts", registry, context, profiles)
    inputs = release.promotion_inputs(
        tmp_path / "receipts", context, profiles, registry, tmp_path, target_group="java"
    )
    other = replace(context, revision="b" * 40)
    amd64, _ = native(registry, "occupied-cpp-amd64")
    arm64, _ = native(registry, "occupied-cpp-arm64")
    registry.add(
        release.index_body(other, "cpp20", {"amd64": amd64.descriptor, "arm64": arm64.descriptor}),
        release.version_tag(profiles["cpp20"], context.version),
    )
    with pytest.raises(ReleaseError, match="occupied by another revision"):
        release.promote_release(
            context,
            profiles,
            registry,
            natives=inputs,
            output=tmp_path / "denied.json",
            target_group="java",
            root=tmp_path,
        )
    assert registry.puts == []


def test_targeted_promotion_requires_only_selected_but_both_native_receipts(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    profiles = add_unselected_group(tmp_path)
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    complete_receipts(folder, registry, context, profiles)
    (folder / "java-arm64/release-receipt.json").unlink()
    with pytest.raises(ReleaseError, match="selected native qualification group"):
        release.promotion_inputs(folder, context, profiles, registry, tmp_path, target_group="java")


def test_core_only_targeted_publication_needs_no_worker_receipts(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    folder.mkdir()
    for architecture in release.ARCHITECTURES:
        seed = receipt(registry, context, profiles, architecture, "python-core")
        child = folder / f"seed-{architecture}"
        child.mkdir()
        (child / "release-receipt.json").write_text(json.dumps(seed))
    inputs = release.promotion_inputs(
        folder, context, profiles, registry, tmp_path, target_group="python-core"
    )
    assert set(inputs) == release.SEEDS
    release.promote_release(
        context,
        profiles,
        registry,
        natives=inputs,
        output=tmp_path / "core-only.json",
        target_group="python-core",
        root=tmp_path,
    )
    assert registry.puts == [
        "1.0.0-worker-python-core",
        "1.0.0-postgres",
        "1.0.0",
        "latest-worker-python-core",
        "latest-postgres",
        "latest",
    ]


def test_partial_version_failure_keeps_app_and_latest_unpublished_then_resumes_exact_digests(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    registry.fail_tag = "1.0.0-worker-java21"
    with pytest.raises(ReleaseError, match="interruption"):
        release.promote_release(
            context, profiles, registry, natives=natives, output=tmp_path / "partial.json"
        )
    assert "1.0.0" not in registry.tags and not any(
        tag.startswith("latest") for tag in registry.tags
    )
    with pytest.raises(ReleaseError, match="original failed promotion"):
        release.gate_release(context, profiles, registry)
    registry.fail_tag = None
    before = len(registry.puts)
    release.promote_release(
        replace(context, run_attempt="2"),
        profiles,
        registry,
        natives=natives,
        output=tmp_path / "recovered.json",
    )
    assert "1.0.0-worker-python-core" not in registry.puts[before:]
    assert registry.puts[-1] == "latest"


def test_conflicting_version_descriptors_fail_before_any_canonical_write(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    other, _ = native(registry, "different-worker")
    changed = {**natives["java21"], "amd64": other.descriptor}
    registry.add(release.index_body(context, "java21", changed), "1.0.0-worker-java21")
    with pytest.raises(ReleaseError, match="Immutable version descriptors"):
        release.promote_release(
            context, profiles, registry, natives=natives, output=tmp_path / "denied.json"
        )
    assert registry.puts == []


def test_an_older_rerun_never_moves_latest_backward(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    newer = replace(context, version="1.1.0", revision="b" * 40)
    for key, profile in profiles.items():
        registry.add(release.index_body(newer, key, natives[key]), release.latest_tag(profile))
    old_latest = dict(registry.tags)
    report = release.promote_release(
        context, profiles, registry, natives=natives, output=tmp_path / "old.json"
    )
    assert report["latest_skipped_newer_release"] is True and report["latest_tags"] == []
    assert all(registry.tags[tag] == digest for tag, digest in old_latest.items())
    assert release.gate_release(context, profiles, registry)["mode"] == "noop"


def test_promotion_waits_out_a_moved_alias_previous_manifest(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr("time.sleep", sleeps.append)
    registry = StaleAliasRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    older = replace(context, version="0.9.0", revision="b" * 40)
    for key, profile in profiles.items():
        registry.add(release.index_body(older, key, natives[key]), release.latest_tag(profile))
    report = release.promote_release(
        context, profiles, registry, natives=natives, output=tmp_path / "moved.json"
    )
    assert report["status"] == "published" and len(report["latest_tags"]) == len(profiles)
    assert sleeps == [2] * len(profiles)  # One previous-manifest read per moved alias.


def test_same_revision_complete_versions_can_finish_missing_aliases(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    for key, profile in profiles.items():
        registry.add(
            release.index_body(context, key, natives[key]),
            release.version_tag(profile, context.version),
        )
    assert release.gate_release(context, profiles, registry)["mode"] == "promote-existing"
    release.promote_release(
        context, profiles, registry, natives=None, output=tmp_path / "aliases.json"
    )
    assert registry.puts == [
        "latest-worker-python-core",
        "latest-worker-java21",
        "latest-postgres",
        "latest",
    ]


def test_latest_unique_same_run_worker_receipts_reuse_exact_selected_seeds(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    expected = complete_receipts(folder, registry, context, profiles)
    current = replace(context, run_attempt="3")
    old = json.loads((folder / "java-amd64/release-receipt.json").read_text())
    newer = receipt(
        registry,
        replace(context, run_attempt="2"),
        profiles,
        "amd64",
        "java",
        seed_digests=old["seed_native_digests"],
        content="retry",
    )
    (folder / "java-retry.json").write_text(json.dumps(newer))
    actual = release.promotion_inputs(folder, current, profiles, registry, tmp_path)
    assert actual["python-core"] == expected["python-core"]
    assert actual["java21"]["amd64"].digest == newer["images"][0]["native"]["digest"]
    assert actual["java21"]["arm64"] == expected["java21"]["arm64"]


def test_old_workers_cannot_be_combined_with_rebuilt_seed_digests(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    complete_receipts(folder, registry, context, profiles)
    newer = receipt(
        registry,
        replace(context, run_attempt="2"),
        profiles,
        "amd64",
        "python-core",
        content="rebuilt",
    )
    (folder / "seed-new.json").write_text(json.dumps(newer))
    with pytest.raises(ReleaseError, match="different seeds"):
        release.promotion_inputs(
            folder, replace(context, run_attempt="2"), profiles, registry, tmp_path
        )
    assert registry.puts == []


@pytest.mark.parametrize(
    "change", [{"run_id": "99999"}, {"revision": "b" * 40}, {"run_attempt": "4"}]
)
def test_receipts_cannot_cross_runs_revisions_or_future_attempts(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    change: dict[str, str],
) -> None:
    registry = FakeRegistry()
    value = receipt(registry, context, profiles, "amd64", "python-core")
    value["context"].update(change)
    with pytest.raises(ReleaseError):
        release.staged_receipt(value, replace(context, run_attempt="3"), profiles, root=tmp_path)


def test_duplicate_attempt_artifacts_are_ambiguous_even_if_bytes_match(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    complete_receipts(folder, registry, context, profiles)
    original = folder / "java-amd64/release-receipt.json"
    (folder / "duplicate.json").write_bytes(original.read_bytes())
    with pytest.raises(ReleaseError, match="Ambiguous duplicate"):
        release.promotion_inputs(folder, context, profiles, registry, tmp_path)


def test_receipt_artifacts_never_accept_image_archives_or_links(tmp_path: Path) -> None:
    folder = tmp_path / "receipts"
    folder.mkdir()
    (folder / "image.tar").write_bytes(b"not a receipt")
    with pytest.raises(ReleaseError, match="small JSON"):
        release.receipt_files(folder)
    (folder / "image.tar").unlink()
    (folder / "linked.json").symlink_to(tmp_path / "private.json")
    with pytest.raises(ReleaseError, match="links"):
        release.receipt_files(folder)


class FakeDocker(release.Docker):
    def __init__(self, registry: FakeRegistry) -> None:
        self.registry = registry
        self.images: dict[str, dict[str, Any]] = {}
        self.by_id: dict[str, Manifest] = {}
        self.tagged: dict[str, str] = {}
        self.operations: list[tuple[str, ...]] = []
        self.pulled: dict[str, dict[str, Any]] = {}

    def native(self, architecture: str) -> None:
        assert architecture in release.ARCHITECTURES
        self.operations.append(("native", architecture))

    def inspect(self, reference: str) -> dict[str, Any]:
        self.operations.append(("inspect", reference))
        return copy.deepcopy(self.images[reference])

    def tag(self, identity: str, target: str) -> None:
        self.operations.append(("tag", identity, target))
        self.tagged[target] = identity

    def push(self, target: str) -> None:
        self.operations.append(("push", target))
        image = self.by_id[self.tagged[target]]
        self.registry.tags[target.split(":", 1)[1]] = image.descriptor.digest

    def pull(self, repository: str, digest: str, architecture: str) -> dict[str, Any]:
        self.operations.append(("pull", repository, digest, architecture))
        return copy.deepcopy(self.pulled[digest])


def local_images(
    registry: FakeRegistry,
    context: release.Context,
    profiles: dict[str, release.Profile],
    arch: str,
) -> FakeDocker:
    docker = FakeDocker(registry)
    for key, profile in profiles.items():
        image, _ = native(registry, key + arch)
        root = root_index(registry, image, arch)
        docker.images[profile.local_repository + ":" + context.version] = {
            "Id": root.descriptor.digest,
            "Os": "linux",
            "Architecture": arch,
            "Descriptor": root.descriptor.record(),
            "Config": {
                "Labels": {
                    release.RELEASE_VERSION: context.version,
                    release.REVISION: context.revision,
                }
            },
        }
        docker.by_id[root.descriptor.digest] = root
    return docker


def test_stage_rejects_changed_tested_images_before_any_candidate_tag_or_push(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    docker = local_images(registry, context, profiles, "amd64")
    snapshot = release.inspect_images(
        context, profiles, sorted(release.SEEDS), "amd64", docker, root=tmp_path
    )
    docker.images[profiles["python-core"].local_repository + ":" + context.version]["Id"] = (
        "sha256:" + "0" * 64
    )
    with pytest.raises(ReleaseError, match="changed after qualification"):
        release.stage_images(
            context,
            profiles,
            snapshot,
            proofs(set(release.SEEDS), "python-core"),
            registry,
            docker,
            tmp_path,
            scan=scan_block(snapshot["images"]),
        )
    assert not [op for op in docker.operations if op[0] in {"tag", "push"}]


def test_successful_seed_stage_binds_pushed_root_native_config_and_qualification(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    docker = local_images(registry, context, profiles, "arm64")
    snapshot = release.inspect_images(
        context, profiles, sorted(release.SEEDS), "arm64", docker, root=tmp_path
    )
    result = release.stage_images(
        context,
        profiles,
        snapshot,
        proofs(set(release.SEEDS), "python-core"),
        registry,
        docker,
        tmp_path,
        scan=scan_block(snapshot["images"]),
    )
    assert release.staged_receipt(result, context, profiles, root=tmp_path) == result
    assert all(
        image["identity_basis"] == "root" and image["config_digest"] for image in result["images"]
    )
    assert [op[1] for op in docker.operations if op[0] == "tag"] == [
        image["tested_image_id"] for image in snapshot["images"]
    ]
    assert not any(tag in registry.tags for tag in ("1.0.0", "latest"))


@pytest.mark.parametrize(("misses", "waits"), [(2, [2, 4] * 3), (99, list(WRITE_VISIBILITY_WAITS))])
def test_stage_waits_briefly_for_a_just_pushed_candidate_then_fails_closed(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
    misses: int,
    waits: list[int],
) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr("time.sleep", sleeps.append)
    registry = LaggingRegistry(misses=misses)
    docker = local_images(registry, context, profiles, "amd64")
    snapshot = release.inspect_images(
        context, profiles, sorted(release.SEEDS), "amd64", docker, root=tmp_path
    )
    proof = proofs(set(release.SEEDS), "python-core")
    if misses > len(WRITE_VISIBILITY_WAITS):
        with pytest.raises(ReleaseError, match="Staged candidate manifest is missing"):
            release.stage_images(
                context,
                profiles,
                snapshot,
                proof,
                registry,
                docker,
                tmp_path,
                scan=scan_block(snapshot["images"]),
            )
    else:
        staged = release.stage_images(
            context,
            profiles,
            snapshot,
            proof,
            registry,
            docker,
            tmp_path,
            scan=scan_block(snapshot["images"]),
        )
        assert len(staged["images"]) == len(release.SEEDS)
    assert sleeps == waits


def test_seed_import_reuses_earlier_attempt_by_native_digest_and_pins_restored_tags(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    seed = receipt(registry, context, profiles, "arm64", "python-core")
    docker = FakeDocker(registry)
    for image in seed["images"]:
        native_image = release.native_descriptor(image["native"], "arm64")
        docker.pulled[native_image.digest] = {
            "Id": image["config_digest"],
            "Os": "linux",
            "Architecture": "arm64",
            "Config": {
                "Labels": {
                    release.RELEASE_VERSION: context.version,
                    release.REVISION: context.revision,
                }
            },
        }
    release.import_seed(
        replace(context, run_attempt="2"), profiles, seed, "arm64", registry, docker, tmp_path
    )
    pulls = [op for op in docker.operations if op[0] == "pull"]
    assert {op[2] for op in pulls} == {image["native"]["digest"] for image in seed["images"]}
    tags = [op for op in docker.operations if op[0] == "tag"]
    assert {op[1] for op in tags} == {image["config_digest"] for image in seed["images"]}
    assert all(op[2].startswith("ds60sqlpy-") for op in tags)
    assert not registry.gets and not registry.puts


def test_worker_inspection_requires_the_selected_native_seed_receipt(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    docker = local_images(registry, context, profiles, "amd64")
    with pytest.raises(ReleaseError, match="seed-receipt"):
        release.inspect_images(context, profiles, ["java21"], "amd64", docker, root=tmp_path)


@pytest.mark.parametrize("label", ["", "f" * 40, None, "dirty"])
@pytest.mark.parametrize("profile", ["app", "python-core", "java21"])
def test_inspected_image_refuses_a_revision_label_other_than_the_release_revision(
    context: release.Context, profiles: dict[str, release.Profile], profile: str, label: Any
) -> None:
    labels: dict[str, Any] = {release.RELEASE_VERSION: context.version}
    if label == "dirty":
        labels[release.REVISION] = context.revision + "-dirty"
    elif label is not None:
        labels[release.REVISION] = label
    raw = {
        "Id": "sha256:" + "c" * 64,
        "Os": "linux",
        "Architecture": "amd64",
        "Config": {"Labels": labels},
    }
    with pytest.raises(ReleaseError, match="revision label must match the release revision"):
        release.inspected_image(raw, profiles[profile], context, "amd64")
    labels[release.REVISION] = context.revision
    assert release.inspected_image(raw, profiles[profile], context, "amd64")["profile"] == profile


def qualification_files(
    tmp_path: Path, context: release.Context, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    from scripts.check_module_references import ReferenceCase

    folder = tmp_path / "courses/example"
    folder.mkdir(parents=True)
    cases = {}
    rows = []
    for number in (1, 2):
        source = f"class Main {{ int value = {number}; }}\n"
        relative = f"courses/example/case-{number}.java"
        (tmp_path / relative).write_text(source)
        case = ReferenceCase(
            f"example-{number:03}", "example", "java21", "java", "practice", None, relative, source
        )
        cases[case.lesson_id] = case
        rows.append(
            {
                **case.metadata(),
                "status": "passed",
                "worker_status": "succeeded",
                "returncode": 0,
                "truncated": False,
                "job_id": str(number) * 32,
            }
        )
    monkeypatch.setattr(release, "expected_references", lambda root, required: cases)
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "passed": True,
                "complete": True,
                "profiles": ["java21"],
                "selected_cases": 2,
                "results": rows,
            }
        )
    )
    summary = tmp_path / "ci.json"
    summary.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "passed": True,
                "complete": True,
                "profiles": ["java21"],
                "group": "java",
                "architecture": "amd64",
                "version": context.version,
                "revision": context.revision,
                "run_id": context.run_id,
                "run_attempt": context.run_attempt,
                "checks": [
                    {"name": name, "passed": True}
                    for name in sorted(release.mandatory_ci_checks("java"))
                ],
            }
        )
    )
    return corpus, summary


def test_shortened_self_consistent_corpus_cannot_claim_complete_qualification(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus, summary = qualification_files(tmp_path, context, monkeypatch)
    assert (
        len(
            release.qualification_records([corpus, summary], context, "amd64", {"java21"}, tmp_path)
        )
        == 2
    )
    value = json.loads(corpus.read_text())
    value["results"].pop()
    value["selected_cases"] = 1
    corpus.write_text(json.dumps(value))
    with pytest.raises(ReleaseError, match="omitted admitted"):
        release.qualification_records([corpus, summary], context, "amd64", {"java21"}, tmp_path)


@pytest.mark.parametrize("change", ["source", "mandatory-check", "context", "failed", "duplicate"])
def test_qualification_rejects_changed_source_incomplete_checks_and_wrong_context(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
    change: str,
) -> None:
    corpus, summary = qualification_files(tmp_path, context, monkeypatch)
    if change == "source":
        (tmp_path / "courses/example/case-1.java").write_text("changed source")
    else:
        path = corpus if change in {"failed", "duplicate"} else summary
        value = json.loads(path.read_text())
        if change == "mandatory-check":
            value["checks"].pop()
        elif change == "context":
            value["run_id"] = "98765"
        elif change == "failed":
            value["results"][0]["worker_status"] = "failed"
        else:
            value["results"][1] = value["results"][0]
        path.write_text(json.dumps(value))
    with pytest.raises(ReleaseError):
        release.qualification_records([corpus, summary], context, "amd64", {"java21"}, tmp_path)


def github_environment(
    tmp_path: Path, context: release.Context, monkeypatch: pytest.MonkeyPatch
) -> Path:
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.0"\n')
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps(
            {
                "ref": "refs/heads/main",
                "deleted": False,
                "head_commit": {"id": context.revision, "message": "Release [publish-docker]"},
                "repository": {"full_name": context.source_repository},
            }
        )
    )
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REPOSITORY": context.source_repository,
        "GITHUB_SHA": context.revision,
        "GITHUB_RUN_ID": context.run_id,
        "GITHUB_RUN_ATTEMPT": context.run_attempt,
        "GITHUB_EVENT_PATH": str(event),
    }.items():
        monkeypatch.setenv(key, value)

    def git(root: Path, args: list[str]) -> str:
        if args[:1] == ["status"]:
            return ""
        if args[:1] == ["log"]:
            return "Release [publish-docker]"
        return context.revision

    monkeypatch.setattr(release, "git_output", git)
    return event


@pytest.mark.parametrize(
    "change",
    ["pull-request", "branch", "head-message", "mixed-marker", "head-id", "deleted", "dirty"],
)
def test_gate_requires_the_actual_main_push_head_marker_before_auth(
    tmp_path: Path, context: release.Context, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    event = github_environment(tmp_path, context, monkeypatch)
    if change == "pull-request":
        monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    elif change == "branch":
        monkeypatch.setenv("GITHUB_REF", "refs/heads/feature")
    elif change == "dirty":
        monkeypatch.setattr(
            release,
            "git_output",
            lambda root, args: (
                "changed"
                if args[:1] == ["status"]
                else context.revision
                if args[:1] == ["rev-parse"]
                else "[publish-docker]"
            ),
        )
    else:
        value = json.loads(event.read_text())
        if change == "head-message":
            value["head_commit"]["message"] = "ordinary change"
            value["commits"] = [{"message": "old [publish-docker]"}]
        elif change == "mixed-marker":
            value["head_commit"]["message"] = "Release [publish-docker] [publish-js]"
        elif change == "head-id":
            value["head_commit"]["id"] = "b" * 40
        else:
            value["deleted"] = True
        event.write_text(json.dumps(value))
    with pytest.raises(ReleaseError):
        release.github_context(tmp_path, context.namespace)


def test_earlier_same_run_gate_returns_current_context_for_fresh_job_receipts(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = replace(context, run_attempt="2")
    github_environment(tmp_path, current, monkeypatch)
    gate = release.gate_release(context, profiles, FakeRegistry())
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(gate))
    loaded, found, mode = release.load_gate(path, tmp_path)
    assert loaded == current and found == profiles and mode == "build"


def test_targeted_gate_revalidates_group_and_selected_profiles(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = replace(context, run_attempt="2")
    event = github_environment(tmp_path, current, monkeypatch)
    payload = json.loads(event.read_text())
    payload["head_commit"]["message"] = "Release [publish-java]"
    event.write_text(json.dumps(payload))
    monkeypatch.setattr(
        release,
        "git_output",
        lambda root, args: (
            ""
            if args[:1] == ["status"]
            else "Release [publish-java]"
            if args[:1] == ["log"]
            else current.revision
        ),
    )
    gate = release.gate_release(
        context, profiles, FakeRegistry(), target_group="java", root=tmp_path
    )
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(gate))
    loaded, found, mode = release.load_gate(path, tmp_path)
    assert loaded == current and found == profiles and mode == "build"
    gate["selection"]["profiles"].remove("python-core")
    path.write_text(json.dumps(gate))
    with pytest.raises(ReleaseError, match="Invalid targeted release group"):
        release.load_gate(path, tmp_path)


def test_docker_layer_transfers_do_not_buffer_or_limit_progress_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess

    calls = []

    def run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append(args)
        assert kwargs["stdout"] == subprocess.DEVNULL and kwargs["stderr"] == subprocess.DEVNULL
        assert "capture_output" not in kwargs
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(subprocess, "run", run)
    release.Docker().push("exampleuser/ds60sqlpy:ci-example")
    assert calls == [["docker", "image", "push", "--quiet", "exampleuser/ds60sqlpy:ci-example"]]


def test_existing_release_with_missing_native_content_cannot_noop(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    for key, profile in profiles.items():
        body = release.index_body(context, key, natives[key])
        registry.add(body, release.version_tag(profile, context.version))
        registry.add(body, release.latest_tag(profile))
    del registry.objects[natives["java21"]["arm64"].digest]
    with pytest.raises(ReleaseError, match="missing native"):
        release.gate_release(context, profiles, registry)
    assert not registry.puts


@pytest.mark.parametrize(
    "system,machine,engine",
    [
        ("Darwin", "arm64", "linux arm64"),
        ("Linux", "x86_64", "linux arm64"),
        ("Linux", "aarch64", "windows arm64"),
    ],
)
def test_native_qualification_never_accepts_host_or_engine_emulation_mismatch(
    monkeypatch: pytest.MonkeyPatch, system: str, machine: str, engine: str
) -> None:
    monkeypatch.setattr(platform, "system", lambda: system)
    monkeypatch.setattr(platform, "machine", lambda: machine)
    monkeypatch.setattr(release.Docker, "output", lambda self, args, **kwargs: engine)
    with pytest.raises(ReleaseError):
        release.Docker().native("arm64")


def test_opaque_registry_secret_is_never_printed_for_invalid_cli(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOCKERHUB_TOKEN", "synthetic-secret-never-print")
    assert release.main(["gate", "--token", "synthetic-secret-never-print"]) == 2
    captured = capsys.readouterr()
    assert "synthetic-secret-never-print" not in captured.out + captured.err


def test_metadata_output_is_bounded_while_reading_and_its_process_is_reaped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess
    import sys

    original = subprocess.Popen
    children: list[subprocess.Popen[bytes]] = []

    def launch(args: list[str], **kwargs: Any) -> subprocess.Popen[bytes]:
        assert args == ["docker", "info"]
        child = original(
            [
                sys.executable,
                "-c",
                "import sys,time; sys.stdout.buffer.write(b'x'*(9*1024*1024)); "
                "sys.stdout.flush(); time.sleep(30)",
            ],
            **kwargs,
        )
        children.append(child)
        return child

    monkeypatch.setattr(subprocess, "Popen", launch)
    with pytest.raises(ReleaseError, match="exceeds limits"):
        release.Docker().output(["info"], timeout=5)
    assert len(children) == 1 and children[0].poll() is not None


def scan_evidence(snapshot: dict[str, Any], policy_sha: str) -> dict[str, Any]:
    """Synthetic `image_scan.py scan --tested` evidence for gate tests."""
    now = datetime.now(UTC)
    image = {
        "revision_label": snapshot["context"]["revision"],
        "reference": False,
        "scanners": "vuln,secret",
        "counts": dict(COUNTS),
        "blocking": [],
        "suppressed": [],
        "reported": [],
        "report_sha256": "f" * 64,
    }
    return {
        "schema": 1,
        "kind": "ds60-scan-evidence",
        "context": copy.deepcopy(snapshot["context"]),
        "architecture": snapshot["architecture"],
        "scanner": {
            "image": image_scan.TRIVY_IMAGE,
            "version": image_scan.TRIVY_VERSION,
            "db_updated_at": stamp(now - timedelta(hours=2)),
            "java_db_updated_at": stamp(now - timedelta(days=3)),
        },
        "policy_sha256": policy_sha,
        "scanned_at": stamp(now - timedelta(minutes=5)),
        "passed": True,
        "unused_policy_entries": [],
        "images": [
            {**image, "profile": row["profile"], "tested_image_id": row["tested_image_id"]}
            for row in snapshot["images"]
        ],
    }


def stage_cli(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[FakeDocker, dict[str, Any], list[str]]:
    registry = FakeRegistry()
    docker = local_images(registry, context, profiles, "amd64")
    snapshot = release.inspect_images(
        context, profiles, sorted(release.SEEDS), "amd64", docker, root=tmp_path
    )
    docker.operations.clear()
    gate = tmp_path / "gate.json"
    gate.write_text(json.dumps({"selection": None}))
    # Optional scan tests use the fixture policy, not the aging historical ledger.
    monkeypatch.setattr(release, "ROOT", tmp_path)
    monkeypatch.setattr(release, "load_gate", lambda path: (context, profiles, "build"))
    monkeypatch.setattr(release, "load_tested", lambda path, ctx, found: snapshot)
    monkeypatch.setattr(
        release,
        "qualification_records",
        lambda *args: proofs(set(release.SEEDS), "python-core"),
    )
    monkeypatch.setattr(release, "registry_for", lambda *args, **kwargs: registry)
    monkeypatch.setattr(release, "Docker", lambda: docker)
    argv = [
        "stage",
        "--gate",
        str(gate),
        "--tested-images",
        str(tmp_path / "tested.json"),
        "--qualification",
        str(tmp_path / "q.json"),
        "--output",
        str(tmp_path / "receipt.json"),
    ]
    return docker, snapshot, argv


def test_stage_without_scan_evidence_still_qualifies_and_records_no_scan(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docker, _, argv = stage_cli(tmp_path, context, profiles, monkeypatch)

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("Default publication must not load the CVE policy or scan evidence")

    monkeypatch.setattr(release, "load_scan", forbidden)
    monkeypatch.setattr(release, "committed_policy", forbidden)
    assert release.main(argv) == 0
    assert [op for op in docker.operations if op[0] == "push"]
    staged = json.loads((tmp_path / "receipt.json").read_text())
    assert staged["scan"] is None
    assert {row["kind"] for row in staged["qualification"]} == {"module-references", "ci-summary"}
    release.staged_receipt(staged, context, profiles, root=tmp_path)


def committed_policy_sha() -> str:
    return hashlib.sha256((release.ROOT / "docker/cve-policy.json").read_bytes()).hexdigest()


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("image-id", "different image than was qualified"),
        ("blocking", "blocking findings"),
        ("missing-profile", "each tested profile exactly once"),
        ("architecture", "another architecture"),
        ("revision", "another source, run or attempt"),
        ("stale-db", "last 24 hours"),
        ("future-db", "last 24 hours"),
        ("policy", "different CVE policy"),
        ("failed-database", "blocking findings"),
        ("scanner", "pinned scanner"),
        ("kind", "Invalid image scan evidence"),
    ],
)
def test_stage_scan_gate_rejects_unbound_or_unclean_evidence_before_any_tag(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    change: str,
    message: str,
) -> None:
    docker, snapshot, argv = stage_cli(tmp_path, context, profiles, monkeypatch)
    evidence = scan_evidence(snapshot, committed_policy_sha())
    now = datetime.now(UTC)
    if change == "image-id":
        evidence["images"][0]["tested_image_id"] = "sha256:" + "0" * 64
    elif change == "blocking":
        evidence["images"][1]["blocking"] = [{"id": "CVE-2026-0001", "reason": "fixable"}]
    elif change == "missing-profile":
        del evidence["images"][1]
    elif change == "architecture":
        evidence["architecture"] = "arm64"
    elif change == "revision":
        evidence["context"]["revision"] = "b" * 40
    elif change == "stale-db":
        evidence["scanner"]["db_updated_at"] = stamp(now - timedelta(hours=25))
    elif change == "future-db":
        evidence["scanner"]["db_updated_at"] = stamp(now + timedelta(hours=2))
    elif change == "policy":
        evidence["policy_sha256"] = "0" * 64
    elif change == "failed-database":
        evidence["passed"] = False
        evidence["images"][-1]["blocking"] = [{"id": "CVE-2026-0002", "reason": "fixable"}]
    elif change == "scanner":
        evidence["scanner"]["image"] = "aquasec/trivy:latest"
    else:
        evidence["kind"] = "trivy-report"
    path = tmp_path / "scan-evidence.json"
    path.write_text(json.dumps(evidence))
    assert release.main([*argv, "--scan", str(path)]) == 2
    assert message in capsys.readouterr().err
    assert docker.operations == []  # No preflight, tag or push ran.
    assert not (tmp_path / "receipt.json").exists()


def test_stage_with_clean_fresh_evidence_writes_a_schema_2_receipt_with_scan_summary(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docker, snapshot, argv = stage_cli(tmp_path, context, profiles, monkeypatch)
    evidence = scan_evidence(snapshot, committed_policy_sha())
    evidence["images"][0]["suppressed"] = [
        {
            "id": "CVE-2026-0003",
            "kind": "vulnerability",
            "package": "libexample",
            "installed": "1",
            "fixed": "",
            "severity": "HIGH",
            "target": "debian",
            "reason": "accepted",
            "expires_at": "2099-01-01",
            "reviewer": "pending-owner",
        }
    ]
    path = tmp_path / "scan-evidence.json"
    path.write_bytes(json.dumps(evidence).encode())
    assert release.main([*argv, "--scan", str(path)]) == 0
    staged = json.loads((tmp_path / "receipt.json").read_text())
    assert staged["schema_version"] == 2
    scan = staged["scan"]
    assert scan["evidence_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert scan["policy_sha256"] == committed_policy_sha()
    assert scan["scanner_image"] == image_scan.TRIVY_IMAGE
    assert [row["profile"] for row in scan["images"]] == ["app", "postgres", "python-core"]
    assert scan["images"][0]["suppressed"] == [
        {"id": "CVE-2026-0003", "package": "libexample", "expires_at": "2099-01-01"}
    ]
    assert {row["tested_image_id"] for row in scan["images"]} == {
        row["tested_image_id"] for row in snapshot["images"]
    }
    assert [op[1] for op in docker.operations if op[0] == "tag"] == [
        row["tested_image_id"] for row in snapshot["images"]
    ]


def test_stage_images_refuses_a_scan_block_for_other_image_ids(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    docker = local_images(registry, context, profiles, "amd64")
    snapshot = release.inspect_images(
        context, profiles, sorted(release.SEEDS), "amd64", docker, root=tmp_path
    )
    scan = scan_block(snapshot["images"])
    scan["images"][0]["tested_image_id"] = "sha256:" + "0" * 64
    with pytest.raises(ReleaseError, match="exactly the staged image IDs"):
        release.stage_images(
            context,
            profiles,
            snapshot,
            proofs(set(release.SEEDS), "python-core"),
            registry,
            docker,
            tmp_path,
            scan=scan,
        )
    assert not [op for op in docker.operations if op[0] in {"tag", "push"}]


@pytest.mark.parametrize("change", ["schema-1", "missing-scan", "extra-scan-key", "wrong-id"])
def test_staged_receipt_requires_schema_2_with_an_exact_scan_block(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    change: str,
) -> None:
    value = receipt(FakeRegistry(), context, profiles, "amd64", "python-core")
    assert release.staged_receipt(value, context, profiles, root=tmp_path) == value
    if change == "schema-1":
        value["schema_version"] = 1
    elif change == "missing-scan":
        del value["scan"]
    elif change == "extra-scan-key":
        value["scan"]["blocking"] = []
    else:
        value["scan"]["images"][0]["tested_image_id"] = "sha256:" + "0" * 64
    with pytest.raises(ReleaseError):
        release.staged_receipt(value, context, profiles, root=tmp_path)


EXPIRED_ENTRY = {
    "id": "CVE-2026-0004",
    "kind": "vulnerability",
    "package": "libexample",
    "images": ["app"],
    "justification": "No upstream fix; not reachable from the classroom.",
    "reviewer": "pending-owner",
    "reviewed_at": "2026-01-01",
    "expires_at": "2026-02-01",
}


def test_unscanned_release_promotes_despite_expired_cve_policy(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    expected = complete_receipts(folder, registry, context, profiles)
    for path in release.receipt_files(folder):
        value = release.read_json(path)
        value["scan"] = None
        release.write_json(path, value)
    (tmp_path / "docker/cve-policy.json").write_text(
        json.dumps({"schema": 1, "entries": [EXPIRED_ENTRY]})
    )
    scans: dict[str, dict[str, Any]] = {}
    inputs = release.promotion_inputs(folder, context, profiles, registry, tmp_path, scans=scans)
    assert inputs == expected
    report = release.promote_release(
        context,
        profiles,
        registry,
        natives=inputs,
        output=tmp_path / "release.json",
        root=tmp_path,
        scan=scans,
    )
    assert all(
        row["status"] == "not_requested" and "counts" not in row
        for by_arch in report["scan"].values()
        for row in by_arch.values()
    )


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("stale-db", "last 24 hours"),
        ("policy-changed", "differs from the committed"),
        ("policy-expired", "invalid or expired"),
        ("suppression-expired", "has expired"),
    ],
)
def test_promote_scan_rejects_stale_changed_or_expired_evidence(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    change: str,
    message: str,
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    complete_receipts(folder, registry, context, profiles)
    now = datetime.now(UTC)
    policy = tmp_path / "docker/cve-policy.json"
    if change == "stale-db":
        now += timedelta(hours=24)
    elif change == "policy-changed":
        policy.write_text('{"schema": 1, "entries": []}')
    elif change == "policy-expired":
        policy.write_text(json.dumps({"schema": 1, "entries": [EXPIRED_ENTRY]}))
    else:
        path = folder / "java-arm64/release-receipt.json"
        value = json.loads(path.read_text())
        value["scan"]["images"][0]["suppressed"] = [
            {
                "id": "CVE-2026-0005",
                "package": "libexample",
                "expires_at": (now.date() - timedelta(days=1)).isoformat(),
            }
        ]
        path.write_text(json.dumps(value))
    with pytest.raises(ReleaseError, match=message):
        release.promotion_inputs(folder, context, profiles, registry, tmp_path, now=now)
    assert registry.puts == []


def test_promote_scan_accepts_fresh_evidence_and_records_it_per_promoted_digest(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    expected = complete_receipts(folder, registry, context, profiles)
    scans: dict[str, dict[str, Any]] = {}
    inputs = release.promotion_inputs(
        folder,
        context,
        profiles,
        registry,
        tmp_path,
        now=datetime.now(UTC) + timedelta(hours=22),
        scans=scans,
    )
    assert inputs == expected
    assert set(scans) == set(profiles)
    output = tmp_path / "release.json"
    report = release.promote_release(
        context, profiles, registry, natives=inputs, output=output, root=tmp_path, scan=scans
    )
    written = json.loads(output.read_text())
    assert written["scan"] == report["scan"] == scans
    for key, by_arch in report["scan"].items():
        assert set(by_arch) == set(release.ARCHITECTURES)
        for arch, row in by_arch.items():
            assert row["native_digest"] == inputs[key][arch].digest
            assert row["policy_sha256"] == POLICY_SHA
            assert row["counts"] == COUNTS
            assert row["suppressed"] == []
    tampered = copy.deepcopy(scans)
    tampered["java21"]["amd64"]["native_digest"] = "sha256:" + "0" * 64
    with pytest.raises(ReleaseError, match="exactly the promoted native digests"):
        release.promote_release(
            context,
            profiles,
            registry,
            natives=inputs,
            output=tmp_path / "other.json",
            root=tmp_path,
            scan=tampered,
        )


SCIENTIFIC_TAGS = [
    "project-spark-torch",
    "project-spark-tmb",
    "project-tmb-public-api",
    "project-tmb-cpp-api",
]


def scientific_natives(registry: FakeRegistry, label: str) -> dict[str, dict[str, Descriptor]]:
    return {
        key: {
            arch: native(registry, f"{label}-{key}-{arch}")[0].descriptor
            for arch in release.ARCHITECTURES
        }
        for key in sorted(release.SCIENTIFIC_STAGED)
    }


def scientific_scan(natives: dict[str, dict[str, Descriptor]]) -> dict[str, dict[str, Any]]:
    return {
        key: {
            arch: {
                "tested_image_id": "sha256:" + hashlib.sha256((key + arch).encode()).hexdigest(),
                "native_digest": value.digest,
                "counts": dict(COUNTS),
                "suppressed": [],
                "report_sha256": "f" * 64,
                "evidence_sha256": "e" * 64,
                "scanner_image": image_scan.TRIVY_IMAGE,
                "db_updated_at": "2026-01-01T00:00:00Z",
                "policy_sha256": POLICY_SHA,
                "scanned_at": "2026-01-01T01:00:00Z",
            }
            for arch, value in by_arch.items()
        }
        for key, by_arch in natives.items()
    }


def test_scientific_indexes_publish_after_workers_and_before_each_app_pointer(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    inputs = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    science = scientific_natives(registry, "first")
    scan = scientific_scan(science)
    output = tmp_path / "release.json"
    report = release.promote_release(
        context,
        profiles,
        registry,
        natives=inputs,
        output=output,
        scientific=science,
        scientific_scan=scan,
    )
    workers = ["worker-python-core", "worker-java21", "postgres"]
    assert registry.puts == [
        *(f"1.0.0-{suffix}" for suffix in workers),
        *(f"1.0.0-{suffix}" for suffix in SCIENTIFIC_TAGS),
        "1.0.0",
        *(f"latest-{suffix}" for suffix in workers),
        *(f"latest-{suffix}" for suffix in SCIENTIFIC_TAGS),
        "latest",
    ]
    assert json.loads(output.read_text()) == report and report["status"] == "published"
    assert len(report["version_tags"]) == len(report["latest_tags"]) == 4
    record = report["scientific"]
    assert record["scan"] == scan
    assert [row["tag"] for row in record["version_tags"]] == [
        "1.0.0-" + suffix for suffix in SCIENTIFIC_TAGS
    ]
    assert [row["tag"] for row in record["latest_tags"]] == [
        "latest-" + suffix for suffix in SCIENTIFIC_TAGS
    ]
    for row in (*record["version_tags"], *record["latest_tags"]):
        assert registry.tags[row["tag"]] == row["digest"]
    for key in SCIENTIFIC_TAGS:
        source = release.SCIENTIFIC_RELEASES[key]
        assert record["images"][key] == {
            "source": source,
            "reused": False,
            "natives": {arch: science[source][arch].digest for arch in release.ARCHITECTURES},
        }
        version, revision, recorded = release.published_index(
            registry.get(f"1.0.0-{key}"), key, context.source_repository
        )
        assert (version, revision, recorded) == ("1.0.0", context.revision, science[source])
    assert (
        registry.tags["1.0.0-project-tmb-cpp-api"] != registry.tags["1.0.0-project-spark-tmb"]
    )  # Each project index names its own profile even when it shares the native images.


def test_scientific_rerun_reuses_the_published_indexes_of_this_revision(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    inputs = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    first = scientific_natives(registry, "first")
    release.promote_release(
        context, profiles, registry, natives=inputs, output=tmp_path / "a.json", scientific=first
    )
    written = len(registry.puts)
    rebuilt = scientific_natives(registry, "rebuilt")
    report = release.promote_release(
        context,
        profiles,
        registry,
        natives=inputs,
        output=tmp_path / "b.json",
        scientific=rebuilt,
        scientific_scan=scientific_scan(rebuilt),
    )
    assert len(registry.puts) == written
    for key, image in report["scientific"]["images"].items():
        source = release.SCIENTIFIC_RELEASES[key]
        assert image["reused"] is True
        assert image["natives"] == {
            arch: first[source][arch].digest for arch in release.ARCHITECTURES
        }


@pytest.mark.parametrize(
    "mutation",
    [
        "targeted",
        "missing-arch",
        "scan-without-images",
        "scan-other-digest",
        "other-revision",
        "shared-disagree",
    ],
)
def test_scientific_publication_is_refused_before_any_write(
    mutation: str,
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
) -> None:
    registry = FakeRegistry()
    inputs = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    science: dict[str, dict[str, Descriptor]] | None = scientific_natives(registry, "first")
    assert science is not None
    scan = scientific_scan(science)
    options: dict[str, Any] = {}
    message = ""
    if mutation == "targeted":
        options = {"target_group": "java", "root": tmp_path}
        inputs = {key: inputs[key] for key in ("app", "java21", "postgres", "python-core")}
        message = "only with a full release"
    elif mutation == "missing-arch":
        del science["project-spark-tmb"]["arm64"]
        message = "on both platforms"
    elif mutation == "scan-without-images":
        science = None
        message = "require scientific native images"
    elif mutation == "scan-other-digest":
        scan["project-spark-torch"]["amd64"]["native_digest"] = "sha256:" + "0" * 64
        message = "exactly the staged native digests"
    elif mutation == "other-revision":
        other = replace(context, revision="b" * 40)
        registry.add(
            release.index_body(other, "project-spark-tmb", science["project-spark-tmb"]),
            "1.0.0-project-spark-tmb",
        )
        message = "another revision"
    else:
        registry.add(
            release.index_body(context, "project-spark-tmb", science["project-spark-tmb"]),
            "1.0.0-project-spark-tmb",
        )
        registry.add(
            release.index_body(context, "project-tmb-cpp-api", science["project-spark-torch"]),
            "1.0.0-project-tmb-cpp-api",
        )
        message = "disagree on their shared image"
    output = tmp_path / "release.json"
    with pytest.raises(ReleaseError, match=message):
        release.promote_release(
            context,
            profiles,
            registry,
            natives=inputs,
            output=output,
            scientific=science,
            scientific_scan=scan,
            **options,
        )
    assert registry.puts == [] and not output.exists()


def test_scientific_release_metadata_size_is_checked_before_any_tag(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ordinary = FakeRegistry()
    inputs = complete_receipts(tmp_path / "ordinary", ordinary, context, profiles)
    release.promote_release(
        context, profiles, ordinary, natives=inputs, output=tmp_path / "ordinary.json"
    )
    monkeypatch.setattr(release, "MAX_RECEIPT", (tmp_path / "ordinary.json").stat().st_size + 64)
    registry = FakeRegistry()
    inputs = complete_receipts(tmp_path / "science", registry, context, profiles)
    science = scientific_natives(registry, "first")
    output = tmp_path / "release.json"
    with pytest.raises(ReleaseError, match="256 KiB bound; no tag was written"):
        release.promote_release(
            context,
            profiles,
            registry,
            natives=inputs,
            output=output,
            scientific=science,
            scientific_scan=scientific_scan(science),
        )
    assert registry.puts == [] and not output.exists()
